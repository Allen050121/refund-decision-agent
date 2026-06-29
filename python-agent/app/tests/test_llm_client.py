"""
测试 OpenAI 兼容 LLM 客户端
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import httpx

from app.infrastructure.llm.client import OpenAILLMClient, SUPPORTS_HTTPX_PROXY


@pytest.mark.asyncio
async def test_chat_uses_configured_openai_compatible_endpoint_without_proxy():
    """测试默认不强制使用本地代理"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "claude-sonnet-4-6",
        "choices": [
            {
                "message": {"content": "ok"},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 2,
            "cached_tokens": 0,
        },
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_async_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_async_client.return_value = mock_client_instance

        client = OpenAILLMClient(
            api_key="test-key",
            base_url="https://cc.freemodel.dev/v1/",
            default_model="claude-sonnet-4-6",
            proxy_url=None,
        )
        result = await client.chat([{"role": "user", "content": "ping"}])

    mock_async_client.assert_called_once_with(timeout=30.0)
    mock_client_instance.post.assert_called_once()
    url = mock_client_instance.post.call_args.args[0]
    kwargs = mock_client_instance.post.call_args.kwargs

    assert url == "https://cc.freemodel.dev/v1/chat/completions"
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["json"]["model"] == "claude-sonnet-4-6"
    assert result.content == "ok"
    assert result.input_tokens == 10
    assert result.output_tokens == 2


@pytest.mark.asyncio
async def test_chat_uses_proxy_only_when_configured():
    """测试只有显式配置代理时才走代理"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "model": "deepseek-chat",
        "choices": [{"message": {"content": "ok"}, "finish_reason": "stop"}],
        "usage": {},
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_async_client:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        mock_async_client.return_value = mock_client_instance

        client = OpenAILLMClient(
            api_key="test-key",
            base_url="https://api.deepseek.com",
            default_model="deepseek-chat",
            proxy_url="http://127.0.0.1:7897",
        )
        await client.chat([{"role": "user", "content": "ping"}])

    if SUPPORTS_HTTPX_PROXY:
        mock_async_client.assert_called_once_with(
            timeout=30.0,
            proxy="http://127.0.0.1:7897",
        )
    else:
        mock_async_client.assert_called_once_with(
            timeout=30.0,
            proxies={
                "http://": "http://127.0.0.1:7897",
                "https://": "http://127.0.0.1:7897",
            },
        )
