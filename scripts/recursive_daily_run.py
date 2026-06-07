#!/usr/local/bin/python3.13
"""Run the recursive improvement daily proof loop with durable readback."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path("/Users/werkstatt/ai_workspace")
DEFAULT_JSON = ROOT / "project_hub/artifacts/recursive-tools/recursive-daily-run-latest.json"
DEFAULT_REPORT = ROOT / "project_hub/artifacts/recursive-tools/recursive-daily-run-latest.md"


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    returncode: int
    stdout: str
    stderr: str


def run_command(command: list[str], timeout: int = 240) -> CommandResult:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return CommandResult(
        command=command,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def parse_json_stdout(result: CommandResult) -> dict[str, Any]:
    if result.returncode != 0:
        return {}
    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def should_auto_execute(proposal: dict[str, Any]) -> bool:
    return bool(
        proposal.get("recommended_action") == "monitor-recursive-lane"
        and proposal.get("approval_required") is False
        and proposal.get("allowed_fix_class") == "no-op-monitoring"
    )


def summarize_command(result: CommandResult) -> dict[str, Any]:
    return {
        "command": result.command,
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-4000:],
        "stderr_tail": result.stderr[-2000:],
    }


def build_report(payload: dict[str, Any]) -> str:
    proposal = payload.get("proposal") or {}
    execution = payload.get("execution") or {}
    status = payload.get("executor_status") or {}
    lines = [
        "# Recursive Daily Run",
        "",
        f"- Recorded: {payload.get('recorded_at')}",
        f"- Mode: `{payload.get('mode')}`",
        f"- Outcome: `{payload.get('outcome')}`",
        f"- Proposal: `{proposal.get('proposal_id', '')}`",
        f"- Recommended action: `{proposal.get('recommended_action', '')}`",
        f"- Approval required: `{proposal.get('approval_required', '')}`",
        f"- Allowed fix class: `{proposal.get('allowed_fix_class', '')}`",
        f"- Auto executed: `{payload.get('auto_executed')}`",
        "",
        "## Snapshot",
        "",
    ]
    snapshot = proposal.get("source_snapshot") if isinstance(proposal.get("source_snapshot"), dict) else {}
    for key in [
        "service_parity_drift",
        "truth_drift_count",
        "proof_issue_count",
        "proof_repair_candidate_count",
        "registry_ok",
        "coverage_ok",
        "historical_clean_success",
    ]:
        if key in snapshot:
            lines.append(f"- {key}: `{snapshot.get(key)}`")
    lines.extend(["", "## Execution", ""])
    if execution:
        lines.extend(
            [
                f"- execution_state: `{execution.get('execution_state', '')}`",
                f"- ratchet_result: `{execution.get('ratchet_result', '')}`",
                f"- verifier_returncode: `{(execution.get('verifier_result') or {}).get('returncode', '')}`",
            ]
        )
    else:
        lines.append("- Not executed. Approval-required or non-monitor proposal.")
    lines.extend(["", "## Executor Status", ""])
    lines.append(f"- approved_unexecuted_count: `{status.get('approved_unexecuted_count', '')}`")
    lines.append(f"- blocked_execution_count: `{status.get('blocked_execution_count', '')}`")
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument(
        "--refresh-historical",
        action="store_true",
        help="Refresh historical recommendation traces before proposal generation. Use for weekly rollup.",
    )
    parser.add_argument("--print-json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    queue_command = ["/usr/local/bin/python3.13", "scripts/recursive_proposal_queue.py", "--json"]
    mode = "weekly-refresh" if args.refresh_historical else "daily"
    if not args.refresh_historical:
        queue_command.insert(-1, "--skip-historical-benchmark-refresh")

    queue_result = run_command(queue_command, timeout=300 if args.refresh_historical else 120)
    proposal = parse_json_stdout(queue_result)
    execution: dict[str, Any] = {}
    auto_executed = False
    outcome = "proposal_generated" if queue_result.returncode == 0 else "queue_failed"

    if proposal and should_auto_execute(proposal):
        auto_executed = True
        execute_result = run_command(
            [
                "/usr/local/bin/python3.13",
                "scripts/recursive_proposal_executor.py",
                "execute",
                "--proposal-id",
                str(proposal["proposal_id"]),
                "--json",
            ],
            timeout=240,
        )
        execution = parse_json_stdout(execute_result)
        outcome = "monitor_verified" if execute_result.returncode == 0 else "monitor_verifier_failed"
    elif proposal and proposal.get("approval_required"):
        outcome = "approval_required"

    status_result = run_command(
        ["/usr/local/bin/python3.13", "scripts/recursive_proposal_executor.py", "status", "--json"],
        timeout=60,
    )
    status = parse_json_stdout(status_result)

    payload = {
        "recorded_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
        "mode": mode,
        "outcome": outcome,
        "auto_executed": auto_executed,
        "proposal": proposal,
        "execution": execution,
        "executor_status": status,
        "commands": {
            "queue": summarize_command(queue_result),
            "status": summarize_command(status_result),
        },
    }
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.report.write_text(build_report(payload), encoding="utf-8")
    if args.print_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"report={args.report}")
        print(f"json={args.json}")
        print(f"outcome={outcome}")
        if proposal:
            print(f"proposal_id={proposal.get('proposal_id')}")
    return 0 if outcome not in {"queue_failed", "monitor_verifier_failed"} else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
