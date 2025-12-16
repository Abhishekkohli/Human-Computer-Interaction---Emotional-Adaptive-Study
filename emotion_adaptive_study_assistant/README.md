# 🎓 Emotion-Adaptive Study Assistant

An intelligent Human-Computer Interaction (HCI) system that enhances self-directed learning by dynamically tailoring the study environment to the learner's emotional state.

## 📋 Project Overview

Unlike traditional e-learning platforms that deliver static content regardless of user experience, this system integrates:

- **Emotion Recognition**: Multimodal detection using facial expressions and voice sentiment
- **Adaptive Response Strategies**: Rule-based interventions tailored to each emotional state
- **Personalized Feedback**: Database-backed tracking for long-term personalization

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Flask - Port 5002)                 │
│         [Study Materials] [Timer] [Adaptive Prompts]            │
└─────────────────────────────────────────────────────────────────┘
                              ▲
                              │ REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND (FastAPI - Port 8000)                  │
│                [Rule-Based Adaptive Engine]                     │
│           Emotion Classification → Intervention Mapping         │
└─────────────────────────────────────────────────────────────────┘
                              ▲
            ┌─────────────────┴─────────────────┐
            │       EMOTION FUSION LAYER        │
            └───────────────┬───────────────────┘
                ┌───────────┴───────────┐
                ▼                       ▼
┌─────────────────────┐   ┌─────────────────────────┐
│   FACIAL ANALYSIS   │   │   VOICE SENTIMENT       │
│   (OpenCV/DeepFace) │   │   (Librosa)             │
│   Webcam Stream     │   │   Microphone Input      │
└─────────────────────┘   └─────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 DATABASE (PostgreSQL/SQLite)                    │
│       [Emotion Logs] [User Feedback] [Personalization]          │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd emotion_adaptive_study_assistant
pip install -r requirements.txt
```

**Note**: Some dependencies (DeepFace, TensorFlow) may take a while to install.

### 2. Run the Application

```bash
# Run both backend and frontend (recommended)
python run.py

# Or run them separately:
python run.py --backend   # FastAPI on port 8000
python run.py --frontend  # Flask on port 5002
```

### 3. Open in Browser

Navigate to **http://localhost:5002** to start using the study assistant.

## 📁 Project Structure

```
emotion_adaptive_study_assistant/
├── app/
│   ├── __init__.py
│   ├── config.py           # Configuration settings
│   ├── database.py         # Database connection (SQLAlchemy)
│   ├── models.py           # ORM models (User, EmotionLog, etc.)
│   ├── facial_detector.py  # Facial emotion detection (OpenCV + DeepFace)
│   ├── voice_detector.py   # Voice sentiment detection (Librosa)
│   ├── emotion_fusion.py   # Multimodal fusion of face + voice
│   ├── adaptive_engine.py  # Rule-based intervention engine
│   └── api.py              # FastAPI REST endpoints
├── frontend/
│   ├── __init__.py
│   └── flask_app.py        # Flask web interface
├── requirements.txt        # Python dependencies
├── run.py                  # Main entry point
└── README.md               # This file
```

## 🎭 Detected Emotions & Interventions

| Emotion | Detection Source | Intervention Type |
|---------|-----------------|-------------------|
| **Confused** | Facial analysis | Hints, simplified explanations |
| **Frustrated** | Facial + Voice | Mindfulness breaks, encouragement |
| **Bored** | Facial analysis | Gamified quizzes, challenges |
| **Curious** | Voice tone | Deep-dive content, advanced topics |
| **Anxious** | Facial + Voice | Reassurance, progress reminders |
| **Confident** | Voice + Facial | Advanced challenges, minimal interruption |
| 🎯 **Focused** | Sustained neutral | Suppress notifications |

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Database (defaults to SQLite if not set)
DATABASE_URL=postgresql://user:password@localhost:5432/emotion_study_db

# Server Ports
FASTAPI_PORT=8000
FLASK_PORT=5002

# Detection Settings
WEBCAM_INDEX=0
AUDIO_SAMPLE_RATE=16000
```

### Database Setup (PostgreSQL)

The system is configured to connect to PostgreSQL with the following settings:

```
Host: localhost
Port: 5432
Database: postgres
Username: postgres
Password: (none)
```

Connection string: `postgresql://postgres@localhost:5432/postgres`

Make sure PostgreSQL is running on your machine.

## 🔌 API Endpoints

### Emotion Detection
- `POST /api/detection/start` - Start webcam/mic detection
- `POST /api/detection/stop` - Stop detection
- `GET /api/emotion` - Get current fused emotion
- `GET /api/emotion/detailed` - Get all modality details

### Adaptive Interventions
- `GET /api/intervention` - Get intervention for current emotion
- `POST /api/emotion/manual?emotion=confused` - Test with manual emotion

### User Management
- `POST /api/users` - Create user
- `POST /api/sessions` - Start study session
- `POST /api/feedback` - Submit feedback

### Analytics
- `GET /api/stats` - Session statistics
- `GET /api/history/{user_id}` - Emotion history

## 💡 How It Works

### 1. Emotion Detection (Multimodal)

**Facial Analysis** (OpenCV + DeepFace):
- Captures webcam stream continuously
- Detects facial expressions every ~1 second
- Maps DeepFace emotions to our target set

**Voice Analysis** (Librosa):
- Captures 2-second audio chunks
- Extracts pitch, energy, tempo features
- Classifies based on audio patterns

### 2. Emotion Fusion

- Weighted combination of face (60%) and voice (40%)
- Agreement bonus when modalities align
- Temporal smoothing to avoid flickering

### 3. Adaptive Engine

Rule-based mapping:
```
confused → Show hints, simplify content
frustrated → Suggest breaks, offer encouragement
bored → Activate gamified quizzes
focused → Suppress interruptions
```

Cooldown system prevents intervention spam.

## 🧪 Testing Without Webcam/Microphone

The system includes manual emotion testing buttons in the UI sidebar. Click any emotion to simulate detection and see the adaptive response.

## 📊 Database Schema

```
Users
  ├── id, username, created_at
  └── → StudySessions, EmotionLogs, Feedback

StudySessions
  ├── id, user_id, topic, started_at, ended_at
  └── → EmotionLogs

EmotionLogs
  ├── id, emotion, confidence, source
  ├── facial_emotion, facial_confidence
  ├── voice_emotion, voice_confidence
  └── timestamp

Interventions
  ├── id, emotion_log_id, type, content
  └── was_helpful

UserFeedback
  ├── id, user_id, rating, feedback_text
  └── feedback_type
```


## 🙏 Acknowledgments

- DeepFace for facial emotion recognition
- Librosa for audio analysis
- FastAPI & Flask for the web framework
- The HCI research community for foundational concepts in affective computing

