import pytest
from core.document_loader import DocumentLoader
from core.ir_engine import IREngine
from core.answer_extractor import AnswerExtractor, QuestionType

@pytest.fixture(scope="module")
def ir_system():
    loader = DocumentLoader('data/documents')
    passages = loader.load_all_documents()
    ir = IREngine()
    ir.build_index(passages)
    extractor = AnswerExtractor()
    return ir, extractor

def test_factoid_sslc_percentage(ir_system):
    ir, extractor = ir_system
    q = "What is the SSLC percentage?"
    exp_q = extractor.expand_query_with_synonyms(q)
    passages = ir.search(exp_q, top_k=5)
    res = extractor.extract_answer(q, passages)
    
    assert res['confidence'] >= 0.85
    assert '92.64%' in res['answer']
    assert res['source'] == 'Jeevilucky.pdf'

def test_factoid_10th_percentage_synonym(ir_system):
    ir, extractor = ir_system
    q = "What is my 10th percentage?"
    exp_q = extractor.expand_query_with_synonyms(q)
    passages = ir.search(exp_q, top_k=5)
    res = extractor.extract_answer(q, passages)
    
    assert res['confidence'] >= 0.85
    assert '92.64%' in res['answer']
    assert res['source'] == 'Jeevilucky.pdf'

def test_factoid_puc_percentage(ir_system):
    ir, extractor = ir_system
    q = "What is the PUC percentage?"
    exp_q = extractor.expand_query_with_synonyms(q)
    passages = ir.search(exp_q, top_k=5)
    res = extractor.extract_answer(q, passages)
    
    assert res['confidence'] >= 0.85
    assert '95.17%' in res['answer']
    assert res['source'] == 'Jeevilucky.pdf'

def test_factoid_cgpa(ir_system):
    ir, extractor = ir_system
    q = "What is the CGPA?"
    exp_q = extractor.expand_query_with_synonyms(q)
    passages = ir.search(exp_q, top_k=5)
    res = extractor.extract_answer(q, passages)
    
    assert res['confidence'] >= 0.85
    assert '9.48' in res['answer']
    assert res['source'] == 'Jeevilucky.pdf'

def test_factoid_email(ir_system):
    ir, extractor = ir_system
    q = "What is the user's email?"
    exp_q = extractor.expand_query_with_synonyms(q)
    passages = ir.search(exp_q, top_k=10)
    res = extractor.extract_answer(q, passages)
    
    assert res['confidence'] >= 0.85
    assert 'jeevilucky2020@gmail.com' in res['answer']
    assert res['source'] == 'Jeevilucky.pdf'

def test_factoid_degree(ir_system):
    ir, extractor = ir_system
    q = "What degree did the user pursue?"
    exp_q = extractor.expand_query_with_synonyms(q)
    passages = ir.search(exp_q, top_k=10)
    res = extractor.extract_answer(q, passages)
    
    assert res['confidence'] >= 0.85
    assert 'Bachelor of Engineering' in res['answer']
    assert res['source'] == 'Jeevilucky.pdf'

def test_factoid_skills(ir_system):
    ir, extractor = ir_system
    q = "What programming languages are mentioned?"
    exp_q = extractor.expand_query_with_synonyms(q)
    passages = ir.search(exp_q, top_k=5)
    res = extractor.extract_answer(q, passages)
    
    assert res['confidence'] >= 0.85
    assert 'Python' in res['answer'] or 'Java' in res['answer']
    assert res['source'] == 'Jeevilucky.pdf'

def test_factoid_graduation_year(ir_system):
    ir, extractor = ir_system
    q = "When did the user graduate?"
    exp_q = extractor.expand_query_with_synonyms(q)
    passages = ir.search(exp_q, top_k=10)
    res = extractor.extract_answer(q, passages)
    
    assert res['confidence'] >= 0.65
    assert '2027' in res['answer'] or '2026' in res['answer'] or '2023' in res['answer']

def test_factoid_non_existent_answer(ir_system):
    ir, extractor = ir_system
    q = "What is the population of Mars?"
    exp_q = extractor.expand_query_with_synonyms(q)
    passages = ir.search(exp_q, top_k=5)
    res = extractor.extract_answer(q, passages)
    
    assert res['confidence'] < 0.40
    assert "couldn't find" in res['answer'].lower()

def test_factoid_multi_percentage_association():
    extractor = AnswerExtractor()
    passage_text = "EDUCATION: Pre-University (12th) – SGPTA PU College 2023|95.17% SSLC (10th) – SSVM 2021|92.64%"
    passage = [{'text': passage_text, 'score': 0.90, 'source': 'Resume.pdf'}]
    
    res_sslc = extractor.extract_answer("What is the SSLC percentage?", passage)
    assert '92.64%' in res_sslc['answer']
    
    res_puc = extractor.extract_answer("What is the PUC percentage?", passage)
    assert '95.17%' in res_puc['answer']
