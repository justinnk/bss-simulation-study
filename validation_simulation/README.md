# validation_simulation folder

This folder contains everything necessary to validate the simple model.

## Contents

- `0-cleanup.py`: used for cleaning the datasets.
- `1-analyse.py`: produces some interesting visualizations of the cleaned data. Old and not of any use for the paper.
- `2-parametrize.py`: inserts the parameters into the model `model.carma` and generates an experiment file `experiment.exp`.
- `4-generate_results.py`: produces visualizations and data of the outcomes of the simulation.
- `3-run_experiment.sh`: will execute the CARMA CLI with the proper parameters.
- `5-validate.py`: produces visualizations and data that can be used to validate the model (in this case only the number of available bikes over time is meaningful. A seperate pipeline/model is used for validation.)
- `get_conficence_intervals.py`: used in the paper to calculate the mean confidence across all measures.
- `settings.json`: stores all the information about parameters and how to clean the data for this validation experiment.
- `model.carma`: the code for the CARMA model of the BSS.
- (`CARMA-CL.jar`): Can be downloaded from [here](http://quanticol.github.io/CARMA/cli.html) and needs to be placed here manually. Runs the CARMA simulator with the given model `model.carma` and the experiment `experiment.exp`. The results are stored in the `results` folder.
- `run_simulation.py`: takes care of running the scripts in the correct order and automates the whole process of cleaning, parameterisation, simulation and outcome processing.
- `results`: will host the simulation outcomes
- `results_graphs`: the processed outcomes of the simulation are stored here

## Usage

To reproduce the results from the paper, simply run `python3 run_simulation.py`. After the simulation finished, the processed outputs should be visible in the `results_graphs` folder.
