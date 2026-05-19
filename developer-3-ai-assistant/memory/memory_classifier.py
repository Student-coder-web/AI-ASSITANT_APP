"""Classifies and extracts user memory statements."""

from __future__ import annotations

import re


_MEMORY_PATTERNS = [
    r"\bmy name is\b",
    r"\bi am\b",
    r"\bi'm\b",
    r"\bremember\b",
    r"\bmy favorite\b",
]


def is_memory_statement(text: str) -> bool:
    cleaned = text.strip().lower()
    if not cleaned:
        return False

    if "?" in cleaned:
        return False

    return any(re.search(pattern, cleaned) for pattern in _MEMORY_PATTERNS)


def extract_memory(text):
    text = text.lower()

    match = re.search(
        r"my name is\s+([a-zA-Z]+)",
        text,
    )

    if match:
        return {
            "type": "name",
            "value": match.group(1).capitalize(),
        }

    return None
