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
import torch
import numpy as np


start_time = time.process_time()

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


translator = Translator()
model = torch.load('model_file')
with open('data_file_4', 'rb') as f:
    questions = pickle.load(f)

query = pre_processing(input('Enter question: '))
query_embedding = model.encode([query])[0]
child_age = int(input('Enter child age: '))
query_content_type = int(input('Enter 1 if pregnancy related and 0 is otherwise: '))
threshold = 0.5
for q in questions:
    if q['text']:
        if query_content_type == q['content_type']:
            if child_age <= 729 and q['age_group_min'] <= child_age <= q['age_group_max']:
                q['similarity'] = np.matmul(query_embedding, q['embedding']) \
                                  / np.linalg.norm(query_embedding * q['embedding'])
            elif child_age > 729:
                q['similarity'] = np.matmul(query_embedding, q['embedding']) \
                                  / np.linalg.norm(query_embedding * q['embedding'])
            else:
                q['similarity'] = -10000
        else:
            q['similarity'] = -10000
    else:
        q['similarity'] = -10000
questions = sorted(questions, key=(lambda x: x['similarity']), reverse=True)
relevant_questions = questions[:10]
connection = None
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='parentlane',
                                         user='root',
                                         password='7happybirthdaytome@')
    if connection.is_connected():
        for i in range(10):
            sql_query = "SELECT content FROM parentlane.answer " \
                        "WHERE question_id = '" + str(relevant_questions[i]['id']) + "';"
            cursor = connection.cursor()
            cursor.execute(sql_query)
            records = cursor.fetchall()
            relevant_questions[i]['answers'] = list(records)
except Error as e:
    print("There was an error", e)
finally:
    if connection.is_connected():
        connection.close()
    print('conn closed')

for q in relevant_questions:
    print('answers:', q['answers'][0])


end_time = time.process_time()
time_taken = end_time - start_time
print(time_taken)
winsound.Beep(2000, 5000)
