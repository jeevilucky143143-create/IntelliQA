import os
import sqlite3
import pandas as pd
import networkx as nx
from typing import List, Dict, Optional, Tuple
from core.preprocessing import tokenize

ATTRIBUTE_SYNONYMS = {
    'creator': ['creator', 'created', 'created by', 'author', 'developer', 'invented', 'founder', 'founded by', 'coined', 'coined by', 'established by'],
    'release_year': ['release year', 'released', 'year', 'birth year', 'founded', 'created year', 'established year', 'established in', 'founded in'],
    'type': ['type', 'kind', 'category', 'classification', 'what is', 'what type'],
    'license': ['license', 'licensing', 'terms'],
    'written_in': ['written in', 'developed using', 'language', 'programming language'],
    'template_engine': ['template engine', 'templating', 'jinja', 'template'],
    'wsgi_toolkit': ['wsgi toolkit', 'wsgi', 'werkzeug'],
    'backend_framework': ['backend framework', 'framework'],
    'location': ['location', 'located in', 'headquarters', 'country', 'city', 'where is'],
    'field': ['field', 'domain', 'focus', 'subject', 'specialization'],
}

class KnowledgeEngine:
    """Manages structured entity-attribute-value knowledge in SQLite/CSV and builds a NetworkX Knowledge Graph."""

    def __init__(self, db_path: str, csv_path: str):
        self.db_path = db_path
        self.csv_path = csv_path
        self.graph = nx.DiGraph()
        self._init_db()
        self.load_from_csv()
        self.build_knowledge_graph()

    def get_connection(self):
        """Get SQLite database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Ensure database table exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entity TEXT NOT NULL,
                    attribute TEXT NOT NULL,
                    value TEXT NOT NULL,
                    category TEXT,
                    description TEXT,
                    source TEXT DEFAULT 'knowledge_base.csv',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            conn.commit()

    def load_from_csv(self):
        """Populate database from CSV if DB is empty or outdated."""
        if not os.path.exists(self.csv_path):
            return

        try:
            df = pd.read_csv(self.csv_path)
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM knowledge;")
                count = cursor.fetchone()[0]
                
                if count == 0:
                    for _, row in df.iterrows():
                        cursor.execute('''
                            INSERT INTO knowledge (entity, attribute, value, category, description, source)
                            VALUES (?, ?, ?, ?, ?, ?);
                        ''', (
                            str(row['entity']).strip(),
                            str(row['attribute']).strip(),
                            str(row['value']).strip(),
                            str(row.get('category', '')).strip(),
                            str(row.get('description', '')).strip(),
                            str(row.get('source', 'knowledge_base.csv')).strip()
                        ))
                    conn.commit()
        except Exception as e:
            print(f"Error loading CSV to database: {e}")

    def add_record(self, entity: str, attribute: str, value: str, category: str = "", description: str = "", source: str = "user_added") -> Dict:
        """Add a new structured knowledge record."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO knowledge (entity, attribute, value, category, description, source)
                VALUES (?, ?, ?, ?, ?, ?);
            ''', (entity.strip(), attribute.strip(), value.strip(), category.strip(), description.strip(), source.strip()))
            conn.commit()
            rec_id = cursor.lastrowid
            
        self.build_knowledge_graph()
        return {
            'id': rec_id,
            'entity': entity,
            'attribute': attribute,
            'value': value,
            'category': category,
            'description': description,
            'source': source
        }

    def delete_record(self, record_id: int) -> bool:
        """Delete a record by ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM knowledge WHERE id = ?;", (record_id,))
            conn.commit()
            success = cursor.rowcount > 0

        self.build_knowledge_graph()
        return success

    def get_all_records(self) -> List[Dict]:
        """Fetch all records from database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM knowledge ORDER BY id DESC;")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def build_knowledge_graph(self):
        """Construct a NetworkX directed graph from structured records."""
        self.graph.clear()
        records = self.get_all_records()
        for r in records:
            e = r['entity']
            attr = r['attribute']
            val = r['value']
            
            self.graph.add_node(e, label=e, type='entity', category=r.get('category', 'General'))
            self.graph.add_node(val, label=val, type='value', category=r.get('category', 'General'))
            self.graph.add_edge(e, val, relation=attr, description=r.get('description', ''))

    def get_graph_data(self) -> Dict:
        """Export nodes and edges formatted for frontend visual graphs (vis.js or D3)."""
        nodes = []
        edges = []
        
        node_id_map = {}
        for idx, node in enumerate(self.graph.nodes()):
            node_id_map[node] = idx + 1
            n_data = self.graph.nodes[node]
            is_entity = n_data.get('type') == 'entity'
            nodes.append({
                'id': idx + 1,
                'label': str(node),
                'shape': 'ellipse' if is_entity else 'box',
                'color': '#A8DADC' if is_entity else '#CDB4DB',
                'font': {'color': '#343434', 'size': 14}
            })
            
        for u, v, data in self.graph.edges(data=True):
            if u in node_id_map and v in node_id_map:
                edges.append({
                    'from': node_id_map[u],
                    'to': node_id_map[v],
                    'label': data.get('relation', 'related_to'),
                    'arrows': 'to',
                    'color': {'color': '#FFC8DD'}
                })
                
        return {'nodes': nodes, 'edges': edges}

    def detect_entity_and_attribute(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Identify matching entity and attribute from a natural language question."""
        q_lower = query.lower()
        records = self.get_all_records()
        entities = list(set([r['entity'] for r in records]))
        
        detected_entity = None
        # Check longest entity match first
        entities.sort(key=lambda x: len(x), reverse=True)
        for e in entities:
            if e.lower() in q_lower:
                detected_entity = e
                break

        detected_attribute = None
        for canonical_attr, synonyms in ATTRIBUTE_SYNONYMS.items():
            for syn in synonyms:
                if syn in q_lower:
                    detected_attribute = canonical_attr
                    break
            if detected_attribute:
                break

        return detected_entity, detected_attribute

    def query(self, question: str, entity_override: Optional[str] = None) -> Optional[Dict]:
        """
        Query structured knowledge base.
        Returns result dict with answer, entity, attribute, value, source, confidence.
        """
        entity, attribute = self.detect_entity_and_attribute(question)
        if entity_override:
            entity = entity_override

        if not entity:
            return None

        records = self.get_all_records()
        
        # 1. Match both entity & attribute
        if attribute:
            for r in records:
                if r['entity'].lower() == entity.lower() and r['attribute'].lower() == attribute.lower():
                    # Format natural language answer
                    answer_text = f"{r['entity']}'s {r['attribute'].replace('_', ' ')} is {r['value']}."
                    if attribute == 'creator':
                        answer_text = f"{r['entity']} was created by {r['value']}."
                    elif attribute == 'type':
                        val = r['value']
                        article = 'an' if val.lower()[0] in 'aeiou' else 'a'
                        answer_text = f"{r['entity']} is {article} {val}."
                    elif attribute == 'written_in':
                        answer_text = f"{r['entity']} is written in {r['value']}."

                    return {
                        'answer': answer_text,
                        'entity': r['entity'],
                        'attribute': r['attribute'],
                        'value': r['value'],
                        'source': r['source'],
                        'confidence': 0.95,
                        'description': r.get('description', '')
                    }

        # 2. General entity lookup (e.g. "Tell me about Python")
        entity_matches = [r for r in records if r['entity'].lower() == entity.lower()]
        if entity_matches:
            first = entity_matches[0]
            summary_parts = [f"{m['attribute'].replace('_', ' ').capitalize()}: {m['value']}" for m in entity_matches]
            combined_summary = f"{entity} details — " + ", ".join(summary_parts) + "."
            return {
                'answer': combined_summary,
                'entity': entity,
                'attribute': 'overview',
                'value': str([m['value'] for m in entity_matches]),
                'source': first['source'],
                'confidence': 0.90,
                'description': first.get('description', '')
            }

        return None
