from langchain_ollama import OllamaLLM
from app.config import OLLAMA_LLM_MODEL
import os

def get_llm(temp: float = 0.2):
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    return OllamaLLM(
        model=OLLAMA_LLM_MODEL,
        temperature=temp,
        base_url=base_url
    )
