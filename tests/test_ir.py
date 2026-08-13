import os
import pytest
from core.preprocessing import clean_text, split_into_sentences, tokenize
from core.document_loader import DocumentLoader
from core.ir_engine import IREngine
from core.answer_extractor import AnswerExtractor, QuestionType

def test_preprocessing():
    text = "Artificial Intelligence (AI) is   great!\nIt transforms industries."
    cleaned = clean_text(text)
    assert cleaned == "Artificial Intelligence (AI) is great! It transforms industries."
    
    sentences = split_into_sentences(cleaned)
    assert len(sentences) >= 2
    assert "Artificial Intelligence" in sentences[0]

def test_ir_engine_search(tmp_path):
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    
    file1 = doc_dir / "ai.txt"
    file1.write_text("Artificial intelligence is a domain of computer science focused on building smart machines.")
    
    loader = DocumentLoader(str(doc_dir))
    passages = loader.load_all_documents()
    assert len(passages) > 0

    ir_engine = IREngine()
    indexed = ir_engine.build_index(passages)
    assert indexed is True

    results = ir_engine.search("What is artificial intelligence?", top_k=2)
    assert len(results) > 0
    assert "artificial intelligence" in results[0]['text'].lower()
    assert results[0]['score'] > 0.1

def test_answer_extractor():
    extractor = AnswerExtractor()
    passages = [{'text': 'Python was created by Guido van Rossum in 1991.', 'score': 0.85, 'source': 'python.txt'}]
    
    res = extractor.extract_answer("Who created Python?", passages)
    assert res['confidence'] > 0.5
    assert res['source'] == 'python.txt'
    assert "Guido van Rossum" in res['answer']
