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

