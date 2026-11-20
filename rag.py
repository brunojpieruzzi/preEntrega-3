"""Cadena RAG asíncrona (LCEL) con respuesta estructurada en Pydantic.

Uso:
    python rag.py                       # corre las dos pruebas (pregunta válida + trampa)
    python rag.py "¿Cuánto dura el token?"   # consulta libre
"""
import asyncio
import sys

from langchain_core.documents import Document
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from pydantic import BaseModel, Field

from config import TOP_K, get_llm
from ingest import ingest


class RAGAnswer(BaseModel):
    """Respuesta estructurada del sistema RAG."""

    answer: str = Field(description="Respuesta basada únicamente en el contexto, o 'No lo sé'.")
    references: list[str] = Field(
        default_factory=list,
        description="Fuentes usadas, con el formato 'archivo.md#fragmento'. Vacío si no hay respuesta.",
    )


parser = PydanticOutputParser(pydantic_object=RAGAnswer)

SYSTEM_PROMPT = """Eres un asistente técnico. Responde SOLO con la información del CONTEXTO.
Reglas:
- No uses conocimiento externo ni inventes datos, cifras o comandos.
- Si la respuesta no está en el CONTEXTO, responde exactamente "No lo sé" en el campo
  "answer" y deja "references" vacío.
- Si sí está, responde en español de forma concisa y cita en "references" solo los
  fragmentos que usaste, con el formato indicado entre corchetes en cada fragmento.

{format_instructions}"""

prompt = ChatPromptTemplate.from_messages(
    [("system", SYSTEM_PROMPT), ("human", "CONTEXTO:\n{context}\n\nPREGUNTA: {question}")]
).partial(format_instructions=parser.get_format_instructions())


def format_docs(docs: list[Document]) -> str:
    """Convierte los fragmentos en texto, etiquetando cada uno con su referencia."""
    return "\n\n".join(
        f"[{d.metadata['source']}#{d.metadata['chunk']}]\n{d.page_content}" for d in docs
    )


def build_chain():
    """retriever -> formateo de documentos -> prompt -> LLM -> parser Pydantic."""
    store = ingest()  # idempotente: no reindexa si ya está al día
    retriever = store.as_retriever(search_kwargs={"k": TOP_K})
    return (
        {
            "context": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough(),
        }
        | prompt
        | get_llm()
        | parser
    )


_chain = None


async def get_rag_response(query: str) -> RAGAnswer:
    """Busca por similitud en ChromaDB, arma el prompt y llama al LLM de forma asíncrona."""
    global _chain
    if _chain is None:
        _chain = await asyncio.to_thread(build_chain)  # la ingesta es síncrona
    return await _chain.ainvoke(query)


async def run_tests() -> None:
    tests = [
        ("Pregunta con respuesta en los documentos", "¿Cuánto dura un token de API por defecto y cuántos puedo tener activos?"),
        ("Pregunta trampa (no está en los documentos)", "¿Cuál es el precio de Nimbus en euros para clientes de Alemania?"),
    ]
    for title, question in tests:
        result = await get_rag_response(question)
        print(f"\n=== {title} ===\nP: {question}\nR: {result.answer}\nReferencias: {result.references}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        r = asyncio.run(get_rag_response(" ".join(sys.argv[1:])))
        print(r.answer, "\nReferencias:", r.references)
    else:
        asyncio.run(run_tests())
