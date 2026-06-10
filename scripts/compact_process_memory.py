#!/usr/local/bin/python3.13
"""Compact memory diagnostics for Codex/Workspaceboard workers.

This intentionally avoids printing full process arguments because Codex prompts
and task bodies can be embedded in command lines.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict


def classify(command: str) -> str:
    lower = command.lower()
    if "codex app-server" in lower:
        return "codex-app-server"
    if "codex" in lower:
        return "codex-worker"
    if "workspaceboard" in lower or "/workspaceboard" in lower:
        return "workspaceboard"
    if "frank_auto_runner" in lower:
        return "frank-auto-runner"
    if "avignon_inbox_cycle" in lower:
        return "avignon-inbox-cycle"
    if "nationaloutreach_mail_cycle" in lower:
        return "nationaloutreach-mail-cycle"
    if "ai_health_check" in lower:
        return "ai-health-check"
    if "node" in lower:
        return "node-other"
    if "python" in lower:
        return "python-other"
    if "php" in lower:
        return "php"
    return "other"


def parse_ps() -> list[dict]:
    result = subprocess.run(
        ["ps", "-axo", "pid=,ppid=,rss=,etime=,comm="],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = []
    for line in result.stdout.splitlines():
        parts = line.strip().split(None, 4)
        if len(parts) < 5:
            continue
        pid, ppid, rss, etime, command = parts
        try:
            rss_kb = int(rss)
        except ValueError:
            continue
        rows.append(
            {
                "pid": int(pid),
                "ppid": int(ppid),
                "rss_kb": rss_kb,
                "rss_mb": round(rss_kb / 1024, 1),
                "etime": etime,
                "command": command,
                "category": classify(command),
            }
        )
    return rows


def summarize(rows: list[dict], limit: int) -> dict:
    groups: dict[str, dict] = defaultdict(lambda: {"count": 0, "rss_kb": 0})
    for row in rows:
        group = groups[row["category"]]
        group["count"] += 1
        group["rss_kb"] += row["rss_kb"]
    categories = [
        {
            "category": category,
            "count": group["count"],
            "rss_mb": round(group["rss_kb"] / 1024, 1),
        }
        for category, group in groups.items()
    ]
    categories.sort(key=lambda item: item["rss_mb"], reverse=True)
    top = sorted(rows, key=lambda item: item["rss_kb"], reverse=True)[:limit]
    return {
        "ok": True,
        "process_count": len(rows),
        "total_rss_mb": round(sum(row["rss_kb"] for row in rows) / 1024, 1),
        "categories": categories,
        "top_processes": [
            {
                "pid": row["pid"],
                "ppid": row["ppid"],
                "rss_mb": row["rss_mb"],
                "etime": row["etime"],
                "category": row["category"],
                "command": row["command"],
            }
            for row in top
        ],
        "note": "Full command arguments intentionally omitted to avoid prompt/token leakage.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=15)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    payload = summarize(parse_ps(), max(1, min(args.limit, 50)))
    if args.json:
        print(json.dumps(payload, sort_keys=True))
        return 0
    print(f"Total RSS: {payload['total_rss_mb']} MB across {payload['process_count']} processes")
    print("Categories:")
    for item in payload["categories"]:
        print(f"- {item['category']}: {item['rss_mb']} MB across {item['count']} processes")
    print("Top processes:")
    for row in payload["top_processes"]:
        print(f"- pid={row['pid']} rss={row['rss_mb']}MB age={row['etime']} category={row['category']} command={row['command']}")
    print(payload["note"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
