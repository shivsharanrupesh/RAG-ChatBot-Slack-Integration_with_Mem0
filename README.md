# RAG IT Support Chatbot (with mem0 session memory)

This project provides a Slack-integrated Retrieval-Augmented Generation (RAG) chatbot for IT support, using company PDF knowledge base, persistent session memory via mem0, and real-time feedback.

## Structure

- `app/ingest.py`: Incremental PDF ingestion and embedding (with deduplication)
- `app/rag_chain.py`: RAG logic and session memory (via mem0)
- `app/api.py`: FastAPI backend
- `slack_bot.py`: Slack bot event handler
- `data/`: Place your company IT PDFs here
- `memory_store/`: Chat/session memory per user (mem0 will store here)

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Place PDFs in `data/`
3. Run `python app/ingest.py`
4. Start API: `uvicorn app.api:app --reload`
5. Configure Slack tokens and run `slack_bot.py`

Edit code for your embedding/LLM provider and company requirements.

# 1. `app/ingest.py` — Incremental PDF Ingestion & Deduplication

**Purpose:**  
Loads your company’s IT PDFs, splits them into chunks, computes semantic embeddings, and stores them in ChromaDB.  
Ensures that only new/changed PDFs are reprocessed (saves cost and prevents duplicates).

**Key Functions:**  
- `get_file_hash(filepath)`  
  - Computes a SHA-256 hash of each PDF’s bytes.  
  - If a PDF’s content hasn’t changed, its hash stays the same.  
- `already_embedded(collection, filename, file_hash)`  
  - Checks ChromaDB for a document with the same filename and hash.  
  - If found, ingestion is skipped (the doc hasn’t changed).  
- `ingest_pdfs()`  
  - Scans `data/` for PDF files.  
  - For each file:  
    - Checks hash against what’s in ChromaDB.  
    - If new or changed: splits into chunks, computes embeddings (Cohere), and adds to ChromaDB with metadata (filename, hash, page).  
    - If unchanged: skips to avoid re-embedding.  
  - Deletes old chunks for updated files to avoid duplicates.  
  - Logs every step and error for troubleshooting.  

**How It Handles Incremental Ingestion:**  
By hashing the PDF and storing the hash as metadata, you can re-run the ingestion anytime without duplicating work or cost.

---

# 2. `app/rag_chain.py` — RAG Chain & File-Based Session Memory (via `mem0`)

**Purpose:**  
Powers your Q&A chain: retrieves relevant chunks, manages chat history for each user, and builds the context for the answer.

**Key Points:**  
- **`mem0` Memory Store**  
  - `memory = Memory(dir=MEMORY_DIR)` sets up file-based, robust session storage.  
  - Each user (session) gets their own history file in `memory_store/`.  
- `get_session_history(session_id, max_turns=10)`  
  - Returns the last N (default 10) question-answer turns from the user's session, using `mem0`.  
  - This is used to provide chat continuity (“memory”).  
- `update_session_history(session_id, question, answer)`  
  - Adds a new Q&A pair to the user's chat history, via `mem0`.  
  - No manual JSON or file logic needed; `mem0` handles it cleanly.  
- `answer_question(question, session_id)`  
  - Loads chat history using `mem0`.  
  - Runs semantic search over the vectorstore to get top-matching PDF chunks.  
  - Composes the full context (recent Q&A history + retrieved chunks).  
  - [In a real system, you’d send this context to an LLM to generate an answer. Here it returns a placeholder answer.]  
  - Updates session history so the next question is aware of this one.  
  - Logs the whole process (including errors, retrieved chunks, and sources).  

---

# 3. `app/api.py` — FastAPI Backend

**Purpose:**  
Exposes your AI Q&A as a web service for Slack (or any frontend).

**Key Functions:**  
- `/health` endpoint:  
  - For status checks and health monitoring.  
- `/ask` endpoint:  
  - Accepts POST with `{question, session_id}`.  
  - Calls `answer_question()` and returns the answer, sources, and metrics.  
  - All requests and errors are logged for observability.  

---

# 4. `slack_bot.py` — Slack Bot Integration & Feedback Capture

**Purpose:**  
Lets users talk to your chatbot in Slack (DM or channel), and collects user feedback via emoji reactions.

**Key Functions:**  
- `ask_backend(question, session_id)`  
  - Sends the user’s question and session ID to the FastAPI backend.  
  - Handles API response, adds sources to the reply, and asks for feedback (👍/👎).  
  - Logs timing, answer length, and sources.  
- **Event Handlers:**  
  - `@app.event("app_mention")` — Responds when bot is mentioned in a channel.  
  - `@app.event("message")` — Responds to direct messages.  
  - `@app.event("reaction_added")` — Logs reactions (user feedback).  
- **Logging:**  
  - Tracks all user interactions, answers, latency, and feedback for analytics.  

---

# 5. Logging, Error Handling, LLM Evaluation Metrics

- Every file uses `logging` — logs every major step, success, error, and key metric (response latency, number of chunks, sources cited).  
- Errors are always caught and logged, never crash the whole pipeline.  
- LLM metrics (like latency, retrieval size) are written to logs and can be analyzed for continuous improvement.  

---

# 6. `requirements.txt` & `README.md`

- **`requirements.txt`**  
  Lists all needed dependencies, including `mem0`, Chroma, Cohere, FastAPI, Slack Bolt, etc.  
- **`README.md`**  
  Explains structure, quickstart, and where to put your PDFs.  
  Can be expanded to describe memory, logging, feedback, or pipeline diagrams.  

---

# 7. Directory Structure

- `data/`: Place your PDFs here.  
- `memory_store/`: `mem0` stores per-user session histories here (one file per Slack user/session).  
- `app/`: All code for ingestion, RAG chain, and API.  
- **Root directory:** Contains `slack_bot.py`, `requirements.txt`, `README.md`, and log files (created automatically).  

---

# Summary Table

| Requirement | Where/How Handled |
|-------------|-------------------|
| Incremental PDF ingestion, deduplication | `ingest.py` with hash check + ChromaDB |
| Session/chat memory (file-based, per user) | `rag_chain.py` with `mem0` |
| Robust logging, error handling, LLM metrics | All files, via Python `logging` |
| Slack bot with feedback capture | `slack_bot.py`, event handlers, logging |
| API backend | `api.py` (FastAPI) |
| Requirements, README, structure | `requirements.txt`, `README.md`, standard folder layout |
