"""
手动测试脚本 - 模拟 HTTP 请求测试 API 接口
直接调用 FastAPI 应用，无需启动独立服务
"""
import asyncio
import json
import time
from datetime import datetime

# 设置工作目录
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ============================================================
# 测试用例
# ============================================================

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_result(name, passed, detail=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"{status} | {name}")
    if detail:
        print(f"   {detail}")

def wait_for_task(task_id, timeout=15, interval=1):
    """等待任务完成"""
    start = time.time()
    while time.time() - start < timeout:
        r = client.get(f"/tasks/{task_id}")
        data = r.json()
        if data.get("status") in ("COMPLETED", "FAILED"):
            return data
        time.sleep(interval)
    return client.get(f"/tasks/{task_id}").json()

# ============================================================
# 1. 健康检查
# ============================================================
print_section("测试 1: 健康检查")

r = client.get("/health")
print_result(
    "基础健康检查",
    r.status_code == 200 and r.json().get("status") == "OK",
    f"status={r.status_code}, body={r.json()}"
)

r = client.get("/health/ready")
data = r.json()
print_result(
    "就绪检查",
    r.status_code == 200 and "checks" in data,
    f"status={data.get('status')}, checks={list(data.get('checks', {}).keys())}"
)

# ============================================================
# 2. 创建任务 - 课程不可用（正常流程）
# ============================================================
print_section("测试 2: 课程不可用 - 应建议退款")

r = client.post("/tasks", json={
    "userId": "U1001",
    "ticketContent": "课程打不开，无法观看，申请退款",
    "orderId": "ORD-001"
})
create_data = r.json()
print_result(
    "创建任务",
    r.status_code == 200 and create_data.get("status") == "CREATED",
    f"taskId={create_data.get('taskId')}"
)

task_id = create_data.get("taskId")
result_data = wait_for_task(task_id)
decision = result_data.get("decision")
reason_code = result_data.get("result", {}).get("reason_code") if result_data.get("result") else None

print_result(
    "查询结果",
    decision == "REFUND_RECOMMENDED" and reason_code == "COURSE_UNAVAILABLE",
    f"decision={decision}, reason_code={reason_code}, status={result_data.get('status')}"
)

# ============================================================
# 3. 创建任务 - 超期退款（拒绝分支）
# ============================================================
print_section("测试 3: 超期退款 - 应拒绝")

r = client.post("/tasks", json={
    "userId": "U1002",
    "ticketContent": "超过30天了，想退款",
    "orderId": "ORD-002"
})
task_id = r.json().get("taskId")
result_data = wait_for_task(task_id)
decision = result_data.get("decision")
reason_code = result_data.get("result", {}).get("reason_code") if result_data.get("result") else None

print_result(
    "超期退款决策",
    decision == "REFUND_REJECTED" and reason_code == "EXPIRED_REFUND_WINDOW",
    f"decision={decision}, reason_code={reason_code}"
)

# ============================================================
# 4. 创建任务 - 无理由退款（审批分支）
# ============================================================
print_section("测试 4: 无理由退款 - 需人工审批")

r = client.post("/tasks", json={
    "userId": "U1003",
    "ticketContent": "不想学了，退款",
    "orderId": "ORD-003"
})
task_id = r.json().get("taskId")
result_data = wait_for_task(task_id)
decision = result_data.get("decision")
reason_code = result_data.get("result", {}).get("reason_code") if result_data.get("result") else None

print_result(
    "无理由退款决策",
    decision == "WAIT_FOR_APPROVAL" and reason_code == "NO_REASON",
    f"decision={decision}, reason_code={reason_code}"
)

# ============================================================
# 5. 创建任务 - 重复购买
# ============================================================
print_section("测试 5: 重复购买 - 应建议退款")

r = client.post("/tasks", json={
    "userId": "U1004",
    "ticketContent": "我不小心买重了课程，申请退款",
    "orderId": "ORD-004"
})
task_id = r.json().get("taskId")
result_data = wait_for_task(task_id)
decision = result_data.get("decision")
reason_code = result_data.get("result", {}).get("reason_code") if result_data.get("result") else None

print_result(
    "重复购买决策",
    decision == "REFUND_RECOMMENDED" and reason_code == "DUPLICATE_PURCHASE",
    f"decision={decision}, reason_code={reason_code}"
)

# ============================================================
# 6. 边界测试 - 缺少必填字段
# ============================================================
print_section("测试 6: 边界测试 - 缺少必填字段")

r = client.post("/tasks", json={
    "userId": "U1005",
    "ticketContent": "我要退款"
})
task_id = r.json().get("taskId")
result_data = wait_for_task(task_id)
errors = result_data.get("result", {}).get("errors", []) if result_data.get("result") else []
has_missing = any("缺少" in str(e) for e in errors)

print_result(
    "缺少 order_id 检测",
    has_missing,
    f"errors={errors}"
)

# ============================================================
# 7. 边界测试 - 空工单内容
# ============================================================
print_section("测试 7: 边界测试 - 空工单内容")

r = client.post("/tasks", json={
    "userId": "U1006",
    "ticketContent": "",
    "orderId": "ORD-006"
})
task_id = r.json().get("taskId")
result_data = wait_for_task(task_id)
status = result_data.get("status")

print_result(
    "空工单不崩溃",
    status in ("COMPLETED", "FAILED"),
    f"status={status}"
)

# ============================================================
# 8. 边界测试 - 无退款关键词的课程问题
# ============================================================
print_section("测试 8: 边界测试 - 无退款关键词")

r = client.post("/tasks", json={
    "userId": "U1007",
    "ticketContent": "课程打不开，无法观看",
    "orderId": "ORD-007"
})
task_id = r.json().get("taskId")
result_data = wait_for_task(task_id)
decision = result_data.get("decision")
reason_code = result_data.get("result", {}).get("reason_code") if result_data.get("result") else None

print_result(
    "无退款关键词但识别为退款",
    decision == "REFUND_RECOMMENDED" and reason_code == "COURSE_UNAVAILABLE",
    f"decision={decision}, reason_code={reason_code}"
)

# ============================================================
# 9. 边界测试 - 查询不存在的任务
# ============================================================
print_section("测试 9: 边界测试 - 不存在的任务")

r = client.get("/tasks/T-not-exist")
print_result(
    "404 错误处理",
    r.status_code == 404,
    f"status={r.status_code}"
)

# ============================================================
# 10. 列表测试
# ============================================================
print_section("测试 10: 任务列表")

r = client.get("/tasks")
data = r.json()
print_result(
    "任务列表",
    r.status_code == 200 and isinstance(data, list) and len(data) > 0,
    f"count={len(data)}"
)

# ============================================================
# 总结
# ============================================================
print_section("测试完成")
print("所有接口测试已执行完毕")
