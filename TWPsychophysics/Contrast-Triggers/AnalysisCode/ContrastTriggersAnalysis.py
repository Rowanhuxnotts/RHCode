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
# Outlier removal doesn't seem to be working...

# %% Initialisation

import glob
import pandas as pd
import numpy as np
from scipy import stats
import seaborn as sns

# Get participant details and parameters
PartInitials = "RH"
Conditions = [0.9, 0.75, 0.6]

FilePrefix = "TW_" + PartInitials + "*"

DataLocation = '/home/rowanhuxley/Documents/Data_Various/BinRiv/Psychophysics/Contrast-Triggers/Data/'
SearchTxt = DataLocation + FilePrefix

# %% Convert dataset to tidy data

# Create list of all file names
AllFileNames =  []
for File in glob.glob(SearchTxt):
    AllFileNames.append(File)
    
# Create list of all data rows
SepSeries = []

for File in AllFileNames:
    df = pd.read_excel(File)
    df = df.reset_index()  # make sure indexes pair with number of rows
    for index, row in df.iterrows():
        row.pop("index")
        row.pop("ContrastLevel_mean")
        row.pop("ContrastLevel_std")
        TravelTimeMean = row.pop("TravelTime_mean")
        TravelTimeSd = row.pop("TravelTime_std")
        SepSeries.append(row)


# Seperate each real column to seperate series
ContLevel = pd.Series(name = "Contrast Level")
ButtonPress = pd.Series(name = "Button_Pressed")
ResponseTime = pd.Series(name = "Response_Time")
for x in SepSeries:
    ContLevel = pd.concat([ContLevel, x.iloc[1:18]])
    ButtonPress = pd.concat([ButtonPress, x.iloc[18:35]])
    ResponseTime = pd.concat([ResponseTime, x.iloc[35:52]])

## Create dataframe with each row being a trial
# Issues with duplicate labels so have to change series to np array
ContLevel = ContLevel.to_numpy()
ButtonPress = ButtonPress.to_numpy()
ResponseTime = ResponseTime.to_numpy()

# Create 1d Numpy array of participant intials
PartInits = np.full(len(ContLevel), PartInitials)

# Recombine data into tidy format
ColumnLabels = ["Participant_Id", "Contrast_Level", "Button_Pressed", "Response_Time"]
AllData = pd.DataFrame([PartInits, ContLevel, ButtonPress, ResponseTime], index = ColumnLabels)
AllData = AllData.transpose()

# Change the contrast levels to correct values
AllData.loc[AllData["Contrast_Level"] == 0.899999976158, "Contrast_Level"] = 0.9
AllData.loc[AllData["Contrast_Level"] == 0.600000023842, "Contrast_Level"] = 0.6

# Add column for trial number

LinTrials = np.linspace(1,17,17)
TrialNumbers = np.array([])
for x in range(int(len(AllData)/17)):
    TrialNumbers = np.append(TrialNumbers,LinTrials)

AllData["Trial_Number"] = TrialNumbers

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
PreResponseTime = AllData["Response_Time"]

def SubRT(x):
    return x - RTMean
    
PostResponseTime = PreResponseTime.apply(SubRT)

AllData["Response_Time"] = PostResponseTime

# Calculating propagated error (STILL TO DO)



# %% Removing outliers (Also descriptives at each contrast level)

# Get descriptives for each contrast level
AllCorrect = (AllData[AllData['Button_Pressed'] == "['right']"])
Descriptives = AllCorrect.groupby(["Contrast_Level"])["Response_Time"].describe()

# Change all above 3sd into nan
print("\n")
print("Outliers Removed")
print("----------------")

#0.9
print("0.9=")
print(AllData.loc[(AllData["Contrast_Level"] == 0.9) & (AllData["Response_Time"] > Descriptives["mean"].iloc[0] * 3)])
AllData.loc[(AllData["Contrast_Level"] == 0.9) & (AllData["Response_Time"] > Descriptives["mean"].iloc[0] * 3)] = np.nan
print("\n")

#0.75
print("0.75=")
print(AllData.loc[(AllData["Contrast_Level"] == 0.75) & (AllData["Response_Time"] > Descriptives["mean"].iloc[1] * 3)])
AllData.loc[(AllData["Contrast_Level"] == 0.75) & (AllData["Response_Time"] > Descriptives["mean"].iloc[1] * 3)] = np.nan
print("\n")

#0.6
print("0.6=")
print(AllData.loc[(AllData["Contrast_Level"] == 0.6) & (AllData["Response_Time"] > Descriptives["mean"].iloc[2] * 3)])
AllData.loc[(AllData["Contrast_Level"] == 0.6) & (AllData["Response_Time"] > Descriptives["mean"].iloc[2] * 3)] = np.nan
print("\n")


# %% Visualisation
sns.set_theme()

# KDE plot
sns.displot(data=AllData[AllData.Button_Pressed == "['right']"], x="Response_Time", 
            hue='Contrast_Level', kind='kde', palette="pastel")

# Violin plot
sns.catplot(data=AllData[AllData.Button_Pressed == "['right']"], kind="violin", 
            x="Contrast_Level", y="Response_Time", palette="pastel")

# Box plot
sns.catplot(data=AllData[AllData.Button_Pressed == "['right']"], kind="box", 
            x="Contrast_Level", y="Response_Time", palette="pastel")


# Over Time anaysis
# Line Graph
for Cond in Conditions:
    Plot = sns.lmplot(data=AllData[AllData.Contrast_Level == Cond], x="Trial_Number", 
                      y="Response_Time",x_estimator=np.mean, height=8.27, aspect=15/8.27)
    #Plot = sns.catplot(data=AllData[AllData.Contrast_Level == Cond], x="Trial_Number",
    #                   y="Response_Time", kind="point", height=8.27, aspect=15/8.27)
    Plot.set_axis_labels("Trial Number", "Response Time (s)")
    Plot.fig.suptitle(Cond, fontsize=20, fontweight='bold')
    Plot.fig.subplots_adjust(top=0.95)
    Plot.set(ylim=(0.65, 2))
    Plot.tick_params(axis='both', which='major', labelsize=14)
    
    
Plot = sns.catplot(data=AllData, x="Trial_Number",
                   y="Response_Time", kind="violin", height=8.27, aspect=15/8.27, col="Contrast_Level")
Plot.set_axis_labels("Trial Number", "Response Time (s)")


