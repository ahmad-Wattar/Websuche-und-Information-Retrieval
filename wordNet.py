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


f = open('topics.json')
topics = json.load(f)


# In[205]:


lis =[]
for i in range(len(topics)):
    x=(topics[i]['title'])
    lis.append(re.sub('[?:,]', '', x))
converted_list = [x.lower() for x in lis]
print ("Topics: ", converted_list)
print("\n")


# In[206]:


tokenized_sents = [word_tokenize(i) for i in converted_list]
#for i in tokenized_sents:
    #print (i)


# In[207]:


lis2 =[]
for i in tokenized_sents:
    tokens_without_sw = [word for word in i if not word in stopwords.words()]
    lemmatizer = WordNetLemmatizer()
    lemmatized_output_0 = ([lemmatizer.lemmatize(w,pos="n") for w in tokens_without_sw])
    lemmatized_output_1 = ([lemmatizer.lemmatize(w,pos="a") for w in lemmatized_output_0])
    lemmatized_output_2 = ' '.join(([lemmatizer.lemmatize(w,pos="v") for w in lemmatized_output_1]))
    lis2.append(lemmatized_output_2)   
print("Lemmatized completely: \n", lis2)
print("\n")


# In[209]:


lis3 =[]
for i in tokenized_sents:
    tokens_without_sw = [word for word in i if not word in stopwords.words()]
    lemmatizer = WordNetLemmatizer()
    lemmatized_output_0 = ([lemmatizer.lemmatize(w,pos="n") for w in tokens_without_sw])
    lemmatized_output_1 = ' '.join(([lemmatizer.lemmatize(w,pos="v") for w in lemmatized_output_0]))
    lis3.append(lemmatized_output_1)   
print("Lemmatized verbs and nouns: \n", lis3)
with open('data/topics_lemmatized.txt', 'wb') as fp:
    pickle.dump(lis3, fp)


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


