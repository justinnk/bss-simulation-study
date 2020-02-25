echo 'Cleaning Data...'
python3 0-cleanup.py
echo 'Analysing Data...'
python3 1-analyse.py
echo 'Parametrizing...'
python3 2-parametrize.py
echo 'Simulating...'
./3-run_experiment.sh
echo 'Producing Results..'
python3 4-generate_results.py
echo 'Validating Results...'
python3 5-validate.py