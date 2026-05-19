"""In-memory chat history."""

from __future__ import annotations

from typing import Dict, List

from app.constants import ROLE_ASSISTANT, ROLE_USER


class ChatMemory:
	"""Stores recent chat messages in memory."""

	def __init__(self, max_messages: int = 12) -> None:
		self.max_messages = max_messages
		self._messages: List[Dict[str, str]] = []

	def add_user_message(self, content: str) -> None:
		self._messages.append({"role": ROLE_USER, "content": content})
		self._trim()

	def add_assistant_message(self, content: str) -> None:
		self._messages.append({"role": ROLE_ASSISTANT, "content": content})
		self._trim()

	def get_recent_history(self, limit: int = 2) -> List[Dict[str, str]]:
		if limit <= 0:
			return []
		return list(self._messages[-limit:])

	def _trim(self) -> None:
		if len(self._messages) > self.max_messages:
			self._messages = self._messages[-self.max_messages :]
