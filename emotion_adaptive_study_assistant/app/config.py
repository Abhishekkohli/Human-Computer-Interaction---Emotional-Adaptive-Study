"""
Configuration settings for the Emotion-Adaptive Study Assistant.
Stores database connection strings, server ports, and other settings.
"""

import os

# Load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use environment variables directly

# Database Configuration
# PostgreSQL connection (no password needed)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres@localhost:5432/postgres"
)

# Server Ports
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))
FLASK_PORT = int(os.getenv("FLASK_PORT", 5002))

# Emotion Detection Settings
WEBCAM_INDEX = int(os.getenv("WEBCAM_INDEX", 0))
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", 16000))
DETECTION_INTERVAL = float(os.getenv("DETECTION_INTERVAL", 1.0))  # seconds

# Emotion Labels - mapping from detection models to our simplified set
EMOTION_MAPPING = {
    # DeepFace emotions -> Our simplified emotions
    "angry": "frustrated",
    "disgust": "frustrated", 
    "fear": "anxious",
    "happy": "confident",
    "sad": "overwhelmed",
    "surprise": "curious",
    "neutral": "focused",
    
    # Additional mappings for voice sentiment
    "positive": "confident",
    "negative": "frustrated",
    "calm": "focused"
}

# Our target emotion states for the adaptive system
TARGET_EMOTIONS = [
    "confused",
    "overwhelmed", 
    "frustrated",
    "bored",
    "curious",
    "anxious",
    "confident",
    "focused"
]

