# -*- coding: utf-8 -*-



'''
created by Fabien and Alexandre (Complexcity lab, EIVP)
July 2016


for extension see http://geoexamples.blogspot.fr/2014/08/shortest-distance-to-geometry-in.html

'''


#
# This script provides a query to inquire whether a flickr photo location is situated in a green space.
# It present the computation of two different methods, a simple and direct one using intersections of polygons, and a 
# more complex one, using an Rtree spatial index in order to accelerate significantly the computation.
# The last lines of code allow the user to compare the durations of the 2 computations, using Rtree or not, and evaluate 
# the impact of using a Rtree index.
#

import shapely
import json 
import decimal
import time
from shapely.geometry import Polygon, Point



# get the Flickr photos locations and put them in a list of points

from  more_itertools import unique_everseen

list_point_coordinates1  = []
with open('not_stress_photos3_stress.json', 'r') as fp:
    data = json.load(fp) 
    for feature in data:
        list_point_coordinates1.append((float(feature['longitude']),float(feature['latitude'])))
    
list_point_coordinates2 = list(unique_everseen(list_point_coordinates1))        

list_point = []
for coordinates in list_point_coordinates2:
    list_point.append(shapely.geometry.Point(coordinates))
            

# get the parks from the geoJSON file and put them in a list of polygons

green_polygons = []
with open('green_spaces_fabien.geojson') as fp:
    data = json.load(fp)
    for feature in data['features']:
#        print feature['geometry']['type']
#        if feature['geometry']['type'] != 'Poygon':
#            continue
        for polygon in feature['geometry']['coordinates']:
            poly = []            
            for coordinate in polygon:
                poly.append((coordinate[0],coordinate[1]))
            green_polygons.append(Polygon(poly))


# Create a Rtree spatial index to store the bounding boxes containing all the green spaces polygons objects

from rtree import index
idx = index.Index()
for pos, poly in enumerate(green_polygons):
    idx.insert(pos, poly.bounds)
    

# define a function that gives 1 as output if the photo is located in a green spaces, and 0 otherwise
    
def green_criteria(photo):
    for poly in green_polygons:
        if photo.intersects(poly):
            return 1
    return 0



# define a function that gives the same output as green_criteria(photo) but is optimized using a Rtree spatial index

def green_criteria_rtree(point):
    for j in idx.intersection((point.bounds)):
        if point.intersects(green_polygons[j]):
            return 1
        else:
            return 0
    return 0
    
    
    

# Measure the duration of computing the query on 1705 photos (observations) WITHOUT Rtree

start_time = decimal.Decimal(time.time()) 
for point in list_point:
    print point, green_criteria(point)
    
end_time = decimal.Decimal(time.time())
timelapse = end_time - start_time

print "temps de calcul 1 : %f" % timelapse


# Measure the duration of computing the query on 1705 photos (observations) WITH Rtree

start_time2 = decimal.Decimal(time.time()) 
for point in list_point:
    print point, green_criteria_rtree(point)
    
end_time2 = decimal.Decimal(time.time())
timelapse2 = end_time2 - start_time2



# Compare the speed of both computation (with and without Rtree)

print "temps de calcul 1 : %f" % timelapse
print "temps de calcul 2 : %f" % timelapse2