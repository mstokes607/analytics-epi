# analytics-epi
Epidemiological analyses using python, pandas, and lifelines
# data
The data used for this example is the NCCTG Lung Cancer Dataset. It is publicly available and included as part of lifelines. 
The data examines survival in patients with advanced lung cancer from the North Central Cancer Treatment Group. A description of the 
variables included in the data is available [here](http://stat.ethz.ch/R-manual/R-patched/library/survival/html/lung.html). 
# creating tables
In the first part of this example we will create tables using functions from [utilities.py](analytics-epi/utilities.py). 
The statistics for the table are stored in individual pandas dataframes and then concatenated together to create the table.
First, lets load the data and import our modules and functions.
```python
import pandas as pd
import numpy as np
from data_analytics_tools.utilities import N4table, meanStd4table, medianIQR4table, freq4table, empty4table, KM_plot_single, KM_plot_double
from matplotlib import pyplot as plt

from lifelines.datasets import load_lung
lungdata = load_lung()
```
Next, we'll create new variables with appropriate values so the data in our table makes sense
```python
lungdata['sex_recode'] = np.where(lungdata['sex'] == 1, 'Male', 'Female') 
lungdata['status_recode'] = np.where(lungdata['status'] == 1, 'Alive', 'Dead')
```
The functions imported from [utilities.py](analytics-epi/utilities.py) are called in the order that we want to view the stats in the table.
A for ... loop is used to cycle through each stratum of data. In this example, we generate table stats for the full group of patients (All)
and for males vs. females. Finally, the individual table stats are concatenated together vertically and stored in the tables var, which
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
