import time
import re
from typing import Dict, Optional, List, Tuple

GREETINGS = {
    'hello': "Hello! I'm IntelliQA. I can answer questions using documents, structured knowledge, and conversation context.",
    'hi': "Hi there! How can I assist you with information retrieval or knowledge queries today?",
    'good morning': "Good morning! Welcome to IntelliQA.",
    'good afternoon': "Good afternoon! How can I help you today?",
    'thank you': "You're very welcome! Feel free to ask if you have more questions.",
    'thanks': "Glad I could help!",
    'bye': "Goodbye! Have a great day ahead.",
    'who are you': "I am IntelliQA, an Intelligent Question Answering & Conversational Assistant powered by Flask.",
    'what can you do': "I can perform IR-based factoid answering from text documents, query structured knowledge databases, and maintain dialogue context across conversational turns."
}

class ConversationFrame:
    """Frame structure holding dialogue state for a session."""

    def __init__(self):
        self.intent: Optional[str] = None
        self.entity: Optional[str] = None
        self.attribute: Optional[str] = None
        self.previous_entity: Optional[str] = None
        self.previous_question: Optional[str] = None
        self.previous_answer: Optional[str] = None
        self.context: Dict = {}
        self.timestamp: float = time.time()
        self.history: List[Dict] = []

    def to_dict(self) -> Dict:
        """Serialize frame to dictionary for Flask session storage."""
        return {
            'intent': self.intent,
            'entity': self.entity,
            'attribute': self.attribute,
            'previous_entity': self.previous_entity,
            'previous_question': self.previous_question,
            'previous_answer': self.previous_answer,
            'context': self.context,
            'timestamp': self.timestamp,
            'history': self.history
        }

    @classmethod
    def from_dict(cls, data: Optional[Dict]) -> 'ConversationFrame':
        """Deserialize frame from session dictionary."""
        frame = cls()
        if data:
            frame.intent = data.get('intent')
            frame.entity = data.get('entity')
            frame.attribute = data.get('attribute')
            frame.previous_entity = data.get('previous_entity')
            frame.previous_question = data.get('previous_question')
            frame.previous_answer = data.get('previous_answer')
            frame.context = data.get('context', {})
            frame.timestamp = data.get('timestamp', time.time())
            frame.history = data.get('history', [])
        return frame

class DialogueManager:
    """Manages multi-turn conversation state, coreference resolution, and small talk interactions."""

    def check_greeting_or_smalltalk(self, query: str) -> Optional[Dict]:
        """Detect and return static response for common greetings/chitchat."""
        q_clean = query.strip().lower().rstrip('!?')
        
        for phrase, response in GREETINGS.items():
            if q_clean == phrase or q_clean.startswith(phrase):
                return {
                    'answer': response,
                    'mode': 'DIALOGUE',
                    'confidence': 1.0,
                    'source': 'dialogue_manager',
                    'intent': 'greeting',
                    'entity': None,
                    'context_used': False
                }
        return None

    def resolve_coreference(self, query: str, frame: ConversationFrame) -> Tuple[str, bool]:
        """
        Substitute pronouns ('it', 'its', 'that', 'this') with the active entity from conversation frame.
        Returns (resolved_query, was_resolved).
        """
        q_lower = query.lower()
        active_entity = frame.entity or frame.previous_entity
        
        if not active_entity:
            return query, False

        # Pronouns to replace
        pronoun_patterns = [
            (r'\b(who created|who built|who wrote|who made) (it|that|this)\b', r'\1 ' + active_entity),
            (r'\b(what is|what type is) (it|that|this)\b', r'\1 ' + active_entity),
            (r'\bits (creator|author|developer|type|release year)\b', active_entity + r"'s \1"),
            (r'\bis (it|that|this) open source\b', f"Is {active_entity} open source"),
            (r'\b(about|tell me about) (it|that|this)\b', r'\1 ' + active_entity),
            (r'\b(it|that)\b', active_entity)
        ]

        resolved = query
        was_resolved = False
        for pattern, replacement in pronoun_patterns:
            if re.search(pattern, resolved, re.IGNORECASE):
                resolved = re.sub(pattern, replacement, resolved, flags=re.IGNORECASE)
                was_resolved = True
                break

        return resolved, was_resolved

    def update_frame(self, frame: ConversationFrame, user_query: str, bot_answer: str, intent: str, entity: Optional[str] = None, attribute: Optional[str] = None):
        """Update conversation frame after completing turn."""
        if entity:
            frame.previous_entity = frame.entity
            frame.entity = entity
            
        frame.previous_question = user_query
        frame.previous_answer = bot_answer
        frame.intent = intent
        if attribute:
            frame.attribute = attribute
        frame.timestamp = time.time()
        
        # Append turn to history
        frame.history.append({
            'user': user_query,
            'bot': bot_answer,
            'intent': intent,
            'entity': entity,
            'timestamp': time.time()
        })
