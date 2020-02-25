# @author justinnk
# Visualizes the outcomes of the simulation
# 
# users.png
#   number of users simultaneously using the system 
#   (note: this is not comparable to number of trips!)
# trips.png
#   cumulative number of trips
# stations_status.png
#   number of empty/full stations
# stations_available.png
#   min, max and avg filling percentage of the stations
# user_satisfaction.png
#   levels of user dissatisfaction over time
# user_satisfaction_measure.png
#   combined measure for user dissatisfaction
# simulation_stats.txt
#   number of trips
#   number of incentivised trips
#   min/mean/median/max user dissatisfaction
#   redistribution effort

import csv
import os
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# load settings from file
settings = {}
with open('settings.json', 'r') as file:
    settings = json.loads(file.read())

# output dir
output_dir = settings['output_dir']

# iteration variables
x = []
y = []
stddev = []
stderr = []

max_time = 4319
width = 24

# figures
fig, ax = plt.subplots()
fig.set_size_inches(width, 8)
fig.tight_layout()
ax.set_yticks(range(0, 500, 20), minor=True)
ax.set_xticks(range(0, max_time, 60), minor=False)
ax.grid(which='major', linestyle='--')
ax.grid(which='minor', linestyle='--')

fig2, ax2 = plt.subplots()
fig2.set_size_inches(width, 8)
fig2.tight_layout()
ax2.set_yticks(range(0, 20), minor=True)
ax2.set_xticks(range(0, max_time, 60), minor=False)
ax2.grid(which='major', linestyle='--')
ax2.grid(which='minor', linestyle='--')

fig3, ax3 = plt.subplots()
fig3.set_size_inches(width, 8)
fig3.tight_layout()

fig4, ax4 = plt.subplots()
fig4.set_size_inches(width, 8)
fig4.tight_layout()

fig6, ax6 = plt.subplots()
fig6.set_size_inches(width, 8)
fig6.tight_layout()
ax6.set_yticks(range(0, 60, 1), minor=True)
ax6.set_xticks(range(0, int(max_time / 60), 1), minor=False)
ax6.grid(which='major', linestyle='--')
ax6.grid(which='minor', linestyle='--')

def get_color(dissatisfaction):
    if dissatisfaction.startswith('DissatisfiedRet[level=0'):
        return '#ffbaba'
    elif dissatisfaction.startswith('DissatisfiedRet[level=1'):
        return '#dc6767'
    elif dissatisfaction.startswith('DissatisfiedRet[level=2'):
        return '#b74141'
    elif dissatisfaction.startswith('DissatisfiedRet[level=3'):
        return '#7e0606'
    elif dissatisfaction.startswith('DissatisfiedGet[level=0'):
        return '#bae3ff'
    elif dissatisfaction.startswith('DissatisfiedGet[level=1'):
        return '#68bfdc'
    elif dissatisfaction.startswith('DissatisfiedGet[level=2'):
        return '#419ab7'
    elif dissatisfaction.startswith('DissatisfiedGet[level=3'):
        return '#06607e'
    else:
        return '#000000'

def get_values(filename, data):
    if filename.startswith('DissatisfiedRet[level=0'):
        d_ret[0] = data
    elif filename.startswith('DissatisfiedRet[level=1'):
        d_ret[1] = data
    elif filename.startswith('DissatisfiedRet[level=2'):
        d_ret[2] = data
    elif filename.startswith('DissatisfiedRet[level=3'):
        d_ret[3] = data
    elif filename.startswith('DissatisfiedGet[level=0'):
        d_get[0] = data
    elif filename.startswith('DissatisfiedGet[level=1'):
        d_get[1] = data
    elif filename.startswith('DissatisfiedGet[level=2'):
        d_get[2] = data
    elif filename.startswith('DissatisfiedGet[level=3'):
        d_get[3] = data

d_get = [None, None, None, None]
d_ret = [None , None, None, None]

results = ['Results']

for file in os.listdir('Results'):
    if file.endswith('.csv'):
        if file.startswith('Biking') or file.startswith('GlobalUsers') or file.startswith('Returning') or file.startswith('Waiting'):
            with open(os.path.join('Results', file),'r') as csvfile:
                plots = csv.reader(csvfile, delimiter=',')
                for row in plots:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    stddev.append(float(row[2]))
                    stderr.append(float(row[3]))
                ax2.errorbar(x, y, stddev, label=file + ' (stddev)', color='#d1e3ff', alpha=0.5)
                ax2.errorbar(x, y, stderr, label=file + '(stderr)')
        elif file.startswith('DissatisfiedRet') or file.startswith('DissatisfiedGet'):
            with open(os.path.join('Results', file),'r') as csvfile:
                plots = csv.reader(csvfile, delimiter=',')
                res = pd.read_csv(os.path.join('Results', file), delimiter=',', usecols=[0,1,2,3], names=['time', 'value', 'stddev', 'stderr'])
                res = res.set_index('time').diff()
                res = res.groupby(np.floor(res.index / 60)).sum()
                #ax2.errorbar(x, y, stddev, label=file + ' (stddev)', color='#d1e3ff', alpha=0.5)
                get_values(file, res)
                ax6.errorbar(res.index, res.value, res.stderr, label=file + '(stderr)', color=get_color(file))
        elif file.startswith('FullStations') or file.startswith('StarvedStations'):
            with open(os.path.join('Results', file),'r') as csvfile:
                plots = csv.reader(csvfile, delimiter=',')
                for row in plots:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    stddev.append(float(row[2]))
                    stderr.append(float(row[3]))
                ax4.errorbar(x, y, stddev, label=file + ' (stddev)', color='#d1e3ff', alpha=0.5)
                ax4.errorbar(x, y, stderr, label=file + ' (stderr)')
        elif file.startswith('Max') or file.startswith('Min') or file.startswith('Avg'):
            with open(os.path.join('Results', file),'r') as csvfile:
                plots = csv.reader(csvfile, delimiter=',')
                for row in plots:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    stddev.append(float(row[2]))
                    stderr.append(float(row[3]))
                ax3.errorbar(x, y, stddev, label=file + ' (stddev)', color='#d1e3ff', alpha=0.5)
                ax3.errorbar(x, y, stderr, label=file + ' (stderr)')
        elif file.startswith('Retrievals') or file.startswith('Returns') or file.startswith('IncRetrievals') or file.startswith('IncReturns'):
            with open(os.path.join('Results', file),'r') as csvfile:
                plots = csv.reader(csvfile, delimiter=',')
                for row in plots:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    stddev.append(float(row[2]))
                    stderr.append(float(row[3]))
                ax.errorbar(x, y, stddev, label=file + ' (stddev)', color='#d1e3ff', alpha=0.5)
                ax.errorbar(x, y, stderr, label=file + ' (stderr)')
    x = []
    y = []
    stddev = []
    stderr = []

ax.legend()
ax2.legend()
ax3.legend()
ax4.legend()
ax6.legend()

# user dissatisfaction
user_dissatisfaction_get = sum([i * (d_get[i]) for i in range(0, 4)]).value / sum([d_get[i] for i in range(0, 4)]).value
user_dissatisfaction_ret = sum([i * (d_ret[i]) for i in range(0, 4)]).value / sum([d_ret[i] for i in range(0, 4)]).value
user_dissatisfaction = (user_dissatisfaction_get + user_dissatisfaction_ret)
fig7, ax7 = plt.subplots()
fig7.set_size_inches(width, 8)
fig7.tight_layout()
ax7.set_ylim((0, 3))
ax7.plot(user_dissatisfaction_get.index, user_dissatisfaction_get, label='get dissatisfaction measure', color='#06607e')
ax7.plot(user_dissatisfaction_ret.index, user_dissatisfaction_ret, label='return dissatisfaction measure', color='#7e0606')
ax7.plot(user_dissatisfaction.index, user_dissatisfaction, label='overall dissatisfaction measure', color='green')
ax7.legend()

# number of trips and incentives
def get_csv(path):
    return pd.read_csv(os.path.join('Results', path),
                    usecols=[0,1,2,3], names=['time', 'value', 'stddev', 'stderr'],
                    index_col='time')

ret = get_csv('Returns.csv')
inc_get = get_csv('IncRetrievals.csv')
inc_ret = get_csv('IncReturns.csv')

# redistributions
def get_result_for_station(i, results):
    for f in results:
        if f[0] == 'Available[sid={0}].csv'.format(i):
            return f[1]
    return None

results = [ (f, get_csv(f)) for f in os.listdir('Results') if f.startswith('Available')]
stations = pd.read_csv('stations.csv')
redist = [0, 0, 0]

for i, s in enumerate(stations):
    r = get_result_for_station(i, results)
    fill_level = r.iloc[1439].value
    desired_fill_level = stations.iloc[i].station_optimal
    redist[0] += abs(desired_fill_level - fill_level)
    fill_level = r.iloc[2879].value
    redist[1] += abs(desired_fill_level - fill_level)
    fill_level = r.iloc[4319].value
    redist[2] += abs(desired_fill_level - fill_level)

# save to file
with open(output_dir + '/simulation_stats.txt', 'w+') as file:
    file.write('Number of Finished Trips: {0} +- {1}\n'.format(ret.iloc[4319].value, ret.iloc[4319].stderr))
    file.write('Number of Get Incentives: {0} +- {1}\n'.format(inc_get.iloc[4319].value, inc_get.iloc[4319].stderr))
    file.write('Number of Ret Incentives: {0} +- {1}\n'.format(inc_ret.iloc[4319].value, inc_ret.iloc[4319].stderr))
    file.write('-' * 10)
    file.write('\nuser dissatisfaction max/mean/median/min\n')
    file.write(str(round(user_dissatisfaction.max(), 3)))
    file.write('/')
    file.write(str(round(user_dissatisfaction.mean(), 3)))
    file.write('/')
    file.write(str(round(user_dissatisfaction.median(), 3)))
    file.write('/')
    file.write(str(round(user_dissatisfaction.min(), 3)))
    file.write('\n' + '-' * 10)
    file.write('\nRedistribution effort as sum of the differences from optimal fill level:\n')
    file.write('1439 / 2879 / 4319\n')
    file.write(str(redist))


# save the figures
fig.savefig(output_dir + '/trips.png', dpi=100)
fig2.savefig(output_dir + '/users.png', dpi=100)
fig3.savefig(output_dir + '/stations_available.png', dpi=100)
fig4.savefig(output_dir + '/stations_status.png', dpi=100)
fig6.savefig(output_dir + '/user_satisfaction.png', dpi=100)
fig7.savefig(output_dir + '/user_satisfaction_measure.png', dpi=100)
