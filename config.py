"""Configuración compartida entre la ingesta y la consulta.

Mantener los embeddings y la colección en un único lugar evita el error #1 de
un RAG: indexar con un modelo de embeddings y consultar con otro.
"""
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
COLLECTION_NAME = "nimbus_docs"

EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")

# Chunking: 500 tokens con 50 de solapamiento (medidos con tiktoken).
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

# Entre 3 y 5 fragmentos para evitar el "contexto infinito".
TOP_K = 4


def get_embeddings() -> OpenAIEmbeddings:
    """Único punto de creación de embeddings (indexación y consulta)."""
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(model=LLM_MODEL, temperature=0)
