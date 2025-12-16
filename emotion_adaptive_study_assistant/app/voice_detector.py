"""
Voice Sentiment Detection Module
--------------------------------
Captures audio from microphone and analyzes for emotional cues.
Uses audio features (pitch, energy, tempo) to infer emotional state.
"""

import numpy as np
from typing import Dict, Optional, Tuple
import threading
import time

# These are imported lazily to avoid slow startup
_sounddevice = None
_librosa = None


def _get_sounddevice():
    """Lazy load sounddevice."""
    global _sounddevice
    if _sounddevice is None:
        import sounddevice as sd
        _sounddevice = sd
    return _sounddevice


def _get_librosa():
    """Lazy load librosa."""
    global _librosa
    if _librosa is None:
        import librosa
        _librosa = librosa
    return _librosa


class VoiceEmotionDetector:
    """
    Detects emotions from voice/audio input.
    
    Uses audio features to infer emotional state:
    - High pitch + high energy -> anxious/frustrated
    - Low pitch + low energy -> bored/overwhelmed  
    - Moderate pitch + steady energy -> focused/confident
    - High variance in pitch -> confused/curious
    """
    
    def __init__(self, sample_rate: int = 16000, chunk_duration: float = 2.0):
        """
        Initialize voice detector.
        
        Args:
            sample_rate: Audio sample rate in Hz
            chunk_duration: Duration of each audio chunk to analyze (seconds)
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.chunk_size = int(sample_rate * chunk_duration)
        
        self.is_running = False
        self.current_emotion = None
        self.current_confidence = 0.0
        self.lock = threading.Lock()
        
        self._detection_thread = None
        self._audio_buffer = []
        
    def start(self) -> bool:
        """
        Start audio capture and emotion detection.
        Returns True if microphone opened successfully.
        """
        try:
            sd = _get_sounddevice()
            
            # Test if microphone is available
            devices = sd.query_devices()
            
            self.is_running = True
            self._detection_thread = threading.Thread(target=self._detection_loop, daemon=True)
            self._detection_thread.start()
            print("[VoiceDetector] Started voice emotion detection")
            return True
            
        except Exception as e:
            print(f"[VoiceDetector] Error starting microphone: {e}")
            return False
    
    def stop(self):
        """Stop voice detection."""
        self.is_running = False
        print("[VoiceDetector] Stopped voice emotion detection")
    
    def _detection_loop(self):
        """
        Background thread that continuously records audio and detects emotions.
        Records 2-second chunks and analyzes each for emotional content.
        """
        sd = _get_sounddevice()
        librosa = _get_librosa()
        
        while self.is_running:
            try:
                # Record a chunk of audio
                audio = sd.rec(
                    self.chunk_size, 
                    samplerate=self.sample_rate, 
                    channels=1, 
                    dtype='float32'
                )
                sd.wait()  # Wait for recording to complete
                
                # Flatten to 1D array
                audio = audio.flatten()
                
                # Skip silent chunks (no speech detected)
                if np.max(np.abs(audio)) < 0.01:
                    with self.lock:
                        # No voice detected, default to focused
                        self.current_emotion = "focused"
                        self.current_confidence = 0.3
                    continue
                
                # Extract audio features and classify emotion
                emotion, confidence = self._analyze_audio(audio, librosa)
                
                with self.lock:
                    self.current_emotion = emotion
                    self.current_confidence = confidence
                    
            except Exception as e:
                # Continue on errors (common with audio devices)
                time.sleep(0.5)
    
    def _analyze_audio(self, audio: np.ndarray, librosa) -> Tuple[str, float]:
        """
        Analyze audio features to determine emotional state.
        
        Uses simple heuristics based on:
        - Pitch (fundamental frequency)
        - Energy (volume/loudness)
        - Speech rate (tempo)
        - Pitch variance (stability of voice)
        
        Returns:
            Tuple of (emotion, confidence)
        """
        try:
            # Extract pitch using librosa
            pitches, magnitudes = librosa.piptrack(
                y=audio, 
                sr=self.sample_rate,
                fmin=50,
                fmax=400
            )
            
            # Get the dominant pitch for each frame
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if not pitch_values:
                return ("focused", 0.3)
            
            # Calculate pitch statistics
            mean_pitch = np.mean(pitch_values)
            pitch_std = np.std(pitch_values)
            
            # Calculate energy (RMS)
            rms = librosa.feature.rms(y=audio)[0]
            mean_energy = np.mean(rms)
            
            # Calculate tempo/speech rate
            onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
            tempo = librosa.feature.tempo(onset_envelope=onset_env, sr=self.sample_rate)[0]
            
            # Simple rule-based classification
            # These thresholds are approximate and could be tuned with real data
            
            # High energy + high pitch variance = frustrated/anxious
            if mean_energy > 0.1 and pitch_std > 50:
                if mean_pitch > 200:
                    return ("frustrated", 0.7)
                else:
                    return ("anxious", 0.6)
            
            # Low energy + low tempo = bored/overwhelmed
            if mean_energy < 0.03 and tempo < 80:
                if pitch_std < 20:
                    return ("bored", 0.6)
                else:
                    return ("overwhelmed", 0.5)
            
            # High pitch variance with moderate energy = confused/curious
            if pitch_std > 40 and mean_energy > 0.03:
                if tempo > 100:
                    return ("curious", 0.6)
                else:
                    return ("confused", 0.5)
            
            # Moderate, stable voice = focused/confident
            if mean_energy > 0.05 and pitch_std < 30:
                if mean_pitch > 150:
                    return ("confident", 0.7)
                else:
                    return ("focused", 0.7)
            
            # Default to focused
            return ("focused", 0.5)
            
        except Exception as e:
            return ("focused", 0.3)
    
    def get_current_emotion(self) -> Tuple[Optional[str], float]:
        """
        Get the most recently detected voice emotion.
        
        Returns:
            Tuple of (emotion_name, confidence_score)
        """
        with self.lock:
            return (self.current_emotion, self.current_confidence)
    
    def analyze_audio_chunk(self, audio: np.ndarray) -> Dict:
        """
        Analyze a single audio chunk (for one-shot detection).
        
        Args:
            audio: Numpy array of audio samples
            
        Returns:
            Dict with emotion analysis results
        """
        librosa = _get_librosa()
        emotion, confidence = self._analyze_audio(audio, librosa)
        
        return {
            'emotion': emotion,
            'confidence': confidence
        }


# Singleton instance
_detector_instance = None


def get_voice_detector(sample_rate: int = 16000) -> VoiceEmotionDetector:
    """Get or create the singleton voice detector instance."""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = VoiceEmotionDetector(sample_rate)
    return _detector_instance

