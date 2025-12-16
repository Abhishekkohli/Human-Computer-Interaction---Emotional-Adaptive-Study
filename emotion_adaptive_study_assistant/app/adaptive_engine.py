"""
Adaptive Engine Module
----------------------
Rule-based system that maps emotional states to contextual interventions.
This is the core "intelligence" that makes the study assistant adaptive.
"""

from typing import Dict, List, Optional
from datetime import datetime


class AdaptiveEngine:
    """
    Maps detected emotions to appropriate study interventions.
    
    Intervention types:
    - Hints: Incremental help for confused learners
    - Breaks: Mindfulness/rest suggestions for frustrated learners
    - Challenges: Gamified quizzes for bored learners
    - Suppress: Reduce interruptions for focused learners
    - Encouragement: Positive reinforcement for confident learners
    """
    
    # Intervention templates for each emotion
    INTERVENTIONS = {
        "confused": {
            "type": "hint",
            "priority": "high",
            "messages": [
                "I notice you might be stuck. Would you like a hint? 💡",
                "Let me break this down into smaller steps...",
                "Here's a simpler way to think about this concept:",
                "Try focusing on just this one part first: ",
                "A common approach is to start by..."
            ],
            "actions": ["show_hint", "simplify_content", "show_example"]
        },
        "overwhelmed": {
            "type": "simplify",
            "priority": "high", 
            "messages": [
                "This is a lot to take in. Let's simplify. 🌟",
                "Don't worry about understanding everything at once.",
                "Let's focus on just the core concept for now.",
                "You're doing great - one step at a time!",
                "Let me highlight just the key points:"
            ],
            "actions": ["reduce_content", "highlight_key_points", "suggest_break"]
        },
        "frustrated": {
            "type": "break",
            "priority": "high",
            "messages": [
                "It's okay to feel stuck. How about a 2-minute break? 🧘",
                "Sometimes stepping away helps. Take a deep breath.",
                "You're working hard! A short pause might help refresh your mind.",
                "Let's take a quick mindfulness moment...",
                "Remember: every expert was once a beginner. You've got this!"
            ],
            "actions": ["suggest_break", "show_encouragement", "offer_alternative_topic"]
        },
        "bored": {
            "type": "challenge",
            "priority": "medium",
            "messages": [
                "Ready for a challenge? Let's make this interesting! 🎮",
                "Quick quiz time! Can you solve this?",
                "Here's a fun puzzle related to what you're learning:",
                "Let's try a more advanced example!",
                "Challenge: Can you explain this concept in your own words?"
            ],
            "actions": ["show_quiz", "increase_difficulty", "gamify_content"]
        },
        "curious": {
            "type": "explore",
            "priority": "medium",
            "messages": [
                "Great curiosity! Here's something interesting... ✨",
                "Want to dive deeper? Check this out:",
                "Fun fact related to this topic:",
                "Here's an advanced concept you might find fascinating:",
                "Since you're curious, here's how this connects to..."
            ],
            "actions": ["show_deep_dive", "suggest_related_topics", "show_advanced_content"]
        },
        "anxious": {
            "type": "reassure",
            "priority": "high",
            "messages": [
                "You're doing fine! Take your time. 💚",
                "There's no rush - learning at your own pace is best.",
                "Remember, it's okay not to know everything immediately.",
                "You've already made progress! Let's build on that.",
                "Deep breath... you've got this!"
            ],
            "actions": ["show_encouragement", "reduce_pressure", "show_progress"]
        },
        "confident": {
            "type": "encourage",
            "priority": "low",
            "messages": [
                "You're doing great! Keep up the momentum! 🚀",
                "Excellent understanding! Ready for more?",
                "You've mastered this well. Want to try something harder?",
                "Great progress! Your understanding is solid.",
                "Nice work! Consider teaching this to solidify your knowledge."
            ],
            "actions": ["increase_difficulty", "suggest_next_topic", "minimal_interruption"]
        },
        "focused": {
            "type": "suppress",
            "priority": "low",
            "messages": [
                # Minimal messages when focused - don't interrupt!
            ],
            "actions": ["suppress_notifications", "track_focus_duration", "minimal_interruption"]
        }
    }
    
    # Cooldown periods (seconds) to avoid spam
    COOLDOWN_PERIODS = {
        "confused": 30,
        "overwhelmed": 45,
        "frustrated": 60,
        "bored": 40,
        "curious": 20,
        "anxious": 45,
        "confident": 60,
        "focused": 120  # Very long cooldown for focused state
    }
    
    def __init__(self):
        """Initialize the adaptive engine."""
        self.last_intervention_time = {}  # Track when each emotion was last addressed
        self.intervention_counts = {}     # Track how many times each emotion was addressed
        self.session_interventions = []   # Log of all interventions this session
        
    def get_intervention(self, emotion: str, context: Optional[Dict] = None) -> Optional[Dict]:
        """
        Get an appropriate intervention for the detected emotion.
        
        Args:
            emotion: The detected emotional state
            context: Optional context (topic, time studying, etc.)
            
        Returns:
            Dict with intervention details, or None if no intervention needed
        """
        # Check if this emotion has interventions defined
        if emotion not in self.INTERVENTIONS:
            return None
        
        # Check cooldown - don't spam interventions
        if not self._check_cooldown(emotion):
            return None
        
        intervention_config = self.INTERVENTIONS[emotion]
        
        # Special case: focused state - rarely interrupt
        if emotion == "focused":
            return self._handle_focused_state()
        
        # Select a message (rotate through them to add variety)
        messages = intervention_config["messages"]
        if not messages:
            return None
            
        # Get message index based on how many times we've intervened for this emotion
        count = self.intervention_counts.get(emotion, 0)
        message_index = count % len(messages)
        message = messages[message_index]
        
        # Update tracking
        self.intervention_counts[emotion] = count + 1
        self.last_intervention_time[emotion] = datetime.now()
        
        # Build intervention response
        intervention = {
            "emotion": emotion,
            "type": intervention_config["type"],
            "priority": intervention_config["priority"],
            "message": message,
            "actions": intervention_config["actions"],
            "timestamp": datetime.now().isoformat()
        }
        
        # Add context-specific modifications
        if context:
            intervention = self._apply_context(intervention, context)
        
        # Log the intervention
        self.session_interventions.append(intervention)
        
        return intervention
    
    def _check_cooldown(self, emotion: str) -> bool:
        """
        Check if enough time has passed since the last intervention for this emotion.
        
        Returns:
            True if intervention is allowed, False if still in cooldown
        """
        if emotion not in self.last_intervention_time:
            return True
        
        last_time = self.last_intervention_time[emotion]
        cooldown = self.COOLDOWN_PERIODS.get(emotion, 30)
        elapsed = (datetime.now() - last_time).total_seconds()
        
        return elapsed >= cooldown
    
    def _handle_focused_state(self) -> Optional[Dict]:
        """
        Handle focused state - minimize interruptions.
        Only return intervention after extended focus for encouragement.
        """
        # Check if we should log focus time (every 10 minutes)
        if "focused" in self.last_intervention_time:
            elapsed = (datetime.now() - self.last_intervention_time["focused"]).total_seconds()
            if elapsed < 600:  # 10 minutes
                return None
        
        self.last_intervention_time["focused"] = datetime.now()
        
        # Silently track focus - no visible intervention
        return {
            "emotion": "focused",
            "type": "suppress",
            "priority": "low",
            "message": None,  # No message - don't interrupt
            "actions": ["track_focus_duration"],
            "timestamp": datetime.now().isoformat(),
            "silent": True
        }
    
    def _apply_context(self, intervention: Dict, context: Dict) -> Dict:
        """
        Modify intervention based on study context.
        
        Context might include:
        - topic: Current study topic
        - time_studying: How long user has been studying
        - difficulty: Current material difficulty
        """
        # Add topic-specific hints if available
        if "topic" in context and intervention["type"] == "hint":
            intervention["topic"] = context["topic"]
        
        # Suggest break if studying for too long
        if "time_studying" in context:
            minutes = context["time_studying"]
            if minutes > 45 and intervention["type"] in ["simplify", "break"]:
                intervention["message"] += f"\n(You've been studying for {minutes} minutes - great dedication!)"
        
        return intervention
    
    def get_session_stats(self) -> Dict:
        """
        Get statistics about interventions in the current session.
        Useful for analyzing which emotions are most common.
        """
        emotion_counts = {}
        for intervention in self.session_interventions:
            emotion = intervention["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        return {
            "total_interventions": len(self.session_interventions),
            "emotion_distribution": emotion_counts,
            "intervention_counts": dict(self.intervention_counts)
        }
    
    def reset_session(self):
        """Reset session-specific data (call when starting new study session)."""
        self.last_intervention_time = {}
        self.intervention_counts = {}
        self.session_interventions = []


# Singleton instance
_engine_instance = None


def get_adaptive_engine() -> AdaptiveEngine:
    """Get or create the singleton adaptive engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = AdaptiveEngine()
    return _engine_instance

