#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Thu Sep 26 16:49:59 2019

@author: glesnick
'''

import os
import pandas as pd
import numpy as np

file_cbsa = '../data/1-raw/county_cbsa_crosswalk.csv'
path_acs = '../data/1-raw/census/'

WEIGHT_METRO = 2
WEIGHT_MICRO = 1

# set which ACS fields to keep

usecols_cty = {'GEO.id2': 'county_fips',
               'HC01_VC74': 'num_households',
               'HC01_VC86': 'income_hh_mean'}

usecols_zip = {'GEO.id2': 'zipcode',
               'HC01_VC74': 'num_households',
               'HC01_VC86': 'income_hh_mean'}

# import ACS data

files_cty = [path_acs + f for f in os.listdir(path_acs) if f.startswith('acs_5yr_econ_cty')]
files_zip = [path_acs + f for f in os.listdir(path_acs) if f.startswith('acs_5yr_econ_zip')]

datasets_cty = []

for f in files_cty:
    data_temp = pd.read_csv(f, usecols=usecols_cty.keys(), dtype={'GEO.id2': object})
    data_temp['year'] = int(f[-8:-4])
    datasets_cty += [data_temp]

data_cty = pd.concat(datasets_cty)
data_cty.rename(usecols_cty, axis=1, inplace=True)

'''
datasets_zip = []

for f in files_zip:
    data_temp = pd.read_csv(f, usecols=usecols_zip.keys(), dtype={'GEO.id2': object})
    data_temp['year'] = int(f[-8:-4])
    datasets_zip += [data_temp]

data_zip = pd.concat(datasets_zip)
data_zip.rename(usecols_zip, axis=1, inplace=True)

data = pd.concat([data_cty, data_zip], sort=False)
'''

# import CBSA data

data_cbsa = pd.read_csv(file_cbsa, dtype=object)
data_cbsa['county_fips'] = data_cbsa.fipsstatecode + data_cbsa.fipscountycode
data_cbsa['metro_title'] = data_cbsa.metropolitanmicropolitanstatis
data_cbsa['metro'] = np.where(data_cbsa.metro_title == 'Metropolitan Statistical Area',
                              WEIGHT_METRO, 0)
data_cbsa['metro'] = np.where(data_cbsa.metro_title == 'Micropolitan Statistical Area',
                              WEIGHT_MICRO, data_cbsa.metro)
data_cbsa = data_cbsa[['county_fips', 'metro']]


# import county rating area crosswalks
crosswalks = [None, None]

for i, plantype in enumerate(['individual', 'small_group']):
    path = f'../data/1-raw/{plantype}/'
    files = [path + f for f in os.listdir(path) if f.startswith('county')]

    crosswalk = pd.concat([pd.read_csv(f, dtype={'fips_code': object}) for f in files])
    crosswalk['small_group'] = i
    crosswalks[i] = crosswalk

ra_crosswalk = pd.concat(crosswalks)

ra_crosswalk.rename({'fips_code': 'county_fips',
                     'rating_area_id': 'area'}, axis=1, inplace=True)
ra_crosswalk = ra_crosswalk[~ra_crosswalk.area.isna()]

# merge ACS data with crosswalks
data = ra_crosswalk.merge(data_cty, on=['county_fips', 'year'], how='left')

# merge CBSA data with crosswalks
data = data.merge(data_cbsa, on='county_fips', how='left')
data.metro = np.where(data.metro.isna(), 0, data.metro)

# collapse data to year-RA-market level
data['total_income'] = data.income_hh_mean * data.num_households
data['total_households'] = data.num_households
data['count_'] = 1

group = ['year', 'area', 'small_group']
data_collapsed = data.groupby(group).sum().reset_index()

data_collapsed['avg_hh_income'] = (data_collapsed.total_income /
                                   data_collapsed.total_households)
data_collapsed['num_hh'] = np.where(data_collapsed.rating_area_count > data_collapsed.count_,
                                    np.nan, data_collapsed.total_households)
data_collapsed['urbanity'] = data_collapsed.metro / data_collapsed.count_

data_collapsed = data_collapsed[group + ['num_hh', 'avg_hh_income', 'urbanity']]

# assign each obs to matching Oregon RAs
# sort of hacky matching scheme...

data_oregon = data_collapsed[data_collapsed.area.str.startswith('OR')]
data_oregon = data_oregon[['year', 'small_group', 'area', 'avg_hh_income', 'urbanity']]

datasets_area_added = []
for i, row in data_oregon.iterrows():
    yr = row.year
    sg = row.small_group
    ra = row.area
    inc = row.avg_hh_income
    urb = row.urbanity
    
    data_with_area = data_collapsed[(data_collapsed.year == yr) &
                                    (data_collapsed.small_group == sg) &
                                    (abs(data_collapsed.avg_hh_income - inc) <= 10000) &
                                    (abs(data_collapsed.urbanity - urb) <= .4)]
    data_with_area['area_oregon'] = ra
    
    datasets_area_added += [data_with_area]

area_correspondence = pd.concat(datasets_area_added)
area_correspondence = area_correspondence[['year', 'area', 'small_group', 'area_oregon']]

# merge back to HIX data

hix_data = pd.read_pickle('../data/2-cleaned/hix_data.pickle')
hix_data = hix_data.merge(area_correspondence, on=['area', 'year', 'small_group'],
                          how='outer')

hix_data.to_csv('../data/2-cleaned/hix_data_with_demographics.csv')
hix_data.to_pickle('../data/2-cleaned/hix_data_with_demographics.pickle')