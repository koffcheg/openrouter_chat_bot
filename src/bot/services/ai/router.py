from __future__ import annotations

from bot.services.ai.model_registry import ModelRegistry


class ModelRouter:
    def __init__(self, model_registry: ModelRegistry) -> None:
        self.model_registry = model_registry

    def model_sequence(self, selected_slug: str) -> list[str]:
        sequence: list[str] = []
        if self.model_registry.is_enabled(selected_slug):
            sequence.append(selected_slug)
        else:
            sequence.append(self.model_registry.default_entry().slug)

        fallback_entries = sorted(
            [entry for entry in self.model_registry.list_enabled() if entry.fallback_rank is not None],
            key=lambda entry: entry.fallback_rank,
        )
        for entry in fallback_entries:
            if entry.slug not in sequence:
                sequence.append(entry.slug)
        return sequence
