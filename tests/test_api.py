import pytest
from app import create_app
from config import Config

class TestConfig(Config):
    TESTING = True

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        yield client

def test_pages(client):
    res_home = client.get('/')
    assert res_home.status_code == 200

    res_chat = client.get('/chat')
    assert res_chat.status_code == 200

    res_docs = client.get('/documents')
    assert res_docs.status_code == 200

    res_kb = client.get('/knowledge')
    assert res_kb.status_code == 200

    res_eval = client.get('/evaluation')
    assert res_eval.status_code == 200

def test_api_ask(client):
    res = client.post('/api/ask', json={'query': 'What are the primary paradigms of machine learning?'})
    assert res.status_code == 200
    data = res.get_json()
    assert 'answer' in data
    assert data['mode'] == 'IR'

def test_api_ask_knowledge(client):
    res = client.post('/api/ask', json={'query': 'Who created Python?'})
    assert res.status_code == 200
    data = res.get_json()
    assert 'answer' in data
    assert 'Guido van Rossum' in data['answer']

def test_api_stats(client):
    res = client.get('/api/stats')
    assert res.status_code == 200
    data = res.get_json()
    assert 'documents_indexed' in data
    assert 'knowledge_records' in data

def test_api_graph(client):
    res = client.get('/api/graph')
    assert res.status_code == 200
    data = res.get_json()
    assert 'nodes' in data
    assert 'edges' in data
