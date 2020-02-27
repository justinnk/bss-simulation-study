import os

path = '../../extended_simulation/Planned_Experiments/'

results = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

table = ''

table += 'strategy                       | redist       | incentives                   | trips     | dissatisfaction \n'
table += '                               | 1  |  2 |  3 | get       | ret       | sum  | trips     | mean  | max  \n'
for r in results:
    outcomes = ''
    with open(os.path.join(path, r, 'simulation_stats.txt'), 'r') as file:
        outcomes = file.read()
    outcomes = outcomes.split('\n')
    wanted_lines = [0, 1, 2, 5, 9]
    outcomes = [outcomes[i] for i in wanted_lines]
    trips = int(round(float(outcomes[0][26:].split('+-')[0].rjust(10)), 0))
    inc_get = int(round(float(outcomes[1][26:].split('+-')[0].rjust(10)), 0))
    inc_ret = int(round(float(outcomes[2][26:].split('+-')[0].rjust(10)), 0))
    trips_pm = round(float(outcomes[0][26:].split('+-')[1].rjust(10)), 1)
    inc_get_pm = round(float(outcomes[1][26:].split('+-')[1].rjust(10)), 1)
    inc_ret_pm = round(float(outcomes[2][26:].split('+-')[1].rjust(10)), 1)
    dis_max = outcomes[3].split('/')[0]
    dis_mean = outcomes[3].split('/')[1]
    redist = outcomes[4].strip('][').split(', ')
    redist = list(map(float, redist))
    redist = [int(round(red, 0)) for red in redist]

    table += '{0} | {1:2} | {2:2} | {3:2} | {4:4}+-{10:3} | {5:4}+-{11:3} | {6:4} | {7:4}+-{12:3} | {8:5} | {9:5}\n'.\
     format(r.rjust(30), redist[0], redist[1], redist[2], inc_get, inc_ret, round(inc_get + inc_ret, 0), trips, dis_mean, dis_max, inc_get_pm, inc_ret_pm, trips_pm)

with open('table2.txt', 'w+') as file:
    file.write(table)