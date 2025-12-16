"""
FastAPI Backend API
-------------------
Provides REST API endpoints for emotion detection, adaptive interventions,
and database operations.
"""

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime

from .database import get_db, init_db
from .models import User, StudySession, EmotionLog, Intervention, UserFeedback
from .emotion_fusion import get_emotion_fusion
from .adaptive_engine import get_adaptive_engine

# Create FastAPI app
app = FastAPI(
    title="Emotion-Adaptive Study Assistant API",
    description="Backend API for emotion detection and adaptive learning interventions",
    version="1.0.0"
)

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response validation
class UserCreate(BaseModel):
    username: str

class SessionCreate(BaseModel):
    user_id: int
    topic: str

class FeedbackCreate(BaseModel):
    user_id: int
    session_id: Optional[int] = None
    rating: int
    feedback_text: Optional[str] = None
    feedback_type: str = "overall"

class EmotionResponse(BaseModel):
    emotion: str
    confidence: float
    facial_emotion: Optional[str] = None
    facial_confidence: Optional[float] = None
    voice_emotion: Optional[str] = None
    voice_confidence: Optional[float] = None

class InterventionResponse(BaseModel):
    emotion: str
    type: str
    priority: str
    message: Optional[str] = None
    actions: List[str]
    timestamp: str


# Global state for emotion detection
emotion_fusion = None
adaptive_engine = None


@app.on_event("startup")
async def startup_event():
    """Initialize database and detection systems on startup."""
    global emotion_fusion, adaptive_engine
    
    # Initialize database tables
    init_db()
    
    # Initialize emotion detection (will start when explicitly requested)
    adaptive_engine = get_adaptive_engine()
    
    print("[API] Backend started successfully")


# ============================================================
# User Management Endpoints
# ============================================================

@app.post("/api/users", response_model=Dict)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user for personalization tracking."""
    # Check if username exists
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        return {"id": existing.id, "username": existing.username, "message": "User already exists"}
    
    db_user = User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {"id": db_user.id, "username": db_user.username, "message": "User created"}


@app.get("/api/users/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "username": user.username}


# ============================================================
# Study Session Endpoints
# ============================================================

@app.post("/api/sessions", response_model=Dict)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """Start a new study session."""
    # End any active sessions for this user
    active_sessions = db.query(StudySession).filter(
        StudySession.user_id == session.user_id,
        StudySession.is_active == True
    ).all()
    
    for s in active_sessions:
        s.is_active = False
        s.ended_at = datetime.utcnow()
    
    # Create new session
    db_session = StudySession(
        user_id=session.user_id,
        topic=session.topic
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    # Reset adaptive engine for new session
    if adaptive_engine:
        adaptive_engine.reset_session()
    
    return {
        "id": db_session.id,
        "topic": db_session.topic,
        "started_at": db_session.started_at.isoformat()
    }


@app.post("/api/sessions/{session_id}/end")
def end_session(session_id: int, db: Session = Depends(get_db)):
    """End a study session."""
    session = db.query(StudySession).filter(StudySession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session.is_active = False
    session.ended_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Session ended", "duration_minutes": 
            (session.ended_at - session.started_at).total_seconds() / 60}


# ============================================================
# Emotion Detection Endpoints
# ============================================================

@app.post("/api/detection/start")
def start_detection():
    """Start emotion detection (webcam + microphone)."""
    global emotion_fusion
    
    emotion_fusion = get_emotion_fusion()
    success = emotion_fusion.start()
    
    if success:
        return {"status": "started", "message": "Emotion detection started"}
    else:
        raise HTTPException(status_code=500, detail="Failed to start detection")


@app.post("/api/detection/stop")
def stop_detection():
    """Stop emotion detection."""
    global emotion_fusion
    
    if emotion_fusion:
        emotion_fusion.stop()
        emotion_fusion = None
    
    return {"status": "stopped", "message": "Emotion detection stopped"}


@app.get("/api/emotion", response_model=EmotionResponse)
def get_current_emotion():
    """Get the current detected emotion (fused from all modalities)."""
    global emotion_fusion
    
    if not emotion_fusion:
        # Return default if detection not started
        return EmotionResponse(
            emotion="focused",
            confidence=0.5
        )
    
    detailed = emotion_fusion.get_detailed_state()
    
    return EmotionResponse(
        emotion=detailed["fused"]["emotion"],
        confidence=detailed["fused"]["confidence"],
        facial_emotion=detailed["facial"]["emotion"],
        facial_confidence=detailed["facial"]["confidence"],
        voice_emotion=detailed["voice"]["emotion"],
        voice_confidence=detailed["voice"]["confidence"]
    )


@app.get("/api/emotion/detailed")
def get_detailed_emotion():
    """Get detailed emotion state from all modalities."""
    global emotion_fusion
    
    if not emotion_fusion:
        return {
            "facial": {"emotion": None, "confidence": 0},
            "voice": {"emotion": None, "confidence": 0},
            "fused": {"emotion": "focused", "confidence": 0.5},
            "history": []
        }
    
    return emotion_fusion.get_detailed_state()


# ============================================================
# Adaptive Intervention Endpoints
# ============================================================

@app.get("/api/intervention")
def get_intervention(
    topic: Optional[str] = None,
    time_studying: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get an adaptive intervention based on current emotional state.
    This is the main endpoint the frontend polls for adaptive responses.
    """
    global emotion_fusion, adaptive_engine
    
    if not adaptive_engine:
        adaptive_engine = get_adaptive_engine()
    
    # Get current emotion
    if emotion_fusion:
        emotion, confidence = emotion_fusion.get_current_emotion()
    else:
        emotion, confidence = "focused", 0.5
    
    # Build context
    context = {}
    if topic:
        context["topic"] = topic
    if time_studying:
        context["time_studying"] = time_studying
    
    # Get intervention
    intervention = adaptive_engine.get_intervention(emotion, context)
    
    if not intervention:
        return {"intervention": None, "emotion": emotion}
    
    return {
        "intervention": intervention,
        "emotion": emotion,
        "confidence": confidence
    }




# ============================================================
# Analytics & Feedback Endpoints
# ============================================================

@app.get("/api/stats")
def get_session_stats():
    """Get statistics about interventions in the current session."""
    global adaptive_engine
    
    if not adaptive_engine:
        return {"total_interventions": 0, "emotion_distribution": {}}
    
    return adaptive_engine.get_session_stats()


@app.post("/api/feedback")
def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit user feedback about the system."""
    db_feedback = UserFeedback(
        user_id=feedback.user_id,
        session_id=feedback.session_id,
        rating=feedback.rating,
        feedback_text=feedback.feedback_text,
        feedback_type=feedback.feedback_type
    )
    db.add(db_feedback)
    db.commit()
    
    return {"message": "Feedback submitted", "id": db_feedback.id}


@app.get("/api/history/{user_id}")
def get_emotion_history(user_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Get emotion history for a user."""
    logs = db.query(EmotionLog).filter(
        EmotionLog.user_id == user_id
    ).order_by(EmotionLog.timestamp.desc()).limit(limit).all()
    
    return {
        "user_id": user_id,
        "logs": [
            {
                "emotion": log.emotion,
                "confidence": log.confidence,
                "source": log.source,
                "timestamp": log.timestamp.isoformat()
            }
            for log in logs
        ]
    }


# ============================================================
# Health Check
# ============================================================

@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "detection_active": emotion_fusion is not None,
        "timestamp": datetime.utcnow().isoformat()
    }

