import pytest
from core.dialogue_manager import DialogueManager, ConversationFrame

def test_greeting_detection():
    dm = DialogueManager()
    res = dm.check_greeting_or_smalltalk("Hello")
    assert res is not None
    assert res['mode'] == 'DIALOGUE'
    assert "IntelliQA" in res['answer']

def test_coreference_resolution():
    dm = DialogueManager()
    frame = ConversationFrame()
    frame.entity = "Python"

    resolved, was_resolved = dm.resolve_coreference("Who created it?", frame)
    assert was_resolved is True
    assert "Python" in resolved

    resolved_creator, was_resolved2 = dm.resolve_coreference("What is its creator?", frame)
    assert was_resolved2 is True
    assert "Python" in resolved_creator

def test_frame_serialization():
    frame = ConversationFrame()
    frame.entity = "Flask"
    frame.intent = "KNOWLEDGE"
    
    d = frame.to_dict()
    assert d['entity'] == "Flask"

    reloaded = ConversationFrame.from_dict(d)
    assert reloaded.entity == "Flask"
