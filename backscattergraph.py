import numpy
import pandas as pd 
import seaborn as sns 
import os 
import scipy 
from scipy import stats 
from openpyxl import Workbook 
import glob 
import matplotlib.pyplot as plt 
from matplotlib.pyplot import show 
import re 
import argparse




parser = argparse.ArgumentParser(description = "input - Zonal statistics in \
json file format of samples with a class identifier of sentinel-1 bands, output \
time series graph, and boxplot of the difference in median values")
parser.add_argument("-i", "--infolder", type = str, metavar = "", required = True, help = "Folder containing the json files")
parser.add_argument("-o", "--outfolder", type = str, metavar = "", required = True,  help= "Folder where the boxplots and \
final time serie's graph will be stored")
parser.add_argument("-t", "--title", type = str, metavar = "", required = True, help="Title of the time series graph")
parser.add_argument("-b", "--band", type = str, metavar = "", required = True, help= "S1 Band")
args = parser.parse_args()

def boxplot_name(path):
	"""Creates a boxplot name from the 
	json filename"""
	prelim_name = os.path.basename(path)
	boxplt_name = prelim_name.replace(".json", "")
	return boxplt_name

def cleaning_data(df):
	"""Eliminate all entries with negative values"""
	df = df[(df["mean"]>0)]
	return df 

def box_plots(df, plot_name, output_path):
	"""Create boxplots, comparing the mean of two classes"""
	fig_name = output_path + "/" + plot_name + ".png"
	if os.path.exists(fig_name):
		print("Boxplot {!s} already exists".format(plot_name))
	else:
		try:
			print("Creating boxplots for {!s}".format(plot_name))
			boxplot = sns.boxplot(x=df["cid"], y=df["mean"], 
				palette= "Blues").set_title(plot_name)
			figure = boxplot.get_figure()
			figure.savefig(fig_name, dpi=500)
		except ValueError:
			print("There is a problem with the min() value as empty sequency")

def summary_stats(df, plot_name, band):
	"""Calculate a summary of the time feature statistic per class and returns a line
	with such summary, a line per time feature"""
	c = {}
	cid = df["cid"].unique()
	classes = ["cl_" + "0" + str(x) for x in cid]
	cid_int = cid.tolist()
	dictionary = dict(zip(cid_int, classes))
	match = re.search(r"\d{4}\d{2}\d{2}",plot_name)
	date=match.group()
	c["date"] = date
	c["band"] = band 

	for k, v in dictionary.items():
		name = str(v) + "_mean"
		mean = df[df["cid"] == k]["mean"]
		mean_desc = mean.describe()["mean"]
		mean_all = mean_desc.mean()
		c[name] = mean_all

	return c

def df_to_csv(df, outfolder, title):
	"""Stores the information contained in a dataframe in a csv file"""
	csv = outfolder + "/" + title + ".csv"
	df.to_csv(csv)
	return csv
	

def time_feature_stats(infolder, outfolder, title, band):
	"""Create a csv file containing the stats summary 
	of all the time features contained in the json file"""
	new_df = []
	json_files = [os.path.join(root, file) for root, subdirs, files
	in os.walk(infolder) for file in files if file.endswith(".json")]


	for json in json_files:
		print(json)
		df = pd.read_json(json)
		# creating database
		columns = list(df.columns.values) # defining columns
		classes = df["cid"].unique().tolist() # defining the classes
		bxplt = boxplot_name(json) # creating boxplot name
		df = cleaning_data(df) # cleaning no data values from df
		box_plots(df, bxplt, outfolder) # creating boxplot for time feature
		stats = summary_stats(df, bxplt, band)# summaring statistics per class per feature
		new_df.append(stats)# storing the new entries in the new dataframe

	df = pd.DataFrame(new_df)
	csv = df_to_csv(df, outfolder, title)
	mk_graph(csv, title)



def mk_graph(csv, Title):
	"""Make the time series graph from the information of a time series dataframe"""
	raw_df = pd.read_csv(csv)
	cols = raw_df.columns.values
	classes = []
	for col in cols:
		[classes.append(col) for col in cols if col.startswith("cl")]
	cols = list(set(classes))
	sns.set()
	raw_df[cols].plot()
	plt.title(Title, fontsize = 14)
	plt.xlabel("Date", fontsize=10)
	plt.ylabel("Backscatter values in db", fontsize=10)
	plt.xticks(range(len(raw_df)), raw_df["date"], rotation=90)
	plt.tick_params(axis="both", which="major", labelsize=7)
	plt.show()


if __name__ == '__main__':
	time_feature_stats(args.infolder, args.outfolder, args.title, args.band)
	








