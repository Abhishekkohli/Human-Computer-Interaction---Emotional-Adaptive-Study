"""
SQLAlchemy ORM models for storing emotional trends and user feedback.
These enable long-term personalization as mentioned in the project abstract.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    """
    User model - stores basic user information for personalization.
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    emotion_logs = relationship("EmotionLog", back_populates="user")
    study_sessions = relationship("StudySession", back_populates="user")
    feedback = relationship("UserFeedback", back_populates="user")


class StudySession(Base):
    """
    Tracks individual study sessions for a user.
    Links emotions detected during a specific study period.
    """
    __tablename__ = "study_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String(200))  # What the user is studying
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="study_sessions")
    emotion_logs = relationship("EmotionLog", back_populates="session")


class EmotionLog(Base):
    """
    Stores each detected emotion with timestamp.
    Used for analyzing emotional trends over time.
    """
    __tablename__ = "emotion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=True)
    
    # Detected emotion and confidence scores
    emotion = Column(String(50))  # confused, frustrated, bored, etc.
    confidence = Column(Float)    # 0.0 to 1.0
    
    # Source of detection (for multimodal fusion analysis)
    source = Column(String(20))   # "facial", "voice", or "fused"
    
    # Raw scores from each modality (useful for debugging/analysis)
    facial_emotion = Column(String(50), nullable=True)
    facial_confidence = Column(Float, nullable=True)
    voice_emotion = Column(String(50), nullable=True)
    voice_confidence = Column(Float, nullable=True)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="emotion_logs")
    session = relationship("StudySession", back_populates="emotion_logs")


class Intervention(Base):
    """
    Logs interventions triggered by the adaptive engine.
    Helps analyze which interventions work best for each emotion.
    """
    __tablename__ = "interventions"
    
    id = Column(Integer, primary_key=True, index=True)
    emotion_log_id = Column(Integer, ForeignKey("emotion_logs.id"))
    
    intervention_type = Column(String(100))  # hint, break, quiz, suppress
    content = Column(Text)                    # The actual intervention message
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Was the intervention helpful? (collected from user feedback)
    was_helpful = Column(Boolean, nullable=True)


class UserFeedback(Base):
    """
    Explicit user feedback on system performance.
    Enables long-term personalization and system improvement.
    """
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=True)
    
    # Rating and comments
    rating = Column(Integer)  # 1-5 stars
    feedback_text = Column(Text, nullable=True)
    
    # What aspect of the system is being rated
    feedback_type = Column(String(50))  # "emotion_accuracy", "intervention_helpfulness", "overall"
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="feedback")


class EmotionTrend(Base):
    """
    Aggregated emotion statistics for personalization.
    Stores patterns like "user tends to get frustrated in the evening"
    """
    __tablename__ = "emotion_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Aggregation period
    period_type = Column(String(20))  # "hourly", "daily", "weekly"
    period_value = Column(String(50)) # e.g., "14:00", "Monday", "Week 45"
    
    # Emotion distribution during this period
    dominant_emotion = Column(String(50))
    emotion_counts = Column(Text)  # JSON string of {emotion: count}
    
    # Average study effectiveness during this period
    avg_focus_duration = Column(Float, nullable=True)  # minutes
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

