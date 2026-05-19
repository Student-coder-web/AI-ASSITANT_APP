"""Vector retrieval logic."""

from __future__ import annotations

from typing import Dict, List

from embeddings.embedding_model import EmbeddingModel
from vector_db.chroma_client import ChromaClientManager


class VectorRetriever:
	"""Retrieves relevant documents from ChromaDB."""

	def __init__(
		self,
		chroma_manager: ChromaClientManager,
		embedder: EmbeddingModel,
		collection_name: str,
	) -> None:
		self._collection = chroma_manager.get_or_create_collection(collection_name)
		self._embedder = embedder

	def query(self, query_text: str, top_k: int) -> List[Dict[str, str]]:
		if not query_text:
			return []

		embedding = self._embedder.embed_query(query_text)
		results = self._collection.query(
			query_embeddings=[embedding],
			n_results=10,
			include=["documents", "metadatas", "distances"],
		)

		hits: List[Dict[str, str]] = []
		documents = results.get("documents", [[]])[0]
		metadatas = results.get("metadatas", [[]])[0]
		distances = results.get("distances", [[]])[0]

		for doc, meta, dist in zip(documents, metadatas, distances):
			hits.append(
				{
					"text": doc,
					"metadata": meta or {},
					"score": str(dist),
				}
			)

		return hits

	def retrieve(self, query_text: str, top_k: int) -> List[str]:
		hits = self.query(query_text=query_text, top_k=top_k)
		return [hit.get("text", "") for hit in hits if hit.get("text")]
