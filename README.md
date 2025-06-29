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

## 3. `app/api.py` — FastAPI Backend

**Purpose:**

Exposes your AI Q&A as a web service for Slack (or any frontend).  

**Key Functions:**  
- **`/health` endpoint:**  
  - For status checks and health monitoring.  
- **`/ask` endpoint:**  
  - Accepts `POST` with `{question, session_id}`.  
  - Calls `answer_question()` and returns the answer, sources, and metrics.  
- All requests and errors are logged for observability.  


## 4. `slack_bot.py` — Slack Bot Integration & Feedback Capture

**Purpose:**

Lets users talk to your chatbot in Slack (DM or channel), and collects user feedback via emoji reactions.  

**Key Functions:**  
- **`ask_backend(question, session_id)`**  
  - Sends the user’s question and session ID to the FastAPI backend.  
  - Handles API response, adds sources to the reply, and asks for feedback (`👍`/`👎`).  
  - Logs timing, answer length, and sources.  

**Event Handlers:**  
- `@app.event("app_mention")` — Responds when bot is mentioned in a channel.  
- `@app.event("message")` — Responds to direct messages.  
- `@app.event("reaction_added")` — Logs reactions (user feedback).  

**Logging:**  
Tracks all user interactions, answers, latency, and feedback for analytics.


### 5. Logging, Error Handling, LLM Evaluation Metrics  
- **Logging:**  
  - Every file uses `logging` — tracks major steps, successes, errors, and key metrics (e.g., response latency, chunk count, sources cited).  
- **Error Handling:**  
  - Errors are caught and logged gracefully; never crash the pipeline.  
- **LLM Metrics:**  
  - Latency, retrieval size, etc., are logged for continuous improvement analysis.  

---

### 6. `requirements.txt` & `README.md`  
#### `requirements.txt`  
- Lists dependencies:  
  - `mem0`, `Chroma`, `Cohere`, `FastAPI`, `Slack Bolt`, etc.  

#### `README.md`  
- **Contents:**  
  - Project structure and quickstart guide.  
  - Instructions for adding PDFs (`data/` directory).  
  - *(Expandable sections for memory, logging, feedback, or pipeline diagrams.)*  

---

### 7. Directory Structure  
```plaintext
data/               # Place your PDFs here.  
memory_store/       # mem0 stores per-user session histories (one file per user/session).  
app/                # Code for ingestion, RAG chain, and API.  
├── api.py          # FastAPI backend.  
├── (other modules)  
root/               # Contains:  
├── slack_bot.py    # Slack integration.  
├── requirements.txt  
├── README.md  
└── logs/           # Auto-generated log files.


