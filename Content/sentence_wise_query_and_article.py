import string
import pickle
import re
import time
import winsound
import torch
import numpy as np

start_time = time.process_time()

model = torch.load('model_file')
with open('dict_file_sentence_wise_with_embedding', 'rb') as f:
    doc_list = pickle.load(f)

query = re.split('[?.]', re.sub(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});', ' ',
                                input("Enter query: ")).strip(string.punctuation).lower())
query = list(filter(None, query))
query_embedding = model.encode(query)
query_type = int(input('Enter type of query:'
                       '\n0 for Baby Health'
                       '\n1 for pregnancy'
                       '\n2 for common'
                       '\n7 for fertility: '))

for doc in doc_list:
    if (doc['content_type'] == 2) or (doc['content_type'] == query_type):
        doc['similarity'] = [max([(np.matmul(query_part_embedding, doc['embedding'][index])
                                   / (np.linalg.norm(query_part_embedding) * np.linalg.norm(doc['embedding'][index])))
                                  for query_part_embedding in query_embedding])
                             for index, sent in enumerate(doc['text'])]
        doc['similarity'] = sum(sorted(doc['similarity'], reverse=True)[:5])/5
    else:
        doc['similarity'] = - 1000

doc_list = sorted(doc_list, key=(lambda x: x['similarity']), reverse=True)
result = doc_list[:10]
for res in result:
    print('title:', res['title'])
    print('similarity:', res['similarity'])
    print()

print('end time:', time.process_time() - start_time)
winsound.Beep(2000, 1000)
