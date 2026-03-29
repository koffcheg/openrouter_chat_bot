import httpx
import pytest

from bot.clients.openrouter import OpenRouterClient


@pytest.mark.asyncio
async def test_openrouter_client_returns_message_content() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/chat/completions")
        payload = {
            "choices": [
                {"message": {"content": "Hello from model"}}
            ]
        }
        return httpx.Response(200, json=payload)

    transport = httpx.MockTransport(handler)
    client = OpenRouterClient(
        api_key="key",
        base_url="https://openrouter.ai/api/v1",
        default_model="nvidia/nemotron-3-super-120b-a12b:free",
        timeout_seconds=10,
        transport=transport,
    )

    result = await client.complete(prompt="Hi", system_prompt="System")
    assert result == "Hello from model"
