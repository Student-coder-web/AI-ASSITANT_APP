"""Post-processes LLM output to remove identity leakage and prompt echoes."""

from __future__ import annotations

import re


_REMOVE_PATTERNS = [
    r"i'm phi from microsoft.*",
    r"i am phi from microsoft.*",
    r"phi from microsoft.*",
    r"source:\s*chat history.*",
    r"context:\s*.*",
    r"user question:\s*.*",
    r"system:\s*.*",
    r"instructions?:.*",
]


def clean_response(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        return cleaned

    for pattern in _REMOVE_PATTERNS:
        cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE | re.DOTALL).strip()

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned
