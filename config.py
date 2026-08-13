import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'intelliqa-secret-key-super-secure-2026')
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    DOCUMENTS_DIR = os.path.join(DATA_DIR, 'documents')
    KNOWLEDGE_BASE_CSV = os.path.join(DATA_DIR, 'knowledge_base.csv')
    SAMPLE_QUESTIONS_CSV = os.path.join(DATA_DIR, 'sample_questions.csv')
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'knowledge.db')
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max upload
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'csv'}
    
    # LLM Optional Settings
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', None)
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY', None)
    USE_TRANSFORMERS_FALLBACK = True
