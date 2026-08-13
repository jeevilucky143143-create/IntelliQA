import os
import pytest
from core.knowledge_engine import KnowledgeEngine

def test_knowledge_engine(tmp_path):
    db_path = str(tmp_path / "test_knowledge.db")
    csv_path = str(tmp_path / "test_knowledge.csv")

    with open(csv_path, 'w') as f:
        f.write("entity,attribute,value,category,description,source\n")
        f.write("Python,creator,Guido van Rossum,Technology,Programming language,csv\n")
        f.write("Flask,type,Web Framework,Technology,Micro framework,csv\n")

    ke = KnowledgeEngine(db_path, csv_path)
    records = ke.get_all_records()
    assert len(records) >= 2

    # Query entity creator
    res = ke.query("Who created Python?")
    assert res is not None
    assert "Guido van Rossum" in res['answer']

    # Query entity type
    res_flask = ke.query("What type of framework is Flask?")
    assert res_flask is not None
    assert "Web Framework" in res_flask['value']

    # Add record
    added = ke.add_record("Django", "creator", "Adrian Holovaty", "Technology", "Web framework")
    assert added['id'] is not None

    # Verify graph data
    graph_data = ke.get_graph_data()
    assert len(graph_data['nodes']) >= 3
    assert len(graph_data['edges']) >= 2
