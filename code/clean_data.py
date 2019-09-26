#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Thu Sep 26 16:49:59 2019

@author: glesnick
'''

import os
import pandas as pd

# set which HIX fields to keep
usecols = ['YEAR', 'ST', 'AREA', 'CARRIER', 'METAL', 'PLANTYPE',
           'PREMIC', 'PREMI27', 'PREMI50', 'PREMI2C30' ,'PREMC2C30']

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
carriers = {'Regence BlueCross BlueShield': 'Regence BCBS',
            'Regence BlueShield of Idaho': 'Regence BCBS',
            'Oregon\'s Health CO-OP': 'Community',
            'Health Republic': 'Health Republic',
            'Health Net': 'HealthNet',
            'Kaiser Permanente': 'Kaiser',
            'LifeWise Health Plan': 'LifeWise',
            'Moda Health': 'Moda',
            'PacificSource Health Plans': 'PacificSource',
            'Providence Health Plan': 'Providence',
            'UnitedHealthcare': 'UnitedHealthcare'}

states = ['AK', 'CA', 'ID', 'MT', 'OR', 'WA']

group = ['year', 'state', 'area', 'carrier', 'metal', 'plantype', 'small_group']

data.columns = map(str.lower, data.columns)
data.rename({'st': 'state'}, axis=1, inplace=True)

data = data[data.carrier.isin(carriers)]
data = data[data.state.isin(states)]
data.carrier = data.carrier.map(carriers)

stats = ['median', 'mean', 'min', 'max', 'count', 'std']
data = data.groupby(group).agg({'premi27': stats})
data = data.reset_index()

data.to_csv('test.csv')