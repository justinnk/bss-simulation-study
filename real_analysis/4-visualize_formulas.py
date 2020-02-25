# author: justinnk
# Produces visualizations of the satisfaction probability of the evaluated formulas

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

stations = pd.read_csv('stations.csv')

results_dir = 'Formulas'

results = os.listdir(results_dir)

dist_pics = []
dist_selection = [1, 6, 10]
time_pics = []
time_selection = [1, 5, 10]
empty = None
full = None
prob = []

for r in results:
    data = pd.read_csv(os.path.join(results_dir, r), names=['par', 'loc', 'prob', 'min', 'max', 'stddev'])
    for p in data.par.drop_duplicates():
        print('generating image for {0}_{1}'.format(r[:-4], p))
        fig, ax = plt.subplots(figsize=(10,10))
        ax.set_title('formula {0}, parameter configuration {1}'.format(r[:-4], p))
        col = ax.scatter(stations.station_longitude, stations.station_latitude, c=data[data.par == p].prob, cmap='coolwarm', vmin=0, vmax=1)#s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
        fig.colorbar(col)
        fig.tight_layout()
        fig.savefig('results_graphs/formulas/{0}_{1}'.format(r[:-4], p))
        plt.close()
        if r[:-4] == 'phi_dist':
              if p in dist_selection:
                   dist_pics.append(data[data.par == p])
        elif r[:-4] == 'phi_time':
              if p in time_selection:
                   time_pics.append(data[data.par == p])
        elif r[:-4] == 'phi_empty':
              empty = data[data.par == p]
        elif r[:-4] == 'phi_full':
              full = data[data.par == p]
        elif r[:-4] == 'phi_prob':
              prob.append(data[data.par == p])

# generate story for phi_dist and phi_time
fig, axs = plt.subplots(2, 3, figsize=(8, 5), sharey=True, sharex=True)
for i, ax in enumerate(axs[0]):
        ax.set_title(r'$\varphi_{{dist}}$ with d={0}m'.format(dist_selection[i] * 50))
        col = ax.scatter(stations.station_longitude, stations.station_latitude, c=dist_pics[i].prob, cmap='coolwarm', s=9, vmin=0, vmax=1)#s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
for i, ax in enumerate(axs[1]):
        ax.set_title(r'$\varphi_{{time}}$ with t={0}min'.format(time_selection[i]))
        col = ax.scatter(stations.station_longitude, stations.station_latitude, c=time_pics[i].prob, cmap='coolwarm', s=9, vmin=0, vmax=1)#s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
fig.tight_layout()
fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.05, 0.025, 0.9])
fig.colorbar(col, cax=cbar_ax)
fig.savefig('results_graphs/dist_time_story.svg', ppi=300)

# generate joint image for phi_empty and phi_full
fig, axs = plt.subplots(1, 2, figsize=(6,3), sharey=True)
axs[0].set_title(r'satisfaction of $\varphi_{empty}$')
axs[0].scatter(stations.station_longitude, stations.station_latitude, c=empty.prob, cmap='coolwarm', s=9, vmin=0, vmax=1)#s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
axs[1].set_title(r'satisfaction of $\varphi_{full}$')
axs[1].scatter(stations.station_longitude, stations.station_latitude, c=full.prob, cmap='coolwarm', s=9, vmin=0, vmax=1)#s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
fig.tight_layout()
fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.05, 0.025, 0.9])
fig.colorbar(col, cax=cbar_ax)
fig.savefig('results_graphs/empty_full.svg', ppi=300)

# generate story for phi_prob
fig, axs = plt.subplots(1, 4, figsize=(9,2.5), sharey=True)
for i, ax in enumerate(axs):
        axs[i].set_title('[{0}, {1}]'.format(i * 360, i * 360 + 359))
        axs[i].scatter(stations.station_longitude, stations.station_latitude, c=prob[i].prob, cmap='coolwarm', s=9, vmin=0, vmax=1)#s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
fig.tight_layout()
fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.05, 0.025, 0.9])
fig.colorbar(col, cax=cbar_ax)
fig.savefig('results_graphs/prob_story.svg', ppi=300)
