"""Embedding model wrapper with singleton loading."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=2)
def _load_model(model_name: str) -> SentenceTransformer:
	return SentenceTransformer(model_name)


class EmbeddingModel:
	"""Shared embedding model instance."""

	def __init__(self, model_name: str) -> None:
		self.model_name = model_name
		self._model = _load_model(model_name)

	def embed_texts(self, texts: List[str]) -> List[List[float]]:
		if not texts:
			return []
		return self._model.encode(texts, normalize_embeddings=True).tolist()

	def embed_query(self, text: str) -> List[float]:
		return self._model.encode([text], normalize_embeddings=True)[0].tolist()
