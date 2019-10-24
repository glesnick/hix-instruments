#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 13:40:46 2019

@author: glesnick
"""

import pandas as pd

# define group vars, collapse vars, and weight vars

vars_group = ['year', 'area_oregon', 'carrier', 'metal', 'plantype', 'small_group']

vars_collapse = ['premi27']

var_weight = 'pop_nongroup'

# import state non-group populations

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

# merge non-group populations into HIX data

data = pd.read_pickle('../data/2-cleaned/hix_data_with_demographics.pickle')
data = data.merge(pop_data, on=['state', 'year']) 

# collapse down to constructed plan level, weighting states by non-group pop

for var in vars_collapse:
    data[f'{var}_times_weight'] = data[var] * data[var_weight]

data_pnw = data[(data.state != 'OR') & (data.in_pnw == 1)].groupby(vars_group)
data_all = data[data.state != 'OR'].groupby(vars_group)

data_collapsed_pnw = data_pnw.sum().reset_index()
data_collapsed_all = data_all.sum().reset_index()

for var in vars_collapse:
    data_collapsed_pnw[var] = (data_collapsed_pnw[f'{var}_times_weight'] /
                               data_collapsed_pnw[var_weight])
    data_collapsed_all[var] = (data_collapsed_all[f'{var}_times_weight'] /
                               data_collapsed_all[var_weight])

data_collapsed_pnw['source'] = 'pnw_states'
data_collapsed_all['source'] = 'all_states'

data_collapsed = pd.concat([data_collapsed_pnw, data_collapsed_all])
data_collapsed = data_collapsed[vars_group + vars_collapse + ['source']]

data_collapsed.to_csv('../data/2-cleaned/hix_instrument.csv')