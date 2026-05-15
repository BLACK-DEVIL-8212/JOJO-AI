from __future__ import print_function
import os.path
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define OAuth Scopes
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Path to credentials.json
CREDENTIALS_FILE = "API/googlecalanderapi.json"

def authenticate_google_calendar():
    creds = None
    # Load token.json if it exists
    if os.path.exists("token.json"):
        from google.oauth2.credentials import Credentials
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If token is invalid, authenticate again
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # Refresh token if expired
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Open browser for authentication

        # Save new token
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds

# Authenticate & Build Calendar Service
creds = authenticate_google_calendar()
service = build("calendar", "v3", credentials=creds)

# Fetch Calendar List to Verify API Works
calendar_list = service.calendarList().list().execute()
print(calendar_list)
