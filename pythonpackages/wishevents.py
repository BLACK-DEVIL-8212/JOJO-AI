from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import datetime

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
TOKEN_FILE = "API/google_token.json"

def get_calendar_service():
    """Load credentials from token file and authenticate with Google Calendar API"""
    if not os.path.exists(TOKEN_FILE):
        print("Token file not found! Please authenticate first.")
        return None

    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return build("calendar", "v3", credentials=creds)

def get_todays_events():
    """Fetch only today's events from Google Calendar"""
    service = get_calendar_service()
    if not service:
        return "Authentication failed."

    # Get current date in YYYY-MM-DD format
    today = datetime.datetime.utcnow().date()
    start_of_day = datetime.datetime.combine(today, datetime.time.min).isoformat() + "Z"
    end_of_day = datetime.datetime.combine(today, datetime.time.max).isoformat() + "Z"

    # Fetch events happening today
    events_result = service.events().list(
        calendarId="primary",
        timeMin=start_of_day,
        timeMax=end_of_day,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    if not events:
        return "No events scheduled for today."

    return "\n".join([f"{event['summary']} at {event['start'].get('dateTime', event['start'].get('date'))}" for event in events])
