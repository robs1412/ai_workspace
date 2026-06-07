#!/usr/local/bin/python3.13
"""Execute or verify approved recursive improvement proposals under an allowlist."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path("/Users/werkstatt/ai_workspace")
PROPOSAL_DIR = ROOT / "project_hub/artifacts/recursive-tools/proposals"
QUEUE_LOG = ROOT / "project_hub/artifacts/recursive-tools/recursive-proposal-queue.jsonl"
EXECUTION_LOG = ROOT / "project_hub/artifacts/recursive-tools/recursive-proposal-executions.jsonl"
HISTORICAL_BENCHMARK_DIR = ROOT / "sandboxes/recursive-improve-pilot-target-313"
RECURSIVE_IMPROVE_BIN = ROOT / "sandboxes/recursive-improve/.venv/bin/recursive-improve"
HISTORICAL_BENCHMARK_RESULTS = (
    HISTORICAL_BENCHMARK_DIR / "eval/historical-recommendation-benchmark/eval_results.json"
)
HISTORICAL_BENCHMARK_REPORT = (
    ROOT / "project_hub/artifacts/recursive-tools/recursive-historical-recommendation-benchmark-2026-05-24.md"
)


@dataclass(frozen=True)
class FixClassPolicy:
    name: str
    mutates_live_state: bool
    verifier: list[str]
    verifier_cwd: Path = ROOT
    auto_mutator: list[str] | None = None
    mutator_cwd: Path = ROOT
    proof_hint: str = ""


FIX_POLICIES: dict[str, FixClassPolicy] = {
    "no-op-monitoring": FixClassPolicy(
        name="no-op-monitoring",
        mutates_live_state=False,
        verifier=[
            "/bin/bash",
            "-lc",
            (
                "./scripts/recursive_registry_lint.py --json >/dev/null && "
                "./scripts/service_parity_check.py --mode all --fail-on-drift >/dev/null && "
                "./scripts/task_flow_truth_drift_check.py --fail-on-drift >/dev/null"
            ),
        ],
        proof_hint="Registry, service parity, and truth-drift checks all return clean.",
    ),
    "proof-closeout-classification": FixClassPolicy(
        name="proof-closeout-classification",
        mutates_live_state=False,
        verifier=["./scripts/task_flow_truth_drift_check.py", "--fail-on-drift"],
        proof_hint="Truth-drift checker returns zero drift and proof issue classes are present for triage.",
    ),
    "registry-metadata-fix": FixClassPolicy(
        name="registry-metadata-fix",
        mutates_live_state=False,
        verifier=["./scripts/recursive_registry_lint.py", "--json"],
        proof_hint="Registry lint returns ok=true.",
    ),
    "recommendation-corpus-fix": FixClassPolicy(
        name="recommendation-corpus-fix",
        mutates_live_state=False,
        verifier=[
            str(RECURSIVE_IMPROVE_BIN),
            "eval",
            "eval/historical-recommendation-traces",
            "--output-dir",
            "eval/historical-recommendation-benchmark",
        ],
        verifier_cwd=HISTORICAL_BENCHMARK_DIR,
        auto_mutator=[
            "/usr/local/bin/python3.13",
            "run_historical_recommendation_benchmark.py",
        ],
        mutator_cwd=HISTORICAL_BENCHMARK_DIR,
        proof_hint="Historical recommendation benchmark returns clean success.",
    ),
    "source-runtime-parity-fix": FixClassPolicy(
        name="source-runtime-parity-fix",
        mutates_live_state=True,
        verifier=[
            "./scripts/service_parity_check.py",
            "--mode",
            "all",
            "--fail-on-drift",
        ],
        auto_mutator=[
            "./scripts/service_parity_check.py",
            "--mode",
            "installed",
            "--fix-installed-interpreters",
        ],
        proof_hint="Service parity check returns zero drift after writable installed-runtime fixes.",
    ),
    "truth-drift-single-item-repair": FixClassPolicy(
        name="truth-drift-single-item-repair",
        mutates_live_state=True,
        verifier=["./scripts/task_flow_truth_drift_check.py", "--fail-on-drift"],
        auto_mutator=None,
        proof_hint="Truth-drift checker returns zero drift. No generic live mutator is allowed yet.",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    status = subparsers.add_parser("status", help="Show approved/executable proposal state.")
    status.add_argument("--json", action="store_true")

    execute = subparsers.add_parser("execute", help="Execute or verify one approved proposal.")
    execute.add_argument("--proposal-id", required=True, help="Proposal id, or 'latest-approved'.")
    execute.add_argument("--dry-run", action="store_true", help="Plan only; do not run mutator/verifier.")
    execute.add_argument(
        "--allow-live-mutation",
        action="store_true",
        help="Permit allowlisted policies that mutate live/runtime state.",
    )
    execute.add_argument("--json", action="store_true")

    supersede = subparsers.add_parser(
        "supersede",
        help="Mark a blocked proposal as superseded by a later verified retry.",
    )
    supersede.add_argument("--proposal-id", required=True, help="Blocked proposal id to supersede.")
    supersede.add_argument("--by-proposal-id", required=True, help="Verified replacement proposal id.")
    supersede.add_argument("--reason", required=True, help="Source-backed reason for superseding.")
    supersede.add_argument("--json", action="store_true")

    return parser.parse_args()


def now_local() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON file: {path}: {exc}") from exc


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def proposal_path_for(proposal_id: str) -> Path:
    return PROPOSAL_DIR / f"{proposal_id}.json"


def queue_rows() -> list[dict[str, Any]]:
    if not QUEUE_LOG.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in QUEUE_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            rows.append({"parse_error": line})
    return rows


def load_proposal(proposal_id: str) -> tuple[Path, dict[str, Any]]:
    path = proposal_path_for(proposal_id)
    return path, read_json(path)


def latest_approved_proposal_id() -> str:
    for row in reversed(queue_rows()):
        proposal_id = row.get("proposal_id")
        if not proposal_id:
            continue
        _, proposal = load_proposal(str(proposal_id))
        if proposal.get("decision_state") == "approved" and not proposal.get("execution_state"):
            return str(proposal_id)
    raise SystemExit("no approved unexecuted recursive proposal found")


def resolve_proposal_id(proposal_id: str) -> str:
    if proposal_id == "latest-approved":
        return latest_approved_proposal_id()
    return proposal_id


def run_command(command: list[str], cwd: Path) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        timeout=180,
    )
    return {
        "command": command,
        "cwd": str(cwd),
        "returncode": proc.returncode,
        "stdout_tail": proc.stdout[-6000:],
        "stderr_tail": proc.stderr[-4000:],
    }


def load_optional_json(path: Path) -> dict[str, Any]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def collect_policy_proof(policy: FixClassPolicy, verifier_result: dict[str, Any]) -> dict[str, Any]:
    proof: dict[str, Any] = {
        "proof_hint": policy.proof_hint,
        "verifier_returncode": verifier_result.get("returncode"),
        "verifier_command": verifier_result.get("command") or [],
        "verifier_cwd": verifier_result.get("cwd") or str(policy.verifier_cwd),
    }
    if policy.name == "recommendation-corpus-fix":
        benchmark = load_optional_json(HISTORICAL_BENCHMARK_RESULTS)
        clean_success = (
            benchmark.get("metrics", {})
            .get("clean_success_rate", {})
            .get("value")
        )
        proof.update(
            {
                "benchmark_results_json": str(HISTORICAL_BENCHMARK_RESULTS),
                "benchmark_report": str(HISTORICAL_BENCHMARK_REPORT),
                "benchmark_run_id": benchmark.get("run_id") or "",
                "benchmark_trace_count": benchmark.get("trace_count", 0),
                "benchmark_clean_success_rate": clean_success,
                "benchmark_success": bool(benchmark.get("success")),
            }
        )
    elif policy.name == "registry-metadata-fix":
        proof["registry_lint_command"] = "./scripts/recursive_registry_lint.py --json"
    elif policy.name == "source-runtime-parity-fix":
        proof["service_parity_report"] = str(
            ROOT / "project_hub/artifacts/recursive-tools/service-parity-check-latest.md"
        )
    elif policy.name in {"truth-drift-single-item-repair", "proof-closeout-classification"}:
        proof["truth_drift_report"] = str(
            ROOT / "project_hub/artifacts/recursive-tools/task-flow-truth-drift-latest.md"
        )
    return proof


def ratchet_result_for(verified: bool, policy: FixClassPolicy) -> dict[str, str]:
    if verified:
        return {
            "ratchet_result": "keep",
            "ratchet_reason": f"{policy.name} verifier passed; execution proof is durable.",
        }
    return {
        "ratchet_result": "revert_required",
        "ratchet_reason": f"{policy.name} verifier failed; stop and revert or repair before another execution.",
    }


def approved_state(proposal: dict[str, Any]) -> bool:
    return proposal.get("decision_state") == "approved"


def execution_authorized(proposal: dict[str, Any], fix_class: str) -> bool:
    if approved_state(proposal):
        return True
    return not proposal.get("approval_required") and fix_class in {"no-op-monitoring", "proof-closeout-classification"}


def execution_statuses() -> dict[str, Any]:
    proposals = []
    for row in queue_rows():
        proposal_id = row.get("proposal_id")
        if not proposal_id:
            continue
        path = proposal_path_for(str(proposal_id))
        if not path.exists():
            continue
        proposal = read_json(path)
        fix_class = str(proposal.get("allowed_fix_class") or "")
        policy = FIX_POLICIES.get(fix_class)
        proposals.append(
            {
                "proposal_id": proposal_id,
                "recommended_action": proposal.get("recommended_action"),
                "allowed_fix_class": fix_class,
                "decision_state": proposal.get("decision_state") or "",
                "execution_state": proposal.get("execution_state") or "",
                "ratchet_result": proposal.get("ratchet_result") or "",
                "approved_unexecuted": approved_state(proposal)
                and not proposal.get("execution_state"),
                "execution_authorized": execution_authorized(proposal, fix_class)
                and not proposal.get("execution_state"),
                "executor_allowlisted": bool(policy),
                "mutates_live_state": bool(policy.mutates_live_state) if policy else False,
                "has_auto_mutator": bool(policy.auto_mutator) if policy else False,
            }
        )
    return {
        "checked_at": now_local(),
        "approved_unexecuted_count": sum(1 for item in proposals if item["approved_unexecuted"]),
        "blocked_execution_count": sum(1 for item in proposals if item["execution_state"] == "blocked"),
        "proposals": proposals,
        "allowlisted_fix_classes": sorted(FIX_POLICIES),
    }


def fail_event(proposal_id: str, proposal: dict[str, Any], state: str, reason: str) -> dict[str, Any]:
    return {
        "event": "execution_blocked",
        "proposal_id": proposal_id,
        "recorded_at": now_local(),
        "execution_state": state,
        "reason": reason,
        "recommended_action": proposal.get("recommended_action"),
        "allowed_fix_class": proposal.get("allowed_fix_class"),
        "risk_class": proposal.get("risk_class"),
    }


def verified_retry_state(proposal: dict[str, Any]) -> bool:
    return proposal.get("execution_state") == "verified" and proposal.get("ratchet_result") == "keep"


def supersede(args: argparse.Namespace) -> int:
    path, proposal = load_proposal(args.proposal_id)
    _, replacement = load_proposal(args.by_proposal_id)

    if proposal.get("execution_state") != "blocked":
        event = fail_event(
            args.proposal_id,
            proposal,
            "blocked_not_supersedable",
            f"execution_state is {proposal.get('execution_state') or 'unset'}, not blocked",
        )
        append_jsonl(EXECUTION_LOG, event)
        if args.json:
            print(json.dumps(event, indent=2, sort_keys=True))
        else:
            print(f"blocked={event['reason']}")
        return 2

    if not verified_retry_state(replacement):
        event = fail_event(
            args.proposal_id,
            proposal,
            "blocked_replacement_not_verified",
            f"replacement {args.by_proposal_id} is not verified with ratchet_result=keep",
        )
        event["replacement_proposal_id"] = args.by_proposal_id
        append_jsonl(EXECUTION_LOG, event)
        if args.json:
            print(json.dumps(event, indent=2, sort_keys=True))
        else:
            print(f"blocked={event['reason']}")
        return 2

    recorded_at = now_local()
    event = {
        "event": "execution_superseded",
        "proposal_id": args.proposal_id,
        "replacement_proposal_id": args.by_proposal_id,
        "recorded_at": recorded_at,
        "execution_state": "superseded_by_verified_retry",
        "recommended_action": proposal.get("recommended_action"),
        "allowed_fix_class": proposal.get("allowed_fix_class"),
        "risk_class": proposal.get("risk_class"),
        "ratchet_result": "superseded",
        "ratchet_reason": args.reason,
    }
    append_jsonl(EXECUTION_LOG, event)

    proposal["execution_state"] = event["execution_state"]
    proposal["execution_recorded_at"] = recorded_at
    proposal["superseded_by"] = args.by_proposal_id
    proposal["superseded_reason"] = args.reason
    proposal["ratchet_result"] = event["ratchet_result"]
    proposal["ratchet_reason"] = event["ratchet_reason"]
    write_json(path, proposal)

    if args.json:
        print(json.dumps(event, indent=2, sort_keys=True))
    else:
        print(f"proposal_id={args.proposal_id}")
        print(f"execution_state={event['execution_state']}")
        print(f"superseded_by={args.by_proposal_id}")
    return 0


def execute(args: argparse.Namespace) -> int:
    proposal_id = resolve_proposal_id(args.proposal_id)
    path, proposal = load_proposal(proposal_id)
    fix_class = str(proposal.get("allowed_fix_class") or "")
    policy = FIX_POLICIES.get(fix_class)

    if not execution_authorized(proposal, fix_class):
        event = fail_event(
            proposal_id,
            proposal,
            "blocked_not_approved",
            f"decision_state is {proposal.get('decision_state') or 'unset'}, not approved and proposal requires approval",
        )
        append_jsonl(EXECUTION_LOG, event)
        if args.json:
            print(json.dumps(event, indent=2, sort_keys=True))
        else:
            print(f"blocked={event['reason']}")
        return 2

    if proposal.get("execution_state") in {"verified", "executed", "blocked"}:
        event = fail_event(
            proposal_id,
            proposal,
            "blocked_already_terminal",
            f"execution_state is already {proposal.get('execution_state')}",
        )
        append_jsonl(EXECUTION_LOG, event)
        if args.json:
            print(json.dumps(event, indent=2, sort_keys=True))
        else:
            print(f"blocked={event['reason']}")
        return 2

    if policy is None:
        event = fail_event(proposal_id, proposal, "blocked_unallowlisted", f"fix class {fix_class} is not allowlisted")
        append_jsonl(EXECUTION_LOG, event)
        if args.json:
            print(json.dumps(event, indent=2, sort_keys=True))
        else:
            print(f"blocked={event['reason']}")
        return 2

    if policy.mutates_live_state and not args.allow_live_mutation:
        event = fail_event(
            proposal_id,
            proposal,
            "blocked_live_mutation_gate",
            f"fix class {fix_class} can mutate live/runtime state; rerun with --allow-live-mutation",
        )
        append_jsonl(EXECUTION_LOG, event)
        if args.json:
            print(json.dumps(event, indent=2, sort_keys=True))
        else:
            print(f"blocked={event['reason']}")
        return 2

    planned = {
        "event": "execution_plan",
        "proposal_id": proposal_id,
        "recorded_at": now_local(),
        "allowed_fix_class": fix_class,
        "mutates_live_state": policy.mutates_live_state,
        "mutator": policy.auto_mutator or [],
        "verifier": policy.verifier,
        "proof_hint": policy.proof_hint,
        "dry_run": bool(args.dry_run),
    }
    if args.dry_run:
        if args.json:
            print(json.dumps(planned, indent=2, sort_keys=True))
        else:
            print(f"proposal_id={proposal_id}")
            print(f"allowed_fix_class={fix_class}")
            print(f"mutator={policy.auto_mutator or []}")
            print(f"verifier={policy.verifier}")
        return 0

    if policy.auto_mutator is None and fix_class not in {"no-op-monitoring", "proof-closeout-classification"}:
        event = fail_event(
            proposal_id,
            proposal,
            "blocked_no_auto_mutator",
            f"fix class {fix_class} is allowlisted for verification but has no generic auto-mutator",
        )
        append_jsonl(EXECUTION_LOG, event)
        proposal["execution_state"] = "blocked"
        proposal["execution_recorded_at"] = event["recorded_at"]
        proposal["execution_blocker"] = event["reason"]
        write_json(path, proposal)
        if args.json:
            print(json.dumps(event, indent=2, sort_keys=True))
        else:
            print(f"blocked={event['reason']}")
        return 2

    mutator_result: dict[str, Any] | None = None
    if policy.auto_mutator:
        mutator_result = run_command(policy.auto_mutator, policy.mutator_cwd)
        if mutator_result["returncode"] != 0:
            event = fail_event(
                proposal_id,
                proposal,
                "blocked_mutator_failed",
                f"mutator exited {mutator_result['returncode']}",
            )
            event["mutator_result"] = mutator_result
            event.update(ratchet_result_for(False, policy))
            append_jsonl(EXECUTION_LOG, event)
            proposal["execution_state"] = "blocked"
            proposal["execution_recorded_at"] = event["recorded_at"]
            proposal["execution_blocker"] = event["reason"]
            proposal["execution_mutator_result"] = mutator_result
            proposal["ratchet_result"] = event["ratchet_result"]
            proposal["ratchet_reason"] = event["ratchet_reason"]
            write_json(path, proposal)
            if args.json:
                print(json.dumps(event, indent=2, sort_keys=True))
            else:
                print(f"blocked={event['reason']}")
            return 2

    verifier_result = run_command(policy.verifier, policy.verifier_cwd)
    recorded_at = now_local()
    verified = verifier_result["returncode"] == 0
    proof = collect_policy_proof(policy, verifier_result)
    ratchet = ratchet_result_for(verified, policy)
    event = {
        "event": "execution_verified" if verified else "execution_blocked",
        "proposal_id": proposal_id,
        "recorded_at": recorded_at,
        "execution_state": "verified" if verified else "blocked",
        "recommended_action": proposal.get("recommended_action"),
        "allowed_fix_class": fix_class,
        "risk_class": proposal.get("risk_class"),
        "mutator_result": mutator_result,
        "verifier_result": verifier_result,
        "execution_proof": proof,
        **ratchet,
        "proof_hint": policy.proof_hint,
    }
    append_jsonl(EXECUTION_LOG, event)

    proposal["execution_state"] = event["execution_state"]
    proposal["execution_recorded_at"] = recorded_at
    proposal["execution_proof_hint"] = policy.proof_hint
    proposal["execution_proof"] = proof
    proposal["ratchet_result"] = ratchet["ratchet_result"]
    proposal["ratchet_reason"] = ratchet["ratchet_reason"]
    proposal["execution_verifier_result"] = verifier_result
    if mutator_result is not None:
        proposal["execution_mutator_result"] = mutator_result
    if not verified:
        proposal["execution_blocker"] = f"verifier exited {verifier_result['returncode']}"
    write_json(path, proposal)

    if args.json:
        print(json.dumps(event, indent=2, sort_keys=True))
    else:
        print(f"proposal_id={proposal_id}")
        print(f"execution_state={event['execution_state']}")
        print(f"execution_log={EXECUTION_LOG}")
    return 0 if verified else 2


def print_status(args: argparse.Namespace) -> int:
    status = execution_statuses()
    if args.json:
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0
    print(f"checked_at={status['checked_at']}")
    print(f"approved_unexecuted_count={status['approved_unexecuted_count']}")
    for item in status["proposals"]:
        print(
            "proposal_id={proposal_id} decision_state={decision_state} "
            "execution_state={execution_state} fix_class={allowed_fix_class}".format(**item)
        )
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "status":
        return print_status(args)
    if args.command == "execute":
        return execute(args)
    if args.command == "supersede":
        return supersede(args)
    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
