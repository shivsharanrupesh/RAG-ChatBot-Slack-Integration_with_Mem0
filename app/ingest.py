
import os
import hashlib
import logging
from tqdm import tqdm
from langchain.document_loaders import PyPDFLoader
from langchain.vectorstores import Chroma
from langchain.embeddings import CohereEmbeddings  # Or OpenAIEmbeddings

logging.basicConfig(
    filename='ingest.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

DATA_DIR = "data"
VECTOR_STORE_DIR = "chroma_db"
EMBEDDING_API_KEY = os.getenv("COHERE_API_KEY")

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def already_embedded(collection, filename, file_hash):
    results = collection.get(where={"filename": filename, "file_hash": file_hash})
    return len(results["ids"]) > 0

def ingest_pdfs():
    if not os.path.exists(VECTOR_STORE_DIR):
        os.makedirs(VECTOR_STORE_DIR)
    embedding_model = CohereEmbeddings(model="embed-english-v3.0", cohere_api_key=EMBEDDING_API_KEY)
    vectorstore = Chroma(persist_directory=VECTOR_STORE_DIR, embedding_function=embedding_model)
    pdf_files = [f for f in os.listdir(DATA_DIR) if f.lower().endswith('.pdf')]

    for fname in tqdm(pdf_files, desc="Processing PDFs"):
        path = os.path.join(DATA_DIR, fname)
        file_hash = get_file_hash(path)
        if already_embedded(vectorstore, fname, file_hash):
            logging.info(f"Skipped {fname} (already embedded)")
            continue
        vectorstore.delete(where={"filename": fname})
        try:
            loader = PyPDFLoader(path)
            docs = loader.load_and_split()
            vectorstore.add_documents(
                docs,
                metadatas=[{"filename": fname, "file_hash": file_hash, "page": doc.metadata.get('page', i+1)} for i, doc in enumerate(docs)]
            )
            logging.info(f"Ingested {fname} ({len(docs)} chunks)")
        except Exception as e:
            logging.error(f"Failed to ingest {fname}: {e}")

if __name__ == "__main__":
    ingest_pdfs()
    logging.info("PDF ingestion complete.")
