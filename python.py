from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import requests
import json
import nltk
import re
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

links = pd.read_excel("C:\\Users\\Manish\\OneDrive\\Desktop\\Blackcoffer\\Input.xlsx")
links.head()

stop_words = []
with open('C:\\Users\\Manish\\OneDrive\\Desktop\\Blackcoffer\\StopWords_Auditor.txt') as f:
    content = f.read().strip()
    stop_words += content.split("\n")

with open('C:\\Users\\Manish\\OneDrive\\Desktop\\Blackcoffer\\StopWords_Currencies.txt') as f:
    content = f.read().strip()
    stop_words += content.split("\n")

with open('C:\\Users\\Manish\\OneDrive\\Desktop\\Blackcoffer\\StopWords_DatesandNumbers.txt') as f:
    content = f.read().strip()
    stop_words += content.split("\n")

with open('C:\\Users\\Manish\\OneDrive\\Desktop\\Blackcoffer\\StopWords_Generic.txt') as f:
    content = f.read().strip()
    stop_words += content.split("\n")

with open('C:\\Users\\Manish\\OneDrive\\Desktop\\Blackcoffer\\StopWords_GenericLong.txt') as f:
    content = f.read().strip()
    stop_words += content.split("\n")

with open('C:\\Users\\Manish\\OneDrive\\Desktop\\Blackcoffer\\StopWords_Geographic.txt') as f:
    content = f.read().strip()
    stop_words += content.split("\n")

with open('C:\\Users\\Manish\\OneDrive\\Desktop\\Blackcoffer\\StopWords_Names.txt') as f:
    content = f.read().strip()
    stop_words += content.split("\n")

stop_words = [i.lower() for i in stop_words]

positive_words = []
with open('C:\\Users\\Manish\\OneDrive\\Desktop\\Blackcoffer\\positive-words.txt') as f:
    content = f.read().strip()
    positive_words += content.split("\n")

negative_words = []
with open('C:\\Users\\Manish\\OneDrive\\Desktop\\Blackcoffer\\negative-words.txt') as f:
    content = f.read().strip()
    negative_words += content.split("\n")

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
}

print(len(links.URL))

output_df = pd.DataFrame(links)
print(output_df)
POSITIVESCORE = []
NEGATIVESCORE = []
POLARITYSCORE = []
SUBJECTIVITYSCORE = []
AVGSENTENCELENGTH = []
PERCENTAGEOFCOMPLEXWORDS = []
FOGINDEX = []
AVGNUMBEROFWORDSPERSENTENCE = []
COMPLEXWORDCOUNT = []
WORDCOUNT = []
SYLLABLEPERWORD = []
PERSONALPRONOUNS = []
AVGWORDLENGTH = []


def count_syllables(word):
    return len(re.findall('(?!e$)[aeiouy]+', word, re.I) + re.findall('^[^aeiouy]*e$', word, re.I))


def load_data(url, url_id):
    try:

        cmc = requests.get(url, headers=headers)
        soup = BeautifulSoup(cmc.content, 'html.parser')
        title_tag = soup.find("h1", attrs={"class": 'entry-title'})
        article_tag = soup.find('div', {'class': 'td-post-content'})
        title = title_tag.get_text()
        article_p = article_tag.find_all("p")
        article = " ".join([p.get_text() for p in article_p])

        title_text = title + " " + article

        cleaned = []
        txt_file = open(f'Extracted Data/{url_id}.txt', 'w+', encoding="utf-8")
        txt_file.write(title)
        txt_file.write(article)
        txt_file.close()

        [i if i.lower() in stop_words else cleaned.append(i) for i in word_tokenize(title_text)]

        cleaned_n = []
        stops = set(stopwords.words('english'))
        for i in word_tokenize(title_text):
            if i not in stops:
                cleaned_n.append(i)

        positive_score = 0
        negative_score = 0
        total_words = len(word_tokenize(title_text))
        Total_Words_after_cleaning = len(cleaned)
        sentences = nltk.sent_tokenize(title_text)
        total_sentences = len(sentences)

        complex_words = []
        for i in word_tokenize(title_text):
            if count_syllables(i.lower()) > 1:
                complex_words.append(i)
        complex_word_count = len(complex_words)

        for i in cleaned:
            if i.lower() in positive_words:
                positive_score += 1

            if i.lower() in negative_words:
                negative_score += 1
        POSITIVESCORE.append(positive_score)
        NEGATIVESCORE.append(negative_score)

        polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
        POLARITYSCORE.append(polarity_score)

        subjectivity_score = (polarity_score + negative_score) / ((Total_Words_after_cleaning) + 0.000001)
        SUBJECTIVITYSCORE.append(subjectivity_score)

        average_sentence_length = total_words / total_sentences
        AVGSENTENCELENGTH.append(average_sentence_length)

        percentage_of_complex_words = complex_word_count / total_words
        PERCENTAGEOFCOMPLEXWORDS.append(percentage_of_complex_words)

        Fog_Index = 0.4 * (average_sentence_length + percentage_of_complex_words)
        FOGINDEX.append(Fog_Index)

        average_number_of_words_per_sentence = average_sentence_length
        AVGNUMBEROFWORDSPERSENTENCE.append(average_number_of_words_per_sentence)

        COMPLEXWORDCOUNT.append(complex_word_count)

        word_count_list = []

        punc = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
        for i in range(len(cleaned_n)):
            if cleaned_n[i] not in punc:
                word_count_list.append(cleaned_n[i])
        word_count = len(word_count_list)
        WORDCOUNT.append(word_count)

        total_syllable = 0
        for i in word_tokenize(title_text):
            total_syllable += count_syllables(i)

        SYLLABLEPERWORD.append(total_syllable)

        pronouns = ["I", "i", "We", "we", "My", "my", "Ours", "ours", "Us", "us"]
        pronouns_count = 0

        for i in pronouns:
            match = re.findall(i, title_text)
            pronouns_count += len(match)

        PERSONALPRONOUNS.append(pronouns_count)

        total_char = re.findall("\w", title_text)
        average_word_length = len(total_char) / len(word_tokenize(title_text))
        AVGWORDLENGTH.append(average_word_length)
        print(
            positive_score,
            negative_score,
            polarity_score,
            subjectivity_score,
            average_sentence_length,
            percentage_of_complex_words,
            Fog_Index,
            average_number_of_words_per_sentence,
            complex_word_count,
            word_count,
            total_syllable,
            pronouns_count,
            average_word_length,
        )
    except:
        POSITIVESCORE.append(0)
        NEGATIVESCORE.append(0)
        POLARITYSCORE.append(0)
        SUBJECTIVITYSCORE.append(0)
        AVGSENTENCELENGTH.append(0)
        PERCENTAGEOFCOMPLEXWORDS.append(0)
        FOGINDEX.append(0)
        AVGNUMBEROFWORDSPERSENTENCE.append(0)
        COMPLEXWORDCOUNT.append(0)
        WORDCOUNT.append(0)
        SYLLABLEPERWORD.append(0)
        PERSONALPRONOUNS.append(0)
        AVGWORDLENGTH.append(0)


[load_data(links.URL[i], links.URL_ID[i]) for i in range(len(links))]

print(
    len(POSITIVESCORE),
    len(NEGATIVESCORE),
    len(POLARITYSCORE),
    len(SUBJECTIVITYSCORE),
    len(AVGSENTENCELENGTH),
    len(PERCENTAGEOFCOMPLEXWORDS),
    len(FOGINDEX),
    len(AVGNUMBEROFWORDSPERSENTENCE),
    len(COMPLEXWORDCOUNT),
    len(WORDCOUNT),
    len(SYLLABLEPERWORD),
    len(PERSONALPRONOUNS),
    len(AVGWORDLENGTH),
)

output_df['POSITIVE SCORE'] = POSITIVESCORE
output_df['NEGATIVE SCORE'] = NEGATIVESCORE
output_df['POLARITY SCORE'] = POLARITYSCORE
output_df['SUBJECTIVITY SCORE'] = SUBJECTIVITYSCORE
output_df['AVG SENTENCE LENGTH'] = AVGSENTENCELENGTH
output_df['PERCENTAGE OF COMPLEX WORDS'] = PERCENTAGEOFCOMPLEXWORDS
output_df['FOG INDEX'] = FOGINDEX
output_df['AVG NUMBER OF WORDS PER SENTENCE'] = AVGNUMBEROFWORDSPERSENTENCE
output_df['COMPLEX WORD COUNT'] = COMPLEXWORDCOUNT
output_df['WORD COUNT'] = WORDCOUNT
output_df['SYLLABLE PER WORD'] = SYLLABLEPERWORD
output_df['PERSONAL PRONOUNS'] = PERSONALPRONOUNS
output_df['AVG WORD LENGTH'] = AVGWORDLENGTH

output_df.to_csv("output.csv", index=False)