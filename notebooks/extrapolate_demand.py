#%% [markdown]
# This notebook will add latent demand to the trips. It is assumed that the phenomenon of censored demand occurs when a station is empty for at least one hour. To recreate the information about the missing trips, new trips are added randomly based on the average behaviour during the same period at other days, but only when the station was not empty. The seed used for our study is 42.

#%%
import numpy as np
import pandas as pd

seed = 42
np.random.seed(seed)


#%%
stations = pd.read_csv('../data/stations_aug.csv')

#%% [markdown]
# Load the snapshots and trips data. The index is rounded to one hour to focus on periods of a full hour.

#%%
snapshots = pd.read_csv('../data/station_snapshot_aug.csv', usecols=['timestamp',
                            'dock_group_title', 'available_bikes'], parse_dates=['timestamp'], index_col='timestamp')
snapshots.index = snapshots.index.map(lambda x: x.round('H'))


#%%
trips_set = pd.read_csv('../data/trips_08-2019.csv', usecols=['started_at', 'ended_at', 'start_station_name',
                        'end_station_name', 'duration'], parse_dates=['started_at', 'ended_at'], index_col='started_at')
trips_set.index = trips_set.index.map(lambda x: x.round('H'))

#%% [markdown]
# The dataset with the additional trips.

#%%
new_trips = pd.DataFrame(columns=['started_at',
                        'ended_at',
                        'duration',
                        'start_station_name',
                        'end_station_name'])
new_trips.started_at = pd.to_datetime(new_trips.started_at)
new_trips.ended_at = pd.to_datetime(new_trips.ended_at)

#%% [markdown]
# This function determines the distribution of all possible destinations in the given dataframe.

#%%
def get_transitions(ds):
    destinations = ds.groupby('end_station_name')['end_station_name'].count().to_frame()
    destinations = destinations.rename(columns={'end_station_name': 'count'})
    destinations = destinations.reset_index()
    destinations['prob'] = destinations['count'] / destinations['count'].sum()
    return destinations

#%% [markdown]
# This function uses `get_transitions` to randomly pick a destination based on the returnd distribution. If it is unsuccessful with the dataset for `hour`, it will try again using the complete dataset, e.g. the overall destination distribution. If that also fails, it will return -1.

#%%
def select_end_station(hour, start_station):
    prob = get_transitions(trips_set[(trips_set.start_station_name == start_station) & (trips_set.index.hour == hour)])
    if len(prob) == 0:
        prob = get_transitions(trips_set[(trips_set.start_station_name == start_station)])
    if len(prob) == 0:
        return -1
    prob = np.random.choice(prob.end_station_name, p=prob.prob, size=1)
    return prob

#%% [markdown]
# This function will generate a new entry for the trips data. The journey will start at `start_station`. It uses the average behaviour in hour `hour` for the station `start_station`. If it is unsuccessfull, it will return an empty dictionary `{}` instead.

#%%
def generate_trip(hour, start_station):
    # choose starting time
    started_at_hour = (h + (0.9 * np.random.rand()))
    started_at_minute = int(round((started_at_hour - int(started_at_hour)) * 60, 0))
    if started_at_minute >= 60:
        started_at_minute = 59
    started_at_hour = int(started_at_hour)
    started_at = pd.Timestamp(year=d.year, month=d.month, day=d.day,
                             hour=started_at_hour, minute=started_at_minute, second=0,
                             microsecond=0)
    # choose origin
    start_station_name = start_station
    # choose destination
    end_station_name = select_end_station(h, start_station)
    if end_station_name == -1:
        return {}
    else:
        end_station_name = end_station_name[0]
    # calculate duration
    duration = trips_set[trips_set.start_station_name == start_station].groupby('end_station_name').duration.mean()
    duration = duration[duration.index == end_station_name]
    if len(duration) <= 0:
        duration = trips_set.duration.mean()
    else:
        duration = duration.values[0]
    # calculate ending time
    ended_at = started_at + pd.to_timedelta(duration, unit='s')
    return {
        'started_at': started_at,
        'ended_at': ended_at,
        'duration': duration,
        'start_station_name': start_station_name,
        'end_station_name': end_station_name
    }

#%% [markdown]
# This is the actual algorithm, that generates the latent demand.

#%%
for station in stations.station_name:
    print('fill for station {0}'.format(station))
    # get all the entries from the snapshots data where the current station was empty
    station_empty = snapshots[(snapshots.dock_group_title == station) & (snapshots.available_bikes == 0)] 
    # pick only those entries where there was no trip in the trips data
    station_empty = station_empty[~station_empty.index.isin(trips_set[trips_set.start_station_name == station].index)]
    # repeat for all hours where the station was empty
    for h in station_empty.index.drop_duplicates().hour:
        # get average demand for that hour when the station was not empty
        trips = trips_set[(trips_set.start_station_name == station)].resample('60Min').duration.count()
        trips = trips.groupby(trips.index.hour).mean()
        trips = trips[trips.index == h]
        # determine the number of trips to generate as the rounded average
        if len(trips) > 0:
            n_trips = int(round(trips.values[0], 0))
        else:
            n_trips = 0
        # loop through all the dates where the station was empty at the current hour
        for d in station_empty[station_empty.index.hour == h].index.drop_duplicates().date:
            # generate trips and append them to the new_trips dataframe
            for i in np.arange(0, n_trips):
                trip = generate_trip(h, station)
                if len(trip) > 0:
                    new_trips = new_trips.append(trip, ignore_index=True)


#%%
new_trips.describe()

#%% [markdown]
# Load the old trips data again and add the newly generated journeys.

#%%
old_trips = pd.read_csv('../data/trips_08-2019.csv', usecols=['started_at', 'ended_at', 'duration', 'start_station_name',
                        'end_station_name'], parse_dates=['started_at', 'ended_at'], index_col='started_at')


#%%
new_trips = new_trips.set_index(new_trips.started_at)
old_trips = old_trips.append(new_trips, sort=True)


#%%
old_trips = old_trips.drop(columns=['started_at'])
old_trips.head()


#%%
old_trips.to_csv('../data/trips_08-2019_latent_demand.csv', columns=['ended_at', 'duration', 'start_station_name',
                        'end_station_name'])


#%%



