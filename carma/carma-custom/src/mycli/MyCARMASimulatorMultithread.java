/**
 * Modified version of the CARMA CLI to support
 * multithreaded single trace generation. This is the
 * class that handles running of the simulation and
 * collection of outcomes/trajectories.
 * 
 * usage: MyCLIMutlithread <nthreads> <seed> <path>/
 * 
 * nthreads must be divisor of number of replications
 * specified in the experiments file.
 * 
 */

package mycli;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import org.apache.commons.math3.stat.descriptive.StatisticalSummary;
import org.cmg.ml.sam.sim.SimulationEnvironment;
import org.cmg.ml.sam.sim.SimulationMonitor;
import org.cmg.ml.sam.sim.sampling.SamplingCollection;
import org.cmg.ml.sam.sim.sampling.SimulationTimeSeries;
import org.cmg.ml.sam.sim.sampling.StatisticSampling;
import eu.quanticol.carma.core.ui.data.MeasureData;
import eu.quanticol.carma.core.ui.data.SimulationOutcome;
import eu.quanticol.carma.simulator.CarmaModel;
import eu.quanticol.carma.simulator.CarmaSystem;

public class MyCARMASimulatorMultithread implements Callable<Object>, Runnable {
	/**
	 * Experiment name.
	 */
	private String name;

	/**
	 * Specific name for this subtask, if applicable.
	 */
	private String taskName;
	
	/**
	 * System to use in the simulation.
	 */
	private String system;
	
	/**
	 * Number of replications in the simulation
	 */
	private int replications;
	
	/**
	 * Simulation time.
	 */
	private double simulationTime;
	
	/**
	 * Number of samplings.
	 */
	private int samplings;
	
	/**
	 * Measures to collect in the simulation
	 */
	private List<MeasureData> measures;
	
	private List<SimulationOutcome> results;

	private CarmaModel model;
	
	private String modelLocation;
	
	private Long seed;
	

	public MyCARMASimulatorMultithread(String name, CarmaModel model, String system, int replications,
			double simulationTime, int samplings, List<MeasureData> measures, String modelName) {
		super();
		this.name = name;
		this.model = model;
		this.system = system;
		this.replications = replications;
		this.simulationTime = simulationTime;
		this.samplings = samplings;
		this.measures = measures;
		this.results = new LinkedList<>();
		this.taskName = null;
		this.seed = null;
		this.modelLocation = modelName;
	}
	
	public MyCARMASimulatorMultithread(String name, CarmaModel model, String system, int replications,
			double simulationTime, int samplings, List<MeasureData> measures) {
		this(name,model,system,replications,simulationTime,samplings,measures,"[no name]");
	}
	
	public MyCARMASimulatorMultithread copy() {
		return new MyCARMASimulatorMultithread(name,model,system,replications,simulationTime,samplings,
				measures,modelLocation);
	}
	
	public void addSimulationResult( SimulationOutcome result ) {
		results.add(result);
	}
	
	public void clearResults() {
		results = new LinkedList<>();
	}
	
	public void removeResult( int i ) {
		results.remove(i);
	}
	
	public SimulationOutcome getResult( int i ) {
		return results.get(i);
	}

	/**
	 * @return the name
	 */
	public String getName() {
		return name;
	}

	/**
	 * @return the system
	 */
	public String getSystem() {
		return system;
	}

	/**
	 * @return the replications
	 */
	public int getReplications() {
		return replications;
	}

	/**
	 * @return the simulationTime
	 */
	public double getSimulationTime() {
		return simulationTime;
	}

	/**
	 * @return the samplings
	 */
	public int getSamplings() {
		return samplings;
	}


	/**
	 * @return The list of measures.
	 */
	public List<MeasureData> getMeasures() {
		return measures;
	}

	public CarmaModel getCarmaModel() {
		return model;
	}
	
	public boolean check() {
		if (model==null) {
			return false;
		}
		if (model.getFactory(system) == null) {
			return false;
		}
		return true;
	}
	
	public List<SimulationOutcome> getResults() {
		return results;
	}

	public void setCarmaModel(CarmaModel model) {
		this.model = model;
	}
	
	public String getModelLocation() {
		return modelLocation;
	}

	public void setReplications(int replications) {
		this.replications = replications;
	}
	
	public void setSimulationTime(double simulationTime) {
		this.simulationTime = simulationTime;
	}
	
	public void setTaskName(String taskName) {
		this.taskName = taskName;
	}
	
	public void setSeed(long seed) {
		this.seed = new Long(seed);
	}
	
	public void setResults(List<SimulationOutcome> results) {
		this.results = results;
	}
	
	public void execute() {
		execute(true);
	}
	
	/*************************************************************************************************************/
	/*************************************************************************************************************/
	/**
	 * @throws IOException 
	 * @throws ExecutionException 
	 * @throws InterruptedException ***********************************************************************************************************/
	
	public void Run(int nthreads, int seed, String path) throws IOException, InterruptedException, ExecutionException {
		double start_time = System.currentTimeMillis();
		// read station data from file
		report("Trying to read stations from " + path + "/stations.csv ...");
		FileReader fr = new FileReader(path + "stations.csv");
		BufferedReader br = new BufferedReader(fr);
		ArrayList<String[]> stations_rows = new ArrayList<String[]>();
		String line = null;
		while ((line = br.readLine()) != null) {
			stations_rows.add(line.split(","));
		}
		br.close();
		fr.close();
		// get station capacities
		int numberOfStations = stations_rows.size() - 1;
		int[] capacities = new int[numberOfStations];
		for (int i = 1; i < stations_rows.size(); i++) {
			capacities[i - 1] = Integer.parseInt(stations_rows.get(i)[3]);
		}
		report("Read " + numberOfStations + " stations.");
		report("Starting simulation with " + nthreads + " threads...");
		// data fields for all the runs
		double[][][] results = new double[replications][][];
		ArrayList<String> resultsNames = new ArrayList<String>();
		ExecutorService executorService = Executors.newFixedThreadPool(nthreads);
		ArrayList<Future<ThreadResult>> futures = new ArrayList<Future<ThreadResult>>(nthreads);
		int repsPerThread = replications / nthreads;
		// start all the threads
		for (int i = 0; i < nthreads; i++) {
			final int x = i * repsPerThread;
			futures.add(executorService.submit(() -> Thread(x, repsPerThread, path, seed, numberOfStations, capacities)));
		}
		// collect results from the threads
		for (int i = 0; i < nthreads; i++) {
			ThreadResult result = futures.get(i).get();
			if (i == 0) {
				resultsNames = result.resultsNames;
			}
			for (int j = 0; j < repsPerThread; j++) {
				results[i * repsPerThread + j] = new double[result.results[j].length][];
				for(int x = 0; x < result.results[j].length; x++) {
					results[i * repsPerThread + j][x] = new double[result.results[j][x].length];
					for(int y = 0; y < result.results[j][x].length; y++) {
						results[i * repsPerThread + j][x][y] = result.results[j][x][y];
					}
				}
			}
		}
		executorService.shutdown();
		// after performing all replications, calculate mean, stddev and stderr for the global and station measures
		report("Producing global results ...");
		for (int m = 0; m < results[0].length; m++) {
			String rows_m = "";
			String measureName = resultsNames.get(m);
			PrintWriter writer = new PrintWriter(path + "Results/" + measureName + ".csv");
			BufferedWriter bwriter = new BufferedWriter(writer);
			for (int t = 0; t < results[0][0].length; t++) {
				double avg_t = 0;
				double sum_of_squared_err = 0;
				double dev_t = 0;
				double err_t = 0;
				rows_m += String.format("%f,", t * (simulationTime / samplings));
				for (int r = 0; r < replications; r++) {
					avg_t += results[r][m][t];
				}
				avg_t /= replications;
				for (int r = 0; r < replications; r++) {
					sum_of_squared_err += (results[r][m][t] - avg_t) * (results[r][m][t] - avg_t);
				}
				dev_t = Math.sqrt(sum_of_squared_err / (replications - 1));
				err_t = dev_t / Math.sqrt(replications);
				rows_m += String.format("%f,", avg_t);
				rows_m += String.format("%f,", dev_t);
				rows_m += String.format("%f", err_t);
				rows_m += "\n";
				bwriter.write(rows_m);
				rows_m = "";
			}
			bwriter.flush();
			bwriter.close();
		}
		System.out.printf("elapsed time: %f", System.currentTimeMillis() - start_time);
	}
	
	// data structure that holds the results of one thread
	private class ThreadResult{
		public double[][][] results;
		public ArrayList<String> resultsNames;
		public ThreadResult(double[][][] _results, ArrayList<String> _resultsNames) {
			this.results = new double[_results.length][][];
			for (int x = 0; x < _results.length; x++) {
				this.results[x] = new double[_results[x].length][];
				for(int y = 0; y < _results[x].length; y++) {
					this.results[x][y] = new double[_results[x][y].length];
					for(int z = 0; z < _results[x][y].length; z++) {
						this.results[x][y][z] = _results[x][y][z];
					}
				}
			}
			this.resultsNames = _resultsNames;
		}
	}
	
	// runs the simulation and collects the results for reps/nthreads replications 
	public ThreadResult Thread(int start, int number, String path, int seed, int numberOfStations, int[] capacities) throws IOException {
		double[][][] results = new double[number][][];
		ArrayList<String> resultsNames = new ArrayList<String>();
		for (int i = 0; i < number; i++) {
			// trajectory of availability at each station
			double[][] trajectories = new double[numberOfStations][];
			// perform a single replication and collect outcomes
			SimulationOutcome outcome = RunSingle(start + i, seed);
			List<SimulationTimeSeries> timeSeries = outcome.getCollectedData();
			results[i] = new double[timeSeries.size()][];
			// for each collected measure, decide whether it is a station or a global measure
			for (SimulationTimeSeries ts : timeSeries) {
				String measureName = ts.getName();
				resultsNames.add(measureName);
				if (measureName.startsWith("Available")) {
					// if it is a station measure collect the trajectory
					measureName = measureName.substring(14, measureName.length() - 1);
					int stationId = Integer.valueOf(measureName);
					StatisticalSummary[] data = ts.getData();
					trajectories[stationId] = new double[data.length];
					results[i][timeSeries.indexOf(ts)] = new double[data.length];
					for (int s = 0; s < data.length; s++) {
						trajectories[stationId][s] = data[s].getMean();
						results[i][timeSeries.indexOf(ts)][s] = data[s].getMean();
					}
				} else {
					// if it's a global measure just add the outcomes to the overall results
					StatisticalSummary[] data = ts.getData();
					results[i][timeSeries.indexOf(ts)] = new double[data.length];
					for (int s = 0; s < data.length; s++) {
						results[i][timeSeries.indexOf(ts)][s] = data[s].getMean();
					}
				}
			}
			// save the trajectory to a csv file
			int trajNum = start + i;
			PrintWriter writer = new PrintWriter(path + "Traces/Traj" + trajNum + ".csv");
			BufferedWriter bwriter = new BufferedWriter(writer);
			double samplingRatio = (simulationTime / samplings);
			for (int t = 0; t < trajectories[0].length; t++) {
				for (int s = 0; s < trajectories.length; s++) {
					bwriter.write((t * samplingRatio) + ",");
					bwriter.write(s + ",");
					bwriter.write(trajectories[s][t] + ",");
					bwriter.write((capacities[s] - trajectories[s][t]) + "\n");
				}
			}
			bwriter.flush();
			bwriter.close();
			report("Saved Trajectory " + trajNum);
		}
		return new ThreadResult(results, resultsNames);
	}
	
	// runs a single replication and returns the outcome
	public SimulationOutcome RunSingle(int number, int seed) {
		// set up simulation environment (simulation, seed, sampling)
		SimulationEnvironment<CarmaSystem> sim = new SimulationEnvironment<CarmaSystem>(model.getFactory(system));
		sim.seed(seed + number);
		SamplingCollection<CarmaSystem> sc = new SamplingCollection<CarmaSystem>();
		for(MeasureData measure : measures){
			sc.addSamplingFunction(new StatisticSampling<CarmaSystem>(
					1 + samplings,
					simulationTime / samplings,
					model.getMeasure(measure.getMeasureName(), measure.getParameters())
			));
		}
		sim.setSampling(sc);
		
		double startTime = System.currentTimeMillis();
		sim.simulate(new SimulationMonitor() {
	    	//private double target = simulationTime;
	    	//private int i = 0;
	    	//private final double ratio = 0.2;
	    	//private double nextStop = ratio * target;
	    	//private double timeWhole = 0;
	    	
			@Override
			public void startIteration(int i) {
				System.out.print("Replication " + (number));
			}
			
			@Override
			public void update(double t) {
				/*if (timeWhole + t >= nextStop) {
					System.out.println();
					if (taskName != null) {
						System.out.print("[" + taskName + "] ");
					}
					// Note: this might not always give the right percentage,
					// if more than ratio*target has passed since the last message
					// but this should only be the case in very short runs.
					System.out.println((10 * ++i) + "% completed");
					nextStop += ratio * target;
				}*/
			}
			
			@Override
			public boolean isCancelled() {
				return false;
			}

			@Override
			public void endSimulation(int i) {
				//timeWhole += simulationTime;
			}
			
	    }, 1, simulationTime);
	    System.out.println();
	    double totalTime = System.currentTimeMillis() - startTime;
		return new SimulationOutcome("Traj" + String.valueOf(number), totalTime, totalTime,
				sc.getSimulationTimeSeries(1));
	}
	
	private static void report(String msg) {
			System.out.println(msg);
	}
	
	/*private static void warn(String msg) {
		System.out.println("Warning: " + msg);
	}*/
	
	/*************************************************************************************************************/
	/*************************************************************************************************************/
	/*************************************************************************************************************/
	//Old methods
	
	public void execute(boolean reportProgress) {
		// set up simulation environment
		SimulationEnvironment<CarmaSystem> sim = new SimulationEnvironment<CarmaSystem>(model.getFactory(system));
		if (seed != null) {
			sim.seed(seed);
		}
		SamplingCollection<CarmaSystem> sc = new SamplingCollection<CarmaSystem>();
		for(MeasureData measure : measures){
			sc.addSamplingFunction(new StatisticSampling<CarmaSystem>(
					1 + samplings,
					simulationTime / samplings,
					model.getMeasure(measure.getMeasureName(), measure.getParameters())
			));
		}
		sim.setSampling(sc);
		
		DateFormat dateFormat1 = new SimpleDateFormat("dd/MM/yyyy  HH:mm:ss");
	    String tag = dateFormat1.format(Calendar.getInstance().getTime());
		double startTime = System.currentTimeMillis();
		
		// run the simulation and collect the results
		//sim.simulate(replications, simulationTime);
	    sim.simulate(new SimulationMonitor() {
	    	private double target = simulationTime * replications;
	    	private int i = 0;
	    	private final double ratio = 0.1;
	    	private double nextStop = ratio * target;
	    	private double timeWhole = 0;
	    	
			@Override
			public void startIteration(int i) {
				if (reportProgress)
					System.out.print("Replication "+(i+1));
			}
			
			@Override
			public void update(double t) {
				if (reportProgress && timeWhole + t >= nextStop) {
					System.out.println();
					if (taskName != null) {
						System.out.print("[" + taskName + "] ");
					}
					// Note: this might not always give the right percentage,
					// if more than ratio*target has passed since the last message
					// but this should only be the case in very short runs.
					System.out.println((10 * ++i) + "% completed");
					nextStop += ratio * target;
				}
			}
			
			@Override
			public boolean isCancelled() {
				return false;
			}

			@Override
			public void endSimulation(int i) {
				timeWhole += simulationTime;
			}
			
	    }, replications, simulationTime);
	    if (reportProgress)
	    	System.out.println();
	    double endTime = System.currentTimeMillis();
	    double totalTime = endTime-startTime;
		addSimulationResult(new SimulationOutcome(tag, totalTime, totalTime/replications,
				sc.getSimulationTimeSeries(replications)));   
	}
	
	public Void call() {
		execute();
		return null;
	}
	
	public void run() {
		execute();
	}

}