"""
Java API 调用工具
文档 3.2: 业务数据查询工具
"""
import httpx
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config import settings


class JavaApiClient:
    """Java API 客户端"""

    def __init__(self):
        self.base_url = settings.JAVA_API_URL
        self.timeout = settings.JAVA_API_TIMEOUT
        self.headers = {
            "Content-Type": "application/json",
            "X-Service-Token": settings.JAVA_API_TOKEN
        }

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4)
    )
    async def get_order(self, order_id: str, requester_user_id: str) -> Dict[str, Any]:
        """
        查询订单信息
        文档工具：get_order(order_id, requester_user_id)
        """
        url = f"{self.base_url}/api/orders/{order_id}"
        params = {"requesterUserId": requester_user_id}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4)
    )
    async def get_learning_progress(self, order_id: str, requester_user_id: str) -> Dict[str, Any]:
        """
        查询学习进度
        文档工具：get_learning_progress(order_id, requester_user_id)
        """
        url = f"{self.base_url}/api/learning/{order_id}"
        params = {"requesterUserId": requester_user_id}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, params=params, headers=self.headers)
            response.raise_for_status()
            return response.json()

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=4)
    )
    async def get_course_status(self, course_id: str) -> Dict[str, Any]:
        """
        查询课程状态
        文档工具：get_course_status(course_id)
        """
        url = f"{self.base_url}/api/courses/{course_id}/status"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()

    def handle_api_error(self, error: httpx.HTTPStatusError) -> Dict[str, Any]:
        """处理 API 错误"""
        status_code = error.response.status_code
        error_data = error.response.json() if error.response.text else {}

        if status_code == 400:
            return {
                "error": "VALIDATION_ERROR",
                "message": error_data.get("message", "参数错误")
            }
        elif status_code == 403:
            return {
                "error": "PERMISSION_DENIED",
                "message": error_data.get("message", "权限拒绝")
            }
        elif status_code == 404:
            return {
                "error": "RESOURCE_NOT_FOUND",
                "message": error_data.get("message", "资源不存在")
            }
        elif status_code == 405:
            return {
                "error": "METHOD_NOT_ALLOWED",
                "message": error_data.get("message", "方法不允许")
            }
        elif status_code >= 500:
            return {
                "error": "DEPENDENCY_UNAVAILABLE",
                "message": error_data.get("message", "服务不可用")
            }
        else:
            return {
                "error": "UNKNOWN_ERROR",
                "message": error_data.get("message", "未知错误")
            }
