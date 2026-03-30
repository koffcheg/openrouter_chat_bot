from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ReplyContextBuilder:
    max_messages: int
    max_chars: int

    @staticmethod
    def message_text(message) -> str:
        text = getattr(message, 'text', None) or getattr(message, 'caption', None) or ''
        return ' '.join(text.split())

    def build_ancestor_context(self, message) -> str:
        cursor = getattr(message, 'reply_to_message', None)
        items: list[str] = []
        while cursor is not None and len(items) < self.max_messages:
            text = self.message_text(cursor)
            if text:
                items.append(text)
            cursor = getattr(cursor, 'reply_to_message', None)
        items.reverse()
        lines: list[str] = []
        total = 0
        for idx, item in enumerate(items, start=1):
            line = f"[context {idx}] {item}"
            extra = len(line) + (1 if lines else 0)
            if total + extra > self.max_chars:
                break
            lines.append(line)
            total += extra
        return '\n'.join(lines)
