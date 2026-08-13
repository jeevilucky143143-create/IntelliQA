import re
from typing import Dict, Tuple, Optional
from core.dialogue_manager import GREETINGS, ConversationFrame

class RouteIntent:
    GREETING = "GREETING"
    KNOWLEDGE = "KNOWLEDGE"
    DIALOGUE_FOLLOWUP = "DIALOGUE_FOLLOWUP"
    IR = "IR"
    UNKNOWN = "UNKNOWN"

class QueryRouter:
    """Intelligently routes user queries to the appropriate QA engine or dialogue manager."""

    def __init__(self, knowledge_engine=None):
        self.knowledge_engine = knowledge_engine

    def route(self, query: str, frame: Optional[ConversationFrame] = None) -> Tuple[str, Dict]:
        """
        Classifies user query.
        Returns (intent, metadata_dict).
        """
        q_lower = query.strip().lower().rstrip('.!?')

        # 1. Check for small talk / greetings
        for g_key in GREETINGS.keys():
            if q_lower == g_key or q_lower.startswith(g_key):
                return RouteIntent.GREETING, {'reason': 'Matches greeting dictionary'}

        # 2. Check for dialogue follow-up pronouns
        pronoun_triggers = [r'\b(it|its|that|this|the creator|who created it|what about)\b']
        if frame and (frame.entity or frame.previous_entity):
            for pattern in pronoun_triggers:
                if re.search(pattern, q_lower):
                    return RouteIntent.DIALOGUE_FOLLOWUP, {
                        'reason': 'Contains contextual pronoun referring to session entity',
                        'active_entity': frame.entity or frame.previous_entity
                    }

        # 3. Check for Knowledge Base entity match
        if self.knowledge_engine:
            entity, attribute = self.knowledge_engine.detect_entity_and_attribute(query)
            if entity and (attribute or any(kw in q_lower for kw in ['who', 'type', 'created', 'year', 'language', 'creator', 'version'])):
                return RouteIntent.KNOWLEDGE, {
                    'reason': 'Matches structured knowledge base entity and attribute',
                    'entity': entity,
                    'attribute': attribute
                }

        # 4. Default to IR Factoid QA engine
        return RouteIntent.IR, {'reason': 'Factoid or unstructured document query'}
