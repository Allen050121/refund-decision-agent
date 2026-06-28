"""
Prompt 管理
文档 3.1: 使用 Pydantic 定义结构化输出
文档 9.4: 模型和 Prompt 版本管理
"""
from .classify_prompt import CLASSIFY_SYSTEM_PROMPT, classify_messages, ClassifyOutput
from .recommend_prompt import RECOMMEND_SYSTEM_PROMPT, recommend_messages, RecommendOutput

__all__ = [
    "CLASSIFY_SYSTEM_PROMPT",
    "classify_messages",
    "ClassifyOutput",
    "RECOMMEND_SYSTEM_PROMPT",
    "recommend_messages",
    "RecommendOutput",
]
