# @author: justinnk
# Parameterises the model `model.carma` with the parameters 
# generated from the (cleaned) historic data by injecting
# the code into the CARMA model.
# Generates an experiment file for the simulation.


import json
import pprint
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# load settings from file
settings = {}
with open('settings.json', 'r') as file:
    settings = json.loads(file.read())

# output directory
output_dir = settings['output_dir']

# print additional information?
verbose = settings['verbose']

#############################################################################################
####[ stations ]#############################################################################
#############################################################################################

# list of all stations in the scheme
stations = pd.DataFrame()

# load stations list from csv file
stations = pd.read_csv('stations.csv')

if verbose:
    print('--- stations ---')
    print(stations.head())
    print('--- ---')

#############################################################################################
####[ tracks ]###############################################################################
#############################################################################################

# list of tracks recorded during a month (excluding those used for validation)
dataset = pd.DataFrame()

# load records from csv file
dataset = pd.read_csv('records.csv', parse_dates=['started_at', 'ended_at'], index_col=0)

if verbose:
    print('--- records ---')
    print(dataset.head())
    print('--- ---')

#############################################################################################
####[ adjacency for graph ]##################################################################
#############################################################################################

# returns distance between points in lat/lon in meter using the haversine formula
# see: https://www.movable-type.co.uk/scripts/latlong.html
def distance(lon1, lon2, lat1, lat2):
    R = 6371000; # meters
    phi1 = np.radians(lat1)
    phi2 = np.radians(lat2)
    dphi = np.radians(lat2-lat1)
    dlamb = np.radians(lon2-lon1)
    a = np.sin(dphi / 2) * np.sin(dphi / 2) + np.cos(phi1) * np.cos(phi2) * np.sin(dlamb / 2) * np.sin(dlamb / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

edges = stations.copy().reset_index()
edges['key'] = 0
edges = edges.merge(edges, on='key')
edges = edges.drop(columns=['key'])
edges['distance'] = distance(edges.station_longitude_x, edges.station_longitude_y, edges.station_latitude_x, edges.station_latitude_y)
edges = edges[edges.distance > 0]
if verbose:
    distances = np.arange(0, len(stations))
    for i, s in stations.iterrows():
        distances[i] = edges[edges.index_x == i].distance.min()
    print('mean station distance:')
    print(np.mean(distances))
    print('median station distance:')
    print(np.median(distances))
edges2 = edges[edges.distance < settings['user_satisfaction_max_distance']].reset_index()
edges = edges[edges.distance < settings['incentives_max_distance']].reset_index()

fig, ax = plt.subplots(figsize=(20, 10))
ax.scatter(stations.station_longitude, stations.station_latitude)
for i, v in edges.iterrows():
        if v.index_y > v.index_x:
            if not (v.index_x == v.index_y):
                ax.plot([v.station_longitude_x, v.station_longitude_y], [v.station_latitude_x, v.station_latitude_y],
                color='black', alpha=0.1) 
ax.set_aspect('equal')
fig.savefig(output_dir + '/stations_graph_parametrization.png')

fig, ax = plt.subplots(figsize=(20, 10))
ax.scatter(stations.station_longitude, stations.station_latitude)
for i, v in edges2.iterrows():
        if v.index_y > v.index_x:
            if not (v.index_x == v.index_y):
                ax.plot([v.station_longitude_x, v.station_longitude_y], [v.station_latitude_x, v.station_latitude_y],
                color='black', alpha=0.1) 
ax.set_aspect('equal')
fig.savefig(output_dir + '/users_graph_parametrization.png')

#############################################################################################
####[ spawnrates per station ]###############################################################
#############################################################################################

# list of spawnrate per station per time segment
spawnrates = dict((s, []) for s in stations.station_name)

by_stations = dataset.groupby('start_station_name')
filler = pd.DataFrame(index=pd.date_range(dataset.index.min().floor('H'), dataset.index.max().floor('H'), freq="60min"))
for g in by_stations.groups:
    f = by_stations.groups[g].to_frame()
    f = f.resample('60Min').count()
    f = f.join(filler, how='outer').fillna(0.0)
    f = f[np.isin(f.index.date, dataset.index.date)]
    f = f.groupby(f.index.hour).mean()
    spawnrates[g] = f.started_at / 60.0

def get_s_at_hour(hour):
    h = 0
    for s in spawnrates:
        h += spawnrates[s][spawnrates[s].index == hour]
    return h

if verbose:
    print('--- spawnrates ---')
    users = []
    for i in range(0, 24):
        rate = float(get_s_at_hour(i))
        users.append(rate * 60.0)
    dep_dayly = dataset.resample('60Min').start_station_name.count()
    dep_dayly = dep_dayly[np.isin(dep_dayly.index.date, dataset.index.date)]
    dep_dayly = dep_dayly.groupby(dep_dayly.index.hour).mean()
    fig, ax = plt.subplots()
    ax.plot(dep_dayly, label='data', color='orange')
    ax.plot(list(range(0, 24)), users, label='param', color='blue')
    ax.legend()
    fig.savefig(output_dir + '/spawnrates_comparison.png')
    print('done.')
    print('--- ---')

#############################################################################################
####[ destination function ]#################################################################
#############################################################################################

# function to get the destination probabilities for the given dataset
def get_transitions(ds):
    destinations = ds.groupby(['start_station_name', 'end_station_name'])['end_station_name'].count().to_frame()
    destinations = destinations.rename(columns={'end_station_name': 'count'})
    destinations = destinations.reset_index()
    destinations = destinations.set_index('start_station_name')
    destinations['sum'] = destinations.groupby('start_station_name')['count'].sum()
    destinations['prob'] = destinations['count'] / destinations['sum']
    return destinations

destinations = []
for i in range(0, 24):
    destinations.append(get_transitions(dataset[dataset.index.hour == i]))

if verbose:
    print('--- destinations ---')
    print(destinations[0].head())
    print('--- ---')

#############################################################################################
####[ trip durations ]#######################################################################
#############################################################################################

durations = dataset.groupby(['start_station_name', 'end_station_name'])['duration'].mean().to_frame()
durations['duration'] /= 60.0

average_duration = dataset['duration'].mean() / 60.0

if verbose:
    print('--- durations ---')
    print(durations.head(25))
    print('--- ---')

#############################################################################################
####[ embed parameters into model ]##########################################################
#############################################################################################

if verbose:
    print('--- injecting parameters ---')

# returns sid for a given station name
def indexOf(station_name):
    for i, s in enumerate(stations['station_name']):
        if s == station_name:
            return i
    return -1

# replaces the part of text between index start and end with substitution
def replace(start, end, text, substitution):
    return text[:start] + substitution + text[end:]

# the text contents of the model file
modelfile = ''

# load model file
with open('model.carma', 'r') as model:
    modelfile = model.read()

avail_field = 'station_optimal' if settings['use_optimals'] else 'station_available'

# average walking time
walking_start = modelfile.find('// WALKTIME START')
walking_end = modelfile.find('// WALKTIME END')
walkingstr = '// WALKTIME START\nconst walk_time = {0};\n'.format(1.0 / float(settings['average_walk_time']))
modelfile = replace(walking_start, walking_end, modelfile, walkingstr)

# user cooperation factor
coop_start = modelfile.find('// COOP START')
coop_end = modelfile.find('// COOP END')
c_factor = float(settings['cooperation'])
coopstr = '// COOP START\n'
if c_factor == 0.0:
    coopstr += 'return false;'
elif c_factor == 1.0:
    coopstr += 'return true;'
else:
    coopstr += 'return (selectFrom(0:{0}, 1:{1}) == 0);'.format(c_factor, 1.0 - c_factor)
coopstr += '\n'
modelfile = replace(coop_start, coop_end, modelfile, coopstr)

# redistribution truck
truck_start = modelfile.find('// TRUCK START')
truck_end = modelfile.find('// TRUCK END')
truckstr = '// TRUCK START\n'
if settings["use_truck"]:
    truckstr += '''
                int time = int(floor(now));
                real difference =  (abs(available_goal[sender.sid] - global.is_avail[sender.sid]) > 0 ? 1.0 : 0.0);
                if ((time >= 1380 && time <= 1439) || (time >= 2810 && time <= 2879) || (time >= 4240 && time <= 4319)){
                	return 500.0 * difference;
                } else {
                	return 0.0;
                }
'''
else:
    truckstr += 'return 0.0;'
truckstr += '\n'
modelfile = replace(truck_start, truck_end, modelfile, truckstr)

# user cooperation factor
inc_start = modelfile.find('// INC START')
inc_end = modelfile.find('// INC END')
strategy = settings['incentives']
incstr = '// INC START\n'
if strategy == 'both':
    incstr += 'new User(orig_incentivized(sender.sid, now, global.is_avail, global.will_return, global.inc_retrievals), dest_incentivized(sender.sid, now, global.is_avail, global.will_return, global.inc_returns));'
elif strategy == 'get':
    incstr += 'new User(orig_incentivized(sender.sid, now, global.is_avail, global.will_return, global.inc_retrievals), dest(sender.sid, int(floor(now / 60.0)) % 24));'
elif strategy == 'ret':
    incstr += 'new User(sender.sid, dest_incentivized(sender.sid, now, global.is_avail, global.will_return, global.inc_returns));'
else:
    incstr += 'new User(sender.sid, dest(sender.sid, int(floor(now / 60.0)) % 24));'
incstr += '\n'
modelfile = replace(inc_start, inc_end, modelfile, incstr)

# adjacency for each station
adj_start = modelfile.find('// ADJACENCY START')
adj_end = modelfile.find('// ADJACENCY END')
adjstr = '// ADJACENCY START\nconst zone_adjacency = [:'
for i, s in stations.iterrows():
    adjacent = edges[edges.station_name_x == s.station_name].index_y.to_numpy()
    if len(adjacent) > 0:
        adjstr += '[:'
        for a in adjacent:
            adjstr += '{0}, '.format(a)
        adjstr = adjstr[:-2]
        adjstr += ':], '
    else:
        adjstr += 'newList(int), '
adjstr = adjstr[:-2]
adjstr += ':];\n'
modelfile = replace(adj_start, adj_end, modelfile, adjstr)

# adjacency for each station 2
adj_start = modelfile.find('// ADJACENCY2 START')
adj_end = modelfile.find('// ADJACENCY2 END')
adjstr = '// ADJACENCY2 START\nconst zone_adjacency_2 = [:'
for i, s in stations.iterrows():
    adjacent = edges2[edges2.station_name_x == s.station_name].index_y.to_numpy()
    if len(adjacent) > 0:
        adjstr += '[:'
        for a in adjacent:
            adjstr += '{0}, '.format(a)
        adjstr = adjstr[:-2]
        adjstr += ':], '
    else:
        adjstr += 'newList(int), '
adjstr = adjstr[:-2]
adjstr += ':];\n'
modelfile = replace(adj_start, adj_end, modelfile, adjstr)

# capacity for each station
cap_start = modelfile.find('// CAPACITIES START')
cap_end = modelfile.find('// CAPACITIES END')
capstr = '// CAPACITIES START\nconst capacity = [:'
for i, s in stations.iterrows():
    capstr += '{0}, '.format(int(s.station_capacity))
capstr = capstr[:-2]
capstr += ':];\n'
modelfile = replace(cap_start, cap_end, modelfile, capstr)

# available bikes for each station
avail_start = modelfile.find('// AVAIL START')
avail_end = modelfile.find('// AVAIL END')
availstr = '// AVAIL START\nattrib is_avail := [:'
for i, s in stations.iterrows():
    availstr += '{0}, '.format(int(s[avail_field]))
availstr = availstr[:-2]
availstr += ':];\n'
modelfile = replace(avail_start, avail_end, modelfile, availstr)

# goal of available bikes for each station

avail_start = modelfile.find('// GOAL START')
avail_end = modelfile.find('// GOAL END')
availstr = '// GOAL START\nconst available_goal = [:'
if 'station_optimal' in stations.columns:
    for i, s in stations.iterrows():
        availstr += '{0}, '.format(int(s.station_optimal))
    availstr = availstr[:-2]
availstr += ':];\n'
modelfile = replace(avail_start, avail_end, modelfile, availstr)

# returns matrix
return_start = modelfile.find('// RETURN START')
return_end = modelfile.find('// RETURN END')
returnstr = '// RETURN START\nattrib will_return := [:'
for i in range(0, 74):
    returnstr += '[: {0} :], '.format(('0,' * len(stations))[:-1])
returnstr = returnstr[:-2]
returnstr += ':];\n'
modelfile = replace(return_start, return_end, modelfile, returnstr)

# durations
duration_start = modelfile.find('// DUR START')
duration_end = modelfile.find('// DUR END')
durationstr = '// DUR START\nconst dur = [:\n'
for i, s in stations.iterrows():
    durationstr += '// {0}\n'.format(s['station_name'])
    durationstr += '[: '
    for i2, s2 in stations.iterrows():
        dur = durations[(durations.index.get_level_values(0) == s['station_name']) & (durations.index.get_level_values(1) == s2['station_name'])]
        if len(dur) > 0:
            dur = round(float(dur['duration']), 2)
        else:
            dur = average_duration#0.0
        durationstr += '{0}, '.format(dur)
    durationstr = durationstr[:-2]
    durationstr += ':],\n'
durationstr = durationstr[:-2]
durationstr += ':];\n'
modelfile = replace(duration_start, duration_end, modelfile, durationstr)

# stations
stations_start = modelfile.find('// STATIONS START')
stations_end = modelfile.find('// STATIONS END')
stationstr = ''
counter = 0
for i, s in stations.iterrows():
    stationstr += 'new Station({0}, {1}, {2}); //{3}\n'.format(counter, int(s['station_capacity']), int(s[avail_field]), s['station_name'])
    stationstr += 'new Spawner({0});\n'.format(counter)
    counter += 1
modelfile = replace(stations_start, stations_end, modelfile, '// STATIONS START\n' + stationstr)

if settings['refresh_destinations']:
    # destination function
    destinations_start = modelfile.find('// DEST START')
    destinations_end = modelfile.find('// DEST END')
    destinationsstr = '// DEST START\n'
    count = 0
    for period in range(0, 24):
        destinationsstr += '\nfun int dest_{0}(int sid){{'.format(period)
        destination = destinations[period]
        for i, s in stations.iterrows():
            dest = destination[(destination.index == s['station_name'])]
            if len(dest) > 0:
                destinationsstr += 'if (sid == {0}) // {1}\n    return selectFrom('.format(count, s['station_name'])
                for i2, s2 in stations.iterrows():
                    dest = destination[(destination.index == s['station_name']) & (destination['end_station_name'] == s2['station_name'])]
                    if len(dest) > 0:
                        destinationsstr += '{0}:{1:.2}, '.format(i2, float(dest['prob']))
                destinationsstr = destinationsstr[:-2]
                destinationsstr += ');\nelse '
            count += 1
        destinationsstr += '\n    return -1;}\n'
        count = 0
    modelfile = replace(destinations_start, destinations_end, modelfile, destinationsstr)

# spawnrates
spawnrates_start = modelfile.find('// SPAWNRATE START')
spawnrates_end = modelfile.find('// SPAWNRATE END')
spawnratestr1 = '// SPAWNRATE START\nconst demand = [:\n'
for i, s in stations.iterrows():
    spawnratestr1 += '// {0}\n'.format(s['station_name'])
    spawnratestr1 += '[:'
    for j in range(0, 24):
        rate = round(spawnrates[s['station_name']][j], 4)
        spawnratestr1 += '{0}, '.format(rate)
    spawnratestr1 = spawnratestr1[:-2]
    spawnratestr1 += ':],\n'
spawnratestr1 = spawnratestr1[:-2]
spawnratestr1 += ':];\n'
modelfile = replace(spawnrates_start, spawnrates_end, modelfile, spawnratestr1)

# save parametrized model file
with open('model.carma', 'w') as model:
    model.write(modelfile)

if verbose:     
    print('done.')
    print('--- ---')

#############################################################################################
####[ Generate Experiment File ]#############################################################
#############################################################################################

if verbose:
    print('--- generating experiment ---')

experimentstr = '''
test_exp
model.carma
TestScenario
{0}
{1}
{2}
Retrievals
IncRetrievals
Returns
IncReturns
GlobalUsers
Biking
Waiting
Returning
AvgAvailable
MinAvailable
MaxAvailable
StarvedStations
FullStations
DissatisfiedRet: level=0
DissatisfiedRet: level=1
DissatisfiedRet: level=2
DissatisfiedRet: level=3
DissatisfiedGet: level=0
DissatisfiedGet: level=1
DissatisfiedGet: level=2
DissatisfiedGet: level=3
'''.format(settings['replications'], settings['simulation_end_time'], settings['samples'])

# add bike availability for each station to the recorded measures
for i in range(len(stations)):
    experimentstr += 'Available: sid={0}\n'.format(i)

with open('experiment.exp', 'w+') as file:
    file.write(experimentstr)

if verbose:
    print('done.')
    print('--- ---')