"""
Langfuse 可观测性集成
文档 10: 统一关联 ID
  trace_id -> task_id -> message_id -> model_call_id -> tool_call_id
文档 10: 记录指标
  - 队列等待时间
  - 每个 LangGraph 节点执行时间
  - 模型名称和路由原因
  - 输入、输出、缓存 Token
  - 模型成本
  - 检索文档 ID 和分数
  - 工具参数摘要和结果状态
"""
import logging
import time
from contextlib import contextmanager
from typing import Optional, Dict, Any, Generator

from app.config import settings

logger = logging.getLogger(__name__)


class LangfuseTracer:
    """
    Langfuse Trace 管理器
    文档 10: 每次执行可定位到具体 Graph 节点、模型调用和工具调用
    """

    def __init__(self):
        self._langfuse = None
        self._enabled = bool(settings.LANGFUSE_PUBLIC_KEY and settings.LANGFUSE_SECRET_KEY)

        if self._enabled:
            try:
                from langfuse import Langfuse

                self._langfuse = Langfuse(
                    public_key=settings.LANGFUSE_PUBLIC_KEY,
                    secret_key=settings.LANGFUSE_SECRET_KEY,
                    host=settings.LANGFUSE_HOST,
                )
                logger.info("Langfuse 已初始化")
            except ImportError:
                logger.warning("Langfuse 未安装，可观测性禁用")
                self._enabled = False
            except Exception as e:
                logger.warning(f"Langfuse 初始化失败: {e}")
                self._enabled = False
        else:
            logger.info("Langfuse 未配置密钥，可观测性禁用")

    def start_trace(
        self,
        task_id: str,
        trace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """
        开始追踪
        文档 10: trace_id -> task_id -> message_id
        """
        if not self._enabled or not self._langfuse:
            return None

        try:
            trace = self._langfuse.trace(
                name="refund-agent-task",
                id=trace_id or task_id,
                session_id=task_id,
                user_id=user_id,
                metadata=metadata or {},
            )
            logger.debug(f"Trace 开始 | task_id={task_id}")
            return trace
        except Exception as e:
            logger.warning(f"Trace 开始失败: {e}")
            return None

    def start_span(
        self,
        trace: Any,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        """开始一个 Span（节点执行）"""
        if not trace:
            return None

        try:
            span = trace.span(name=name, metadata=metadata or {})
            return span
        except Exception as e:
            logger.warning(f"Span 开始失败: {e}")
            return None

    def end_span(self, span: Any, output: Optional[Dict[str, Any]] = None) -> None:
        """结束 Span"""
        if not span:
            return

        try:
            span.end(output=output)
        except Exception as e:
            logger.warning(f"Span 结束失败: {e}")

    def record_model_call(
        self,
        trace: Any,
        name: str,
        model: str,
        input_messages: Any,
        output: str,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
    ) -> None:
        """
        记录模型调用
        文档 10: 模型名称、Token、成本
        """
        if not trace:
            return

        try:
            trace.generation(
                name=name,
                model=model,
                input=input_messages,
                output=output,
                usage={
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens,
                },
                cost=cost,
            )
        except Exception as e:
            logger.warning(f"模型调用记录失败: {e}")

    def record_tool_call(
        self,
        trace: Any,
        name: str,
        input_params: Dict[str, Any],
        output: Any,
        status: str = "success",
    ) -> None:
        """
        记录工具调用
        文档 10: 工具参数摘要和结果状态
        """
        if not trace:
            return

        try:
            trace.span(
                name=f"tool:{name}",
                input=input_params,
                output=output,
                metadata={"status": status},
            )
        except Exception as e:
            logger.warning(f"工具调用记录失败: {e}")

    def flush(self) -> None:
        """刷新所有待发送的数据"""
        if self._langfuse:
            try:
                self._langfuse.flush()
            except Exception as e:
                logger.warning(f"Langfuse flush 失败: {e}")

    @contextmanager
    def trace_task(self, task_id: str, **kwargs) -> Generator:
        """
        上下文管理器：追踪任务执行
        用法:
            with tracer.trace_task("T001", user_id="U1001") as trace:
                # 执行工作流
        """
        trace = self.start_trace(task_id, **kwargs)
        start_time = time.time()
        try:
            yield trace
        finally:
            elapsed = time.time() - start_time
            if trace:
                logger.info(f"任务 Trace 完成 | task_id={task_id} | elapsed={elapsed:.2f}s")
            self.flush()
