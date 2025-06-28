# RAG-ChatBot-Slack-Integration_with_Mem0

# RAG System Documentation

## 1. `app/ingest.py` - Incremental PDF Ingestion & Deduplication

### Purpose
- Loads company IT PDFs, splits into chunks, computes embeddings, and stores in ChromaDB
- Implements incremental processing to only handle new/changed PDFs

### Key Functions
| Function | Description |
|----------|-------------|
| `get_file_hash(filepath)` | Computes SHA-256 hash of PDF bytes for change detection |
| `already_embedded(collection, filename, file_hash)` | Checks if unchanged PDF exists in ChromaDB |
| `ingest_pdfs()` | Main ingestion pipeline with change detection |

### Workflow
1. Scan `data/` for PDF files
2. For each file:
   - Compute hash and check against ChromaDB metadata
   - If new/changed:
     - Split into chunks
     - Compute embeddings (Cohere)
     - Store in ChromaDB with metadata (filename, hash, page)
     - Delete old chunks for updated files
   - If unchanged: skip processing
3. Log all operations and errors

### Incremental Processing Benefits
- Cost savings by avoiding re-embedding unchanged documents
- Prevents duplicate content in vector store
- Enables safe re-runs of ingestion process

## 2. `app/rag_chain.py` - RAG Chain & File-Based Session Memory

### Purpose
- Powers Q&A with semantic search and chat history
- Manages per-user session memory using mem0

### Key Components
```python
memory = Memory(dir=MEMORY_DIR)  # File-based session storage

## Core Functions

| Function | Description |
|----------|-------------|
| `get_session_history(session_id, max_turns=10)` | Retrieves last N Q&A pairs for context |
| `update_session_history(session_id, question, answer)` | Appends new interaction to history |
| `answer_question(question, session_id)` | Full RAG pipeline execution |

## RAG Pipeline

1. Load chat history from mem0
2. Semantic search over vectorstore for relevant chunks
3. Compose context (history + retrieved chunks)
4. [Placeholder for LLM answer generation]
5. Update session history
6. Log process details and metrics

---

## `app/api.py` - FastAPI Backend

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Service health check |
| `/ask` | POST | Main Q&A endpoint (`{question, session_id}`) |

### Features

- Full request/response logging
- Error handling and metrics collection
- Integration point for Slack bot and other frontends

---

## `slack_bot.py` - Slack Integration

### Key Features

- Direct message and channel mention handling
- Feedback collection via emoji reactions (👍/👎)
- Comprehensive interaction logging

### Event Handlers

```python
@app.event("app_mention")  # Channel mentions
@app.event("message")     # Direct messages
@app.event("reaction_added")  # Feedback collection
