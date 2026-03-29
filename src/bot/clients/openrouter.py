from __future__ import annotations

from typing import Any

import httpx

from bot.core.exceptions import ProviderError, ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError


class OpenRouterClient:
    def __init__(self, *, api_key: str, base_url: str, default_model: str, timeout_seconds: float, http_referer: str = "", app_title: str = "", transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout_seconds = timeout_seconds
        self.http_referer = http_referer
        self.app_title = app_title
        self.transport = transport

    async def complete(self, *, prompt: str, system_prompt: str, model: str | None = None) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        if self.http_referer:
            headers["HTTP-Referer"] = self.http_referer
        if self.app_title:
            headers["X-Title"] = self.app_title

        payload: dict[str, Any] = {
            "model": model or self.default_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds, transport=self.transport) as client:
                response = await client.post(f"{self.base_url}/chat/completions", headers=headers, json=payload)
        except httpx.TimeoutException as exc:
            raise ProviderTimeoutError("OpenRouter request timed out") from exc
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("OpenRouter connection failed") from exc

        if response.status_code == 429:
            raise ProviderRateLimitError("OpenRouter rate limited the request")
        if response.status_code >= 500:
            raise ProviderUnavailableError(f"OpenRouter request failed with status {response.status_code}")
        if response.status_code >= 400:
            raise ProviderError(f"OpenRouter request failed with status {response.status_code}")

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError, TypeError) as exc:
            raise ProviderError("OpenRouter response did not contain message content") from exc
