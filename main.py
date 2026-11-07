# IMPORTING THE LIBRARIES:
import os 
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import io

#===============================================================================
# SETTING UP ENVIRONMENT FOR SHEET READING (GOOGLE SHEETS API):
# Loading .env variables
load_dotenv() # reads variables from a .env file and sets them in os.environ
sheet_id = os.getenv("sheet_id")
study_stats_key = os.getenv("study_stats_key")

# Defines the scope of access for the code
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Gets the service account file with key.json information (this is secret)
SERVICE_ACCOUNT_FILE = "/Users/oscar/Desktop/Hobbies/Personal project/StudyStats/key.json" 

# Creating credentials from service acconut
credentials = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes = SCOPES)

# Creating the client for sheets with version 4 and credentials specified
service = build('sheets', 'v4', credentials = credentials)

# Declaring the sheet / creating an object to handle all the operations
sheets = service.spreadsheets()

# Using a test range on only some tasks in the dataset to read
subject = 'A4:Z'

# Intializing sheet reading variable(?) by using the sheets object
sheet_read = sheets.values().get(spreadsheetId = sheet_id, range = subject).execute()

print("===== Initial Sheet Read:====")
print(sheet_read)
print("====================\n")

values = sheet_read.get('values', [])
# Looping and printing all data in given range
for row in values:
    print(row)


#===============================================================================
# CREATING NEW LOOP TO GET ALL OPTIONS IN SUBJECT COLUMN AVAILABLE:
# Doing an API call to get the values in one specific column
subject_read = sheets.get(
    spreadsheetId = sheet_id,
    ranges = ["A6:A6"], # This value is the first instance of a dropdown menu 
    # for subject. This should not be changed under the ideal condition, but 
    # further processing may need to be done in the future to prevent catch 
    # error.
    includeGridData = True, # Including crucial info beyond just metadata
    fields = "sheets(data(rowData(values(dataValidation))))", # adds a field 
    # mask that limits grid data to only data validation as a part of the 
    # dropdown menu rather than also color, font etc.
).execute()

# The response is nested, so this walks down it: first sheet, first data block 
# (one per requested range), first row, first cell. Since we asked for a single 
# cell, each level has one entry. .get("dataValidation") returns None instead 
# of crashing if the cell has no dropdown.

# Printing subject read for visualization 
print("===== Subject Read:====")
print(subject_read)
print("====================\n")


cell = subject_read["sheets"][0]["data"][0]["rowData"][0]["values"][0] 
# Response of subject_read is heavily nested. This walks it down through the 
# first sheet, the first data, the frst rowData, first cell. Because we only 
# requested for one cell, it is very simple to process so we just define it as 
# the first index (0th index) of each category.

# Printing cell for visualization 
print("======= Cell:=======")
print(cell)
print("====================\n")


rule = cell.get("dataValidation") # Gets the data validation part of the 
# "cell", up till here we are just extracting data step by step

# Printing rule for visualization 
print("======= Rule:=======")
print(rule)
print("====================\n")

if rule:
    cond = rule["condition"] # Gets the condition inside "rule", one more extra 
    # step taken to advance the data processing/extracting
    # Printing cond for visualization 
    print("======= Cond:=======")
    print(cond)
    print("====================\n")
    # Checks how the dropdown was defined: 1) Options is typed directly into 
    # the rule or 2) option comes from cells elsewhere
    if cond["type"] == "ONE_OF_LIST":
        # Printing cond[values] for visualization 
        print("=== cond[values]:===")
        print(cond["values"])
        print("====================\n")
        subject_options = [v["userEnteredValue"] for v in cond["values"]] 
        # Loops through all items in cond["values"]

    # Skipping documentation here for now since unused.
    elif cond["type"] == "ONE_OF_RANGE":
        src = cond["values"][0]["userEnteredValue"].lstrip("=")  
        vals = service.spreadsheets().values().get(
            spreadsheetId=sheet_id, range=src
        ).execute()
        subject_options = [row[0] for row in vals.get("values", []) if row]

 # Printing subject_options for visualization 
print("== Subject options:==")
print(subject_options)
print("====================\n")



#===============================================================================
# READING VALUES INTO A PANDAS DATAFRAME:
npArray = np.array(values, dtype = object) # Converting values to a numpy 
# array, dtype helps to specify that the array is quite messy and contains 
# objects, rather than a standard array.
myDF = pd.DataFrame(npArray) # Reading a numpy array into a pandas dataframe 
# using DataFrame function in pandas. 

print("== Initial MyDF head:==")
print(myDF.head()) # Visualizing top 5 results of myDF dataframe, works as 
# intended.
print("====================\n")



#===============================================================================
# SEGMENTATION OF PARTS IN MyDF: 
assignmentTarget = "Weekly assignments / practice / revision"
examTarget = "Exams"
externalTarget = "External coursework / activities"
completedTarget = "Completed"

# Find row function to find where each row's index is
def findRows(df, target):
    # Enumerate is a function in python used to keep track of both the index 
    # and the values in an iterable
    for pos, cell in enumerate(df[0]):
        # Error check that if the data type passed in (the current cell/row) is 
        # either a list or a tuple and that the cell isn't empty
        if isinstance(cell, (list, tuple)) and len(cell) > 0:
            # Checks if the non-trailing space and lowered version of both the 
            # target and the value at current row at index 0 are equal
            if str(cell[0]).strip().lower() == target.strip().lower():
                return pos
    return None

# TODO: Write another checker that helps to find the column names themselves 
# and add to all the separate dataframes

# Finding positions of all segments
assignmentPos = findRows(myDF, assignmentTarget)
examPos = findRows(myDF,examTarget)
externalPos = findRows(myDF, externalTarget)
completedPos = findRows(myDF, completedTarget)

# Creating segmentations for task types.
assignmentDF = myDF.iloc[(assignmentPos + 1):examPos,:]
examDF = myDF.iloc[(examPos + 1):externalPos,:]
externalDF = myDF.iloc[(externalPos + 1):completedPos,:]
completedDF = myDF.iloc[(completedPos + 1):,:]



#===============================================================================
# DATA CLEANING AND FORMATTING MyDF: 
# Data cleaning and managing dataframe structure issue
print("== Shape of MyDF:==")
print(myDF.shape)
print("====================\n")

header = myDF.iloc[0]

print("== Type of header:==")
print(type(header))
print("====================\n")

print("== Visualization of header:==")
print (header)
print("====================\n")

# Creating correctly column-labeled dataframes
labeledAssignmentDF = pd.concat([header, assignmentDF])
labeledExamDF = pd.concat([header, examDF])
labeledExternalDF = pd.concat([header, externalDF])
labeledCompletedDF = pd.concat([header, completedDF])

print(labeledAssignmentDF.head())
print(labeledAssignmentDF.columns)

# Removing all empty instances
noEmptyAssignmentDF = labeledAssignmentDF[labeledAssignmentDF[0].str.len() > 0]
noEmptyExamDF = labeledExamDF[labeledExamDF[0].str.len() > 0]
noEmptyExternalDF = labeledExternalDF[labeledExternalDF[0].str.len() > 0]
noEmptyCompletedDF = labeledCompletedDF[labeledCompletedDF[0].str.len() > 0]

# Converting the dataframes into multi-column dataframes (making it actually 
# readable and useful to analyze)
expandedAssignmentDF = pd.DataFrame(noEmptyAssignmentDF[0].tolist(), index=noEmptyAssignmentDF.index) 
expandedExamDF = pd.DataFrame(noEmptyExamDF[0].tolist(), index=noEmptyExamDF.index)
expandedExternalDF = pd.DataFrame(noEmptyExternalDF[0].tolist(), index=noEmptyExternalDF.index)
expandedCompletedDF = pd.DataFrame(noEmptyCompletedDF[0].tolist(), index=noEmptyCompletedDF.index)


# Dropping the top initial column and making it row 0
expandedAssignmentDF.columns = expandedAssignmentDF.iloc[0]
expandedAssignmentDF = expandedAssignmentDF.iloc[1:].reset_index(drop=True)

expandedExamDF.columns = expandedExamDF.iloc[0]
expandedExamDF = expandedExamDF.iloc[1:].reset_index(drop=True)

expandedExternalDF.columns = expandedExternalDF.iloc[0]
expandedExternalDF = expandedExternalDF.iloc[1:].reset_index(drop=True)

expandedCompletedDF.columns = expandedCompletedDF.iloc[0]
expandedCompletedDF = expandedCompletedDF.iloc[1:].reset_index(drop=True)


# Printing all the segmented, cleaned, and organized dataframes:
print("== Visualization of expandedAssignmentDF:==")
print (expandedAssignmentDF.head(3))
print("============================================\n")

print("== Visualization of expandedExamDF:==")
print (expandedExamDF.head(3))
print("============================================\n")

print("== Visualization of expandedExternalDF:==")
print (expandedExternalDF.head(3))
print("============================================\n")

print("== Visualization of expandedCompletedDF:==")
print (expandedCompletedDF.head(3))
print("============================================\n")

print(expandedCompletedDF.columns.tolist())


# Initial test analysis 1, Finding the average task length for a specific 
# subject in the completedDF dataframe:


# subject_options for the subjects (honestly prolly don't even need it)


# Tried to add segmentation function to the program and fixed some comment 
# formating issues. Thinking of adding function the read the color of highlight 
# of the task to label the importance and do further analysis.
