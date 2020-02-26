import os
import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

files = glob.glob('*.csv')
files = list(filter(lambda x: x != 'stations.csv', files))
files.sort()

stations = pd.read_csv('stations.csv')

fig, axss = plt.subplots(3, 3, figsize=(8,7.5), sharey=True, sharex=True)

for i, axs in enumerate(axss):
    for j, ax in enumerate(axs):
        data = pd.read_csv(files[j + 3 * i], names=['par', 'loc', 'prob', 'min', 'max', 'stddev'])
        #ax.set_title(files[j + 3 * i])
        col = ax.scatter(stations.station_longitude, stations.station_latitude, c=data[data.par == 13].prob, s=9, cmap='coolwarm', vmin=0, vmax=1)#s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)

fig.tight_layout()
fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.05, 0.025, 0.9])
fig.colorbar(col, cax=cbar_ax)
fig.savefig('prob_comparison.svg', ppi=300)



'''
real = pd.read_csv('real_phi_dist.csv', names=['par', 'loc', 'prob', 'min', 'max', 'stddev'])

fig, axs = plt.subplots(1, 2, figsize=(6,3), sharey=True)

axs[0].set_title('phi_prob on Day 1 (Actual)')
axs[0].scatter(stations.station_longitude, stations.station_latitude, c=real[real.par == 0].prob, s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
axs[1].set_title('phi_prob on Day 1 (Baseline)')
col = axs[1].scatter(stations.station_longitude, stations.station_latitude, c=baseline[baseline.par == 12].prob, s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)

fig.tight_layout()
fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.05, 0.025, 0.9])
fig.colorbar(col, cax=cbar_ax)
fig.savefig('baseline_comparison.png', ppi=300)
'''