#%% [markdown]
# This script will generate a list of stations with capacity and initial number of available bikes for august. It will be saved in the `data` folder as `stations_aug.csv`.

#%%
import numpy as np
import pandas as pd


#%%
snapshots_aug = pd.read_csv('../data/station_snapshot_aug.csv', parse_dates=['timestamp'], index_col='timestamp')

#%% [markdown]
# The list of stations will comprise all stations that are recorded in the first few entries of the dataset.

#%%
stations_aug = snapshots_aug[snapshots_aug.index.day == 1].groupby('dock_group_title').first()

#%% [markdown]
# Calculate the capacity of the stations as sum of the medians of available bikes and available slots at their first appearance.

#%%
cap_aug = snapshots_aug.groupby('dock_group_title').available_docks.median()
cap_aug += snapshots_aug.groupby('dock_group_title').available_bikes.median()
stations_aug['station_capacity'] = np.ceil(cap_aug)


#%%
stations_aug = stations_aug.drop(columns=['available_bikes', 'available_docks'])

#%% [markdown]
# Set the number of initially available bikes (e.g. the number of bikes available at the start of the day in the simulation) to the median availability between 12pm and 2pm (inclusive).

#%%
first_aug = snapshots_aug[(snapshots_aug.index.hour <= 2)]
stations_aug['station_available'] = np.ceil(first_aug.groupby('dock_group_title')['available_bikes'].median())

#%% [markdown]
# Rename all the columns to match the format of the open data and set the proper index.

#%%
cols = {'latitude': 'station_latitude', 'longitude': 'station_longitude', 'dock_group_title': 'station_name'}
stations_aug = stations_aug.reset_index()
stations_aug = stations_aug.rename(columns=cols)
stations_aug = stations_aug.set_index(stations_aug.station_name)
stations_aug = stations_aug.drop(columns=['station_name'])


#%%
stations_aug.head()


#%%
stations_aug.index.values

#%% [markdown]
# In this step, we eliminate all the stations that are not important or would even harm our study. The stations on the blacklist are for special events/customers only, so we don't want them for the average day. Through further investigation (see the very bottom of this notebook), we also found that "Pollock Halls Virtual" always has no bikes available (maybe the status wasn't updated to decomissioned/not_in_service).

#%%
blacklist = ['Depot Virtual', 'Eden Locke - Aparthotel (RESIDENTS ONLY)',
             'Fountain Court  - Apartments (RESIDENTS ONLY)',
             'Haymarket - Murrayfield Rugby Event', "Holyrood Park - Woman's Tour Of Scotland (Event 11/08/19)",
             'Pollock Halls Virtual']
stations_aug = stations_aug[~stations_aug.index.isin(blacklist)]


#%%
stations_aug.station_capacity = stations_aug.station_capacity.astype(int)
stations_aug.station_available = stations_aug.station_available.astype(int)


#%%
stations_aug.describe()


#%%
stations_aug.to_csv('../data/stations_aug.csv')

#%% [markdown]
# Finally we do some sanity checks to see whether the total number of available bikes in the system is roughly the same as in the beginning of the original dataset. As you can see, the difference is negligible.

#%%
avail_orig = snapshots_aug.groupby('dock_group_title')['available_bikes'].first().sum()
avail_orig


#%%
stations_aug = pd.read_csv('../data/stations_aug.csv')


#%%
avail_deriv = stations_aug.station_available.sum()
avail_deriv


#%%
avail_orig - avail_deriv

#%% [markdown]
# As mentioned above, this station seems to be not active during August.

#%%
(snapshots_aug[snapshots_aug.dock_group_title == 'Pollock Halls Virtual'].available_bikes > 0).any()


