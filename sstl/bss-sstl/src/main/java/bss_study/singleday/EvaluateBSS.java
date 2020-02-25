/**
 * @author justinnk
 * 
 * This file contains the code needed to read in trajetories
 * and evaluate the formulas on them. It will assumes that a
 * folder named "Formulas" exists at the same path and write
 * all outputs to that folder.
 * Usage: EvaluateBSS <ntraj>
 * 
 * <ntraj>: number of trajectories to evaluate
 * 
 */

package bss_study.singleday;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

import eu.quanticol.jsstl.core.formula.Signal;
import eu.quanticol.jsstl.core.formula.SignalStatistics;
import eu.quanticol.jsstl.core.formula.jSSTLScript;
import eu.quanticol.jsstl.core.space.GraphModel;
import eu.quanticol.jsstl.core.io.SyntaxErrorExpection;
import eu.quanticol.jsstl.core.io.TraGraphModelReader;

public class EvaluateBSS {
	
	public static void main(String[] args) throws SyntaxErrorExpection, IOException {
		EvaluateBSS t = new EvaluateBSS(Integer.parseInt(args[0]));
	}
	
	public EvaluateBSS(int replications) throws SyntaxErrorExpection, IOException {
		// Load the graph representing the spatial structure
		TraGraphModelReader graphread = new TraGraphModelReader();
		GraphModel graph = graphread.read("model.tra");//"../../graph.tra");
		System.out.println("Loaded graph.");
		System.out.println("\tlocations: " + graph.getLocations());
		System.out.println("\t#edges: " + graph.getEdges().size());
		// compute the distance matrix for the graph (shortest distances between all locations)
		double dMcomputationTime = System.currentTimeMillis();
		graph.dMcomputation();
		dMcomputationTime = (System.currentTimeMillis() - dMcomputationTime) / 1000.0;
		// load the sstl script
		System.out.println("Initialized script.");
		jSSTLScript script = new BSSFormulas();
		// set number of runs and prefix for trajectories
		int runs = replications;
		String trajPref = "Traces/Traj";
		// evaluate formulas
		System.out.println("Start checking.");
		double totalCheckTime = System.currentTimeMillis();
		double phi_time = checkFormula(script, "phi_time", graph, graph.getNumberOfLocations(), getPhiTimeParams(), runs, trajPref);
		double phi_dist = checkFormula(script, "phi_dist", graph, graph.getNumberOfLocations(), getPhiDistParams(), runs, trajPref);
		//double phi_dist_plus = checkFormula(script, "phi_dist+", graph, graph.getNumberOfLocations(), getPhiDistPlusParams(), runs, trajPref);
		double phi_empty = checkFormula(script, "phi_empty", graph, graph.getNumberOfLocations(), getNoParams(), runs, trajPref);
		double phi_full = checkFormula(script, "phi_full", graph, graph.getNumberOfLocations(), getNoParams(), runs, trajPref);
		//double phi_clust_b = checkFormula(script, "phi_clust_b", graph, graph.getNumberOfLocations(), getPhiClustParams(), runs, trajPref);
		//double phi_clust_s = checkFormula(script, "phi_clust_s", graph, graph.getNumberOfLocations(), getPhiClustParams(), runs, trajPref);
		double phi_prob = checkFormula(script, "phi_prob", graph, graph.getNumberOfLocations(), getPhiProbParams(), runs, trajPref);
		// check phi's
		totalCheckTime = (System.currentTimeMillis() - totalCheckTime) / 1000.0;
		System.out.println("End checking.");
		// print performance information
		System.out.println("Time for distance matrix: " + dMcomputationTime + "s");
		System.out.println("Total time for checking: " + totalCheckTime + "s");
		System.out.println("Average time per run for checking (phi_dist): " + phi_dist + "s");
		System.out.println("Average time per run for checking (phi_time): " + phi_time + "s");
		//System.out.println("Average time per run for checking (phi_dist+): " + phi_dist_plus + "s");
		System.out.println("Average time per run for checking (phi_empt): " + phi_empty + "s");
		System.out.println("Average time per run for checking (phi_full): " + phi_full + "s");
		//System.out.println("Average time per run for checking (phi_clust): " + phi_clust_b + "s");
		//System.out.println("Average time per run for checking (phi_clust): " + phi_clust_s + "s");
		System.out.println("Average time per run for checking (phi_prob): " + phi_prob + "s");
	}
	
	/**
	 * Get parameters for formulas that are parameterless
	 * @return
	 */
	private ArrayList<HashMap<String,Double>> getNoParams(){
		return new ArrayList<HashMap<String,Double>>();
	}
	
	/**
	 * Get parameter values for PHI_DIST
	 * 0m to 500m in steps of 50m
	 * @return ArrayList of parameter names and values
	 */
	private ArrayList<HashMap<String,Double>> getPhiDistParams(){
		ArrayList<HashMap<String, Double>> params = new ArrayList<HashMap<String,Double>>();
		for (int i = 0; i < 501; i += 50) {
			HashMap<String, Double> map = new HashMap<String, Double>();
			map.put("d", Double.valueOf(i));
			params.add(map);
		}
		return params;
	}
	
	/**
	 * Get parameter values for PHI_DIST+
	 * @return the same parameters as for PHI_DIST
	 */
	/*private ArrayList<HashMap<String,Double>> getPhiDistPlusParams(){
		return getPhiDistParams();
	}*/
	
	/**
	 * Get parameter values for PHI_TIME
	 * 0min to 10min in steps of 1min
	 * @return ArrayList of parameter names and values
	 */
	private ArrayList<HashMap<String,Double>> getPhiTimeParams(){
		ArrayList<HashMap<String, Double>> params = new ArrayList<HashMap<String,Double>>();
		for (int i = 0; i < 11; i += 1) {
			HashMap<String, Double> map = new HashMap<String, Double>();
			map.put("t", Double.valueOf(i));
			params.add(map);
		}
		return params;
	}
	
	private ArrayList<HashMap<String,Double>> getPhiProbParams(){
		ArrayList<HashMap<String, Double>> params = new ArrayList<HashMap<String,Double>>();
		for (int ts = 0; ts < 1439; ts+=360) {
			HashMap<String, Double> map = new HashMap<String, Double>();
			map.put("ts", Double.valueOf(ts));
			map.put("te", Double.valueOf(ts + 359));
			params.add(map);
		}
		return params;
	}
	
	/**
	 * Get parameter values for PHI_CLUST
	 * for each k (min. bikes) value from 0 to 3, for each distance from 0m to 500m in 50m steps
	 * @return ArrayList of parameter names and values
	 */
	/*private ArrayList<HashMap<String,Double>> getPhiClustParams(){
		ArrayList<HashMap<String, Double>> params = new ArrayList<HashMap<String,Double>>();
		for (int k = 0; k < 3; k++) {
			for (int d = 0; d < 500; d += 50) {
				HashMap<String, Double> map = new HashMap<String, Double>();
				map.put("k", Double.valueOf(k));
				map.put("dc", Double.valueOf(d));
				params.add(map);
			}
		}
		return params;
	}*/
	
	/**
	 * Reads a Trajectory from a file and turns it into a spatio-temporal signal
	 * Format: time, location, values...
	 * @return Signal corresponding to the given trajectory
	 * 
	 * We have to use a workaround that copies the last time-frame and pastes it as 1440 at
	 * the end. Otherwise a final time of 1439 for the formulas results in an error. The
	 * adjustments made for that are marked with WORKAROUND.
	 * 
	 */
	public Signal readTrajectory(GraphModel graph, String filename) throws IOException {
		// read csv file row by row
		FileReader fr = new FileReader(filename);
		BufferedReader br = new BufferedReader(fr);
		ArrayList<String[]> rows = new ArrayList<String[]>();
		String line = null;
		while ((line = br.readLine()) != null) {
			rows.add(line.split(","));
		}
		br.close();
		fr.close();
		// Get number of locations
		int locLength = graph.getNumberOfLocations();
		// Get array with all the probe times
		Set<Double> times_dupl = new HashSet<Double>();
		for (int t = 1; t < rows.size(); t++) {
			times_dupl.add(Double.valueOf(rows.get(t)[0]));
		}
		int timesLength = times_dupl.size();
		//System.out.printf("Times: (%d)\n", timesLength);
		double[] times = new double[timesLength + 1]; // WORKAROUND: +1
		for(int r = 0; r < timesLength * locLength; r += locLength) {
			times[r / locLength] = Double.valueOf(rows.get(r)[0]);
			//System.out.printf("%f\n", times[r / locLength]);
		}
		times[times.length - 1] = 1440.0; // WORKAROUND
		// read values for number of available bikes and slots
		//System.out.println("Values: \n");
		double[] bikes = new double[rows.size() + locLength]; // WORKAROUND: +locLength
		double[] slots = new double[rows.size() + locLength]; // WORKAROUND: +locLength
		for (int r = 0; r < rows.size(); r++) {
			bikes[r] = Double.valueOf(rows.get(r)[2]);
			slots[r] = Double.valueOf(rows.get(r)[3]);
			//System.out.printf("%f, %f\n", bikes[r], slots[r]);
		}
		// WORKAROUND
		for (int r = 0; r < locLength; r++) {
			bikes[rows.size() + r] = Double.valueOf(rows.get(rows.size() - locLength + r)[2]);
			slots[rows.size() + r] = Double.valueOf(rows.get(rows.size() - locLength + r)[3]);
		}
		// transform data to signal format
		double[][][] data = new double[locLength][][];
		for (int l = 0; l < locLength; l++) {
			data[l] = new double[timesLength + 1][]; // WORKAROUND: +1
		}
		for (int t = 0; t < timesLength + 1; t++) { // WORKAROUND: +1
			for (int l = 0; l < locLength; l++) {
				data[l][t] = new double[2];
				data[l][t][0] = bikes[t * locLength + l];
				data[l][t][1] = slots[t * locLength + l];
				//System.out.printf("location: %d, time: %d, bikes: %f, slots: %f\n", l, t, data[l][t][0], data[l][t][1]);
			}
		}
		Signal s = new Signal(graph, times, data);
		return s;
	}
	
	/**
	 * Function to check the boolean satisfaction of a given {@link formula}.
	 * 
	 * @param script The script containing the formula.
	 * @param formula The formula to evaluate.
	 * @param graph The graph for the given system.
	 * @param locations The number of locations in the graph.
	 * @param params List of parameter values.
	 * @param runs Number of runs.
	 * @param trajPref Prefix for the trajectories.
	 * @return Average evaluation time in milliseconds.
	 * @throws IOException In case saving the results fails.
	 */
	public double checkFormula( jSSTLScript script, String formula, GraphModel graph, int locations, ArrayList<HashMap<String,Double>> params , int runs, String trajPref) throws IOException {
		// 
		int end = params.size() == 0 ? 1 : params.size();
		// statistics for each parameter
		ArrayList<SignalStatistics> statphi = new ArrayList<SignalStatistics>();
		// wall clock time measurement for the evaluation
		double time = 0.0;
		// string for the csv results
		String rows = "";
		// populate statistics list
		for (int i = 0; i < end; i++) {
			statphi.add(i, new SignalStatistics(locations));
		}
		// loop through all the trajectories
		for (int i = 0; i < runs; i++) {
			System.out.println("\t(" + formula + ") Trajectory: " + i);
			// retreive trajectory for current run
				/*Trajectory traj = model.simulate( vartosave, tinit, tf, steps);
				double[] times = model.timesTraj(traj);
				double[][][] data = model.dataTraj(traj, locations, times.length, var);
				Signal s = new Signal(graph, times, data);*/
			Signal s = readTrajectory(graph, trajPref + i + ".csv");
			// loop through all the parameter values
			for (int k = 0; k < end; k++) {
				HashMap<String,Double> parValues = new HashMap<String, Double>();
				if (params.size() > 0) {
					parValues = params.get(k);
				}
				double tStartB = System.currentTimeMillis();
				statphi.get(k).add(script.booleanSat(formula, parValues, graph, s));
				//System.out.println(script.booleanCheck(parValues, formula, graph, s).toString());
				double elapsedSecondsB = (System.currentTimeMillis() - tStartB) / 1000.0;
				time += elapsedSecondsB;
			}
		}
		// for every parameter, get the mean and stddev from the evaluation
		// and save those in a csv file: param | loc | avg | min | max | dev
		PrintWriter csvprinter = new PrintWriter("Formulas/" + formula + ".csv");
		BufferedWriter writer = new BufferedWriter(csvprinter);
		for (int k = 0; k < end; k++) {
			for (int l = 0; l < locations; l++) {
				rows += String.format(Locale.US, "%d", k);
				rows += String.format(Locale.US, ",%d", l);
				double mean = statphi.get(k).getAverage()[l];
				rows += String.format(Locale.US, ",%.10f", mean);
				double min = statphi.get(k).getMin()[l];
				rows += String.format(Locale.US, ",%.10f", min);
				double max = statphi.get(k).getMax()[l];
				rows += String.format(Locale.US, ",%.10f", max);
				double stdev = statphi.get(k).getStandardDeviation()[l];
				rows += String.format(Locale.US, ",%.10f", stdev);
				rows += "\n";
				writer.write(rows);
				rows = "";
			}
		}
		writer.flush();
		writer.close();
		return time / runs;
	}
}
