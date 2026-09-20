from flask import Blueprint, render_template, request, jsonify, session, current_app
from core.query_router import QueryRouter, RouteIntent
from core.dialogue_manager import DialogueManager, ConversationFrame

qa_bp = Blueprint('qa', __name__)

# Global counter for answered questions
TOTAL_QUESTIONS_ANSWERED = 0
CONFIDENCE_SCORES_ACCUMULATED = []

def process_ask_query(query: str, session_data: dict) -> dict:
    """Helper function to execute QA query pipeline and update session state."""
    global TOTAL_QUESTIONS_ANSWERED, CONFIDENCE_SCORES_ACCUMULATED

    if not query or not query.strip():
        return {
            'answer': "Please provide a valid question.",
            'mode': 'UNKNOWN',
            'confidence': 0.0,
            'source': 'system'
        }

    ir_engine = current_app.ir_engine
    knowledge_engine = current_app.knowledge_engine
    dialogue_manager = current_app.dialogue_manager
    answer_extractor = current_app.answer_extractor
    query_router = QueryRouter(knowledge_engine)

    frame = ConversationFrame.from_dict(session_data.get('frame'))

    # Route intent
    intent, route_meta = query_router.route(query, frame)

    result = {}

    # 1. Handle Greetings / Small Talk
    if intent == RouteIntent.GREETING:
        greet_res = dialogue_manager.check_greeting_or_smalltalk(query)
        if greet_res:
            result = greet_res
        else:
            result = {
                'answer': "Hello! I am IntelliQA. How can I help you today?",
                'mode': 'DIALOGUE',
                'confidence': 1.0,
                'source': 'dialogue_manager',
                'intent': 'greeting'
            }

    # 2. Handle Dialogue Follow-up Coreference
    elif intent == RouteIntent.DIALOGUE_FOLLOWUP:
        resolved_q, was_resolved = dialogue_manager.resolve_coreference(query, frame)
        # Try knowledge lookup on resolved query first
        kb_res = knowledge_engine.query(resolved_q, entity_override=frame.entity or frame.previous_entity)
        if kb_res:
            result = {
                'answer': kb_res['answer'],
                'mode': 'KNOWLEDGE',
                'confidence': kb_res['confidence'],
                'source': kb_res['source'],
                'entity': kb_res['entity'],
                'attribute': kb_res['attribute'],
                'value': kb_res['value'],
                'context_used': was_resolved,
                'resolved_query': resolved_q
            }
        else:
            # Fallback to IR search on resolved query
            exp_q = answer_extractor.expand_query_with_synonyms(resolved_q)
            passages = ir_engine.search(exp_q, top_k=10)
            if not passages:
                passages = ir_engine.search(resolved_q, top_k=3)
            extracted = answer_extractor.extract_answer(resolved_q, passages)
            result = {
                'answer': extracted['answer'],
                'mode': 'IR',
                'confidence': extracted['confidence'],
                'source': extracted['source'],
                'passage': extracted['passage'],
                'retrieval_score': passages[0]['score'] if passages else 0.0,
                'intent': 'ir_followup',
                'context_used': was_resolved,
                'search_explanation': extracted['search_explanation']
            }

    # 3. Handle Knowledge Base QA
    elif intent == RouteIntent.KNOWLEDGE:
        kb_res = knowledge_engine.query(query)
        if kb_res:
            result = {
                'answer': kb_res['answer'],
                'mode': 'KNOWLEDGE',
                'confidence': kb_res['confidence'],
                'source': kb_res['source'],
                'entity': kb_res['entity'],
                'attribute': kb_res['attribute'],
                'value': kb_res['value'],
                'intent': 'knowledge_lookup'
            }
        else:
            # Fallback to IR if KB missed exact entity attribute
            exp_q = answer_extractor.expand_query_with_synonyms(query)
            passages = ir_engine.search(exp_q, top_k=10)
            if not passages:
                passages = ir_engine.search(query, top_k=3)
            extracted = answer_extractor.extract_answer(query, passages)
            result = {
                'answer': extracted['answer'],
                'mode': 'IR',
                'confidence': extracted['confidence'],
                'source': extracted['source'],
                'passage': extracted['passage'],
                'retrieval_score': passages[0]['score'] if passages else 0.0,
                'intent': 'factoid',
                'search_explanation': extracted['search_explanation']
            }

    # 4. Handle IR-based QA (Default)
    else:
        exp_q = answer_extractor.expand_query_with_synonyms(query)
        passages = ir_engine.search(exp_q, top_k=10)
        if not passages:
            passages = ir_engine.search(query, top_k=3)
        extracted = answer_extractor.extract_answer(query, passages)
        result = {
            'answer': extracted['answer'],
            'mode': 'IR',
            'confidence': extracted['confidence'],
            'source': extracted['source'],
            'passage': extracted['passage'],
            'retrieval_score': passages[0]['score'] if passages else 0.0,
            'intent': 'factoid',
            'search_explanation': extracted['search_explanation']
        }

    # Update session dialogue frame
    dialogue_manager.update_frame(
        frame=frame,
        user_query=query,
        bot_answer=result.get('answer', ''),
        intent=result.get('mode', 'UNKNOWN'),
        entity=result.get('entity'),
        attribute=result.get('attribute')
    )
    session_data['frame'] = frame.to_dict()

    # Track metrics
    TOTAL_QUESTIONS_ANSWERED += 1
    CONFIDENCE_SCORES_ACCUMULATED.append(result.get('confidence', 0.85))

    return result

@qa_bp.route('/chat')
def chat():
    return render_template('chat.html')

@qa_bp.route('/api/ask', methods=['POST'])
def api_ask():
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    
    response_payload = process_ask_query(query, session)
    return jsonify(response_payload)

@qa_bp.route('/api/stats', methods=['GET'])
def api_stats():
    doc_loader = current_app.document_loader
    ir_engine = current_app.ir_engine
    knowledge_engine = current_app.knowledge_engine

    doc_summaries = doc_loader.get_document_summary()
    kb_records = knowledge_engine.get_all_records()

    avg_conf = round(sum(CONFIDENCE_SCORES_ACCUMULATED) / len(CONFIDENCE_SCORES_ACCUMULATED), 2) if CONFIDENCE_SCORES_ACCUMULATED else 0.91

    return jsonify({
        'documents_indexed': len(doc_summaries),
        'total_passages': len(ir_engine.passages),
        'knowledge_records': len(kb_records),
        'questions_answered': TOTAL_QUESTIONS_ANSWERED,
        'average_confidence': avg_conf
    })

@qa_bp.route('/api/clear-session', methods=['POST'])
def api_clear_session():
    session.pop('frame', None)
    return jsonify({'status': 'success', 'message': 'Conversation session context cleared.'})
