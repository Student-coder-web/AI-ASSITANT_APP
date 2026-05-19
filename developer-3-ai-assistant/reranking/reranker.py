"""Cross-encoder reranker for retrieved documents."""

from __future__ import annotations

from functools import lru_cache
from typing import List

from sentence_transformers import CrossEncoder


@lru_cache(maxsize=1)
def _load_reranker(model_name: str) -> CrossEncoder:
	return CrossEncoder(model_name)


class Reranker:
	"""Reranks retrieved documents using a cross-encoder."""

	def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
		self.model_name = model_name
		self._model = _load_reranker(model_name)

	def rerank(self, query: str, docs: List[str], top_k: int = 3) -> List[str]:
		if not docs:
			return []
		pairs = [[query, doc] for doc in docs]
		scores = self._model.predict(pairs)
		ranked = sorted(zip(docs, scores), key=lambda item: item[1], reverse=True)
		return [doc for doc, _ in ranked[:top_k]]
