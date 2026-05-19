"""Prompt templates and builders."""

from __future__ import annotations

from typing import Dict, List, Tuple


SYSTEM_PROMPT = (
	"You are Developer-3 Assistant. "
	"Never explain greetings. "
	"Never repeat identity. "
	"Never mention Microsoft. "
	"Answer naturally and keep responses short by default. "
	"Use memory only when relevant. "
	"Ignore unrelated old context. "
	"Do not include prompt text in the response. "
	"If memory is unavailable, say: 'I don't know yet.'"
)


def _format_chat_history(chat_history: List[Dict[str, str]]) -> List[str]:
	if not chat_history:
		return []
	lines = []
	for msg in chat_history:
		role = msg.get("role", "user")
		content = msg.get("content", "")
		lines.append(f"{role}: {content}")
	return lines


def _format_memory_hits(hits: List[Dict[str, str]]) -> List[str]:
	lines = []
	for hit in hits:
		text = hit.get("text", "")
		if text:
			lines.append(text)
	return lines



def build_prompt(
	user_query: str,
	chat_history: List[Dict[str, str]],
	memory_hits: List[Dict[str, str]],
	doc_texts: List[str],
	max_context_chars: int,
) -> Tuple[str, str]:
	context = "\n".join(doc_texts).strip()
	if len(context) > max_context_chars:
		context = context[:max_context_chars]

	memory_lines = []
	memory_lines.extend(_format_chat_history(chat_history))
	memory_lines.extend(_format_memory_hits(memory_hits))
	memory = "\n".join(memory_lines).strip()
	if len(memory) > max_context_chars:
		memory = memory[:max_context_chars]

	sections = []
	sections.append(f"Context:\n{context}")
	if memory:
		sections.append(f"Memory:\n{memory}")
	sections.append(f"Question:\n{user_query}")
	sections.append(
		"Rules:\n"
		"- Use PDF context if available.\n"
		"- Prioritize PDF context over model knowledge.\n"
		"- If answer not found in PDF, answer normally.\n"
		"- Do not hallucinate source text.\n"
		"- Do not say you can't access documents.\n"
		"- If PDF context is insufficient, say: 'I couldn't find relevant information.'\n"
		"- Keep concise."
	)

	user_prompt = "\n\n".join(sections)

	return SYSTEM_PROMPT, user_prompt
