#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 13:59:02 2020

@author: gary
"""

import numpy as np
import pandas as pd
import re
#from datetime import datetime

listings_full = pd.read_csv('../../Data/listings_full.csv')

percent_NA = listings_full.isnull().sum() * 100 / len(listings_full)
NA_info = pd.DataFrame({'percent_NA': percent_NA})
NA_info[NA_info["percent_NA"]>5]

col_many_na = percent_NA[percent_NA > 60].index
listings_full.drop(col_many_na, axis = 1, inplace = True)

#col_var = {}
#for i in listings_full.columns:
#    col_var[i] = len(np.unique(listings_full[i]))

col_to_del = ['listing_url', 'scrape_id', 'last_scraped', 'experiences_offered',
              'picture_url', 'host_url', 'country_code', 'country', 'calendar_last_scraped']
listing1 = listings_full.drop(col_to_del, axis = 1)


percent_NA = listing1.isnull().sum() * 100 / len(listing1)
col_w_na = percent_NA[percent_NA > 0].index
a = listing1.head()[col_w_na]

# =============================================================================
# numeric variable
# =============================================================================

# convert $ into number
def to_num(x):
    x = re.sub(r',', '', x)
    return float(x[1:])

listing1['price'] = list(map(to_num, listing1['price']))
valid_ind_security = ~listing1['security_deposit'].isnull()
listing1.loc[valid_ind_security, 'security_deposit'] = list(
        map(to_num, listing1.loc[valid_ind_security, 'security_deposit']))
valid_ind_clean = ~listing1['cleaning_fee'].isnull()
listing1.loc[valid_ind_clean, 'cleaning_fee'] = list(
        map(to_num, listing1.loc[valid_ind_clean, 'cleaning_fee']))
listing1['extra_people'] = list(map(to_num, listing1['extra_people']))

def str_to_pct(x):
    x = re.sub(r'%', '', x)
    return float(x) / 100
valid_ind_host= ~listing1['host_response_rate'].isnull()
listing1.loc[valid_ind_host, 'host_response_rate'] = list(
        map(str_to_pct, listing1.loc[valid_ind_host, 'host_response_rate']))

# numeric col with na
num_col_w_na = [
        'host_response_rate', 'host_listings_count', 'host_total_listings_count',
        'bathrooms', 'bedrooms', 'beds', 'security_deposit',
        'cleaning_fee', 'review_scores_rating',
       'review_scores_accuracy', 'review_scores_cleanliness',
       'review_scores_checkin', 'review_scores_communication',
       'review_scores_location', 'review_scores_value', 'reviews_per_month']
mean_na_col = {}
for col in num_col_w_na:
    mean_na_col[col] = np.mean(listing1[col])

for col_name in num_col_w_na:
    na_row_ind = listing1[col_name].isnull()
    listing1.loc[na_row_ind, col_name] = mean_na_col[col_name]

# =============================================================================
# Qualitative Variable
# =============================================================================
#cat_col = ['host_response_time', 'host_neighbourhood', 'host_has_profile_pic',
#           'host_is_superhost', 'host_identity_verified', 'neighbourhood',
#           'city', 'state', 'market']
qualtv_col = col_w_na[~col_w_na.isin(num_col_w_na)]
for col_name in qualtv_col:
    na_row_ind = listing1[col_name].isnull()
    listing1.loc[na_row_ind, col_name] = 'Unknown'

# for columns of word description, i.e. non-categorical variables,
# convert them into binary variable of having content vs. not
col_to_binary = ['name', 'summary', 'space', 'description', 'neighborhood_overview',
       'notes', 'transit', 'access', 'interaction', 'house_rules', 'host_name',
       'host_location', 'host_about', 'host_thumbnail_url',
       'host_picture_url', 'zipcode', 'first_review', 'last_review']
for col in col_to_binary:
    binary_col_name = 'has_' + col
    listing1[binary_col_name] = (listing1[col] == 'Unknown').astype(int)

listing1.to_csv("listing_clean.csv", index = False)


    
    






