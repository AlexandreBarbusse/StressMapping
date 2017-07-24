# -*- coding: utf-8 -*-
"""
Created on Mon Oct 17 14:22:02 2016

@author: Alexandre Barbusse, EIVP & KTH Sudent

This script brings a simple tool to convert the data provided by the MIT Media Lab "Place Pulse" project 
as a JSON file (available here : http://pulse.media.mit.edu/static/data/consolidated_data_jsonformatted.json)
without geometry, into a GeoJSON file which could be used to visualise these data, using a GIS for instance.
In order to use this script, you should first download the data from the web page as a JSON file, which is entitled 
'place_pulse.json' in the following code.

It is really important to note that all numbers will be displayed as strings in the output GeoJSON file. If you need the
data to be stored as double, you should manage to either add commands such as float() directly from this script or 
convert the data when importing it, in a GIS for example.

For further information, please feel free to contact me at barbusse@kth.se 
                                                        or alexandre.barbusse@eivp-paris.fr
"""

import json
import time
import decimal

# start the duration calcualation
#
#
start_time = decimal.Decimal(time.time())  


# Read the imported JSON file provided by MIT Media Lab, Place Pulse project
#
#
with open('place_pulse.json', 'r') as fp:
    data1 = json.load(fp) 
    #
    # Loop within all surveyed places
    #
    for object in data1 :
        # test if the coordinates display as you wish
        print (object['Lon'],object['Lat'])
        break
    
    
    #
    # Extract the geometry information as a dictionary 
    #
    geos = []
    for object in data1 :
        point = {
            'type': 'Point',
            'coordinates': [object['Lon'],object['Lat']],
        }
        geos.append(point)
    
    #
    # Extract the place survey scores information as a dictionary
    #
    propers = []
    for object in data1 :
        properties = {
            'Upperclass': object['QS Upperclass'],
            'Safe': object['QS Safer'],
            'Unique': object['QS Unique'],
            'City': object['City'],
            'ID': object['ID'],
        }
        propers.append(properties)

#
# Merge all extracted information in a feature collection appropriate for the GeoJSON export
#
feats = []
for i in range(len(geos)) :
    feat = {
        'type': 'Feature',
        'geometry': geos[i],
        'properties': propers[i],
    }
    feats.append(feat)

#
# Format the feature collection for GeoJSON export using dictionnaries
#
features = {
        'crs': {
               'type':'name',
               'properties':{
                       'name' : 'urn:ogc:def:crs:EPSG::4326'
                       },
           },
        'type': 'FeatureCollection',
        'features': feats,
}



print len(geos)
print len(propers)


#
# Write the output GeoJSON file using json.dump
#
o1 = open('place_pulse_recoded_1.geojson', 'w')
json.dump(features, o1)
o1.close()


#
# Display the duration of the whole process
#
end_time = decimal.Decimal(time.time())
timelapse = end_time - start_time
print "temps de calcul 1 : %f" % timelapse