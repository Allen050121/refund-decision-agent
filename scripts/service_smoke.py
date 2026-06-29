"""Smoke test already-running Java and Python services.

This script does not start services. It verifies the runtime surface that is
hard to prove with offline unit tests: health endpoints, seeded Java query
APIs, and deterministic refund eligibility.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


DEFAULT_JAVA_URL = "http://localhost:8080"
DEFAULT_PYTHON_URL = "http://localhost:8000"


@dataclass
class SmokeResult:
    name: str
    ok: bool
    detail: str
    status: int | None = None
    data: dict[str, Any] | None = field(default=None)


def request_json(
    method: str,
    url: str,
    body: dict[str, Any] | None = None,
    timeout: float = 5.0,
) -> tuple[int, dict[str, Any] | list[Any] | str]:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = Request(url, data=data, headers=headers, method=method)
    with urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8")
        if not raw:
            return response.status, {}
        try:
            return response.status, json.loads(raw)
        except json.JSONDecodeError:
            return response.status, raw


def result_from_exception(name: str, exc: Exception) -> SmokeResult:
    if isinstance(exc, HTTPError):
        try:
            body = exc.read().decode("utf-8")
        except Exception:
            body = ""
        return SmokeResult(name=name, ok=False, status=exc.code, detail=f"HTTP {exc.code}: {body[:240]}")
    if isinstance(exc, URLError):
        return SmokeResult(name=name, ok=False, detail=f"connection failed: {exc.reason}")
    return SmokeResult(name=name, ok=False, detail=str(exc))


def expect_result_code(payload: Any, code: int = 200) -> bool:
    return isinstance(payload, dict) and payload.get("code") == code


def get_data(payload: Any) -> dict[str, Any]:
    if isinstance(payload, dict) and isinstance(payload.get("data"), dict):
        return payload["data"]
    return {}


def check_java_health(java_url: str, timeout: float) -> SmokeResult:
    name = "java.health"
    try:
        status, payload = request_json("GET", f"{java_url}/health", timeout=timeout)
        ok = status == 200
        return SmokeResult(name, ok, "OK" if ok else f"HTTP {status}", status, payload if isinstance(payload, dict) else None)
    except Exception as exc:
        return result_from_exception(name, exc)


def check_python_health(python_url: str, timeout: float) -> SmokeResult:
    name = "python.health"
    try:
        status, payload = request_json("GET", f"{python_url}/health", timeout=timeout)
        ok = status == 200 and isinstance(payload, dict) and payload.get("status") == "OK"
        detail = "OK" if ok else f"unexpected payload: {payload}"
        return SmokeResult(name, ok, detail, status, payload if isinstance(payload, dict) else None)
    except Exception as exc:
        return result_from_exception(name, exc)


def check_python_ready(python_url: str, timeout: float) -> SmokeResult:
    name = "python.ready"
    try:
        status, payload = request_json("GET", f"{python_url}/health/ready", timeout=timeout)
        ready = isinstance(payload, dict) and payload.get("status") in {"ready", "degraded"}
        detail = payload.get("status", "unknown") if isinstance(payload, dict) else str(payload)
        return SmokeResult(name, status == 200 and ready, detail, status, payload if isinstance(payload, dict) else None)
    except Exception as exc:
        return result_from_exception(name, exc)


def check_java_order(java_url: str, timeout: float) -> SmokeResult:
    name = "java.order.seed"
    query = urlencode({"requesterUserId": "U1002"})
    url = f"{java_url}/api/orders/O20260622003?{query}"
    try:
        status, payload = request_json("GET", url, timeout=timeout)
        data = get_data(payload)
        ok = status == 200 and expect_result_code(payload) and data.get("orderId") == "O20260622003"
        detail = "seed order O20260622003 loaded" if ok else f"unexpected payload: {payload}"
        return SmokeResult(name, ok, detail, status, data)
    except Exception as exc:
        return result_from_exception(name, exc)


def check_java_learning(java_url: str, timeout: float) -> SmokeResult:
    name = "java.learning.seed"
    query = urlencode({"requesterUserId": "U1002"})
    url = f"{java_url}/api/learning/O20260622003?{query}"
    try:
        status, payload = request_json("GET", url, timeout=timeout)
        data = get_data(payload)
        ok = status == 200 and expect_result_code(payload) and data.get("orderId") == "O20260622003"
        detail = "seed learning progress loaded" if ok else f"unexpected payload: {payload}"
        return SmokeResult(name, ok, detail, status, data)
    except Exception as exc:
        return result_from_exception(name, exc)


def check_java_course(java_url: str, timeout: float) -> SmokeResult:
    name = "java.course.seed"
    url = f"{java_url}/api/courses/C2003/status"
    try:
        status, payload = request_json("GET", url, timeout=timeout)
        data = get_data(payload)
        ok = status == 200 and expect_result_code(payload) and data.get("courseId") == "C2003"
        detail = "seed course C2003 loaded" if ok else f"unexpected payload: {payload}"
        return SmokeResult(name, ok, detail, status, data)
    except Exception as exc:
        return result_from_exception(name, exc)


def check_java_eligibility(java_url: str, timeout: float) -> SmokeResult:
    name = "java.refund.eligibility"
    body = {
        "orderId": "O20260622003",
        "requesterUserId": "U1002",
        "reasonCode": "COURSE_UNAVAILABLE",
    }
    try:
        status, payload = request_json("POST", f"{java_url}/api/refund/check-eligibility", body, timeout)
        data = get_data(payload)
        ok = (
            status == 200
            and expect_result_code(payload)
            and data.get("eligible") is True
            and data.get("decisionCode") == "COURSE_SERVICE_FAILURE"
        )
        detail = "course unavailable eligibility passed" if ok else f"unexpected payload: {payload}"
        return SmokeResult(name, ok, detail, status, data)
    except Exception as exc:
        return result_from_exception(name, exc)


def run_smoke(java_url: str, python_url: str, timeout: float, skip_python: bool) -> list[SmokeResult]:
    results = [
        check_java_health(java_url, timeout),
        check_java_order(java_url, timeout),
        check_java_learning(java_url, timeout),
        check_java_course(java_url, timeout),
        check_java_eligibility(java_url, timeout),
    ]
    if not skip_python:
        results.extend(
            [
                check_python_health(python_url, timeout),
                check_python_ready(python_url, timeout),
            ]
        )
    return results


def print_results(results: list[SmokeResult]) -> None:
    print("Service smoke results")
    print("Check                    | Result | Detail")
    print("-" * 78)
    for item in results:
        marker = "PASS" if item.ok else "FAIL"
        print(f"{item.name.ljust(24)} | {marker.ljust(6)} | {item.detail}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test already-running refund Agent services.")
    parser.add_argument("--java-url", default=DEFAULT_JAVA_URL, help="Java service base URL")
    parser.add_argument("--python-url", default=DEFAULT_PYTHON_URL, help="Python service base URL")
    parser.add_argument("--timeout", type=float, default=5.0, help="Request timeout in seconds")
    parser.add_argument("--skip-python", action="store_true", help="Only check the Java service")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    results = run_smoke(args.java_url.rstrip("/"), args.python_url.rstrip("/"), args.timeout, args.skip_python)
    failed = [item for item in results if not item.ok]

    if args.json:
        print(
            json.dumps(
                {
                    "ok": not failed,
                    "total": len(results),
                    "failed": len(failed),
                    "results": [item.__dict__ for item in results],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_results(results)
        if failed:
            print("\nSome checks failed. Start/restart the services, then rerun this script.")
        else:
            print(f"\nAll {len(results)} service smoke checks passed.")

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
