"""Long-term memory storage using ChromaDB."""

from __future__ import annotations

import uuid
from typing import Dict

from embeddings.embedding_model import EmbeddingModel
from memory.memory_classifier import is_memory_statement
from vector_db.chroma_client import ChromaClientManager


class MemoryStore:
    """Stores useful interactions in a vector store."""

    def __init__(
        self,
        chroma_manager: ChromaClientManager,
        embedder: EmbeddingModel,
        collection_name: str,
    ) -> None:
        self._collection = chroma_manager.get_or_create_collection(collection_name)
        self._embedder = embedder

    def store_interaction(
        self,
        user_query: str,
        assistant_response: str,
        metadata: Dict[str, str],
    ) -> None:
        if not self.should_store(user_query):
            return

        content = f"User: {user_query}\nAssistant: {assistant_response}"
        embedding = self._embedder.embed_query(content)
        memory_id = str(uuid.uuid4())

        self._collection.add(
            ids=[memory_id],
            documents=[content],
            metadatas=[metadata],
            embeddings=[embedding],
        )

    def save(self, user_query: str) -> None:
        if not user_query.strip():
            return
        content = user_query
        embedding = self._embedder.embed_query(content)
        memory_id = str(uuid.uuid4())

        self._collection.add(
            ids=[memory_id],
            documents=[content],
            metadatas=[{"source": "memory"}],
            embeddings=[embedding],
        )

    def should_store(self, user_query: str) -> bool:
        return is_memory_statement(user_query)
