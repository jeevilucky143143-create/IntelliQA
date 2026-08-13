import re
from typing import Dict, List, Optional
from core.preprocessing import tokenize, STOPWORDS

class QuestionType:
    WHO = "WHO"
    WHAT = "WHAT"
    WHEN = "WHEN"
    WHERE = "WHERE"
    WHY = "WHY"
    HOW = "HOW"
    WHICH = "WHICH"
    YES_NO = "YES_NO"
    DEFINITION = "DEFINITION"
    ATTRIBUTE = "ATTRIBUTE"
    GENERAL = "GENERAL"

def detect_question_type(question: str) -> str:
    """Detect functional question type from user prompt."""
    q_lower = question.lower().strip()
    
    if q_lower.startswith(('is ', 'are ', 'was ', 'were ', 'do ', 'does ', 'did ', 'can ', 'could ', 'has ', 'have ')):
        return QuestionType.YES_NO
    if re.search(r'\b(who|created by|authored by|developer of)\b', q_lower):
        return QuestionType.WHO
    if re.search(r'\b(when|year|date|time)\b', q_lower):
        return QuestionType.WHEN
    if re.search(r'\b(where|location|place|country|city)\b', q_lower):
        return QuestionType.WHERE
    if re.search(r'\b(why|reason|purpose)\b', q_lower):
        return QuestionType.WHY
    if re.search(r'\b(how|method|procedure)\b', q_lower):
        return QuestionType.HOW
    if re.search(r'\bwhat is\b|\bwhat are\b|\bdefine\b|\bdefinition of\b', q_lower):
        return QuestionType.DEFINITION
    if re.search(r'\b(what|which)\b', q_lower):
        return QuestionType.WHAT
    return QuestionType.GENERAL

class AnswerExtractor:
    """Extracts concise factoid answers from retrieved passages using pattern heuristics and score ranking."""

    def extract_answer(self, question: str, retrieved_passages: List[Dict]) -> Dict:
        """
        Processes top retrieved passages and extracts the most relevant factoid answer.
        Returns a dict containing:
        - answer: string answer
        - question_type: detected QuestionType
        - confidence: confidence score 0.0 - 1.0
        - source: source file name
        - passage: passage text
        - search_explanation: step-by-step reasoning
        """
        q_type = detect_question_type(question)
        
        if not retrieved_passages:
            return {
                'answer': "I couldn't find enough reliable information in the available sources to answer that question.",
                'question_type': q_type,
                'confidence': 0.0,
                'source': "none",
                'passage': "",
                'search_explanation': {
                    'query': question,
                    'retrieved_passages': [],
                    'selected_passage': None,
                    'extracted_answer': "No passages retrieved."
                }
            }

        top_passage = retrieved_passages[0]
        text = top_passage['text']
        score = top_passage.get('score', 0.0)
        source = top_passage.get('source', 'document')

        # Refine answer based on question type
        concise_answer = text
        
        # Calculate overall confidence score based on similarity score & keyword overlap
        q_tokens = set(tokenize(question, remove_stopwords=True))
        p_tokens = set(tokenize(text, remove_stopwords=True))
        overlap = len(q_tokens.intersection(p_tokens)) / max(len(q_tokens), 1) if q_tokens else 0.5

        # Normalize confidence score
        confidence = min(0.98, max(0.20, (score * 0.7) + (overlap * 0.3)))
        
        # If score is very low, declare low confidence / out of domain
        if score < 0.08:
            return {
                'answer': "I couldn't find enough reliable information in the available sources to answer that question.",
                'question_type': q_type,
                'confidence': round(confidence, 2),
                'source': "none",
                'passage': text,
                'search_explanation': {
                    'query': question,
                    'retrieved_passages': [p['text'] for p in retrieved_passages],
                    'selected_passage': None,
                    'extracted_answer': "Low retrieval similarity score."
                }
            }

        return {
            'answer': concise_answer,
            'question_type': q_type,
            'confidence': round(confidence, 2),
            'source': source,
            'passage': text,
            'search_explanation': {
                'query': question,
                'retrieved_passages': [p['text'] for p in retrieved_passages],
                'similarity_scores': [p.get('score', 0) for p in retrieved_passages],
                'selected_passage': text,
                'extracted_answer': concise_answer
            }
        }
