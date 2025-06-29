
import logging
from fastapi import FastAPI
from pydantic import BaseModel
from rag_chain import answer_question

logging.basicConfig(
    filename='backend.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    session_id: str

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ask")
def ask(request: QueryRequest):
    question = request.question
    session_id = request.session_id
    logging.info(f"Received Q | Session: {session_id} | Q: {question}")
    try:
        result = answer_question(question, session_id)
        return result
    except Exception as e:
        logging.error(f"Error answering Q | Session: {session_id} | Error: {e}")
        return {
            "answer": f"Internal error: {e}",
            "sources": [],
            "retrieved_chunks": 0
        }
