# -*- coding: utf-8 -*-
"""class_evaluation_preprocessing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15zSXUyjkSGGipu7RNKEk95Osry4wmWty
"""
import util
import shutil
import pandas as pd
import neologdn
import copy
import transformers
import sentence_transformers
# transformers.BertTokenizer = transformers.BertJapaneseTokenizer
from sentence_transformers import SentenceTransformer
from sentence_transformers import models, datasets, losses
import string
from sklearn.cluster import KMeans
import numpy as np

"""# Preprocessing text"""

file_path = "01.xlsx"


"""Normalize"""

def normalize_x(x):
  if type(x)!=str:
    x = '' # Convert to blank
  x = neologdn.normalize(x)
  return x


"""Remove stopwords and numericals"""

temp = open('stopwords-ja.txt','r').read().split('\n')
my_stopwords = temp
remove_digits = str.maketrans('0123456789', '%%%%%%%%%%')

def remove_mystopwords(sentence):
    tokens = sentence.split(" ")
    tokens_filtered= [word for word in tokens if not word in my_stopwords]
    return (" ").join(tokens_filtered)

def remove_unness_character(x):
  x = remove_mystopwords(x)
  x = x.translate(remove_digits)
  return x


"""Removing punctuation marks"""

punctuation = string.punctuation + '！’”＃＄％＾＆＊（）＿＋＝：；＜＞「」＠『』。、“■・【】●○⌒☆｀´→'
regular_punct = list(punctuation)
def remove_punctuation(text, punct_list=regular_punct):
    for punc in punct_list:
        if punc in text:
            text = text.replace(punc, ' ')
    return text.strip()

def preprocess_data(file_path):
    data = pd.read_excel(file_path, sheet_name=None, skiprows=7) #Read multiple sheets using sheet_name = None
    global df1 
    df1 = copy.deepcopy(data)
    for x in df1: 
        df1[x] = df1[x].rename(columns={df1[x].columns[0]: "Answer", df1[x].columns[1]:"First Thoughts", df1[x].columns[2]:"Post Thoughts"})
        df1[x]['First Thoughts'] = df1[x]['First Thoughts'].apply(lambda x: normalize_x(x))
        df1[x]['Post Thoughts'] = df1[x]['Post Thoughts'].apply(lambda x: normalize_x(x))
    df2 = copy.deepcopy(df1)
    for x in df2:
        df2[x]['First Thoughts'] = df2[x]['First Thoughts'].apply(lambda x: remove_unness_character(x))
        df2[x]['Post Thoughts'] = df2[x]['Post Thoughts'].apply(lambda x: remove_unness_character(x))
    df3 = copy.deepcopy(df2)
    for x in df3:
        df3[x]['First Thoughts'] = df3[x]['First Thoughts'].apply(lambda x: remove_punctuation(x))
        df3[x]['Post Thoughts'] = df3[x]['Post Thoughts'].apply(lambda x: remove_punctuation(x))
    
    data_preprocessed = copy.deepcopy(df3)

    return data_preprocessed
"""# Import Model"""


bert = models.Transformer("sonoisa/sentence-luke-japanese-base-lite")
pooling = models.Pooling(
        bert.get_word_embedding_dimension(),
        pooling_mode_mean_tokens=True,
)

model = SentenceTransformer(modules=[bert, pooling])


"""# KMEANS applying"""


def apply_kmeans(X_clustering, n_clusters):
  kmeans = KMeans(n_clusters = n_clusters, random_state=0, init='k-means++', n_init=10)
  kmeans.fit(X_clustering)
  return kmeans.labels_


def write_result(data_preprocessed, new_file):
    xl = pd.ExcelFile(new_file)
    i = 0
    for x in data_preprocessed:
      first_thoughts_clustering = model.encode(data_preprocessed[x]['First Thoughts'].to_list(), show_progress_bar=True)
      post_thoughts_clustering = model.encode(data_preprocessed[x]['Post Thoughts'].to_list(), show_progress_bar=True)
      first_thoughts_labels = apply_kmeans(first_thoughts_clustering, n_clusters=6)
      post_thoughts_labels = apply_kmeans(post_thoughts_clustering, n_clusters=6)


      df_first_thoughts = df1[x][['Answer', 'First Thoughts']]
      df_first_thoughts['first_thoughts_group'] = first_thoughts_labels
      df_first_thoughts = df_first_thoughts.sort_values('first_thoughts_group')

      df_post_thoughts = df1[x][['Answer', 'Post Thoughts']]
      df_post_thoughts['post_thoughts_group'] = post_thoughts_labels
      df_post_thoughts = df_post_thoughts.sort_values('post_thoughts_group')

      #Write clusterd result to excel
      with pd.ExcelWriter(new_file, mode='a', if_sheet_exists='replace') as writer:  
        df_first_thoughts.to_excel(writer, sheet_name=xl.sheet_names[i]+'_clustered')
      
      with pd.ExcelWriter(new_file, mode='a', if_sheet_exists='overlay') as writer:  
          df_post_thoughts.to_excel(writer, startcol=7, sheet_name=xl.sheet_names[i]+'_clustered')
      
      i+=1

if __name__ == "__main__":
    new_file = file_path.replace('.xlsx', '')+"_clustered.xlsx"
    shutil.copy(file_path, new_file)
    data_preprocessed = preprocess_data(new_file)
    write_result(data_preprocessed, new_file)
