
# coding: utf-8

# ---
# 
# _You are currently looking at **version 1.1** of this notebook. To download notebooks and datafiles, as well as get help on Jupyter notebooks in the Coursera platform, visit the [Jupyter Notebook FAQ](https://www.coursera.org/learn/python-data-analysis/resources/0dhYG) course resource._
# 
# ---

# In[ ]:





# In[1]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Assignment 4 - Hypothesis Testing
# This assignment requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[ ]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[ ]:


def get_list_of_university_towns():
    univ = pd.read_csv('university_towns.txt', sep='\n', names=['RegionName'])
    univ.insert(0, 'State', univ[univ['RegionName'].str.contains('\[edit\]')])
    univ['State'] = univ['State'].fillna(method='ffill')
    univ = univ[univ['State'] != univ['RegionName']]
    univ['State'] = univ['State'].str.replace('\[edit\]', '')
    for col in univ:
        univ[col] = univ[col].str.split('(',expand=True)[0].str.split('[', expand=True)[0].str.rstrip()
    return univ


# In[ ]:


def get_gdp_table():
    excel_gdp = pd.read_excel('gdplev.xls', skiprows=7)
    gdp = pd.DataFrame()
    gdp['Quarter'] = excel_gdp['Unnamed: 4']
    gdp['GDP'] = excel_gdp['Unnamed: 6']
    gdp = gdp[gdp['Quarter'] >= "2000q1"]
    return gdp

def get_recession_start():
    gdp = get_gdp_table()
    
    gdp_diff = gdp[gdp['GDP'].diff() < 0]
    
    gdp_diff['Idx'] = gdp_diff.index
    gdp_diff['Idx_diff'] = gdp_diff['Idx'].diff()
    min_idx = gdp_diff['Idx_diff'].idxmin()
    
    return gdp['Quarter'].loc[min_idx-1]


# In[ ]:


def get_recession_end():
    gdp = get_gdp_table()
    
    gdp_diff = gdp[gdp['GDP'].diff() > 0]
    
    gdp_diff['Idx'] = gdp_diff.index
    gdp_diff['Idx_diff'] = gdp_diff['Idx'].diff()
    max_idx = gdp_diff['Idx_diff'].idxmax()
    
    return gdp['Quarter'].loc[max_idx+1]


# In[ ]:


def get_recession_bottom():
    gdp = get_gdp_table()
    start = get_recession_start()
    end = get_recession_end()

    gdp = gdp[gdp['Quarter'] >= start]
    gdp = gdp[gdp['Quarter'] <= end]
    min_idx = gdp['GDP'].idxmin()

    return gdp['Quarter'].loc[min_idx]


# In[ ]:


def convert_housing_data_to_quarters():
    def to_quarter(date):
        date = date.split('-')
        quarter = int((int(date[1]) - 1) / 3) + 1
        return date[0] + 'q' + str(quarter)

    homes = pd.read_csv('City_Zhvi_AllHomes.csv')
    
    start = homes.columns.get_loc('2000-01')
    end = homes.columns.get_loc('2016-08')
    new_homes = homes.filter(homes.columns[start:end])
    
    new_homes.insert(0, 'State', homes['State'].map(states))
    new_homes.insert(1, 'RegionName', homes['RegionName'])
    new_homes.set_index(['State', 'RegionName'], inplace=True)
    new_homes.sort_index(inplace=True)
    
    new_homes = new_homes.groupby(to_quarter, axis=1).mean()
    
    return new_homes


# In[ ]:


def run_ttest():
    # read the houses prices
    houses = convert_housing_data_to_quarters()

    # read university towns
    univ_towns = get_list_of_university_towns()
    univ_towns.set_index(['State', 'RegionName'], inplace=True)

    # get difference of prices before/at the bottom of recession
    rec_start = get_recession_start()
    rec_bottom = get_recession_bottom()
    idx_start = houses.columns.get_loc(rec_start) - 1 # before recession, not when it starts
    idx_bottom = houses.columns.get_loc(rec_bottom)

    prices = np.divide(houses.iloc[:,idx_start], houses.iloc[:,idx_bottom]).to_frame()
    prices.dropna(inplace=True)

    # get university towns and non-university towns
    univ_prices = prices.merge(univ_towns, left_index=True, right_index=True, how='inner')
    nonuniv_prices = prices.drop(univ_prices.index)

    # compute pvalue
    p_value = ttest_ind(univ_prices.values, nonuniv_prices.values).pvalue[0]

    # get university town
    better = 'non-university town'
    if univ_prices.mean().values < nonuniv_prices.mean().values:
        better='university town'

    return (p_value < 0.01, p_value, better)

