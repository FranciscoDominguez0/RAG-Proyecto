import os
from pathlib import Path
from typing import List, Dict, Any, Tuple

import ollama
from pypdf import PdfReader
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.vector_store import (
    add_documents_to_store,
    search_similar_documents,
    collection_has_docs,
    get_stats
)

DOCS_FOLDER = "./documentos"
LLM_MODEL = "llama3"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

SYSTEM_PROMPT = """Eres un Consultor Profesional de Ciberseguridad.
Tu unica fuente de conocimiento es el contexto proporcionado.

Reglas:
1. Responde unicamente con informacion del contexto.
2. No inventes datos ni uses conocimiento externo.
3. Si la informacion no esta en el contexto responde exactamente:
   "No encontre informacion suficiente en la base de conocimiento para responder esta consulta."
4. Lenguaje profesional y tecnico. Precisión sobre extension.

CONTEXTO:
{context}

PREGUNTA:
{question}

RESPUESTA:"""


def extract_text(filepath: str) -> str:
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        reader = PdfReader(filepath)
        return "\n".join(p.extract_text() or "" for p in reader.pages)
    elif ext == ".docx":
        doc = Document(filepath)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    raise ValueError(f"Formato no soportado: {ext}")


def split_text(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    return splitter.split_text(text)


def load_and_index_documents(force_reload: bool = False) -> Dict[str, Any]:
    if collection_has_docs() and not force_reload:
        return get_stats()

    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
        return {"total_chunks": 0, "files_processed": 0}

    supported = {".pdf", ".docx", ".txt"}
    files = [f for f in Path(DOCS_FOLDER).iterdir()
             if f.is_file() and f.suffix.lower() in supported]

    if not files:
        return {"total_chunks": 0, "files_processed": 0}

    all_chunks, all_meta = [], []
    processed = 0

    for filepath in files:
        try:
            text = extract_text(str(filepath))
            if not text.strip():
                continue
            chunks = split_text(text)
            for i, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_meta.append({
                    "source": filepath.name,
                    "chunk_index": i,
                    "file_type": filepath.suffix.lower()
                })
            processed += 1
        except Exception:
            continue

    if all_chunks:
        add_documents_to_store(all_chunks, all_meta)

    return {"total_chunks": len(all_chunks), "files_processed": processed}


def build_context(documents: List[Dict[str, Any]]) -> str:
    parts = []
    for i, doc in enumerate(documents, 1):
        source = doc["metadata"].get("source", "Desconocido")
        parts.append(f"[Fragmento {i} | {source}]\n{doc['content'].strip()}")
    return "\n\n---\n\n".join(parts)


def generate_rag_response(question: str) -> Tuple[str, List[Dict[str, Any]]]:
    retrieved = search_similar_documents(query=question, n_results=5)

    if not retrieved:
        return (
            "No encontre informacion suficiente en la base de conocimiento "
            "para responder esta consulta.",
            []
        )

    context = build_context(retrieved)
    prompt = SYSTEM_PROMPT.format(context=context, question=question)

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"], retrieved