# @author justinnk
# Visualizes the outcomes of the simulation
# 
# users.png
#   number of users simultaneously using the system 
#   (note: this is not comparable to number of trips, although it has a similar shape!)
# trips.png
#   cumulative number of trips
# stations_status.png
#   number of empty/full stations
# stations_available.png
#   min, max and avg filling percentage of the stations
# error_measures.png
#   users at the error station that is used for verification

import matplotlib.pyplot as plt
import csv
import os

# iteration variables
x = []
y = []
stddev = []
stderr = []

# figures
fig, ax = plt.subplots()
fig.set_size_inches(12, 8)
fig.tight_layout()

fig2, ax2 = plt.subplots()
fig2.set_size_inches(12, 8)
fig2.tight_layout()

fig3, ax3 = plt.subplots()
fig3.set_size_inches(12, 8)
fig3.tight_layout()

fig4, ax4 = plt.subplots()
fig4.set_size_inches(12, 8)
fig4.tight_layout()

fig5, ax5 = plt.subplots()
fig5.set_size_inches(12, 8)
fig5.tight_layout()

# load latest result from results directory and extract data
results = [d for d in os.listdir('results') if os.path.isdir(os.path.join('results', d))]
results.sort(reverse=True)

for file in os.listdir(os.path.join('results', results[0])):
    if file.endswith('.csv'):
        if file.startswith('Biking') or file.startswith('GlobalUsers') or file.startswith('Returning') or file.startswith('Waiting'):
            with open(os.path.join('results', results[0], file),'r') as csvfile:
                plots = csv.reader(csvfile, delimiter=';')
                for row in plots:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    stddev.append(float(row[2]))
                    stderr.append(float(row[3]))
                ax2.errorbar(x, y, stddev, label=file + ' (stddev)', color='#d1e3ff', alpha=0.5)
                ax2.errorbar(x, y, stderr, label=file + '(stderr)')
                ax2.legend()
                ax2.set_yticks(range(0, 20), minor=True)
                ax2.set_xticks(range(0, 1440, 60), minor=False)
                ax2.grid(which='major', linestyle='--')
                ax2.grid(which='minor', linestyle='--')
        elif file.startswith('FullStations') or file.startswith('StarvedStations'):
            with open(os.path.join('results', results[0], file),'r') as csvfile:
                plots = csv.reader(csvfile, delimiter=';')
                for row in plots:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    stddev.append(float(row[2]))
                    stderr.append(float(row[3]))
                ax4.errorbar(x, y, stddev, label=file + ' (stddev)', color='#d1e3ff', alpha=0.5)
                ax4.errorbar(x, y, stderr, label=file + ' (stderr)')
                ax4.legend()
        elif file.startswith('Error'):
            with open(os.path.join('results', results[0], file),'r') as csvfile:
                plots = csv.reader(csvfile, delimiter=';')
                for row in plots:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    stddev.append(float(row[2]))
                    stderr.append(float(row[3]))
                ax5.errorbar(x, y, stderr, label=file)
                ax5.legend()
                ax5.set_yticks(range(0, 10), minor=True)
                ax5.set_xticks(range(0, 1440, 60), minor=False)
                ax5.grid(which='major', linestyle='--')
                ax5.grid(which='minor', linestyle='--')
        elif file.startswith('Max') or file.startswith('Min') or file.startswith('Avg'):
            with open(os.path.join('results', results[0], file),'r') as csvfile:
                plots = csv.reader(csvfile, delimiter=';')
                for row in plots:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    stddev.append(float(row[2]))
                    stderr.append(float(row[3]))
                ax3.errorbar(x, y, stddev, label=file + ' (stddev)', color='#d1e3ff', alpha=0.5)
                ax3.errorbar(x, y, stderr, label=file + ' (stderr)')
                ax3.legend()
        elif file.startswith('Returns') or file.startswith('Retrievals'):
            with open(os.path.join('results', results[0], file),'r') as csvfile:
                plots = csv.reader(csvfile, delimiter=';')
                for row in plots:
                    x.append(float(row[0]))
                    y.append(float(row[1]))
                    stddev.append(float(row[2]))
                    stderr.append(float(row[3]))
                ax.errorbar(x, y, stddev, label=file + ' (stddev)', color='#d1e3ff', alpha=0.5)
                ax.errorbar(x, y, stderr, label=file + ' (stderr)')
                ax.legend()
                ax.set_yticks(range(0, 500, 20), minor=True)
                ax.set_xticks(range(0, 1440, 60), minor=False)
                ax.grid(which='major', linestyle='--')
                ax.grid(which='minor', linestyle='--')
    x = []
    y = []
    stddev = []
    stderr = []

# save the figures
fig.savefig('results_graphs/trips.png', dpi=100)
fig2.savefig('results_graphs/users.png', dpi=100)
fig3.savefig('results_graphs/stations_available.png', dpi=100)
fig4.savefig('results_graphs/stations_status.png', dpi=100)
fig5.savefig('results_graphs/error_measures.png', dpi=100)
