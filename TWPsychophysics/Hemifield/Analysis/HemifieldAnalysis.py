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

# Get participant details and parameters
PartInitials = "RH"
Conditions = ['Left', 'Right']

FilePrefix = "HF_" + PartInitials + "*"

DataLocation = '/home/rowanhuxley/Documents/Data_Various/BinRiv/Psychophysics/Hemifield/Data/'
SearchTxt = DataLocation + FilePrefix

# %% Convert dataset to tidy data

# Create list of all file names
AllFileNames =  []
for File in glob.glob(SearchTxt):
    AllFileNames.append(File)

# 
DataFrames = []
for File in AllFileNames:
    df = pd.read_csv(File)
    df = df.reset_index()  # make sure indexes pair with number of rows
    DataFrames.append(df)
    
AllData = pd.concat(DataFrames)

# %% Subtract reaction time from response time

RTPrefix = "RT_" + PartInitials + "*"

DataLocation = '/home/rowanhuxley/Documents/Data_Various/BinRiv/Psychophysics/Contrast-Triggers/Data/'
RTSearchTxt = DataLocation + RTPrefix


# Create list of all file names
RTAllFileNames =  []
for File in glob.glob(RTSearchTxt):
    RTAllFileNames.append(File)

# Create list of all reaction times
RTAll = []
for File in RTAllFileNames:
    df = pd.read_excel(File)
    df = df.reset_index()  # make sure indexes pair with number of rows
    for index, row in df.iterrows():
        row.pop("index")
        row.pop("n")
        row.pop("RT_mean")
        row.pop("RT_std")
        for x in range(row.size):
            RTAll.append(float(row.iloc[x]))

# Get mean and std 
RTMean = float(np.nanmean(RTAll))
RTSE = stats.sem(RTAll)

# Subtract reaction time mean from all response time values
PreResponseTime = AllData["ResponseTime"]

def SubRT(x):
    return x - RTMean
    
PostResponseTime = PreResponseTime.apply(SubRT)

AllData["ResponseTime"] = PostResponseTime

# Calculating propagated error (STILL TO DO)



# %% Removing outliers (Also descriptives at each contrast level)

# Get descriptives for each contrast level
AllCorrect = (AllData[AllData['Direction'] == "right"])
Descriptives = AllCorrect.groupby(["VisibleHemifield"])["ResponseTime"].describe()

# Change all above 3sd into nan
# Right
AllData.loc[(AllData["VisibleHemifield"] == "Right") & (AllData["ResponseTime"] > Descriptives["mean"].iloc[0] * 3)] = np.nan

# Left
AllData.loc[(AllData["VisibleHemifield"] == "Left") & (AllData["ResponseTime"] > Descriptives["mean"].iloc[1] * 3)] = np.nan


print("\n")
print("Outliers Removed")
print("----------------")
print("Right=")
print(AllData.loc[(AllData["VisibleHemifield"] == "Right") & (AllData["ResponseTime"] > Descriptives["mean"].iloc[0] * 3)])
print("\n")
print("Left=")
print(AllData.loc[(AllData["VisibleHemifield"] == "Left") & (AllData["ResponseTime"] > Descriptives["mean"].iloc[1] * 3)])
print("\n")

# %% Stats

# T-test 


stats.ttest_rel(AllData.loc[(AllData["Direction"] == "right") & (AllData["VisibleHemifield"] == "Right"), "ResponseTime"], AllData.loc[(AllData["Direction"] == "right") & (AllData["VisibleHemifield"] == "Left"), "ResponseTime"])
# %% Visualisation
sns.set_theme()

# Wave speed 

# KDE plot
sns.displot(data=AllData[AllData.Direction == "right"], x="ResponseTime", 
            hue='VisibleHemifield', kind='kde', palette="pastel")

# Violin plot
sns.catplot(data=AllData[AllData.Direction == "right"], kind="violin", 
            x="VisibleHemifield", y="ResponseTime", palette="pastel")

# Box plot
sns.catplot(data=AllData[AllData.Direction == "right"], kind="box", 
            x="VisibleHemifield", y="ResponseTime", palette="pastel")


# Over Time anaysis
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


# Trigger rate

# bar chart
sns.countplot(data=AllData, x="Direction", hue = "VisibleHemifield", palette="pastel")

