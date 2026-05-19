"""High-level assistant interface."""

from __future__ import annotations

import uuid

from app.config import Settings
from app.orchestrator import Orchestrator
from embeddings.embedding_model import EmbeddingModel
from ingestion.chunking import chunk_documents
from ingestion.pdf_loader import load_pdf
from llm.ollama_client import get_ollama_client
from memory.chat_memory import ChatMemory
from memory.memory_retrieval import MemoryRetriever
from memory.memory_store import MemoryStore
from reranking.reranker import Reranker
from vector_db.chroma_client import ChromaClientManager
from vector_db.retrieval import VectorRetriever


class Assistant:
    """Coordinates dependencies and exposes a simple ask() interface."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        embedder = EmbeddingModel(settings.embedding_model_name)
        chroma_manager = ChromaClientManager(settings.chroma_persist_dir)

        doc_retriever = VectorRetriever(
            chroma_manager=chroma_manager,
            embedder=embedder,
            collection_name=settings.chroma_collection_docs,
        )
        memory_retriever = MemoryRetriever(
            chroma_manager=chroma_manager,
            embedder=embedder,
            collection_name=settings.chroma_collection_memory,
        )
        memory_store = MemoryStore(
            chroma_manager=chroma_manager,
            embedder=embedder,
            collection_name=settings.chroma_collection_memory,
        )

        llm_client = get_ollama_client(
            settings.ollama_base_url,
            settings.ollama_model,
            settings.request_timeout_s,
        )

        self._embedder = embedder
        self._chroma_manager = chroma_manager
        self._doc_collection_name = settings.chroma_collection_docs

        self.chat_memory = ChatMemory(max_messages=settings.max_chat_messages)
        reranker = Reranker()
        self.orchestrator = Orchestrator(
            settings=settings,
            llm_client=llm_client,
            doc_retriever=doc_retriever,
            memory_retriever=memory_retriever,
            memory_store=memory_store,
            reranker=reranker,
        )

    def ingest_pdf(self, pdf_path: str) -> None:
        documents = load_pdf(pdf_path)
        chunks = chunk_documents(
            documents=documents,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )

        if not chunks:
            return

        texts = [chunk["text"] for chunk in chunks]
        embeddings = self._embedder.embed_texts(texts)
        metadatas = [chunk.get("metadata", {}) for chunk in chunks]

        collection = self._chroma_manager.get_or_create_collection(
            self._doc_collection_name
        )

        ids = [f"doc_{uuid.uuid4()}" for _ in texts]
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def ask(self, user_query: str) -> str:
        self.chat_memory.add_user_message(user_query)
        response = self.orchestrator.generate_response(
            user_query=user_query,
            chat_history=self.chat_memory.get_recent_history(limit=2),
        )
        self.chat_memory.add_assistant_message(response)
        return response
