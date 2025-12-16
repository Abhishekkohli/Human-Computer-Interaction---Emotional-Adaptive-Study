"""
Facial Emotion Detection Module
-------------------------------
Uses OpenCV for video capture and DeepFace for emotion recognition.
Processes webcam stream to detect emotions like confusion, focus, frustration, boredom.
"""

import cv2
import numpy as np
from typing import Dict, Optional, Tuple
import threading
import time

# DeepFace is imported lazily to avoid slow startup
_deepface = None


def _get_deepface():
    """Lazy load DeepFace to speed up initial import."""
    global _deepface
    if _deepface is None:
        from deepface import DeepFace
        _deepface = DeepFace
    return _deepface


class FacialEmotionDetector:
    """
    Detects emotions from facial expressions using webcam feed.
    
    DeepFace returns these emotions: angry, disgust, fear, happy, sad, surprise, neutral
    We map these to our target emotions: confused, frustrated, anxious, confident, focused, etc.
    """
    
    # Mapping DeepFace emotions to our study-relevant emotions
    EMOTION_MAP = {
        "angry": "frustrated",
        "disgust": "frustrated",
        "fear": "anxious", 
        "happy": "confident",
        "sad": "overwhelmed",
        "surprise": "curious",
        "neutral": "focused"
    }
    
    def __init__(self, camera_index: int = 0):
        """
        Initialize the facial detector.
        
        Args:
            camera_index: Which camera to use (0 is usually the default webcam)
        """
        self.camera_index = camera_index
        self.cap = None
        self.is_running = False
        self.current_emotion = None
        self.current_confidence = 0.0
        self.lock = threading.Lock()
        
        # Detection runs in background thread
        self._detection_thread = None
        
    def start(self) -> bool:
        """
        Start the webcam and begin emotion detection.
        Returns True if camera opened successfully.
        """
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"[FacialDetector] Could not open camera {self.camera_index}")
                return False
            
            self.is_running = True
            self._detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self._detection_thread.start()
            print("[FacialDetector] Started facial emotion detection")
            return True
            
        except Exception as e:
            print(f"[FacialDetector] Error starting camera: {e}")
            return False
    
    def stop(self):
        """Stop detection and release camera resources."""
        self.is_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        print("[FacialDetector] Stopped facial emotion detection")
    
    def _detection_loop(self):
        """
        Background thread that continuously reads frames and detects emotions.
        Runs at ~1 detection per second to balance responsiveness and CPU usage.
        """
        DeepFace = _get_deepface()
        
        while self.is_running:
            try:
                ret, frame = self.cap.read()
                if not ret:
                    time.sleep(0.1)
                    continue
                
                # Analyze the frame for emotions
                # actions=['emotion'] tells DeepFace to only do emotion detection (faster)
                # enforce_detection=False prevents errors when no face is found
                result = DeepFace.analyze(
                    frame, 
                    actions=['emotion'],
                    enforce_detection=False,
                    silent=True
                )
                
                # DeepFace returns a list if multiple faces, we take the first
                if isinstance(result, list):
                    result = result[0]
                
                # Get the dominant emotion and its confidence
                raw_emotion = result.get('dominant_emotion', 'neutral')
                emotion_scores = result.get('emotion', {})
                confidence = emotion_scores.get(raw_emotion, 0.0) / 100.0
                
                # Map to our target emotion set
                mapped_emotion = self.EMOTION_MAP.get(raw_emotion, 'focused')
                
                # Update current state (thread-safe)
                with self.lock:
                    self.current_emotion = mapped_emotion
                    self.current_confidence = confidence
                
            except Exception as e:
                # Silently continue on detection errors (common when face not visible)
                pass
            
            # Wait before next detection (1 second interval)
            time.sleep(1.0)
    
    def get_current_emotion(self) -> Tuple[Optional[str], float]:
        """
        Get the most recently detected emotion.
        
        Returns:
            Tuple of (emotion_name, confidence_score)
            emotion_name is None if no detection has occurred yet
        """
        with self.lock:
            return (self.current_emotion, self.current_confidence)
    
    def detect_single_frame(self, frame: np.ndarray) -> Dict:
        """
        Detect emotion from a single frame (for one-shot detection).
        Useful for testing or when not using continuous detection.
        
        Args:
            frame: OpenCV image (BGR format)
            
        Returns:
            Dict with 'emotion', 'confidence', and 'all_scores'
        """
        DeepFace = _get_deepface()
        
        try:
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=False,
                silent=True
            )
            
            if isinstance(result, list):
                result = result[0]
            
            raw_emotion = result.get('dominant_emotion', 'neutral')
            emotion_scores = result.get('emotion', {})
            confidence = emotion_scores.get(raw_emotion, 0.0) / 100.0
            mapped_emotion = self.EMOTION_MAP.get(raw_emotion, 'focused')
            
            return {
                'emotion': mapped_emotion,
                'raw_emotion': raw_emotion,
                'confidence': confidence,
                'all_scores': emotion_scores
            }
            
        except Exception as e:
            return {
                'emotion': 'focused',
                'raw_emotion': 'neutral',
                'confidence': 0.0,
                'all_scores': {},
                'error': str(e)
            }
    
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame from the webcam."""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                return frame
        return None


# Singleton instance for easy access across the application
_detector_instance = None


def get_facial_detector(camera_index: int = 0) -> FacialEmotionDetector:
    """Get or create the singleton facial detector instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = FacialEmotionDetector(camera_index)
    return _detector_instance

