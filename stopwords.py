#!/usr/bin/env python
# coding: utf-8

# In[1]:


from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer 
from nltk.corpus import stopwords
import json
import nltk
nltk.download('stopwords')
nltk.download('punkt')


# In[2]:


f = open('topics.json')
topics = json.load(f)


# In[3]:


lis =[]
for i in range(len(topics)):
    x=(topics[i]['title'])
    lis.append(x)
converted_list = [x.lower() for x in lis]
print (converted_list)


# In[4]:


tokenized_sents = [word_tokenize(i) for i in converted_list]
#for i in tokenized_sents:
    #print (i)


# In[5]:


lis2 =[]
for i in tokenized_sents:
    tokens_without_sw = [word for word in i if not word in stopwords.words()]
    lemmatizer = WordNetLemmatizer()
    lemmatized_output_0 = ([lemmatizer.lemmatize(w,pos="n") for w in tokens_without_sw])
    lemmatized_output_1 = ([lemmatizer.lemmatize(w,pos="a") for w in lemmatized_output_0])
    lemmatized_output_2 = ' '.join(([lemmatizer.lemmatize(w,pos="v") for w in lemmatized_output_1]))
    lis2.append(lemmatized_output_2)   
print(lis2)


# In[7]:


lis3 =[]
for i in tokenized_sents:
    tokens_without_sw = [word for word in i if not word in stopwords.words()]
    lemmatizer = WordNetLemmatizer()
    lemmatized_output_0 = ([lemmatizer.lemmatize(w,pos="n") for w in tokens_without_sw])
    lemmatized_output_1 = ' '.join(([lemmatizer.lemmatize(w,pos="v") for w in lemmatized_output_0]))
    lis3.append(lemmatized_output_1)   
print(lis3)


# In[ ]:




