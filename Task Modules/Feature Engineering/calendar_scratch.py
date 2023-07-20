#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 13:59:02 2020

@author: gary
"""

import numpy as np
import scipy as sp
import pandas as pd
import matplotlib
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns
import re

data_calendar = pd.read_csv('../../Data/calendar.csv')

a = (data_calendar
 .groupby('listing_id')
 .count()
 )

price_calendar = data_calendar['price'].copy()


price_calendar.isnull()

na_column = data_calendar.apply(lambda x: sum(x.isnull()), axis = 0)

na_by_id = (data_calendar
     .groupby('listing_id')
     .agg(
        num_price_na = ('price', lambda x: sum(x.isnull())),
        num_adj_price_na = ('adjusted_price', lambda x: sum(x.isnull())),
        num_min_night_na = ('minimum_nights', lambda x: sum(x.isnull())),
        num_max_night_na = ('maximum_nights', lambda x: sum(x.isnull()))
     ))

has_na_listing_id = na_by_id[na_by_id.apply(lambda x: any(x.iloc[0:4]), axis = 1)]

price_na_listing_id = na_by_id[(na_by_id['num_price_na'] > 0) | (na_by_id['num_adj_price_na'] > 0)].index
len(price_na_listing_id) # five listings have missing data of around 170, which is over one third of 365
data_calendar = data_calendar[~data_calendar['listing_id'].isin(price_na_listing_id)]

def to_num(x):
    x = re.sub(r',', '', x)
    return float(x[1:])

data_calendar['price'] = list(map(to_num, data_calendar['price']))
data_calendar['adjusted_price'] = list(map(to_num, data_calendar['adjusted_price']))

calendar_summary = (
        data_calendar
        .groupby('listing_id')
        .agg(np.nanmean))









