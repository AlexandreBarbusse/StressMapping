# -*- coding: utf-8 -*-
"""
Created by Alexandre Barbusse (ComplexCity, EIVP, KTH)
July 2016
"""
# this script allows you to upload and store all the flickr photo information from a specific query

import json
from datetime import date, timedelta
import time as t
import requests

#choose the path in order to upload the photos
path='C:/Stage_Shanghai/Donnees/flickr/anxious/'

#choose the starting date
d1 = date(2007, 7, 18)
oneDay = timedelta(days=1)
d2 = d1 + oneDay

# get 2 years worth of data
for i in range(1, 3000):
    #initialize
	d2 = d1 + oneDay

	params = {'method': 'flickr.photos.search', 'format' : 'json', 'woe_id' : 2459115, 'api_key', 'min_taken_date':str(d1), 'max_taken_date':str(d2), 'has_geo':1, 'tags':'anxious', 'extras':'geo'}
	data = requests.get('https://api.flickr.com/services/rest/', params=params)
      # select the path to one particular photo 
	dataFile = open(path + str(d1) + "-photos.json","w+")
      # write the photo content 
	dataFile.write(data.text)
	dataFile.close()
      # get the last page of photos for the selected query
	dataJSONified = json.loads(data.text.lstrip("jsonFlickrApi(").rstrip(')'))
	pages = dataJSONified["photos"]["pages"]
      # do the same for all the results of the query
	for page in range(2,pages+1,1):
		params = {'method': 'flickr.photos.search', 'format' : 'json', 'woe_id' : 2459115, 'api_key', 'min_taken_date':str(d1), 'max_taken_date':str(d2), 'has_geo':1, 'tags':'stress', 'extras':'geo', 'page':page}
		data = requests.get('https://api.flickr.com/services/rest/', params=params)

		dataFile = open(path + str(d1) + "-" + str(page) + "-photos.json","w+")
		dataFile.write(data)
		dataFile.close()

      # indicate the data is uploaded for the previous photo
	print "\t" + str(d1) + " done"

	d1 = d1 + oneDay
	t.sleep(1)
