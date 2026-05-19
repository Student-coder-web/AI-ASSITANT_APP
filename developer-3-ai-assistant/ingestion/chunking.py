"""Chunking logic using RecursiveCharacterTextSplitter."""

from __future__ import annotations

from typing import Dict, List

from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_documents(
	documents: List[Dict[str, str]],
	chunk_size: int,
	chunk_overlap: int,
) -> List[Dict[str, str]]:
	splitter = RecursiveCharacterTextSplitter(
		chunk_size=chunk_size,
		chunk_overlap=chunk_overlap,
	)

	chunks: List[Dict[str, str]] = []
	for doc in documents:
		text = doc.get("text", "")
		if not text:
			continue
		metadata = doc.get("metadata", {})
		for chunk in splitter.split_text(text):
			chunks.append({"text": chunk, "metadata": metadata})

	return chunks
