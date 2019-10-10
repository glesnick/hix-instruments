#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 13:40:46 2019

@author: glesnick
"""

import pandas as pd

data = pd.read_pickle('../data/2-cleaned/hix_data_PNW.pickle')

pop_data = pd.read_csv('../data/1-raw/kaiser_state_indiv_pop.csv',
                       skiprows=2)
pop_data = pop_data[~pop_data['2008__Non-Group'].isna()].drop(columns='Footnotes')

pop_data = pop_data.melt(id_vars=['Location'],
                         value_vars=[c for c in pop_data.columns
                                     if c.endswith('Non-Group')],
                         value_name='pop_nongroup')
pop_data['year'] = pop_data.variable.apply(lambda s: int(s[:4]))

state_crosswalk = pd.read_csv('../data/1-raw/state-name-abbr.csv', header=None)
state_crosswalk.columns = ['state_name', 'state']
pop_data = pop_data.merge(state_crosswalk, left_on='Location', right_on='state_name')

pop_data.drop(columns=['variable', 'Location', 'state_name'], inplace=True)

data = data.merge(pop_data, on=['state', 'year'])