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

def wordCount(tfDict):
    wc = {}
    
    for doc in tfDict:
        for word in tfDict[doc]:
            if word in wc:
                wc[word] += 1
            else:
                wc[word] = 1
    return wc

def IDF(data1,wc):
    idfDict = {}
    for word in wc:
        idfDict[word] = math.log(len(data1) / wc[word])
    return idfDict

def TF_IDF(dtf, idfDict):
    ditf = {}
    
    for word in dtf:
        ditf[word] = dtf[word] * idfDict[word]
    return ditf

def Vector(doc,wordDict):
      tfidfVector = [0.0] * len(wordDict)
     
      for i, word in enumerate(wordDict):
          if word in doc:
              tfidfVector[i] = doc[word]
      return tfidfVector

def dotProduct(a, b):
    dp = 0.0
    for i,j in zip(a, b):
       dp += i*j
    return dp

def magnitude(a):
    m = 0.0
    for i in a:
      m += math.pow(i, 2)
    return math.sqrt(m)

def similarity(a,b):
    if magnitude(a) == 0 or magnitude(b) == 0:
        return 0
    return dotProduct(a,b)/ (magnitude(a) * magnitude(b))

#query
def process_query(que):
	tfidfDict=[]
	cou = 0
	while cou < 3000:
		cou += 1
		try:
			with open(os.path.join("./tfidf", str(cou)+'.json'), "r") as json_file:  
				tfidfDict.append(json.load(json_file))
				tfidfDict[cou-1] = tfidfDict[cou-1]["tfidfDict"]
		except Exception as e:
			tfidfDict[cou] = ""

	nsw = []
	docs = {}
	cou = 1
	for i in tfidfDict:
		docs[cou] = list(i.keys())
		nsw += i.keys()
		cou += 1
	nsw = set(nsw)
	wordDict = nsw

	porter = PorterStemmer()
	stop_words = stopwords.words('english')
	q = que
	queryData = 'computer science. \n' + q
	translator = str.maketrans('', '', string.punctuation)
	queryData.translate(translator)
	queryData = sent_tokenize(queryData)
	queries = {}
	c = 1
	for i in queryData:
	    queries[c] = word_tokenize(i)
	    c += 1
	 
	c = 1    
	for i in queries:
	    queries[c] = [word for word in queries[i] if re.match('\w',word)]
	    c += 1

	for i in queries:
	    queries[i] = [porter.stem(word) for word in queries[i]]
	    queries[i] = [w for w in queries[i] if not w in stop_words]
	    queries[i] = [word for word in queries[i] if (len(word)>2)]

	top200 = []
	for i in docs:
		if not set(queries[2]).isdisjoint(set(docs[i])):
		#if(set(queries[2]).issubset(set(docs[i]))):
			top200.append(i)

	top200scores = {}
	for i in top200:
		score = 0
		for j in queries[2]:
			if j in docs[i]:
				score += tfidfDict[int(i)-1][j]
		top200scores[i] = score

	top20 = sorted(top200scores.items(),reverse=True, key=operator.itemgetter(1))[:20]
	top20 = [i[0] for i in top20]

	tfidfVector = {}
	for i in top20:
		tfidfVector[i] = Vector(tfidfDict[i-1],wordDict)

	tfDict = {}
	for i in queries:
	    tfDict[i] = TF(queries[i])

	wc = wordCount(tfDict)
	idfDict = IDF(queries, wc)
	tfidfDict = [TF_IDF(tfDict[doc],idfDict) for doc in tfDict]
	tfidfVector1 = [0.0] * len(wordDict)
	tfidfVector1 = [Vector(doc,wordDict) for doc in tfidfDict]

	print(time.time()-st)

	retreived10 = []
	sim = {}
	for i in top20:
		sim[i] = similarity(tfidfVector[i],tfidfVector1[1])
	top10 = sorted(sim.items(),reverse=True, key=operator.itemgetter(1))
	#retreived10 = top10[:10]
	retreived10 = top10

	temp = retreived10
	for j in range(len(temp)):
		with open(os.path.join("./data", str(temp[j][0])+'.json'), "r") as json_file:  
			temp[j] = json.load(json_file)['url']
	
	return temp

#process_query("computer science")
#print(time.time()-st)