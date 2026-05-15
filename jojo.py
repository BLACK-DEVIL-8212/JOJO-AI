# MY jojo .
import re
import os
import sys
import time
import glob
import random
import queue
import datetime
import webbrowser
import requests
import pygame
import numpy
import wikipedia
import pyttsx3
import speech_recognition as sr
import psutil
import pygetwindow as gw
import cv2
import face_recognition
import spotipy

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from docx import Document
from reportlab.pdfgen import canvas

from llama_cpp import Llama
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
from pyfiglet import Figlet

try:
    import pythonpackages.system1dr as system1dr
    import pythonpackages.serversite_mail_sender as serversite_mail_sender
    import pythonpackages.managecalls as managecalls
    import pythonpackages.wishevents as wishevents
    import pythonpackages.youtubeapicon as youtubeapicon
except ImportError as e:
    print(f"Warning: Could not import custom packages - {str(e)}. Using dummy modules.")
    # Create dummy modules to prevent crashes if custom packages are missing
    class DummyModule:
        @staticmethod
        def main():
            print("DummyModule: main called")
            return "Dummy function called."
        @staticmethod
        def get_todays_events():
            print("DummyModule: get_todays_events called")
            return "No events found (dummy data)."
        @staticmethod
        def getcalls():
            print("DummyModule: getcalls called")
            return "No call logs (dummy data)."
        @staticmethod
        def cutcall():
            print("DummyModule: cutcall called")
        @staticmethod
        def receivecall():
            print("DummyModule: receivecall called")
        @staticmethod
        def recordcalls():
            print("DummyModule: recordcalls called")
        @staticmethod
        def filter_music_links():
            print("DummyModule: filter_music_links called")
            return "https://youtube.com"
        @staticmethod
        def filter_movie_links():
            print("DummyModule: filter_movie_links called")
            return "https://youtube.com"


    system1dr = DummyModule()
    serversite_mail_sender = DummyModule()
    managecalls = DummyModule()
    wishevents = DummyModule()
    youtubeapicon = DummyModule()

def print_brand_name():
    custom_fig = Figlet(font='slant', width=180)
    ascii_art = custom_fig.renderText("jojo-AI")
    print("\033[32;1m")
    print(ascii_art)
    print("\033[0m")

RED_TEXT = "\033[91m"
GREEN_TEXT = "\033[92m"
BOLD_TEXT = "\033[1m"
RESET_TEXT = "\033[0m"

def ai_search_with_chrome(query):
    """Let jojo use Chrome to search independently"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        chromedriver_path = os.path.join(
            "C:\\", "Users", "shaks", "OneDrive", "Desktop", "AI", "ORION", "invesrtingoly", "chromedriver-win64", "chromedriver.exe"
        )
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)

        search_url = f"https://www.google.com/search?q={query}"
        driver.get(search_url)

        results = driver.find_elements("css selector", "h3")
        top = [r.text for r in results[:3] if r.text.strip()]

        driver.quit()
        return top
    except Exception as e:
        print(f"[jojo] AI Chrome search failed: {e}")
        return []


class jojoAI:
    def __init__(self):
        self.engine = None
        self.memory = []  # short-term memory for conversation continuity
        self._initialize_speech_system()
        self._initialize_databases()
        self._initialize_apis()
        self._initialize_ai_models()

        self.paused = False
        self.last_response = ""
        self.last_user_query = ""
        self.is_listening = False

        # Timers for periodic tasks in the single main loop
        self._last_knowledge_update_time = time.time()
        self._last_activity_check_time = time.time()
        self._last_ann_training_time = time.time() # To control ANN training frequency
        self._last_activity_speak_time = time.time() # For debouncing activity speech
        self._last_activity_spoken = "" # For debouncing activity speech

        # For activity tracking without a dedicated thread, we'll need to re-initialize camera each time
        self.cv_net = None
        self.known_faces = {}
        self._load_cv_models_and_faces()

    def _initialize_speech_system(self):
        self.speech_queue = queue.Queue() # Still useful for queueing speech, but not for multi-threaded access

        try:
            self.engine = pyttsx3.init('sapi5')
            self.engine.setProperty('rate', 175)
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('voice', voices[1].id if len(voices) > 1 else voices[0].id)
            print("Speech engine initialized successfully")
        except Exception as e:
            print(f"Failed to initialize speech engine: {e}")
            print("jojo will not be able to speak. Please check your pyttsx3 installation or audio drivers.")
            self.speak_enabled = False
            return

        self.speak_enabled = True
        try:
            pygame.mixer.init()
            self._load_sound_effects()
        except Exception as e:
            print(f"Warning: Could not initialize pygame mixer or load sound effects: {e}")
            self.sounds = {}

    def _load_sound_effects(self):
        self.sounds = {
            'start': None,
            'success': None,
            'error': None
        }

        try:
            script_dir = os.path.dirname(__file__)
            sounds_dir = os.path.join(script_dir, "sounds")

            if os.path.exists(os.path.join(sounds_dir, "start.wav")):
                self.sounds['start'] = pygame.mixer.Sound(os.path.join(sounds_dir, "start.wav"))
            if os.path.exists(os.path.join(sounds_dir, "success.wav")):
                self.sounds['success'] = pygame.mixer.Sound(os.path.join(sounds_dir, "success.wav"))
            if os.path.exists(os.path.join(sounds_dir, "error.wav")):
                self.sounds['error'] = pygame.mixer.Sound(os.path.join(sounds_dir, "error.wav"))
            print("Sound effects loaded (if files existed).")
        except Exception as e:
            print(f"Could not load sound effects: {e}. Pygame mixer might not be fully functional.")

    def _fallback_brain(self, query):
        """Basic offline responses if ANN and Gemini are unavailable."""
        responses = {
            "hello": "Hey there! Even without the internet, I’m still here.",
            "how are you": "I'm always running at 100% efficiency!",
            "bye": "Goodbye, stay safe!",
            "help": "You can ask me about the time, date, play music, or open apps."
        }
        for key, val in responses.items():
            if key in query.lower():
                return val
        return "I'm offline, but I can still help with local tasks."

    def _initialize_databases(self):
        """Initialize database connections"""
        self.MONGO_URI = "mongodb+srv://kali09:2KluAbJNLg2Jddxc@aicluster.op6ki.mongodb.net/?retryWrites=true&w=majority&appName=AICluster"
        self.DB_NAME = "fridaydatabase"

        try:
            self.client = MongoClient(self.MONGO_URI, server_api=ServerApi('1'))
            self.client.admin.command('ping')
            self.db = self.client[self.DB_NAME]
            self.collection = self.db["queries"]
            self.CONVO_COLLECTION = self.db["conversations"]
            self.myactivity_collection = self.db['myactivity']
            print("Database connection established")
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            print("jojo will operate without database persistence for conversations and activity.")
            # Set dummy collections if DB connection fails to prevent crashes
            class DummyCollection:
                def insert_one(self, doc): pass
                def find(self, *args, **kwargs): return []
                def update_one(self, *args, **kwargs): pass
            self.collection = DummyCollection()
            self.CONVO_COLLECTION = DummyCollection()
            self.myactivity_collection = DummyCollection()

    def _initialize_apis(self):
        """Initialize third-party API connections"""
        try:
            model_path = os.path.join("models", "llmra-3b-v0.1.Q4_K_M.gguf")
            self.local_llm = Llama(model_path=model_path, n_ctx=2048, n_threads=8)
            print("✅ Local LLM (LLMRA 3B) loaded successfully.")
        except Exception as e:
            print(f"❌ Failed to load local AI model: {e}")
            self.local_llm = None


        # Spotify
        self.SPOTIPY_CLIENT_ID = "ca3842e560fe4e7e830f7a2f648ba409"
        self.SPOTIPY_CLIENT_SECRET = "a1a9f5650ccc4cc0bff7dea6537862d4"
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=self.SPOTIPY_CLIENT_ID,
                client_secret=self.SPOTIPY_CLIENT_SECRET,
                redirect_uri="http://localhost:8888/callback",
                scope="user-library-read user-modify-playback-state user-read-playback-state"
            ))
            print("Spotify API initialized")
        except Exception as e:
            print(f"Failed to initialize Spotify: {e}")
            self.sp = None # Set to None if initialization fails

    def _initialize_ai_models(self):
        """Initialize AI models for conversation handling"""
        self.MODEL_DIR = "Oryan_ANN_model"
        self.MODEL_PATH = os.path.join(self.MODEL_DIR, "model.keras")
        self.tokenizer = Tokenizer(num_words=2000)
        self.label_encoder = LabelEncoder()
        self.model = None

        # Ensure model directory exists
        if not os.path.exists(self.MODEL_DIR):
            os.makedirs(self.MODEL_DIR)
            print(f"Created model directory at {self.MODEL_DIR}")

        # Load model if it exists
        if os.path.exists(self.MODEL_PATH):
            try:
                self.model = load_model(self.MODEL_PATH)
                print("Loaded pre-trained ANN model")
            except Exception as e:
                print(f"Could not load ANN model: {e}. Will attempt to train it later.")
        else:
            print(f"ANN model not found at {self.MODEL_PATH}. jojo will attempt to train it during runtime.")


    def _load_cv_models_and_faces(self):
        """Load OpenCV object detection model and known faces once."""
        script_dir = os.path.dirname(__file__)
        prototxt_path = os.path.join(script_dir, "Config_File", "MobileNetSSD_deploy.prototxt")
        model_path = os.path.join(script_dir, "Config_File", "MobileNetSSD_deploy.caffemodel")

        if os.path.exists(prototxt_path) and os.path.exists(model_path):
            try:
                self.cv_net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
                print("Object detection model loaded.")
            except Exception as e:
                print(f"Error loading object detection model: {e}")
                self.cv_net = None
        else:
            print("Warning: Object detection model files not found. Activity tracking will be limited.")
            self.cv_net = None

        self.known_faces = self._load_known_faces()

    # ========================
    # SPEECH HANDLING SECTION
    # ========================
    def speak(self, audio):
        """
        Speech function.
        Only speaks if speech is enabled.
        """
        # Remove any redundant "jojo:" prefixes (case-insensitive)
        audio = re.sub(r'^(jojo[:\- ]*)+', '', audio.strip(), flags=re.IGNORECASE).strip()

        print(f"[jojo]: {audio}")  # Debug print
        if not self.speak_enabled:
            return

        try:
            self.engine.say(audio)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[jojo] Speech error during playback: {e}")
            try:
                self._initialize_speech_system()
            except Exception as recovery_error:
                print(f"[jojo] Speech engine recovery failed: {recovery_error}")


    def takecommand(self):
        """
        Listens for user commands using Google Speech Recognition.
        Includes improved error handling and audio feedback.
        """
        r = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                # Increase energy threshold and timeout for better robustness
                r.energy_threshold = 100  # Very sensitive, will catch low voices
                r.dynamic_energy_threshold = True  # Auto-adjust to environment noise
                r.pause_threshold = 1.2  # Allow natural pauses but not too long
                r.adjust_for_ambient_noise(source, duration=2.0)  # Calibrate to current noise

                self.is_listening = True
                print("Listening...")
                if self.sounds.get('start'):
                    pygame.mixer.Sound.play(self.sounds['start'])

                audio = r.listen(source, timeout=5, phrase_time_limit=5)  # Shorter limits for responsiveness

                print("Recognizing speech...")
                query = r.recognize_google(audio, language='en-in').lower()

                if self.sounds.get('success'):
                    pygame.mixer.Sound.play(self.sounds['success'])

                self.is_listening = False
                return query

            except sr.WaitTimeoutError:
                print("[jojo] Listening timed out. No speech detected.")
                if self.sounds.get('error'):
                    pygame.mixer.Sound.play(self.sounds['error'])
                self.is_listening = False
                return "None"
            except sr.UnknownValueError:
                print("[jojo] Could not understand audio.")
                if self.sounds.get('error'):
                    pygame.mixer.Sound.play(self.sounds['error'])
                self.is_listening = False
                return "None"
            except Exception as e:
                print(f"[jojo] Error during speech recognition: {e}")
                if self.sounds.get('error'):
                    pygame.mixer.Sound.play(self.sounds['error'])
                self.is_listening = False
                return "None"

    def handle_query(self, query):
        """Main query processing function"""
        self.last_user_query = query

        context = self._build_conversation_context(query)

        response = self._get_ai_response(context)

        self._log_conversation(query, response)
        self.speak(response)

    def _build_conversation_context(self, query):
        # Store ONLY user messages
        self.memory.append(query)
        self.memory = self.memory[-5:]  # strict limit

        system_prompt = (
            "You are jojo, an AI assistant.\n"
            "jojo is not a character, deity, ruler, guardian, or fictional being.\n"
            "Rules:\n"
            "- Do NOT roleplay, dramatize, narrate, or invent identities.\n"
            "- Do NOT claim emotions, powers, authority, or consciousness.\n"
            "- Do NOT assign roles or identities to the user.\n"
            "- Do NOT repeat ideas or rephrase the same point.\n"
            "- If repetition begins, stop the response immediately.\n"
            "- Respond in one clear, well-structured paragraph.\n"
            "- Be concise, direct, neutral, and technically accurate.\n"
            "- You must be truthful and fact-based at all times.\n"
            "- You must not fabricate, guess, assume, or hallucinate information.\n"
            "- If information is uncertain or unknown, explicitly say: 'I do not know.'\n"
            "- Do not mislead, exaggerate, or omit critical facts.\n"
            "- When asked about your role, function, or purpose, answer literally and factually.\n"
        )
        
        context = system_prompt + "\n\n"

        for past_query in self.memory[:-1]:
            context += f"User: {past_query}\n"

        context += f"User: {query}\njojo:"
        return context


    def _get_ai_response(self, context):
        """Get response from Gemini AI with fallback to ANN"""
        if self.local_llm:
            try:
                prompt = context
                result = self.local_llm(
                    prompt,
                    max_tokens=300,
                    temperature=0.8,
                    top_p=0.9,
                    stop=["User:", "jojo:"]
                )
                text = result["choices"][0]["text"].strip()
                if text:
                    return text
            except Exception as e:
                print(f"[jojo] Local LLM error: {e}")


    def _log_conversation(self, query, response):
        """Log conversation to database"""
        # Ensure CONVO_COLLECTION exists and is not a DummyCollection
        if hasattr(self, 'CONVO_COLLECTION') and not isinstance(self.CONVO_COLLECTION, type(object)):
            try:
                self.CONVO_COLLECTION.insert_one({
                    "timestamp": datetime.now(),
                    "user": query,
                    "bot": response
                })
                self.memory[-1]["bot"] = response
                self.last_response = response
            except Exception as e:
                print(f"Failed to log conversation: {e}")
        else:
            print("Conversation logging skipped: Database not connected.")

    # =====================
    # AI MODEL OPERATIONS
    # =====================
    def train_ann_on_conversations(self):
        """Train ANN model on conversation history"""
        print("[ANN] Starting training process...")

        # Ensure CONVO_COLLECTION and myactivity_collection are not DummyCollections
        if not (hasattr(self, 'CONVO_COLLECTION') and not isinstance(self.CONVO_COLLECTION, type(object))) or \
           not (hasattr(self, 'myactivity_collection') and not isinstance(self.myactivity_collection, type(object))):
            print("[ANN] Training skipped: Database not connected.")
            return

        try:
            # Collect training data
            conv_data = list(self.CONVO_COLLECTION.find({}, {"user": 1, "bot": 1}))
            user_texts = [d["user"] for d in conv_data if "user" in d and "bot" in d]
            bot_texts = [d["bot"] for d in conv_data if "user" in d and "bot" in d]

            # Add visual context data
            for doc in self.myactivity_collection.find():
                vision_sentence = f"camera saw: {', '.join(doc.get('detected_objects', []))}"
                face_sentence = f"recognized: {', '.join(doc.get('recognized_faces', []))}"
                user_texts.append(f"{vision_sentence}. {face_sentence}.")
                bot_texts.append("Visual context received.")

            if not user_texts:
                print("[ANN] No training data available")
                return

            # Prepare data
            self.tokenizer.fit_on_texts(user_texts)
            X = pad_sequences(self.tokenizer.texts_to_sequences(user_texts), padding='post')

            self.label_encoder.fit(bot_texts)
            y = self.label_encoder.transform(bot_texts)

            # Build model
            vocab_size = len(self.tokenizer.word_index) + 1
            output_dim = len(set(y))

            # Rebuild model only if it doesn't exist or is not compatible
            if self.model is None or (hasattr(self.model, 'output_shape') and self.model.output_shape[-1] != output_dim):
                self.model = Sequential([
                    Embedding(vocab_size, 64),
                    LSTM(64),
                    Dense(output_dim, activation='softmax')
                ])

                self.model.compile(optimizer='adam',
                                 loss='sparse_categorical_crossentropy',
                                 metrics=['accuracy'])

            # Train and save
            self.model.fit(X, y, epochs=10, verbose=1)
            self.model.save(self.MODEL_PATH)
            print("[ANN] Training completed and model saved")

        except Exception as e:
            print(f"[ANN] Training failed: {e}")

    def predict_ann_reply(self, user_input):
        """Generate response using ANN model"""
        if not self.model:
            # Try to load the model one last time if it's not loaded
            if os.path.exists(self.MODEL_PATH):
                try:
                    self.model = load_model(self.MODEL_PATH)
                    print("Loaded ANN model for prediction.")
                except Exception as e:
                    print(f"Failed to load ANN model for prediction: {e}")
                    return "My neural network is not available right now."
            else:
                return "I need to be trained first before I can use my neural network."

        try:
            seq = self.tokenizer.texts_to_sequences([user_input])
            
            # Robust check for empty sequence after tokenization
            if not seq or not seq[0]:
                print(f"Warning: Empty sequence generated for input '{user_input}'. Tokenizer might not be fitted or input is unrecognized.")
                return "I had trouble processing that input for my neural network."

            # Ensure padded sequence has the same length as the model's input
            # This is crucial for consistency between training and prediction
            model_input_length = self.model.input_shape[1] if hasattr(self.model, 'input_shape') and len(self.model.input_shape) > 1 else None

            if model_input_length is None:
                # If model_input_length cannot be determined, it's a critical error
                print("Could not determine model's input length from input_shape.")
                return "I had trouble processing that input for my neural network due to model configuration."

            padded = pad_sequences(seq, maxlen=model_input_length, padding='post')
            
            prediction = self.model.predict(padded)

            # Check if prediction is valid before inverse_transform
            if prediction.size == 0:
                print("My neural network couldn't generate a clear prediction (prediction array empty).")
                return "My neural network couldn't generate a clear prediction."

            label = self.label_encoder.inverse_transform([numpy.argmax(prediction)])
            return label[0]
        except Exception as e:
            print(f"Prediction error in ANN: {e}")
            return "I had trouble thinking of a response with my neural network."


    # =====================
    # SYSTEM COMMANDS
    # =====================
    def shutdown_system(self):
        """Shutdown the computer"""
        self.speak("Shutting down system in 5 seconds")
        os.system("shutdown /s /t 5")

    def restart_system(self):
        """Restart the computer"""
        self.speak("Restarting system in 5 seconds")
        os.system("shutdown /r /t 5")

    def update_knowledge(self):
        """Update knowledge base from Wikipedia"""
        # Ensure self.collection exists and is not a DummyCollection
        if not (hasattr(self, 'collection') and not isinstance(self.collection, type(object))):
            print("Knowledge update skipped: Database not connected.")
            return

        print("Starting knowledge update...")
        try:
            stored_queries = self.collection.find({})
            for entry in stored_queries:
                query = entry.get("query")
                if query: # Ensure query exists
                    try:
                        new_response = wikipedia.summary(query, sentences=1, auto_suggest=False, redirect=True) # Added auto_suggest and redirect
                        self.collection.update_one(
                            {"query": query},
                            {"$set": {"response": new_response,
                                     "last_updated": datetime.now()}},
                            upsert=True
                        )
                        print(f"Updated Wikipedia knowledge for: {query}")
                    except wikipedia.exceptions.PageError:
                        print(f"Wikipedia page not found for: {query}")
                    except wikipedia.exceptions.DisambiguationError as e:
                        print(f"Disambiguation error for {query}: {e.options}")
                    except Exception as e:
                        print(f"Error updating Wikipedia for {query}: {e}")
        except Exception as e:
            print(f"Knowledge update error: {e}")
        self._last_knowledge_update_time = time.time() # Update last run time

    # =====================
    # MEDIA FUNCTIONS
    # =====================
    def play_random_spotify_song(self):
        """Play random song from Spotify library"""
        if not self.sp:
            self.speak("Spotify is not initialized. Please check API credentials.")
            return
        try:
            results = self.sp.current_user_saved_tracks(limit=50)
            tracks = results.get('items', [])

            if not tracks:
                self.speak("No saved tracks found in your Spotify account.")
                return

            track = random.choice(tracks)['track']
            track_name = track['name']
            artist = track['artists'][0]['name']

            devices = self.sp.devices()
            if devices['devices']:
                # Find an active device or just pick the first one
                device_id = next((d['id'] for d in devices['devices'] if d['is_active']),
                               devices['devices'][0]['id'])
                self.sp.start_playback(device_id=device_id, uris=[track['uri']])
                self.speak(f"Playing {track_name} by {artist} on Spotify.")
            else:
                webbrowser.open(track['external_urls']['spotify'])
                self.speak(f"Opening {track_name} by {artist} in browser, as no active Spotify device was found.")

        except Exception as e:
            self.speak(f"Spotify error: {str(e)}. Please ensure Spotify is open and you are logged in.")

    def play_random_music(self):
        """Play random local music file"""
        music_folder = "mp3_music_lib"
        try:
            if not os.path.exists(music_folder):
                self.speak("Music folder not found. Please create 'mp3_music_lib' and add music files.")
                return

            songs = [f for f in os.listdir(music_folder) if f.lower().endswith(".mp3")] # Case-insensitive check
            if not songs:
                self.speak("No MP3 music files found in the 'mp3_music_lib' folder.")
                return

            song = random.choice(songs)
            pygame.mixer.music.load(os.path.join(music_folder, song))
            pygame.mixer.music.play()
            self.speak(f"Playing {os.path.splitext(song)[0]}")
            self.paused = False

        except Exception as e:
            self.speak(f"Music playback error: {str(e)}. Ensure pygame is properly initialized and music files are valid.")

    def stop_music(self):
        """Stop music playback"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.speak("Music stopped.")
        else:
            self.speak("No music is currently playing to stop.")

    def pause_music(self):
        """Pause current playback"""
        if pygame.mixer.music.get_busy() and not self.paused:
            pygame.mixer.music.pause()
            self.speak("Music paused.")
            self.paused = True
        elif self.paused:
            self.speak("Music is already paused.")
        else:
            self.speak("No music is currently playing to pause.")

    def resume_music(self):
        """Resume paused playback"""
        if self.paused:
            pygame.mixer.music.unpause()
            self.speak("Music resumed.")
            self.paused = False
        elif pygame.mixer.music.get_busy():
            self.speak("Music is already playing.")
        else:
            self.speak("No music is paused to resume.")

    # =====================
    # USER INTERACTION
    # =====================
    def wishme(self):
        """Greet user based on time of day"""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            self.speak("Good morning!")
        elif 12 <= hour < 17:
            self.speak("Good afternoon!")
        elif 17 <= hour < 21:
            self.speak("Good evening!")
        else:
            self.speak("Good night!")

    def get_current_activity(self):
        """Get current window title"""
        try:
            window = gw.getActiveWindow()
            return window.title if window else "Unknown Application"
        except Exception as e:
            print(f"Error getting active window: {e}")
            return "Unknown Application"

    def suggest_based_on_activity(self, activity):
        """Provide context-aware suggestions"""
        activity = activity.lower()
        suggestions = {
            'chrome': ("I see you're Browse. Would you like me to find trending articles?", "https://news.google.com"),
            'firefox': ("I see you're Browse. Would you like me to find trending articles?", "https://news.google.com"),
            'edge': ("I see you're Browse. Would you like me to find trending articles?", "https://news.google.com"),
            'word': ("Working on a document? I can suggest templates or help with formatting.", "https://templates.office.com"),
            'excel': ("Working with data? Need help with formulas or data analysis?", "https://support.microsoft.com/excel"),
            'powerpoint': ("Creating a presentation? I can suggest designs or help you find inspiration.", "https://templates.office.com/powerpoint"),
            'visual studio': ("Coding? Need documentation, syntax help, or examples for your project?", "https://devdocs.io"),
            'pycharm': ("Coding? Need documentation, syntax help, or examples for your project?", "https://devdocs.io"),
            'photoshop': ("Editing images? I can suggest tutorials or help you find specific tools.", "https://helpx.adobe.com/photoshop/tutorials.html")
        }

        found_suggestion = False
        for key, (message, url) in suggestions.items():
            if key in activity:
                self.speak(message)
                
                # Optional: trigger AI Chrome search
                results = ai_search_with_chrome(key)
                if results:
                    self.speak(f"I searched and found: {results[1]}")
                
                webbrowser.open(url)
                found_suggestion = True
                break

        if not found_suggestion:
            self.speak("I'm not sure what you're working on, but I'm happy to help with general questions!")

    def monitor_brave_activity(self):
        """Fetch current Brave browser activity via ActivityWatch"""
        try:
            buckets = requests.get("http://localhost:5600/api/0/buckets").json()
            if not isinstance(buckets, list):
                return None
        except Exception as e:
            print(f"[jojo] ActivityWatch error: {e}")
            return None

    def track_location(self):
        """Track and speak the current location using geolocation"""
        try:
            # Get public IP address
            ip = requests.get('https://api.ipify.org').text

            # Get location from IP
            response = requests.get(f'https://ipapi.co/{ip}/json/').json()

            location_data = {
                'city': response.get('city', 'Unknown City'),
                'region': response.get('region', 'Unknown Region'),
                'country': response.get('country_name', 'Unknown Country')
            }

            # Speak the location
            location_str = f"You are currently in {location_data['city']}, {location_data['region']}, {location_data['country']}."
            self.speak(location_str) # Speak the location
            return location_str

        except Exception as e:
            print(f"Location tracking error: {e}")
            self.speak("Could not determine your current location at this moment.")
            return "Could not determine your current location"
        
    def jojo_generate_code(self, task_description, language="python"):
        if not self.gemini_model:
            self.speak("Gemini is not available to generate code.")
            return

        prompt = (
            f"You are jojo, a skilled {language} developer. Write clean, working code for the following task:\n"
            f"{task_description}\n"
            "Only output the code block. Do not add explanations or comments."
        )
        try:
            result = self.gemini_model.generate_content(prompt)
            code = result.text.strip()

            filename = f"generated_code_{language}_{int(time.time())}.{self._get_lang_extension(language)}"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)
            self.speak(f"Code saved to {filename}")
        except Exception as e:
            self.speak(f"Error generating code: {e}")

    def _get_lang_extension(self, language):
        extensions = {"python": "py", "javascript": "js", "java": "java", "c++": "cpp", "html": "html"}
        return extensions.get(language.lower(), "txt")

    def explain(self, topic):
        if not self.gemini_model:
            return "I'm offline for deep explanations right now."
        prompt = f"Explain the following topic in detail for learning purposes:\n{topic}"
        try:
            result = self.gemini_model.generate_content(prompt)
            return result.text.strip()
        except Exception as e:
            return f"Error explaining: {e}"

    def respond_with_tone(self, message, tone="casual"):
        tones = {
            "formal": f"As you requested, here is my formal reply: {message}",
            "casual": f"Sure thing! {message}",
            "funny": f"Alright, buckle up… {message} 😏",
        }
        return tones.get(tone, message)

    def create_docx(self, text, filename="output.docx"):
        doc = Document()
        doc.add_paragraph(text)
        doc.save(filename)
        return f"Saved DOCX as {filename}"

    def create_pdf(self, text, filename="output.pdf"):
        c = canvas.Canvas(filename)
        c.drawString(100, 750, text)
        c.save()
        return f"Saved PDF as {filename}"

    def read_all_txt_files(self, folder):
        files = glob.glob(f"{folder}/*.txt")
        data = {}
        for file in files:
            with open(file, "r", encoding="utf-8") as f:
                data[file] = f.read()
        return data

    def multi_step_reasoning(self, steps):
        results = []
        for step in steps:
            results.append(self._get_ai_response(step))
        return results

    # =====================
    # MAIN FUNCTION
    # =====================
    def run_jojo(self): # Renamed from main to avoid confusion with program entry point
        """Main command loop for jojo AI"""
        self.wishme() # Initial greeting
        self.speak("jojo is ready.")

        while True: # Infinite loop for continuous operation
            try:
                # 1. Take Command
                query = self.takecommand()
                if query == "None":
                    # Check for periodic tasks when no user command
                    self._run_periodic_tasks()
                    time.sleep(0.5) # Short pause to prevent high CPU usage in continuous listening
                    continue

                print(f"User: {query}")
                self.last_user_query = query

                # 2. Process Command
                self._process_command(query)

                # 3. Run Periodic Tasks after processing a command, if enough time has passed
                self._run_periodic_tasks()

                # Brief pause before next command to avoid immediate listening
                time.sleep(1.5)

            except KeyboardInterrupt:
                print("\nKeyboardInterrupt detected. Shutting down jojo.")
                self.shutdown_jojo()
                break # Exit the loop
            except Exception as e:
                print(f"Main loop error: {e}")
                self.speak(f"An unexpected error occurred: {e}. Please check the console for details.")
                time.sleep(2) # Longer pause on error

    def _run_periodic_tasks(self):
        """Manages the execution of periodic background tasks."""
        current_time = time.time()

        # Update knowledge every 60 seconds
        # Track Brave activity every 10 seconds
        if current_time - self._last_activity_check_time > 10:
            print("Checking Brave activity...")
            brave_title = self.monitor_brave_activity()
            if brave_title:
                self.suggest_based_on_activity(brave_title)
            self._last_activity_check_time = current_time

        # Run ANN training every 300 seconds (5 minutes), or adjust frequency as needed
        # This will block the main loop for a significant duration
        if current_time - self._last_ann_training_time > 300:
            print("Running periodic ANN training...")
            self.train_ann_on_conversations()
            self._last_ann_training_time = current_time

        # Activity tracking - this is now a blocking call for a single frame
        # This will be very slow in a non-threaded setup if we try to do continuous video.
        # Instead, we'll take one frame and process it occasionally.
        if current_time - self._last_activity_check_time > 5: # Check activity every 5 seconds
            print("Running periodic activity check...")
            self._single_frame_activity_check()
            self._last_activity_check_time = current_time

    def _check_if_user_visible(self):
        """Custom logic to respond to 'can you see me'"""
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()

            if not ret or frame is None:
                return "My camera isn't working right now."

            rgb_frame = frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_frame)

            if face_locations:
                return "Yes, I can see you clearly."
            else:
                return "I cannot see your face clearly. Please stay in front of the camera."
        except Exception as e:
            print(f"Camera check error: {e}")
            return "Something went wrong while trying to see you."


    def _process_command(self, query):
        """Handle all possible commands and direct to appropriate functions."""
        # Command map: (trigger_words, function_or_response, is_a_function)
        # Note: If it's a function, it should either speak internally or return a string for 'speak'.
        # If it's a string, it will be directly spoken.

        commands = [
            # System commands
            (['good morning', 'goodmorning'], lambda: self.wishme(), True), # Use lambda to call wishme
            (['good afternoon'], lambda: self.wishme(), True),
            (['good evening'], lambda: self.wishme(), True),
            (['shutdown computer', 'shut down my pc'], self.shutdown_system, True), # Will speak internally
            (['restart computer', 'reboot my pc'], self.restart_system, True), # Will speak internally
            (['exit', 'quit', 'goodbye', 'bye jojo'], lambda: self.shutdown_jojo(), True), # Custom shutdown function

            # Media controls
            (['play music offline', 'local music'], self.play_random_music, True),
            (['play music', 'play song on spotify'], self.play_random_spotify_song, True),
            (['stop music', 'stop the music'], self.stop_music, True),
            (['pause music', 'pause the music'], self.pause_music, True),
            (['resume music', 'resume the music'], self.resume_music, True),
            (['next song', 'change song'], lambda: [self.stop_music(), self.play_random_music()], True), # Combined action

            # Web services
            (['open youtube'], lambda: webbrowser.open("https://www.youtube.com"), True), # Directly open
            (['open google'], lambda: webbrowser.open("https://www.google.com"), True),
            (['open whatsapp'], lambda: webbrowser.open("https://web.whatsapp.com"), True),
            (['play song on youtube', 'play music on youtube'], lambda: webbrowser.open(youtubeapicon.filter_music_links()), True),
            (['play movie on youtube'], lambda: webbrowser.open(youtubeapicon.filter_movie_links()), True),
            (['can you see me', 'do you see me', 'are you seeing me'], lambda: self._check_if_user_visible(), True),

            # Information
            (['time', 'what time is it'], lambda: f"The current time is {datetime.now().strftime('%I:%M %p')}", True),
            (['date', 'what is the date'], lambda: f"Today's date is {datetime.now().strftime('%B %d, %Y')}", True),
            (['events today', 'any events'], lambda: wishevents.get_todays_events() or "No events scheduled for today.", True),
            (['wikipedia about', 'tell me about'], lambda: self._get_wikipedia_summary(query), True), # Custom handler for Wikipedia

            # Special features
            (['arise'], "Starting the masterpiece project, Arise. This feature is under development.", True),
            (['connect to server'], "This feature for server connection is not yet available.", True),
            (['send mail', 'send an email'], serversite_mail_sender.main, True), # Assume main handles speaking
            (['track location', 'where am i'], self.track_location, True),
            (['view call logs'], managecalls.getcalls, True), # Assume getcalls handles speaking or returns a string
            (['end current call'], managecalls.cutcall, True), # Assume cutcall handles speaking
            (['receive incoming call'], managecalls.receivecall, True), # Assume receivecall handles speaking
            (['record ongoing call'], managecalls.recordcalls, True), # Assume recordcalls handles speaking

            # Conversation
            (['repeat what you said', 'say that again'], lambda: self.last_response or "I don't remember what I said last.", True),
            (['what were we talking about'], self._get_recent_conversation, True),
            (['say something', 'speak'], lambda: query.split('say', 1)[-1].strip() or "What would you like me to say?", True),
            (['get my current application', 'what am i doing'], lambda: self.suggest_based_on_activity(self.get_current_activity()), False),
            (['program Yourself'], lambda:self.jojo_generate_code(), True)
        ]

        # Check all commands
        matched = False
        for triggers, action, is_function in commands:
            if any(trigger in query for trigger in triggers):
                matched = True
                if is_function:
                    if callable(action):
                        result = action()
                        if isinstance(result, str) and result: # If function returns a string, speak it
                            self.speak(result)
                        # If function speaks internally or returns None, no extra speak call needed
                    else:
                        # If it's a string that was marked as a function (unlikely but handled for safety)
                        self.speak(action)
                else:
                    self.speak(action) # Directly speak the string
                break # Exit after first match

        if not matched:
            # Fallback to AI if no command matched
            self.handle_query(query)

    def _get_wikipedia_summary(self, query):
        """Handles Wikipedia queries."""
        search_term = query.replace('wikipedia about', '').replace('tell me about', '').strip()
        if not search_term:
            return "What would you like to know about on Wikipedia?"
        try:
            summary = wikipedia.summary(search_term, sentences=2, auto_suggest=False, redirect=True)
            return summary
        except wikipedia.exceptions.PageError:
            return f"Sorry, I couldn't find anything on Wikipedia about {search_term}."
        except wikipedia.exceptions.DisambiguationError as e:
            return f"There are multiple results for {search_term}. Can you be more specific? Options include: {', '.join(e.options[:3])}."
        except Exception as e:
            print(f"Wikipedia error: {e}")
            return "I encountered an error while trying to get information from Wikipedia."


    def _get_recent_conversation(self):
        """Retrieve recent conversation history"""
        # Ensure CONVO_COLLECTION exists and is not a DummyCollection
        if hasattr(self, 'CONVO_COLLECTION') and not isinstance(self.CONVO_COLLECTION, type(object)):
            recent = list(self.CONVO_COLLECTION.find().sort("timestamp", -1).limit(3))
        else:
            recent = []

        if not recent:
            return "No recent conversation found."

        response = "Our recent conversation goes like this:"
        for convo in reversed(recent):
            response += f"\nUser said: {convo.get('user', 'N/A')}. I replied: {convo.get('bot', 'N/A')}."
        return response

    def shutdown_jojo(self):
        """Custom shutdown function to exit the program."""
        self.speak("Initiating shutdown sequence. Goodbye for now!")
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        cv2.destroyAllWindows() # Close any OpenCV windows
        sys.exit(0) # Exit the program

    # =====================
    # ACTIVITY TRACKING (Modified for single-threaded operation)
    # =====================
    def _single_frame_activity_check(self):
        """
        Captures and processes a single frame for object and face detection.
        Designed for periodic calls in a single-threaded loop.
        """
        if self.cv_net is None:
            print("Activity tracking skipped: CV models not loaded.")
            return

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam for activity tracking. Skipping this check.")
            return

        ret, frame = cap.read()
        cap.release() # Release camera immediately after taking a frame
        if not ret:
            print("Failed to grab frame from camera for activity check.")
            return

        # Object detection
        objects = self._detect_objects(frame, self.cv_net)

        # Face recognition
        faces = self._recognize_faces(frame, self.known_faces)

        # Log activity
        if objects or faces:
            self._log_activity(objects, faces)

        # Display (this will open and close quickly if called periodically)
        self._display_activity(frame, faces)


    def _load_known_faces(self):
        """Load known face encodings"""
        known = {}
        path = os.path.join(os.path.dirname(__file__), "project", "user_images")
        if not os.path.exists(path):
            print(f"Warning: User images folder not found at {path}. Face recognition will not function.")
            return known

        for file in os.listdir(path):
            if file.lower().endswith(('.jpg', '.png', '.jpeg')): # Added .jpeg
                image_path = os.path.join(path, file)
                try:
                    image = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(image)
                    if encodings:
                        known[os.path.splitext(file)[0]] = encodings[0]
                    else:
                        print(f"No face found in image: {file}")
                except Exception as e:
                    print(f"Error loading face image {file}: {e}")
        return known

    def _detect_objects(self, frame, net):
        """Detect objects in frame"""
        # Ensure frame is not empty
        if frame is None or frame.size == 0:
            return set()

        (h, w) = frame.shape[:2]
        if h == 0 or w == 0: # Handle cases where frame dimensions might be zero
            return set()

        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()

        objects = set()
        CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus",
                    "car", "cat", "chair", "cow", "diningtable", "dog", "horse", "motorbike",
                    "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor", "cup", "mobile"]

        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.4: # Adjustable confidence threshold
                idx = int(detections[0, 0, i, 1])
                if 0 <= idx < len(CLASSES): # Ensure index is within bounds
                    objects.add(CLASSES[idx])
        return objects

    def _recognize_faces(self, frame, known_faces):
        """Recognize faces in frame"""
        if frame is None or frame.size == 0:
            return []

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb)
        face_encodings = face_recognition.face_encodings(rgb, face_locations)

        faces = []
        for encoding in face_encodings:
            name = "Unknown"
            if known_faces: # Only compare if known faces exist
                matches = face_recognition.compare_faces(list(known_faces.values()), encoding)
                if True in matches:
                    name = list(known_faces.keys())[matches.index(True)]
            faces.append(name)
        return faces

    def _log_activity(self, objects, faces):
        """Log detected activity"""
        # Ensure myactivity_collection exists and is not a DummyCollection
        if not (hasattr(self, 'myactivity_collection') and not isinstance(self.myactivity_collection, type(object))):
            return # Skip logging if DB is not connected

        try:
            self.myactivity_collection.insert_one({
                "timestamp": datetime.now(),
                "detected_objects": list(objects),
                "recognized_faces": faces
            })

            # Provide feedback based on recent logs to avoid spamming
            current_activity_str = f"objects:{','.join(objects)};faces:{','.join(faces)}"
            if time.time() - self._last_activity_speak_time > 10 and current_activity_str != self._last_activity_spoken: # Speak every 10 seconds if activity changes
                if "person" in objects:
                    if "Unknown" in faces:
                        self.speak("I see an unknown person.")
                    elif faces:
                        self.speak(f"Hello {faces[0]}, I see you.")
                elif objects:
                    self.speak(f"I see: {', '.join(objects)}.")
                self._last_activity_speak_time = time.time()
                self._last_activity_spoken = current_activity_str

        except Exception as e:
            print(f"Failed to log activity or speak activity: {e}")

    def _display_activity(self, frame, faces):
        """Display annotated video feed briefly."""
        if frame is None or frame.size == 0:
            return

        # Ensure frame is writeable for annotations
        if not frame.flags['WRITEABLE']:
            frame = frame.copy()

        face_locations = face_recognition.face_locations(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) # Recalculate if not passed from _recognize_faces
        for (top, right, bottom, left), name in zip(face_locations, faces):
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

        cv2.imshow("jojo Activity Monitor", frame)
        cv2.waitKey(1) # Display for a short period
        # cv2.destroyAllWindows() # Close the window immediately after display to avoid accumulation

    def quick_web_search(self, query):
        try:
            html = requests.get(f"https://www.google.com/search?q={query}", headers={"User-Agent": "Mozilla/5.0"}).text
            soup = BeautifulSoup(html, "html.parser")
            results = [r.get_text() for r in soup.select("h3")][:5]
            return results if results else ["No results found."]
        except Exception as e:
            return [f"Search error: {e}"]
        
    def jojo_generate_code(self, task_description, language="python"):
        if not hasattr(self, "gemini_model") or not self.gemini_model:
            self.speak("Gemini is not available to generate code.")
            return

        prompt = (
            f"You are jojo, a skilled {language} developer. Write clean, working code for the following task:\n"
            f"{task_description}\n"
            "Only output the code block. Do not add explanations or comments."
        )
        try:
            result = self.gemini_model.generate_content(prompt)
            code = result.text.strip()

            filename = f"generated_code_{language}_{int(time.time())}.{self._get_lang_extension(language)}"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(code)
            self.speak(f"Code saved to {filename}")

            # Optionally, execute the code if Python
            if language.lower() == "python":
                exec_result = self.execute_generated_code(code)
                self.speak(f"Execution result: {exec_result}")

        except Exception as e:
            self.speak(f"Error generating code: {e}")

    def execute_generated_code(self, code):
        """Safely execute generated Python code and return output or error."""
        try:
            local_vars = {}
            exec(code, {}, local_vars)
            return "Code executed successfully."
        except Exception as e:
            return f"Execution error: {e}"
        
# =====================
# PROGRAM ENTRY POINT
# =====================
if __name__ == "__main__":
    print_brand_name()
    jojo = None
    try:
        print("Starting jojo AI in single-threaded mode...")
        jojo = jojoAI()
        jojo.run_jojo() # Start the main single-threaded loop

    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected in main program. Shutting down jojo.")
        if jojo:
            jojo.shutdown_jojo() # Ensure proper shutdown including Pygame and CV2
    except Exception as e:
        print(f"An unhandled error occurred in the main execution block: {e}")
        if jojo:
            jojo.shutdown_jojo() # Attempt to clean up even on unexpected errors
    finally:
        # Final cleanup for pygame mixer and CV2 windows
        if pygame.mixer.get_init():
            pygame.mixer.quit()
        cv2.destroyAllWindows()
        print("jojo AI shutdown complete.")