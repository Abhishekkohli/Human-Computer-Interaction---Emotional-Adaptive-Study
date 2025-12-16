# Emotion-Adaptive Study Assistant

An intelligent Human-Computer Interaction (HCI) system that enhances self-directed learning by dynamically tailoring the study environment to the learner's emotional state.

## Project Overview

Unlike traditional e-learning platforms that deliver static content regardless of user experience, this system integrates:

- **Emotion Recognition**: Multimodal detection using facial expressions and voice sentiment
- **Adaptive Response Strategies**: Rule-based interventions tailored to each emotional state
- **Personalized Feedback**: Database-backed tracking for long-term personalization

## Architecture

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
│                      DATABASE (PostgreSQL)                      │
│       [Emotion Logs] [User Feedback] [Personalization]          │
└─────────────────────────────────────────────────────────────────┘
```

## Low-Level Design (LLD)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FLASK FRONTEND                                 │
│  flask_app.py                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Routes:                                                              │   │
│  │   GET  /                    → Render study UI                       │   │
│  │   GET  /api/materials/{topic} → Get study materials                 │   │
│  │   GET  /api/material/{topic}/{id} → Get specific material           │   │
│  │   POST /api/detection/start → Proxy to backend                      │   │
│  │   POST /api/detection/stop  → Proxy to backend                      │   │
│  │   GET  /api/emotion         → Proxy to backend                      │   │
│  │   GET  /api/intervention    → Proxy to backend                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ HTTP REST
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FASTAPI BACKEND                                │
│  api.py                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Endpoints:                                                           │   │
│  │   /api/detection/start  → emotion_fusion.start()                    │   │
│  │   /api/detection/stop   → emotion_fusion.stop()                     │   │
│  │   /api/emotion          → emotion_fusion.get_current_emotion()      │   │
│  │   /api/intervention     → adaptive_engine.get_intervention()        │   │
│  │   /api/users, /api/sessions, /api/feedback → Database CRUD          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
┌───────────────────────────────────┐   ┌───────────────────────────────────┐
│        EmotionFusion              │   │        AdaptiveEngine             │
│  emotion_fusion.py                │   │  adaptive_engine.py               │
├───────────────────────────────────┤   ├───────────────────────────────────┤
│  - facial_detector                │   │  - INTERVENTIONS: Dict            │
│  - voice_detector                 │   │  - COOLDOWN_PERIODS: Dict         │
│  - emotion_history: List          │   │  - last_intervention_time: Dict   │
│  - FACIAL_WEIGHT = 0.6            │   │  - intervention_counts: Dict      │
│  - VOICE_WEIGHT = 0.4             │   ├───────────────────────────────────┤
├───────────────────────────────────┤   │  + get_intervention(emotion)      │
│  + start() → bool                 │   │  + _check_cooldown(emotion)       │
│  + stop()                         │   │  + get_session_stats()            │
│  + get_current_emotion()          │   │  + reset_session()                │
│  + get_detailed_state()           │   └───────────────────────────────────┘
│  - _fuse_emotions()               │
│  - _apply_smoothing()             │
└───────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌─────────────────────┐   ┌─────────────────────┐
│ FacialEmotionDetector│   │ VoiceEmotionDetector│
│ facial_detector.py  │   │ voice_detector.py   │
├─────────────────────┤   ├─────────────────────┤
│ - cap: VideoCapture │   │ - sample_rate: int  │
│ - current_emotion   │   │ - chunk_size: int   │
│ - current_confidence│   │ - current_emotion   │
│ - EMOTION_MAP: Dict │   │ - current_confidence│
├─────────────────────┤   ├─────────────────────┤
│ + start() → bool    │   │ + start() → bool    │
│ + stop()            │   │ + stop()            │
│ + get_current_emotion│   │ + get_current_emotion│
│ - _detection_loop() │   │ - _detection_loop() │
│                     │   │ - _analyze_audio()  │
│   ┌─────────────┐   │   │   ┌─────────────┐   │
│   │  DeepFace   │   │   │   │   Librosa   │   │
│   │  .analyze() │   │   │   │  .piptrack()│   │
│   └─────────────┘   │   │   │  .rms()     │   │
└─────────────────────┘   │   │  .tempo()   │   │
                          │   └─────────────┘   │
                          └─────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DATABASE LAYER                                 │
│  database.py + models.py                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Models (SQLAlchemy ORM):                                             │   │
│  │   User ──┬── StudySession ── EmotionLog                             │   │
│  │          ├── UserFeedback                                            │   │
│  │          └── EmotionTrend                                            │   │
│  │   Intervention (linked to EmotionLog)                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Functions:                                                           │   │
│  │   init_db()  → Create all tables                                    │   │
│  │   get_db()   → Yield database session                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User interacts with UI
         │
         ▼
┌─────────────────┐    Poll every 1s    ┌─────────────────┐
│  Flask Frontend │ ─────────────────── │ FastAPI Backend │
└─────────────────┘                     └─────────────────┘
                                                 │
                              ┌──────────────────┼──────────────────┐
                              ▼                  ▼                  ▼
                     ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
                     │    Webcam    │   │  Microphone  │   │  PostgreSQL  │
                     │   (OpenCV)   │   │ (sounddevice)│   │   Database   │
                     └──────────────┘   └──────────────┘   └──────────────┘
                              │                  │
                              ▼                  ▼
                     ┌──────────────┐   ┌──────────────┐
                     │   DeepFace   │   │   Librosa    │
                     │   Analysis   │   │   Analysis   │
                     └──────────────┘   └──────────────┘
                              │                  │
                              └────────┬─────────┘
                                       ▼
                              ┌──────────────────┐
                              │  Emotion Fusion  │
                              │  (60% face +     │
                              │   40% voice)     │
                              └──────────────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Adaptive Engine  │
                              │ (Rule-based      │
                              │  interventions)  │
                              └──────────────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │  UI Displays     │
                              │  Intervention    │
                              └──────────────────┘
```

## Quick Start

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

## Project Structure

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

## Detected Emotions & Interventions

| Emotion | Detection Source | Intervention Type |
|---------|-----------------|-------------------|
| **Confused** | Facial + Voice | Hints, simplified explanations |
| **Frustrated** | Facial + Voice | Mindfulness breaks, encouragement |
| **Bored** | Facial + Voice | Gamified quizzes, challenges |
| **Curious** | Facial + Voice | Deep-dive content, advanced topics |
| **Anxious** | Facial + Voice | Reassurance, progress reminders |
| **Confident** | Facial + Voice | Advanced challenges, minimal interruption |
| **Overwhelmed** | Facial + Voice | Simplify content, suggest breaks |
| **Focused** | Facial + Voice | Suppress notifications |

## Database Setup (PostgreSQL)

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

## API Endpoints

### Emotion Detection
- `POST /api/detection/start` - Start webcam/mic detection
- `POST /api/detection/stop` - Stop detection
- `GET /api/emotion` - Get current fused emotion
- `GET /api/emotion/detailed` - Get all modality details

### Adaptive Interventions
- `GET /api/intervention` - Get intervention for current emotion

### User Management
- `POST /api/users` - Create user
- `GET /api/users/{user_id}` - Get user by ID
- `POST /api/sessions` - Start study session
- `POST /api/sessions/{session_id}/end` - End study session
- `POST /api/feedback` - Submit feedback

### Analytics
- `GET /api/stats` - Session statistics
- `GET /api/history/{user_id}` - Emotion history
- `GET /api/health` - Health check

## How It Works

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
confused    → Show hints, simplify content
frustrated  → Suggest breaks, offer encouragement
bored       → Activate gamified quizzes
overwhelmed → Reduce content, highlight key points
anxious     → Show reassurance, reduce pressure
curious     → Show deep-dive content
confident   → Increase difficulty, minimal interruption
focused     → Suppress interruptions
```

Cooldown system prevents intervention spam.

## Database Schema

```
Users
  ├── id, username, created_at
  └── → StudySessions, EmotionLogs, Feedback

StudySessions
  ├── id, user_id, topic, started_at, ended_at, is_active
  └── → EmotionLogs

EmotionLogs
  ├── id, user_id, session_id, emotion, confidence, source
  ├── facial_emotion, facial_confidence
  ├── voice_emotion, voice_confidence
  └── timestamp

Interventions
  ├── id, emotion_log_id, intervention_type, content
  ├── timestamp, was_helpful

UserFeedback
  ├── id, user_id, session_id, rating, feedback_text
  ├── feedback_type, timestamp

EmotionTrends
  ├── id, user_id, period_type, period_value
  ├── dominant_emotion, emotion_counts
  └── avg_focus_duration, updated_at
```

## Acknowledgments

- DeepFace for facial emotion recognition
- Librosa for audio analysis
- FastAPI & Flask for the web framework
- The HCI research community for foundational concepts in affective computing
