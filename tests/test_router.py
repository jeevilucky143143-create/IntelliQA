import pytest
from core.query_router import QueryRouter, RouteIntent
from core.dialogue_manager import ConversationFrame

class MockKnowledgeEngine:
    def detect_entity_and_attribute(self, query):
        if "python" in query.lower():
            return "Python", "creator"
        return None, None

def test_query_router():
    ke = MockKnowledgeEngine()
    router = QueryRouter(ke)

    # Greeting
    intent1, _ = router.route("Hello")
    assert intent1 == RouteIntent.GREETING

    # Dialogue follow-up
    frame = ConversationFrame()
    frame.entity = "Python"
    intent2, _ = router.route("Who created it?", frame)
    assert intent2 == RouteIntent.DIALOGUE_FOLLOWUP

    # Knowledge
    intent3, _ = router.route("Who created Python?")
    assert intent3 == RouteIntent.KNOWLEDGE

    # IR Factoid
    intent4, _ = router.route("What is quantum neural network architecture?")
    assert intent4 == RouteIntent.IR
