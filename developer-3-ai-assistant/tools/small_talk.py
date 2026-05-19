"""Small-talk handler."""

from __future__ import annotations

from typing import Optional


def handle_small_talk(text: str) -> Optional[str]:
    text = text.lower()

    if "hi" in text or "hello" in text:
        return "Hi Ajay 👋"

    if "thanks" in text:
        return "You're welcome."

    if "bye" in text:
        return "See you."

    return None
