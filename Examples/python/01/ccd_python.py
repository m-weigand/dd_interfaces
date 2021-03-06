#!/usr/bin/env python
# *-* coding: utf-8 *-*
# simple example on using the ccd_single module directly from Python
import lib_dd.decomposition.ccd_single as ccd_single
import lib_dd.config.cfg_single as cfg_single
import numpy as np

# import os
# import shutil
# if os.path.isdir('results'):
#     shutil.rmtree('results')
# os.makedirs('results')

frequencies = np.loadtxt('data/frequencies.dat')
data = np.loadtxt('data/data.dat')

# set options using this dict-like object
config = cfg_single.cfg_single()
config['frequency_file'] = frequencies
config['data_file'] = data
config['fixed_lambda'] = 10

ccd_obj = ccd_single.ccd_single(config)
ccd_obj.fit_data()

last_it = ccd_obj.results[0].iterations[-1]
print(dir(last_it))
print('fit parameters', last_it.m)
print('stat_pars', last_it.stat_pars)
