"""Core orchestration logic for retrieval-augmented generation."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict, List

from app.config import Settings
from llm.ollama_client import OllamaClient
from llm.prompts import build_prompt
from llm.response_cleaner import clean_response
from memory.memory_classifier import extract_memory
from memory.memory_retrieval import MemoryRetriever
from memory.memory_store import MemoryStore
from reranking.reranker import Reranker
from tools.input_router import classify_input
from tools.small_talk import handle_small_talk
from vector_db.retrieval import VectorRetriever


class Orchestrator:
    """Runs the end-to-end flow for a single user query."""

    def __init__(
        self,
        settings: Settings,
        llm_client: OllamaClient,
        doc_retriever: VectorRetriever,
        memory_retriever: MemoryRetriever,
        memory_store: MemoryStore,
        reranker: Reranker,
    ) -> None:
        self.settings = settings
        self.llm_client = llm_client
        self.doc_retriever = doc_retriever
        self.memory_retriever = memory_retriever
        self.memory_store = memory_store
        self.reranker = reranker

    def generate_response(self, user_query: str, chat_history: List[Dict[str, str]]) -> str:
        query_lower = user_query.lower()

        if (
            "what is my name" in query_lower
            or "tell my name" in query_lower
        ):
            memories = self.memory_retriever.retrieve(
                query_text="name",
                top_k=self.settings.top_k_memory,
                distance_threshold=None,
            )

            for memory in memories:
                text = memory.get("text", "")
                if text.startswith("name:"):
                    name = text.split(":", 1)[1]
                    return f"Your name is {name}"

            return "I don't know your name yet."

        route = classify_input(user_query)

        if route == "small_talk":
            return handle_small_talk(user_query) or "Hi Ajay 👋"

        if route == "memory":
            memory = extract_memory(user_query)
            if memory:
                self.memory_store.save(f"{memory['type']}:{memory['value']}")
            return "Got it, I'll remember that."

        if route == "knowledge":
            response = self.llm_client.generate(prompt=user_query, system=None)
            return clean_response(response)

        if route == "summary":
            print("\nSummary Mode Activated")
            docs = self.doc_retriever.retrieve(
                query_text=user_query,
                top_k=20,
            )
            docs = self.reranker.rerank(user_query, docs)
            print("Retrieved Chunks:", len(docs))

            context = "\n".join(docs)
            prompt = (
                "Document Content:\n\n"
                f"{context}\n\n"
                "Task:\n"
                "Provide a concise overview of this PDF.\n\n"
                "Explain:\n"
                "* main topic\n"
                "* key concepts\n"
                "* what user can learn\n"
                "* short summary\n\n"
                "Only use provided document content."
            )

            response = self.llm_client.generate(prompt=prompt, system=None)
            return clean_response(response)

        memory_hits = self.memory_retriever.retrieve(
            query_text=user_query,
            top_k=self.settings.top_k_memory,
        )
        memory_texts = [hit.get("text", "") for hit in memory_hits]

        if "what is my name" in user_query.lower():
            for text in memory_texts:
                if text.startswith("name:"):
                    name = text.split(":", 1)[1]
                    return f"Your name is {name}"
        docs = self.doc_retriever.retrieve(
            query_text=user_query,
            top_k=self.settings.top_k_docs,
        )
        print("\nBefore reranking:")
        print(docs)

        docs = self.reranker.rerank(user_query, docs)
        print("\nAfter reranking:")
        print(docs)
        doc_hits = self.doc_retriever.query(
            query_text=user_query,
            top_k=self.settings.top_k_docs,
        )

        if "pdf" in query_lower and not doc_hits:
            return "The PDF does not contain this type of content."

        memory_for_prompt = memory_hits
        if doc_hits or "pdf" in query_lower:
            memory_for_prompt = []

        system_prompt, user_prompt = build_prompt(
            user_query=user_query,
            chat_history=chat_history,
            memory_hits=memory_for_prompt,
            doc_texts=docs,
            max_context_chars=self.settings.max_context_chars,
        )

        response = self.llm_client.generate(prompt=user_prompt, system=system_prompt)
        response = clean_response(response)

        if doc_hits:
            response_lower = response.lower()
            if (
                "access" in response_lower
                and ("can't" in response_lower or "cannot" in response_lower)
            ):
                response = "I couldn't find relevant information."

        if doc_hits:
            response = self._append_citations(response, doc_hits)

        self.memory_store.store_interaction(
            user_query=user_query,
            assistant_response=response,
            metadata={
                "timestamp": datetime.utcnow().isoformat(),
                "source": "chat",
            },
        )

        return response

    def _append_citations(self, response: str, doc_hits: List[Dict[str, str]]) -> str:
        for hit in doc_hits:
            meta = hit.get("metadata", {})
            source = meta.get("source", "")
            page = meta.get("page", "")
            if source and page:
                filename = Path(source).name
                return f"{response}\n\nSource:{filename}(Page:{page})"

        return response
