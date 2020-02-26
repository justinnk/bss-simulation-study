import os

path = '../../validation_simulation/results_graphs/validation/error.txt'
errors = ''
table = 'dataset    | max. MSE  | min. MSE. | mean MSE  | median MSE\n'

with open(path, 'r') as file:
    errors = file.read()

errors = errors.split('---------------')
validation_error = errors[2].split('\n')[-5:-1]
table += 'validation | '
for e in validation_error:
    table += '{0}     | '.format(round(float(e.split(':')[1]), 3))

training_error = errors[4].split('\n')[-5:-1]
table += '\ntraining   | '
for e in training_error:
    table += '{0}     | '.format(round(float(e.split(':')[1]), 3))

with open('table1.txt', 'w+') as file:
    file.write(table)