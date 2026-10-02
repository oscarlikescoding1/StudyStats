# Importing the libraries (Docs not done)
import os 
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv
import pandas as pd

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
subject = 'A:Z'

# Intializing sheet reading variable(?) by using the sheets object
sheet_read = sheets.values().get(spreadsheetId = sheet_id, range = subject).execute()


values = sheet_read.get('values', [])
# Looping and printing all data in given range
for row in values:
    print(row)



#===============================================================================
# Creating a new loop that finds all values/options in a dropdown menu of the subject column.


# Doing an API call to get the values in one specific column
subject_read = sheets.get(
    spreadsheetId = sheet_id,
    ranges = ["A6:A6"], # This value is the first instance of a dropdown menu for subject. This should not be changed under the ideal condition, but further processing may need to be done in the future to prevent catch error.
    includeGridData = True, # Including crucial info beyond just metadata
    fields = "sheets(data(rowData(values(dataValidation))))", # adds a field mask that limits grid data to only data validation as a part of the dropdown menu rather than also color, font etc.
).execute()

# The response is nested, so this walks down it: first sheet, first data block (one per requested range), first row, first cell. Since we asked for a single cell, each level has one entry. .get("dataValidation") returns None instead of crashing if the cell has no dropdown.

# Printing subject read for visualization 
print("===== Subject Read:====")
print(subject_read)
print("====================\n")


cell = subject_read["sheets"][0]["data"][0]["rowData"][0]["values"][0] # Response of subject_read is heavily nested. This walks it down through the first sheet, the first data, the frst rowData, first cell. Because we only requested for one cell, it is very simple to process so we just define it as the first index (0th index) of each category.
# Printing cell for visualization 
print("======= Cell:=======")
print(cell)
print("====================\n")

rule = cell.get("dataValidation") # Gets the data validation part of the "cell", up till here we are just extracting data step by step
# Printing rule for visualization 
print("======= Rule:=======")
print(rule)
print("====================\n")

if rule:
    cond = rule["condition"] # Gets the condition inside "rule", one more extra step taken to advance the data processing/extracting
    # Printing cond for visualization 
    print("======= Cond:=======")
    print(cond)
    print("====================\n")
    # Checks how the dropdown was defined: 1) Options is typed directly into the rule or 2) option comes from cells elsewhere
    if cond["type"] == "ONE_OF_LIST":
        # Printing cond[values] for visualization 
        print("=== cond[values]:===")
        print(cond["values"])
        print("====================\n")
        subject_options = [v["userEnteredValue"] for v in cond["values"]] # Loops through all items in cond["values"]

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

