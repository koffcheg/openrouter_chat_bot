import httpx
import pytest

from bot.clients.openrouter import OpenRouterClient
from bot.core.exceptions import ProviderRateLimitError


@pytest.mark.asyncio
async def test_openrouter_client_returns_message_content() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {"content": "Hello from model"}}]})

    client = OpenRouterClient(api_key="key", base_url="https://openrouter.ai/api/v1", default_model="nvidia/nemotron-3-super-120b-a12b:free", timeout_seconds=10, transport=httpx.MockTransport(handler))
    result = await client.complete(prompt="Hi", system_prompt="System")
    assert result == "Hello from model"


@pytest.mark.asyncio
async def test_openrouter_client_raises_rate_limit() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limit"})

    client = OpenRouterClient(api_key="key", base_url="https://openrouter.ai/api/v1", default_model="nvidia/nemotron-3-super-120b-a12b:free", timeout_seconds=10, transport=httpx.MockTransport(handler))
    with pytest.raises(ProviderRateLimitError):
        await client.complete(prompt="Hi", system_prompt="System")
