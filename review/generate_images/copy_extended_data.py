import os

# copy stations list from simulation
os.system('cp ../../extended_simulation/stations.csv baseline_comparison/stations.csv')
os.system('cp ../../extended_simulation/stations.csv baseline_empty_full/stations.csv')
os.system('cp ../../extended_simulation/stations.csv prob_comparison/stations.csv')

# copy files for baseline_comparison
os.system('cp ../../real_analysis/Formulas/phi_dist.csv baseline_comparison/real_phi_dist.csv')
os.system('cp ../../extended_simulation/Planned_Experiments/aug_baseline/Formulas/phi_prob.csv baseline_comparison/baseline_phi_prob.csv')

# copy files for baseline_empty_full
os.system('cp ../../extended_simulation/Planned_Experiments/aug_baseline/Formulas/phi_empty.csv baseline_empty_full/phi_empty.csv')
os.system('cp ../../extended_simulation/Planned_Experiments/aug_baseline/Formulas/phi_full.csv baseline_empty_full/phi_full.csv')

# copy files for prob_comparison
os.system('cp ../../extended_simulation/Planned_Experiments/aug_baseline_latent_demand/Formulas/phi_prob.csv prob_comparison/0_baseline_ld.csv')
os.system('cp ../../extended_simulation/Planned_Experiments/aug_baseline_latent_demand_opt/Formulas/phi_prob.csv prob_comparison/1_baseline_ld_opt.csv')
os.system('cp ../../extended_simulation/Planned_Experiments/aug_inc_both_700_100/Formulas/phi_prob.csv prob_comparison/2_inc_700_100.csv')
os.system('cp ../../extended_simulation/Planned_Experiments/aug_inc_both_700_50/Formulas/phi_prob.csv prob_comparison/3_inc_700_50.csv')
os.system('cp ../../extended_simulation/Planned_Experiments/aug_inc_both_700_25/Formulas/phi_prob.csv prob_comparison/4_inc_700_25.csv')
os.system('cp ../../extended_simulation/Planned_Experiments/aug_inc_both_600_50/Formulas/phi_prob.csv prob_comparison/5_inc_600_50.csv')
os.system('cp ../../extended_simulation/Planned_Experiments/aug_inc_both_500_50/Formulas/phi_prob.csv prob_comparison/6_inc_500_50.csv')
os.system('cp ../../extended_simulation/Planned_Experiments/aug_static_opt/Formulas/phi_prob.csv prob_comparison/7_static.csv')
os.system('cp ../../extended_simulation/Planned_Experiments/aug_static_inc_opt/Formulas/phi_prob.csv prob_comparison/8_static_inc.csv')