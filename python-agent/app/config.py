"""
应用配置
"""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # 服务配置
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Java API (本地运行)
    JAVA_API_URL: str = "http://localhost:8080"
    JAVA_API_TOKEN: str = "internal-service-token"
    JAVA_API_TIMEOUT: int = 10  # 秒

    # Redis (Virtual Machine)
    REDIS_URL: str = "redis://192.168.85.66:6379/0"
    REDIS_STREAM_NAME: str = "after-sale:agent:tasks"
    REDIS_EVENTS_KEY: str = "after-sale:agent:events:{task_id}"

    # Elasticsearch (Virtual Machine)
    ELASTICSEARCH_URL: str = "http://192.168.85.66:9200"
    ELASTICSEARCH_INDEX: str = "refund-rules"

    # LLM
    LLM_MODEL: str = "claude-sonnet-4-6"
    LLM_BASE_URL: str = "https://cc.freemodel.dev/v1"
    LLM_PROXY_URL: str | None = None
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 2000
    OPENAI_API_KEY: str | None = None

    # Embedding
    EMBEDDING_MODEL: str = "text-embedding-ada-002"

    # Langfuse (可观测性)
    LANGFUSE_PUBLIC_KEY: str | None = None
    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_HOST: str = "https://cloud.langfuse.com"

    # 任务限制
    MAX_TASK_TIMEOUT: int = 300  # 秒
    MAX_MODEL_CALLS: int = 10
    MAX_TOOL_CALLS: int = 15
    MAX_TOKEN_COST: float = 1.0  # 美元


settings = Settings()
