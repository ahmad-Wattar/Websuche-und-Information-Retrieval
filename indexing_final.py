#!/usr/bin/env python
# coding: utf-8

# In[40]:


import sys
import os
from elasticsearch import Elasticsearch
from zipfile import ZipFile
import re
import pandas as pd
import json
import requests
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
import nltk
import pickle
import pytrec_eval
nltk.download('stopwords')
nltk.download('punkt')
from elasticsearch import NotFoundError

es = Elasticsearch()


# In[41]:


input_dir = 'data/docs'
output_dir = 'results'


# In[42]:


for filename in os.listdir():
    if filename.endswith(".zip"):
        with ZipFile(filename, 'r') as zip:
            zip.extractall()


# In[43]:


def strip_punct(s):
    s = re.sub('[^A-Za-z0-9]', ' ', s)
    s = s.lower()
    return " ".join(s.split())


# In[44]:


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


# In[45]:


def search(search_param, filename, q, ind):
    
    qid = []
    Q0 = []
    doc = []
    rank = []
    score = []
    tag = []

    num=1

    for i in q:
        for x in search_param['query']['bool']['should']:
            if type(i) == dict:
                for key in x['match']:
                    x['match'][key] = i['title']
            else:
                for key in x['match']:
                    x['match'][key] = i

    
        response = es.search(index=ind, body=search_param)
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
    df.to_csv((output_dir+'/'+filename+'.txt'), sep = ' ', index = False, header = False)


# In[46]:


def search_extended(search_param, filename, q, ind):
    qid = []
    Q0 = []
    doc = []
    rank = []
    score = []
    tag = []

    num=1
#['bool']['should']
    for idx, row in q.iterrows():
            
            #for key in x['match']:
                #x['match'][key] = row['query']
        for x in search_param['query']['bool']['should']:
            for key in x["match"]:
                #print(key)
                if "boost" in x['match'][key]:
                    x['match'][key]["query"] = row['query']
                else:
                    x['match'][key] = ' '.join(row['syn'])
        #print(search_param)
        response = es.search(index=ind, body=search_param)
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
    df.to_csv((output_dir+'/'+filename+'.txt'), sep = ' ', index = False, header = False)


# In[47]:


def create_index(b, k1, index):
    
    #create template for index
    request_body = {
    "settings" : {
	        "number_of_shards": 1,
	        "number_of_replicas": 0,
        "similarity": {
      "default": { 
        "type": "BM25",
        "b":b,
        "k1":k1
      }
    }
	    }
	}

    es.indices.create(index = index, body = request_body)
    
    
    #load data to index
    with open('data/bulk_data.json') as f:
        bulk_data = json.load(f)
        
    for x in bulk_data[::2]:
        x['index']['_index']=index
        
    bulks = chunks(bulk_data, 100)
    for x in bulks:
        res = es.bulk(index = index, body = x)
    


# In[48]:


def create_run(d, run_name, index, mode):
    #d, run_name, index
    
    if mode=='simple':
        f = open("data/topics_lemmatized.txt", 'rb')
        queries_lem = pickle.load(f)
        f.close()
        search_param = {
    
        'size': 50,
        "query": {
        "bool": {
        "should": d
        }
        }
        }
        #print(search_param)

        search(search_param, run_name, queries_lem, index)
    elif mode=='syn':
        df_syn = pd.read_csv('data/q_for_syn.tsv', sep = '\t')
        search_param = {
    
        'size': 50,
        "query": {
        "bool": {
        "should": d
        }
        }
        }

        search_extended(search_param, run_name, df_syn, index)
    else:
        print('Wrong arguments!')
        
    


# In[49]:


def evaluate_run(run_path, qrel_path):
    run = pd.read_csv(run_path, sep = ' ', names = ['topic','Q0','id','rank','score','team'])

    qrel = pd.read_csv(qrel_path, sep = ' ', names = ['topic','Q0','id','relevance'])

    qrels = {}
    for i in range(1,51):
        qrels[str(i)] = {}
    
    for idx, row in qrel.iterrows():
        qrels[str(row['topic'])][row['id']] = row['relevance']
    
    runs = {}
    for i in range(1,51):
        runs[str(i)] = {}
    
    for idx, row in run.iterrows():
        runs[str(row['topic'])][row['id']] = row['score']

    evaluator = pytrec_eval.RelevanceEvaluator(
        qrels,{'map_cut', 'ndcg_cut', 'recall', 'P'})

    res = evaluator.evaluate(runs)

    results = {}
    recall = {}
    pres = {}
    for key in res:
        results[key] = res[key]['ndcg_cut_10']
        recall[key] = res[key]['recall_10']
        pres[key] = res[key]['P_10']
        #print(res[key])
    
    filename = re.split('\.', sys.argv[1])
    with open((filename[0]+'_evaluated.json'), 'w') as f:
        json.dump(results, f)
        
    s = sum(results.values())/50
    r = sum(recall.values())/50
    p = sum(pres.values())/50
    if r+p != 0:
        f1 = (2*(r*p)/(r+p))
    else: 
        f1 = 0
    '''
    print("Average ndcg_cut_10: ", s)
    print("Average recall_10: ", r)
    print("Av. precision: ", p)
    print("F1-score: ",f1)
    '''    
    return s, r, p, f1


# In[50]:


index = 'final_0.68'
create_index(0.68, 1.2, index)


# In[51]:


#runs for args
d=[]
d.append({
          "match": {
            "title_lem": ""
          }})
create_run(d, 'run_title', index, 'simple')


d=[]
d.append({
          "match": {
            "lem": ""
          }
        })
create_run(d, 'run_doc', index, 'simple')


d=[]
d.append({
          "match": {
            "args": ""
          }
        })      
create_run(d, 'run_arg', index, 'simple')


d=[]
d.append({
          "match": {
            "title_lem": ""
          }})
d.append({
          "match": {
            "args": ""
          }
        })
create_run(d, 'run_title_arg', index, 'simple')


d=[]
d.append({
          "match": {
            "title_lem": ""
          }})
d.append({
          "match": {
            "lem": ""
          }
        })
create_run(d, 'run_title_doc', index, 'simple')


d=[]
d.append({
          "match": {
            "lem": ""
          }})
d.append({
          "match": {
            "args": ""
          }
        })
create_run(d, 'run_doc_arg', index, 'simple')


d=[]
d.append({
          "match": {
            "title_lem": ""
          }})
d.append({
          "match": {
            "lem": ""
          }
        })
d.append({
          "match": {
            "args": ""
          }
        })
create_run(d, 'run_title_doc_arg', index, 'simple')


# In[52]:


#runs for synonyms


d=[]
d.append({"match": {"title_lem": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"title_lem": {""}}})
create_run(d, 'run_title_syn', index, 'syn')


d=[]
d.append({"match": {"lem": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"lem": {""}}})
create_run(d, 'run_doc_syn', index, 'syn')


d=[]
d.append({"match": {"args": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"args": {""}}})
create_run(d, 'run_args_syn', index, 'syn')


d=[]
d.append({"match": {"title_lem": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"args": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"title_lem": {""}}})
d.append({"match": {"args": {""}}})
create_run(d, 'run_title_arg_syn', index, 'syn')


d=[]
d.append({"match": {"title_lem": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"lem": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"title_lem": {""}}})
d.append({"match": {"lem": {""}}})
create_run(d, 'run_title_doc_syn', index, 'syn')


d=[]
d.append({"match": {"lem": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"args": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"lem": {""}}})
d.append({"match": {"args": {""}}})
create_run(d, 'run_doc_arg_syn', index, 'syn')


d=[]
d.append({"match": {"title_lem": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"lem": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"args": {
                        "query":"",
                    "boost":5}}})
d.append({"match": {"title_lem": {""}}})
d.append({"match": {"lem": {""}}})
d.append({"match": {"args": {""}}})
create_run(d, 'run_title_doc_arg_syn', index, 'syn')


# In[55]:


#evaluation
run = []
ndcg = []
rec = []
prec = []
f1s = []

for filename in os.listdir(output_dir):
    if filename.endswith(".txt"):
        #print(filename)
        s, r, p, f1 = evaluate_run((output_dir+"/{}").format(filename), 'touche2020-task2-relevance-withbaseline(1).qrels')
        run.append(filename)
        ndcg.append(s)
        rec.append(r)
        prec.append(p)
        f1s.append(f1)
df = pd.DataFrame({'run':run,'ndcg_cut10':ndcg, 'recall_10':rec, 'precision':prec, 'f1-score':f1s})


# In[56]:


print(df.sort_values(by = ['ndcg_cut10'], ascending = False))


# In[39]:


#print(index)
#es.indices.delete(index=index)


# In[ ]:




