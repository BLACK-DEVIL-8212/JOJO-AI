import requests
import json
import os
import sys
import time
import speech_recognition as sr
import pyttsx3

# OneDrive API credentials
ACCESS_TOKEN = "YOUR_ONEDRIVE_ACCESS_TOKEN"
CALL_LOG_PATH = "/call_logs/calls.json"  # Change this path to match your OneDrive file location

# Initialize speech recognition & text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
engine.setProperty("rate", 160)  # Speed of speech

def speak(text):
    """Convert text to speech"""
    engine.say(text)
    engine.runAndWait()

def listen():
    """Capture voice command from user"""
    with sr.Microphone() as source:
        print("Listening for command...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio).lower()
            print(f"You said: {query}")
            return query
        except sr.UnknownValueError:
            print("Sorry, I couldn't understand that.")
            return None
        except sr.RequestError:
            print("Network error. Check your connection.")
            return None

def fetch_onedrive_file(file_path):
    """Fetch file from OneDrive using API"""
    url = f"https://graph.microsoft.com/v1.0/me/drive/root:{file_path}:/content"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text  # Return file content
    else:
        print(f"Failed to fetch file. Status code: {response.status_code}")
        return None

def getcalls():
    """Fetch and speak call logs from OneDrive"""
    speak("Fetching call logs from OneDrive...")
    
    file_content = fetch_onedrive_file(CALL_LOG_PATH)
    if not file_content:
        speak("Failed to retrieve call logs.")
        return

    try:
        call_logs = json.loads(file_content)
    except json.JSONDecodeError:
        speak("Error reading call log format.")
        return

    if not call_logs:
        speak("No call logs available.")
        return
    
    for call in call_logs:
        speak(f"Caller: {call['caller']}, Number: {call['number']}, Status: {call['status']}")

def cutcall():
    """Simulates ending an ongoing call"""
    speak("Call disconnected successfully.")

def receivecall():
    """Simulates receiving an incoming call"""
    incoming_call = {"caller": "Unknown", "number": "+9999999999", "status": "Incoming"}
    speak(f"Incoming call from {incoming_call['caller']}")
    
    speak("Do you want to accept or decline?")
    action = listen()
    
    if action in ["accept", "yes", "answer"]:
        speak("Call answered.")
        incoming_call["status"] = "Received"
    else:
        speak("Call declined.")
        incoming_call["status"] = "Missed"

def recordcalls(duration=10):
    """Simulates recording a call for a given duration"""
    speak("Recording started.")
    for i in range(duration, 0, -1):
        sys.stdout.write(f"\rRecording... {i} sec remaining")
        sys.stdout.flush()
        time.sleep(1)
    print("\nRecording saved as 'recorded_call.mp3'.")
    speak("Recording completed and saved.")

