#!/usr/bin/env python
# coding: utf-8

# In[15]:


import pandas as pd
import pytrec_eval
import json
import sys
import re

def evaluate_run(run_path, qrel_path):
    run = pd.read_csv(run_path, sep = ' ', names = ['topic','Q0','id','rank','score','team'])

    #run['topic_mustbe'] = 0

    #i = 1
    #t = 0
    #for idx, row in run.iterrows():
        #if row['rank']>1:
            #run.at[idx,'topic_mustbe']=t
        #else:
            #t+=1
            #run.at[idx,'topic_mustbe']=t

#'touche2020-task2-relevance-withbaseline(1).qrels'
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
        qrels, {'map_cut', 'ndcg_cut'})

    res = evaluator.evaluate(runs)

    results = {}
    for key in res:
        results[key] = res[key]['ndcg_cut_10']
    
    filename = re.split('\.', sys.argv[1])
    with open((filename[0]+'_evaluated.json'), 'w') as f:
        json.dump(results, f)
        
evaluate_run(sys.argv[1], sys.argv[2])

