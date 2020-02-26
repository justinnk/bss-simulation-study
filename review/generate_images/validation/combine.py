import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def load_csv(path):
    return pd.read_csv(path, delimiter=';', usecols=[0,1,2,3], names=['time', 'value', 'stddev', 'stderr'])

s_data = {'Bruntsfield links': load_csv('available_bruntsfield_links.csv'), 'Dundee Terrace': load_csv('available_dundee_terrace.csv')}
retrievals = load_csv('retrievals.csv')

dataset_validation = pd.read_csv('records_validation.csv', index_col=0, parse_dates=['started_at', 'ended_at'])
dataset_training = pd.read_csv('records.csv', index_col=0, parse_dates=['started_at', 'ended_at'])

stations = pd.read_csv('stations.csv')

# read arrivals and departures from files for validation and training data
departure_data = pd.read_csv('records_validation.csv', usecols=['started_at', 'start_station_name'], parse_dates=['started_at'], index_col=0)
arrival_data = pd.read_csv('records_validation.csv', usecols=['ended_at', 'end_station_name'], parse_dates=['ended_at'], index_col=0)
departure_data_training = pd.read_csv('records.csv', usecols=['started_at', 'start_station_name'], parse_dates=['started_at'], index_col=0)
arrival_data_training = pd.read_csv('records.csv', usecols=['ended_at', 'end_station_name'], parse_dates=['ended_at'], index_col=0)

# global retrievals
trips_simulation = retrievals
trips_simulation = trips_simulation.set_index('time').diff().fillna(0)
trips_simulation = trips_simulation.groupby(np.floor(trips_simulation.index / 60)).sum()

fig, ax = plt.subplots(figsize=(7, 4))

trips_validation = dataset_validation.resample('60Min').count()
trips_validation = trips_validation[np.isin(trips_validation.index.date, dataset_validation.index.date)]
trips_validation_mean = trips_validation.groupby(trips_validation.index.hour).start_station_name.mean()
trips_validation_var = trips_validation.groupby(trips_validation.index.hour).start_station_name.var() / 100

trips_training = dataset_training.resample('60Min').count()
trips_training = trips_training[np.isin(trips_training.index.date, dataset_training.index.date)]
trips_training_mean = trips_training.groupby(trips_training.index.hour).start_station_name.mean()
trips_training_var = trips_training.groupby(trips_training.index.hour).start_station_name.var() / 100

ax.errorbar(trips_training_mean.index, trips_training_mean.values, trips_training_var.values, label='#retrievals (trainig)', color='#3f6c91')
ax.errorbar(trips_validation_mean.index, trips_validation_mean.values, trips_validation_var.values, label='#retrievals (validation)', color='#06B500')
ax.errorbar(trips_simulation.index, trips_simulation.value, 0, label='d #retrievals / dt (simulation)', color='#1c7ac7')
ax.legend()
ax.set_yticks(range(0, 60, 5), minor=True)
ax.set_xticks(range(0, 24), minor=False)
ax.grid(which='major', linestyle='--')
ax.grid(which='minor', linestyle='--')
ax.set_title('Comparison of Number of Retrievals')
fig.tight_layout()
fig.savefig('retrievals.svg')

# number of hours the simulation is run for
simulation_hours = 24

# list containing error information
valid_err = []
train_err = []

# returns the history of the number of available bikes for the given station
def get_availability(station, departure_frame, arrival_frame):

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
    start = station.station_available
    cap = []
    for i in range(0, simulation_hours):
        if i == 0:
            cap.append(float(start) + change[i])
        else:
            cap.append(cap[i - 1] + change[i])
    cap = np.array(cap)
    return cap

# returns the history of the variance of the number of available bikes for the given station
def get_availability_variance(station, departure_frame, arrival_frame):

    filler = pd.DataFrame(index=pd.date_range(departure_frame.index.min().floor('H'), departure_frame.index.max().floor('H'), freq="60min"))
    filler = filler[np.isin(filler.index.date, departure_frame.index.date)]

    dep_dayly = departure_frame[departure_frame['start_station_name'] == station.station_name]
    dep_dayly = dep_dayly.resample('60Min').count()
    dep_dayly = dep_dayly.join(filler, how='right').fillna(0.0)
    dep_dayly = dep_dayly.groupby(dep_dayly.index.hour).var()
    dep_dayly = dep_dayly.rename(columns={'start_station_name': 'departures'})

    arr_dayly = arrival_frame[arrival_frame['end_station_name'] == station.station_name]
    arr_dayly = arr_dayly.resample('60Min').count()
    arr_dayly = arr_dayly.join(filler, how='right').fillna(0.0)
    arr_dayly = arr_dayly.groupby(arr_dayly.index.hour).var()
    arr_dayly = arr_dayly.rename(columns={'end_station_name': 'arrivals'})

    return dep_dayly['departures'] - arr_dayly['arrivals']

# returns the 99% confidence interval for simulation results.
# only returns the sddev/sqrt(n) part and thus has to be added/subtracted
# to the mean (e.g. with errorbar)
def get_confidence_interval(sim_results):
    z_star_99 = 2.576 # value of the z-distribution for a 99% confidence interval
    c_i = z_star_99 * sim_results.stderr
    return c_i

s_list = ['Bruntsfield links', 'Dundee Terrace']

for i, s in stations[stations.station_name.isin(s_list)].iterrows():

    # get data from simulation
    availability_simulation = s_data[s.station_name]
    availability_simulation.time /= 60.0
    availability_simulation.time -= 1
    availability_simulation = availability_simulation.set_index(availability_simulation.time)
    confidence_simulation = get_confidence_interval(availability_simulation)

    # get data from historic dataset for validation
    availability_validation = get_availability(s, departure_data, arrival_data)
    availability_variance_validation = get_availability_variance(s, departure_data, arrival_data)

    # get data from historic dataset
    availability_training = get_availability(s, departure_data_training, arrival_data_training)
    availability_variance_training = get_availability_variance(s, departure_data_training, arrival_data_training)

    # calculate error
    step = int((1440 + 1) / simulation_hours)
    last_entry = availability_simulation.loc[availability_simulation.index.max()]
    last_entry = pd.DataFrame({'value': [last_entry.value], 'stddev': [last_entry.stddev], 'stderr': [last_entry.stderr]}, index=[23.0])
    avail = availability_simulation.append(last_entry, sort=True)
    error_valid = np.abs(availability_validation - avail.value[0::step])
    error_training = np.abs(availability_training - avail.value[0::step])
    valid_err.append(sum((availability_validation - avail.value[0::step]) ** 2) / simulation_hours)
    train_err.append(sum((availability_training - avail.value[0::step]) ** 2) / simulation_hours)

    # plot results
    fig, ax = plt.subplots(figsize=(4,4))
    ax.set_title('Availability for {0}'.format(s.station_name))
    ax.set_ylim((0, 25))
    ax.set_yticks(range(0, 25), minor=True)
    ax.set_xticks(range(0, 24), minor=True)
    # capacity
    cap = s.station_capacity
    ax.hlines(cap, 0, 24)
    # availability simulation results
    ax.errorbar(availability_simulation['time'], availability_simulation.value, availability_simulation['stddev'], label='stddev sim', color='#d1e3ff', alpha=0.25)
    ax.errorbar(availability_simulation['time'], availability_simulation.value, confidence_simulation, label='#available (simulation)', color='#1c7ac7')
    # availability validation set
    ax.errorbar(range(0, simulation_hours), availability_validation, availability_variance_validation, label='#available (validation)', color='#06B500')
    # availability training set
    ax.errorbar(range(0, simulation_hours), availability_training, availability_variance_training, label='#available (trainig)', color='#3f6c91')
    # error
    ax.plot(error_valid, label='abs. err. (sim./validation)', color='#ba0d21')
    ax.plot(error_training, label='abs. err. (sim./training)', color='#de7016')
    ax.legend()
    ax.grid(which='major', linestyle='-')
    ax.grid(which='minor', linestyle='--')
    fig.tight_layout()
    fig.savefig('{0}_available.svg'.format(s.station_name))
    plt.close(fig)