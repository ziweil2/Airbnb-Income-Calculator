import numpy as np
import pandas as pd
import re

data_calendar = pd.read_csv('../../Data/calendar.csv')
listings_full = pd.read_csv('../../Data/listings_full.csv')

# =============================================================================
# calendar
# =============================================================================

na_column = data_calendar.apply(lambda x: sum(x.isnull()), axis = 0)

def num_na(x):
    return sum(x.isnull())
na_by_id = (data_calendar
     .groupby('listing_id')
     .agg(
        num_price_na = ('price', num_na),
        num_adj_price_na = ('adjusted_price', num_na),
        num_min_night_na = ('minimum_nights', num_na),
        num_max_night_na = ('maximum_nights', num_na)
     ))

has_na_listing_id = na_by_id[na_by_id.apply(lambda x: any(x.iloc[0:4]), axis = 1)]

price_na_listing_id = na_by_id[(na_by_id['num_price_na'] > 0) | (na_by_id['num_adj_price_na'] > 0)].index
# five listings have missing data, the number of rows with missing data is around 170, almost half the 365 days,
# therefore, we delete the record of this 5 listings
len(price_na_listing_id)
data_calendar = data_calendar[~data_calendar['listing_id'].isin(price_na_listing_id)]

def to_num(x):
    x = re.sub(r',', '', x)
    return float(x[1:])
data_calendar['price'] = list(map(to_num, data_calendar['price']))
data_calendar['adjusted_price'] = list(map(to_num, data_calendar['adjusted_price']))

calendar_summary = (
        data_calendar
        .groupby('listing_id')
        .agg({
            'available': lambda x: sum(x == 't') / len(x),
            'price': np.mean,
            'adjusted_price': np.mean,
            'minimum_nights': np.mean,
            'maximum_nights': np.mean
        }))

calendar_summary = calendar_summary.reset_index()
calendar_summary.rename(columns = {'price':'price_avrg', 'adjusted_price':'adjusted_price_avrg'}, inplace=True)



# =============================================================================
# Listing
# =============================================================================

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
    listing1[binary_col_name] = (listing1[col] != 'Unknown').astype(int)

#listing1.to_csv("listing_clean.csv", index = False)





# =============================================================================
# combine
# =============================================================================

listing1.shape
calendar_summary.shape


sum(listing1['id'].isin(calendar_summary['listing_id']))
sum(calendar_summary['listing_id'].isin(listing1['id']))

listing_calendar = pd.merge(listing1, calendar_summary, 'inner',
                            left_on = 'id', right_on = 'listing_id')
listing_calendar.drop('listing_id', axis = 1, inplace = True)

listing_calendar.to_csv("listing_calendar_clean.csv", index = False)
