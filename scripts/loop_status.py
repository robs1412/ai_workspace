#!/usr/local/bin/python3.13
"""Aggregate read-only loop engineering status for recursive/task-mode work."""

from __future__ import annotations

import argparse
import json
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path("/Users/werkstatt/ai_workspace")
ARTIFACT_DIR = ROOT / "project_hub/artifacts/recursive-tools"
DEFAULT_JSON = ARTIFACT_DIR / "loop-status-latest.json"
DEFAULT_REPORT = ARTIFACT_DIR / "loop-status-latest.md"
DEFAULT_BOARD_JSON = ARTIFACT_DIR / "loop-status-board-latest.json"
MONITOR_STATUS_URL = "http://127.0.0.1:17878/api/monitor-status"
SCHEMA_VERSION = 2


def now_local() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def safe_text(value: object, limit: int = 500) -> str:
    return " ".join(str(value or "").split())[:limit]


def read_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def artifact_status(path: Path, generated_at: str = "") -> dict[str, Any]:
    exists = path.exists()
    return {
        "path": str(path),
        "exists": exists,
        "mtime": datetime.fromtimestamp(path.stat().st_mtime).astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
        if exists
        else "",
        "generated_at": generated_at,
    }


def run_json_command(command: list[str], timeout: int = 240) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        return {
            "ok": False,
            "state": "degraded",
            "command": command,
            "returncode": proc.returncode,
            "error": safe_text(proc.stderr or proc.stdout),
        }
    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return {
            "ok": False,
            "state": "degraded",
            "command": command,
            "returncode": proc.returncode,
            "error": f"invalid JSON: {safe_text(exc)}",
        }
    if isinstance(data, dict):
        data.setdefault("ok", True)
        return data
    return {"ok": True, "items": data}


def fetch_json(url: str, timeout: float = 4.0) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = json.loads(response.read())
    except (TimeoutError, socket.timeout, urllib.error.URLError, json.JSONDecodeError) as exc:
        return {"ok": False, "state": "degraded", "url": url, "error": safe_text(exc)}
    return data if isinstance(data, dict) else {"ok": True, "items": data}


def monitor_summary() -> dict[str, Any]:
    payload = fetch_json(MONITOR_STATUS_URL, timeout=12.0)
    rows = payload.get("rows") or payload.get("items") or []
    counts: dict[str, int] = {}
    if isinstance(rows, list):
        for row in rows:
            if not isinstance(row, dict):
                continue
            status = safe_text(row.get("status") or row.get("state") or "unknown", 80)
            counts[status] = counts.get(status, 0) + 1
    return {
        "ok": bool(payload.get("ok", False)),
        "state": "ok" if payload.get("ok", False) else "degraded",
        "url": MONITOR_STATUS_URL,
        "error": payload.get("error") or "",
        "checked_at": now_local(),
        "count": len(rows) if isinstance(rows, list) else 0,
        "by_status": counts,
    }


def git_summary() -> dict[str, Any]:
    plan = run_json_command(
        [
            "/usr/local/bin/python3.13",
            "scripts/git_hygiene_inventory.py",
            "--root",
            "/Users/werkstatt",
            "--plan",
            "--json",
        ],
        timeout=240,
    )
    if not plan.get("ok", True):
        return plan
    return {
        "ok": True,
        "state": "ok",
        "checked_at": now_local(),
        "repo_count": plan.get("repo_count", 0),
        "dirty_repo_count": plan.get("dirty_repo_count", 0),
        "buckets": {
            bucket: len(items) if isinstance(items, list) else 0
            for bucket, items in (plan.get("buckets") or {}).items()
        },
    }


def git_dirty_review_summary() -> dict[str, Any]:
    return run_json_command(
        [
            "/usr/local/bin/python3.13",
            "scripts/git_dirty_repo_reviewer.py",
            "status",
            "--json",
        ],
        timeout=300,
    )


def latest_recursive_artifacts() -> dict[str, Any]:
    daily_path = ARTIFACT_DIR / "recursive-daily-run-latest.json"
    truth_path = ARTIFACT_DIR / "task-flow-truth-drift-latest.json"
    candidates_path = ARTIFACT_DIR / "task-flow-proof-repair-candidates-latest.json"
    packets_path = ARTIFACT_DIR / "task-flow-proof-repair-packets-latest.json"
    daily = read_json(daily_path)
    truth = read_json(truth_path)
    candidates = read_json(candidates_path)
    packets = read_json(packets_path)
    return {
        "daily": {
            "recorded_at": daily.get("recorded_at") or daily.get("generated_at") or "",
            "source": artifact_status(daily_path, daily.get("recorded_at") or daily.get("generated_at") or ""),
            "outcome": daily.get("outcome") or "",
            "recommended_action": daily.get("recommended_action") or "",
            "approval_required": bool(daily.get("approval_required")),
            "proposal_id": daily.get("proposal_id") or "",
            "server_health_status": (daily.get("server_health") or {}).get("status") or "",
        },
        "truth_drift": {
            "recorded_at": truth.get("generated_at") or truth.get("recorded_at") or "",
            "source": artifact_status(truth_path, truth.get("generated_at") or truth.get("recorded_at") or ""),
            "board_ok": truth.get("board_ok"),
            "drift_count": truth.get("drift_count", 0),
            "proof_issue_count": truth.get("proof_issue_count", 0),
            "proof_issue_classes": truth.get("proof_issue_classes") or {},
        },
        "proof_repair_candidates": {
            "generated_at": candidates.get("generated_at") or "",
            "source": artifact_status(candidates_path, candidates.get("generated_at") or ""),
            "candidate_count": candidates.get("candidate_count", 0),
            "mutation_allowed": bool(candidates.get("mutation_allowed")),
            "candidate_keys": [
                safe_text(item.get("dedupe_key"), 120)
                for item in (candidates.get("candidates") or [])[:10]
                if isinstance(item, dict)
            ],
        },
        "proof_repair_packets": {
            "generated_at": packets.get("generated_at") or "",
            "source": artifact_status(packets_path, packets.get("generated_at") or ""),
            "packet_count": packets.get("packet_count", 0),
            "mutation_allowed": bool(packets.get("mutation_allowed")),
            "needs_approval_count": sum(
                1
                for item in (packets.get("packets") or [])
                if isinstance(item, dict)
                and item.get("approval_required")
                and item.get("status") in {"needs_approval", "ready_for_review", ""}
            ),
        },
    }


def packet_review_summary() -> dict[str, Any]:
    return run_json_command(
        [
            "/usr/local/bin/python3.13",
            "scripts/task_flow_proof_repair_packet_reviewer.py",
            "status",
            "--json",
        ],
        timeout=60,
    )


def next_action(status: dict[str, Any]) -> str:
    recursive = status["recursive"]
    packets = recursive["proof_repair_packets"]
    candidates = recursive["proof_repair_candidates"]
    executor = status["proposal_executor"]
    monitor = status["workspaceboard_monitor"]
    reviews = status.get("proof_repair_packet_reviews") or {}
    git_reviews = status.get("git_dirty_reviews") or {}
    pending_review_count = reviews.get("pending_review_count")
    if pending_review_count is None:
        pending_review_count = packets.get("needs_approval_count", 0)
    if not monitor.get("ok"):
        return "repair_or_classify_workspaceboard_monitor_status"
    if executor.get("approved_unexecuted_count", 0):
        return "execute_or_verify_approved_recursive_proposal"
    if pending_review_count:
        return "review_proof_repair_packets_for_approval"
    if candidates.get("candidate_count", 0) and not packets.get("packet_count", 0):
        return "generate_proof_repair_packets"
    if recursive["truth_drift"].get("drift_count", 0):
        return "repair_truth_drift_before_monitor_mode"
    if git_reviews.get("pending_review_count", status["git_hygiene"].get("dirty_repo_count", 0)):
        return "review_dirty_repositories"
    return "monitor_mode"


def build_status() -> dict[str, Any]:
    status = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_local(),
        "mode": "read-only-loop-status",
        "mutation_allowed": False,
        "workspaceboard_monitor": monitor_summary(),
        "proposal_executor": run_json_command(
            ["/usr/local/bin/python3.13", "scripts/recursive_proposal_executor.py", "status", "--json"],
            timeout=60,
        ),
        "git_hygiene": git_summary(),
        "git_dirty_reviews": git_dirty_review_summary(),
        "recursive": latest_recursive_artifacts(),
        "proof_repair_packet_reviews": packet_review_summary(),
    }
    status["next_action"] = next_action(status)
    degraded = []
    for name in (
        "workspaceboard_monitor",
        "proposal_executor",
        "git_hygiene",
        "git_dirty_reviews",
        "proof_repair_packet_reviews",
    ):
        section = status.get(name)
        if isinstance(section, dict) and not section.get("ok", True):
            degraded.append(
                {
                    "section": name,
                    "command": section.get("command", ""),
                    "url": section.get("url", ""),
                    "error": section.get("error", ""),
                }
            )
    status["degraded_sources"] = degraded
    return status


def build_board_status(status: dict[str, Any]) -> dict[str, Any]:
    recursive = status["recursive"]
    packets = recursive["proof_repair_packets"]
    reviews = status.get("proof_repair_packet_reviews") or {}
    monitor = status["workspaceboard_monitor"]
    git_reviews = status.get("git_dirty_reviews") or {}
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": status["generated_at"],
        "mode": status["mode"],
        "mutation_allowed": False,
        "next_action": status["next_action"],
        "workspaceboard_monitor": {
            "ok": monitor.get("ok"),
            "count": monitor.get("count", 0),
            "by_status": monitor.get("by_status", {}),
            "error": monitor.get("error", ""),
        },
        "proof_repair": {
            "packet_count": packets.get("packet_count", 0),
            "needs_approval_count": packets.get("needs_approval_count", 0),
            "pending_review_count": reviews.get("pending_review_count", 0),
        },
        "git_dirty_reviews": {
            "repo_count": git_reviews.get("repo_count", 0),
            "pending_review_count": git_reviews.get("pending_review_count", 0),
            "blocked_review_count": git_reviews.get("blocked_review_count", 0),
        },
        "truth_drift_count": recursive["truth_drift"].get("drift_count", 0),
        "degraded_count": len(status.get("degraded_sources") or []),
    }


def render_markdown(status: dict[str, Any]) -> str:
    monitor = status["workspaceboard_monitor"]
    executor = status["proposal_executor"]
    git = status["git_hygiene"]
    git_reviews = status.get("git_dirty_reviews") or {}
    recursive = status["recursive"]
    candidates = recursive["proof_repair_candidates"]
    packets = recursive["proof_repair_packets"]
    truth = recursive["truth_drift"]
    lines = [
        "# Loop Status",
        "",
        f"- Recorded: {status['generated_at']}",
        f"- Schema version: `{status.get('schema_version', 1)}`",
        "- Mode: `read-only-loop-status`",
        "- Mutation allowed: `False`",
        f"- Next action: `{status['next_action']}`",
        "",
        "## Workspaceboard",
        "",
        f"- ok: `{monitor.get('ok')}`",
        f"- checked_at: `{monitor.get('checked_at', '')}`",
        f"- checks: `{monitor.get('count', 0)}`",
        f"- by_status: `{json.dumps(monitor.get('by_status', {}), sort_keys=True)}`",
        f"- error: `{monitor.get('error') or ''}`",
        "",
        "## Recursive Executor",
        "",
        f"- approved_unexecuted_count: `{executor.get('approved_unexecuted_count', 0)}`",
        f"- blocked_execution_count: `{executor.get('blocked_execution_count', 0)}`",
        "",
        "## Truth And Proof Repair",
        "",
        f"- drift_count: `{truth.get('drift_count', 0)}`",
        f"- proof_issue_count: `{truth.get('proof_issue_count', 0)}`",
        f"- proof_repair_candidate_count: `{candidates.get('candidate_count', 0)}`",
        f"- proof_repair_packet_count: `{packets.get('packet_count', 0)}`",
        f"- proof_repair_needs_approval_count: `{packets.get('needs_approval_count', 0)}`",
        f"- candidates_source_mtime: `{candidates.get('source', {}).get('mtime', '')}`",
        f"- packets_source_mtime: `{packets.get('source', {}).get('mtime', '')}`",
        f"- packet_pending_review_count: `{(status.get('proof_repair_packet_reviews') or {}).get('pending_review_count', 0)}`",
        "",
        "## Git Hygiene",
        "",
        f"- repos_scanned: `{git.get('repo_count', 0)}`",
        f"- dirty_repos: `{git.get('dirty_repo_count', 0)}`",
        f"- dirty_repo_pending_review_count: `{git_reviews.get('pending_review_count', 0)}`",
        f"- dirty_repo_blocked_review_count: `{git_reviews.get('blocked_review_count', 0)}`",
        f"- buckets: `{json.dumps(git.get('buckets', {}), sort_keys=True)}`",
        "",
        "## Degraded Sources",
        "",
        f"- count: `{len(status.get('degraded_sources') or [])}`",
    ]
    for source in status.get("degraded_sources") or []:
        lines.append(
            f"- `{source.get('section')}` command=`{source.get('command')}` url=`{source.get('url')}` error=`{source.get('error')}`"
        )
    lines.extend(
        [
        "## Boundary",
        "",
        "- This status is read-only. It does not send email, mutate Task Flow, update OPS/Portal, commit, push, pull, or clean repositories.",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--board-json", type=Path, default=DEFAULT_BOARD_JSON)
    parser.add_argument("--print-json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    status = build_status()
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.board_json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.write_text(render_markdown(status), encoding="utf-8")
    args.board_json.write_text(json.dumps(build_board_status(status), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.print_json:
        print(json.dumps(status, indent=2, sort_keys=True))
    else:
        print(f"report={args.report}")
        print(f"json={args.json}")
        print(f"next_action={status['next_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
