import os
try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional dependency for local dev setup
    def load_dotenv():
        return False
from flask import Flask, render_template, jsonify

load_dotenv()

from config import Config
from core.document_loader import DocumentLoader
from core.ir_engine import IREngine
from core.knowledge_engine import KnowledgeEngine
from core.dialogue_manager import DialogueManager
from core.answer_extractor import AnswerExtractor
from core.llm_adapter import LLMAdapter

from routes.main_routes import main_bp
from routes.qa_routes import qa_bp
from routes.document_routes import document_bp
from routes.knowledge_routes import knowledge_bp
from routes.evaluation_routes import evaluation_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure required directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DOCUMENTS_DIR'], exist_ok=True)
    os.makedirs(os.path.dirname(app.config['DATABASE_PATH']), exist_ok=True)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(qa_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(knowledge_bp)
    app.register_blueprint(evaluation_bp)

    # Initialize Core Engines
    app.document_loader = DocumentLoader(app.config['DOCUMENTS_DIR'])
    app.ir_engine = IREngine()
    app.knowledge_engine = KnowledgeEngine(app.config['DATABASE_PATH'], app.config['KNOWLEDGE_BASE_CSV'])
    app.dialogue_manager = DialogueManager()
    app.answer_extractor = AnswerExtractor()
    app.llm_adapter = LLMAdapter(
        grok_api_key=app.config['GROK_API_KEY'],
        huggingface_api_key=app.config['HUGGINGFACE_API_KEY']
    )

    # Build initial IR TF-IDF index from documents
    passages = app.document_loader.load_all_documents()
    app.ir_engine.build_index(passages)

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', page_title="404 Page Not Found", content="<div class='container py-5 text-center'><h2>404 — Page Not Found</h2><p>The requested page does not exist.</p><a href='/' class='btn btn-primary mt-3'>Return to Dashboard</a></div>"), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({'error': 'An internal server error occurred. Please try again later.'}), 500

    return app

app = create_app()

if __name__ == '__main__':
    import socket
    
    def find_available_port(start_port=5050):
        port = start_port
        while port < start_port + 100:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', port)) != 0:
                    return port
            port += 1
        return start_port

    target_port = int(os.environ.get('PORT', find_available_port(5050)))
    print(f"\n=======================================================")
    print(f" IntelliQA Server running at: http://localhost:{target_port}")
    print(f"=======================================================\n")
    app.run(host='0.0.0.0', port=target_port, debug=True)
