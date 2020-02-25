# @author justinnk
# Visualizes the cleansed data:
#   - geographical position of stations (stations.png)
#   - roundtrips per station (start_station = end_station) (roundtrips.png)
#   - arrivals and departures per station (arrivals_departures_absolute.png and arrivals_departures_average.png)
#   - average durations of trips for each hour of the day
# and generates some stats (stats.txt):
#   - number of users per month
#   - number of users per day
#   - maximum trip duration
#   - minimum trip duration
#   - average trip duration
#   - median of trip duration
# that can be used for comparison with the validations stats (stats_validation.txt)

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# load settings from file
settings = {}
with open('settings.json', 'r') as file:
    settings = json.loads(file.read())

# output dir
output_dir = settings['output_dir']

# load stations list from csv file
stations = pd.read_csv('stations.csv')

# load records from csv file
dataset = pd.read_csv('records.csv', parse_dates=['started_at', 'ended_at'], index_col=0)

d = dataset.resample('D').count()
d = d[d.duration > 0]
days_in_set = len(d)

# stats training
total_users_this_month = len(dataset)
corrected_users_this_month = total_users_this_month - len(dataset[dataset.index.date != dataset.ended_at.dt.date]) - len(dataset[dataset.ended_at.dt.weekday >= 5])
avg_users_per_day = len(dataset) / days_in_set
corrected_avg_users = corrected_users_this_month / days_in_set

maximum_trip_duration = dataset.duration.max()
minimum_trip_duration = dataset.duration.min()
avg_trip_duration = dataset.duration.mean()
median_trip_duration = dataset.duration.median()

with open(output_dir + '/stats.txt', 'w+') as file:
    file.write(
        '''
All calculations EXCLUDE the records from the validation set
Numbers in brackets: corrected for trips that ended on weekends/days in validation set
Number of days in calculations: {6}
total users in month: {0} ({7})
average users per day: {1} ({8})

maximum trip duration: {2} m
minimum trip duration: {3} m
average trip duration: {4} m
medain trip duration: {5} m
        '''.format(
            total_users_this_month,
            avg_users_per_day,
            maximum_trip_duration / 60.0,
            minimum_trip_duration / 60.0,
            avg_trip_duration / 60.0,
            median_trip_duration / 60.0,
            days_in_set,
            corrected_users_this_month,
            corrected_avg_users
        )
    )

# stats validation
dataset_validation = pd.read_csv('records_validation.csv', parse_dates=['started_at', 'ended_at'], index_col=0)
days_in_set = dataset_validation.resample('D').count()
days_in_set = days_in_set[days_in_set.duration > 0]
days_in_set = len(days_in_set)

total_users_this_month = len(dataset_validation)
avg_users_per_day = len(dataset_validation) / days_in_set

maximum_trip_duration = dataset_validation['duration'].max()
minimum_trip_duration = dataset_validation['duration'].min()
avg_trip_duration = dataset_validation['duration'].mean()
median_trip_duration = dataset_validation['duration'].median()

with open(output_dir + '/validation_stats.txt', 'w+') as file:
    file.write(
        '''
All calculations ARE BASED on the records from the validation set
Number of days in calculations: {6}
total users in month: {0}
average users per day: {1}

maximum trip duration: {2} m
minimum trip duration: {3} m
average trip duration: {4} m
medain trip duration: {5} m
        '''.format(
            total_users_this_month,
            avg_users_per_day,
            maximum_trip_duration / 60.0,
            minimum_trip_duration / 60.0,
            avg_trip_duration / 60.0,
            median_trip_duration / 60.0,
            days_in_set
        )
    )

# Visualize Stations
station_numbers = np.arange(len(stations))
longs = stations.station_longitude
lats = stations.station_latitude
caps = stations.station_capacity * 2
fig, ax = plt.subplots()
fig.set_size_inches(12, 8)
ax.set_title('Geographical positions of Stations in the JEB Scheme')
ax.set_xlabel('Degrees Longitude')
ax.set_ylabel('Degrees Latitude')
st = ax.scatter(longs,
     lats,
     s=caps,
     color='red')
for i, txt in enumerate(station_numbers):
    size = caps[i] * 0.008
    ax.annotate(txt, (longs[i], lats[i]), ha='center', va='center', size=size if size > 10 else 10, color='black')
ax.legend(('station; greater radius means greater capacity', st))
plt.savefig(output_dir + '/stations.png', dpi=300)

# write station numbers to file
with open(output_dir + '/station_numbers.txt', 'w+') as file:
    for n in station_numbers:
        file.write('{0}: {1} ({2})\n'.format(n, stations.iloc[n]['station_name'], stations.iloc[n]['station_capacity']))

# visualize roundtrips per station
roundtrips = dataset[dataset.start_station_name == dataset.end_station_name]
roundtrips = roundtrips.groupby('start_station_name').count()
fig, ax = plt.subplots()
fig.set_size_inches(12, 8)
ax.set_title('Number of Roundtrips per Month')
ax.set_xlabel('station name')
ax.set_ylabel('#roundtrips')
ro = ax.bar(roundtrips.index, roundtrips.duration)
plt.xticks(rotation='90')
fig.subplots_adjust(bottom=0.3)
fig.savefig(output_dir + '/roundtrips.png', dpi=300)


# arrivals and departures per station
fig, ax = plt.subplots()
fig.set_size_inches(12, 8)
ax.set_title('Total Arrivals and Departures from Stations per Month')
ax.set_xlabel('station name')
ax.set_ylabel('absolute frequency')
width = 0.35
dar = dataset.groupby('end_station_name').count().reset_index()
dde = dataset.groupby('start_station_name').count().reset_index()
ar = ax.bar(dar.index, dar.duration, width)
de = ax.bar(dar.index + width, dde.duration, width)
ax.set_xticks(dar.index + width / 2)
ax.set_xticklabels(stations.station_name.sort_values())
ax.legend((ar[0], de[0]), ('#arrivals', '#departures'))
ax.autoscale_view()
plt.xticks(rotation='90')
fig.subplots_adjust(bottom=0.3)
fig.savefig(output_dir + '/arrivals_departures_absolute.png', dpi=300)