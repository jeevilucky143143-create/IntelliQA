# Dialogue Management & Frame State Design

## 1. Dialogue Strategy

IntelliQA implements a frame-based dialogue management framework using Flask session tracking. This enables multi-turn conversations and pronoun resolution ("it", "its creator", "that") without requiring heavy language models.

---

## 2. ConversationFrame Schema

```python
class ConversationFrame:
    intent: Optional[str]            # Intent classification (e.g. 'KNOWLEDGE', 'IR', 'GREETING')
    entity: Optional[str]            # Active entity name (e.g. 'Python')
    attribute: Optional[str]         # Active attribute (e.g. 'creator')
    previous_entity: Optional[str]   # Previous entity from turn t-1
    previous_question: Optional[str] # User query text from turn t-1
    previous_answer: Optional[str]   # Generated answer text from turn t-1
    context: Dict                    # Additional metadata
    timestamp: float                 # Turn epoch timestamp
    history: List[Dict]              # Full session turn history
```

---

## 3. Pronoun Coreference Resolution Rules

When a question contains contextual pronouns, the `DialogueManager` replaces the pronoun with the active entity in the conversation frame:

1. **"Who created it?"** &rarr; `"Who created [Active Entity]?"`
2. **"What is its creator?"** &rarr; `"[Active Entity]'s creator"`
3. **"Is it open source?"** &rarr; `"Is [Active Entity] open source?"`
4. **"Tell me about it"** &rarr; `"Tell me about [Active Entity]"`

---

## 4. Multi-Turn Dialogue Walkthrough

### Turn 1:
- **User**: *"What is Python?"*
- **Router**: Detects IR/Knowledge query. Entity = `"Python"`.
- **System**: Returns overview answer. Updates frame: `entity = "Python"`.

### Turn 2:
- **User**: *"Who created it?"*
- **Router**: Detects pronoun `"it"` + active entity `"Python"` in frame &rarr; `DIALOGUE_FOLLOWUP`.
- **Resolution**: Replaces `"it"` &rarr; `"Python"`.
- **System**: Queries Knowledge Base for `"Python"` + `"creator"` &rarr; `"Python was created by Guido van Rossum."`
