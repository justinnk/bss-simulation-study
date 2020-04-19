#@author: justinnk
# runs a single experiment, specified in settings.json

import os
import json

def print_line():
    print('-' * 10)
    print('\n')

def print_header(header):
    print_line()
    print(header)
    print('\n')
    print_line()

# load settings from file
settings = {}
with open('settings.json', 'r') as file:
    settings = json.loads(file.read())

print_header('1/10 Cleansing')
os.system('python3 0-cleanup.py')
print_header('2/10 Analysis')
os.system('python3 1-analyse.py')
print_header('3/10 Station Optimals Calculation')
os.system('python3 2-calc_optimals.py')
print_header('4/10 Parametrization')
os.system('python3 3-parametrize.py')
print_header('5/10 Simulating')
os.system('java -Duser.country=UK -Duser.language=en -Xmx7G -jar MyCLI.jar {0} {1} /'.format(settings['nthreads'], settings['simulation_seed']))
print_header('6/10 Output Generation')
os.system('python3 5-generate_results.py')
print_header('7/10 Validation')
os.system('python3 6-validate.py')
print_header('8/10 jSSTL Graph Generation')
os.system('python3 7-generate_graph.py')
print_header('9/10 jSSTL Evaluation')
os.system('java -Duser.country=UK -Duser.language=en -jar jSSTLEvalMulti.jar {0}'.format(settings['replications']))
print_header('10/10 jSSTL Visualization')
os.system('python3 9-visualize_formulas.py')
