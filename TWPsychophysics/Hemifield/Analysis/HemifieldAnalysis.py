# Basic analysis and visualisation of the "Hemifield" experiment
#
# Binouclar rivalry travelling waves experiment. Participants are shown 
# differing annuli in either the left or right side of visual field. They 
# respond with right arrow when wave reaches bottom of annuli. (left if the 
# wave fails)
#
# RJH 19/11/2024
#
# To do-
# Trigger rate analysis

# %% Initialisation

import glob
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns
from scipy.stats import f_oneway
from scipy.stats import ttest_ind

# Participant details and parameters(Maybe change to input fields with default)
PartInitials = "RH"
Conditions = ['Left', 'Right']

FilePrefix = "HF_" + PartInitials + "*"

DataLocation = '/home/rowanhuxley/Documents/Data_Various/BinRiv/Psychophysics/Hemifield/Data/'
SearchTxt = DataLocation + FilePrefix

# %% Read in data and make one dataframe called "AllData" to work off

# Create list of all file names
AllFileNames =  []
for File in glob.glob(SearchTxt):
    CSVCheck = File.split(".")
    if CSVCheck[1] == "csv":
        AllFileNames.append(File)
        
DataFrames = []
for File in AllFileNames:
    df = pd.read_csv(File)
    df = df.reset_index()  # make sure indexes pair with number of rows
    DataFrames.append(df)
    
AllData = pd.concat(DataFrames)

# %% Subtract reaction time from response time to give an estimate of true
#    wave travel time 

RTPrefix = "RT_" + PartInitials + "*"

DataLocation = '/home/rowanhuxley/Documents/Data_Various/BinRiv/Psychophysics/Contrast-Triggers/Data/'
RTSearchTxt = DataLocation + RTPrefix


# Pull all reaction time files and concat into a main dataframe "RTAll"
RTAllFileNames =  []
for File in glob.glob(RTSearchTxt):
    CSVCheck = File.split(".")
    if CSVCheck[1] == "csv":
        RTAllFileNames.append(File)

RTAll = []
for File in RTAllFileNames:
    df = pd.read_csv(File)
    df = df.reset_index()  # make sure indexes pair with number of rows
    RTAll.append(df)
    
RTAll = pd.concat(RTAll)

# Had an issue with a column name being 0 so this fixes that
RTAll = RTAll.rename(columns={"0": "ResponseTime"})

# Calculate mean reaction time to subtract from main trial response times
RTMean = RTAll["ResponseTime"].mean()
PreResponseTime = AllData["ResponseTime"]

# There might be a more eligant way than a function but it works
def SubRT(x):
    return x - RTMean
PostResponseTime = PreResponseTime.apply(SubRT)

AllData["ResponseTime"] = PostResponseTime

# Calculating propagated error (STILL TO DO)



# %% Removing outliers (Also gives descriptives at each contrast level)

# Get descriptives for each contrast level
AllCorrect = (AllData[AllData['Direction'] == "right"])
Descriptives = AllCorrect.groupby(["VisibleHemifield"])["ResponseTime"].describe()

# Change all response times above 3sd into nan
# Right
AllData.loc[(AllData["VisibleHemifield"] == "Right") & (AllData["ResponseTime"] > (Descriptives["mean"].iloc[0] + (Descriptives["std"].iloc[0] *3)))] = np.nan

# Left
AllData.loc[(AllData["VisibleHemifield"] == "Left") & (AllData["ResponseTime"] > (Descriptives["mean"].iloc[0] + (Descriptives["std"].iloc[0] *3)))] = np.nan

# For sanity checking 
print("\n")
print("Outliers Removed")
print("----------------")
print("Right=")
print(AllData.loc[(AllData["VisibleHemifield"] == "Right") & (AllData["ResponseTime"] > (Descriptives["mean"].iloc[0] + (Descriptives["std"].iloc[0] *3)))])
print("\n")
print("Left=")
print(AllData.loc[(AllData["VisibleHemifield"] == "Left") & (AllData["ResponseTime"] > (Descriptives["mean"].iloc[0] + (Descriptives["std"].iloc[0] *3)))])
print("\n")

# %% Stats

# T-test comparing response times between hemifields
RightResp = AllData[AllData['VisibleHemifield'] == "Right"]["ResponseTime"]
LeftResp = AllData[AllData['VisibleHemifield'] == "Left"]["ResponseTime"]

ttest_ind(RightResp, LeftResp)

# %% Visualisation
sns.set_theme() # Resets from other projects previously ran

# Wave speed-

# KDE plot
sns.displot(data=AllData[AllData.Direction == "right"], x="ResponseTime", 
            hue='VisibleHemifield', kind='kde', palette="pastel")

# Violin plot
sns.catplot(data=AllData[AllData.Direction == "right"], kind="violin", 
            x="VisibleHemifield", y="ResponseTime", palette="pastel")

# Box plot
sns.catplot(data=AllData[AllData.Direction == "right"], kind="box", 
            x="VisibleHemifield", y="ResponseTime", palette="pastel")


# Wave speed over time-
# Line Graph
for Cond in Conditions:
    Plot = sns.lmplot(data=AllData[AllData.VisibleHemifield == Cond], x="index", 
                      y="ResponseTime",x_estimator=np.mean, height=8.27, aspect=15/8.27)
    #Plot = sns.catplot(data=AllData[AllData.Contrast_Level == Cond], x="Trial_Number",
    #                   y="Response_Time", kind="point", height=8.27, aspect=15/8.27)
    Plot.set_axis_labels("Trial Number", "Response Time (s)")
    Plot.fig.suptitle(Cond, fontsize=20, fontweight='bold')
    Plot.fig.subplots_adjust(top=0.95)
    #Plot.set(ylim=(0.65, 2))
    Plot.tick_params(axis='both', which='major', labelsize=14)
    

AllData = AllData.reset_index()
Plot = sns.catplot(data=AllData, x="index", y="ResponseTime", kind="violin", 
                   height=8.27, aspect=15/8.27, col="VisibleHemifield")
Plot.set_axis_labels("Trial Number", "Response Time (s)")


# Trigger rate-

# Bar chart
m = sns.countplot(data=AllData, x="VisibleHemifield", hue = "Direction", palette="pastel")
m.set_axis_labels("Visible Hemifield", "Number of occurances")