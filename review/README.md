# Detailed Reproduction Instructions

This document contains detailed instructions to reproduce the results shown in the paper. For more detailed information on each step, see the separate readmes in the other folders. For the reproduction to work properly, please follow the steps in the order in which they are provided here (top to bottom).

## Requirements

### Software Requirements

- linux operating system
  - may also work on windows, but this is not tested
  - there may especially be problems with the `cp` command used in `extended_simulation` and `review/generate_images` and with the path definitions
- `python 3` or higher, with the folliwing modules installed
  - `numpy`
  - `pandas`
  - `matplotlib`
- `java runtime environment`
- all paths are relative within the repository, so there is no need to adjust them

### Hardware Requirements

- about 10GB of free disk space
- 8GB RAM
- a multicore CPU is advisable to speed up the simulations, but not required
  - the number of threads used by the simulations can be changed if needed. This can be done in the `settings.json` file in `validation_simulation` (default 16) and in the `plan.json` (default 8) file in `extended_simulation`
- it is advisable to run the simulations on a separate server to not block your own resources, as they may take multiple hours to complete

## Preparation

1. clone this repository to your harddrive using git: `git clone https://github.com/justinnk/bss-simulation-study`
(if you don't have git, you can also download it as `.zip`-archive from the above link)
2. remove the `.gitignore` files in the following folders: `extended_simulation/Formulas`, `extended_simulation/Traces`, `extended_simulation/Results`, `real_analysis/Traces`, `real_analysis/Formulas` and `validation_simulation/results`. In most file explorers you have to activate the option "show hidden files" in order to see those.
3. todo: data
4. Navigate to the `notebooks` folder and execute the commands `python3 extract_stations.py` and `python3 extrapolate_demand.py`. This should generate two new datasets named `trips_08-2019_latent_demand.csv` and `stations_aug.csv` in the `data` folder

## Section 3 (Figures 2, 3 and 4)

To reprodue the figures in section 3, navigate to the folder `real_analysis`. Run the following commands in that folder in this order:

1. `python3 0-cleanup.py`
2. `python3 1-generate_traces.py`
3. `python3 2-generate_graph.py`
4. `java -jar jSSTLEval.jar 21`
5. `python3 4-visualize_formulas.py`

You should now be able to find the figures as `.svg` files in the folder `real_analysis/results_graphs`. `empty_full.svg` is used for **Figure 2**, `dist_time_story.svg` is used for **Figure 3** and `prob_story.svg` is used for **Figure 4**. The map in the background was added manually using [Inkscape(todo)]() and can be found in `review/generate_images/map.svg`.

## Section 4.1 (Figure 6 and Table 1)

To reproduce the figures and tables in Section 4.1, navigate to the folder `validation_simulation`. If you want to modify the number of threads used, do so by modifying the value of `nthreads` in `settings.json`. Run the following command to execute the simulation: `python3 run_simulation.py`. Once the simulation is finished, the processed output can be found in the `validation_simulation/results_graphs` folder and its children. For the paper, these were processed a bit further.
To get the exact images shown in **Figure 6**, navigate to the folder `review/generate_images`. Run the following command `python3 copy_validation_data.py`. This script assumes, that there is only one folder in `validation_simulation/results`, e.g. the one the simulation just created. Please make sure, that this is the case. It will copy the required results to the folder `review/generate_images/validation`, where you can execute `python3 combine.py`, which will produce the `.svg` files used in Figure 6.
To get the values for **Table 1**, navigate to `review/generate_tables` and execute `python3 generate_1.py`. You can then find it as `table1.txt`. For the formatting to work, you may want to increase the width of the window when opening. Note, that the order of the columns and rows is changed because of technical reasons.

## Section 5 (Figures 7, 8 and 9 and Table 2)

Reproducing the results for this Section is very similar to the previous approach. Fist, navigate to the folder `extended_simulation`. If you want to change the number of threads used, change it for every entry in `plan.json`. **Important:** the number of threads must be a divisor of the number of replications (in this case 1000). Changing it may also impact the way which seed is chosen for which thread, but the overall results should still stay the same (however, this is not tested, so it is best to leave it at 8).
Run the following command to start the execution of all experiments used in the paper: `python3 run_planned.py`. Be aware that, depending on the used hardware, this may take a couple of hours. It will generate about 4.8GB of trajectories in the `extended_simulation/Traces` folder. Additionally, some space for the processed simulation outcomes is requred.
Once finished, the results should be in their corresponding folders in `extended_simulation/Planned_Experiments`. Again, the images used in the paper combine these to save space. To get the exact images used, do the following.
Navigate to `review/generate_images`. Execute the command `python3 copy_extended_data.py`. This should take care of copying all the simulation outcomes to the right folders. After this, the images can be generated as follows

- for **Figure 7**, navigate to `review/generate_images/baseline_comparison` and execute `python3 combine.py`
- for **Figure 8**, navigate to `review/generate_images/baseline_epmty_full` and execute `python3 combine.py`
- for **Figure 9**, navigate to `review/generate_images/prob_comparison` and execute `python3 combine.py`

As already stated before, the map in the background was added manually.
To get the results for **Table 2**, navigate to `review/generate_table` and execute `python3 generate_2.py`. The table should be generated in a text file called `table2.txt`. For the formatting to work, you may want to increase the width of the window when opening. Note that the order in which the strategies appear differs from the one used in the paper, but the numbers should be the same. The only exception, as mentioned in Section 5 of the paper, is the redistribution effort for the strategies "static" and "static + inc".
