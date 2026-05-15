'''
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import os.path
import pickle

# If modifying these scopes, delete the token.pickle file.
SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']  # example scope, change as needed

def get_google_token(credentials_path='API/credential.json', token_path='token.pickle'):
    creds = None
    # Load existing token if available
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token_file:
            creds = pickle.load(token_file)

    # If no valid creds, start OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the token for the next run
        with open(token_path, 'wb') as token_file:
            pickle.dump(creds, token_file)
    return creds

if __name__ == '__main__':
    creds = get_google_token()
    print('Access token:', creds.token)
'''

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import os

# ✅ Combined required scopes for all services
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/cloud-vision",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/devstorage.read_only"
]

def get_google_token(credentials_path='API/credential.json', token_path='API/google_token.json'):
    creds = None

    # Ensure folder exists
    os.makedirs(os.path.dirname(token_path), exist_ok=True)

    # Load existing token
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If no valid credentials, run OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the token as JSON
        with open(token_path, 'w') as token_file:
            token_file.write(creds.to_json())

    return creds

if __name__ == '__main__':
    creds = get_google_token()
    print("✅ Access token:", creds.token)
