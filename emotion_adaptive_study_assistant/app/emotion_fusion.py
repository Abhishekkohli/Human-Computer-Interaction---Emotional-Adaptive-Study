"""
Multimodal Emotion Fusion Module
--------------------------------
Combines facial and voice emotion detection to generate a reliable emotional profile.
Uses weighted averaging and conflict resolution strategies.
"""

from typing import Dict, Optional, Tuple
import threading
import time
from .facial_detector import get_facial_detector, FacialEmotionDetector
from .voice_detector import get_voice_detector, VoiceEmotionDetector


class EmotionFusion:
    """
    Fuses emotions from multiple modalities (face + voice) into a single reliable prediction.
    
    Fusion strategy:
    1. Weighted average based on confidence scores
    2. Agreement bonus: if both modalities agree, boost confidence
    3. Recency weighting: more recent detections have higher weight
    """
    
    # Weight for each modality (can be tuned based on reliability)
    FACIAL_WEIGHT = 0.6  # Facial expressions are often more reliable
    VOICE_WEIGHT = 0.4
    
    # Emotions that are likely to co-occur (used for conflict resolution)
    COMPATIBLE_EMOTIONS = {
        "frustrated": ["anxious", "overwhelmed"],
        "anxious": ["frustrated", "confused"],
        "confused": ["anxious", "curious"],
        "curious": ["focused", "confident"],
        "focused": ["confident", "curious"],
        "confident": ["focused", "curious"],
        "bored": ["overwhelmed"],
        "overwhelmed": ["frustrated", "bored", "anxious"]
    }
    
    def __init__(self, camera_index: int = 0, sample_rate: int = 16000):
        """
        Initialize fusion module with both detectors.
        
        Args:
            camera_index: Webcam index for facial detection
            sample_rate: Audio sample rate for voice detection
        """
        self.facial_detector = get_facial_detector(camera_index)
        self.voice_detector = get_voice_detector(sample_rate)
        
        self.is_running = False
        self.current_emotion = "focused"
        self.current_confidence = 0.5
        self.lock = threading.Lock()
        
        self._fusion_thread = None
        
        # History of recent emotions for smoothing
        self.emotion_history = []
        self.history_max_size = 5
        
    def start(self) -> bool:
        """
        Start both detectors and the fusion process.
        Returns True if at least one detector started successfully.
        """
        facial_started = self.facial_detector.start()
        voice_started = self.voice_detector.start()
        
        if not facial_started and not voice_started:
            print("[EmotionFusion] Warning: No detectors could be started")
            return False
        
        self.is_running = True
        self._fusion_thread = threading.Thread(target=self._fusion_loop, daemon=True)
        self._fusion_thread.start()
        
        print(f"[EmotionFusion] Started with facial={facial_started}, voice={voice_started}")
        return True
    
    def stop(self):
        """Stop all detectors and fusion."""
        self.is_running = False
        self.facial_detector.stop()
        self.voice_detector.stop()
        print("[EmotionFusion] Stopped emotion fusion")
    
    def _fusion_loop(self):
        """
        Background thread that continuously fuses emotions from both modalities.
        Runs every 500ms to provide responsive emotion updates.
        """
        while self.is_running:
            try:
                # Get current emotions from both detectors
                facial_emotion, facial_conf = self.facial_detector.get_current_emotion()
                voice_emotion, voice_conf = self.voice_detector.get_current_emotion()
                
                # Fuse the emotions
                fused_emotion, fused_confidence = self._fuse_emotions(
                    facial_emotion, facial_conf,
                    voice_emotion, voice_conf
                )
                
                # Apply temporal smoothing using history
                smoothed_emotion = self._apply_smoothing(fused_emotion, fused_confidence)
                
                with self.lock:
                    self.current_emotion = smoothed_emotion
                    self.current_confidence = fused_confidence
                    
            except Exception as e:
                pass
            
            time.sleep(0.5)  # Update fusion every 500ms
    
    def _fuse_emotions(
        self, 
        facial_emotion: Optional[str], 
        facial_conf: float,
        voice_emotion: Optional[str], 
        voice_conf: float
    ) -> Tuple[str, float]:
        """
        Fuse emotions from facial and voice modalities.
        
        Fusion strategy:
        1. If both agree: use that emotion with boosted confidence
        2. If one is None: use the other
        3. If they disagree: weighted vote based on confidence
        """
        # Handle missing modalities
        if facial_emotion is None and voice_emotion is None:
            return ("focused", 0.3)
        
        if facial_emotion is None:
            return (voice_emotion, voice_conf * 0.8)
        
        if voice_emotion is None:
            return (facial_emotion, facial_conf * 0.8)
        
        # Both modalities present
        
        # Case 1: Agreement - boost confidence
        if facial_emotion == voice_emotion:
            combined_conf = min(1.0, (facial_conf + voice_conf) / 2 + 0.15)
            return (facial_emotion, combined_conf)
        
        # Case 2: Compatible emotions - use higher confidence one
        if voice_emotion in self.COMPATIBLE_EMOTIONS.get(facial_emotion, []):
            # They're compatible, use the one with higher weighted confidence
            facial_score = facial_conf * self.FACIAL_WEIGHT
            voice_score = voice_conf * self.VOICE_WEIGHT
            
            if facial_score >= voice_score:
                return (facial_emotion, facial_score + voice_score * 0.3)
            else:
                return (voice_emotion, voice_score + facial_score * 0.3)
        
        # Case 3: Conflicting emotions - weighted vote
        facial_score = facial_conf * self.FACIAL_WEIGHT
        voice_score = voice_conf * self.VOICE_WEIGHT
        
        if facial_score >= voice_score:
            # Reduce confidence due to conflict
            return (facial_emotion, facial_score * 0.7)
        else:
            return (voice_emotion, voice_score * 0.7)
    
    def _apply_smoothing(self, emotion: str, confidence: float) -> str:
        """
        Apply temporal smoothing to avoid rapid emotion flickering.
        
        Uses a simple majority vote over recent history.
        """
        # Add to history
        self.emotion_history.append((emotion, confidence))
        
        # Keep only recent entries
        if len(self.emotion_history) > self.history_max_size:
            self.emotion_history = self.emotion_history[-self.history_max_size:]
        
        # Count weighted votes for each emotion
        votes = {}
        for i, (emo, conf) in enumerate(self.emotion_history):
            # More recent entries have higher weight
            recency_weight = (i + 1) / len(self.emotion_history)
            weight = conf * recency_weight
            votes[emo] = votes.get(emo, 0) + weight
        
        # Return emotion with highest weighted votes
        if votes:
            return max(votes.keys(), key=lambda e: votes[e])
        return emotion
    
    def get_current_emotion(self) -> Tuple[str, float]:
        """
        Get the current fused emotion.
        
        Returns:
            Tuple of (emotion_name, confidence_score)
        """
        with self.lock:
            return (self.current_emotion, self.current_confidence)
    
    def get_detailed_state(self) -> Dict:
        """
        Get detailed emotional state from all modalities.
        Useful for debugging and logging.
        
        Returns:
            Dict with facial, voice, and fused emotion data
        """
        facial_emotion, facial_conf = self.facial_detector.get_current_emotion()
        voice_emotion, voice_conf = self.voice_detector.get_current_emotion()
        
        with self.lock:
            fused_emotion = self.current_emotion
            fused_conf = self.current_confidence
        
        return {
            "facial": {
                "emotion": facial_emotion,
                "confidence": facial_conf
            },
            "voice": {
                "emotion": voice_emotion,
                "confidence": voice_conf
            },
            "fused": {
                "emotion": fused_emotion,
                "confidence": fused_conf
            },
            "history": list(self.emotion_history)
        }


# Singleton instance
_fusion_instance = None


def get_emotion_fusion(camera_index: int = 0, sample_rate: int = 16000) -> EmotionFusion:
    """Get or create the singleton emotion fusion instance."""
    global _fusion_instance
    if _fusion_instance is None:
        _fusion_instance = EmotionFusion(camera_index, sample_rate)
    return _fusion_instance

