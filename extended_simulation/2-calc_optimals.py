# @author justinnk
# calculates optimal allocations to satisfy the average demand of one day.
# uses a hill climbing algorithm to keep the number of available bikes between 3 and capacity-3.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_availability(station, departure_frame, arrival_frame, available):

    filler = pd.DataFrame(index=pd.date_range(departure_frame.index.min().floor('H'), departure_frame.index.max().floor('H'), freq="60min"))
    filler = filler[np.isin(filler.index.date, departure_frame.index.date)] # departure_frame for both because of possible endings in unwanted (validation) days

    dep_dayly = departure_frame[departure_frame['start_station_name'] == station.station_name]
    dep_dayly = dep_dayly.resample('60Min').count()
    dep_dayly = dep_dayly.join(filler, how='right').fillna(0.0)
    dep_dayly = dep_dayly.groupby(dep_dayly.index.hour).mean()
    dep_dayly = dep_dayly.rename(columns={'start_station_name': 'departures'})

    arr_dayly = arrival_frame[(arrival_frame['end_station_name'] == station.station_name) & ~(arrival_frame.index.date != departure_frame.index.date)]
    arr_dayly = arr_dayly.resample('60Min').count()
    arr_dayly = arr_dayly.join(filler, how='right').fillna(0.0)
    arr_dayly = arr_dayly.groupby(arr_dayly.index.hour).mean()
    arr_dayly = arr_dayly.rename(columns={'end_station_name': 'arrivals'})

    change = arr_dayly['arrivals'] - dep_dayly['departures']
    start = available
    cap = []
    for i in range(0, 24):
        if i == 0:
            cap.append(float(start) + change[i])
        else:
            cap.append(cap[i - 1] + change[i])
    cap = np.array(cap)
    return cap

departures_aug = pd.read_csv('records.csv', usecols=['started_at', 'start_station_name'], index_col='started_at', parse_dates=['started_at'])
arrivals_aug = pd.read_csv('records.csv', usecols=['ended_at', 'end_station_name'], index_col='ended_at', parse_dates=['ended_at'])
stations_aug = pd.read_csv('stations.csv')

availability = []
for i, s in stations_aug.iterrows():
    problematic = True
    up = False
    last_up = False
    counter = 0
    percent = 0.45
    while problematic:
        print(s.station_name, percent)
        last_up = up
        available = int(s.station_capacity * percent)
        cap = get_availability(stations_aug[stations_aug.station_name == s.station_name].iloc[0],
                               departures_aug, arrivals_aug, available)
        available = cap
        if (available < 4).any():
            percent += 0.05
            up = True
            if not last_up:
                counter += 1
        elif (available > s.station_capacity - 4).any():
            percent -= 0.05
            up = False
            if last_up:
                counter += 1
        else:
            problematic = False
            availability.append(int(s.station_capacity * percent))
        if percent < 0.0:
            availability.append(0)
            break
        elif percent > 1.0:
            availability.append(s.station_capacity - 1)
            break
        if counter >= 4:
            availability.append(int(s.station_capacity * percent))
            break

# write changes
stations_aug['station_optimal'] = availability
print(stations_aug.head())
stations_aug.set_index('station_name').to_csv('stations.csv')

