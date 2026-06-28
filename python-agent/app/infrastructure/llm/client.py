"""
OpenAI LLM 客户端实现
文档 4.2: 主模型 + 备用模型
文档 5.3: 模型超时 -> 重试一次，再切备用模型
"""
import logging
from typing import Optional, List, Dict, Any

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.application.ports.llm_port import LLMPort, LLMResponse
from app.config import settings
from app.domain.exceptions import (
    DependencyTimeoutException,
    DependencyUnavailableException,
)

logger = logging.getLogger(__name__)


class OpenAILLMClient(LLMPort):
    """
    OpenAI 兼容 LLM 客户端
    文档 5.3:
      - 模型超时 -> 重试一次，再切备用模型
      - 结构化输出错误 -> 使用原模型修复一次
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.openai.com/v1",
        default_model: Optional[str] = None,
        fallback_model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = base_url
        self.default_model = default_model or settings.LLM_MODEL
        self.fallback_model = fallback_model or "gpt-3.5-turbo"
        self.timeout = timeout

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type(DependencyTimeoutException),
    )
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        """发送聊天请求，支持重试和降级"""
        use_model = model or self.default_model

        try:
            return await self._call_api(
                messages=messages,
                model=use_model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format,
            )
        except DependencyTimeoutException:
            logger.warning(f"模型超时，尝试降级到备用模型 | model={use_model}")
            # 文档 5.3: 重试一次，再切备用模型
            try:
                return await self._call_api(
                    messages=messages,
                    model=self.fallback_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                )
            except Exception as e:
                raise DependencyUnavailableException(
                    f"主模型和备用模型均不可用: {e}"
                )

    async def chat_with_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_schema: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """
        带结构化输出的聊天
        文档 3.1: 输出解析失败时只允许修复一次
        """
        response_format = {"type": "json_object", "schema": response_schema}
        response = await self.chat(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format=response_format,
        )

        # 文档 3.1: 解析失败 -> 使用原模型修复一次
        import json

        try:
            json.loads(response.content)
        except json.JSONDecodeError:
            logger.warning("结构化输出解析失败，尝试修复一次")
            repair_messages = messages + [
                {"role": "assistant", "content": response.content},
                {
                    "role": "user",
                    "content": "你的输出格式有误，请严格按照 JSON Schema 重新输出。",
                },
            ]
            response = await self.chat(
                messages=repair_messages,
                model=model,
                temperature=0.0,
                max_tokens=max_tokens,
                response_format=response_format,
            )

        return response

    async def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """获取文本向量"""
        use_model = model or settings.EMBEDDING_MODEL

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=self._build_headers(),
                    json={"input": text, "model": use_model},
                )
                response.raise_for_status()
                data = response.json()
                return data["data"][0]["embedding"]
            except httpx.TimeoutException as e:
                raise DependencyTimeoutException(f"Embedding 请求超时: {e}")
            except httpx.HTTPStatusError as e:
                raise DependencyUnavailableException(f"Embedding 请求失败: {e}")

    async def _call_api(
        self,
        messages: List[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: int,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        """调用 OpenAI API"""
        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            payload["response_format"] = response_format

        logger.info(f"调用 LLM | model={model} | messages_count={len(messages)}")

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._build_headers(),
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                choice = data["choices"][0]
                usage = data.get("usage", {})

                return LLMResponse(
                    content=choice["message"]["content"],
                    model=data["model"],
                    input_tokens=usage.get("prompt_tokens", 0),
                    output_tokens=usage.get("completion_tokens", 0),
                    cache_tokens=usage.get("cached_tokens", 0),
                    finish_reason=choice.get("finish_reason"),
                )
            except httpx.TimeoutException as e:
                raise DependencyTimeoutException(f"LLM 请求超时: {e}")
            except httpx.HTTPStatusError as e:
                raise DependencyUnavailableException(f"LLM 请求失败: {e}")

    def _build_headers(self) -> Dict[str, str]:
        """构建请求头"""
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
