# author: justinnk
# generates trajectories from the historical data by splitting it into weekdays.

import numpy as np
import pandas as pd

# load snapshot table
print('loading datasets')
snaps_aug = pd.read_csv('../data/station_snapshot_aug.csv', parse_dates=['timestamp'], index_col='timestamp')
snaps_aug = snaps_aug.drop(columns=['latitude', 'longitude'])

# resample for 1Min granularity
print('resampling')
snaps_aug_hourly = snaps_aug.groupby('dock_group_title').resample('1Min').mean()

# fill missing times
full_range = pd.date_range('2019-08-01 00:00:00', '2019-08-31 23:59:59', freq='1Min')
stations = snaps_aug.groupby('dock_group_title').first().index.values
new_index = pd.MultiIndex.from_product([stations, full_range], names=['dock_group_title', 'timestamp'])
snaps_aug_hourly = snaps_aug_hourly.reindex(new_index)
snaps_aug_hourly = snaps_aug_hourly.reset_index().fillna(method='ffill')

# produce individual trace for every day
pd.options.mode.chained_assignment = None # suppress unnecessary warning
print('generating traces')
print(snaps_aug_hourly.head())
stations_aug = pd.read_csv('stations.csv', usecols=['station_name']).reset_index()
n = 0
for i in range(0, 31):
    if pd.Timestamp('2019-08-{0}'.format(str(i + 1).zfill(2))).dayofweek < 5:
	    print('day {0}: n0. {1}'.format(i + 1, n))
	    trace = snaps_aug_hourly[snaps_aug_hourly.timestamp.dt.day == i + 1]
	    trace.timestamp = trace.timestamp.apply(lambda x: x.hour * 60 + x.minute)
	    trace = trace.sort_values('timestamp').set_index('timestamp').sort_index().reset_index()
	    trace = trace.merge(stations_aug, left_on='dock_group_title', right_on='station_name')
	    trace = trace.drop(columns=['station_name', 'dock_group_title'])
	    trace = trace.rename(columns={'index': 'location'})
	    trace = trace.sort_values('timestamp').sort_values(by=['timestamp', 'location'])
	    trace.to_csv('Traces/Traj{0}.csv'.format(n), columns=['timestamp', 'location',
		                                          'available_bikes', 'available_docks'], index=False, header=False)
	    n += 1
