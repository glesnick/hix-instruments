#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Thu Sep 26 16:49:59 2019

@author: glesnick
'''

import os
import numpy as np
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
    datasets[i] = data
    
    print(f'{plantype} plans: {len(data)}')

# clean data
usestates = ['AK', 'CA', 'ID', 'MT', 'OR', 'WA']

for df in datasets:
    df.columns = map(str.lower, df.columns)
    df.rename({'st': 'state'}, inplace=True)
