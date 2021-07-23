#!/usr/bin/env python
# coding: utf-8

# In[12]:


import xml.etree.ElementTree as ET
import requests
from string import punctuation 
import json
import pickle
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
import nltk
from nltk import pos_tag
from nltk.corpus import wordnet
import re
import pandas as pd
nltk.download('stopwords')
nltk.download('punkt')
import sys
import os
from zipfile import ZipFile
import pytrec_eval
from boilerpy3 import extractors
from urllib.error import HTTPError
from elasticsearch import Elasticsearch
from elasticsearch import NotFoundError


# In[19]:


input_dir = 'data_final'
output_dir = 'results_final'

#input_dir = sys.argv[1]
#output_dir = sys.argv[2]


# In[2]:


#parse the XML-file with queries

mytree = ET.parse(input_dir+'/topics-task-2-only-titles.xml')
myroot = mytree.getroot()

#preprocess the queries
q = []
topics = []
for item in myroot:
    d = {}
    for x in item:
        d[x.tag] = x.text.strip('\n')
        #print(d)
        
        if x.tag == "title":
            #append the query to an array
            q.append(x.text)
    topics.append(d)
    
#save topics as json
#with open(input_dir+'/topics_final.json', 'w') as file:
#    json.dump(topics, file)
    
results = []
chatnoir = "https://www.chatnoir.eu/api/v1/_search"
attr = {"apikey": "7dd15626-53aa-46c6-bd34-b2feaa2d9d81",
        "query": "hello world",
        "index": "cw12",
        "pretty": True
}

for x in q:
    attr["query"] = x
    #somehow index doesn't work correctly when passed as an array (it only searches the 1st index of the array), so search
    #in each index separately and sum up the results
    response = requests.post(chatnoir, data = attr)
    res = response.json()["meta"]["total_results"]
    
    results.append(res)
    
#save results as txt

#with open(input_dir+"/results_final.txt", "wb") as fp:   #Pickling
#    pickle.dump(results, fp)


# In[7]:


#RETRIEVAL
#open the file with topics
#f = open(input_dir+"/topics_final.json", encoding='utf8')
#topics = json.load(f)

#open the file with amount of results for each topic
#with open(input_dir+"/results_final.txt", "rb") as fp:   # Unpickling
#    results = pickle.load(fp)
 
#preprocess the queries
for i in range(len(topics)):
    topics[i]['title'] = topics[i]['title'].replace(' ', ' AND ')
    topics[i]['title'] = re.sub('[?:,]', '', topics[i]['title'])
    topics[i]['results'] = results[i]
    
attr = {"apikey": "7dd15626-53aa-46c6-bd34-b2feaa2d9d81",
        "query": "",
        "index": "cw12",
        "size": 10
       }

#save first 110 docs for each topic
extractor = extractors.ArticleExtractor()
def topics_iter(q):
    docs = []
    attr["query"] = q['title']
    #attr['size'] = q['results']
    if q['results']<=110:
        num_of_res = q['results']
    else:
        num_of_res = 110
    count = 0
    print(attr)
    print(num_of_res)
    url = "https://www.chatnoir.eu/api/v1/_search?"
    while count < num_of_res:
        attr["from"] = count
        while True:
            try:
                r = requests.post(url, json = attr)
                res = r.json()
                print(count)
                #print(res)
                res_len = len(res['results'])
                print(res_len)
            except KeyError:
                continue
            break
        
    
        for i in range(res_len):
            
            doc_url = "https://www.chatnoir.eu/cache?uuid="+res['results'][i]['uuid']+"&index=cw12&raw"
            #print(doc_url)
            try:
                doc = extractor.get_doc_from_url(doc_url)
                content = doc.content
                title = doc.title
                res['results'][i]['document'] = content
            except HTTPError:
                print("HTTPError")
                continue
        docs.append(res['results'])
        count+=10
        
    return docs


# In[8]:


for q in topics:
    q['documents'] = topics_iter(q)
    with open(input_dir+"/docs_final/docs_for_topic_{}.txt".format(q['number']), "w") as f:
        json.dump(q, f)
        
    f.close()


# In[10]:


#lemmatize topics
#f = open(input_dir+'/topics_final.json')
#topics = json.load(f)
#f.close()
lis =[]
for i in range(len(topics)):
    x=(topics[i]['title'])
    lis.append(re.sub('[?:,]', '', x))
converted_list = [x.lower() for x in lis]
#print ("Topics: ", converted_list)
#print("\n")

tokenized_sents = [word_tokenize(i) for i in converted_list]
#for i in tokenized_sents:
    #print (i)
lis3 =[]

for i in tokenized_sents:
    tokens_without_sw = [word for word in i if not word in stopwords.words()]
    lemmatizer = WordNetLemmatizer()
    lemmatized_output_0 = ([lemmatizer.lemmatize(w,pos="n") for w in tokens_without_sw])
    lemmatized_output_1 = ' '.join(([lemmatizer.lemmatize(w,pos="v") for w in lemmatized_output_0]))
    lis3.append(lemmatized_output_1)   
#print("Lemmatized verbs and nouns: \n", lis3)
#with open(input_dir+'/topics_final_lemmatized.txt', 'wb') as fp:
#    pickle.dump(lis3, fp)
#fp.close()


# In[ ]:


#create and save bulk data for index
#input_dir = 'data/docs_final'
#output_dir = 'res'
def strip_punct(s):
    s = re.sub('[^A-Za-z0-9]', ' ', s)
    s = s.lower()
    return " ".join(s.split())

count = 0
c=0
t = 1
url = 'https://demo.webis.de/targer-api/classifyCombo'
headers = {'accept': 'application/json', 'Content-Type': 'text/plain'}
bulk_data = []
#extract docs from zip-files
for filename in os.listdir(input_dir+'/docs_final'):
    if filename.endswith(".zip"):
        with ZipFile((input_dir+"/{}").format(filename), 'r') as zip:
            zip.extractall(input_dir)
            
for filename in os.listdir(input_dir+'/docs_final'):
    if filename.endswith(".txt"):
        name = re.split('_|\.', filename)
        num = next(obj for obj in name if obj.isdigit())
        with open((input_dir+"/{}").format(filename), "r") as f:
            topic = json.load(f)
            topic['title'] = strip_punct(topic['title']).lower()
            print(filename)
            print(topic['title'])
            print(t)
            t+=1
            for n in topic["documents"]:
                print(len(n))
                if count<10:
                    count+=1
                    for doc in n:
                        try:
                            doc_raw = doc['document'].rstrip('\n')
                            doc_raw = doc_raw.rstrip('\\n')
                            
                            doc['lem'] = word_tokenize(strip_punct(doc_raw).lower())
                            tokens_without_sw = [word for word in doc['lem'] if not word in stopwords.words()]
                            lemmatizer = WordNetLemmatizer()
                            lemmatized_output_0 = ([lemmatizer.lemmatize(w,pos="n") for w in tokens_without_sw])
                            doc['lem'] = ' '.join(([lemmatizer.lemmatize(w,pos="v") for w in lemmatized_output_0]))
                            doc['lem'] = doc['lem'].rstrip()
                            
                            title_lem = strip_punct(doc['title'].lower().rstrip())
                            title_lem = word_tokenize(title_lem)
                            tokens_without_sw = [word for word in title_lem if not word in stopwords.words()]
                            lemmatizer = WordNetLemmatizer()
                            lemmatized_output_0 = ([lemmatizer.lemmatize(w,pos="n") for w in tokens_without_sw])
                            title_lem = ' '.join(([lemmatizer.lemmatize(w,pos="v") for w in lemmatized_output_0]))
                            
                            
                            
                            b = {
                                    'query': topic['title'],
                                    'title': doc['title'],
                                    'title_lem': title_lem,
                                    'num': num,
                                    'uuid': doc['uuid'],
                                    'score': doc['score'],
                                    'document': doc['document'],
                                    'lem': doc['lem']
                                }

                            templ = {'index': {'_index': 'test_index', 
                                           '_type': 'doc', 
                                           '_id': doc['trec_id']}}
                            bulk_data.append(templ)
                            bulk_data.append(b)

                            c+=1
                        except KeyError:
                            pass
                else:
                    break
            count=0
            
#with open(input_dir+"/bulk_data_final.json", "w") as f:
#    json.dump(bulk_data,f)


# In[7]:


#create synonyms
#with open(input_dir+'/topics_final_lemmatized.txt', 'rb') as f:
#    queries_lem = pickle.load(f)
#f.close()
df = pd.DataFrame(columns = ['query', 'syn'])
df['query'] = queries_lem
#print(df)
#df.to_csv(input_dir+'/q_for_syn_final.tsv', sep = '\t')

#define words for synonyms in the .tsv file manually!


# In[8]:


#df = pd.read_csv(input_dir+'/q_for_syn_final.tsv', sep = '\t')
#df = df.fillna(0)

for idx, row in df.iterrows():
    if row['query']!=0:
        tokenized = word_tokenize(row['query'])
        pos_tagged = nltk.pos_tag(tokenized)
        satz_synonyms = []
        for wort in pos_tagged:
            if  wort[1] != 'RB' and wort[1] != 'JJ' and wort[1] != 'JJS' and wort[1]!='RBR'and wort[1]!='RBS':
                #print(wort[0])
                for syn in wordnet.synsets(wort[0]):
                    for l in syn.lemmas()[:1]:
                        for n in l.name().split():
                            if n not in satz_synonyms:
                                satz_synonyms.append(n)
        else:
            satz_synonyms.append(wort[0])
        s = ' '.join(str(v) for v in satz_synonyms)
        s = ''.join(s)
        s = s.split('_')
        s = ' '.join(s)
        #print(s)
        df.at[idx,['syn']] = s
#df.to_csv(input_dir+'/q_for_syn_final.tsv', sep = '\t', index = False)


# In[17]:


#create index

es = Elasticsearch()

'''
for filename in os.listdir(input_dir):
    if filename.endswith(".zip"):
        with ZipFile(filename, 'r') as zip:
            zip.extractall()
'''            
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

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
                    x['match'][key] = row['syn']
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
    df.to_csv((output_dir+'/'+'run.txt'), sep = ' ', index = False, header = False)
    
    
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
    #with open(input_dir+'/bulk_data_final.json') as f:
    #    bulk_data = json.load(f)
        
    for x in bulk_data[::2]:
        x['index']['_index']=index
        
    bulks = chunks(bulk_data, 100)
    for x in bulks:
        res = es.bulk(index = index, body = x)
    
def create_run(d, run_name, index, mode):
    #d, run_name, index
    
    if mode=='simple':
        #f = open(input_dir+"/topics_final_lemmatized.txt", 'rb')
        #queries_lem = pickle.load(f)
        #f.close()
        queries_lem = lis3
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
        #df_syn = pd.read_csv(input_dir+'/q_for_syn.tsv', sep = '\t')
        search_param = {
    
        'size': 50,
        "query": {
        "bool": {
        "should": d
        }
        }
        }
        #print(search_param)

        search_extended(search_param, run_name, df, index)
    else:
        print('Wrong arguments!')
        
index = 'final_0.68'
create_index(0.68, 1.2, index)

#create run for doc+title with synonyms
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


# In[16]:


es.indices.delete(index=index)

