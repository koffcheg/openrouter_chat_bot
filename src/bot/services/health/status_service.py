from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeStatus:
    selected_model: str = ''
    fallback_chain: list[str] = field(default_factory=list)
    attempted_models: list[str] = field(default_factory=list)
    last_served_model: str = ''
    fallback_used: bool = False
    last_provider_error: str = ''
    last_duration_ms: int | None = None
    last_command: str = ''
    total_requests: int = 0
    provider_failures: int = 0


class StatusService:
    def __init__(self) -> None:
        self._by_chat: dict[int, RuntimeStatus] = {}

    def _get(self, chat_id: int) -> RuntimeStatus:
        if chat_id not in self._by_chat:
            self._by_chat[chat_id] = RuntimeStatus()
        return self._by_chat[chat_id]

    def begin_request(self, *, chat_id: int, command: str, selected_model: str, fallback_chain: list[str]) -> None:
        status = self._get(chat_id)
        status.selected_model = selected_model
        status.fallback_chain = list(fallback_chain)
        status.attempted_models = []
        status.last_command = command
        status.last_provider_error = ''
        status.last_duration_ms = None
        status.fallback_used = False

    def record_attempt(self, *, chat_id: int, model_slug: str) -> None:
        status = self._get(chat_id)
        status.attempted_models.append(model_slug)

    def record_provider_error(self, *, chat_id: int, error_text: str) -> None:
        status = self._get(chat_id)
        status.provider_failures += 1
        status.last_provider_error = error_text

    def record_success(self, *, chat_id: int, model_slug: str, duration_ms: int) -> None:
        status = self._get(chat_id)
        status.total_requests += 1
        status.last_served_model = model_slug
        status.fallback_used = bool(status.attempted_models and status.attempted_models[0] != model_slug)
        status.last_duration_ms = duration_ms

    def record_terminal_failure(self, *, chat_id: int, error_text: str, duration_ms: int | None = None) -> None:
        status = self._get(chat_id)
        status.total_requests += 1
        status.last_provider_error = error_text
        status.last_duration_ms = duration_ms

    def snapshot(self, *, chat_id: int) -> RuntimeStatus:
        status = self._get(chat_id)
        return RuntimeStatus(
            selected_model=status.selected_model,
            fallback_chain=list(status.fallback_chain),
            attempted_models=list(status.attempted_models),
            last_served_model=status.last_served_model,
            fallback_used=status.fallback_used,
            last_provider_error=status.last_provider_error,
            last_duration_ms=status.last_duration_ms,
            last_command=status.last_command,
            total_requests=status.total_requests,
            provider_failures=status.provider_failures,
        )
