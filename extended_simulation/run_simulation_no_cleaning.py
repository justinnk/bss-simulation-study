#@author: justinnk
# runs a single experiment, specified in settings.json, but omits the data cleaning phase

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

#print_header('1/9 Cleansing')
#os.system('python3 0-cleanup.py')
#print_header('2/9 Analysis')
#os.system('python3 1-analyse.py')
#print_header('3/9 Analysis')
#os.system('python3 2-calc_optimals.py')
print_header('3/9 Parametrization')
os.system('python3 3-parametrize.py')
print_header('4/9 Simulating')
os.system('java -Xmx7G -jar MyCLI.jar {0} {1} /'.format(settings['nthreads'], settings['simulation_seed']))
print_header('5/9 Output Generation')
os.system('python3 5-generate_results.py')
print_header('6/9 Validation')
os.system('python3 6-validate.py')
print_header('7/9 jSSTL Graph Generation')
os.system('python3 7-generate_graph.py')
print_header('8/9 jSSTL Evaluation')
os.system('java -jar jSSTLEvalMulti.jar {0}'.format(settings['replications']))
print_header('9/9 jSSTL Visualization')
os.system('python3 9-visualize_formulas.py')
