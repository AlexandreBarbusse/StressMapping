# -*- coding: utf-8 -*-
"""
Created in Aug 2016

@author: Alexandre Barbusse (ComplexCity, EIVP, KTH)
"""

#
# This script investigates the surrounding built environment of flickr photo locations thanks to 13 precise queries.
# It was implemented in order to build a statistic model to describe stress feeling and link it with the built environment.
# Thus, it provides an export solution with a JSON file output.
#




import json
import ijson
import shapely
from shapely.geometry import Point, LineString, Polygon, MultiLineString, MultiPolygon
from shapely.wkt import dumps, loads
from osgeo import ogr, osr
import time
import decimal

start_time = decimal.Decimal(time.time()) 





# Prepare your photos for the queries of the environment surrounding them
#
# 
 
from  more_itertools import unique_everseen

# load the flickr data to store the locations of the photos

list_point_coordinates1  = []
with open('not_stress_photos3_stress.json', 'r') as fp:
    data = json.load(fp) 
    for feature in data:
        list_point_coordinates1.append((float(feature['longitude']),float(feature['latitude'])))

# remove the duplicates

list_point_coordinates2 = list(unique_everseen(list_point_coordinates1)) 
       
# store the photo location as a georeferenced point
       
list_point = []
for coordinates in list_point_coordinates2:
    list_point.append(shapely.geometry.Point(coordinates))
    
# transformation of a point to fit the selected projection system and give coordinates as an output
    
def coordinates(point):
    Point = ogr.CreateGeometryFromWkt(dumps(point))
   # transform both geometries to the fittest projection
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    target = osr.SpatialReference()
    target.ImportFromEPSG(26918)
                
    transform = osr.CoordinateTransformation(source, target)
    Point.Transform(transform)
    x0 = Point.GetX()
    y0 = Point.GetY()
    return x0, y0
    



# Create the queries    
    
# Query 1 : count the sidewalkcafes within 25 meters of the photo location
    
lines = []
with open('sidewalkcafe_26918.json') as fp:
    data = json.load(fp)   
    for item in data['features']:
        if item['properties']['CafeType'] is not None:
            if item['geometry']['type'] == 'LineString':
                if item['properties']['CafeType'] != 'Not Permitted':
                    lines.append(LineString(item['geometry']['coordinates']))
                    
from rtree import index
idx1 = index.Index()
for pos, line in enumerate(lines):
    idx1.insert(pos, line.bounds)

def count_cafes(point):
    count = 0
    for j in idx1.intersection(Point(coordinates(point)).buffer(25).bounds):
        if lines[j].intersects(Point(coordinates(point)).buffer(25)):
            count += 1
    return count
   
   
   
   
# Query 2 : count the benches within 20 meters of the photo location
   
benches = []
with open('bench_26918.json') as fp:
    data = json.load(fp)   
    for item in data['features']:
        benches.append(Point(item['geometry']['coordinates']))
        
from rtree import index
idx2 = index.Index()
for pos, bench in enumerate(benches):
    idx2.insert(pos, bench.bounds)

def count_benches(point):
    count = 0
    for j in idx2.intersection(Point(coordinates(point)).buffer(20).bounds):
        if benches[j].intersects(Point(coordinates(point)).buffer(20)):
            count += 1
    return count



# Query 3 : inquire wether the photo location is situated within 50 meters of a waterfront

hydro_polygons = []
with open('hydrography_26918.geojson') as fp:
    data = json.load(fp)
    for feature in data['features']:
        for polygon in feature['geometry']['coordinates']:
            poly = []            
            for coordinates1 in polygon:
                for coordinate in coordinates1:
                    poly.append((coordinate[0],coordinate[1]))
            hydro_polygons.append(Polygon(poly))

from rtree import index
idx3 = index.Index()
for pos, poly in enumerate(hydro_polygons):
    idx3.insert(pos, poly.bounds)


def hydro_criteria(photo):
    for j in idx3.intersection(Point(coordinates(photo)).buffer(50).bounds):
        if Point(coordinates(photo)).buffer(50).intersects(hydro_polygons[j]):
            return 1
        else:
            return 0
    return 0



# Query 4 : inquire wether the photo location is situated in a green space

green_polygons = []
with open('green_spaces_fabien.geojson') as fp:
    data = json.load(fp)
    for feature in data['features']:
        for polygon in feature['geometry']['coordinates']:
            poly = []            
            for coordinate in polygon:
                poly.append((coordinate[0],coordinate[1]))
            green_polygons.append(Polygon(poly))

from rtree import index
idx4 = index.Index()
for pos, poly in enumerate(green_polygons):
    idx4.insert(pos, poly.bounds)

def green_criteria(point):
    for j in idx4.intersection((point.coords[0])):
        if point.intersects(green_polygons[j]):
            return 1
        else:
            return 0
    return 0



# Query 5 : count the number of trees within 20 meters of the photo location 

trees = []
f = open('trees.json')
objects = ijson.items(f, 'features.item')
for obj in objects:
    Point2 = ogr.CreateGeometryFromWkt(dumps(shapely.geometry.Point(float(obj['properties']['longitude']),float(obj['properties']['latitude']))))
    source = osr.SpatialReference()
    source.ImportFromEPSG(4326)
    target = osr.SpatialReference()
    target.ImportFromEPSG(26918)                        
    transform = osr.CoordinateTransformation(source, target)
    Point2.Transform(transform)
    x2 = Point2.GetX()
    y2 = Point2.GetY()
    trees.append(shapely.geometry.Point(x2,y2))


from rtree import index
idx5 = index.Index()
for pos, tree in enumerate(trees):
    idx5.insert(pos, tree.bounds)

def count_trees(point):
    count = 0
    for j in idx5.intersection(Point(coordinates(point)).buffer(20).bounds):
        if trees[j].intersects(Point(coordinates(point)).buffer(20)):
            count += 1
    return count




# Query 6 : get the total built, floor area within 100 meters of the flickr photo location
# Query 7 : get the average age of the buildings located within 100 meters of the flickr photo location
# Query 8 : get the average roofheights of the buildings located within 100 meters of the flickr photo location

batiments = []
heightroof = []
year = []
build_area = []
f = open('building_footprints.geojson')
objects = ijson.items(f, 'features.item')
for obj in objects:
    for polygon in obj['geometry']['coordinates']:
        poly = []            
        for coordinates1 in polygon:
            for coordinate in coordinates1:
                poly.append((coordinate[0],coordinate[1]))
        wktPolygon = dumps(Polygon(poly))
        polygon1 = ogr.CreateGeometryFromWkt(wktPolygon)
        source = osr.SpatialReference()
        source.ImportFromEPSG(4326)
        target = osr.SpatialReference()
        target.ImportFromEPSG(26918)
        transform = osr.CoordinateTransformation(source, target)
        polygon1.Transform(transform)
        wktPolygon1 = polygon1.ExportToWkt()
        batiments.append(loads(wktPolygon1))
        heightroof.append(float(obj['properties']['heightroof']))
        year.append(float(obj['properties']['cnstrct_yr']))
        build_area.append(float(obj['properties']['shape_area']))
        
from rtree import index
idx6 = index.Index()
for pos, batiment in enumerate(batiments):
    idx6.insert(pos, batiment.bounds)

def area_criteria(point):
    total_area = 0
    build_area1 = []
    for j in idx6.intersection(Point(coordinates(point)).buffer(100).bounds):
        if batiments[j].intersects(Point(coordinates(point)).buffer(100)):
            build_area1.append(build_area[j])
    if len(build_area1)>0:
        total_area = (float(sum(build_area1)))
    else:
        total_area = 0
    return total_area

def age_criteria(point):
    average_age = 0
    year1 = []
    for j in idx6.intersection(Point(coordinates(point)).buffer(100).bounds):
        if batiments[j].intersects(Point(coordinates(point)).buffer(100)):
            year1.append(year[j])
    if len(year1)>0:
        average_age = 2016-(float(sum(year1))/float(len(year1)))
    else:
        average_age = 63
    return average_age
    
def height_criteria(point):
    average_height = 0
    heightroof1 = []
    for j in idx6.intersection(Point(coordinates(point)).buffer(100).bounds):
        if batiments[j].intersects(Point(coordinates(point)).buffer(100)):
            heightroof1.append(heightroof[j])
    if len(heightroof1)>0:
        average_height = (float(sum(heightroof1))/float(len(heightroof1)))
    else:
        average_height = 50
    return average_height   
    
routes = []
with open('aadt_26918.json') as fp:
    data = json.load(fp)
    for feature in data['features']:
        if feature is not None:
            if feature['geometry'] is not None:
                if feature['properties']['MUNI'] in ['Manhattan', 'Bronx', 'Brooklyn', 'Queens', 'Staten Island', 'New York', 'CITY OF NEW YORK']:
                    if feature['geometry']['type'] is not None:
                        if feature['geometry']['type'] == 'LineString':
                            if feature['geometry']['coordinates'] is not None:
                                routes.append(feature)
                        else:
                            if feature['properties']['MUNI'] == 'MultiLineString':
                                if feature['geometry']['coordinates'] is not None:
                                #if Point(coordinates(point)).buffer(100).intersects(MultiLineString(feature['geometry']['coordinates'])):                  
                                    routes.append(feature)
                          
from rtree import index
idx = index.Index()
for pos, route in enumerate(routes):
    if route['geometry'] is not None:
        if route['geometry']['type'] == 'LineString':
            idx.insert(pos, LineString(route['geometry']['coordinates']).bounds)
        else:
            idx.insert(pos, MultiLineString(route['geometry']['coordinates']).bounds)

def dist(x1,y1, x2,y2, x3,y3): # x3,y3 is the point
    px = x2-x1
    py = y2-y1

    something = px*px + py*py

    u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)

    if u > 1:
        u = 1
    elif u < 0:
        u = 0

    x = x1 + u * px
    y = y1 + u * py

    dx = x - x3
    dy = y - y3

    dist = math.sqrt(dx*dx + dy*dy)

    return dist

def dist_point_line(point,line):
    if line is not None:
        wktLine = dumps(line)
        # create geometries from wkt
        Line = ogr.CreateGeometryFromWkt(wktLine)
        if Line is not None:
            # transform both geometries to the fittest projection
            Point = ogr.CreateGeometryFromWkt(dumps(point))
            # transform both geometries to the fittest projection
            source = osr.SpatialReference()
            source.ImportFromEPSG(4326)
            target = osr.SpatialReference()
            target.ImportFromEPSG(26918)
            
            transform = osr.CoordinateTransformation(source, target)
            Point.Transform(transform)
            # create a line for each point in the first geometry of the polygon
                # initialize
            x0 = Point.GetX()
            y0 = Point.GetY()
            
            distance1 = []
            for i in range(0, Line.GetPointCount()-1):
                xi, yi, zi = Line.GetPoint(i)
                ai, bi, ci = Line.GetPoint(i+1)
                    # create line and check length
                distance1.append(dist(xi,yi,ai,bi,x0,y0))
            return min(distance1)

def dist_point_multi(point,multi):
    if multi is not None:
        wktMulti = dumps(multi)
        # create geometries from wkt
        Multi = ogr.CreateGeometryFromWkt(wktMulti)
        # transform both geometries to the fittest projection
        if Multi is not None:
            Point = ogr.CreateGeometryFromWkt(dumps(point))
            # transform both geometries to the fittest projection
            source = osr.SpatialReference()
            source.ImportFromEPSG(4326)
            target = osr.SpatialReference()
            target.ImportFromEPSG(26918)
            
            transform = osr.CoordinateTransformation(source, target)
            Point.Transform(transform)
            # create a line for each point in the first geometry of the polygon
                # initialize
            x0 = Point.GetX()
            y0 = Point.GetY()
            
            distance1 = []
            for line in Multi:
                for i in range(0, line.GetPointCount()-1):
                    xi, yi, zi = line.GetPoint(i)
                    ai, bi, ci = line.GetPoint(i+1)
                    # create line and check length
                    distance1.append(dist(xi,yi,ai,bi,x0,y0))
            return min(distance1)
    
def intersecting_nearest_route(point):
    routes_list = []
    distances = []
    intersecting_routes = []
    a0 = 110
    a1 = 150
    for j in idx.intersection(Point(coordinates(point)).buffer(100).bounds):
        if routes[j]['geometry']['type'] == 'LineString':
            if LineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(100)):
                routes_list.append(routes[j])
        else:
            if MultiLineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(100)):
                routes_list.append(routes[j])
    if len(routes_list) != 0:
        for route in routes_list:
            if route['properties']['MUNI'] == 'MultiLineString':
                distances.append(dist_point_multi(point,MultiLineString(route['geometry']['coordinates'])))
            else:
                distances.append(dist_point_line(point,LineString(route['geometry']['coordinates'])))
        a0 = min(distances)
        if len(distances)>1: 
            new_routes = routes_list
            distances2 = []
            for route in new_routes:
                if route['properties']['MUNI'] == 'MultiLineString':
                    if dist_point_multi(point,MultiLineString(route['geometry']['coordinates'])) == a0 :
                        new_routes.remove(route)
                        intersecting_routes.append(route)
                else:
                    if dist_point_line(point,LineString(route['geometry']['coordinates'])) == a0:
                        new_routes.remove(route)
                        intersecting_routes.append(route)
            for route in new_routes:
                if route['geometry']['type'] == 'MultiLineString':
                    if routes[0]['geometry']['type'] == 'MultiLineString':
                        if MultiLineString(route['geometry']['coordinates']).intersects(MultiLineString(routes[0]['geometry']['coordinates'])) == False:
                            new_routes.remove(route)
                    else:
                         if MultiLineString(route['geometry']['coordinates']).intersects(LineString(routes[0]['geometry']['coordinates'])) == False:
                            new_routes.remove(route)
                else:
                    if routes[0]['geometry']['type'] == 'MultiLineString':
                        if LineString(route['geometry']['coordinates']).intersects(MultiLineString(routes[0]['geometry']['coordinates'])) == False:
                            new_routes.remove(route)
                    else:
                         if LineString(route['geometry']['coordinates']).intersects(LineString(routes[0]['geometry']['coordinates'])) == False:
                            new_routes.remove(route)
            for route in new_routes:
                if route['properties']['MUNI'] == 'MultiLineString':
                    distances2.append(dist_point_multi(point,MultiLineString(route['geometry']['coordinates'])))
                else:
                    distances2.append(dist_point_line(point,LineString(route['geometry']['coordinates'])))
            if len(distances2)>0:
                a1 = min(distances2)
            else:
                a1 = 150
    if a1 == a0:
        a1 = 0              
    return a1

def nearest_route(point):
    routes_list = []
    distances = []
    a0 = 110
    for j in idx.intersection(Point(coordinates(point)).buffer(100).bounds):
        if routes[j]['geometry']['type'] == 'LineString':
            if LineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(100)):
                routes_list.append(routes[j])
        else:
            if MultiLineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(100)):
                routes_list.append(routes[j])
    if len(routes_list) != 0:
        for route in routes_list:
            if route['properties']['MUNI'] == 'MultiLineString':
                distances.append(dist_point_multi(point,MultiLineString(route['geometry']['coordinates'])))
            else:
                distances.append(dist_point_line(point,LineString(route['geometry']['coordinates'])))
        a0 = min(distances)
    return a0



# Query 9 : get the inverse square distance between the photo location and the nearest route

def inverse_square_nearest_route(point):
    return 1/(nearest_route(point)**2)
    


# Query 10 : get the inverse square distance between the photo location and the nearest route among the routes which intersect with the nearest route

def inverse_square_intersecting_nearest_route(point):
    return 1/(intersecting_nearest_route(point)**2)



# Query 11 : count the number of different routes within 20 meters of the photo location 

def count_route_under_20(point):
    count = 0
    for j in idx.intersection(shapely.geometry.Point(coordinates(point)).buffer(20).bounds):
        if routes[j]['geometry']['type'] == 'LineString':
            if LineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(20)):
                count += 1
        else:
            if MultiLineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(20)):
                count += 1
    return count



# Query 12 : count the number of different routes within 50 meters of the photo location 

def count_route_under_50(point):
    count = 0
    for j in idx.intersection(shapely.geometry.Point(coordinates(point)).buffer(50).bounds):
        if routes[j]['geometry']['type'] == 'LineString':
            if LineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(50)):
                count += 1
        else:
            if MultiLineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(50)):
                count += 1
    return count



# Query 13 : get the annual average daily trafic of the nearest route to the photo location and normalize it by the length of this route

def aadt13_nearest_route(point):
    routes_list = []
    distances = []
    a0 = 110
    for j in idx.intersection(Point(coordinates(point)).buffer(100).bounds):
        if routes[j]['geometry']['type'] == 'LineString':
            if LineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(100)):
                routes_list.append(routes[j])
        else:
            if MultiLineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(100)):
                routes_list.append(routes[j])
    if len(routes_list) != 0:
        for route in routes_list:
            if route['properties']['MUNI'] == 'MultiLineString':
                distances.append(dist_point_multi(point,MultiLineString(route['geometry']['coordinates'])))
            else:
                distances.append(dist_point_line(point,LineString(route['geometry']['coordinates'])))
        a0 = min(distances)
    new_routes = routes_list
    for route in new_routes:
        if route['properties']['MUNI'] == 'MultiLineString':
            if dist_point_multi(point,MultiLineString(route['geometry']['coordinates'])) == a0 :
                return route['properties']['AADT13']
        else:
            if dist_point_line(point,LineString(route['geometry']['coordinates'])) == a0:
                return route['properties']['AADT13']
            
                
def lenght_nearest_route(point):
    routes_list = []
    distances = []
    a0 = 110
    for j in idx.intersection(Point(coordinates(point)).buffer(100).bounds):
        if routes[j]['geometry']['type'] == 'LineString':
            if LineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(100)):
                routes_list.append(routes[j])
        else:
            if MultiLineString(routes[j]['geometry']['coordinates']).intersects(Point(coordinates(point)).buffer(100)):
                routes_list.append(routes[j])
    if len(routes_list) != 0:
        for route in routes_list:
            if route['properties']['MUNI'] == 'MultiLineString':
                distances.append(dist_point_multi(point,MultiLineString(route['geometry']['coordinates'])))
            else:
                distances.append(dist_point_line(point,LineString(route['geometry']['coordinates'])))
        a0 = min(distances)
    new_routes = routes_list
    for route in new_routes:
        if route['properties']['MUNI'] == 'MultiLineString':
            if dist_point_multi(point,MultiLineString(route['geometry']['coordinates'])) == a0 :
                return route['properties']['SHAPE_Leng']
        else:
            if dist_point_line(point,LineString(route['geometry']['coordinates'])) == a0:
                return route['properties']['SHAPE_Leng']
    
def normalized_aadt(point):
    if aadt13_nearest_route(point) is not None:
        if aadt13_nearest_route(point) != 'null':
            return float(aadt13_nearest_route(point))/float(lenght_nearest_route(point))
        else:
            return aadt13_nearest_route(point)
    else:
        return None
    
    
    
# Finalize by exporting all the results of the 13 queries in a JSON file    

import collections

objects_list = []
for point in list_point:
    d = collections.OrderedDict()
    d['count_cafes'] = count_cafes(point)
    d['count_benches'] = count_benches(point)
    d['count_trees'] = count_trees(point)
    d['green_criteria'] = green_criteria(point)
    d['hydro_criteria'] = hydro_criteria(point)
    d['area_criteria'] = area_criteria(point)
    d['age_criteria'] = age_criteria(point)
    d['height_criteria'] = height_criteria(point)
    d['inverse_square_nearest_route'] = inverse_square_nearest_route(point)
    d['inverse_square_intersecting_nearest_route'] = inverse_square_intersecting_nearest_route(point)
    d['count_route_under_20'] = count_route_under_20(point)
    d['count_route_under_50'] = count_route_under_50(point)
    d['normalized_aadt'] = normalized_aadt(point)
    d['variable_y'] = 0
    objects_list.append(d)

o1 = open('final_results.json', 'w')
o1.write(json.dumps(objects_list))
o1.close()


o2 = open('final_results.json', 'w')
json.dump(json.dumps(objects_list), o2)
o2.close()

o3 = open('final_results.json', 'w')
json.dump(objects_list, o3)
o3.close()

          
end_time = decimal.Decimal(time.time())
timelapse = end_time - start_time
print "temps de calcul : %f" % timelapse 