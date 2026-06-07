import ollama
from typing import List

EMBEDDING_MODEL = "nomic-embed-text"


def generate_embedding(text: str) -> List[float]:
    try:
        response = ollama.embed(model=EMBEDDING_MODEL, input=text)
        return response["embeddings"][0]
    except Exception as e:
        print(f"[EMBED] ERROR generando embedding: {e}")
        raise


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    print(f"[EMBED] Generando {len(texts)} embeddings...")
    embeddings = []
    for i, t in enumerate(texts):
        print(f"[EMBED] Chunk {i+1}/{len(texts)}...")
        embeddings.append(generate_embedding(t))
    print(f"[EMBED] Todos los embeddings generados OK")
    return embeddings