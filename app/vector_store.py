import chromadb
from typing import List, Dict, Any
from app.embeddings import generate_embedding, generate_embeddings_batch

CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "ciberseguridad_docs"


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )


def add_documents_to_store(chunks: List[str], metadatas: List[Dict[str, Any]]) -> None:
    collection = get_collection()
    embeddings = generate_embeddings_batch(chunks)
    ids = [f"chunk_{i}_{metadatas[i].get('source', 'doc')[:20]}" for i in range(len(chunks))]

    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        end = min(i + batch_size, len(chunks))
        collection.add(
            documents=chunks[i:end],
            embeddings=embeddings[i:end],
            metadatas=metadatas[i:end],
            ids=ids[i:end]
        )


def search_similar_documents(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    collection = get_collection()
    count = collection.count()
    if count == 0:
        return []

    query_embedding = generate_embedding(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, count),
        include=["documents", "metadatas", "distances"]
    )

    documents = []
    if results["documents"] and results["documents"][0]:
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            documents.append({
                "content": doc,
                "metadata": meta,
                "similarity": 1 - dist
            })
    return documents


def collection_has_docs() -> bool:
    try:
        return get_collection().count() > 0
    except Exception:
        return False


def get_stats() -> Dict[str, Any]:
    count = get_collection().count()
    return {"total_chunks": count, "collection": COLLECTION_NAME}