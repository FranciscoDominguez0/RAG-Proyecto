import ollama
from typing import List

EMBEDDING_MODEL = "nomic-embed-text"


def generate_embedding(text: str) -> List[float]:
    response = ollama.embed(model=EMBEDDING_MODEL, input=text)
    return response["embeddings"][0]


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    return [generate_embedding(t) for t in texts]