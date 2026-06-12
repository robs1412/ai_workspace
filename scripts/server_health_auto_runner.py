#!/usr/local/bin/python3.13
"""Metadata-only server health runner with bounded memory/process readback."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path("/Users/werkstatt/ai_workspace")
DEFAULT_URL = "http://127.0.0.1:17878/api/server-health"
DEFAULT_JSON = ROOT / "tmp/ai-health-manager/server-health-auto-run-latest.json"
DEFAULT_REPORT = ROOT / "tmp/ai-health-manager/server-health-auto-run-latest.md"
DEFAULT_LOG = ROOT / "tmp/ai-health-manager/server-health-auto-runs.jsonl"


def fetch_json(url: str, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = json.loads(response.read().decode("utf-8", errors="replace"))
    return payload if isinstance(payload, dict) else {}


def run_ps() -> list[dict[str, Any]]:
    proc = subprocess.run(
        ["/bin/ps", "-axo", "pid,ppid,rss,%mem,command"],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if proc.returncode != 0:
        return []
    rows: list[dict[str, Any]] = []
    for line in proc.stdout.splitlines()[1:]:
        parts = line.strip().split(None, 4)
        if len(parts) < 5:
            continue
        pid, ppid, rss, percent, command = parts
        try:
            rss_kb = int(rss)
            percent_value = float(percent)
        except ValueError:
            continue
        rows.append(
            {
                "pid": int(pid),
                "ppid": int(ppid),
                "rss_mb": round(rss_kb / 1024, 1),
                "mem_percent": percent_value,
                "label": safe_process_label(command),
            }
        )
    rows.sort(key=lambda item: float(item["rss_mb"]), reverse=True)
    return rows


def safe_process_label(command: str) -> str:
    lowered = command.lower()
    if "codex app-server" in lowered:
        return "codex app-server"
    if "/codex" in lowered or " codex " in lowered:
        return "codex session"
    if "frank_auto_runner.py" in lowered:
        return "frank auto runner"
    if "ai_health_check.py" in lowered:
        return "ai health manager"
    if "workspaceboard" in lowered and "server/index.js" in lowered:
        return "workspaceboard server"
    if "bdldaemon" in lowered:
        return "bitdefender daemon"
    if "python" in lowered:
        return "python process"
    if "node" in lowered:
        return "node process"
    return command.split()[0].split("/")[-1][:80] or "process"


def process_categories(processes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    categories: dict[str, dict[str, Any]] = {}
    for item in processes:
        label = str(item.get("label") or "process")
        category = label
        if label in {"codex session", "codex app-server"}:
            category = "codex"
        elif label in {"python process", "ai health manager", "frank auto runner"}:
            category = "python workers"
        elif label in {"node process", "workspaceboard server"}:
            category = "node/workspaceboard"
        bucket = categories.setdefault(category, {"category": category, "count": 0, "rss_mb": 0.0})
        bucket["count"] += 1
        bucket["rss_mb"] += float(item.get("rss_mb") or 0)
    result = [
        {"category": value["category"], "count": value["count"], "rss_mb": round(value["rss_mb"], 1)}
        for value in categories.values()
    ]
    result.sort(key=lambda item: float(item["rss_mb"]), reverse=True)
    return result


def classify(payload: dict[str, Any], processes: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, Any]:
    memory = payload.get("memory") if isinstance(payload.get("memory"), dict) else {}
    repositories = payload.get("repositories") if isinstance(payload.get("repositories"), dict) else {}
    disk = payload.get("disk") if isinstance(payload.get("disk"), dict) else {}
    used_percent = int(memory.get("used_percent") or 0)
    dirty_repos = int(repositories.get("dirty") or 0)
    disk_used = int(disk.get("used_percent") or 0)
    high_processes = [item for item in processes if float(item.get("rss_mb") or 0) >= args.process_rss_warning_mb]
    categories = {str(item["category"]): item for item in process_categories(processes)}
    codex_category = categories.get("codex", {})
    codex_rss = float(codex_category.get("rss_mb") or 0)
    codex_count = int(codex_category.get("count") or 0)
    issues: list[dict[str, Any]] = []
    status = "passed"

    if used_percent >= args.memory_critical_percent:
        status = "critical"
        issues.append({"id": "memory-critical", "reason": f"memory used {used_percent}% >= {args.memory_critical_percent}%"})
    elif used_percent >= args.memory_warning_percent:
        status = "attention"
        issues.append({"id": "memory-attention", "reason": f"memory used {used_percent}% >= {args.memory_warning_percent}%"})

    if disk_used >= args.disk_warning_percent:
        status = "critical" if disk_used >= 95 else max_status(status, "attention")
        issues.append({"id": "disk-attention", "reason": f"disk used {disk_used}% >= {args.disk_warning_percent}%"})

    if high_processes:
        status = max_status(status, "attention")
        labels = ", ".join(f"{item['label']} {item['rss_mb']} MB" for item in high_processes[:5])
        issues.append({"id": "large-processes", "reason": f"large resident processes: {labels}"})

    if codex_rss >= args.codex_total_rss_warning_mb:
        status = max_status(status, "attention")
        issues.append({"id": "codex-memory-aggregate", "reason": f"Codex aggregate RSS {codex_rss:.1f} MB >= {args.codex_total_rss_warning_mb:.1f} MB"})

    if codex_count >= args.codex_process_count_warning:
        status = max_status(status, "attention")
        issues.append({"id": "codex-process-count", "reason": f"Codex process count {codex_count} >= {args.codex_process_count_warning}"})

    if dirty_repos > args.dirty_repo_warning_count:
        status = max_status(status, "attention")
        issues.append({"id": "dirty-repositories", "reason": f"dirty repos {dirty_repos} > {args.dirty_repo_warning_count}"})

    return {
        "status": status,
        "issues": issues,
        "recommended_action": recommended_action(status, issues),
    }


def max_status(left: str, right: str) -> str:
    order = {"passed": 0, "attention": 1, "critical": 2}
    return right if order.get(right, 0) > order.get(left, 0) else left


def recommended_action(status: str, issues: list[dict[str, Any]]) -> str:
    if status == "passed":
        return "record-only; no auto action needed"
    issue_ids = {str(issue.get("id")) for issue in issues}
    if "memory-critical" in issue_ids:
        return "stop worker fan-out; reconcile stale sessions before starting new workers; inspect top resident processes"
    if "codex-memory-aggregate" in issue_ids or "codex-process-count" in issue_ids:
        return "pause new Codex worker fan-out; close stale sessions; reuse existing workers until aggregate RSS drops"
    if "large-processes" in issue_ids:
        return "reuse existing Codex sessions and close proof-backed stale wrappers before launching more workers"
    if "dirty-repositories" in issue_ids:
        return "route repo hygiene through Code/Git Manager for approval-gated commit/push closeout; preserve untracked code and do not auto-commit without preflight"
    return "record attention state and route one bounded health follow-up"


def build_report(record: dict[str, Any]) -> str:
    server = record.get("server_health") if isinstance(record.get("server_health"), dict) else {}
    classification = record.get("classification") if isinstance(record.get("classification"), dict) else {}
    memory = server.get("memory") if isinstance(server.get("memory"), dict) else {}
    disk = server.get("disk") if isinstance(server.get("disk"), dict) else {}
    repositories = server.get("repositories") if isinstance(server.get("repositories"), dict) else {}
    lines = [
        "# Server Health Auto Run",
        "",
        f"- Recorded: {record.get('recorded_at')}",
        f"- Status: `{classification.get('status', 'unknown')}`",
        f"- Recommended action: {classification.get('recommended_action', '')}",
        "",
        "## Snapshot",
        "",
        f"- Memory used: `{memory.get('used_percent', '')}%`",
        f"- Disk used: `{disk.get('used_percent', '')}%`",
        f"- Dirty repos: `{repositories.get('dirty', '')}`",
        "",
        "## Top Resident Processes",
        "",
    ]
    for item in record.get("top_processes", [])[:10]:
        lines.append(f"- `{item.get('label')}` pid `{item.get('pid')}` rss `{item.get('rss_mb')} MB` mem `{item.get('mem_percent')}%`")
    lines.extend(["", "## Process Categories", ""])
    for item in record.get("process_categories", [])[:10]:
        lines.append(f"- `{item.get('category')}` rss `{item.get('rss_mb')} MB` across `{item.get('count')}` processes")
    lines.extend(["", "## Issues", ""])
    issues = classification.get("issues") or []
    if not issues:
        lines.append("- None.")
    else:
        for issue in issues:
            lines.append(f"- `{issue.get('id')}`: {issue.get('reason')}")
    return "\n".join(lines) + "\n"


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--log", type=Path, default=DEFAULT_LOG)
    parser.add_argument("--timeout-seconds", type=int, default=8)
    parser.add_argument("--top-process-limit", type=int, default=12)
    parser.add_argument("--memory-warning-percent", type=int, default=75)
    parser.add_argument("--memory-critical-percent", type=int, default=85)
    parser.add_argument("--disk-warning-percent", type=int, default=85)
    parser.add_argument("--process-rss-warning-mb", type=float, default=1024.0)
    parser.add_argument("--codex-total-rss-warning-mb", type=float, default=4096.0)
    parser.add_argument("--codex-process-count-warning", type=int, default=12)
    parser.add_argument("--dirty-repo-warning-count", type=int, default=4)
    parser.add_argument("--print-json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    server_health = fetch_json(args.url, args.timeout_seconds)
    processes = run_ps()
    classification = classify(server_health, processes, args)
    categories = process_categories(processes)
    record = {
        "recorded_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "epoch": int(time.time()),
        "server_health_url": args.url,
        "classification": classification,
        "server_health": {
            "ok": bool(server_health.get("ok")),
            "generated_at": server_health.get("generated_at", ""),
            "host": server_health.get("host", ""),
            "uptime_human": server_health.get("uptime_human", ""),
            "load_average": server_health.get("load_average", {}),
            "memory": server_health.get("memory", {}),
            "disk": server_health.get("disk", {}),
            "repositories": {
                "dirty": (server_health.get("repositories") or {}).get("dirty", 0),
                "needs_action": (server_health.get("repositories") or {}).get("needs_action", 0),
                "total": (server_health.get("repositories") or {}).get("total", 0),
            },
        },
        "top_processes": processes[: max(1, args.top_process_limit)],
        "process_categories": categories,
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.write_text(build_report(record), encoding="utf-8")
    append_jsonl(args.log, record)
    if args.print_json:
        print(json.dumps(record, indent=2, sort_keys=True))
    else:
        print(f"report={args.report}")
        print(f"json={args.json}")
        print(f"status={classification.get('status')}")
    return 0 if classification.get("status") != "critical" else 2


if __name__ == "__main__":
    raise SystemExit(main())
