# author: justinnk
# Produces clean datasets as starting point for the pipeline

import csv
import json
import pprint
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

#############################################################################################
####[ Helper Functions ]#####################################################################
#############################################################################################

# return only the entries for weekdays from dataframe
def only_weekdays(dataframe):
    return dataframe[dataframe.index.dayofweek < 5]

# return only the entries for weekends from dataframe
def only_weekends(dataframe):
    return dataframe[dataframe.index.dayofweek >= 5]

# remove stations from dataset, that have a departure frequency less than threshold over 1 month
def remove_unused_stations(dataframe, threshold):
    dataframe_copy = dataframe.copy()
    stations_dep = dataframe.groupby('start_station_name')
    stations_arr = dataframe.groupby('end_station_name')
    if len(stations_arr) != len(stations_dep):
        print('WARNING: Stations with no departures/arrivals exist!')
    for s in stations_arr.groups.keys():
        num_arrivals = len(stations_arr.groups[s])
        if num_arrivals < threshold:
            if verbose: print('station {0} has only {1} arrivals in the whole month'.format(s, num_arrivals))
            dataframe_copy = dataframe_copy[dataframe_copy['start_station_name'] != s]
            dataframe_copy = dataframe_copy[dataframe_copy['end_station_name'] != s]
    for s in stations_dep.groups.keys():
        num_departures = len(stations_dep.groups[s])
        if num_departures < threshold:
            if verbose: print('station {0} has only {1} departures in the whole month'.format(s, num_departures))
            dataframe_copy = dataframe_copy[dataframe_copy['start_station_name'] != s]
            dataframe_copy = dataframe_copy[dataframe_copy['end_station_name'] != s]
    return dataframe_copy

# returns for a single stations the number of days that it does not appear in the historic data
def get_station_invisibility(dataframe, station_name):
    month_start = dataframe.index.min()
    month_end = dataframe.index.max()
    days = pd.DataFrame(index=pd.date_range(month_start.date(), month_end.date(), freq="D"))
    station_history = dataframe[dataframe.start_station_name == station_name].resample('D').count()
    station_history.index = station_history.index.map(lambda x: x.date())
    station_history = days.join(station_history, how='outer')
    nulldays = station_history.start_station_name.isnull().sum()
    return nulldays

#find stations that only appear in the data for len(month) - 2 days or less
def find_introduced_stations(dataframe):
    bad_stations = []
    for s in dataframe.start_station_name.drop_duplicates():
        if get_station_invisibility(dataframe, s) > 2:
            bad_stations.append(s)
    return bad_stations

# remove stations that oly appear in the data for len(month) - 2 days or less
def remove_introduced_stations(dataframe):
    data = dataframe.copy()
    bad_stations = find_introduced_stations(data)
    if verbose: print('removing stations {0}, because they possibly got introduced/removed during the month.'.format(bad_stations))
    return data[~data.start_station_name.isin(bad_stations)]

# remove entries with a duration lower than the low-th quantile or higher than the high-th quantile
def remove_duration(dataframe, high, low):
    high_threshold = dataframe['duration'].quantile(high)
    low_threshold = dataframe['duration'].quantile(low)
    return dataframe[(dataframe['duration'] >= low_threshold) & (dataframe['duration'] <= high_threshold)]

#############################################################################################
####[ Cleansing ]############################################################################
#############################################################################################

# load settings from file
settings = {}
with open('settings.json', 'r') as file:
    settings = json.loads(file.read())

# print additional information?
verbose = settings['verbose']

# historic data location
historic_data = settings['historic_data_location']

# live data location
live_data = settings['stations_data_location']

# minimum and maximum duration for a trip to be included in the produced dataset
duration_min = settings['duration_min_quantile']
duration_max = settings['duration_max_quantile']

# length of dataset before and after cleansing
dataset_len = 0
dataset_len_old = 0
dataset_len_validation = 0

# historic dataset
dataset = pd.read_csv(historic_data, usecols=[
        'started_at',
        'ended_at',
        'duration',
        'start_station_name',
        'end_station_name'
    ], parse_dates=['started_at', 'ended_at'], index_col=0)

dataset_original = dataset.copy()

# set original length of dataset
dataset_len_old = len(dataset)

if verbose:
    print('\n--- loading dataset ---')
    print(dataset.head())
    print(dataset.describe())

# load stations
stations = pd.read_csv(live_data, index_col='station_name')
old_stations = stations.copy()

if verbose:
    print('\n--- loading stations ---')
    print(stations.head())
    print(stations.describe())

# eliminate weekends

n = len(dataset)
dataset = only_weekdays(dataset)
if verbose: 
    print('\n--- removing weekends ---')
    print('{0} weekend entries removed.'.format(n - len(dataset)))

# remove stations with neglectable usage. Those probably got introduced halfway
# through the month and should be taken account for only in the next month.

if verbose: print('\n--- removing unused stations ---')
n = len(dataset)
dataset = remove_unused_stations(dataset, settings['station_usage_threshold'])
if verbose: print('{0} unused station entries removed.'.format(n - len(dataset)))

# remove trips with too long/short duration (outliers)

n = len(dataset)
dataset = remove_duration(dataset, settings['duration_max_quantile'], settings['duration_min_quantile'])
if verbose: 
    print('\n--- removing extreme duration trips ---')
    print('{0} extreme duration entries removed.'.format(n - len(dataset)))

# eliminate all stations from dataset that do not appear in the live stations data

n = len(dataset)
dataset = dataset[dataset['start_station_name'].isin(stations.index)]
dataset = dataset[dataset['end_station_name'].isin(stations.index)]
if verbose: 
    print('\n--- removing stations that are not in the stations list ---')
    print(dataset[~dataset['start_station_name'].isin(stations.index)])
    print(dataset[~dataset['end_station_name'].isin(stations.index)])
    print('{0} entries removed.'.format(n - len(dataset)))

# eliminate all stations from live stations data that do not appear in the dataset

n = len(stations)
stations = stations[stations.index.isin(dataset['start_station_name'])]
stations = stations[stations.index.isin(dataset['end_station_name'])]
if verbose:
    print('\n--- removing stations that are not in the trips anymore ---')
    print(stations[~stations.index.isin(dataset['start_station_name'])])
    print(stations[~stations.index.isin(dataset['end_station_name'])])
    print('{0} entries removed.'.format(n - len(stations)))

# split historic data for validation
'''
limit = int(len(set(dataset.index.day)) * settings['validation_percentage'])
seed = np.random.randint(0,10000)
np.random.seed(seed)
seeds = ''
try:
    with open('results_graphs/seeds.txt', 'r') as file:
        seeds = file.read()
except FileNotFoundError:
    seeds = ''
with open('results_graphs/seeds.txt', 'w+') as file:
    seeds += '{0}\n'.format(seed)
    file.write(seeds)
validation_days = list(set(dataset.index.day))
np.random.shuffle(validation_days)
validation_days = validation_days[:limit]

dataset_split_validation = dataset[dataset.index.day.isin( validation_days)]
dataset = dataset[~dataset.index.day.isin(validation_days)]

dataset_len_validation = len(dataset_split_validation)
dataset_len = len(dataset)
'''
if verbose:
    print('-- splitting datasets ---')

np.random.seed(settings['split_seed'])

validation_days = [dataset[dataset.index.weekday == i].index.day.drop_duplicates().values for i in range(0, 5)]
print(validation_days)
validation_days = [np.random.permutation(w) for w in validation_days]
print(validation_days)
validation_days = list(map(lambda x: x[0], validation_days))
print(validation_days)

dataset_split_validation = dataset[dataset.index.day.isin( validation_days)]
dataset = dataset[~dataset.index.day.isin(validation_days)]

dataset_len_validation = len(dataset_split_validation)
dataset_len = len(dataset)

#############################################################################################
####[ Write Output ]#########################################################################
#############################################################################################

if verbose:
    print('\n--- dataset (cleaned) ---')
    print(dataset.head())
    print(dataset.describe())
    print('\n--- dataset validation (cleaned) ---')
    print(dataset_split_validation.head())
    print(dataset_split_validation.describe())

# write clean list of stations to new csv file
stations.to_csv('stations.csv')

# write clean dataset to new csv file
dataset.to_csv('records.csv')

# write splitted validation dataset to new csv file
dataset_split_validation.to_csv('records_validation.csv')

# compare cleansed stations to original stations
fig, ax = plt.subplots()
fig.set_size_inches(10, 8)
ax.set_title('Stations in the JEB Scheme Before and After Cleansing')
ax.set_xlabel('degrees longitude')
ax.set_ylabel('degrees latitude')
ax.set_aspect(2)
c = ax.scatter(old_stations['station_longitude'],
     old_stations['station_latitude'],
     s=old_stations['station_capacity'],
     color='blue')
o = ax.scatter(stations['station_longitude'],
     stations['station_latitude'],
     s=stations['station_capacity'],
     color='red')
ax.legend((c, o), ('stations removed', 'stations remaining'))
fig.savefig('results_graphs/stations_cleansing_comparison.png', dpi=300)

# compare number of records before and after cleansing
fig, ax = plt.subplots()
fig.set_size_inches(8, 10)
ax.set_title('Number of Records in Historical Dataset Before and After Cleansing')
ax.set_ylabel('#records')
b = ax.bar(['before cleansing', 'after cleansing'], [dataset_len_old, dataset_len], color=['green', 'blue'])
b2 = ax.bar(['after cleansing'], [dataset_len_validation], bottom=[dataset_len], color='navy')
ax.legend((b[0], b[1], b2), ('records before cleansing: {0}'.format(dataset_len_old), 'records after cleansing: {0}'.format(dataset_len), 'records used for validation: {0}'.format(dataset_len_validation)))
fig.savefig('results_graphs/number_of_records_cleansing_comparison.png', dpi=300)