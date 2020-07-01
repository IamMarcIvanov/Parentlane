from sentence_transformers import SentenceTransformer
from mysql.connector import Error
import mysql.connector
import string
import pickle
from textblob import TextBlob
import re
import time
import num2words
from googletrans import Translator
import winsound
import itertools


def pre_processing(question):
    def lemmatize_with_pos_tag(sentence):
        tokenized_sentence = TextBlob(sentence)
        tag_dict = {"J": 'a', "N": 'n', "V": 'v', "R": 'r'}
        words_and_tags = [(word, tag_dict.get(pos[0], 'n')) for word, pos in tokenized_sentence.tags]
        lemmatized_list = [wd.lemmatize(tag) for wd, tag in words_and_tags]
        return " ".join(lemmatized_list)

    question = question.lower()  # to lowercase

    # remove unnecessary patterns
    patterns = [r'\n', 'http://www', 'php', ']', '[']
    for pat in patterns:
        question = question.replace(pat, ' ', )
    question = question.replace('bm', 'breast milk')
    question = question.replace('fm', 'formula milk')
    question = re.sub(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', ' ', question)  # remove html stuff
    question.translate(str.maketrans(" ", " ", string.punctuation))  # remove punctuation
    question = re.sub(r"(\d+)", lambda x: num2words.num2words(int(x.group(0))), question)  # convert numbers to words
    question = ' '.join(question.split())  # remove extra whitespaces from between words
    try:
        if not (translator.detect([question]))[0].lang == 'en':  # translate to english
            question = (translator.translate([question]))[0].text
    except:
        question = ' '
    question = lemmatize_with_pos_tag(question)  # lemmatization

    return question


connection = None
data = []
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='parentlane',
                                         user='root',
                                         password='7happybirthdaytome@')
    if connection.is_connected():
        sql_query = "SELECT id, title, details, age_group_min, age_group_max, content_type FROM parentlane.question;"
        cursor = connection.cursor()
        cursor.execute(sql_query)
        records = cursor.fetchall()
        for row in records:
            row = list(row)
            text = ''
            if row[1]:
                row[1] = pre_processing(row[1])
            if row[2]:
                row[2] = pre_processing(row[2])
            if row[1] and not row[2]:
                text = row[1]
            elif row[2] and not row[1]:
                text = row[2]
            elif row[1] and row[2]:
                text = row[1] + " " + row[2]
            data.append({'id': row[0],
                         'text': text,
                         'age_group_min': row[3],
                         'age_group_max': row[4],
                         'content_type': row[5]})
except Error as e:
    print("There was an error", e)
finally:
    if connection.is_connected():
        connection.close()
    print('conn closed')



def word_embedding(question):
    return model.encode([question])[0]


start_time = time.process_time()
translator = Translator()
model = SentenceTransformer('roberta-large-nli-stsb-mean-tokens')
print('curr =', time.process_time() - start_time)
all_text = [query['text'] for query in data]
all_embeddings = [embedding for embedding in model.encode(all_text)]
c = itertools.count(0, 1)
for query in data:
    query['embedding'] = all_embeddings[next(c)]
print('curr =', time.process_time() - start_time)

with open('data_file_4', 'wb') as f:
    pickle.dump(data, f)

end_time = time.process_time()
time_taken = end_time - start_time
print(time_taken)
winsound.Beep(2000, 5000)
