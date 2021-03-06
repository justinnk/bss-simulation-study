import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

stations = pd.read_csv('stations.csv')
empty = pd.read_csv('phi_empty.csv', names=['par', 'loc', 'prob', 'min', 'max', 'stddev'])
full = pd.read_csv('phi_full.csv', names=['par', 'loc', 'prob', 'min', 'max', 'stddev'])

fig, axs = plt.subplots(1, 2, figsize=(6,3), sharey=True)

axs[0].scatter(stations.station_longitude, stations.station_latitude, c=empty[empty.par == 2].prob, s=9, cmap='coolwarm', vmin=0, vmax=1)#s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
axs[0].set_title(r'$\varphi_{empty}$ over Day 3 (Baseline)')
col = axs[1].scatter(stations.station_longitude, stations.station_latitude, c=full[full.par == 2].prob, s=9, cmap='coolwarm', vmin=0, vmax=1)#s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
axs[1].set_title(r'$\varphi_{full}$ over Day 3 (Baseline)')

fig.tight_layout()
fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.05, 0.025, 0.9])
fig.colorbar(col, cax=cbar_ax)
fig.savefig('baseline_empty_full.svg', ppi=300)