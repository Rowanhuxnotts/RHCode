# Make Tidy
# 
# Temporary script that will turn the default output from 
# the psychopy trial handeler into tidy data format. 
# Planning to turn this idea into a module with functions to use in future.
# Still very janky when switching between reaction time and travelling wave task...
#
# Outputs .csv file in tidy data format

import sys
import pandas as pd
import glob
import numpy as np

BackupCheck = input("Is the data backed up elsewhere? yes/no:\n").lower()
BackupCheck = BackupCheck.lower()

if BackupCheck == "yes":
    pass
elif BackupCheck == "no":
    sys.exit("Then back it up!")
else:
    sys.exit("Invalid response, expecting yes or no")
    

# Asks for the files experiment name and participant initials
PartInitials = input("Participant initials?\n").upper()
DataLocation = input("Data location?\n")
ExperimentName = input("Experiment initials?\n")

if DataLocation[-1] != "/":
    DataLocation = DataLocation + "/"

FilePrefix = ExperimentName + "_" + PartInitials + "*"
Conditions = [0.9, 0.75, 0.6]
SearchTxt = DataLocation + FilePrefix

# Uses above information to pull list of data
# %%
def loadExcelData(filename, ExperimentInitials):
    """
    loadExcelData - load in 1 excel file and return the SepSeries    
    """
    SepSeries = []
    print(filename)
    df = pd.read_excel(filename)
    df = df.reset_index()  # make sure indexes pair with number of rows
    if ExperimentInitials == "TW":
        for index, row in df.iterrows(): 
            row.pop("index")
            row.pop("ContrastLevel_mean")
            row.pop("ContrastLevel_std")
            TravelTimeMean = row.pop("TravelTime_mean")
            TravelTimeSd = row.pop("TravelTime_std")
            SepSeries.append(row)
    else:
        for index, row in df.iterrows(): 
            row.pop("index")
            row.pop("n")
            row.pop("RT_mean")
            row.pop("RT_std")
            SepSeries.append(row)
    return SepSeries


    
def tidyUpSeries(SepSeries, PartInitials):
    """
    tidyUpSeries - reorganises the very long 1d series 
                   into a table with rows = trial, columns = variables

    used to save out files in tidy format, so we can opt into pandas goodness.
    """
    # make 3 columns (empty for now)
    ContLevel = pd.Series(name = "Contrast Level")
    ButtonPress = pd.Series(name = "Button_Pressed")
    ResponseTime = pd.Series(name = "Response_Time")
    # at this point for 1 file... expect x to be 3
    #assert len(SepSeries) == 3, f"Uhoh size should be 3, but is {len(SepSeries)}"
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
    tidyData = pd.DataFrame({"ParticipantID" : PartInits,
                             "ContrastLevel" : ContLevel,
                             "Direction" : ButtonPress, 
                             "ResponseTime" : ResponseTime});
    return tidyData 

def SaveOutCSV(Data, FileName):
    """
    SaveOutCSV- Takes dataframe and file namea nd outputs to csv file in 
                current directory. Will strip previous extension if using one.
                
    Parameters
    ----------
    Data : Pandas Dataframe
        Any dimentions.
    FileName : String
        Name that the file will be saved as. Can also include path.

    Returns
    -------
    None.
    
    """
    OutputFormat = ".csv"
    FileName = FileName.split(".")
    FileName = FileName[0] + OutputFormat
    Data.to_csv(FileName, index=False)

# Create list of all file names
AllFileNames =  []
for File in glob.glob(SearchTxt):
    AllFileNames.append(File)

# load in, tidy up, and output datafile
for CurFile in AllFileNames:
    CSVCheck = CurFile.split(".")
    if CSVCheck[1] == "csv":
        pass
    else:
        if ExperimentName != "RT":
            SepSeries = loadExcelData(CurFile, ExperimentName)
    #if ExperimentName == "RT":
    #    SaveOutCSV(SaveOutCSV, CurFile)
    # else:
            TidySeries = tidyUpSeries(SepSeries, PartInitials)
            TidySeries['Direction'] = TidySeries['Direction'].map(lambda x: x.lstrip("['").rstrip("']"))
            SaveOutCSV(TidySeries, CurFile)
        else:
            SepSeries = loadExcelData(CurFile, ExperimentName)
            SepSeries = SepSeries[0]
            SepSeries.to_csv(CurFile, index=False)
    

