# analytics-epi
Epidemiological analyses using python, pandas, and lifelines
# data
The data used for this example is the NCCTG Lung Cancer Dataset. It is publicly available and included as part of lifelines. 
The survival of patients with advanced lung cancer from the North Central Cancer Treatment Group is examined. A description of the 
variables included in the data is available [here](http://stat.ethz.ch/R-manual/R-patched/library/survival/html/lung.html). In this example we'll examine the patient characteristics in males vs. females, and then later investigate whether there are survival differences between these groups.
# creating tables
The first part of this example shows how to create tables using functions from [utilities.py](utilities.py). 
The general approach is to store statistics for the table in individual pandas dataframes and then concatenate them together to create the full table for presentation. 
First, lets load the data and import our modules and functions.
```python
import pandas as pd
import numpy as np
from data_analytics_tools.utilities import N4table, meanStd4table, medianIQR4table, freq4table, empty4table, KM_plot_single, KM_plot_double
from matplotlib import pyplot as plt

from lifelines.datasets import load_lung
lungdata = load_lung()
```
Next, we create new variables with appropriate values so the info in our table is formatted coherently.
```python
lungdata['sex_recode'] = np.where(lungdata['sex'] == 1, 'Male', 'Female') 
lungdata['status_recode'] = np.where(lungdata['status'] == 1, 'Alive', 'Dead')
```
We create the vars: *male*, *female*, and *all* to enable the selection of the patient subgroups from lung data. Labels for the table along with the strata variables are stored as a list. Finally, an empty list (*tables*) for storing the descriptive stats for each subgroup is initialized. We'll populate the list *tables* in the next step.
```python
male = (lungdata['sex_recode'] == 'Male')
female = ~male
all = pd.Series([True] * len(lungdata))
strata = [all, male, female]
labels = ['All', 'Male', 'Female']
tables = [] # tables[0] == All, tables[1] = Male, etc.
i=0
```
The functions imported from [utilities.py](utilities.py) are called in the same order as we want the stats to appear in our table.
A for ... loop is used to cycle through each subgroup or stratum of data. In this example, we generate table stats for the full group of patients (All)
and then for males and females. Finally, the individual table stats are concatenated together vertically and stored in the *tables* var, which
is simply a list of dataframes corresonding to each patient group.
```python
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
```
The last step is to concatenate the tables for each subgroup horizontally and then to save the results as a .csv file.
```python
results_folder = "~data_analytics_tools/results/"
result = pd.concat([tables[0], tables[1], tables[2]], axis=1, sort=False)
result.to_csv(results_folder + 'descriptive_table.csv')
```
![alt text](https://github.com/mstokes607/analytics-epi/blob/master/screenshots4example/descriptive_table.png)
# survival analysis
The next part of this example compares overall survival among males vs. females using the Kaplan-Meier survival function. 
First, let's create the necessary vars in order to fit our data.
```python
T = lungdata['time']
lungdata['status_km'] = np.where(lungdata['status'] == 2, 1, 0) # recode status vars for lifelines package
E = lungdata['status_km'] # 1 = dead , # 0 = censored
```
We then import the necessary objects from lifelines. The KaplanMeierFitter is used to fit the survival model to our data and to help plot the survival curves. The logrank_test is used to statistically compare survival among males vs. females. 
```python
from lifelines import KaplanMeierFitter 
# all patients
kmf = KaplanMeierFitter()
kmf.fit(T, E)
from lifelines.statistics import logrank_test
male = (lungdata['sex_recode'] == 'Male') # to stratify population into males and ~males (females)
results = logrank_test(T[male], T[~male], E[male], E[~male], alpha=.99)
```
A call to the function *KM_plot_double* from [utilities.py](utilities.py) creates the survival plot comparing males vs. females with custom styling using matplotlib, including presentation of the log-rank p-value directly on the graph.
```python
KM_plot_double(kmf,strat=male,logrank=results, survtime=T, events=E, xlabel='Days of follow-up', legend_labels = ['Male', 'Female'],
			   ylabel='Survival probability',title='Overall survival in lung cancer patients')
```
