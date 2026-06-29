"""
健康检查 API
"""
import logging
from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("")
async def health_check():
    """基础健康检查"""
    return {"status": "OK"}


@router.get("/ready")
async def readiness_check():
    """
    就绪检查 - 验证依赖服务是否可用
    文档: 检查 Java API, Elasticsearch, Redis
    """
    checks = {}

    # 检查 Java API
    checks["java_api"] = await _check_java_api()

    # 检查 Elasticsearch
    checks["elasticsearch"] = await _check_elasticsearch()

    # 检查 Redis
    checks["redis"] = await _check_redis()

    all_ready = all(c.get("status") == "ok" for c in checks.values())

    return {
        "status": "ready" if all_ready else "degraded",
        "checks": checks,
    }


async def _check_java_api() -> dict:
    """检查 Java API 连通性"""
    try:
        import httpx
        from app.config import settings

        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{settings.JAVA_API_URL}/health")
            if response.status_code == 200:
                return {"status": "ok"}
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def _check_elasticsearch() -> dict:
    """检查 Elasticsearch 连通性"""
    try:
        import httpx
        from app.config import settings

        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{settings.ELASTICSEARCH_URL}/_cluster/health")
            if response.status_code == 200:
                data = response.json()
                cluster_status = data.get("status", "unknown")
                return {"status": "ok" if cluster_status in ("green", "yellow") else "error",
                        "cluster_status": cluster_status}
            return {"status": "error", "message": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def _check_redis() -> dict:
    """检查 Redis 连通性"""
    try:
        import redis.asyncio as aioredis
        from app.config import settings

        r = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await r.ping()
        await r.aclose()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
