"""Run a small real-LLM Agent chain smoke test.

This script is intentionally separate from unit tests because it calls the
configured OpenAI-compatible model gateway and may cost money or be rate
limited. It still keeps business facts deterministic by injecting local
fixtures, so failures point to the model/Agent boundary rather than Java or ES.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Awaitable, Callable


ROOT = Path(__file__).resolve().parents[1]
PYTHON_AGENT = ROOT / "python-agent"
sys.path.insert(0, str(PYTHON_AGENT))

from app.agent.nodes import (  # noqa: E402
    check_eligibility,
    classify_and_extract,
    generate_recommendation,
    retrieve_rules,
    risk_gate,
    set_ports,
    validate_required_fields,
)
from app.agent.state import AgentState  # noqa: E402
from app.config import settings  # noqa: E402
from app.infrastructure.llm.client import OpenAILLMClient  # noqa: E402
from app.infrastructure.retrieval.fake_retriever import FakeRetriever  # noqa: E402


Node = Callable[[AgentState], Awaitable[dict[str, Any]]]


CASES: list[dict[str, Any]] = [
    {
        "id": "REAL-LLM-001",
        "title": "真实模型参与课程不可用退款链路",
        "user_id": "U1002",
        "order_id": "O20260622003",
        "ticket_content": "React 前端课程一直打不开，视频服务故障，订单号 O20260622003，想退款",
        "business_fixture": {
            "order_snapshot": {
                "status": "PAID",
                "totalAmount": 17900,
                "maxRefundAmount": 17900,
                "courseId": "C2003",
            },
            "learning_progress": {
                "progressPercentage": 10,
                "exceedsLimit": False,
            },
            "course_status": {
                "status": "UNAVAILABLE",
                "isPromotional": False,
            },
        },
        "expected": {
            "intent": "REFUND_REQUEST",
            "reason_code": "COURSE_UNAVAILABLE",
            "decision": "REFUND_RECOMMENDED",
        },
    },
    {
        "id": "REAL-LLM-002",
        "title": "真实模型泛化时由确定性规则校正",
        "user_id": "U1002",
        "order_id": "O20260622003",
        "ticket_content": "这个课从昨天开始就加载失败，视频一直无法观看，我希望售后处理并退款",
        "business_fixture": {
            "order_snapshot": {
                "status": "PAID",
                "totalAmount": 17900,
                "maxRefundAmount": 17900,
                "courseId": "C2003",
            },
            "learning_progress": {
                "progressPercentage": 10,
                "exceedsLimit": False,
            },
            "course_status": {
                "status": "UNAVAILABLE",
                "isPromotional": False,
            },
        },
        "expected": {
            "intent": "REFUND_REQUEST",
            "reason_code": "COURSE_UNAVAILABLE",
            "decision": "REFUND_RECOMMENDED",
        },
    },
    {
        "id": "REAL-LLM-003",
        "title": "缺少订单号必须要求补充信息",
        "user_id": "U1001",
        "order_id": None,
        "ticket_content": "我买的课程打不开，想退款",
        "expected": {
            "intent": "REFUND_REQUEST",
            "reason_code": "COURSE_UNAVAILABLE",
            "decision": "NEED_MORE_INFORMATION",
            "missing_fields_contains": ["order_id"],
        },
    },
    {
        "id": "REAL-LLM-004",
        "title": "非退款咨询不得进入退款建议",
        "user_id": "U1001",
        "order_id": None,
        "ticket_content": "我想咨询一下 Java 课程大纲和上课时间",
        "expected": {
            "intent": "OTHER",
            "decision": "NEED_MORE_INFORMATION",
        },
    },
]


def enum_value(value: Any) -> Any:
    return getattr(value, "value", value)


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def merge_state(state: AgentState, update: dict[str, Any]) -> AgentState:
    payload = state.model_dump()
    payload.update(update)
    return AgentState(**payload)


async def apply_node(state: AgentState, node: Node) -> AgentState:
    return merge_state(state, await node(state))


def inject_fixture(state: AgentState, case: dict[str, Any]) -> AgentState:
    fixture = case.get("business_fixture", {})
    if not fixture:
        return state
    return merge_state(
        state,
        {
            "order_snapshot": fixture.get("order_snapshot"),
            "learning_progress": fixture.get("learning_progress"),
            "course_status": fixture.get("course_status"),
        },
    )


async def run_case(case: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    state = AgentState(
        task_id=case["id"],
        user_id=case.get("user_id"),
        order_id=case.get("order_id"),
        ticket_content=case.get("ticket_content", ""),
    )

    state = await apply_node(state, classify_and_extract)
    state = await apply_node(state, validate_required_fields)
    state = inject_fixture(state, case)
    state = await apply_node(state, retrieve_rules)
    state = await apply_node(state, check_eligibility)
    state = await apply_node(state, generate_recommendation)
    state = await apply_node(state, risk_gate)

    final_state = state.model_dump()
    return final_state, check_case(case, final_state)


def check_case(case: dict[str, Any], final_state: dict[str, Any]) -> list[str]:
    expected = case["expected"]
    failures: list[str] = []

    for key in ("intent", "reason_code", "decision"):
        if key in expected:
            actual = enum_value(final_state.get(key))
            if actual != expected[key]:
                failures.append(f"{key}: expected {expected[key]}, got {actual}")

    for field in expected.get("missing_fields_contains", []):
        if field not in set(as_list(final_state.get("missing_fields"))):
            failures.append(f"missing_fields: expected to contain {field}")

    return failures


def row_from(case: dict[str, Any], final_state: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    return {
        "case": case["id"],
        "title": case["title"],
        "intent": enum_value(final_state.get("intent")),
        "reason_code": enum_value(final_state.get("reason_code")),
        "decision": enum_value(final_state.get("decision")),
        "rules": as_list(final_state.get("rule_citations")),
        "risk_hints": as_list(final_state.get("risk_hints")),
        "model_calls": final_state.get("budget", {}).get("used_model_calls", 0),
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


async def run_smoke(timeout: float) -> list[dict[str, Any]]:
    if not settings.OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is not configured in python-agent/.env or environment")

    llm = OpenAILLMClient(timeout=timeout)
    set_ports(llm=llm, retrieval=FakeRetriever())
    try:
        rows: list[dict[str, Any]] = []
        for case in CASES:
            final_state, failures = await run_case(case)
            rows.append(row_from(case, final_state, failures))
        return rows
    finally:
        set_ports(llm=None, retrieval=None)


def print_table(rows: list[dict[str, Any]]) -> None:
    print(f"Real LLM Agent smoke: model={settings.LLM_MODEL} base_url={settings.LLM_BASE_URL}")
    print("Case         | Intent           | Reason                   | Decision               | Calls | Result")
    print("-" * 104)
    for row in rows:
        print(
            f"{row['case'].ljust(12)} | "
            f"{str(row['intent']).ljust(16)} | "
            f"{str(row['reason_code']).ljust(24)} | "
            f"{str(row['decision']).ljust(22)} | "
            f"{str(row['model_calls']).ljust(5)} | "
            f"{row['result']}"
        )

    failed = [row for row in rows if row["failures"]]
    if failed:
        print("\nFailures:")
        for row in failed:
            for failure in row["failures"]:
                print(f"- {row['case']}: {failure}")
    else:
        print(f"\nAll {len(rows)} real LLM Agent smoke cases passed.")


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run real LLM Agent chain smoke checks.")
    parser.add_argument("--timeout", type=float, default=30.0, help="LLM request timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    rows = await run_smoke(timeout=args.timeout)
    failed = [row for row in rows if row["failures"]]

    if args.json:
        print(
            json.dumps(
                {
                    "ok": not failed,
                    "model": settings.LLM_MODEL,
                    "base_url": settings.LLM_BASE_URL,
                    "total": len(rows),
                    "failed": len(failed),
                    "rows": rows,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_table(rows)

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
