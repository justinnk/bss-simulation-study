/**
 * Modified version of the CARMA CLI to support
 * multithreaded single trace generation. This part
 * handles reading the command line parameters and
 * the experiment file.
 * 
 * usage: MyCLIMutlithread <nthreads> <seed> <path>/
 * 
 * nthreads must be divisor of number of replications
 * specified in the experiments file.
 * 
 */

package mycli;

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ExecutionException;

import eu.quanticol.carma.core.ModelLoader;
import eu.quanticol.carma.core.ui.data.MeasureData;
import eu.quanticol.carma.simulator.CarmaModel;

public class MyCLIMultithread {

	public static void main(String[] args) throws IOException, InterruptedException, ExecutionException {
		if (args.length > 2) {
			if (args[2].equals("/")) {
				args[2] = "";
			}
			MyCARMASimulatorMultithread sim = readExperiment(args[2] + "experiment.exp");
			try {
				sim.Run(Integer.parseInt(args[0]), Integer.parseInt(args[1]), args[2]);
			} catch(NumberFormatException e) {
				printUsage();
			}
		} else {
			printUsage();
		}
	}
	
	private static void printUsage() {
		System.out.println("usage: MyCLIMultithread <nthreads> <seed> <path>/");
	}
	
	/* Read experiment file */
	public static MyCARMASimulatorMultithread readExperiment(String filename) throws IOException {
		BufferedReader reader;
		try {
			reader = new BufferedReader(new FileReader(filename));
		}
		catch (Exception e) {
			System.out.println("Error when reading experiments file (details below). Exiting.");
			System.out.println("Error encountered:");
			e.printStackTrace();
			return null;
		}
		String name;
		// disregard any empty lines between the previous experiment and this, also ensuring
		// that there is still an experiment description left (ie we are not at EOF)
		do {
			name = reader.readLine();
		} while (name.isEmpty());
		String modelName = reader.readLine();
		CarmaModel model = getCARMAModel(modelName);
		if (model == null) {
			System.out.println("Could not read model from " + modelName + ".");
			// continue reading until you find blank line or EOF (disregard experiment)
			String line;
			do {
				line = reader.readLine();
			} while (line != null && !line.isEmpty());
			reader.close();
			return null;
		}
		String system = reader.readLine();
		int reps = Integer.parseInt(reader.readLine());
		double stopTime = Double.parseDouble(reader.readLine());
		int samplings = Integer.parseInt(reader.readLine());
		List<MeasureData> measures = readMeasures(reader,model);
		
		MyCARMASimulatorMultithread sim = new MyCARMASimulatorMultithread(name, model, system, reps,
				stopTime, samplings, measures, modelName);
		return sim;
	}
	
	/* read carma model */
	private static CarmaModel getCARMAModel(String name) {
		if (name.endsWith(".carma")) {
			try {
				ModelLoader loader = new ModelLoader();
				return loader.load(name);
			} catch (Exception e) {
				System.out.println("Problem when loading model from file " + name + ":");
				e.printStackTrace();
				return null;
			}
		}
		else {
			System.out.println("Could not read model file. Please specify a .carma file.");
			return null;
		}
	}
	
	/* read measures from experiment file */
	private static List<MeasureData> readMeasures(BufferedReader reader, CarmaModel model)
			throws IOException {
			List<String> allMeasures = Arrays.asList(model.getMeasures());
			List<MeasureData> measureList = new ArrayList<MeasureData>();
			String measureSpec = reader.readLine();
			while (measureSpec != null && !measureSpec.isEmpty()) {
				// measure specifications should be written as:
				// measureName (if no parameters are required)
				// or: measureName : parName = parValue
				// or: measureName : parName1 = parValue1, parName2 = parValue2, ... 
				String[] parts = measureSpec.split(":");
				String measureName = parts[0].trim();
				if (!allMeasures.contains(measureName)) {
					System.out.println("Measure " + measureName + " not found (ignoring).");
				}
				else if (parts.length > 2) {
					System.out.println("Invalid measure specification " + measureSpec + "(ignoring)");
				}
				else {
					// parse the specification 
					HashMap<String,Object> measurePars = new HashMap<String,Object>();
					if (parts.length == 2) {
						// the measure has parameters, read them one by one
						String[] parSpecs = parts[1].split(",");
						Map<String,Class<?>> parClasses = model.getParametersType(measureName);
						for (String parSpec : parSpecs) {
							int eqInd = parSpec.indexOf("=");
							String parName = parSpec.substring(0, eqInd).trim();
							String parValue = parSpec.substring(eqInd+1).trim();
							if (!parClasses.containsKey(parName)) {
								System.out.println("Unrecognised parameter " + parName +
										" for measure " + measureName + "  (ignoring).");
								continue;
							}
							Object valueToPut;
							if (parClasses.get(parName).equals(Integer.class))
								valueToPut = Integer.parseInt(parValue);
							else
								valueToPut = Double.parseDouble(parValue);
							measurePars.put(parName, valueToPut);
						}
					}
					// add the measure if all the necessary parameters have been given
					if (measurePars.size() != model.getMeasureParameters(measureName).length)
						System.out.println("Measure " + measureName + " requires more parameters.");
					else
						measureList.add(new MeasureData(measureName,measurePars));
				}
				measureSpec = reader.readLine();
			}
			return measureList;
		}
	
}
