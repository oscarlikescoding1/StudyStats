# Importing the libraries (Docs not done)
import os 
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

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
test_range = 'A6:A12'

# Intializing sheet reading variable(?) by using the sheets object
sheet_read = sheets.values().get(spreadsheetId = sheet_id, range = test_range).execute()

values = sheet_read.get('values', [])
# Looping and printing all data in given range
for row in values:
    print(row)


