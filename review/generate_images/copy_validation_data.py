import os


results_folders = [ d for d in os.listdir('../../validation_simulation/results/') if d.startswith('test_exp')]
results_folders.sort(reverse=True)
results_folder = results_folders[0]

timestamp = results_folder[8:]

os.system('cp ../../validation_simulation/results/{0}/Retrievals{1}.csv validation/retrievals.csv'.format(results_folder, timestamp))
os.system('cp ../../validation_simulation/results/{0}/Available[sid=2]{1}.csv validation/available_bruntsfield_links.csv'.format(results_folder, timestamp))
os.system('cp ../../validation_simulation/results/{0}/Available[sid=18]{1}.csv validation/available_dundee_terrace.csv'.format(results_folder, timestamp))