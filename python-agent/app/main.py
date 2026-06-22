from fastapi import FastAPI
from app.config import settings


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""

    app = FastAPI(
        title="售后退款决策 Agent",
        description="面向在线教育场景的售后退款决策 Agent",
        version="0.1.0"
    )

    # 注册路由
    from app.api import health, tasks

    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

    return app


app = create_app()
