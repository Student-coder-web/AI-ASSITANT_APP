"""Centralized configuration for the assistant."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional


def _load_dotenv() -> None:
	try:
		from dotenv import load_dotenv  # type: ignore

		load_dotenv()
	except Exception:
		# Optional dependency. If missing, rely on environment variables.
		pass


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_CHROMA_DIR = BASE_DIR / "chroma_db"


@dataclass(frozen=True)
class Settings:
	app_name: str
	ollama_base_url: str
	ollama_model: str
	embedding_model_name: str
	chroma_persist_dir: Path
	chroma_collection_docs: str
	chroma_collection_memory: str
	chunk_size: int
	chunk_overlap: int
	top_k_docs: int
	top_k_memory: int
	max_chat_messages: int
	max_context_chars: int
	request_timeout_s: int

	@classmethod
	def from_env(cls) -> "Settings":
		_load_dotenv()

		chroma_dir = os.getenv("CHROMA_PERSIST_DIR")
		data_dir = os.getenv("DATA_DIR")

		return cls(
			app_name=os.getenv("APP_NAME", "Developer-3-AI-Assistant"),
			ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
			ollama_model=os.getenv("OLLAMA_MODEL", "phi3"),
			embedding_model_name=os.getenv(
				"EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
			),
			chroma_persist_dir=Path(chroma_dir) if chroma_dir else DEFAULT_CHROMA_DIR,
			chroma_collection_docs=os.getenv("CHROMA_COLLECTION_DOCS", "documents"),
			chroma_collection_memory=os.getenv("CHROMA_COLLECTION_MEMORY", "memory"),
			chunk_size=int(os.getenv("CHUNK_SIZE", "800")),
			chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
			top_k_docs=int(os.getenv("TOP_K_DOCS", "6")),
			top_k_memory=int(os.getenv("TOP_K_MEMORY", "6")),
			max_chat_messages=int(os.getenv("MAX_CHAT_MESSAGES", "12")),
			max_context_chars=int(os.getenv("MAX_CONTEXT_CHARS", "6000")),
			request_timeout_s=int(os.getenv("REQUEST_TIMEOUT_S", "90")),
		)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
	return Settings.from_env()
