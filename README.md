# Pre-entrega 3: Sistema RAG local con ChromaDB y LangChain

Sistema de recuperación semántica end-to-end: ingesta de documentos → base vectorial persistente (ChromaDB) → cadena LCEL asíncrona que responde **solo** con el contexto recuperado y devuelve un objeto Pydantic con texto y referencias.

## Estructura

| Archivo | Rol |
|---|---|
| `data/*.md` | Dataset de ejemplo: manual de "Nimbus", una plataforma de despliegue ficticia (4 documentos) |
| `config.py` | Configuración y embeddings compartidos (garantiza el mismo modelo al indexar y consultar) |
| `ingest.py` | Ingesta: lectura de `/data`, chunking y persistencia en `./vectorstore` |
| `rag.py` | Cadena RAG asíncrona `get_rag_response(query)` + las dos pruebas |

## Cómo ejecutarlo

1. Crear el entorno virtual e instalar dependencias:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Configurar la clave de API (nunca se sube al repo):

   ```powershell
   copy .env.example .env
   # editar .env y poner OPENAI_API_KEY
   ```

3. Indexar los documentos (opcional: `rag.py` lo hace solo si hace falta):

   ```powershell
   python ingest.py
   ```

4. Correr las dos pruebas (pregunta válida + pregunta trampa):

   ```powershell
   python rag.py
   ```

   O hacer una consulta libre: `python rag.py "¿Qué roles existen en un equipo?"`

## Decisiones de diseño

- **Chunking:** `RecursiveCharacterTextSplitter.from_tiktoken_encoder` con `chunk_size=500` y `chunk_overlap=50`, medidos en **tokens** (`cl100k_base`). Los separadores priorizan encabezados Markdown y párrafos.
- **Embeddings:** `text-embedding-3-small`, creado en una única función (`config.get_embeddings`) usada tanto en la ingesta como en la consulta, para evitar embeddings no coincidentes.
- **Persistencia:** ChromaDB persistente en `./vectorstore`. Se guarda un hash del contenido y de los parámetros de chunking; si no cambiaron, la ingesta se omite. `python ingest.py --force` reconstruye todo.
- **Retriever:** búsqueda por similitud con `top_k = 4` (rango recomendado 3–5) para evitar el "contexto infinito".
- **Prompt "filtro de veracidad":** instruye a responder solo con el CONTEXTO y a contestar exactamente `No lo sé` si la respuesta no está, con `references` vacío.
- **Cadena LCEL:** `{contexto: retriever | formato, pregunta} | prompt | ChatOpenAI | PydanticOutputParser`, invocada con `ainvoke`. La salida es un modelo `RAGAnswer(answer, references)`; las referencias tienen el formato `archivo.md#n`.
- Temperatura 0 para minimizar variaciones y alucinaciones.

## Pruebas

`python rag.py` ejecuta:

1. **Pregunta con respuesta en los documentos:** *"¿Cuánto dura un token de API por defecto y cuántos puedo tener activos?"* → debe responder 90 días y máximo 20 tokens, citando `02_autenticacion.md`.
2. **Pregunta trampa:** *"¿Cuál es el precio de Nimbus en euros para clientes de Alemania?"* → los documentos solo mencionan precios en dólares y nada sobre Alemania, por lo que el modelo debe responder `No lo sé` sin referencias.

### Resultado real de la ejecución

```
=== Pregunta con respuesta en los documentos ===
P: ¿Cuánto dura un token de API por defecto y cuántos puedo tener activos?
R: Por defecto, un token de API vence a los 90 días y cada cuenta puede tener como máximo 20 tokens activos al mismo tiempo.
Referencias: ['02_autenticacion.md#2']

=== Pregunta trampa (no está en los documentos) ===
P: ¿Cuál es el precio de Nimbus en euros para clientes de Alemania?
R: No lo sé
Referencias: []
```

El modelo respondió correctamente con la información de los documentos y citó la fuente; ante la pregunta trampa no alucinó y devolvió "No lo sé" con referencias vacías.

## Variables de entorno

| Variable | Obligatoria | Por defecto |
|---|---|---|
| `OPENAI_API_KEY` | Sí | — |
| `LLM_MODEL` | No | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | No | `text-embedding-3-small` |

Cambiar `EMBEDDING_MODEL` requiere ejecutar `python ingest.py --force`.
