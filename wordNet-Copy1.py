#!/usr/bin/env python
# coding: utf-8

# In[203]:


from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
import json
import nltk
from nltk import pos_tag
from nltk.corpus import wordnet
import re
import pickle
nltk.download('stopwords')
nltk.download('punkt')


# In[204]:


#f = open('topics.json')
#topics = json.load(f)


with open('data/topics_lemmatized.txt', 'wb') as fp:
    t_lem = pickle.load(fp)


# In[231]:


query ='difference sex love'
tokenized = word_tokenize(query)


# In[232]:


pos_tagged = nltk.pos_tag(tokenized)
satz_synonyms = []
for wort in pos_tagged:
    if  wort[1] != 'RB' and wort[1] != 'JJ' and wort[1] != 'JJS' and wort[1]!='RBR'and wort[1]!='RBS':
        for syn in wordnet.synsets(wort[0]):
            for l in syn.lemmas()[:1]:
                for n in l.name().split():
                    if n not in satz_synonyms:
                        satz_synonyms.append(n)
    else:
        satz_synonyms.append(wort[0])


# In[233]:


satz_synonyms


# In[234]:


final_satz = ' '.join(satz_synonyms)
final_satz


# In[ ]:





# In[ ]:


