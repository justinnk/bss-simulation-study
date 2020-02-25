# sstl folder

This folder contains the code used for evaluating sstl formulas on model and historical trajectories. The classes are part of a maven project `bss-sstl`, which can be opened in eclipse as such. In order to compile them, first install [jsstl](https://github.com/Quanticol/jsstl). The endproduct should be two exeutable `.jar`s: `jSSTLEval.jar` and `jSSTLEvalMulti.jar`, which can then be used in the simulations or historical data analysis. Additionally, the precompiled `.jar`s are available [here](). 

## Instructions for Building from Source

First, clone the repository of [jsstl](https://github.com/Quanticol/jsstl) to this folder.

`git clone https://github.com/Quanticol/jsstl.git`

You should now have two folders beside this readme: `bss-sstl` and `jsstl`. Next build the jsstl maven project:

`cd jsstl`
`mvn clean verify`

Now install jsstl into your local maven repository:

`mvn install`

Next, import the folder `bss-sstl` in eclipse as a maven project. In the package explorer navigate to `bss_study.singleday` and right-click on the entry. Seclect `Export...` and then `Java > Runnable Jar file`. Click Next. Under `Run Configureation` select `EvaluateBSS` and choose to `Extract required libraries into generated jar`. Select an export destination and name the file `jSSTLEval.jar`.
Repeat this for the package `bss_study.multiday`, but select `EvaluateBSSMulti` as run configuration and name the file `jSSTLEvalMulti.jar`.
Those runnable jar files can now be used for the other parts of this study.

## Usage

The tool assumes, that there is a folder `Traces`, which contains the trajectories and a folder `Formulas`, where the results are written into. The trajectories need to have the following fields (in that order):

- `timestamp`: integer representing time
- `location`: location, represented as integer. The number must correspond to the graph.
- `bikes`: number of available bikes as double
- `slots`: number of available slots as double

It is also assumed, that the graph can be found in the file `model.tra`. This file is in the following format:


```plaintext
LOCATIONS
0
1
2
3
...
n
EDGES
0 1 w[1]
0 2 w[2]
...
```

where n is the number of locations and w[1] ... w[n*n] are the weights of the edges. There is no need for the graph to be fully connected. The tool takes in the number of trajectories as parameter:

`java jSSTLEval.jar <n_traj>`

If needed, all this can be changed and altered in the sourcecode, depending on the usecase.
