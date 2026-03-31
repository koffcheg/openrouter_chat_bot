from __future__ import annotations

import re


_MARKDOWN_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MARKDOWN_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_MISSING_SPACE = re.compile(r"(?<=[A-Za-zА-Яа-яЁё])(?=[A-ZА-ЯЁ][a-zа-яё])")


def cleanup_model_text(text: str) -> str:
    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")
    cleaned = cleaned.replace("‑", "-").replace("—", " — ").replace("–", " - ")
    cleaned = _MARKDOWN_BOLD.sub(r"\1", cleaned)
    cleaned = _MARKDOWN_ITALIC.sub(r"\1", cleaned)
    cleaned = cleaned.replace("```", "")
    cleaned = _MISSING_SPACE.sub(" ", cleaned)
    lines = []
    for line in cleaned.split("\n"):
        normalized = _MULTI_SPACE.sub(" ", line).strip()
        lines.append(normalized)
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()
