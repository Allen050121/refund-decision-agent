"""
测试 Java API 客户端
"""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.infrastructure.java_api.client import JavaApiClient


@pytest.mark.asyncio
async def test_get_order_success():
    """测试订单查询成功"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 200,
        "data": {"orderId": "ORD-001", "status": "PAID"},
    }
    mock_response.raise_for_status = MagicMock()

    client = JavaApiClient()

    with patch("httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        MockClient.return_value = mock_client_instance

        result = await client.get_order("ORD-001", "U1001")
        assert result["code"] == 200
        assert result["data"]["orderId"] == "ORD-001"


@pytest.mark.asyncio
async def test_get_learning_progress_success():
    """测试学习进度查询成功"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 200,
        "data": {"progressPercentage": 15},
    }
    mock_response.raise_for_status = MagicMock()

    client = JavaApiClient()

    with patch("httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        MockClient.return_value = mock_client_instance

        result = await client.get_learning_progress("ORD-001", "U1001")
        assert result["code"] == 200


@pytest.mark.asyncio
async def test_get_course_status_success():
    """测试课程状态查询成功"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "code": 200,
        "data": {"courseId": "C-101", "status": "ACTIVE"},
    }
    mock_response.raise_for_status = MagicMock()

    client = JavaApiClient()

    with patch("httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        mock_client_instance.get.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=None)
        MockClient.return_value = mock_client_instance

        result = await client.get_course_status("C-101")
        assert result["code"] == 200


def test_handle_api_error_400():
    """测试 400 错误处理"""
    mock_error = MagicMock()
    mock_error.response.status_code = 400
    mock_error.response.text = '{"message": "参数错误"}'
    mock_error.response.json.return_value = {"message": "参数错误"}

    client = JavaApiClient()
    result = client.handle_api_error(mock_error)
    assert result["error"] == "VALIDATION_ERROR"


def test_handle_api_error_403():
    """测试 403 错误处理"""
    mock_error = MagicMock()
    mock_error.response.status_code = 403
    mock_error.response.text = '{"message": "权限拒绝"}'
    mock_error.response.json.return_value = {"message": "权限拒绝"}

    client = JavaApiClient()
    result = client.handle_api_error(mock_error)
    assert result["error"] == "PERMISSION_DENIED"


def test_handle_api_error_404():
    """测试 404 错误处理"""
    mock_error = MagicMock()
    mock_error.response.status_code = 404
    mock_error.response.text = '{"message": "资源不存在"}'
    mock_error.response.json.return_value = {"message": "资源不存在"}

    client = JavaApiClient()
    result = client.handle_api_error(mock_error)
    assert result["error"] == "RESOURCE_NOT_FOUND"


def test_handle_api_error_500():
    """测试 500 错误处理"""
    mock_error = MagicMock()
    mock_error.response.status_code = 500
    mock_error.response.text = '{"message": "内部错误"}'
    mock_error.response.json.return_value = {"message": "内部错误"}

    client = JavaApiClient()
    result = client.handle_api_error(mock_error)
    assert result["error"] == "DEPENDENCY_UNAVAILABLE"
