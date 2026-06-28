"""
Noop Tracer - 当 Langfuse 未配置时使用
"""
from contextlib import contextmanager
from typing import Optional, Dict, Any, Generator


class NoopTracer:
    """空实现 Tracer，不记录任何数据"""

    def start_trace(self, task_id: str, **kwargs) -> None:
        return None

    def start_span(self, trace: Any, name: str, **kwargs) -> None:
        return None

    def end_span(self, span: Any, **kwargs) -> None:
        pass

    def record_model_call(self, trace: Any, **kwargs) -> None:
        pass

    def record_tool_call(self, trace: Any, **kwargs) -> None:
        pass

    def flush(self) -> None:
        pass

    @contextmanager
    def trace_task(self, task_id: str, **kwargs) -> Generator:
        yield None
