
import os
import logging
from mem0 import Memory
from langchain.vectorstores import Chroma
from langchain.embeddings import CohereEmbeddings

VECTOR_STORE_DIR = "chroma_db"
MEMORY_DIR = "memory_store"
EMBEDDING_API_KEY = os.getenv("COHERE_API_KEY")

logging.basicConfig(
    filename='rag_chain.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

memory = Memory(dir=MEMORY_DIR)

def get_session_history(session_id, max_turns=10):
    history = memory.get(session_id) or []
    return history[-max_turns:]

def update_session_history(session_id, question, answer):
    history = memory.get(session_id) or []
    history.append({"question": question, "answer": answer})
    memory.set(session_id, history)

def answer_question(question: str, session_id: str) -> dict:
    history = get_session_history(session_id)
    embedding_model = CohereEmbeddings(model="embed-english-v3.0", cohere_api_key=EMBEDDING_API_KEY)
    vectorstore = Chroma(persist_directory=VECTOR_STORE_DIR, embedding_function=embedding_model)
    try:
        retrieved_docs = vectorstore.similarity_search(question, k=4)
        retrieved_chunks = len(retrieved_docs)
        sources = []
        for doc in retrieved_docs:
            meta = getattr(doc, "metadata", {})
            sources.append({
                "source": meta.get("filename"),
                "page": meta.get("page")
            })
        context = "\n\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history])
        context += "\n\n" + "\n\n".join([doc.page_content for doc in retrieved_docs])
        answer = f"Sample answer for: {question}\n(Context and retrieved docs would be used here.)"
        update_session_history(session_id, question, answer)
        logging.info(f"Answered Q | Session: {session_id} | Chunks: {retrieved_chunks} | Sources: {sources}")
        return {
            "answer": answer,
            "sources": sources,
            "retrieved_chunks": retrieved_chunks
        }
    except Exception as e:
        logging.error(f"Error answering Q | Session: {session_id} | Error: {e}")
        return {
            "answer": f"Internal error: {e}",
            "sources": [],
            "retrieved_chunks": 0
        }
