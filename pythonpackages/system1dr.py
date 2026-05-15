import cv2
import requests
import time
import speech_recognition as sr

# Replace with your ESP32 IP address
ESP32_IP = "192.168.4.1"  # Example IP (use the correct one from your ESP32 setup)

# Endpoints
VIDEO_URL = f"http://{ESP32_IP}/video"
query_URL = f"http://{ESP32_IP}/query"

def send_query(query):
    """Send a control query to the drone."""
    try:
        response = requests.post(query_URL, data={"cmd": query})
        if response.status_code == 200:
            print(f"✅ query '{query}' sent successfully.")
        else:
            print(f"❌ Failed to send query '{query}'. Status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error sending query: {e}")

def display_video():
    """Display the live video feed from the ESP32-CAM."""
    cap = cv2.VideoCapture(VIDEO_URL)
    if not cap.isOpened():
        print("❌ Failed to open video stream.")
        return

    print("🎥 Say 'EXIT VIDEO' to stop viewing.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("❌ Failed to receive frame.")
            break

        cv2.imshow("Drone Video Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

def listen_for_query():
    """Recognize voice querys and execute them."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)  # Reduce background noise
        recognizer.dynamic_energy_threshold = True  # Auto-adjusts for noise levels
        print("🎤 Listening for a query...")

        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=5)
            query = recognizer.recognize_google(audio).upper()
            print(f"🗣️ Recognized query: {query}")

            return query

        except sr.UnknownValueError:
            print("⚠️ Could not understand the query.")
            return None
        except sr.RequestError as e:
            print(f"⚠️ Voice recognition error: {e}")
            return None

def voice_control():
    """Continuously listen for voice querys and execute them."""
    print("🎙️ Say 'ARISE' to activate drone control!")
    
    while True:
        query = listen_for_query()
        
        if query == "ARISE":
            print("🚀 Drone control activated! Say a query.")
            break
    
    predefined_path = ["UP", "UP", "RIGHT", "DOWN", "LEFT", "HOVER"]
    
    while True:
        query = listen_for_query()

        if query is None:
            continue
        elif query in ["UP", "DOWN", "LEFT", "RIGHT", "HOVER"]:
            send_query(query)
        elif query == "VIDEO":
            display_video()
        elif query == "EXIT VIDEO":
            print("🔴 Stopping video feed.")
            cv2.destroyAllWindows()
        elif query == "STOP":
            print("⛔ Emergency Stop Activated!")
            send_query("STOP")
        elif query == "EXIT":
            print("🔴 Exiting Drone Control Mode.")
            break
        elif query == "PATH":
            print("🚀 Executing Predefined Flight Path...")
            for cmd in predefined_path:
                send_query(cmd)
                time.sleep(2)
        else:
            print("⚠️ Unknown query. Please try again.")

if __name__ == "__main__":
    voice_control()
