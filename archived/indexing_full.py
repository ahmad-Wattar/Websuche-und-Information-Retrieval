#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
import os
from elasticsearch import Elasticsearch
from zipfile import ZipFile
import re
import pandas as pd
import json

input_dir = sys.argv[1]
output_dir = sys.argv[2]
#input_dir = 'data/docs'
#output_dir = 'results'

es = Elasticsearch()


#extract docs from zip-files
for filename in os.listdir(input_dir):
    if filename.endswith(".zip"):
        with ZipFile((input_dir+"/{}").format(filename), 'r') as zip:
            zip.extractall(input_dir)
            

#create index, iterating over txt-files
for filename in os.listdir(input_dir):
    if filename.endswith(".txt"):
        name = re.split('_|\.', filename)
        num = next(obj for obj in name if obj.isdigit())
        with open((input_dir+"/{}").format(filename), "r") as f:
            topic = json.load(f)
            for n in topic["documents"]:
                for doc in n:
                    try:
                        b = {
                        'query': topic['title'],
                        'title': doc['title'],
                        'num': num,
                        'uuid': doc['uuid'],
                        'score': doc['score'],
                        'document': doc['document']
                            }
                        es.index(index='test_index',doc_type='doc',id=doc['trec_id'],body=b)
                    except KeyError:
                        pass
                    
                    
#create run-file
f = open("data/topics.json", encoding='utf8')
queries = json.load(f)
for i in range(len(queries)):
    queries[i]['title'] = re.sub('[?:,]', '', queries[i]['title'])
    
search_param = {
    'size': 50,
    "query": {
         'match': {
            "title": ''
        }
    }
}

qid = []
Q0 = []
doc = []
rank = []
score = []
tag = []

num=1
for i in queries:
    search_param['query']['match']['title'] = i['title']
    response = es.search(index="test_index", body=search_param)
    r = 1
    for x in response['hits']['hits']:
        qid.append(num)
        Q0.append('Q0')
        doc.append(x['_id'])
        rank.append(r)
        score.append(x['_score'])
        tag.append('uh-t2-thor')
        r+=1
    num+=1
        
qrels = {'qid': qid, 'Q0': Q0, 'doc': doc, 'rank':rank, 'score':score, 'tag':tag}
df = pd.DataFrame(qrels)
df.to_csv((output_dir+'/run.txt'), sep = ' ', index = False, header = False)


# In[3]:


#es.indices.delete(index='test_index')

