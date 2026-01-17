from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from app.config import OLLAMA_EMBED_MODEL

def get_embeddings():
    return OllamaEmbeddings(model=OLLAMA_EMBED_MODEL)

def save_index(chunks, path):
    db = FAISS.from_texts(chunks, get_embeddings())
    db.save_local(path)

def load_index(path):
    return FAISS.load_local(path, get_embeddings())
