#!/usr/local/bin/python3.13
"""Read-only Task Flow and Workspaceboard truth-drift checker."""

from __future__ import annotations

import argparse
import json
import re
import socket
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from recursive_registry_core import load_json as load_registry_json
from recursive_registry_core import validate_task_flow_truth_config


DEFAULT_CONFIG = Path("/Users/werkstatt/ai_workspace/scripts/task_flow_truth_surfaces.json")
DEFAULT_REPORT = Path(
    "/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/"
    "task-flow-truth-drift-latest.md"
)
DEFAULT_JSON = Path(
    "/Users/werkstatt/ai_workspace/project_hub/artifacts/recursive-tools/"
    "task-flow-truth-drift-latest.json"
)


@dataclass
class Drift:
    kind: str
    severity: str
    title: str
    detail: str
    path: str = ""
    session_id: str = ""
    dedupe_key: str = ""


@dataclass
class ProofIssue:
    kind: str
    severity: str
    title: str
    detail: str
    dedupe_key: str = ""
    session_id: str = ""
    owner_lane: str = ""
    missing_fields: list[str] | None = None


def safe_text(value: object, limit: int = 220) -> str:
    text = " ".join(str(value or "").split())
    return text[:limit]


NON_SESSION_REF = re.compile(
    r"^(none|n/a|not_applicable|ai|task|manager|direct|runtime|queued|start_or_reuse)",
    re.IGNORECASE,
)


def is_session_ref(value: str) -> bool:
    return value != "" and NON_SESSION_REF.search(value) is None


def load_json_path(path: Path) -> dict:
    return load_registry_json(path)


def validate_config(config: dict) -> dict:
    return validate_task_flow_truth_config(config)


def run_json_command(command: list[str], payload: dict | None = None, timeout: int = 20) -> dict:
    result = subprocess.run(
        command,
        input=(json.dumps(payload) if payload is not None else None),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(command)} :: {safe_text(result.stderr, 300)}")
    return json.loads(result.stdout)


def fetch_json(url: str, timeout: float) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return json.loads(response.read())
    except TimeoutError as exc:
        raise RuntimeError(f"timed out fetching {url} after {timeout:g}s") from exc
    except socket.timeout as exc:
        raise RuntimeError(f"timed out fetching {url} after {timeout:g}s") from exc
    except urllib.error.URLError as exc:
        reason = safe_text(getattr(exc, "reason", exc), 300)
        raise RuntimeError(f"failed fetching {url}: {reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"invalid JSON from {url}: {safe_text(exc, 300)}") from exc


def load_board_sessions(config: dict, timeout: float) -> tuple[dict, dict[str, dict]]:
    board_config = config["board"]
    command = board_config.get("overview_cmd")
    if isinstance(command, list) and command:
        board = run_json_command(command, None, timeout=max(1, int(timeout)))
        source = " ".join(str(part) for part in command)
    else:
        source = board_config["status_url"]
        board = fetch_json(source, timeout)
    sessions = board.get(board_config["managed_sessions_key"], [])
    if not isinstance(sessions, list):
        raise RuntimeError(f"{source} did not return list field {board_config['managed_sessions_key']}")
    session_map: dict[str, dict] = {}
    for item in sessions:
        if not isinstance(item, dict):
            continue
        session_id = safe_text(item.get("session_id") or item.get("id"), 80)
        if session_id:
            session_map[session_id] = item
    return board, session_map


def normalize_session_refs(item: dict) -> list[str]:
    raw_refs = item.get("workspaceboard_session_refs")
    if isinstance(raw_refs, list):
        refs = []
        for ref in raw_refs:
            text = safe_text(ref, 80)
            if is_session_ref(text):
                refs.append(text)
    else:
        refs = []
        direct = safe_text(item.get("workspaceboard_session") or item.get("session_id"), 80)
        if is_session_ref(direct):
            refs.append(direct)

    seen = set()
    ordered = []
    for ref in refs:
        if ref not in seen:
            seen.add(ref)
            ordered.append(ref)
    return ordered


def build_drifts(config: dict, board_sessions: dict[str, dict], tf_report: dict, proof_report: dict) -> list[Drift]:
    drifts: list[Drift] = []
    active_statuses = set(config["task_flow"]["active_statuses"])
    closed_statuses = set(config["task_flow"]["closed_statuses"])
    board_active = set(config["board"]["active_runtime_statuses"])
    rules = config["rules"]

    items = tf_report.get("items", [])
    for item in items:
        if not isinstance(item, dict):
            continue
        effective_status = safe_text(item.get("effective_status") or item.get("status"), 80)
        title = safe_text(item.get("display_name") or item.get("title") or item.get("scheduled_action"), 180)
        dedupe_key = safe_text(item.get("dedupe_key"), 180)
        session_refs = normalize_session_refs(item)

        if rules.get("flag_active_missing_board_session") and effective_status in active_statuses:
            for session_id in session_refs:
                if session_id and session_id not in board_sessions:
                    drifts.append(
                        Drift(
                            kind="active_missing_board_session",
                            severity="high",
                            title=title,
                            detail=f"active Task Flow row references missing board session {session_id}",
                            session_id=session_id,
                            dedupe_key=dedupe_key,
                        )
                    )

    proof_items = proof_report.get("items", [])
    for item in proof_items:
        if not isinstance(item, dict):
            continue
        effective_status = safe_text(item.get("effective_status") or item.get("status"), 80)
        title = safe_text(item.get("display_name") or item.get("title") or item.get("scheduled_action"), 180)
        dedupe_key = safe_text(item.get("dedupe_key"), 180)
        closeout_proof = bool(item.get("closeout_proof_present"))
        sent_proof = bool(item.get("sent_proof_present"))
        output_channel = safe_text(item.get("output_channel"), 40)
        if (
            rules.get("flag_closed_without_closeout_proof")
            and effective_status in closed_statuses
            and not closeout_proof
        ):
            drifts.append(
                Drift(
                    kind="closed_without_closeout_proof",
                    severity="high",
                    title=title,
                    detail=f"{effective_status} row lacks closeout proof in proof report",
                    dedupe_key=dedupe_key,
                )
            )
        if (
            rules.get("flag_email_report_without_sent_proof")
            and effective_status in {"reported", "completed"}
            and output_channel == "email"
            and not sent_proof
        ):
            drifts.append(
                Drift(
                    kind="email_report_without_sent_proof",
                    severity="medium",
                    title=title,
                    detail=f"{effective_status} email row lacks sent proof in proof report",
                    dedupe_key=dedupe_key,
                )
            )

        if rules.get("flag_closed_with_live_board_session") and effective_status in closed_statuses:
            for session_id in session_refs:
                board_item = board_sessions.get(session_id)
                if not board_item:
                    continue
                runtime_status = safe_text(
                    board_item.get("runtime_status") or board_item.get("persisted_status"),
                    80,
                )
                if runtime_status in board_active:
                    drifts.append(
                        Drift(
                            kind="closed_with_live_board_session",
                            severity="medium",
                            title=title,
                            detail=f"closed Task Flow row still has live board session {session_id} in {runtime_status}",
                            session_id=session_id,
                            dedupe_key=dedupe_key,
                        )
                    )

    totals = tf_report.get("totals", {})
    if rules.get("flag_scheduler_violations") and int(totals.get("scheduler_violations") or 0) > 0:
        drifts.append(
            Drift(
                kind="scheduler_violations_present",
                severity="high",
                title="Scheduler violations present",
                detail=f"{int(totals.get('scheduler_violations') or 0)} scheduler violations in task-flow-report",
            )
        )
    if rules.get("flag_scheduler_route_candidates") and int(totals.get("scheduler_route_candidates") or 0) > 0:
        drifts.append(
            Drift(
                kind="scheduler_route_candidates_present",
                severity="medium",
                title="Scheduler route candidates present",
                detail=f"{int(totals.get('scheduler_route_candidates') or 0)} scheduler route candidates in task-flow-report",
            )
        )

    return drifts


def classify_proof_issue(item: dict) -> ProofIssue:
    severity = safe_text(item.get("severity"), 80)
    effective_status = safe_text(item.get("effective_status") or item.get("status"), 80)
    status = safe_text(item.get("status"), 80)
    dedupe_key = safe_text(item.get("dedupe_key"), 180)
    owner_lane = safe_text(item.get("owner_lane"), 80)
    session_id = safe_text(item.get("workspaceboard_session"), 80)
    title = safe_text(item.get("display_name") or item.get("title") or item.get("source_links") or dedupe_key, 180)
    missing_fields = [safe_text(field, 80) for field in item.get("missing_fields", []) if safe_text(field, 80)]
    blocked_state = safe_text(item.get("blocked_resolution_state"), 120)
    latest_event = safe_text(item.get("latest_event"), 120)
    next_update = safe_text(item.get("next_update"), 220)

    if effective_status == "working" and "ops_portal_or_domain_task" in missing_fields and session_id:
        kind = "active_worker_missing_domain_task"
        detail = f"working row has visible session {session_id} but lacks ops_portal_or_domain_task"
    elif blocked_state == "routed_needs_owner_question":
        kind = "blocked_needs_owner_question_proof"
        detail = "blocked row is routed-needs-owner-question and needs owner-question/blocker proof"
    elif blocked_state == "blocker_email_required":
        kind = "blocked_missing_blocker_email"
        detail = "blocked row requires blocker email or equivalent source-backed blocker proof"
    elif status == "blocked" or effective_status == "blocked":
        kind = "blocked_unclassified_proof_gap"
        detail = f"blocked row has unclassified proof posture: {blocked_state or latest_event or next_update}"
    elif severity == "attention":
        kind = "attention_missing_finish_link"
        detail = f"attention row missing {', '.join(missing_fields) if missing_fields else 'proof/readback fields'}"
    elif severity == "closeout_gap":
        kind = "closed_closeout_gap"
        detail = "closed/reported/filed row lacks closeout proof marker"
    else:
        kind = "proof_issue_unclassified"
        detail = f"{severity or 'unknown'} proof issue for status {effective_status or status}"

    return ProofIssue(
        kind=kind,
        severity=severity,
        title=title,
        detail=detail,
        dedupe_key=dedupe_key,
        session_id=session_id,
        owner_lane=owner_lane,
        missing_fields=missing_fields,
    )


def proof_issue_has_blocker_marker(item: dict) -> bool:
    return any(
        safe_text(item.get(field), 300)
        for field in [
            "completion_or_blocker_email",
            "clarification_email",
        ]
    )


def classify_proof_issues(proof_report: dict) -> list[ProofIssue]:
    issues: list[ProofIssue] = []
    for item in proof_report.get("items", []):
        if not isinstance(item, dict):
            continue
        if safe_text(item.get("severity"), 80) in {"closeout_gap", "attention", "blocked"}:
            if (
                safe_text(item.get("blocked_resolution_state"), 120) == "blocker_email_required"
                and proof_issue_has_blocker_marker(item)
            ):
                continue
            issues.append(classify_proof_issue(item))
    return issues


def build_report(
    board: dict,
    tf_report: dict,
    proof_report: dict,
    drifts: list[Drift],
    proof_issues: list[ProofIssue],
    config_path: Path,
) -> str:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    lines = [
        "# Task Flow Truth Drift Check",
        "",
        f"- Recorded: {now}",
        f"- Config: `{config_path}`",
        f"- Board ok: `{bool(board.get('ok'))}`",
        f"- Managed sessions: `{len(board.get('managed_sessions', []))}`",
        f"- Task Flow rows scanned: `{len(tf_report.get('items', []))}`",
        f"- Proof rows scanned: `{len(proof_report.get('items', []))}`",
        f"- Drift count: `{len(drifts)}`",
        "",
        "## Summary",
        "",
        f"- scheduler_violations: `{int(tf_report.get('totals', {}).get('scheduler_violations') or 0)}`",
        f"- scheduler_route_candidates: `{int(tf_report.get('totals', {}).get('scheduler_route_candidates') or 0)}`",
        f"- proof_closeout_issues: `{int(proof_report.get('totals', {}).get('closeout_issues_shown') or 0)}`",
        "",
        "## Proof Issue Classes",
        "",
    ]
    if proof_issues:
        counts: dict[str, int] = {}
        for item in proof_issues:
            counts[item.kind] = counts.get(item.kind, 0) + 1
        for kind, count in sorted(counts.items()):
            lines.append(f"- {kind}: `{count}`")
        lines.extend(["", "## Proof Issue Samples", ""])
        for item in proof_issues[:20]:
            lines.extend(
                [
                    f"- {item.kind}: `{item.severity}` {item.title}",
                    f"  - detail: {item.detail}",
                    f"  - dedupe_key: `{item.dedupe_key}`",
                ]
            )
            if item.session_id:
                lines.append(f"  - session_id: `{item.session_id}`")
            if item.owner_lane:
                lines.append(f"  - owner_lane: `{item.owner_lane}`")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Drift",
            "",
        ]
    )
    if drifts:
        for item in drifts[:40]:
            lines.extend(
                [
                    f"- {item.kind}: `{item.severity}` {item.title}",
                    f"  - detail: {item.detail}",
                ]
            )
            if item.session_id:
                lines.append(f"  - session_id: `{item.session_id}`")
            if item.dedupe_key:
                lines.append(f"  - dedupe_key: `{item.dedupe_key}`")
    else:
        lines.append("- None")
    lines.extend(["", "## Recommendation", ""])
    if drifts:
        lines.append("- Truth drift exists. Repair should stay targeted to the named contradiction classes, not broad queue mutation.")
    elif proof_issues:
        lines.append("- Truth drift is clean, but proof issue classes remain. Classify or repair one named class before returning to monitor mode.")
    else:
        lines.append("- Checked board, Task Flow, and proof surfaces are aligned at current coverage.")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--fail-on-drift", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    config = validate_config(load_json_path(args.config))
    board, board_sessions = load_board_sessions(config, args.timeout)
    tf_report = run_json_command(
        config["task_flow"]["workspaceboard_report_cmd"],
        config["task_flow"]["workspaceboard_report_payload"],
        timeout=20,
    )
    proof_report = run_json_command(config["task_flow"]["proof_report_cmd"], None, timeout=20)
    drifts = build_drifts(config, board_sessions, tf_report, proof_report)
    proof_issues = classify_proof_issues(proof_report)

    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        build_report(board, tf_report, proof_report, drifts, proof_issues, args.config),
        encoding="utf-8",
    )
    args.json.parent.mkdir(parents=True, exist_ok=True)
    proof_issue_counts: dict[str, int] = {}
    for item in proof_issues:
        proof_issue_counts[item.kind] = proof_issue_counts.get(item.kind, 0) + 1
    payload = {
        "config": str(args.config),
        "board_ok": bool(board.get("ok")),
        "managed_sessions": len(board.get("managed_sessions", [])),
        "task_flow_rows_scanned": len(tf_report.get("items", [])),
        "proof_rows_scanned": len(proof_report.get("items", [])),
        "scheduler_violations": int(tf_report.get("totals", {}).get("scheduler_violations") or 0),
        "scheduler_route_candidates": int(tf_report.get("totals", {}).get("scheduler_route_candidates") or 0),
        "proof_closeout_issues": int(proof_report.get("totals", {}).get("closeout_issues_shown") or 0),
        "proof_issue_count": len(proof_issues),
        "proof_issue_class_counts": proof_issue_counts,
        "proof_issue_samples": [asdict(item) for item in proof_issues[:20]],
        "drift_count": len(drifts),
        "drifts": [asdict(item) for item in drifts],
    }
    args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"report={args.report}")
    print(f"json={args.json}")
    print(f"drift_count={len(drifts)}")
    if args.fail_on_drift and drifts:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
