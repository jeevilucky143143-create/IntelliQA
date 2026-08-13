from flask import Blueprint, render_template, jsonify, current_app
from core.evaluator import Evaluator
from routes.qa_routes import process_ask_query

evaluation_bp = Blueprint('evaluation', __name__)

@evaluation_bp.route('/evaluation')
def evaluation():
    return render_template('evaluation.html')

@evaluation_bp.route('/api/evaluate', methods=['POST'])
def api_run_evaluation():
    sample_csv = current_app.config['SAMPLE_QUESTIONS_CSV']
    
    # Simple wrapper over process_ask_query that mimics session
    def ask_eval_wrapper(q: str):
        dummy_session = {}
        return process_ask_query(q, dummy_session)

    evaluator = Evaluator(sample_csv, ask_eval_wrapper)
    report = evaluator.run_evaluation()

    return jsonify(report)
