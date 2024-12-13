# Basic analysis and visualisation of the "Contrast triggers" experiment
#
# Based on Naber et al (2009) exp. 1
# Participants view binocular rivalry annuli, a contrast incrase causes a shift
# in dominance. Participants respond with a "right" arrow key press when the 
# wave reaches a desired end point.
#
# RJH 14/11/2024
#
# To do-
# Error propagation


# %% Initialisation

import glob
import pandas as pd
import numpy as np
import seaborn as sns
from scipy.stats import f_oneway
from scipy.stats import ttest_ind

# Get participant details and parameters
PartInitials = "MS"
Conditions = [0.9, 0.75, 0.6]

FilePrefix = "TW_" + PartInitials + "*"

DataLocation = '/home/rowanhuxley/Documents/Data_Various/BinRiv/Psychophysics/Data/ContrastTriggers/'
SearchTxt = DataLocation + FilePrefix

# %% Convert dataset to tidy data

# Create list of all file names
AllFileNames =  []
for File in glob.glob(SearchTxt):
    print(File)
    CSVCheck = File.split(".")
    if CSVCheck[1] == "csv":
        AllFileNames.append(File)


# Move dataframe into list to then concat together
DataFrames = []
for File in AllFileNames:
    df = pd.read_csv(File)
    df = df.reset_index()  # make sure indexes pair with number of rows
    DataFrames.append(df)
    
AllData = pd.concat(DataFrames)

AllData = AllData.rename(columns={"index": "TrialNumber", "Participant_Id": "ParticipantID", "Contrast_Level": "ContrastLevel", "Button_Pressed":"Direction","Response_Time":"ResponseTime"})

# Change the contrast levels to correct values
AllData.loc[AllData["ContrastLevel"] == 0.899999976158, "ContrastLevel"] = 0.9
AllData.loc[AllData["ContrastLevel"] == 0.600000023842, "ContrastLevel"] = 0.6

#cols = ['Participant]

#df.assign(ParticipantID=df[cols].sum(1)).drop(cols, 1)

# %% Subtract reaction time from response time

RTPrefix = "RT_" + PartInitials + "*" 

DataLocation = '/home/rowanhuxley/Documents/Data_Various/BinRiv/Psychophysics/Data/ContrastTriggers/'
RTSearchTxt = DataLocation + RTPrefix


# Create list of all file names
RTAllFileNames =  []
for File in glob.glob(RTSearchTxt):
    CSVCheck = File.split(".")
    if CSVCheck[1] == "csv":
        RTAllFileNames.append(File)

# Create list of all reaction times
RTList = []
for File in RTAllFileNames:
    df = pd.read_csv(File)
    df = df.reset_index()  # make sure indexes pair with number of rows
    RTList.append(df)

RTAll = pd.concat(RTList)
RTAll = RTAll.rename(columns={"0": "ResponseTime"})
# Generate mean reaction time
RTMean = RTAll["ResponseTime"].mean()

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
Descriptives = AllCorrect.groupby(["ContrastLevel"])["ResponseTime"].describe()

# # Change all above 3sd into nan
# print("\n")
# print("Outliers Removed")
# print("----------------")

 #0.9
# print("0.9=")
print(AllData.loc[(AllData["ContrastLevel"] == 0.9) & (AllData["ResponseTime"] > (Descriptives["mean"].iloc[0] + (Descriptives["std"].iloc[0] *2)))])
AllData.loc[(AllData["ContrastLevel"] == 0.9) & (AllData["ResponseTime"] > (Descriptives["mean"].iloc[0] + (Descriptives["std"].iloc[0] *2)))] = np.nan
# print("\n")

 #0.75
# print("0.75=")
print(AllData.loc[(AllData["ContrastLevel"] == 0.75) & (AllData["ResponseTime"] > (Descriptives["mean"].iloc[0] + (Descriptives["std"].iloc[0] *2)))])
AllData.loc[(AllData["ContrastLevel"] == 0.75) & (AllData["ResponseTime"] > (Descriptives["mean"].iloc[0] + (Descriptives["std"].iloc[0] *2)))] = np.nan
# print("\n")

 #0.6
# print("0.6=")
print(AllData.loc[(AllData["ContrastLevel"] == 0.6) & (AllData["ResponseTime"] > (Descriptives["mean"].iloc[0] + (Descriptives["std"].iloc[0] *2)))])
AllData.loc[(AllData["ContrastLevel"] == 0.6) & (AllData["ResponseTime"] > (Descriptives["mean"].iloc[0] + (Descriptives["std"].iloc[0] *2)))] = np.nan
# print("\n")

# Get descriptives for each contrast level
AllCorrect = (AllData[AllData['Direction'] == "right"])
Descriptives = AllCorrect.groupby(["ContrastLevel"])["ResponseTime"].describe()
Median = AllCorrect["ResponseTime"].median()

# %% Visualisation
sns.set_theme()
AllData = AllData.reset_index(drop=True)

# KDE plot
sns.displot(data=AllData[AllData.Direction == "right"], x="ResponseTime", 
            hue='ContrastLevel', kind='kde', palette="pastel")

# Violin plot
sns.catplot(data=AllData[AllData.Direction == "right"], kind="violin", 
            x="ContrastLevel", y="ResponseTime", palette="pastel")

# Box plot
sns.catplot(data=AllData[AllData.Direction == "right"], kind="box", 
            x="ContrastLevel", y="ResponseTime", palette="pastel")


# Over Time anaysis
# Line Graph
for Cond in Conditions:
    Plot = sns.lmplot(data=AllCorrect[AllCorrect.ContrastLevel == Cond], x="TrialNumber", 
                      y="ResponseTime",x_estimator=np.mean, height=8.27, aspect=15/8.27)
    #Plot = sns.catplot(data=AllData[AllData.ContrastLevel == Cond], x="Trial_Number",
    #                   y="ResponseTime", kind="point", height=8.27, aspect=15/8.27)
    Plot.set_axis_labels("Trial Number", "Response Time (s)")
    Plot.fig.suptitle(Cond, fontsize=20, fontweight='bold')
    Plot.fig.subplots_adjust(top=0.95)
    #Plot.set(ylim=(0.1, 4))
    Plot.tick_params(axis='both', which='major', labelsize=14)

AllData = AllData.rename(columns={"TrialNumber": "TrialNumber"})
Plot = sns.catplot(data=AllData, x="TrialNumber", y="ResponseTime", kind="violin", height=8.27, aspect=15/8.27, col="ContrastLevel")
Plot.set_axis_labels("Trial Number", "Response Time (s)")


# Plot over time from pauses 

a = np.linspace(1,5,5)
b = np.linspace(1,5,5)
c = np.linspace(1,5,5)
d = np.linspace(1,2,2)
LinPause = np.concatenate((a, b,c ,d), axis=None)

PauseInt = np.array([])
for x in range(int(len(AllData)/17)):
    PauseInt = np.append(PauseInt,LinPause)

AllData["PauseInt"] = PauseInt

PausesPlot = sns.catplot(data=AllData, x="PauseInt",
                   y="ResponseTime", kind="violin", height=8.27, aspect=15/8.27, col="ContrastLevel")
PausesPlot.set_axis_labels("Trial Number", "Response Time (s)")


# Count the occurrences of values in column A
counts = AllData.groupby(['Direction'])

AllData.groupby('Direction').ContrastLevel.count()
AllData.groupby(["ContrastLevel",'Direction']).ContrastLevel.agg([len])

TriggerRatePlot = sns.catplot(data=AllData.groupby(["ContrastLevel",'Direction']).ContrastLevel.agg([len]), x="ContrastLevel", y= "len", kind="bar",hue='Direction')
TriggerRatePlot.set(ylim=(0, 180))
TriggerRatePlot.set_axis_labels("Contrast Level", "Number of occurrances")



# Group the data by contrast level and get response times
group1 = AllData[AllData['ContrastLevel'] == 0.6]["ResponseTime"]
group2 = AllData[AllData['ContrastLevel'] == 0.75]["ResponseTime"]
group3 = AllData[AllData['ContrastLevel'] == 0.9]["ResponseTime"]

# Perform ANOVA to test for significant differences between group means
f, p = f_oneway(group1, group2, group3)

if p < 0.05:
    print('Reject null hypothesis: at least one group mean is different')
else:
    print('Fail to reject null hypothesis: all group means are the same')
    
    
ttest_ind(group1, group2)
ttest_ind(group2, group3)
ttest_ind(group3, group1)
