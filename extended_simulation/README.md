# extended_simulation folder

## Contents

This folder contains the code used to execute the experiments in the paper. The following files and folders can be found:

- `0-cleanup.py`: used for cleaning the datasets.
- `1-analyse.py`: produces some interesting visualizations of the cleaned data.
- `2-calc_optimals.py`: calculates optimal bike allocation at the beginning of the day using a simple hill climbing algorithm.
- `3-parametrize.py`: inserts the parameters into the model `model.carma` and generates an experiment file `experiment.exp`.
- `MyCLI.jar`: runs the CARMA simulator with the given model `model.carma` and the experiment - `experiment.exp`. Traces are stored in the `Traces/` and overall results are store in the `Results/` folder.
- `5-generate_results.py`: produces visualizations and data of the outcomes of the simulation.
- `6-validate.py`: produces visualizations and data that can be used to validate the model (in this case only the number of available bikes over time is meaningful. A seperate pipeline/model is used for validation.)
- `7-generate_graph.py`: generates the graph `model.tra` that can be used for the evaluation with SSTL.
- `jSSTLEvalMulti.jar`: evaluates the sstl formulas on the trajectories from `Traces` and puts the results in `Formulas`.
- `9-visualize_formulas.py`: produces visualisations of the SSTL evaluation outcomes.
- `settings.json`: stores settings for the current experiment
- `settings.json.txt`: same as `settings.json`, but with an explaination of all the parameters
- `plan.json`: stores the description of multiple experiments to execute them automatically
- `model.carma`: code for the extended CARMA model
- `run_simulation.py` and `run_simulation_no_cleaning.py`: python scripts to run the experiment specified in `settings.json` with and without the cleaning phase.
- `run_planned.py`: python script to run all the experiments specified in `plan.json`. Will automatically execute them one after another and place the results in `Planned_Experiments` (the output directories can be altered by changing the parameters in `plan.json`)
- `Traces`: this is where all the resulting trajectories are stored
- `Results`: this is where the accumulated results for the measures are stored
- `Formulas`: this is where all the formula satisfaction probabilities are stored
- `Planned_Experiments`: this is where the results of planned experiments are stored when using the provided plans.
- `results_graphs`: output directory for the processed simulation outcomes (only in case of a single experiment)

The java-executables can be compiled from source (see folders `carma` and `sstl`) or retrieved from [TODO]().
There are two ways to execute experiments:

## Usage

### Single Experiment

`run_simulation.py` will execute the whole pipeline with the experiment specification defined in `setting.json`. An explaination of the different parameters can be found in `settings.json.txt`. Note that the `output_dir`-option should be set to `results_graphs` for single experiments.
`run_simulation_no_cleaning.py` will do the same, but omit `0-cleaning.py`, `1-analyse.py` and `2-calc_optimals.py`. This is only used as an optimisation when running multiple planned experiments one after another since most of the time they can use the same cleaned data.

### Multiple Experiments

`run_planned.py` will run all the experiments specified in `plan.json`. The outputs are stored in the `Planned_Experiments/` folder. This script essentially views this folder as a state machine: at the beginning, the settings for the current experiment are copied to `settings.json` and the simulation outcomes are stored in their usual folders. In the end, the output during processing is redirected to the folder specified in the settings and the formula satisfactions are copied there. The traces and accumulated outcomes get discarded (This could easily be changed by modifying the script slighltly).

## Reproduction

To reproduce the results shown in the paper, use (copy to `plan.json`) the experiment-plan specified in `plan_reproduction.json` and run the pipeline by using `python3 run_planned.py`.
