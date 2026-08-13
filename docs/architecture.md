# IntelliQA System Architecture & Technical Specifications

## 1. System Overview

IntelliQA is a modular, multi-mode Question Answering (QA) and Conversational Assistant developed using **Python Flask**. The architecture combines three distinct QA paradigms:

1. **IR-Based Factoid QA**: Information Retrieval engine over unstructured text documents using TF-IDF and Cosine Similarity.
2. **Knowledge-Based QA**: Structured Entity-Attribute-Value query engine over SQLite and CSV data with NetworkX knowledge graph visualization.
3. **Dialogue Manager**: Session-backed conversation frame manager handling context tracking and pronoun resolution ("it", "its creator").

---

## 2. High-Level Architecture Diagram

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

## 3. Module Breakdown

### Core Modules (`core/`)
- **`preprocessing.py`**: Handles text cleaning, lowercasing, punctuation normalization, sentence segmentation, and keyword extraction.
- **`document_loader.py`**: Ingests `.txt`, `.pdf` (via PyPDF), and `.csv` files from `data/documents/` into structured passages with metadata.
- **`ir_engine.py`**: Fits a `TfidfVectorizer` (sublinear_tf=True, 1-2 ngrams) on passage collections and ranks candidate passages using Cosine Similarity.
- **`answer_extractor.py`**: Implements question-type detection (Who/What/When/Where/Why/How/Which/YesNo/Definition) and candidate sentence scoring for factoid extraction.
- **`knowledge_engine.py`**: Interfaces with SQLite (`database/knowledge.db`) and CSV records (`data/knowledge_base.csv`). Generates a `networkx.DiGraph` representing entity relationships for visual graph rendering.
- **`dialogue_manager.py`**: Manages `ConversationFrame` state in Flask session context. Resolves pronouns ("it", "that") based on active entities.
- **`query_router.py`**: Classifies incoming user queries into `GREETING`, `KNOWLEDGE`, `DIALOGUE_FOLLOWUP`, or `IR`.
- **`evaluator.py`**: Runs benchmark tests against `data/sample_questions.csv`, calculating Exact Match (EM), token-level Precision, Recall, F1 score, and confidence.
- **`llm_adapter.py`**: Safe extension wrapper for optional external LLMs (OpenAI/HuggingFace), falling back automatically to the local pipeline.

---

## 4. API Endpoints

- `GET /`: Dashboard Overview page.
- `GET /chat`: Interactive QA Chat interface.
- `GET /documents`: Unstructured Document Management interface.
- `GET /knowledge`: Structured Knowledge Base table view.
- `GET /graph`: Interactive NetworkX Knowledge Graph visualizer.
- `GET /evaluation`: Academic Benchmark Evaluation Dashboard.
- `GET /dialogue`: Dialogue Flow Architecture & Frame documentation.
- `GET /about`: Project info & Requirement Traceability Matrix.

### REST API
- `POST /api/ask`: Main question processing endpoint.
- `GET /api/stats`: Real-time application metrics.
- `GET /api/documents`: List indexed document summaries.
- `POST /api/upload`: Upload `.txt`, `.pdf`, or `.csv` files with real-time TF-IDF re-indexing.
- `POST /api/documents/delete`: Remove document and rebuild index.
- `GET /api/knowledge`: Fetch all structured records.
- `POST /api/knowledge/add`: Insert new entity-attribute-value record.
- `POST /api/knowledge/delete`: Remove knowledge record by ID.
- `GET /api/graph`: Returns graph nodes & edges formatted for vis.js.
- `POST /api/evaluate`: Runs benchmark evaluation suite.
- `POST /api/clear-session`: Resets conversation memory frame.
