# real_analysis folder

This folder contains what is needed to evaluate the SSTL formulas on the historical data. A listing of all the files and folders and their function can be found below.

## Contents

- `0-cleanup.py`: used for cleaning the data based on `settings.json`. Very similar to the script used for the simulation.
- `1-generate_traces.py`: this will generate the trajectories for each day in August in the `Traces` folder.
- `2-generate_graph.py`: will generate the graph used for the SSTL evaluation as `model.tra`.
- (`jSSTLEval.jar`): needs to be placed here manually. It is used to evaluate the formulas on the trajectories in `Traces` and will output the results to `Formulas`.
- `4-visualize_formulas.py`: will generate images based on the satisfaction probability of the evaluated formulas.
- `settings.json`: contains the settings/parameters used for an experiment, as used in the simulations. In this case only the parameters that influence cleaning are used.
- `Formulas`: output directory for the satisfaction probabilities.
- `Traces`: output directory for the trajectories.
- `results_graphs`: output directory for the visualisations.
  - `/formulas`: large images for every single parameter configuration.

## Usage

To execute the evaluation, run the scripts in the order of their numbering. Between steps 2 and 4, execute the following command: `java -jar jSSTLEval.jar 21` (where 21 is the number of trajectories, in this case for our data from August). After that, you should find the outputs in the places described above.
