# IntelliQA — Intelligent Information Retrieval, Knowledge-Based Question Answering & Conversational Assistant

IntelliQA is a complete, polished, and academically presentable Question Answering (QA) and Chatbot prototype built using **Python Flask**.

The system intelligently routes user queries across three primary QA engines:
1. **IR-Based Factoid QA**: Information retrieval over unstructured text documents using TF-IDF vectorization and Cosine Similarity.
2. **Knowledge-Based QA**: Entity-Attribute-Value querying over SQLite and CSV datasets with interactive NetworkX Knowledge Graph visualization.
3. **Dialogue Manager**: Session-backed conversation frame manager handling context tracking and pronoun coreference resolution ("it", "its creator").

---

## Architecture Overview

```
                                USER
                                 │
                        CHAT / QA INTERFACE
                                 │
                        QUERY PREPROCESSING
                                 │
                   QUERY ROUTER / INTENT CLASSIFIER
                                 │
      ┌──────────────────────────┼──────────────────────────┐
      ▼                          ▼                          ▼
IR-BASED FACTOID QA     KNOWLEDGE-BASED QA           DIALOGUE MANAGER
  (Unstructured Docs)     (Structured Data/CSV/DB)    (Conversation Memory)
      │                          │                          │
  Document Retrieval      Entity / Attribute Query    Context Resolution
      │                          │                          │
  Passage Ranking           Value Extraction            Entity Coreference
      │                          │                          │
      └──────────────────────────┴──────────────────────────┘
                                 │
                      FACTOID / CONTEXT ANSWER
                                 │
                     ANSWER QUALITY EVALUATOR
                     (Confidence, Relevance, F1, EM)
                                 │
                        FINAL RESPONSE + SOURCE
                                 │
                           USER INTERFACE
```

---

## Academic Requirement Traceability Matrix

| Requirement | Implementation Details | Location |
| :--- | :--- | :--- |
| **Retrieve relevant passages** | TF-IDF retrieval engine over text document passages using scikit-learn & Cosine Similarity. | `core/ir_engine.py` |
| **Extract factoid answers** | Question type detector & sentence scoring extractor. | `core/answer_extractor.py` |
| **Query structured knowledge sources** | Entity-Attribute-Value lookup on SQLite & CSV data. | `core/knowledge_engine.py` |
| **Handle conversational interaction** | Dialogue manager with Flask session frame & pronoun resolution ("it"). | `core/dialogue_manager.py` |
| **Intelligent query routing** | Hybrid intent router for Greetings, Knowledge Base, Dialogue, and IR. | `core/query_router.py` |
| **Evaluate answer quality** | Calculates Exact Match (EM), Precision, Recall, and F1 score across 25+ benchmark questions. | `core/evaluator.py` |
| **Working QA/chatbot prototype** | Complete, working Flask web application. | `app.py` |
| **Sample QA dataset** | Benchmark question evaluation set with ground truth answers. | `data/sample_questions.csv` |
| **Document Upload & Indexing** | Ingests `.txt`, `.pdf`, and `.csv` files with real-time TF-IDF re-indexing. | `routes/document_routes.py` |
| **Knowledge Graph Visualization** | Renders entity nodes and attribute relationships via NetworkX & vis.js. | `routes/knowledge_routes.py` |
| **Pastel UI & Responsive Design** | Modern academic AI interface using pastel palette (`#FAF8F5`, `#A8DADC`, `#CDB4DB`, `#FFC8DD`, `#FFE5B4`, `#BDE0C0`). | `static/css/style.css` |
| **Automated Test Suite** | Full Pytest suite covering all core engines, router, dialogue, and API endpoints. | `tests/` |

---

## Installation & Setup Guide

### 1. Prerequisites
- Python 3.9 or higher installed.

### 2. Create & Activate Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## How to Run the Application

```bash
source venv/bin/activate
python app.py
```
Open your browser and navigate to:
```
http://localhost:5000
```

---

## How to Run Automated Tests

Run the complete test suite using pytest:
```bash
source venv/bin/activate
pytest tests/ -v
```

---

## Main Features & Pages

1. **Dashboard Home (`/`)**: Overview hero, real-time live stats (Documents indexed, Passages total, Knowledge records, Questions answered, Average confidence), and core QA feature cards.
2. **QA Chat (`/chat`)**: Interactive chatbot with mode badges (`[ IR-BASED QA ]`, `[ KNOWLEDGE-BASED QA ]`, `[ DIALOGUE ]`), confidence score indicators, source file tags, expandable "How IntelliQA found this answer" reasoning accordion, try-example question chips, and context clearing.
3. **Documents Management (`/documents`)**: Table of indexed document passages, file upload form for `.txt`, `.pdf`, `.csv` with real-time index rebuilding, and document deletion.
4. **Knowledge Base (`/knowledge`)**: Entity-Attribute-Value table, instant search filtering, add structured record modal, and deletion.
5. **Knowledge Graph (`/graph`)**: Interactive NetworkX knowledge network visualization rendered using vis.js.
6. **Evaluation Dashboard (`/evaluation`)**: Interactive benchmark test runner calculating EM, Precision, Recall, F1 score, Chart.js pie and bar charts, and question breakdown table.
7. **Dialogue Flow (`/dialogue`)**: Documentation and visualization of `ConversationFrame` state machine and coreference resolution.
8. **About (`/about`)**: Architecture overview and requirement traceability table.

---

## API Endpoints Documentation

- `POST /api/ask`: Submit a question JSON `{"query": "What is Python?"}` &rarr; returns answer, mode, confidence, source, passage, and search explanation.
- `GET /api/stats`: Real-time system statistics.
- `GET /api/documents`: List document summaries.
- `POST /api/upload`: Upload `.txt`, `.pdf`, `.csv` files.
- `POST /api/documents/delete`: Remove document file.
- `GET /api/knowledge`: Fetch all structured records.
- `POST /api/knowledge/add`: Add new record.
- `POST /api/knowledge/delete`: Delete record by ID.
- `GET /api/graph`: Fetch graph nodes and edges.
- `POST /api/evaluate`: Execute benchmark evaluation suite.
- `POST /api/clear-session`: Reset conversation frame context.

---

## Sample Questions to Try

- **IR Factoid**:
  - *"What is artificial intelligence?"*
  - *"What is machine learning?"*
  - *"What are the primary paradigms of machine learning?"*
  - *"Why is Flask classified as a microframework?"*

- **Knowledge-Based**:
  - *"Who created Python?"*
  - *"What type of framework is Flask?"*
  - *"When was Python released?"*
  - *"What language is Flask written in?"*

- **Dialogue Context (Multi-Turn)**:
  - Turn 1: *"What is Python?"*
  - Turn 2: *"Who created it?"* (Resolves "it" &rarr; "Python")

---

## Limitations & Future Enhancements
- Current entity coreference resolution uses rule-based heuristic patterns; deep neural coreference resolution (e.g. AllenNLP) can be integrated for longer multi-entity narratives.
- Optional Hugging Face / OpenAI adapter can be enabled by specifying API keys in `.env`.
