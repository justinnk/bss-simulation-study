[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3702267.svg)](https://doi.org/10.5281/zenodo.3702267)

[![License: CC BY-SA 4.0](https://i.creativecommons.org/l/by-sa/4.0/80x15.png)](http://creativecommons.org/licenses/by-sa/4.0/)

# bss-simulation-study

This repository contains the accompanying code and documentation for the paper "Probing the Performance of the Edinburgh Bike Sharing System using SSTL".

**Note:** Some folders contain a `.gitignore` file to keep them in the version control despite being empty. Some scripts may fail if that file is present, so it is safest to delete all the gitignore files in the "empty" folders. Those generally include the folders named: `Formulas`, `Traces` and `Results`.

**Note:** Depending on your installation of python, you may have to use python instead of python3 to execute the respective commands below. You may also have to change some scripts to use another call.
Instead of changing the scripts and calls, you can also define an alias, e.g. alias python3="python". In this case you should not need to change anything

## Reproducability Initiative / Artifact Evaluation

You can find the requested single readme with a detailed explaination and scripts to reproduce the tables and figures in the folder called `review`.

## Software Requirements

**Required:** `python3` with `matplotlib`, `numpy`, `pandas`; `java runtime environment`
**Optional:** `jupyter notebook` (to run the notebooks, but they are also included as plain python scripts), `eclipse`, `maven` and the `m2e` plugin for eclipse (to build the simulator and sstl evaluator from source, but precompiled versions are also included in the respective foldersE)

## Hardware Requirements

The simulation should run on any hardware that supports the dependencies listed above. However, to achieve the best performance, a multicore CPU is preferrable. Also, in order to perform 1000 replications while recording Traces for the simulation over three days, a minumum of 7GB of RAM is required. This can be overwritten in `run_simulation.py` and `run_simulation_no_cleaning.py`. Keep in mind that, depending on the desired number of replications, the simulator will fail with an `OutOfMemoryError`. In order to store 1000 trajectories and the outputs of a couple of experiments, about 10GB of disk space is required.

## Contents and Usage

The below table gives an overview over the different top-level directories, their contents and the Section in the paper they are (first) used in. Each of them also contains its own readme file, which gives a more detailed explaination. Usually all the code files also contain a comment at the top that briefly explains their purpose and usage. All the paths, that refer to the data, are relative, so that there should be no problems as long as the structure of the repository is unchanged.

| Folder | Contents | Section in the Paper |
|-------:|:---------|:--------------------:|
| `review` | Instructions for reproduction for reviewing the artifacts. | - |
| `data`   | The datasets used for this study. Because of the size they must be downloaded seperately from [here](https://doi.org/10.5281/zenodo.3702259). Place the two csv files and license in the data folder. Please note the license provided with them: they must only be used to reproduce this study and aid in understanding it. | 2.1 |
| `notebooks` | A number of jupyter notebooks that are used to transform the datasets to ones that can be used by the simulation (e.g. generating a list of stations, extrapolating demand). | 4/5 |
| `sstl` | The java code that defines the formulas and evaluates them. There are two versions: the first one is used for the historical data and the second one is used for the extended model (where there are 3 days per trajectory instead of one). | 3 |
| `carma` | A modified version of the [CARMA CLI](http://quanticol.github.io/CARMA/cli.html) that supports generating Traces for SSTL. | 4.2 |
| `real_analysis` | The code used for the sstl model checking with the historical data. | 3 |
| `validation_simulator` | The code used for validating the simple model. | 4.1 |
| `extended_simulator` | The code used for executing experiments with the extended model and also model checking the simulation outcomes with sstl. | 5 |
