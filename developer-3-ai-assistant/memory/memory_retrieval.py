"""Long-term memory retrieval."""

from __future__ import annotations

from typing import Dict, List

from embeddings.embedding_model import EmbeddingModel
from vector_db.chroma_client import ChromaClientManager


class MemoryRetriever:
    """Retrieves long-term memories relevant to the query."""

    def __init__(
        self,
        chroma_manager: ChromaClientManager,
        embedder: EmbeddingModel,
        collection_name: str,
    ) -> None:
        self._collection = chroma_manager.get_or_create_collection(collection_name)
        self._embedder = embedder

    def retrieve(
        self,
        query_text: str,
        top_k: int,
        distance_threshold: float | None = 0.5,
    ) -> List[Dict[str, str]]:
        if not query_text:
            return []

        embedding = self._embedder.embed_query(query_text)
        results = self._collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        hits: List[Dict[str, str]] = []
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, dist in zip(documents, metadatas, distances):
            if distance_threshold is not None and dist >= distance_threshold:
                continue
            hits.append(
                {
                    "text": doc,
                    "metadata": meta or {},
                    "score": str(dist),
                }
            )

        return hits
