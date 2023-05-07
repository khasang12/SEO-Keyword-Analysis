#Import libraries

# packages for Vietnamese
        # !pip install underthesea
        # !pip install advertools
import requests
import nltk
import math
import re
import regex as re
import pandas as pd
import numpy as np
import statistics as stats
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import json

#You will need to download some packages from NLTK. 

from bs4 import BeautifulSoup 
from nltk.corpus import stopwords


import advertools as adv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from underthesea import word_tokenize

###### TOKENIZE SENTENCES INTO MEANINGFUL CHUNKS
def tokenizer(df):
  
  stop_words=set(adv.stopwords['vietnamese'])
  df['title'] = df['title'].map(lambda x:word_tokenize(str(x)))
  df['content'] = df['content'].map(lambda x:word_tokenize(str(x)))
  
  # handle unnecessary tokens: stopwords, digit, sign (comma, dot, brackets,..)
  df['title'] = df['title'].map(lambda x:[w.lower() for w in x if w.replace(' ','_') not in stop_words and not w.isdigit() and len(w)>1])
  df['content'] = df['content'].map(lambda x:[w for w in x if w not in stop_words and not w.isdigit() and len(w)>1])
  df['content'] = df['content'].map(lambda x:' '.join(x).lower())
  
###### GET KEYWORDS WITH LENGTH FOR EACH LINK
def get_keywords(df, content_list,ngrams):
  kw = []
  #The first function pre-processes text by lowering the case of characters, 
  #and removing special characters. 
  def pre_process(text):
      text=text.lower()
      text=re.sub("</?.*?>"," <> ",text)
      text=re.sub("(\\d|\\W)+"," ",text)
      return text

  #This function maps matrices to coordinates. The TF-IDF function maps 
  #Frequency scores to matrices, which then need to be sorted to help us find our keywords. 

  def sort_coo(coo_matrix):
      tuples = zip(coo_matrix.col, coo_matrix.data)
      return sorted(tuples, key=lambda x: (x[1], x[0]), reverse=True)

  #As with above, this is a helper function that will assist in the sorting and
  #selection of keywords once the frequencies have been mapped to matrices. 
  #This function specifically helps us to choose the most relevant keywords, 
  #based on TF-IDF statistics

  def extract_topn_from_vector(feature_names, sorted_items, topn=10):
      sorted_items = sorted_items[:topn]
      score_vals = []
      feature_vals = []

      for idx, score in sorted_items:
          fname = feature_names[idx]
          score_vals.append(round(score, 3))
          feature_vals.append(feature_names[idx])

      results= {}
      for idx in range(len(feature_vals)):
          results[feature_vals[idx]]=score_vals[idx]
      return results

  #The final function, which incorporates the above helper functions, 
  #Applies a TF-IDF algorithm to the body of our text to find keywords based
  #on frequency of usage. 
  
  iteration=1
  processed_text=[pre_process(text) for text in content_list]

  stop_words=set(adv.stopwords['vietnamese'])

  cv=CountVectorizer(max_df=0.7,stop_words=stop_words,ngram_range = ((ngrams,ngrams)))
  word_count_vector=cv.fit_transform(processed_text)
  tfidf_transformer=TfidfTransformer(smooth_idf=True,use_idf=True)
  tfidf_transformer.fit(word_count_vector)

  feature_names=cv.get_feature_names_out()

  for i in range(len(processed_text)):
    print('Getting Keywords',iteration,'/',len(content_list))
    doc=processed_text[i]
    tf_idf_vector=tfidf_transformer.transform(cv.transform([doc]))
    sorted_items=sort_coo(tf_idf_vector.tocoo())
    keys=extract_topn_from_vector(feature_names,sorted_items,10)
    kw.append(list(keys.keys()))
    iteration+=1
  return kw

def kw_extract(path):
  df = pd.read_csv(path)
  tokenizer(df)
    
  content_list = df['content'].tolist()
  kw1 = get_keywords(df,content_list,1)
  kw2 = get_keywords(df,content_list,2)
  kw3 = get_keywords(df,content_list,3)
  df['Keyword_1'] = kw1
  df['Keyword_2'] = kw2
  df['Keyword_3'] = kw3

  df = df.sort_values(by="date")
  df.to_csv('./analysis_result/extract_result.csv',index=False)
  
if __name__ == '__main__':
    df = pd.read_csv("./csv/bds_bdsvn.csv")
    tokenizer(df)
    
    content_list = df['content'].tolist()
    kw1 = get_keywords(df,content_list,1)
    kw2 = get_keywords(df,content_list,2)
    kw3 = get_keywords(df,content_list,3)
    df['Keyword_1'] = kw1
    df['Keyword_2'] = kw2
    df['Keyword_3'] = kw3

    df = df.sort_values(by="date")
    df.to_csv('./analysis_result/extract_result.csv',index=False)