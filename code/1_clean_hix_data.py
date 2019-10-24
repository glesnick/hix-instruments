#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Thu Sep 26 16:49:59 2019

@author: glesnick
'''

import os
import pandas as pd
import numpy as np

# set which HIX fields to keep
usecols = ['YEAR', 'ST', 'AREA', 'PLANID', 'CARRIER', 'METAL', 'PLANTYPE',
           'PREMIC', 'PREMI27', 'PREMI50','PREMI2C30' ,'PREMC2C30']

# import HIX data
datasets = [None, None]

for i, plantype in enumerate(['individual', 'small_group']):
    path = f'../data/1-raw/{plantype}/'
    files = [path + f for f in os.listdir(path) if f.startswith('plans')]

    data = pd.concat([pd.read_csv(f, usecols=usecols) for f in files])
    data['small_group'] = i
    datasets[i] = data

    print(f'{plantype} plans: {len(data)}')

data = pd.concat(datasets)

# clean data

data.columns = map(str.lower, data.columns)
data.rename({'st': 'state'}, axis=1, inplace=True)

data['hios'] = data.planid.apply(lambda s: s[:14])

carriers_ = pd.read_csv('1_carrier_crosswalk.csv')
carriers = carriers_.set_index('full_name').short_name.to_dict()

group = ['year', 'state', 'area', 'carrier', 'metal', 'plantype', 'small_group']
years = [2014, 2015, 2016]

data = data[data.carrier.isin(carriers)]
data = data[data.year.isin(years)]
data.carrier = data.carrier.map(carriers)

#stats = ['median', 'mean', 'min', 'max', 'count', 'std']
#data_collapsed = data.groupby(group).agg({'premi27': stats}).reset_index()
data_collapsed = data.groupby(group).mean().reset_index()
data_collapsed = data_collapsed[group + ['premi27']]

states_pnw = ['AK', 'CA', 'ID', 'MT', 'OR', 'WA']
data_collapsed['in_pnw'] = np.where(data_collapsed.state.isin(states_pnw), 1, 0)

data_test = data_collapsed[(data_collapsed.state != 'OR')]
years_ = data_test.year.unique()
carriers_ = data_test.carrier.unique()
data_test = data_test[data_test.in_pnw == 1]
for y in years_:
    for c in carriers_:
        if len(data_test[(data_test.year == y) & (data_test.carrier == c)]) == 0:
            print(f'{y}, {c}: No HIX data for PNW states outside Oregon.')

data_collapsed.to_csv('../data/2-cleaned/hix_data.csv')
data_collapsed.to_pickle('../data/2-cleaned/hix_data.pickle')