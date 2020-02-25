# @author: justinnk
# Parametrizes the model `model.carma` with the parameters generated from the (cleaned) historic data

import json
import pprint
import numpy as np
import pandas as pd

# load settings from file
settings = {}
with open('settings.json', 'r') as file:
    settings = json.loads(file.read())

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
####[ spawnrates per station ]###############################################################
#############################################################################################

# list of spawnrate per station per time segment
spawnrates = dict((s, []) for s in stations.station_name)

by_stations = dataset.groupby('start_station_name')
filler = pd.DataFrame(index=pd.date_range(dataset.index.min().floor('H'), dataset.index.max().floor('H'), freq="60min"))
for g in by_stations.groups:
    f = by_stations.groups[g].to_frame()
    f = f.resample('60Min').count()
    f = f.join(filler, how='right').fillna(0.00)
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
    import matplotlib.pyplot as plt
    users = []
    for i in range(0, 24):
        rate = float(get_s_at_hour(i))
        users.append(rate * 60.0)
    dep_dayly = dataset.resample('60Min').start_station_name.count()
    dep_dayly = dep_dayly[np.isin(dep_dayly.index.date, dataset.index.date)]
    dep_dayly = dep_dayly.groupby(dep_dayly.index.hour).mean()
    plt.plot(dep_dayly, label='data', color='orange')
    plt.plot(list(range(0, 24)), users, label='param', color='blue')
    plt.legend()
    plt.savefig('results_graphs/spawnrates.png')
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
            dur = float(dur['duration'])
        else:
            dur = average_duration
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
    stationstr += 'new Station({0}, {1}, {2}); //{3}\n'.format(counter, int(s['station_capacity']), int(s['station_available']), s['station_name'])
    stationstr += 'new Spawner({0});\n'.format(counter)
    counter += 1
modelfile = replace(stations_start, stations_end, modelfile, '// STATIONS START\n' + stationstr)

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
spawnratestr = 'const demand = [:'
for i, s in stations.iterrows():
    spawnratestr += '// {0}\n'.format(s['station_name'])
    spawnratestr += '[:'
    for j in range(0, 24):
        rate = round(spawnrates[s['station_name']][j], 4)
        spawnratestr += '{0}, '.format(rate)
    spawnratestr = spawnratestr[:-2]
    spawnratestr += ':],\n'
spawnratestr = spawnratestr[:-2]
spawnratestr += ':];\n'
modelfile = replace(spawnrates_start, spawnrates_end, modelfile, '// SPAWNRATE START\n' + spawnratestr)

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
Returns
GlobalUsers
Biking
Waiting
Returning
AvgAvailable
MinAvailable
MaxAvailable
StarvedStations
FullStations
ErrorStation
ErrorDest
ErrorOrig
'''.format(settings['replications'], settings['simulation_end_time'], settings['samples'])

# add bike availability for each station to the recorded measures
for i in range(len(stations)):
    experimentstr += 'Available: sid={0}\n'.format(i)

with open('experiment.exp', 'w+') as file:
    file.write(experimentstr)

if verbose:
    print('done.')
    print('--- ---')