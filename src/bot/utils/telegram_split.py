from __future__ import annotations


def split_telegram_text(text: str, max_len: int) -> list[str]:
    if len(text) <= max_len:
        return [text]
    chunks: list[str] = []
    current = ''
    for part in text.splitlines(keepends=True):
        if len(part) > max_len:
            if current:
                chunks.append(current)
                current = ''
            for i in range(0, len(part), max_len):
                chunks.append(part[i:i + max_len])
            continue
        if len(current) + len(part) <= max_len:
            current += part
        else:
            if current:
                chunks.append(current)
            current = part
    if current:
        chunks.append(current)
    return chunks
