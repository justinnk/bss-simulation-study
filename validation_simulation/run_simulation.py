#@author: justinnk
# executes a single simulation experiment with the validation model

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

print_header('1/6 Cleansing')
os.system('python3 0-cleanup.py')
print_header('2/6 Analysis')
os.system('python3 1-analyse.py')
print_header('3/6 Parametrization')
os.system('python3 2-parametrize.py')
print_header('4/6 Simulating')
os.system('java -jar CARMA-CL.jar experiment.exp -m {0} -q -seed {1}'.format(settings['nthreads'], settings['simulation_seed']))
print_header('5/6 Output Generation')
os.system('python3 4-generate_results.py')
print_header('6/6 Validation')
os.system('python3 5-validate.py')