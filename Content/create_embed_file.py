from mysql.connector import Error
import mysql.connector
import re
import pickle
import torch
import time
import winsound

start_time = time.process_time()

doc_list = []
try:
    connection = mysql.connector.connect(host='localhost',
                                         database='parentlane',
                                         user='root',
                                         password='7happybirthdaytome@')
    sql_query = "SELECT title, text, content_type FROM parentlane.article;"
    cursor = connection.cursor()
    cursor.execute(sql_query)
    records = cursor.fetchall()
    max_len = 0
    for row in records:
        row = list(row)
        if len(row[1]) < 100:
            continue
        row[1] = re.sub(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', ' ', row[1])  # remove html stuff
        row[1] = row[1].encode('ascii', 'ignore').decode("utf-8")  # remove non-ascii characters like emoji symbols
        row[1] = (' '.join(row[1].split())).strip()  # remove extra whitespaces from between words
        doc_list.append({"title": row[0],
                         "text": list(filter(None, row[1].lower().split('.'))),
                         'content_type': row[2]})
except Error as e:
    print("Error", e)

print('after loading sql & dumping:', time.process_time() - start_time)
model = torch.load('model_file')
print('after loading model:', time.process_time() - start_time)

loop_start_time = time.process_time() - start_time
for i, doc in enumerate(doc_list):
    doc['embedding'] = model.encode(doc['text'])
    if i % 1000 == 0:
        print(i, 'iterations takes:', time.process_time() - loop_start_time)
print('after main loop:', time.process_time() - start_time)

with open('dict_file_sentence_wise_with_embedding', 'wb') as f:
    pickle.dump(doc_list, f)

winsound.Beep(2000, 5000)
