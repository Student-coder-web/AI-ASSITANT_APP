"""PDF loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from pypdf import PdfReader


def load_pdf(file_path: str | Path) -> List[Dict[str, str]]:
	"""Load a PDF and return page-level documents."""

	path = Path(file_path)
	if not path.exists():
		raise FileNotFoundError(f"PDF not found: {path}")

	reader = PdfReader(str(path))
	documents: List[Dict[str, str]] = []

	filename = path.name
	for page_index, page in enumerate(reader.pages, start=1):
		text = page.extract_text() or ""
		text = text.strip()
		if not text:
			continue
		documents.append(
			{
				"text": text,
				"metadata": {
					"source": filename,
					"page": str(page_index),
				},
			}
		)

	return documents
