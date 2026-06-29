"""
FastAPI 应用入口
文档 4.1: FastAPI + LangGraph Agent 服务
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    启动时初始化依赖，关闭时释放资源
    """
    # ---- 启动 ----
    logger.info("=" * 60)
    logger.info("售后退款决策 Agent 启动")
    logger.info(f"  Java API: {settings.JAVA_API_URL}")
    logger.info(f"  Elasticsearch: {settings.ELASTICSEARCH_URL}")
    logger.info(f"  Redis: {settings.REDIS_URL}")
    logger.info(f"  LLM Model: {settings.LLM_MODEL}")
    logger.info("=" * 60)

    # 初始化 Port 实例
    _init_ports()

    yield

    # ---- 关闭 ----
    logger.info("应用关闭，清理资源...")


def _init_ports():
    """初始化并注入 Port 实例到 Agent 节点"""
    from app.agent.nodes import set_ports

    # 初始化 LLM Port
    llm_port = None
    if settings.OPENAI_API_KEY:
        from app.infrastructure.llm import OpenAILLMClient

        llm_port = OpenAILLMClient(
            base_url=settings.LLM_BASE_URL,
        )
        logger.info(f"LLM Port: 使用模型 {settings.LLM_MODEL} @ {settings.LLM_BASE_URL}")
    else:
        logger.warning("OPENAI_API_KEY 未配置，LLM 功能将使用规则匹配回退")

    # 初始化 Retrieval Port
    retrieval_port = None
    try:
        from app.infrastructure.retrieval import ElasticsearchRetriever

        retrieval_port = ElasticsearchRetriever()
        logger.info("Retrieval Port: Elasticsearch 检索器已初始化")
    except Exception as e:
        logger.warning(f"Elasticsearch 检索器初始化失败: {e}")

    # 注入到节点
    set_ports(llm=llm_port, retrieval=retrieval_port)


def create_app() -> FastAPI:
    """创建 FastAPI 应用实例"""

    app = FastAPI(
        title="售后退款决策 Agent",
        description="面向在线教育场景的售后退款决策 Agent（文档 4.1）",
        version="0.2.0",
        lifespan=lifespan,
    )

    # 注册路由
    from app.api import demo, health, tasks

    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
    app.include_router(demo.router, prefix="/demo", tags=["demo"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True,
    )
