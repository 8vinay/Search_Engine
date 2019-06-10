import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from operator import itemgetter
from collections import Counter
import os
import string
import math
import operator
import sys
from nltk.stem.porter import PorterStemmer
import json
import time
import numpy as np

st = time.time()
data={}
cou = 0
while cou < 3000:
    cou += 1
    try:
        with open(os.path.join("./data", str(cou)+'.json'), "r") as json_file:  
            data[str(cou)] = json.load(json_file)
            data[str(cou)] = data[str(cou)]["text"]
    except Exception as e:
        data[str(cou)] = ""

porter = PorterStemmer()
stop_words = stopwords.words('english')

for i in data:
    data[i] = [re.sub('\d','',(word.replace(",","").replace(".","").replace("(","").replace(")","").replace(";","").replace("|","").replace("/","").replace("[","").replace("]","").replace("*","").replace(":","").replace("\"","").replace("!","").replace("'","").replace("=","").replace("<","").replace(">","").replace("{","").replace("}","").replace("@",""))) for word in data[i].lower().split()]
    data[i] = [word.split('_')[0] for word in data[i]]
    data[i] = [porter.stem(word) for word in data[i] if(len(word)>0)]
    data[i] = [w for w in data[i] if not w in stop_words]
    data[i] = [word for word in data[i] if (len(word)>2)]

nsw = []
for i in data:
    nsw += data[i]
nsw = set(nsw)

for i in data:
    data[i] = np.asarray(data[i])

#tf-idf
def TF(doc):
    dtf = {}
    for word in doc:
        if word in dtf:
            dtf[word] += 1
        else:
            dtf[word] = 1
              
    for word in dtf:
        dtf[word] = dtf[word] / len(doc)
    return dtf

tfDict = {}
for i in data:
    tfDict[i] = TF(data[i])

#print(tfDict)
def wordCount():
    wc = {}
    
    for doc in tfDict:
        for word in tfDict[doc]:
            if word in wc:
                wc[word] += 1
            else:
                wc[word] = 1
    return wc

wc = wordCount()

def IDF(data1):
    idfDict = {}
    for word in wc:
        idfDict[word] = math.log(len(data1) / wc[word])
    return idfDict
  
idfDict = IDF(data)
#print(idfDict)
def TF_IDF(dtf):
    ditf = {}
    
    for word in dtf:
        ditf[word] = dtf[word] * idfDict[word]
    return ditf

tfidfDict = [TF_IDF(tfDict[doc]) for doc in tfDict]

wordDict = nsw

def Vector(doc):
      tfidfVector = [0.0] * len(wordDict)
     
      for i, word in enumerate(wordDict):
          if word in doc:
              tfidfVector[i] = doc[word]
      return tfidfVector

tfidfVector = [Vector(doc) for doc in tfidfDict]

for i in range(len(tfidfDict)):
    jsonData = ({
        'tfidfDict': tfidfDict[i]
        })
    with open('tfIdf/'+str(i+1)+'.json','w') as outfile:
        json.dump(jsonData, outfile)