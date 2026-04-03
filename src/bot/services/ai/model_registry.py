from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelEntry:
    slug: str
    label: str
    enabled: bool = True
    is_default: bool = False
    fallback_rank: int | None = None


class ModelRegistry:
    def __init__(self, entries: list[ModelEntry]) -> None:
        self._entries = {entry.slug: entry for entry in entries}

    @classmethod
    def default(cls) -> 'ModelRegistry':
        return cls(
            [
                ModelEntry(
                    slug='nvidia/nemotron-3-super-120b-a12b:free',
                    label='Nemotron 3 Super (free)',
                    enabled=True,
                    is_default=True,
                    fallback_rank=10,
                ),
                ModelEntry(
                    slug='meta-llama/llama-3.3-70b-instruct:free',
                    label='Llama 3.3 70B Instruct (free)',
                    enabled=True,
                    is_default=False,
                    fallback_rank=20,
                ),
                ModelEntry(
                    slug='openrouter/free',
                    label='OpenRouter Free Router',
                    enabled=True,
                    is_default=False,
                    fallback_rank=90,
                ),
            ]
        )

    def list_enabled(self) -> list[ModelEntry]:
        return [entry for entry in self._entries.values() if entry.enabled]

    def get(self, slug: str) -> ModelEntry | None:
        return self._entries.get(slug)

    def is_enabled(self, slug: str) -> bool:
        entry = self.get(slug)
        return bool(entry and entry.enabled)

    def default_entry(self) -> ModelEntry:
        for entry in self._entries.values():
            if entry.is_default and entry.enabled:
                return entry
        enabled = self.list_enabled()
        if not enabled:
            raise RuntimeError('No enabled models configured')
        return enabled[0]
