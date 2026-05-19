"""Ollama client wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

import requests


@dataclass
class OllamaClient:
	base_url: str
	model: str
	timeout_s: int

	def generate(self, prompt: str, system: Optional[str] = None) -> str:
		payload = {
			"model": self.model,
			"prompt": prompt,
			"stream": False,
		}
		if system:
			payload["system"] = system

		response = requests.post(
			f"{self.base_url}/api/generate",
			json=payload,
			timeout=self.timeout_s,
		)
		response.raise_for_status()
		data = response.json()
		return data.get("response", "").strip()


@lru_cache(maxsize=1)
def get_ollama_client(base_url: str, model: str, timeout_s: int) -> OllamaClient:
	return OllamaClient(base_url=base_url, model=model, timeout_s=timeout_s)
