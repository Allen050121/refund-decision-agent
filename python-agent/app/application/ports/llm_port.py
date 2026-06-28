"""
LLM Port - 抽象接口
文档 4.4: LangGraph Node 不直接依赖具体模型 SDK，调用 Port 接口
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class LLMResponse(BaseModel):
    """LLM 响应"""

    content: str = Field(..., description="模型输出内容")
    model: str = Field(..., description="使用的模型名称")
    input_tokens: int = Field(default=0, description="输入 Token 数")
    output_tokens: int = Field(default=0, description="输出 Token 数")
    cache_tokens: int = Field(default=0, description="缓存 Token 数")
    cost: float = Field(default=0.0, description="成本（美元）")
    finish_reason: Optional[str] = Field(None, description="结束原因")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(None, description="工具调用")


class LLMPort(ABC):
    """
    LLM 抽象接口
    文档 5.3: 模型超时 -> 重试一次，再切备用模型
    """

    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        """
        发送聊天请求
        Args:
            messages: 消息列表 [{"role": "system"|"user"|"assistant", "content": "..."}]
            model: 模型名称，None 使用默认
            temperature: 温度
            max_tokens: 最大 Token
            response_format: 结构化输出格式 (JSON Schema)
        Returns:
            LLMResponse
        Raises:
            DependencyTimeoutException: 模型超时
            DependencyUnavailableException: 模型不可用
        """
        ...

    @abstractmethod
    async def chat_with_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_schema: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """
        带结构化输出的聊天请求
        文档 3.1: 输出解析失败时只允许修复一次
        """
        ...

    @abstractmethod
    async def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """
        获取文本向量
        文档 3.3: BGE 系列或模型供应商 Embedding
        """
        ...
