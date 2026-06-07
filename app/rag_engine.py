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
    print(f"[EXTRACT] Leyendo archivo: {filepath} (tipo: {ext})")
    if ext == ".pdf":
        reader = PdfReader(filepath)
        text = "\n".join(p.extract_text() or "" for p in reader.pages)
        print(f"[EXTRACT] PDF leido: {len(text)} caracteres")
        return text
    elif ext == ".docx":
        doc = Document(filepath)
        text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        print(f"[EXTRACT] DOCX leido: {len(text)} caracteres")
        return text
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        print(f"[EXTRACT] TXT leido: {len(text)} caracteres")
        return text
    raise ValueError(f"Formato no soportado: {ext}")


def split_text(text: str) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = splitter.split_text(text)
    print(f"[SPLIT] Texto dividido en {len(chunks)} chunks")
    return chunks


def load_and_index_documents(force_reload: bool = False) -> Dict[str, Any]:
    print(f"[INDEX] Iniciando indexacion... force_reload={force_reload}")

    if collection_has_docs() and not force_reload:
        stats = get_stats()
        print(f"[INDEX] Coleccion ya existe con {stats.get('total_chunks')} chunks. Saltando indexacion.")
        return stats

    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
        print(f"[INDEX] Carpeta '{DOCS_FOLDER}' no existia, fue creada. Agrega documentos y recarga.")
        return {"total_chunks": 0, "files_processed": 0}

    supported = {".pdf", ".docx", ".txt"}
    files = [f for f in Path(DOCS_FOLDER).iterdir()
             if f.is_file() and f.suffix.lower() in supported]

    print(f"[INDEX] Archivos encontrados: {[f.name for f in files]}")

    if not files:
        print("[INDEX] No hay archivos soportados en /documentos")
        return {"total_chunks": 0, "files_processed": 0}

    all_chunks, all_meta = [], []
    processed = 0

    for filepath in files:
        try:
            print(f"[INDEX] Procesando: {filepath.name}")
            text = extract_text(str(filepath))
            if not text.strip():
                print(f"[INDEX] ADVERTENCIA: {filepath.name} no tiene texto extraible")
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
            print(f"[INDEX] {filepath.name} procesado OK — {len(chunks)} chunks")
        except Exception as e:
            print(f"[INDEX] ERROR procesando {filepath.name}: {e}")
            continue

    print(f"[INDEX] Total chunks a embedear: {len(all_chunks)}")

    if all_chunks:
        print("[INDEX] Iniciando generacion de embeddings con Ollama...")
        try:
            add_documents_to_store(all_chunks, all_meta)
            print("[INDEX] Embeddings generados y guardados en ChromaDB OK")
        except Exception as e:
            print(f"[INDEX] ERROR al guardar en vector store: {e}")
            raise

    return {"total_chunks": len(all_chunks), "files_processed": processed}


def build_context(documents: List[Dict[str, Any]]) -> str:
    parts = []
    for i, doc in enumerate(documents, 1):
        source = doc["metadata"].get("source", "Desconocido")
        parts.append(f"[Fragmento {i} | {source}]\n{doc['content'].strip()}")
    return "\n\n---\n\n".join(parts)


def generate_rag_response(question: str) -> Tuple[str, List[Dict[str, Any]]]:
    print(f"[RAG] Pregunta recibida: {question}")
    print("[RAG] Buscando documentos similares...")
    retrieved = search_similar_documents(query=question, n_results=5)
    print(f"[RAG] Fragmentos recuperados: {len(retrieved)}")

    if not retrieved:
        return (
            "No encontre informacion suficiente en la base de conocimiento "
            "para responder esta consulta.",
            []
        )

    context = build_context(retrieved)
    prompt = SYSTEM_PROMPT.format(context=context, question=question)
    print("[RAG] Enviando prompt a Ollama (llama3)...")

    try:
        response = ollama.chat(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        print("[RAG] Respuesta recibida de Ollama OK")
    except Exception as e:
        print(f"[RAG] ERROR llamando a Ollama: {e}")
        raise

    return response["message"]["content"], retrieved