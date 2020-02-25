#@author: justinnk
# calculates the mean confidence interval across all measures

import os
import pandas as pd

# returns the 99% confidence interval for simulation results.
# only returns the sddev/sqrt(n) part and thus has to be added/subtracted
# to the mean (e.g. with errorbar)
def get_confidence_interval(sim_results):
    z_star_99 = 2.576 # value of the z-distribution for a 99% confidence interval
    c_i = z_star_99 * sim_results.stderr
    return c_i

def read_csv(path):
	return pd.read_csv(path, delimiter=';', usecols=[0,1,2,3], names=['time', 'value', 'stddev', 'stderr'])

results_dir = [d for d in os.listdir('results') if os.path.isdir(os.path.join('results', d))]
results_dir.sort(reverse=True)
sim_results = [read_csv(os.path.join('results', results_dir[0], file)) for file in os.listdir(os.path.join('results', results_dir[0])) if file.endswith('.csv')]
#sim_names = [name for name in os.listdir(os.path.join('results', results_dir[0])) if name.endswith('.csv')]

max_confs = pd.DataFrame(['max_confidence'])
mean_confs = pd.DataFrame(['mean_confidence'])

for i, r in enumerate(sim_results):
	max_conf = get_confidence_interval(r).max()
	mean_conf = get_confidence_interval(r).mean()
#	max_conf = get_confidence_interval(r).max()
	max_confs = max_confs.append({'max_confidence': max_conf}, ignore_index=True)
	mean_confs = mean_confs.append({'mean_confidence': mean_conf}, ignore_index=True)

print(max_confs.max())
print(mean_confs.mean())
