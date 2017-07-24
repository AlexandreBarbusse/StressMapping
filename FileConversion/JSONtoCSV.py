# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 2016

@author: Alexandre Barbusse (ComplexCity, EIVP, KTH)
"""

# This script converts a json file in csv file

import json 

benches = []

# read json file and store the content in a list
with open('bench_26918.json', 'r') as fp:
    data1 = json.load(fp) 
    for feature in data1['features']:
        benches.append(feature['properties'])
        
import csv

# get the keys for the csv file
print benches[0]
keys = benches[0].keys()

# write the content of the list into the csv output file
with open('benches.csv', 'wb') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(benches)