import re

GREETINGS = {
    "hi",
    "hii",
    "hello",
    "hey",
    "thanks",
    "bye",
}

FACT_PATTERNS = [
    "who is",
    "what is",
    "where is",
    "history of",
]

SUMMARY_PATTERNS = [
    "explain pdf",
    "explain the pdf",
    "summarize pdf",
    "summarize document",
    "what pdf contains",
    "what does pdf contain",
    "explain document",
]


def classify_input(text):
    text = text.lower().strip()

    words = set(
        re.findall(
            r"\b\w+\b",
            text,
        )
    )

    # exact greeting check
    if words & GREETINGS:
        return "small_talk"

    if (
        "my name is" in text
        or "remember" in text
        or "i am learning" in text
    ):
        return "memory"

    for pattern in FACT_PATTERNS:
        if pattern in text:
            return "knowledge"

    for pattern in SUMMARY_PATTERNS:
        if pattern in text:
            return "summary"

    return "normal"
