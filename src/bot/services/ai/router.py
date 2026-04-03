from __future__ import annotations

from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.prompt_policies import normalize_language_code


class ModelRouter:
    def __init__(self, model_registry: ModelRegistry) -> None:
        self.model_registry = model_registry

    def model_sequence(self, selected_slug: str | None, language: str = 'ru') -> list[str]:
        normalized_language = normalize_language_code(language)
        enabled_entries = {entry.slug: entry for entry in self.model_registry.list_enabled()}
        default_slug = self.model_registry.default_entry().slug
        primary = selected_slug if selected_slug in enabled_entries else default_slug

        sequence: list[str] = [primary]

        fallback_entries = sorted(
            [entry for entry in enabled_entries.values() if entry.fallback_rank is not None],
            key=lambda entry: entry.fallback_rank,
        )
        for entry in fallback_entries:
            if entry.slug in sequence:
                continue
            if normalized_language in {'ru', 'uk'} and entry.slug == 'meta-llama/llama-3.3-70b-instruct:free':
                continue
            sequence.append(entry.slug)

        if normalized_language in {'ru', 'uk'} and 'meta-llama/llama-3.3-70b-instruct:free' in enabled_entries and 'openrouter/free' not in sequence:
            # Keep named llama out of the normal Slavic-language path.
            pass
        elif 'meta-llama/llama-3.3-70b-instruct:free' in enabled_entries and 'meta-llama/llama-3.3-70b-instruct:free' not in sequence:
            sequence.append('meta-llama/llama-3.3-70b-instruct:free')

        return sequence
