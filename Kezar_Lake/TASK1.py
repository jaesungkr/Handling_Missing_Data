#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import math
from sklearn.impute import KNNImputer
#my own output setting
pd.set_option('display.max_rows',2000)
pd.set_option('display.max_columns',2000)

# Open the xlsx file and naming each
sheets = pd.read_excel('Kezar Lake.xlsx', engine='openpyxl', sheet_name=[0, 1, 2])
CH = sheets[0] #chila   
TT = sheets[1] #temperature
TP = sheets[2] #total p


# In[2]:


# set last three of columns. Because Midas,lake,town,station columns are all same 
# so we're skipping those 
CH = CH.loc[:,['Date','Depth', CH.columns.values[6]]]
CH = CH.sort_values(by = 'Date')

TT.rename(columns={'DEPTH':'Depth'}, inplace=True)
TT = TT.loc[:,['Date','Depth', TT.columns.values[6]]]
TT = TT.sort_values(by = 'Date')

TP = TP.loc[:,['Date','Depth', TP.columns.values[6]]]
TP = TP.sort_values(by = 'Date')


# In[3]:


#initialize
#1993-06
comparingYear = CH.loc[0,'Date'].year
comparingMonth = CH.loc[0, 'Date'].month
comparingDepth = CH.loc[0, CH.columns.values[1]]
chila = CH.loc[0, CH.columns.values[2]]
count = 1
k = 0
depth_list = []
chila_list = []


# In[4]:


if comparingMonth != 5: # only applied in chla file
    depth_list.append(np.nan)
    chila_list.append(np.nan)


# In[5]:


for com in CH.itertuples():
    # generate comparison target
    index = com[0]
    year = com[1].year
    month = com[1].month
    depth = com[2]
    newChila = com[3]
    
    #for last row
    # this part is the main difference between Chla, temperature and total p
    if k == len(CH) -1 :       
        chilaDivided = chila / count
        depthDivided = comparingDepth / count
        chila_list.append(chilaDivided)
        depth_list.append(depthDivided)
        
        chila_list.append(newChila)
        depth_list.append(depth)
        if (month == 9):
            depth_list.append(np.nan)
            chila_list.append(np.nan)
        continue
    k += 1
     # when year gets past
    if (comparingYear != year):
        chilaDivided = chila / count
        depthDivided = comparingDepth / count
        chila_list.append(chilaDivided)
        depth_list.append(depthDivided)
        if (comparingMonth == 9):
            depth_list.append(np.nan)
            chila_list.append(np.nan)
    
        if (month == 6):
            depth_list.append(np.nan)
            chila_list.append(np.nan)
        
        ##reformatting
        comparingYear = year
        comparingMonth = month
        comparingDepth = com[2]
        chila = com[3]
        count = 1
        continue
        #for the first row
    if index == 0:
        continue
        #to avoid testing same row
    if index == CH.index[k]:
        k -= 1
        continue
        
        #when years are same but not months
    if (comparingYear == year) and (comparingMonth != month):
        
        chilaDivided = chila / count
        depthDivided = comparingDepth / count
        chila_list.append(chilaDivided)
        depth_list.append(depthDivided)
        if (comparingYear == year) and (month - comparingMonth == 2):
            depth_list.append(np.nan)
            chila_list.append(np.nan)
        
        comparingYear = year
        comparingMonth = month
        comparingDepth = com[2]
        chila = com[3]
        count = 1
        continue
        # year and month are same so we need to get mean of these
    if (comparingYear == year) and (comparingMonth == month):
        chila += newChila
        comparingDepth += depth
        count += 1
        comparingYear = year
        comparingMonth = month
        continue
        
#new chila_list and depth_list created with nan imputed
newDate = []
for newYear in range(1993, 2008):
    
    if newYear == 1995:
            continue
    for month in range(5, 11):
        newDate.append(pd.to_datetime(str(newYear) + '-' + str(month) + '-1'))

processed_df = pd.DataFrame({'Date': newDate, 'Depth': depth_list, 'CHLA (mg/L)': chila_list})


# In[6]:


KNNCH = processed_df.copy()


# In[7]:


# getValue is to get Chla, temperature, and total P on designated date
def getValue(df, date):
    #if theres no unknown, return result
    if math.isnan(df[df['Date'] == date].iloc[0, 2]) == False:
        result = df[df['Date'] == date].iloc[0, 2]
    else:
        #there are only difference in May and Oct
        if date.month == 5:
            # for May, use June July
            post1 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(6)))
            post2 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(7)))
            result = (post1 + post2) / 2
            
            
        elif date.month == 6:
            post1 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(5)))
            post2 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(7)))
            result = (post1 + post2) / 2
            
            
        elif date.month == 7:
            post1 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(6)))
            post2 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(8)))
            result = (post1 + post2) / 2
            
            
        elif date.month == 8:
            post1 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(7)))
            post2 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(9)))
            result = (post1 + post2) / 2
            
            
        elif date.month == 9:
            post1 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(8)))
            post2 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(10)))
            result = (post1 + post2) / 2
            
            
        elif date.month == 10:
            # for October, use Auguust, Sept
            post1 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(9)))
            post2 = getValue(df, pd.to_datetime(str(date.year)+'-'+str(8)))
            result = (post1 + post2) / 2
            
    return result


# In[8]:


# same mean imputation with above function excpet returning depth
#testing = []
def getDepth(df3, date):
    # print(date)
    df = df3.copy(deep=True)
   # processed_df[processed_df['Date'] == date].iloc[0,1]
    if math.isnan(df[df['Date'] == date].iloc[0, 1]) == False:
        result2 = df[df['Date'] == date].iloc[0, 1]
    else:
        #same processes as getValue
        if date.month == 5:
            p1 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(6)))
            p2 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(7)))
            result2 = (p1 + p2) / 2
            
            
        elif date.month == 6:
            p1 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(5)))
            p2 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(7)))
            result2 = (p1 + p2) / 2
            
            
        elif date.month == 7:
            p1 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(6)))
            p2 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(8)))
            result2 = (p1 + p2) / 2
            
            
        elif date.month == 8:
            p1 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(7)))
            p2 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(9)))
            result2 = (p1 + p2) / 2
            
            
        elif date.month == 9:
            p1 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(8)))
            p2 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(10)))
            result2 = (p1 + p2) / 2
            
            
        elif date.month == 10:
            p1 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(9)))
            p2 = getDepth(df, pd.to_datetime(str(date.year)+'-'+str(8)))
            result2 = (p1 + p2) / 2
            
       
        
    return result2


# In[9]:


# mean imputation with using above methods and build Chla dataframe 
for com2 in processed_df.itertuples():
    date = pd.to_datetime(str(com2[1].year)+'-'+str(com2[1].month))
    output = getValue(processed_df, date)
    processed_df.iloc[com2[0], 2] = output  
    # for depths
    output2 = getDepth(processed_df, date)
    processed_df.iloc[com2[0], 1] = output2
    
ChlaFinal = pd.DataFrame({"MIDAS":97, "Lake":"Kezar Lake", "Town":"Lovell,Stow", "Station":1,
                    "Date":processed_df['Date'], "Depth":processed_df.iloc[:, 1],
                    "CHLA (mg/L)":processed_df.iloc[:, 2]})


# In[10]:


#/////////////////////////////////////////////////////////////CHLA ENd
# Belows are for Temperature and TotalP. The whole processes are same except for beginning of pre-processing part ( where I handle the last row)
# I was planned to merge all three processes into one method, but I became short on time. But there's no problem with running perfectly


# In[11]:


for index, date in enumerate(TT.Date):
    if date.year == 1995:
        TT.drop(index, inplace = True)
comparingYear = TT.loc[0,'Date'].year
comparingMonth = TT.loc[0, 'Date'].month
comparingDepth = TT.loc[0, TT.columns.values[1]]
temp = TT.loc[0, TT.columns.values[2]]
count = 1
k = 0
depth_list = []
temp_list = []
if comparingMonth != 5:
    depth_list.append(np.nan)
    temp_list.append(np.nan)


# In[12]:


for com in TT.itertuples():
    index = com[0]
    year = com[1].year
    month = com[1].month
    depth = com[2]
    newChila = com[3]
    
    if k == len(TT) -1 :      
        temp += newChila
        comparingDepth += depth
        count += 1
        
        tempDivided = temp / count
        depthDivided = comparingDepth / count
        temp_list.append(tempDivided)
        depth_list.append(depthDivided)
        
       
        if (month == 9):
            depth_list.append(np.nan)
            temp_list.append(np.nan)
        continue
    k += 1
 
    if (comparingYear != year):
        tempDivided = temp / count
        depthDivided = comparingDepth / count
        temp_list.append(tempDivided)
        depth_list.append(depthDivided)
        if (comparingMonth == 9):
            depth_list.append(np.nan)
            temp_list.append(np.nan)
    
        if (month == 6):
            depth_list.append(np.nan)
            temp_list.append(np.nan)
        
        ##reformatting
        comparingYear = year
        comparingMonth = month
        comparingDepth = com[2]
        temp = com[3]
        count = 1
        continue
        
    if index == 0:
        continue
        
    if index == TT.index[k]:
        k -= 1
        continue
        
    if (comparingYear == year) and (comparingMonth != month):
        
        tempDivided = temp / count
        depthDivided = comparingDepth / count
        temp_list.append(tempDivided)
        depth_list.append(depthDivided)
        if (comparingYear == year) and (month - comparingMonth == 2):
            depth_list.append(np.nan)
            temp_list.append(np.nan)
        
        comparingYear = year
        comparingMonth = month
        comparingDepth = com[2]
        temp = com[3]
        count = 1
        continue
        
    if (comparingYear == year) and (comparingMonth == month):
        temp += newChila
        comparingDepth += depth
        count += 1
        comparingYear = year
        comparingMonth = month
        continue
        
#new temp_list and depth_list created with nan imputed
newDate = []
for newYear in range(1993, 2008):
    #there's no value on 1995 
    if newYear == 1995:
            continue
    for month in range(5, 11):
        newDate.append(pd.to_datetime(str(newYear) + '-' + str(month) + '-1'))

processed_dfTT = pd.DataFrame({'Date': newDate, 'Depth': depth_list, 'TEMPERATURE (Centrigrade)': temp_list})


# In[13]:


KNNTT = processed_dfTT.copy()


# In[14]:



for com2 in processed_dfTT.itertuples():
    date = pd.to_datetime(str(com2[1].year)+'-'+str(com2[1].month))
    output = getValue(processed_dfTT, date)
    processed_dfTT.iloc[com2[0], 2] = output  
    
    output2 = getDepth(processed_dfTT, date)
    processed_dfTT.iloc[com2[0], 1] = output2
    
TtFinal = pd.DataFrame({"MIDAS":97, "Lake":"Kezar Lake", "Town":"Lovell,Stow", "Station":1,
                    "Date":processed_df['Date'], "Depth":processed_dfTT.iloc[:, 1],
                    "Temperature (Centrigrade)":processed_dfTT.iloc[:, 2]})


# In[15]:


#/////////////////////////// temperature finished


# In[16]:


for index, date in enumerate(TP.Date):
    if date.year == 1995:
        TP.drop(index, inplace = True)
comparingYear = TP.loc[0,'Date'].year
comparingMonth = TP.loc[0, 'Date'].month
comparingDepth = TP.loc[0, TP.columns.values[1]]
tptemp = TP.loc[0, TP.columns.values[2]]
count = 1
k = 0
depth_list = []
tptemp_list = []
if comparingMonth != 5:
    depth_list.append(np.nan)
    tptemp_list.append(np.nan)


# In[17]:


for com in TP.itertuples():
    index = com[0]
    year = com[1].year
    month = com[1].month
    depth = com[2]
    newChila = com[3]
    
    if k == len(TP) -1 :      
     
        tptempDivided = tptemp / count
        depthDivided = comparingDepth / count
        tptemp_list.append(tptempDivided)
        depth_list.append(depthDivided)
        
        tptemp_list.append(newChila)
        depth_list.append(depth)
       
        if (month == 9):
            depth_list.append(np.nan)
            tptemp_list.append(np.nan)
        continue
        
    k += 1
 
    if (comparingYear != year):
        tptempDivided = tptemp / count
        depthDivided = comparingDepth / count
        tptemp_list.append(tptempDivided)
        depth_list.append(depthDivided)
        if (comparingMonth == 9):
            depth_list.append(np.nan)
            tptemp_list.append(np.nan)
    
        if (month == 6):
            depth_list.append(np.nan)
            tptemp_list.append(np.nan)
        
        ##reformatting
        comparingYear = year
        comparingMonth = month
        comparingDepth = com[2]
        tptemp = com[3]
        count = 1
        continue
        
    if index == 0:
        continue
        
    if index == TP.index[k]:
        k -= 1
        continue
        
    if (comparingYear == year) and (comparingMonth != month):
        
        tptempDivided = tptemp / count
        depthDivided = comparingDepth / count
        tptemp_list.append(tptempDivided)
        depth_list.append(depthDivided)
        if (comparingYear == year) and (month - comparingMonth == 2):
            depth_list.append(np.nan)
            tptemp_list.append(np.nan)
        
        comparingYear = year
        comparingMonth = month
        comparingDepth = com[2]
        tptemp = com[3]
        count = 1
        continue
        
    if (comparingYear == year) and (comparingMonth == month):
        tptemp += newChila
        comparingDepth += depth
        count += 1
        comparingYear = year
        comparingMonth = month
        continue
        
#new temp_list and depth_list created with nan imputed
newDate = []
for newYear in range(1993, 2008):
    #there's no value on 1995 
    if newYear == 1995:
            continue
    for month in range(5, 11):
        newDate.append(pd.to_datetime(str(newYear) + '-' + str(month) + '-1'))

processed_dfTP = pd.DataFrame({'Date': newDate, 'Depth': depth_list, 'TEMPERATURE (Centrigrade)': tptemp_list})


# In[18]:


KNNTP = processed_dfTP.copy()


# In[19]:



for com2 in processed_dfTP.itertuples():
    date = pd.to_datetime(str(com2[1].year)+'-'+str(com2[1].month))
    output = getValue(processed_dfTP, date)
    processed_dfTP.iloc[com2[0], 2] = output  
    
    output2 = getDepth(processed_dfTT, date)
    processed_dfTP.iloc[com2[0], 1] = output2
    
TpFinal = pd.DataFrame({"MIDAS":97, "Lake":"Kezar Lake", "Town":"Lovell,Stow", "Station":1,
                    "Date":processed_df['Date'], "Depth":processed_dfTP.iloc[:, 1],
                    "Total P (mg/L)":processed_dfTP.iloc[:, 2]})


# In[20]:


# All three finished ChlaFinal TtFinal TpFinal


# In[21]:


#concat three and export
Mean = pd.DataFrame({"MIDAS":97, "Lake":"Kezar Lake", "Town":"Lovell Stow", "Station":1,
                       "Date":ChlaFinal['Date'].dt.date, "Depth":0, "CHLA (mg/L)":ChlaFinal.iloc[:, 6],
                  "TEMPERATURE (Centrigrade)":TtFinal.iloc[:, 6],
                   "Total P (mg/L)":TpFinal.iloc[:, 6]})


# In[22]:


# KNN 
# pre-processed files from above : KNNCH, KNNTT, KNNTP


# In[23]:


#extracting date and 
#KNNCH.isnull().sum()
# invalid literal for 1993-05. to impute with KNN, only month should be imputed
month = [int(x[5:7])for x in KNNCH['Date'].astype(str).tolist()]
temp_df = pd.DataFrame({"Month":month, "Chla": KNNCH.iloc[:, 2].tolist()})


# In[24]:


imputer = KNNImputer(n_neighbors=4)
df = pd.DataFrame(imputer.fit_transform(temp_df),columns = temp_df.columns)


# In[25]:


newKNNCH = pd.DataFrame({"MIDAS":97, "Lake":"Kezar Lake", "Town":"Lovell,Stow", "Station":1,
                    "Date":KNNCH['Date'], "Depth":0,
                    "CHLA (mg/L)":df.iloc[:, 1]})


# In[26]:


month = [int(x[5:7])for x in KNNTT['Date'].astype(str).tolist()]
temp_df = pd.DataFrame({"Month":month, "Temperature": KNNTT.iloc[:, 2].tolist()})


# In[27]:


df = pd.DataFrame(imputer.fit_transform(temp_df),columns = temp_df.columns)


# In[28]:


newKNNTT = pd.DataFrame({"MIDAS":97, "Lake":"Kezar Lake", "Town":"Lovell,Stow", "Station":1,
                    "Date":KNNCH['Date'], "Depth":0,
                    "TEMPERATURE (Centrigrade)":df.iloc[:, 1]})


# In[29]:


month = [int(x[5:7])for x in KNNTP['Date'].astype(str).tolist()]
temp_df = pd.DataFrame({"Month":month, "TotalP": KNNTP.iloc[:, 2].tolist()})


# In[30]:


df = pd.DataFrame(imputer.fit_transform(temp_df),columns = temp_df.columns)


# In[31]:


newKNNTP = pd.DataFrame({"MIDAS":97, "Lake":"Kezar Lake", "Town":"Lovell,Stow", "Station":1,
                    "Date":KNNCH['Date'], "Depth":0,
                    "Total P (mg/L)":df.iloc[:, 1]})


# In[32]:


#concat three and expoxt
KNN = pd.DataFrame({"MIDAS":97, "Lake":"Kezar Lake", "Town":"Lovell Stow", "Station":1,
                       "Date":ChlaFinal['Date'].dt.date, "Depth":0, "CHLA (mg/L)":newKNNCH.iloc[:, 6],
                  "TEMPERATURE (Centrigrade)":newKNNTT.iloc[:, 6],
                   "Total P (mg/L)":newKNNTP.iloc[:, 6]})


# In[33]:


# save both mean and KNN
Mean.to_excel("Kezar_Mean.xlsx", index=False)
KNN.to_excel("Kezar_KNN.xlsx", index = False)


# In[ ]:




