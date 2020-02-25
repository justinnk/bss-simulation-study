# @author justinnk
# Visualizes the outcomes of the evaluation with SSTL.

import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# load settings from file
settings = {}
with open('settings.json', 'r') as file:
    settings = json.loads(file.read())

# output dir
output_dir = settings['output_dir']

stations = pd.read_csv('stations.csv')

results_dir = 'Formulas'

results = os.listdir(results_dir)

dist_pics = []
dist_selection = [1, 6, 10]
time_pics = []
time_selection = [1, 5, 10]
empty = []
full = []
prob = []

for r in results:
    data = pd.read_csv(os.path.join(results_dir, r), names=['par', 'loc', 'prob', 'min', 'max', 'stddev'])
    for p in data.par.drop_duplicates():
        print('generating image for {0}_{1}'.format(r[:-4], p))
        plt.figure(figsize=(10,8))
        plt.title('formula {0}, parameter configuration {1}'.format(r[:-4], p))
        plt.scatter(stations.station_longitude, stations.station_latitude, c=data[data.par == p].prob, s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
        plt.colorbar()
        plt.savefig(output_dir + '/formulas/{0}_{1}'.format(r[:-4], p))
        plt.close()
        if r[:-4] == 'phi_dist':
              if p in dist_selection:
                   dist_pics.append(data[data.par == p])
        elif r[:-4] == 'phi_time':
              if p in time_selection:
                   time_pics.append(data[data.par == p])
        elif r[:-4] == 'phi_empty':
              empty.append(data[data.par == p])
        elif r[:-4] == 'phi_full':
              full.append(data[data.par == p])
        elif r[:-4] == 'phi_prob':
              prob.append(data[data.par == p])

# generate story for phi_dist and phi_time
fig, axs = plt.subplots(2, 3, figsize=(12, 8), sharey=True)
for i, ax in enumerate(axs[0]):
        ax.set_title('phi_dist for d={0}m'.format(dist_selection[i] * 50))
        col = ax.scatter(stations.station_longitude, stations.station_latitude, c=dist_pics[i].prob, s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
for i, ax in enumerate(axs[1]):
        ax.set_title('phi_time for t={0}min'.format(time_selection[i]))
        col = ax.scatter(stations.station_longitude, stations.station_latitude, c=time_pics[i].prob, s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
fig.tight_layout()
fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.05, 0.025, 0.9])
fig.colorbar(col, cax=cbar_ax)
fig.savefig(output_dir + '/formulas/dist_time_story.png', ppi=300)

# generate joint image for phi_empty and phi_full
fig, axs = plt.subplots(2, 3, figsize=(12,6), sharey=True)
for i, ax in enumerate(axs[0]):
      ax.set_title('satisfaction of phi_empty day {0}'.format(i))
      ax.scatter(stations.station_longitude, stations.station_latitude, c=empty[i].prob, s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
for i, ax in enumerate(axs[1]):
      ax.set_title('satisfaction of phi_full day {0}'.format(i))
      ax.scatter(stations.station_longitude, stations.station_latitude, c=full[i].prob, s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
fig.tight_layout()
fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.05, 0.025, 0.9])
fig.colorbar(col, cax=cbar_ax)
fig.savefig(output_dir + '/formulas/empty_full.png', ppi=300)

# generate story for phi_prob
fig, axs = plt.subplots(3, 4, figsize=(12,6), sharey=True)
for x in range(0, 3):
      for i, ax in enumerate(axs[x]):
            ax.set_title('phi_prob in [{0}, {1}]'.format((x * 3 + x + i) * 360, (x * 3 + x + i) * 360 + 359))
            ax.scatter(stations.station_longitude, stations.station_latitude, c=prob[x * 3 + i].prob, s=stations.station_capacity, cmap='coolwarm', vmin=0, vmax=1)
fig.tight_layout()
fig.subplots_adjust(right=0.9)
cbar_ax = fig.add_axes([0.92, 0.05, 0.025, 0.9])
fig.colorbar(col, cax=cbar_ax)
fig.savefig(output_dir + '/formulas/prob_story.png', ppi=300)