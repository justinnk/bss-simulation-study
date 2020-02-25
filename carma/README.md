# carma folder

This folder contains the java code used for the custom version of the carma cli. The precompiled executable can be found [here]().

## Build from Source

To build the executable from source, import the project as java project into eclipse. Download the [carma cli]() and add the `.jar`-file as an external dependency to the eclipse project. Then, right click the `mycli`-package in the package explorer and select `Export...`. Select `Java > Runnable JAR file` and hit next. Finally select `MyCLIMultithread` as build configuration. Name the outputted file `MyCLI.jar` and choose to `Extract required libraries into generated jar`. You should now have the correct executable to use for `validation_simulation` and `extended_simulation`.

**Note:** should there be no build configuration, just right click on the file `MyCLIMultithread.java` and select `Run As... > Java Application`. This will fail, since there is no model etc., but will create the configuration.

## Usage

The tool will assume that there is a file called `stations.csv` in the same place, which contains all the stations with their capacities. This file is used in deriving the trajectories. To run the tool use:

`java -jar MyCLI.jar <nthreads> <seed> <path>/`

for example:

`java -jar MyCLI.jar 8 42 /`
