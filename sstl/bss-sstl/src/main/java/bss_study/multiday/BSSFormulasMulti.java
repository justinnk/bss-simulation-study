/**
 * @author justinnk
 * 
 * This file contains the formula definitions used for evaluation
 * in EvaluateBSSMulti.java
 * 
 */

package bss_study.multiday;
import java.util.Map;

import eu.quanticol.jsstl.core.formula.AndFormula;
import eu.quanticol.jsstl.core.formula.AtomicFormula;
import eu.quanticol.jsstl.core.formula.EventuallyFormula;
import eu.quanticol.jsstl.core.formula.GloballyFormula;
import eu.quanticol.jsstl.core.formula.NotFormula;
import eu.quanticol.jsstl.core.formula.ParametricExpression;
import eu.quanticol.jsstl.core.formula.ParametricInterval;
import eu.quanticol.jsstl.core.formula.ReferencedFormula;
import eu.quanticol.jsstl.core.formula.SignalExpression;
import eu.quanticol.jsstl.core.formula.SomewhereFormula;
import eu.quanticol.jsstl.core.formula.jSSTLScript;

public class BSSFormulasMulti extends jSSTLScript{

	
	public static final int B_VAR_ = 0; // bikes available
	public static final int S_VAR_ = 1; // docking points available
	
	public static final double T_END_ = 4319.0;
	
	
	public BSSFormulasMulti() {
		super(new String[] {
				"B",
				"S"
		});
		// parameters
		addParameter("T_start", 0.0, T_END_ - 1440.0); // start time for each day
		addParameter("T_end", 0.0, T_END_); // final time for each day
		addParameter("t", 0.0, 10.0); // time limit (minutes) for PHI_TIME
		addParameter("d", 0.0, 500.0); // distance (meters) from station for PHI_DIST
		//addParameter("dc", 0.0, 500.0); // cluster max. distance for PHI_CLUST_B/_S
		//addParameter("k", 0.0, 3.0); // cluster max. allowed bikes for PHI_CLUST_B/_S
		addParameter("ts", 0.0, T_END_ - 60.0); // start time for problematic stations PHI_PROB
		addParameter("te", 0.0, T_END_); // end time for problematic stations PHI_PROB
		
		// number of available bikes > 0
		this.addFormula("phiB", 
			new AtomicFormula(new ParametricExpression() {
				public SignalExpression eval(Map<String, Double> parameters) {
					return new SignalExpression() {
						public double eval(double... variables) {
							return variables[getIndex(B_VAR_)];
						}
					};
				}
			}, true), null);
		// number of free slots > 0
		this.addFormula("phiS", 
			new AtomicFormula(new ParametricExpression() {
				public SignalExpression eval(Map<String, Double> parameters) {
					return new SignalExpression() {
						public double eval(double... variables) {
							return variables[getIndex(S_VAR_)];
						}
					};
				}
			}, true), null);
		// Somewhere within distance d there is a free slot and a bike
		this.addFormula( "phid0" ,
				new AndFormula( 
					new SomewhereFormula( 
						new ParametricInterval( 
							new ParametricExpression() {
								public SignalExpression eval( final Map<String,Double> parameters ) {
									return new SignalExpression() {
										public double eval( double ... variables ) {
											return 0;
										}
									};					
								}
							} , 
							new ParametricExpression() {
								public SignalExpression eval( final Map<String,Double> parameters ) {
									return new SignalExpression() {
										public double eval( double ... variables ) {
											return parameters.get("d");
										}
									};					
								}
							} 		
						)		
						 ,
						new ReferencedFormula( 
							this ,
							"phiB"
						)		
					),
					new SomewhereFormula( 
						new ParametricInterval( 
							new ParametricExpression() {
								public SignalExpression eval( final Map<String,Double> parameters ) {
									return new SignalExpression() {
										public double eval( double ... variables ) {
											return 0;
										}
									};					
								}
							}, 
							new ParametricExpression() {
								public SignalExpression eval( final Map<String,Double> parameters ) {
									return new SignalExpression() {
										public double eval( double ... variables ) {
											return parameters.get("d");
										}
									};					
								}
							} 		
						),
						new ReferencedFormula( 
							this ,
							"phiS"
						)		
					)		
				), null);
		/* 
		 * PHI_DIST
		 * There is always a bike and a free slot at distance d
		 */
		this.addFormula("phi_dist",
			new GloballyFormula( 
				new ParametricInterval( 
					new ParametricExpression() {
						public SignalExpression eval( final Map<String,Double> parameters ) {
							return new SignalExpression() {
								public double eval( double ... variables ) {
									return 0.0;
								}
							};					
						}
					}, 
					new ParametricExpression() {
						public SignalExpression eval( final Map<String,Double> parameters ) {
							return new SignalExpression() {
								public double eval( double ... variables ) {
									return T_END_;
								}
							};					
						}
					} 		
				),
				new ReferencedFormula( 
					this ,
					"phid0"
				)		
			), null);
		// within the interval of 0 to t, eventually there will be a bike and a free slot
		this.addFormula( "phit0" ,
				new EventuallyFormula( 
					new ParametricInterval( 
						new ParametricExpression() {
							public SignalExpression eval( final Map<String,Double> parameters ) {
								return new SignalExpression() {
									public double eval( double ... variables ) {
										return 0;
									}
								};					
							}
						} , 
						new ParametricExpression() {
							public SignalExpression eval( final Map<String,Double> parameters ) {
								return new SignalExpression() {
									public double eval( double ... variables ) {
										return parameters.get("t");
									}
								};					
							}
						} 		
					),
					new AndFormula( 
						new ReferencedFormula( 
							this ,
							"phiB"
						),
						new ReferencedFormula( 
							this ,
							"phiS"
						)		
					)
		), null );
		/*
		 * PHI_TIME
		 * If I wait t minutes, there will be a bike and a free slot
		 */
		this.addFormula("phi_time",
				new GloballyFormula( 
					new ParametricInterval( 
						new ParametricExpression() {
							public SignalExpression eval( final Map<String,Double> parameters ) {
								return new SignalExpression() {
									public double eval( double ... variables ) {
										return 0.0;
									}
								};					
							}
						}, 
						new ParametricExpression() {
							public SignalExpression eval( final Map<String,Double> parameters ) {
								return new SignalExpression() {
									public double eval( double ... variables ) {
										return T_END_ - parameters.get("t");
									}
								};					
							}
						} 		
					),
				new ReferencedFormula( 
					this ,
					"phit0"
				)		
			), null);
			/*
			 * PHI_EMPTY
			 * The station will eventually be empty
			 */
			this.addFormula("phi_empty", new EventuallyFormula(
				new ParametricInterval( 
					new ParametricExpression() {
						public SignalExpression eval( final Map<String,Double> parameters ) {
							return new SignalExpression() {
								public double eval( double ... variables ) {
									return parameters.get("T_start");
								}
							};					
						}
					}, 
					new ParametricExpression() {
						public SignalExpression eval( final Map<String,Double> parameters ) {
							return new SignalExpression() {
								public double eval( double ... variables ) {
									return parameters.get("T_end");
								}
							};					
						}
					} 		
				),
				new NotFormula(new ReferencedFormula(this, "phiB"))), null);
			/*
			 * PHI_FULL
			 * The station will eventually be full
			 */
			this.addFormula("phi_full", new EventuallyFormula(
				new ParametricInterval( 
						new ParametricExpression() {
							public SignalExpression eval( final Map<String,Double> parameters ) {
								return new SignalExpression() {
									public double eval( double ... variables ) {
										return parameters.get("T_start");
									}
								};					
							}
						}, 
						new ParametricExpression() {
							public SignalExpression eval( final Map<String,Double> parameters ) {
								return new SignalExpression() {
									public double eval( double ... variables ) {
										return parameters.get("T_end");
									}
								};					
							}
						} 		
					),
					new NotFormula(new ReferencedFormula(this, "phiS"))), null);
			/*
			 * PHI_PROB
			 * Within the specified interval the station has at least a bike and a slot available
			 */
			this.addFormula("phi_prob", 
				new GloballyFormula(
					new ParametricInterval( 
							new ParametricExpression() {
								public SignalExpression eval( final Map<String,Double> parameters ) {
									return new SignalExpression() {
										public double eval( double ... variables ) {
											return parameters.get("ts");
										}
									};					
								}
							} , 
							new ParametricExpression() {
								public SignalExpression eval( final Map<String,Double> parameters ) {
									return new SignalExpression() {
										public double eval( double ... variables ) {
											return parameters.get("te");
										}
									};					
								}
							} 		
						),
					new AndFormula( 
						new AtomicFormula( 
							new ParametricExpression( ) {
								public SignalExpression eval( Map<String, Double> parameters ) {
									return new SignalExpression() {		
										public double eval(double... variables) {
											return (variables[getIndex(B_VAR_)]);
										}
									};				
								}
							},
						true),
						new AtomicFormula( 
							new ParametricExpression( ) {
								public SignalExpression eval( Map<String, Double> parameters ) {
									return new SignalExpression() {		
										public double eval(double... variables) {
											return (variables[getIndex(S_VAR_)]);
										}
									};				
								}
							},
						true)
					)
			), null);
			
			// --------------------------------------------------------------------------------
			// Testing / Debugging ------------------------------------------------------------
			// --------------------------------------------------------------------------------
			// there is a station somewhere between 0 and d with a bike
			this.addFormula("phiTest", 
				new SomewhereFormula( //Somewhere
					new ParametricInterval( // in interval from
						new ParametricExpression() { // lower bound 0
							public SignalExpression eval(final Map<String, Double> parameters) {
								return new SignalExpression() {
									public double eval(double... variables) {
										return 0;
									}
								};
							}
					}, new ParametricExpression() { // upper bound parameter d
						public SignalExpression eval(final Map<String, Double> parameters) {
							return new SignalExpression() {
								public double eval(double... values) {
									return parameters.get("d");
								}
							};
						}
					}), new ReferencedFormula(this, "phiB")), new String[] {"phiB"});
			// The station will eventually become empty
			this.addFormula("eventuallyEmpty", new EventuallyFormula(new ParametricInterval(
					new ParametricExpression() {
						public SignalExpression eval(final Map<String, Double> parameters) {
							return new SignalExpression() {
								public double eval(double... variables) {
									return parameters.get("T_start");
								}
							};
						}
						
					}, 
					new ParametricExpression() {
						public SignalExpression eval(final Map<String, Double> parameters) {
							return new SignalExpression() {
								public double eval(double... variables) {
									return parameters.get("T_end");
								}
							};
						}
					}),
					new NotFormula(new ReferencedFormula(this, "phiB"))), null);
			// --------------------------------------------------------------------------------
			// --------------------------------------------------------------------------------
			// --------------------------------------------------------------------------------
			
			/* Unused formulae */
			
			/*
			 * PHI_DIST+
			 * An empty station is always surrounded by ones that have a bike
			 */
			/*this.addFormula( "phi_dist+",
					new GloballyFormula(				
						new ParametricInterval(0, T_END_),
							new SurroundFormula(	
								new ParametricInterval( 
									new ParametricExpression() {
										public SignalExpression eval( final Map<String,Double> parameters ) {
											return new SignalExpression() {
												public double eval( double ... variables ) {
													return 0;
												}
											};					
										}
									}, 
									new ParametricExpression() {
										public SignalExpression eval( final Map<String,Double> parameters ) {
											return new SignalExpression() {
												public double eval( double ... variables ) {
													return parameters.get("d");
												}	
											};					
										}
									} 		
								), 
								new AtomicFormula( 
									new ParametricExpression() {
										public SignalExpression eval( Map<String, Double> parameters ) {
											return )new SignalExpression() {		
												public double eval(double... variables) {
													return 1 - (variables[getIndex(B_VAR_)]); // eq. B = 0
												}
											};				
										}
									},
								true),
								new AtomicFormula( 
									new ParametricExpression() {
										public SignalExpression eval( Map<String, Double> parameters ) {
											return new SignalExpression() {	
												public double eval(double... variables) {
													return (variables[getIndex(B_VAR_)]);
												}				
											};	
										}
									}, true)		
							)														
						), null);		*/
			
			/*
			 * PHI_EMPT
			 * At some point in time, there is and will be no more bike available
			 */
			/*this.addFormula("phi_empt", 
				new UntilFormula(
					new ParametricInterval(0, T_END_ - 450),
					new AtomicFormula(
						new ParametricExpression() {
							public SignalExpression eval(Map<String, Double> parameters) {
								return new SignalExpression() {
									public double eval(double... variables) {
										return variables[getIndex(B_VAR_)];
									}
								};
							}
						}, true),
				//new EventuallyFormula(
					//new ParametricInterval(0, T_END_),
					new GloballyFormula(
						new ParametricInterval(0, T_END_ - 1000),
						new AtomicFormula(
							new ParametricExpression() {
								public SignalExpression eval(Map<String, Double> parameters) {
									return new SignalExpression() {
										public double eval(double... variables) {
											return 1 - variables[getIndex(B_VAR_)];
										}
									};
								}
							}, true)
						)
				), null);*/
			/*
			 * PHI_FULL
			 * At some point in time, there is and will be no more slot available
			 */
			/*this.addFormula("phi_full", 
				new UntilFormula(
					new ParametricInterval(0, T_END_ - 450),
					new AtomicFormula(
						new ParametricExpression() {
							public SignalExpression eval(Map<String, Double> parameters) {
								return new SignalExpression() {
									public double eval(double... variables) {
										return variables[getIndex(S_VAR_)];
									}
								};
							}
						}, true),
					new GloballyFormula(
						new ParametricInterval(0, T_END_ - 1000),
						new AtomicFormula(
							new ParametricExpression() {
								public SignalExpression eval(Map<String, Double> parameters) {
									return new SignalExpression() {
										public double eval(double... variables) {
											return 1 - variables[getIndex(S_VAR_)];
										}
									};
								}
							}, true)
						)
				), null);*/
			/*
			 * PHI_CLUST_B
			 * A station with no bikes is surrounded by stations that have less than k bikes (are also quite empty)
			 */
			/*this.addFormula("phi_clust_b",
				new SurroundFormula(
					new ParametricInterval(
						new ParametricExpression() {
							public SignalExpression eval(Map<String, Double> parameters) {
								return new SignalExpression() {
									public double eval(double... variables) {
										return 0;
									}
								};
							}
						},
						new ParametricExpression() {
							public SignalExpression eval(final Map<String, Double> parameters) {
								return new SignalExpression() {
									public double eval(double... variables) {
										return parameters.get("dc");
									}
								};
							}
						}
					),
					new AtomicFormula(
							new ParametricExpression() {
								public SignalExpression eval(Map<String, Double> parameters) {
									return new SignalExpression() {
										public double eval(double... variables) {
											return 1 - variables[getIndex(B_VAR_)]; // eq. B = 0
										}
									};
								}
							}, true),
					new AtomicFormula(
							new ParametricExpression() {
								public SignalExpression eval(final Map<String, Double> parameters) {
									return new SignalExpression() {
										public double eval(double... variables) {
											return parameters.get("k") - variables[getIndex(B_VAR_)]; // eq. B < k
										}
									};
								}
							}, true)),
			null);*/
			/*
			 * PHI_CLUST_S
			 * A station with no bikes is surrounded by stations that have less than k bikes (are also quite empty)
			 */
			/*this.addFormula("phi_clust_s",
				new SurroundFormula(
					new ParametricInterval(
						new ParametricExpression() {
							public SignalExpression eval(Map<String, Double> parameters) {
								return new SignalExpression() {
									public double eval(double... variables) {
										return 0;
									}
								};
							}
						},
						new ParametricExpression() {
							public SignalExpression eval(final Map<String, Double> parameters) {
								return new SignalExpression() {
									public double eval(double... variables) {
										return parameters.get("dc");
									}
								};
							}
						}
					),
					new AtomicFormula(
							new ParametricExpression() {
								public SignalExpression eval(Map<String, Double> parameters) {
									return new SignalExpression() {
										public double eval(double... variables) {
											return 1 - variables[getIndex(S_VAR_)]; // eq. S = 0
										}
									};
								}
							}, true),
					new AtomicFormula(
							new ParametricExpression() {
								public SignalExpression eval(final Map<String, Double> parameters) {
									return new SignalExpression() {
										public double eval(double... variables) {
											return parameters.get("k") - variables[getIndex(S_VAR_)]; // eq. S < k
										}
									};
								}
							}, true)),
			null);*/
	}

}
