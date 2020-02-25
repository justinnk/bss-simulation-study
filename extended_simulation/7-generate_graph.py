# # @author justinnk
# Generates the spatial graph for the evlaluation with SSTL.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

# returns distance between points in lat/lon in meter using the haversine formula
# see: https://www.movable-type.co.uk/scripts/latlong.html
def distance(lon1, lon2, lat1, lat2):
    R = 6371000; # metres
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2-lat1)
    dlamb = np.radians(lon2-lon1)
    a = np.sin(dphi / 2) * np.sin(dphi / 2) + np.cos(phi1) * np.cos(phi2) * np.sin(dlamb / 2) * np.sin(dlamb / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

stations = pd.read_csv('stations.csv', usecols=['station_latitude', 'station_longitude'])

edges = stations.copy().reset_index()
edges['key'] = 0
edges = edges.merge(edges, on='key')
edges = edges.drop(columns=['key'])
edges['distance'] = distance(edges.station_longitude_x, edges.station_longitude_y, edges.station_latitude_x, edges.station_latitude_y)
#edges['distance'] = (edges.station_longitude_y - edges.station_longitude_x) ** 2 \
#    + (edges.station_latitude_y - edges.station_latitude_x) ** 2
#edges = edges[edges.distance < 500].reset_index()
edges = edges.reset_index()

with open('model.tra', 'w+') as file:
    file.write('LOCATIONS\n')
    for i in stations.index:
        file.write('{0}\n'.format(i))
    file.write('EDGES\n')
    for i, v in edges.iterrows():
        if v.index_y > v.index_x:
            if not (v.index_x == v.index_y):
                file.write('{0} {1} {2:.2f}\n'.format(int(v.index_x), int(v.index_y), round(v.distance, 2)))

#plt.scatter(stations.station_longitude, stations.station_latitude)
#for i, v in edges.iterrows():
#        if v.index_y > v.index_x:
#            if not (v.index_x == v.index_y):
#                plt.plot([v.station_longitude_x, v.station_longitude_y], [v.station_latitude_x, v.station_latitude_y],
#                color='black', alpha=0.1) 
#plt.show()
#plt.savefig('graph_vis.png')