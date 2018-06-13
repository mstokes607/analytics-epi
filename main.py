import pandas as pd
import numpy as np
from data_analytics_tools.utilities import N4table, meanStd4table, medianIQR4table, freq4table, empty4table, KM_plot_single, KM_plot_double
from matplotlib import pyplot as plt

# lifelines package comes with sample data sets
from lifelines.datasets import load_lung
lungdata = load_lung()

results_folder = "/Users/michaelstokes/miniconda2/envs/data_analytics_tools/data_analytics_tools/results/"

# recode some variables for clarity
lungdata['sex_recode'] = np.where(lungdata['sex'] == 1, 'Male', 'Female') 
lungdata['status_recode'] = np.where(lungdata['status'] == 1, 'Alive', 'Dead')

# analyses for all patients and my subgroups
male = (lungdata['sex_recode'] == 'Male')
female = ~male
all = pd.Series([True] * len(lungdata))
strata = [all, male, female]
labels = ['All', 'Male', 'Female']
tables = [] # tables[0] == All, tables[1] = Male, etc.
i=0

for group in strata:  
	row1 = N4table(lungdata[group], statlabel='Number of patients', groupname=labels[i])
	row2 = meanStd4table(lungdata['age'][group], decimals=1, label='Age', statlabel='Mean (SD)', groupname=labels[i])
	row3 = medianIQR4table(lungdata['age'][group], decimals=1, statlabel='Median (IQR)', groupname=labels[i])
	row4 = freq4table(lungdata['sex_recode'], group=group, decimals=1, label='Gender', groupname=labels[i])
	row5 = meanStd4table(lungdata['wt.loss'][group], decimals=1, label='Weight loss', statlabel='Mean (SD)', groupname=labels[i])
	row6 = freq4table(lungdata['ph.ecog'],group=group, decimals=4, label='ECOG performance (physician)', groupname=labels[i])
	row7 = freq4table(lungdata['ph.karno'],group=group, decimals=4, label='Karnofsky performance (physician)', groupname=labels[i])
	row8 = freq4table(lungdata['pat.karno'],group=group, decimals=4, label='Karnofsky performance (patient)', groupname=labels[i])
	row9 = meanStd4table(lungdata['meal.cal'][group], decimals=1, label='Calories consumed at meals', statlabel='Mean (SD)', groupname=labels[i])
	row10 = medianIQR4table(lungdata['meal.cal'][group], decimals=1, statlabel='Median (IQR)', groupname=labels[i])
	row11 = meanStd4table(lungdata['wt.loss'][group], decimals=1, label='Weight loss in last 6 months', statlabel='Mean (SD)', groupname=labels[i])
	row12 = freq4table(lungdata['status_recode'],group=group, decimals=1, label='Patient status', groupname=labels[i])
	empty_row = empty4table(groupname=labels[i])
	strata_table = pd.concat([row1, empty_row, row2, row3, empty_row, row4, empty_row, 
                     row5, empty_row, row6, empty_row, row7, empty_row, row8, empty_row, row9, row10, empty_row,
                     row11, empty_row, row12])
	tables.append(strata_table)
	i += 1

# append tables together (must be all the same length)
result = pd.concat([tables[0], tables[1], tables[2]], axis=1, sort=False)
result.to_csv(results_folder + 'descriptive_table.csv')

# kaplan-meier analyses ...
# overall
T = lungdata['time']
lungdata['status_km'] = np.where(lungdata['status'] == 2, 1, 0) # recode status vars for lifelines package
E = lungdata['status_km'] # 1 = dead , # 0 = censored

from lifelines import KaplanMeierFitter # fit KM survival model to the data
# all patients
kmf = KaplanMeierFitter()
kmf.fit(T, E)
KM_plot_single(kmf, xlabel='Days of follow-up', ylabel='Survival probability', title='Overall survival in lung cancer patients')

# stratify by sex
from lifelines.statistics import logrank_test
male = (lungdata['sex_recode'] == 'Male') # to stratify population into males and ~males (females)
results = logrank_test(T[male], T[~male], E[male], E[~male], alpha=.99)

KM_plot_double(kmf,strat=male,logrank=results, survtime=T, events=E, xlabel='Days of follow-up', legend_labels = ['Male', 'Female'],
			   ylabel='Survival probability',title='Overall survival in lung cancer patients')
			   
# Cox PH regression
from lifelines import CoxPHFitter

cph = CoxPHFitter()

lungdata['age_grp'] = np.where(lungdata['age'] >= 65, 1, 0)
lungdata['sex'] = np.where(lungdata['sex'] == 1, 1, 2)

lung_cph = lungdata[['time', 'status_km', 'sex', 'age', 'wt.loss']] # only keep vars needed for model
lung_cph = lung_cph[lung_cph['wt.loss'].notna()] # drop nan values so the model can converge

cph.fit(lung_cph, 'time', event_col='status_km')
cph.print_summary()

# extract stats for the multivariate table & save as .csv format
cph.summary.to_csv(results_folder + 'multivariate_table.csv')
			   
# miscellaneous ... 
# look at the survival table
from lifelines.utils import survival_table_from_events

table = survival_table_from_events(T, E)
print(table.head())
			   
