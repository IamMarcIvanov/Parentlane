from googletrans import Translator
import string
import pickle
from textblob import TextBlob
import re
import time
import num2words
import winsound
import torch
from scipy.spatial.distance import cosine

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
    # question.translate(str.maketrans(" ", " ", string.punctuation))  # remove punctuation
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
with open('dict_file_sentence_wise_with_embedding', 'rb') as f:
    doc_list = pickle.load(f)
print('after loading model and list:', time.process_time() - start_time)

query = re.split('[?.]', input("Enter query: ").strip(string.punctuation))
query_embedding = model.encode(query)


for doc in doc_list:
    doc['similarity'] = [max([1 - cosine(query_part_embedding, doc['embedding'][index])
                              for query_part_embedding in query_embedding]) for index, sent in enumerate(doc['text'])]
    doc['similarity'] = sum(sorted(doc['similarity'], reverse=True)[:5])/5

doc_list = sorted(doc_list, key=(lambda x: x['similarity']), reverse=True)
result = doc_list[:10]
for res in result:
    print('title:', res['title'])
    print('content:', res['text'])
    print('similarity:', res['similarity'])
    print()
print('end time:', time.process_time() - start_time)
winsound.Beep(2000, 5000)
