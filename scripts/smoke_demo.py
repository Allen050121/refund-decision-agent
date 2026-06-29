"""Run deterministic offline demo smoke cases for the refund decision Agent.

The smoke path executes the core Agent nodes with Fake LLM/RAG ports and
case-owned business snapshots. It does not require Java, Redis,
Elasticsearch, or a real model gateway to be running.
"""

from __future__ import annotations

import argparse
import asyncio
import html
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable


ROOT = Path(__file__).resolve().parents[1]
PYTHON_AGENT = ROOT / "python-agent"
DEFAULT_CASES = PYTHON_AGENT / "data" / "demo_cases.json"
DEFAULT_HTML = ROOT / "docs" / "demo-report.html"

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
from app.infrastructure.llm.fake_client import FakeLLMClient  # noqa: E402
from app.infrastructure.retrieval.fake_retriever import FakeRetriever  # noqa: E402


Node = Callable[[AgentState], Awaitable[dict[str, Any]]]


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
    expected = case.get("expected", {})
    failures: list[str] = []

    for key in ("intent", "reason_code"):
        if key in expected:
            actual = enum_value(final_state.get(key))
            if actual != expected[key]:
                failures.append(f"{key}: expected {expected[key]}, got {actual}")

    if "decision_any_of" in expected:
        actual_decision = enum_value(final_state.get("decision"))
        if actual_decision not in expected["decision_any_of"]:
            failures.append(
                f"decision: expected one of {expected['decision_any_of']}, got {actual_decision}"
            )

    if "missing_fields_contains" in expected:
        missing_fields = set(as_list(final_state.get("missing_fields")))
        for field in expected["missing_fields_contains"]:
            if field not in missing_fields:
                failures.append(f"missing_fields: expected to contain {field}")

    if "rule_citation_any_of" in expected:
        citations = {str(item) for item in as_list(final_state.get("rule_citations"))}
        required = set(expected["rule_citation_any_of"])
        if not citations.intersection(required):
            failures.append(
                f"rule_citations: expected any of {sorted(required)}, got {sorted(citations)}"
            )

    return failures


def build_row(case: dict[str, Any], final_state: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    return {
        "case": case["id"],
        "title": case["title"],
        "ticket_content": case.get("ticket_content", ""),
        "order_id": case.get("order_id"),
        "user_id": case.get("user_id"),
        "intent": enum_value(final_state.get("intent")),
        "reason": enum_value(final_state.get("reason_code")),
        "decision": enum_value(final_state.get("decision")),
        "rules": [str(item) for item in as_list(final_state.get("rule_citations"))],
        "missing_fields": as_list(final_state.get("missing_fields")),
        "risk_hints": as_list(final_state.get("risk_hints")),
        "evidence": as_list(final_state.get("evidence")),
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
    }


async def run_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    set_ports(llm=FakeLLMClient(), retrieval=FakeRetriever())
    try:
        rows: list[dict[str, Any]] = []
        for case in cases:
            final_state, failures = await run_case(case)
            rows.append(build_row(case, final_state, failures))
        return rows
    finally:
        set_ports(llm=None, retrieval=None)


def build_report(cases_path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    passed = sum(1 for row in rows if row["result"] == "PASS")
    failed = len(rows) - passed
    decisions: dict[str, int] = {}
    for row in rows:
        decisions[row["decision"]] = decisions.get(row["decision"], 0) + 1
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "cases_path": str(cases_path),
        "total": len(rows),
        "passed": passed,
        "failed": failed,
        "decisions": decisions,
        "rows": rows,
    }


def format_cell(value: Any, width: int) -> str:
    text = "" if value is None else str(value)
    if len(text) > width:
        text = text[: width - 1] + "..."
    return text.ljust(width)


def print_table(cases_path: Path, report: dict[str, Any]) -> None:
    rows = report["rows"]
    print(f"Demo smoke cases: {cases_path}")
    print(
        " | ".join(
            [
                format_cell("Case", 9),
                format_cell("Title", 28),
                format_cell("Intent", 16),
                format_cell("Reason", 24),
                format_cell("Decision", 22),
                format_cell("Result", 6),
            ]
        )
    )
    print("-" * 119)
    for row in rows:
        print(
            " | ".join(
                [
                    format_cell(row["case"], 9),
                    format_cell(row["title"], 28),
                    format_cell(row["intent"], 16),
                    format_cell(row["reason"], 24),
                    format_cell(row["decision"], 22),
                    format_cell(row["result"], 6),
                ]
            )
        )

    failures = [row for row in rows if row["failures"]]
    if failures:
        print("\nFailures:")
        for row in failures:
            for failure in row["failures"]:
                print(f"- {row['case']}: {failure}")
    else:
        print(f"\nAll {len(rows)} demo smoke cases passed.")


def badge(text: str, tone: str) -> str:
    return f'<span class="badge {tone}">{html.escape(text)}</span>'


def list_text(items: list[Any]) -> str:
    if not items:
        return '<span class="muted">-</span>'
    return ", ".join(html.escape(str(item)) for item in items)


def render_html(report: dict[str, Any]) -> str:
    rows_html = []
    for row in report["rows"]:
        tone = "ok" if row["result"] == "PASS" else "bad"
        decision_tone = {
            "REFUND_RECOMMENDED": "ok",
            "REFUND_REJECTED": "bad",
            "WAIT_FOR_APPROVAL": "warn",
            "NEED_MORE_INFORMATION": "info",
        }.get(row["decision"], "info")
        rows_html.append(
            f"""
            <tr>
              <td><strong>{html.escape(row["case"])}</strong><span>{html.escape(row["title"])}</span></td>
              <td>{html.escape(row["intent"])}</td>
              <td>{html.escape(row["reason"])}</td>
              <td>{badge(row["decision"], decision_tone)}</td>
              <td>{list_text(row["rules"])}</td>
              <td>{list_text(row["risk_hints"])}</td>
              <td>{badge(row["result"], tone)}</td>
            </tr>
            """
        )

    case_blocks = []
    for row in report["rows"]:
        case_blocks.append(
            f"""
            <section class="case">
              <header>
                <div>
                  <span class="case-id">{html.escape(row["case"])}</span>
                  <h2>{html.escape(row["title"])}</h2>
                </div>
                {badge(row["result"], "ok" if row["result"] == "PASS" else "bad")}
              </header>
              <p>{html.escape(row["ticket_content"])}</p>
              <dl>
                <div><dt>用户</dt><dd>{html.escape(str(row["user_id"] or "-"))}</dd></div>
                <div><dt>订单</dt><dd>{html.escape(str(row["order_id"] or "-"))}</dd></div>
                <div><dt>意图</dt><dd>{html.escape(row["intent"])}</dd></div>
                <div><dt>原因</dt><dd>{html.escape(row["reason"])}</dd></div>
                <div><dt>决策</dt><dd>{html.escape(row["decision"])}</dd></div>
                <div><dt>规则</dt><dd>{list_text(row["rules"])}</dd></div>
                <div><dt>证据</dt><dd>{list_text(row["evidence"])}</dd></div>
                <div><dt>风险</dt><dd>{list_text(row["risk_hints"])}</dd></div>
              </dl>
            </section>
            """
        )

    decision_items = "".join(
        f"<li><span>{html.escape(decision)}</span><strong>{count}</strong></li>"
        for decision, count in sorted(report["decisions"].items())
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>售后退款决策 Agent Demo 报告</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172026;
      --muted: #60707d;
      --line: #d8e0e6;
      --panel: #f7f9fb;
      --ok: #0f7a4f;
      --ok-bg: #e4f6ed;
      --bad: #b42318;
      --bad-bg: #fde7e5;
      --warn: #996500;
      --warn-bg: #fff3cf;
      --info: #1456a0;
      --info-bg: #e8f1ff;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, "Segoe UI", "Microsoft YaHei", Arial, sans-serif;
      color: var(--ink);
      background: #ffffff;
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px 20px 48px;
    }}
    header.page {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 24px;
      align-items: end;
      border-bottom: 1px solid var(--line);
      padding-bottom: 18px;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      line-height: 1.2;
      letter-spacing: 0;
    }}
    .subtitle {{
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(3, minmax(88px, 1fr));
      gap: 10px;
      min-width: 300px;
    }}
    .metric {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: var(--panel);
    }}
    .metric span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }}
    .metric strong {{
      font-size: 24px;
    }}
    .band {{
      margin-top: 22px;
      border-top: 1px solid var(--line);
      padding-top: 18px;
    }}
    .decision-list {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      padding: 0;
      margin: 12px 0 0;
      list-style: none;
    }}
    .decision-list li {{
      display: flex;
      gap: 12px;
      align-items: center;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px 12px;
      background: #fff;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 16px;
      font-size: 14px;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 12px 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      background: var(--panel);
    }}
    td span {{
      display: block;
      color: var(--muted);
      margin-top: 4px;
      font-size: 12px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      border-radius: 999px;
      padding: 3px 9px;
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
    }}
    .ok {{ color: var(--ok); background: var(--ok-bg); }}
    .bad {{ color: var(--bad); background: var(--bad-bg); }}
    .warn {{ color: var(--warn); background: var(--warn-bg); }}
    .info {{ color: var(--info); background: var(--info-bg); }}
    .muted {{ color: var(--muted); }}
    .case {{
      border-top: 1px solid var(--line);
      padding: 18px 0;
    }}
    .case header {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: start;
    }}
    .case h2 {{
      margin: 4px 0 0;
      font-size: 18px;
      letter-spacing: 0;
    }}
    .case-id {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }}
    .case p {{
      margin: 12px 0;
      line-height: 1.7;
    }}
    dl {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 10px;
      margin: 0;
    }}
    dl div {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 10px;
      min-width: 0;
    }}
    dt {{
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 6px;
    }}
    dd {{
      margin: 0;
      overflow-wrap: anywhere;
    }}
    footer {{
      margin-top: 28px;
      color: var(--muted);
      font-size: 12px;
      border-top: 1px solid var(--line);
      padding-top: 16px;
    }}
    @media (max-width: 820px) {{
      header.page {{
        grid-template-columns: 1fr;
      }}
      .summary {{
        min-width: 0;
      }}
      table {{
        display: block;
        overflow-x: auto;
      }}
      dl {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header class="page">
      <div>
        <h1>售后退款决策 Agent Demo 报告</h1>
        <p class="subtitle">生成时间：{html.escape(report["generated_at"])}；数据源：{html.escape(report["cases_path"])}</p>
      </div>
      <div class="summary">
        <div class="metric"><span>用例</span><strong>{report["total"]}</strong></div>
        <div class="metric"><span>通过</span><strong>{report["passed"]}</strong></div>
        <div class="metric"><span>失败</span><strong>{report["failed"]}</strong></div>
      </div>
    </header>

    <section class="band">
      <h2>决策分布</h2>
      <ul class="decision-list">{decision_items}</ul>
    </section>

    <section class="band">
      <h2>冒烟结果</h2>
      <table>
        <thead>
          <tr>
            <th>Case</th>
            <th>Intent</th>
            <th>Reason</th>
            <th>Decision</th>
            <th>Rules</th>
            <th>Risk</th>
            <th>Result</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows_html)}
        </tbody>
      </table>
    </section>

    <section class="band">
      <h2>用例详情</h2>
      {''.join(case_blocks)}
    </section>

    <footer>
      Offline smoke report generated by scripts/smoke_demo.py. No Java, Redis, Elasticsearch, or real model gateway was required.
    </footer>
  </main>
</body>
</html>
"""


def write_html_report(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(report), encoding="utf-8")


async def main() -> int:
    parser = argparse.ArgumentParser(description="Run deterministic offline demo smoke cases.")
    parser.add_argument("--cases", default=str(DEFAULT_CASES), help="Path to demo_cases.json")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON report")
    parser.add_argument(
        "--html",
        nargs="?",
        const=str(DEFAULT_HTML),
        help="Write a static HTML demo report, optionally to the given path",
    )
    args = parser.parse_args()

    cases_path = Path(args.cases).resolve()
    payload = json.loads(cases_path.read_text(encoding="utf-8"))
    rows = await run_cases(payload.get("cases", []))
    report = build_report(cases_path, rows)

    if args.html:
        html_path = Path(args.html).resolve()
        write_html_report(html_path, report)
        if not args.json:
            print(f"HTML demo report: {html_path}")

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_table(cases_path, report)

    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
