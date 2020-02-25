#@author: justinnk
# runs all the experiments specified in plan.json

import os
import json

plan = []
with open('plan.json', 'r') as file:
    plan = json.load(file)

for exp in plan:
    name = exp['name']
    output_folder = os.path.join('Planned_Experiments', name)
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)
        os.mkdir(os.path.join(output_folder, 'validation'))
        os.mkdir(os.path.join(output_folder, 'formulas'))
    with open(os.path.join(output_folder, 'settings.json'), 'w+') as file:
        file.write(json.dumps(exp, indent=4))
    with open('settings.json', 'w') as file:
        file.write(json.dumps(exp, indent=4))
    if exp['needs_cleaning']:
        print('starting experiment "{0}", outputting to "{1}"'.format(name, output_folder))
        os.system('python3 run_simulation.py 2>&1 | tee {0}'.format(os.path.join(output_folder, 'out.txt')))
        os.system(' cp -avr Formulas/ {0}/'.format(output_folder))
        print('finished.')
    else:
        print('starting experiment "{0}", outputting to "{1}"'.format(name, output_folder))
        print('omitting cleaning')
        os.system('python3 run_simulation_no_cleaning.py 2>&1 | tee {0}'.format(os.path.join(output_folder, 'out.txt')))
        os.system(' cp -avr Formulas/ {0}/'.format(output_folder))
        print('finished.')
    