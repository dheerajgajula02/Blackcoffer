import requests
from bs4 import BeautifulSoup
import os
import re
import pandas as pd
import nltk
from nltk.corpus import stopwords
import string
nltk.download('punkt')
from nltk.tokenize import sent_tokenize, word_tokenize

def sentiment(url:str, index:int):

    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
    except:
        print(f"article taken off the internet{url}")
    
    try:
        title = soup.find('h1').get_text()
        article = soup.find('div', class_="td-post-content tagdiv-type")
        paragraphs = article.find_all('p')
        my_paragraph = title
        for para in paragraphs:
            my_paragraph += para.get_text()

    except:
        print("not found the tag but doing something stupid")
        my_paragraph=""
        paragraphs = soup.find_all('p')
        for para in paragraphs:
            my_paragraph += para.get_text()

        

    
    readability_analysis(my_paragraph, index)
    word_count_stop= word_count(my_paragraph)
    syllabes_per_word = avg_syllables_per_word(my_paragraph)
    avg_word_length_ = avg_word_length(my_paragraph)
    peronal_pronouns = cal_pronouns(my_paragraph)


    for files in os.listdir("StopWords/"):
        with open("StopWords/"+files, "r") as file:
            lines = file.readlines()
            
            cleaned_lines=[]
            for line in lines:
                line = line.strip()
                line=line.split("|", 2)[0]
                line = line.replace(" ", "")
                cleaned_lines.append(line)
            file.close()
    list_para = my_paragraph.split()
    new_list_para = []
    for words in list_para:
        words = re.sub(r'[^a-zA-Z\s]', "", words).upper()
        new_list_para.append(words)

    after_stops = []
    for word in new_list_para:
        if word in after_stops:
            after_stops.append(word)
        elif word not in cleaned_lines:
            after_stops.append(word)
        else:
            continue
    
    
    with open("MasterDictionary/negative-words.txt", "r") as file:
        negative_words = file.readlines()
        file.close()
    clean_negative=[]

    for word in negative_words:
        word = word.strip().upper()
        clean_negative.append(word)
    
    with open("MasterDictionary/positive-words.txt", "r") as file:
        positive_words = file.readlines()
        file.close()
    clean_positive=[]
    for words in positive_words:
        words=words.strip().upper()
        clean_positive.append(words)

    negative_score=0
    positive_score=0
    normal_score =0
    for word in after_stops:
        if word in clean_negative:
            negative_score+=1
        elif word in clean_positive:
            positive_score+=1
        else:
            normal_score+=1
    polarity_score = (positive_score-negative_score)/((positive_score+negative_score)+0.000001)
    subjectivity_score = (positive_score+negative_score)/(positive_score+negative_score+normal_score+0.000001)
    data_frame = pd.read_excel("Output Data Structure.xlsx")
    data_frame.at[index,"POSITIVE SCORE"]=positive_score
    data_frame.at[index,"NEGATIVE SCORE"]=negative_score
    data_frame.at[index,"POLARITY SCORE"]=polarity_score
    data_frame.at[index,"SUBJECTIVITY SCORE"]=subjectivity_score
    data_frame.at[index,"WORD COUNT"]=word_count_stop
    data_frame.at[index,"SYLLABLE PER WORD"]=syllabes_per_word
    data_frame.at[index,"AVG WORD LENGTH"]=avg_word_length_
    data_frame.at[index,"PERSONAL PRONOUNS"]=peronal_pronouns
    data_frame.to_excel("Output Data Structure.xlsx", index=False)

def word_count(paragraph:str):
    words = word_tokenize(paragraph)
    table = str.maketrans("","", string.punctuation)
    words = [word.translate(table) for word in words]
    
    stop_words = set(stopwords.words('english'))
    
    cleaned_words = [word for word in words if word.lower() not in stop_words]
    return len(cleaned_words)

def avg_word_length(paragraph:str):
    words = word_tokenize(paragraph)
    table = str.maketrans("","", string.punctuation)
    words = [word.translate(table) for word in words]
    
    total_length = 0
    for word in words:
        total_length += len(word)
    return total_length/len(words)



def is_complex(word):
    exceptions = ["es", "ed", "le", "ing", "ly"]
    word = word.lower()
    for exception in exceptions:
        if word.endswith(exception):
            word = word[: -len(exception)]
    syllable_count = 0

    vowels = "aeiouyAEIOUY"
    for i in range(len(word)):
        char = word[i]

        if char == 'y' and i > 0 and i < len(word) - 1:
            if word[i - 1] not in vowels and word[i + 1] not in vowels:
                syllable_count += 1
        elif char in vowels:
            syllable_count += 1
    if len(word) == 1 and word[0] in vowels:
        syllable_count = 1
        
    if syllable_count>2:
        return True, syllable_count
    return False, syllable_count

def avg_syllables_per_word(paragraph:str):
    words = word_tokenize(paragraph)
    syllable_count = 0
    for word in words:
        syllable_count += is_complex(word)[1]
    return syllable_count/len(words)
    
def complex_word_count_sent(sentence:str):
    words = word_tokenize(sentence)
    complex_word_count = 0
    for word in words:
        if is_complex(word)[0]:
            complex_word_count += 1
    return complex_word_count


def readability_analysis(paragraph:str, index:int):
    sentences = sent_tokenize(paragraph)
    total_words = 0
    complex_words_count=0
    for sentence in sentences:
        words = word_tokenize(sentence)
        complex_words = [word for word in words if is_complex(word)[0]]
        complex_words_count += len(complex_words)
        total_words += len(words)
    average_senlen = total_words/len(sentences)

    precent_complex_words = complex_words_count/total_words
    fog_index = 0.4*(average_senlen+precent_complex_words)
    data_frame = pd.read_excel("Output Data Structure.xlsx")
    data_frame.at[index,"FOG INDEX"]=fog_index
    data_frame.at[index, "AVG SENTENCE LENGTH"]=average_senlen
    data_frame.at[index, "COMPLEX WORD COUNT"]=complex_words_count
    data_frame.at[index, "PERCENTAGE OF COMPLEX WORDS"]=precent_complex_words
    data_frame.at[index, "AVG NUMBER OF WORDS PER SENTENCE"]= average_senlen
    data_frame.to_excel("Output Data Structure.xlsx", index=False)

    
def cal_pronouns(paragraph:str):
    

    pronouns = ["i", "we", "my", "our", "us"]
    paragraph= paragraph.replace("US", "")
    paragraph= paragraph.replace("U.S", "")
    words = word_tokenize(paragraph)
    pronoun_count = 0
    for word in words:
        if word.lower() in pronouns:
            pronoun_count += 1
    return pronoun_count


sheet = pd.read_excel("Input.xlsx")        

for row in sheet.index:
    url = sheet.at[row,"URL"]
    sentiment(url, row)

    
    



    