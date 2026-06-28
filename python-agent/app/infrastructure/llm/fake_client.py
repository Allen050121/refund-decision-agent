"""
Fake LLM 客户端 - 用于确定性测试
文档 4.4: LangGraph Node 调用 Port 接口，方便替换 Fake 实现完成确定性测试
"""
import json
from typing import Optional, List, Dict, Any

from app.application.ports.llm_port import LLMPort, LLMResponse


class FakeLLMClient(LLMPort):
    """
    Fake LLM 实现
    用于单元测试和集成测试，返回预定义的响应
    """

    def __init__(self, responses: Optional[List[Dict[str, Any]]] = None):
        """
        Args:
            responses: 预定义的响应队列，按调用顺序返回
                       每项可包含 content, model, input_tokens, output_tokens 等
        """
        self._responses = responses or []
        self._call_count = 0
        self.call_history: List[Dict[str, Any]] = []

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> LLMResponse:
        """返回预定义的响应"""
        self._call_count += 1
        self.call_history.append({
            "type": "chat",
            "messages": messages,
            "model": model,
            "temperature": temperature,
        })

        if self._responses:
            resp = self._responses.pop(0)
        else:
            resp = self._default_response(messages)

        return LLMResponse(
            content=resp.get("content", ""),
            model=resp.get("model", "fake-model"),
            input_tokens=resp.get("input_tokens", 10),
            output_tokens=resp.get("output_tokens", 20),
        )

    async def chat_with_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_schema: Dict[str, Any],
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> LLMResponse:
        """返回预定义的结构化响应"""
        self._call_count += 1
        self.call_history.append({
            "type": "structured_chat",
            "messages": messages,
            "model": model,
            "schema": response_schema,
        })

        if self._responses:
            resp = self._responses.pop(0)
        else:
            resp = self._default_structured_response(messages, response_schema)

        return LLMResponse(
            content=json.dumps(resp.get("content", {})),
            model=resp.get("model", "fake-model"),
            input_tokens=resp.get("input_tokens", 10),
            output_tokens=resp.get("output_tokens", 30),
        )

    async def get_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """返回固定的向量"""
        self._call_count += 1
        self.call_history.append({
            "type": "embedding",
            "text": text,
            "model": model,
        })
        # 返回一个固定维度的假向量
        return [0.1] * 1536

    def _default_response(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """默认响应 - 根据消息内容简单匹配"""
        last_msg = messages[-1]["content"] if messages else ""
        return {
            "content": json.dumps(self._classify_content(last_msg)),
            "model": "fake-model",
        }

    def _default_structured_response(self, messages: Optional[List[Dict[str, str]]] = None, schema: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """默认结构化响应 - 根据 schema 和消息内容匹配"""
        # 根据 schema 判断是分类还是推荐
        if schema and "properties" in schema:
            props = schema["properties"]
            if "decision" in props:
                # 推荐请求 - 返回决策
                return self._recommend_response(messages)
            elif "intent" in props:
                # 分类请求 - 返回意图
                content = self._extract_user_content(messages)
                return {"content": self._classify_content(content), "model": "fake-model"}

        # 默认按消息内容判断
        content = self._extract_user_content(messages)
        return {"content": self._classify_content(content), "model": "fake-model"}

    def _extract_user_content(self, messages: Optional[List[Dict[str, str]]]) -> str:
        """从消息列表中提取用户内容"""
        if not messages:
            return ""
        for msg in messages:
            if msg.get("role") == "user":
                return msg.get("content", "")
        return ""

    def _recommend_response(self, messages: Optional[List[Dict[str, str]]]) -> Dict[str, Any]:
        """生成推荐响应 - 根据工单内容判断决策"""
        content = self._extract_user_content(messages)
        classification = self._classify_content(content)
        reason_code = classification.get("reason_code", "GENERAL")

        # 根据原因码生成决策
        if reason_code in ("COURSE_UNAVAILABLE", "DUPLICATE_PURCHASE"):
            decision = "REFUND_RECOMMENDED"
        elif reason_code in ("EXCEEDED_PROGRESS_LIMIT", "EXPIRED_REFUND_WINDOW"):
            decision = "REFUND_REJECTED"
        elif reason_code == "NO_REASON":
            decision = "WAIT_FOR_APPROVAL"
        else:
            decision = "NEED_MORE_INFORMATION"

        return {
            "content": {
                "decision": decision,
                "reason": f"根据原因码 {reason_code} 自动判定",
                "recommended_amount": 19900 if decision == "REFUND_RECOMMENDED" else None,
                "risk_hints": [],
                "rule_citations": ["REFUND-2026-001"],
            },
            "model": "fake-model",
        }

    def _classify_content(self, text: str) -> Dict[str, Any]:
        """根据文本内容分类"""
        if not text.strip():
            return {"intent": "OTHER", "reason_code": "GENERAL"}

        # 先检测具体原因（不依赖退款关键词）
        reason_code = "GENERAL"
        has_specific_reason = False
        if "打不开" in text or "无法观看" in text or "故障" in text or "无法" in text:
            reason_code = "COURSE_UNAVAILABLE"
            has_specific_reason = True
        elif "重复" in text or "买重了" in text or "买重" in text:
            reason_code = "DUPLICATE_PURCHASE"
            has_specific_reason = True
        elif "不想学了" in text or "无理由" in text or "不想学" in text:
            reason_code = "NO_REASON"
            has_specific_reason = True
        elif ("超过" in text and ("天" in text or "日" in text)) or "超期" in text:
            reason_code = "EXPIRED_REFUND_WINDOW"
            has_specific_reason = True

        # 判断意图：有退款关键词或具体问题关键词都视为退款意图
        is_refund = "退款" in text or "refund" in text.lower() or "售后" in text or "投诉" in text
        intent = "REFUND_REQUEST" if (is_refund or has_specific_reason) else "OTHER"

        return {
            "intent": intent,
            "reason_code": reason_code,
            "confidence": 0.9,
        }

    @property
    def total_calls(self) -> int:
        return self._call_count

    def reset(self) -> None:
        """重置调用记录"""
        self._call_count = 0
        self.call_history = []
