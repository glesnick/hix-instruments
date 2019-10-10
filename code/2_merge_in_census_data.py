#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Created on Thu Sep 26 16:49:59 2019

@author: glesnick
'''

import os
import pandas as pd

# set which ACS fields to keep

usecols_cty = {'GEO.id2': 'county_fips',
               'HC01_VC74': 'num_households',
               'HC01_VC86': 'income_hh_mean'}

usecols_zip = {'GEO.id2': 'zipcode',
               'HC01_VC74': 'num_households',
               'HC01_VC86': 'income_hh_mean'}

# import ACS data

path = '../data/1-raw/census/'
files_cty = [path + f for f in os.listdir(path) if f.startswith('acs_5yr_econ_cty')]
files_zip = [path + f for f in os.listdir(path) if f.startswith('acs_5yr_econ_zip')]

datasets = []

for f in files_cty:
    data_temp = pd.read_csv(f, usecols=usecols_cty.keys())
    data_temp['year'] = int(f[-8:-4])
    datasets += [data_temp]

data_cty = pd.concat(datasets)
data_cty.rename(usecols_cty, axis=1, inplace=True)

datasets = []

for f in files_zip:
    data_temp = pd.read_csv(f, usecols=usecols_zip.keys())
    data_temp['year'] = int(f[-8:-4])
    datasets += [data_temp]

data_zip = pd.concat(datasets)
data_zip.rename(usecols_zip, axis=1, inplace=True)

data = pd.concat([data_cty, data_zip], sort=False)

# clean data


