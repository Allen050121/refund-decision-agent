"""
测试 FastAPI 任务 API
"""
import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.mark.asyncio
async def test_create_task():
    """测试创建任务"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/tasks",
            json={
                "userId": "U1001",
                "ticketContent": "课程打不开，申请退款",
                "orderId": "ORD-001",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "taskId" in data
        assert data["status"] == "CREATED"


@pytest.mark.asyncio
async def test_create_task_without_order_id():
    """测试不带订单 ID 创建任务"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/tasks",
            json={
                "userId": "U1002",
                "ticketContent": "我要退款",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CREATED"


@pytest.mark.asyncio
async def test_get_task_not_found():
    """测试查询不存在的任务"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/tasks/T-NONEXISTENT")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_task_after_create():
    """测试创建后查询任务"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 先创建
        create_resp = await client.post(
            "/tasks",
            json={
                "userId": "U1003",
                "ticketContent": "重复购买了课程",
                "orderId": "ORD-003",
            },
        )
        task_id = create_resp.json()["taskId"]

        # 再查询
        get_resp = await client.get(f"/tasks/{task_id}")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["taskId"] == task_id


@pytest.mark.asyncio
async def test_list_tasks():
    """测试列出任务"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/tasks")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_health_check():
    """测试健康检查"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "OK"


@pytest.mark.asyncio
async def test_readiness_check():
    """测试就绪检查"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data


@pytest.mark.asyncio
async def test_demo_console_page():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/demo")
        assert response.status_code == 200
        assert "售后退款决策 Agent 控制台" in response.text
        assert "/tasks" in response.text
