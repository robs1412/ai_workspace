#!/usr/local/bin/python3.13
"""Read-only verifier for Claude Planner recursive proof exports.

This checker only treats the dedicated /proof routes as proof. Broader Planner
task/chain reads are intentionally not accepted as recursive proof because they
may include volatile fields.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://planner.koval.lan"
DEFAULT_TASK_ID = "1725"
FORBIDDEN_FIELDS = {"previous_status", "session_id", "context_summary"}
REQUIRED_STABLE_FIELDS = {"id", "status", "tags"}


def now_local() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--task-id", default=DEFAULT_TASK_ID)
    parser.add_argument("--plan-guid", default="")
    parser.add_argument("--timeout-seconds", type=float, default=8.0)
    parser.add_argument("--json", type=Path, help="Optional output JSON path.")
    parser.add_argument("--report", type=Path, help="Optional Markdown report path.")
    parser.add_argument("--fail-on-not-ready", action="store_true")
    return parser.parse_args()


def clean_base_url(value: str) -> str:
    return str(value or DEFAULT_BASE_URL).rstrip("/")


def proof_url(args: argparse.Namespace) -> str:
    base = clean_base_url(args.base_url)
    if args.plan_guid:
        return f"{base}/api/proof?{urllib.parse.urlencode({'plan_guid': args.plan_guid})}"
    return f"{base}/api/tasks/{urllib.parse.quote(str(args.task_id), safe='')}/proof"


def context_url(args: argparse.Namespace) -> str:
    base = clean_base_url(args.base_url)
    return f"{base}/api/tasks/{urllib.parse.quote(str(args.task_id), safe='')}"


def fetch_json(url: str, timeout: float) -> tuple[dict[str, Any], dict[str, Any]]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            body = response.read(2_000_000)
            status = int(getattr(response, "status", 0) or 0)
            content_type = response.headers.get("content-type", "")
    except urllib.error.HTTPError as error:
        raw = error.read(2000).decode("utf-8", errors="replace")
        return {}, {
            "ok": False,
            "http_status": int(error.code),
            "error": f"HTTP {error.code}",
            "body_excerpt": raw[:1000],
        }
    except TimeoutError:
        return {}, {"ok": False, "http_status": 0, "error": "timeout"}
    except OSError as error:
        return {}, {"ok": False, "http_status": 0, "error": str(error)[:500]}

    try:
        parsed = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        return {}, {
            "ok": False,
            "http_status": status,
            "content_type": content_type,
            "error": f"invalid JSON: {error}",
            "body_excerpt": body[:1000].decode("utf-8", errors="replace"),
        }
    if not isinstance(parsed, dict):
        return {}, {
            "ok": False,
            "http_status": status,
            "content_type": content_type,
            "error": "JSON response is not an object",
        }
    return parsed, {"ok": True, "http_status": status, "content_type": content_type}


def find_forbidden_fields(value: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in FORBIDDEN_FIELDS:
                found.append(path)
            found.extend(find_forbidden_fields(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_forbidden_fields(child, f"{prefix}[{index}]"))
    return found


def get_task_object(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("task", "proof", "data"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return payload


def proof_comment_count(payload: dict[str, Any]) -> int:
    total = 0
    for key in ("proof_comments", "verification_comments", "delivery_comments", "comments"):
        value = payload.get(key)
        if isinstance(value, list):
            total += len([item for item in value if isinstance(item, dict)])
    task = get_task_object(payload)
    if task is not payload:
        total += proof_comment_count(task)
    return total


def validate_proof_payload(payload: dict[str, Any]) -> tuple[str, list[str], dict[str, Any]]:
    issues: list[str] = []
    task = get_task_object(payload)
    forbidden = find_forbidden_fields(payload)
    if forbidden:
        issues.append(f"forbidden volatile fields present: {', '.join(forbidden[:10])}")

    present = {field for field in REQUIRED_STABLE_FIELDS if field in task}
    missing = sorted(REQUIRED_STABLE_FIELDS - present)
    if missing:
        issues.append(f"required stable fields missing: {', '.join(missing)}")

    tags = task.get("tags")
    if "tags" in task and not isinstance(tags, list):
        issues.append("tags must be an array")

    comments = proof_comment_count(payload)
    summary = {
        "task_id": task.get("id") or payload.get("id") or "",
        "status_value": task.get("status") or payload.get("status") or "",
        "tag_count": len(tags) if isinstance(tags, list) else 0,
        "proof_comment_count": comments,
        "has_plan_guid": bool(task.get("plan_guid") or payload.get("plan_guid")),
        "has_worklog_guid": bool(task.get("worklog_guid") or payload.get("worklog_guid")),
    }
    return ("passed" if not issues else "failed"), issues, summary


def write_outputs(args: argparse.Namespace, result: dict[str, Any]) -> None:
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "# Claude Planner Proof Check",
            "",
            f"- checked_at: `{result['checked_at']}`",
            f"- status: `{result['status']}`",
            f"- proof_url: `{result['proof_url']}`",
            f"- context_url: `{result['context_url']}`",
            f"- http_status: `{result.get('http_status', 0)}`",
            f"- reason: {result.get('reason', '')}",
            f"- forbidden_field_count: `{len(result.get('forbidden_fields', []))}`",
            f"- proof_comment_count: `{result.get('proof_summary', {}).get('proof_comment_count', 0)}`",
            "",
            "## Rule",
            "",
            "- Only `/proof` routes are accepted as Planner proof.",
            "- `/api/tasks/{id}` and `/chain` are context-only until `/proof` is live.",
            "- `previous_status`, `session_id`, and `context_summary` are volatile and must not appear in proof payloads.",
        ]
        args.report.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    url = proof_url(args)
    payload, fetch = fetch_json(url, max(1.0, float(args.timeout_seconds)))
    result: dict[str, Any] = {
        "checked_at": now_local(),
        "status": "not-ready",
        "base_url": clean_base_url(args.base_url),
        "task_id": str(args.task_id or ""),
        "plan_guid": str(args.plan_guid or ""),
        "proof_url": url,
        "context_url": context_url(args),
        "http_status": fetch.get("http_status", 0),
        "reason": fetch.get("error", ""),
        "forbidden_fields": [],
        "proof_summary": {},
    }
    if fetch.get("ok"):
        status, issues, summary = validate_proof_payload(payload)
        forbidden = find_forbidden_fields(payload)
        result.update(
            {
                "status": status,
                "reason": "; ".join(issues),
                "forbidden_fields": forbidden,
                "proof_summary": summary,
            }
        )
    write_outputs(args, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    if result["status"] == "passed":
        return 0
    return 2 if args.fail_on_not_ready else 0


if __name__ == "__main__":
    raise SystemExit(main())
