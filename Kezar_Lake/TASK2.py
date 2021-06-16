#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from scipy.stats import kendalltau
from scipy.stats import spearmanr
from scipy.stats import pearsonr
from scipy.stats import pointbiserialr
from astropy.stats import biweight_midcorrelation
pd.set_option('display.max_rows',2000)
pd.set_option('display.max_columns',2000)
fopen = pd.read_excel('Kezar_KNN.xlsx', engine = 'openpyxl')
df = fopen.loc[:, ['CHLA (mg/L)', 'TEMPERATURE (Centrigrade)', 'Total P (mg/L)']]


# In[2]:


# correlation of temerature and TotalP to CHLA
col3 = spearmanr(df.iloc[:, 0], df.iloc[:, 0])
col5 = spearmanr(df.iloc[:, 1], df.iloc[:, 0])
col9 = spearmanr(df.iloc[:, 2], df.iloc[:, 0])


cor_1 = [col3[0], col5[0], col9[0]]


# In[3]:


col3 = kendalltau(df.iloc[:, 0], df.iloc[:, 0])
col5 = kendalltau(df.iloc[:, 1], df.iloc[:, 0])
col9 = kendalltau(df.iloc[:, 2], df.iloc[:, 0])
cor_2 = [col3[0], col5[0], col9[0]]


# In[4]:


col3 = pointbiserialr(df.iloc[:, 0], df.iloc[:, 0])
col5 = pointbiserialr(df.iloc[:, 1], df.iloc[:, 0])
col9 = pointbiserialr(df.iloc[:, 2], df.iloc[:, 0])
cor_3 = [col3[0], col5[0], col9[0]]


# In[5]:


col3 = biweight_midcorrelation(df.iloc[:, 0], df.iloc[:, 0])
col5 = biweight_midcorrelation(df.iloc[:, 1], df.iloc[:, 0])
col9 = biweight_midcorrelation(df.iloc[:, 2], df.iloc[:, 0])
cor_4 = [col3, col5, col9]


# In[6]:


col3 = pearsonr(df.iloc[:, 0], df.iloc[:, 0])
col5 = pearsonr(df.iloc[:, 1], df.iloc[:, 0])
col9 = pearsonr(df.iloc[:, 2], df.iloc[:, 0])
cor_5 = [col3[0], col5[0], col9[0]]


# In[7]:


#creating dataframe
name = ['CHLA','Temperature','Total P']
df = pd.DataFrame({'SpearmanR': cor_1,'KendallR' : cor_2,'PointB' : cor_3,'Biweight' : cor_4,'PearsonR' : cor_5},index = name)


# In[8]:


df.sort_values("PointB", inplace =True)
finished = df.iloc[::-1]


# In[9]:


finished.to_excel("Rank_sorted.xlsx")

