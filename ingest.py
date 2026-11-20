"""Módulo de ingesta: lee /data, fragmenta y persiste en ChromaDB.

Uso:
    python ingest.py            # indexa solo si la base no existe o los datos cambiaron
    python ingest.py --force    # reconstruye la colección desde cero
"""
import argparse
import hashlib
import json
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    DATA_DIR,
    VECTORSTORE_DIR,
    get_embeddings,
)

MANIFEST = VECTORSTORE_DIR / "manifest.json"


def load_documents(data_dir: Path = DATA_DIR) -> list[Document]:
    """Carga todos los .txt y .md de la carpeta de datos."""
    docs = []
    for path in sorted(data_dir.glob("*")):
        if path.suffix.lower() in {".txt", ".md"}:
            docs.append(
                Document(
                    page_content=path.read_text(encoding="utf-8"),
                    metadata={"source": path.name},
                )
            )
    if not docs:
        raise FileNotFoundError(f"No hay archivos .txt/.md en {data_dir}")
    return docs


def split_documents(docs: list[Document]) -> list[Document]:
    """Chunking de 500 tokens con 50 de overlap (contados con tiktoken)."""
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    # Id legible por fragmento: sirve como referencia en las respuestas.
    counters: dict[str, int] = {}
    for chunk in chunks:
        src = chunk.metadata["source"]
        counters[src] = counters.get(src, 0) + 1
        chunk.metadata["chunk"] = counters[src]
    return chunks


def _data_fingerprint(docs: list[Document]) -> str:
    """Hash del contenido + parámetros, para detectar si hay que reindexar."""
    h = hashlib.sha256()
    h.update(f"{CHUNK_SIZE}-{CHUNK_OVERLAP}".encode())
    for d in docs:
        h.update(d.metadata["source"].encode())
        h.update(d.page_content.encode())
    return h.hexdigest()


def get_vectorstore() -> Chroma:
    """Cliente persistente de Chroma (mismo embedding para indexar y consultar)."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=str(VECTORSTORE_DIR),
    )


def ingest(force: bool = False) -> Chroma:
    """Indexa los documentos; si la base ya está al día, no hace nada."""
    docs = load_documents()
    fingerprint = _data_fingerprint(docs)
    store = get_vectorstore()

    up_to_date = (
        MANIFEST.exists()
        and json.loads(MANIFEST.read_text())["fingerprint"] == fingerprint
        and store._collection.count() > 0
    )
    if up_to_date and not force:
        print(f"Base vectorial ya indexada ({store._collection.count()} fragmentos). Se omite la ingesta.")
        return store

    store.reset_collection()
    chunks = split_documents(docs)
    store.add_documents(chunks)
    MANIFEST.write_text(json.dumps({"fingerprint": fingerprint, "chunks": len(chunks)}))
    print(f"Indexados {len(chunks)} fragmentos de {len(docs)} documentos en '{VECTORSTORE_DIR.name}/'.")
    return store


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingesta de documentos en ChromaDB")
    parser.add_argument("--force", action="store_true", help="reindexar aunque ya exista")
    ingest(force=parser.parse_args().force)
