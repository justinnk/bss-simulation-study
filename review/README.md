# Detailed Reproduction Instructions

This document contains detailed instructions to reproduce the results shown in the paper. This only contains instructions for reproducing the exact experimental results. For more detailed information on each step, see the separate readmes in the other folders. For the reproduction to work properly, please follow the steps in the order in which they are provided here (top to bottom). When mentioning of folders, they are always relative to the repository root, e.g. `README.md` would mean the file named "README.md" in the root and `review/README.md` means this file.

## Permanent Access

To ensure permanent access to the artifacts (datasets and code), we use [Zenodo](https://zenodo.org/). Also see their plan for permanent accessibility [here](https://about.zenodo.org/principles/). This repository is archived on Zenodo and the newest release can be found under

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3702267.svg)](https://doi.org/10.5281/zenodo.3702267)

The datasets can be found under

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3702258.svg)](https://doi.org/10.5281/zenodo.3702258)

## List of Artifacts

This repository includes all the artifacts needed for reproduction, including:

- the bike sharing data in the `data` folder (due to size restrictions, it must be obtained seperately, as described below)
- the software used in the study, consisting of:
  - the pipeline for analysing the historical data in the `real_analysis` folder
  - the validation model in the `validation_simulation` folder
  - the extended model in the `extended_simulation` folder

A full list of this repositories contents can be found in `README.md`.

## Documentation

The documentation for each artifact can be found in the respective subfolders of the root. A list of those folders and their contents is given in `README.md`.
All artifact-folders contain their own `README.md`, where the contents and their use is described. Additionally, all code is commented and most of it features a description at the top of the file.

## Requirements

### Software Requirements

- linux or unix like operating system
  - may also work on windows, but this is not completely tested. If you need to use windows, please contact your corresponding author.
  - there may especially be problems with the `cp` command used in `extended_simulation` and `review/generate_images` and with the path definitions
- `python 3` or higher, with the following modules installed. Instructions to install python can be found [here](https://www.python.org/)
  - `numpy`
  - `pandas`
  - `matplotlib`
  - NOTE: Depending on your installation of python, you may have to use `python` instead of `python3` to execute the respective commands below. You may also have to change some scripts to use another call. If so, these places are inidcated by a note below.
  - Instead of changing the scripts and calls, you can also define an alias, e.g. `alias python3="python"`. In this case you should not need to change anything
- `java runtime environment` (see [here](https://www.java.com/en/download/) for details)
- java and python must be added to your `PATH` environment variable, e.g. you must be able to execute `java` and `python3` from the command line. This is normally done automatically upon installation.
- all paths are relative within the repository, so there is no need to adjust them

### Hardware Requirements

- to fully reproduce and store all results from the paper:
  - about 10GB of free disk space
  - 8GB RAM
- a multicore CPU is advisable to speed up the simulations, but not required
  - the number of threads used by the simulations can be changed if needed. This can be done in the `settings.json` file in `validation_simulation` (default 16) and in the `plan.json` (default 8) file in `extended_simulation`
- it is advisable to run the simulations on a separate server to not block your own resources, as they may take multiple hours to complete

## Preparation

1. clone this repository to your harddrive using git: `git clone https://github.com/justinnk/bss-simulation-study`
(if you don't have git, you can also download it as `.zip`-archive from the above link or via it's DOI)
2. remove the `.gitignore` files in the following folders: `extended_simulation/Formulas`, `extended_simulation/Traces`, `extended_simulation/Results`, `real_analysis/Traces`, `real_analysis/Formulas` and `validation_simulation/results`. In most file explorers you have to activate the option "show hidden files" in order to see those.
3. download the two datasets from [here](https://doi.org/10.5281/zenodo.3702259) and place the two `csv` files together with the license in the `data` folder.
4. Navigate to the `notebooks` folder and execute the commands `python3 extract_stations.py` and `python3 extrapolate_demand.py`. This should generate two new datasets named `trips_08-2019_latent_demand.csv` and `stations_aug.csv` in the `data` folder

## Section 3 (Figures 2, 3 and 4)

To reprodue the figures in section 3, navigate to the folder `real_analysis`. Run the following commands in that folder in this order:

1. `python3 0-cleanup.py`
2. `python3 1-generate_traces.py`
3. `python3 2-generate_graph.py`
4. `java -jar jSSTLEval.jar 21`
5. `python3 4-visualize_formulas.py`

You should now be able to find the figures as `.svg` files in the folder `real_analysis/results_graphs`. `empty_full.svg` is used for **Figure 2**, `dist_time_story.svg` is used for **Figure 3** and `prob_story.svg` is used for **Figure 4**. The map in the background was added manually using [Inkscape](https://inkscape.org/) and can be found in `review/generate_images/map.svg`.

## Section 4.1 (Figure 6 and Table 1)

To reproduce the figures and tables in Section 4.1, navigate to the folder `validation_simulation`. If you want to modify the number of threads used, do so by modifying the value of `nthreads` in `settings.json`. Run the following command to execute the simulation: `python3 run_simulation.py`. This takes about 15min on a 6 core/12 thread processor. NOTE: If no output is produced, you may need to change "python3" in the commands found in `validation_simulation/run_simulation.py` to "python" or the call you use to execute the python interpreter. Once the simulation is finished, the processed output can be found in the `validation_simulation/results_graphs` folder and its children. For the paper, these were processed a bit further.
To get the exact images shown in **Figure 6**, navigate to the folder `review/generate_images`. Run the following command `python3 copy_validation_data.py`. This script assumes, that there is only one folder in `validation_simulation/results`, the one the simulation just created. Please make sure, that this is the case. It will copy the required results to the folder `review/generate_images/validation`, where you can execute `python3 combine.py`, which will produce the `.svg` files used in Figure 6.
To get the values for **Table 1**, navigate to `review/generate_tables` and execute `python3 generate_1.py`. You can then find it as `table1.txt`. For the formatting to work, you may want to increase the width of the window when opening. Note, that the order of the columns and rows is changed because of technical reasons.

## Section 5 (Figures 7, 8 and 9 and Table 2)

Reproducing the results for this Section is very similar to the previous approach. First, navigate to the folder `extended_simulation`. If you want to change the number of threads used, change it for every entry in `plan.json`. **Important:** the number of threads must be a divisor of the number of replications (in this case 1000). Changing it may also impact the way which seed is chosen for which thread, but the overall results should still stay the same (however, this is not tested, so it is best to leave it at 8).
Run the following command to start the execution of all experiments used in the paper: `python3 run_planned.py`. NOTE: you may need to change the python calls in the scripts `extended_simulation/run_planned.py`, `extended_simulation/run_simulation.py` and `extended_simulation/run_simulation_no_cleaning.py` if you didn't define an alias and use another call. Be aware that, depending on the used hardware, this may take a couple of hours. It will generate about 4.8GB of trajectories in the `extended_simulation/Traces` folder. Additionally, some space for the processed simulation outcomes is requred.
Once finished, the results should be in their corresponding folders in `extended_simulation/Planned_Experiments`. Again, the images used in the paper combine these to save space. To get the exact images used, do the following.
Navigate to `review/generate_images`. Execute the command `python3 copy_extended_data.py`. This should take care of copying all the simulation outcomes to the right folders. After this, the images can be generated as follows

- for **Figure 7**, navigate to `review/generate_images/baseline_comparison` and execute `python3 combine.py`
- for **Figure 8**, navigate to `review/generate_images/baseline_epmty_full` and execute `python3 combine.py`
- for **Figure 9**, navigate to `review/generate_images/prob_comparison` and execute `python3 combine.py`

As already stated before, the map in the background was added manually.
To get the results for **Table 2**, navigate to `review/generate_table` and execute `python3 generate_2.py`. The table should be generated in a text file called `table2.txt`. For the formatting to work, you may want to increase the width of the window when opening. Note that the order in which the strategies appear differs from the one used in the paper, but the numbers should be the same. The only exception, as mentioned in Section 5 of the paper, is the redistribution effort for the strategies "static" and "static + inc".
