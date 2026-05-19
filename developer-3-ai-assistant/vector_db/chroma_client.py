"""ChromaDB client manager."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

import chromadb


@lru_cache(maxsize=2)
def _get_client(persist_dir: str) -> chromadb.PersistentClient:
	return chromadb.PersistentClient(path=persist_dir)


class ChromaClientManager:
	"""Creates and reuses ChromaDB client and collections."""

	def __init__(self, persist_dir: Path) -> None:
		self.persist_dir = persist_dir
		self._client = _get_client(str(persist_dir))

	def get_or_create_collection(self, name: str):
		return self._client.get_or_create_collection(name=name)
