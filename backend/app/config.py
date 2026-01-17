import os
from dotenv import load_dotenv

load_dotenv()

OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3.1:70b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

# Authentication
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://lecture_user:lecture_pass@localhost:5432/lecture_db")

# Qdrant
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Directories
DATA_DIR = "data"
LECTURE_DIR = f"{DATA_DIR}/lectures"
INDEX_DIR = f"{DATA_DIR}/indexes"
PDF_DIR = f"{DATA_DIR}/pdfs"

# Text processing
CHUNK_SIZE = 800
CHUNK_OVERLAP = 150
TOP_K = 4
