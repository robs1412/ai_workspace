#!/usr/local/bin/python3.13
"""Build a narrow context packet for recursive loop task-mode startup.

The packet is read-only. It summarizes current loop state, source artifacts,
approval gates, recent proof, and the next safe action without loading broad
handoffs or transcripts.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path("/Users/werkstatt/ai_workspace")
ARTIFACT_DIR = ROOT / "project_hub/artifacts/recursive-tools"
DEFAULT_STATUS_JSON = ARTIFACT_DIR / "loop-status-latest.json"
DEFAULT_PACKET_JSON = ARTIFACT_DIR / "recursive-loop-context-latest.json"
DEFAULT_PACKET_MD = ARTIFACT_DIR / "recursive-loop-context-latest.md"
SCHEMA_VERSION = 1


def now_local() -> datetime:
    return datetime.now().astimezone()


def now_text() -> str:
    return now_local().strftime("%Y-%m-%d %H:%M:%S %Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def safe_text(value: object, limit: int = 500) -> str:
    return " ".join(str(value or "").split())[:limit]


def artifact_meta(path: Path, max_age_hours: float) -> dict[str, Any]:
    exists = path.exists()
    mtime = datetime.fromtimestamp(path.stat().st_mtime).astimezone() if exists else None
    stale_after = now_local() - timedelta(hours=max_age_hours)
    return {
        "path": str(path),
        "exists": exists,
        "mtime": mtime.strftime("%Y-%m-%d %H:%M:%S %Z") if mtime else "",
        "stale": bool((not exists) or (mtime and mtime < stale_after)),
        "max_age_hours": max_age_hours,
    }


def refresh_loop_status() -> dict[str, Any]:
    proc = subprocess.run(
        ["/usr/local/bin/python3.13", "scripts/loop_status.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=300,
    )
    if proc.returncode != 0:
        return {
            "ok": False,
            "command": ["/usr/local/bin/python3.13", "scripts/loop_status.py"],
            "returncode": proc.returncode,
            "error": safe_text(proc.stderr or proc.stdout),
        }
    return {"ok": True, "command": ["/usr/local/bin/python3.13", "scripts/loop_status.py"]}


def approval_gates(status: dict[str, Any]) -> dict[str, Any]:
    recursive = status.get("recursive") if isinstance(status.get("recursive"), dict) else {}
    packets = recursive.get("proof_repair_packets") if isinstance(recursive.get("proof_repair_packets"), dict) else {}
    return {
        "external_send_allowed": False,
        "production_mutation_allowed": False,
        "approval_required_for_packet_execution": bool(packets.get("needs_approval_count", 0)),
        "approved_packet_count": sum(
            1
            for packet in (status.get("proof_repair_packet_reviews") or {}).get("packets", [])
            if isinstance(packet, dict) and packet.get("status") == "approved"
        ),
        "boundary": "No external sends, Task Flow mutations, OPS/Portal mutations, deploys, commits, pushes, pulls, or cleanup without explicit approval.",
    }


def source_artifacts(status_path: Path, status: dict[str, Any], max_age_hours: float) -> list[dict[str, Any]]:
    recursive = status.get("recursive") if isinstance(status.get("recursive"), dict) else {}
    candidates = recursive.get("proof_repair_candidates") if isinstance(recursive.get("proof_repair_candidates"), dict) else {}
    packets = recursive.get("proof_repair_packets") if isinstance(recursive.get("proof_repair_packets"), dict) else {}
    sources = [
        artifact_meta(status_path, max_age_hours),
        artifact_meta(Path((candidates.get("source") or {}).get("path") or ARTIFACT_DIR / "task-flow-proof-repair-candidates-latest.json"), max_age_hours),
        artifact_meta(Path((packets.get("source") or {}).get("path") or ARTIFACT_DIR / "task-flow-proof-repair-packets-latest.json"), max_age_hours),
    ]
    return sources


def build_packet(status_path: Path, max_age_hours: float) -> dict[str, Any]:
    status = read_json(status_path)
    recursive = status.get("recursive") if isinstance(status.get("recursive"), dict) else {}
    truth = recursive.get("truth_drift") if isinstance(recursive.get("truth_drift"), dict) else {}
    packets = recursive.get("proof_repair_packets") if isinstance(recursive.get("proof_repair_packets"), dict) else {}
    reviews = status.get("proof_repair_packet_reviews") if isinstance(status.get("proof_repair_packet_reviews"), dict) else {}
    monitor = status.get("workspaceboard_monitor") if isinstance(status.get("workspaceboard_monitor"), dict) else {}
    git = status.get("git_hygiene") if isinstance(status.get("git_hygiene"), dict) else {}
    sources = source_artifacts(status_path, status, max_age_hours)
    stale_sources = [source for source in sources if source.get("stale")]
    next_action = status.get("next_action") or "refresh_loop_status"
    if stale_sources:
        next_safe_action = "refresh_loop_status_before_execution"
    elif status.get("degraded_sources"):
        next_safe_action = "classify_degraded_sources_before_execution"
    else:
        next_safe_action = next_action
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_text(),
        "mode": "read-only-recursive-loop-context",
        "mutation_allowed": False,
        "workspace": str(ROOT),
        "startup_files": [
            str(ROOT / "AGENTS.md"),
            str(ROOT / "docs/task-mode-startup.md"),
            str(DEFAULT_PACKET_JSON),
        ],
        "current_state": {
            "loop_status_generated_at": status.get("generated_at", ""),
            "workspaceboard_monitor_ok": bool(monitor.get("ok")),
            "workspaceboard_monitor_count": monitor.get("count", 0),
            "truth_drift_count": truth.get("drift_count", 0),
            "proof_issue_count": truth.get("proof_issue_count", 0),
            "proof_repair_packet_count": packets.get("packet_count", 0),
            "packet_pending_review_count": reviews.get("pending_review_count", 0),
            "dirty_repo_count": git.get("dirty_repo_count", 0),
            "next_action": next_action,
        },
        "source_artifacts": sources,
        "stale_source_count": len(stale_sources),
        "degraded_sources": status.get("degraded_sources") or [],
        "approval_gates": approval_gates(status),
        "recent_proof": [
            "loop-status-latest.json readback",
            "proof-repair packet review status readback",
            "Workspaceboard monitor summary readback",
        ],
        "next_safe_action": next_safe_action,
        "stop_condition": "If source artifacts are stale, missing, or contradicted by live readback, refresh/read live state before acting.",
    }


def render_markdown(packet: dict[str, Any]) -> str:
    state = packet["current_state"]
    gates = packet["approval_gates"]
    lines = [
        "# Recursive Loop Context Packet",
        "",
        f"- Recorded: {packet['generated_at']}",
        f"- Schema version: `{packet['schema_version']}`",
        "- Mode: `read-only-recursive-loop-context`",
        "- Mutation allowed: `False`",
        f"- Next safe action: `{packet['next_safe_action']}`",
        "",
        "## Startup",
        "",
    ]
    lines.extend(f"- `{path}`" for path in packet["startup_files"])
    lines.extend(
        [
            "",
            "## Current State",
            "",
            f"- loop_status_generated_at: `{state['loop_status_generated_at']}`",
            f"- workspaceboard_monitor_ok: `{state['workspaceboard_monitor_ok']}`",
            f"- workspaceboard_monitor_count: `{state['workspaceboard_monitor_count']}`",
            f"- truth_drift_count: `{state['truth_drift_count']}`",
            f"- proof_issue_count: `{state['proof_issue_count']}`",
            f"- proof_repair_packet_count: `{state['proof_repair_packet_count']}`",
            f"- packet_pending_review_count: `{state['packet_pending_review_count']}`",
            f"- dirty_repo_count: `{state['dirty_repo_count']}`",
            f"- loop_next_action: `{state['next_action']}`",
            "",
            "## Source Artifacts",
            "",
        ]
    )
    for source in packet["source_artifacts"]:
        lines.append(
            f"- `{source['path']}` exists=`{source['exists']}` mtime=`{source['mtime']}` stale=`{source['stale']}`"
        )
    lines.extend(
        [
            "",
            "## Approval Gates",
            "",
            f"- external_send_allowed: `{gates['external_send_allowed']}`",
            f"- production_mutation_allowed: `{gates['production_mutation_allowed']}`",
            f"- approval_required_for_packet_execution: `{gates['approval_required_for_packet_execution']}`",
            f"- approved_packet_count: `{gates['approved_packet_count']}`",
            f"- boundary: {gates['boundary']}",
            "",
            "## Stop Condition",
            "",
            f"- {packet['stop_condition']}",
        ]
    )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--status-json", type=Path, default=DEFAULT_STATUS_JSON)
    parser.add_argument("--json", type=Path, default=DEFAULT_PACKET_JSON)
    parser.add_argument("--report", type=Path, default=DEFAULT_PACKET_MD)
    parser.add_argument("--max-age-hours", type=float, default=24)
    parser.add_argument("--refresh-loop-status", action="store_true")
    parser.add_argument("--print-json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.refresh_loop_status:
        refresh = refresh_loop_status()
        if not refresh.get("ok"):
            raise SystemExit(json.dumps(refresh, sort_keys=True))
    packet = build_packet(args.status_json, args.max_age_hours)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.write_text(render_markdown(packet), encoding="utf-8")
    if args.print_json:
        print(json.dumps(packet, indent=2, sort_keys=True))
    else:
        print(f"report={args.report}")
        print(f"json={args.json}")
        print(f"next_safe_action={packet['next_safe_action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
