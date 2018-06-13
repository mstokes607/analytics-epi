# create tables for data analysis
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# functions to create tables
# idea is to generate statistics and store each stat in a separate dataframe
# tables for study groups are created by concatenating the stats stored in individual frames
# tables of study groups can then be merged together to create a table, presenting data for multiple groups 

def N4table(myframe, statlabel, groupname):
	myNtotal = len(myframe)
	myNtotal = pd.DataFrame([myNtotal],[statlabel], columns=[groupname])
	return myNtotal

def meanStd4table(mycolumn, decimals, label, statlabel, groupname):
	mymean = str(round(mycolumn.mean(), decimals))
	mystd = str(round(mycolumn.std(), decimals))
	myN = str(mycolumn.count())
	number = pd.DataFrame([myN],['N nonmissing'],columns=[groupname])
	mean_std = mymean + " (" + mystd + ")"
	mean_std = pd.DataFrame([mean_std],[statlabel],columns=[groupname])
	# add row for the variable label
	label_row = pd.DataFrame(index=[label],columns=[groupname])
	label_row = label_row.fillna('')
	result = pd.concat([label_row, number, mean_std]) # index is reset to create common 'index' column for merging tables
	return result
	
def medianIQR4table(mycolumn, decimals, statlabel, groupname):
	mymedian = str(round(mycolumn.median(), decimals))
	myquantiles = mycolumn.quantile([.25, .75]).tolist()
	result = mymedian + " (" + str(myquantiles[0]) + ", " + str(myquantiles[1]) + ")"
	return pd.DataFrame([result],[statlabel],columns=[groupname])
	
def freq4table(mycolumn, decimals, label, groupname, group=[]):
	if len(group) == 0:
		myfreq = mycolumn.value_counts(normalize=True, dropna=False).to_frame(name='Pct')
		mynum = mycolumn.value_counts(dropna=False).to_frame(name='N')	
		all_cats = mycolumn.value_counts().index.values	
	elif group.empty == False:
			myfreq = mycolumn[group].value_counts(normalize=True, dropna=False).to_frame(name='Pct')
			mynum = mycolumn[group].value_counts(dropna=False).to_frame(name='N')
			all_cats = mycolumn.value_counts().index.values
	result = mynum.join(myfreq) # join stats
	result['Pct'] = result['Pct'].round(decimals) * 100 # convert to decimal to percent
	result[groupname] = result['N'].apply(str) + ' ' + '(' + result['Pct'].apply(str) + ')'
	# add row for the variable label
	label_row = pd.DataFrame(index=[label], columns=[groupname])
	label_row = label_row.fillna('')
	result = result[groupname].to_frame(name=groupname)
	result = result.reindex(all_cats).sort_index()
	result = pd.concat([label_row, result])
	return result
	
def empty4table(groupname):
	empty_row = pd.DataFrame(index=[''], columns=[groupname])
	empty_row = empty_row.fillna('')
	return empty_row
	
# functions for lifeline plots
def KM_plot_single(kmfobject, xlabel=None, ylabel=None, title=None):
	ax = plt.subplot(111)
	ax = kmfobject.plot(ax=ax)
	if xlabel != None: plt.xlabel(xlabel)
	if ylabel != None: plt.ylabel(ylabel)
	if title != None: plt.title(title)
	ax.get_legend().remove()
	plt.show()
	
def KM_plot_double(kmfobject, strat, logrank, survtime, events, legend_labels, xlabel=None, ylabel=None, title=None):
	ax = plt.subplot(111)
	plt.ylim(0, 1)
	kmfobject.fit(survtime[strat], event_observed=events[strat], label=legend_labels[0])
	kmfobject.plot(ax=ax, ci_force_lines=False)
	kmfobject.fit(survtime[~strat], event_observed=events[~strat], label=legend_labels[1])
	kmfobject.plot(ax=ax, ci_force_lines=False)
	if title != None : plt.title(title)
	if xlabel != None: plt.xlabel(xlabel)
	if ylabel != None: plt.ylabel(ylabel)
	plt.legend(prop={'size': 8}, frameon=False)
	ax.text(max(survtime)-(max(survtime)*0.35), 0.70, 'log-rank p=' + str(round(logrank.p_value,4)), fontsize=8)
	plt.show()
	



