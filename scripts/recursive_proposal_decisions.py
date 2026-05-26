#!/usr/local/bin/python3.13
"""Record and inspect approval decisions for recursive proposal packets."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path("/Users/werkstatt/ai_workspace")
PROPOSAL_DIR = ROOT / "project_hub/artifacts/recursive-tools/proposals"
QUEUE_LOG = ROOT / "project_hub/artifacts/recursive-tools/recursive-proposal-queue.jsonl"
DECISION_LOG = ROOT / "project_hub/artifacts/recursive-tools/recursive-proposal-decisions.jsonl"

DECISION_TO_STATE = {
    "yes": "approved",
    "approve": "approved",
    "approved": "approved",
    "no": "rejected",
    "reject": "rejected",
    "rejected": "rejected",
    "unclear": "needs_clarification",
    "clarify": "needs_clarification",
    "needs_clarification": "needs_clarification",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    record = subparsers.add_parser("record-decision", help="Record a yes/no/unclear decision.")
    record.add_argument("--proposal-id", required=True, help="Proposal id, or 'latest-pending'.")
    record.add_argument("--decision", required=True, choices=sorted(DECISION_TO_STATE))
    record.add_argument("--source-message-id", default="", help="Reply Message-ID or source reference.")
    record.add_argument("--notes", default="", help="Short non-secret operator note.")
    record.add_argument("--json", action="store_true", help="Print the updated proposal JSON.")

    status = subparsers.add_parser("status", help="Print proposal decision status.")
    status.add_argument("--json", action="store_true", help="Print status JSON.")
    status.add_argument("--limit", type=int, default=20, help="Maximum proposal rows to show.")

    reconcile = subparsers.add_parser(
        "reconcile-clean-monitor",
        help="Supersede pending approval proposals that predate a later clean monitor.",
    )
    reconcile.add_argument("--json", action="store_true", help="Print reconciliation JSON.")

    return parser.parse_args()


def now_local() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing proposal JSON: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid proposal JSON: {path}: {exc}") from exc


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


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


def proposal_path_for(proposal_id: str) -> Path:
    return PROPOSAL_DIR / f"{proposal_id}.json"


def latest_pending_proposal_id() -> str:
    for row in reversed(queue_rows()):
        proposal_id = row.get("proposal_id")
        if not proposal_id:
            continue
        proposal = read_json(proposal_path_for(str(proposal_id)))
        if proposal.get("approval_required") and not proposal.get("decision_state"):
            return str(proposal_id)
    raise SystemExit("no pending approval-required recursive proposal found")


def resolve_proposal_id(proposal_id: str) -> str:
    if proposal_id == "latest-pending":
        return latest_pending_proposal_id()
    return proposal_id


def infer_status(proposal: dict[str, Any]) -> str:
    if proposal.get("decision_state"):
        return str(proposal["decision_state"])
    if proposal.get("approval_required"):
        return "approval_pending"
    return "monitor_no_action"


def collect_status(limit: int) -> dict[str, Any]:
    rows = queue_rows()
    proposal_statuses: list[dict[str, Any]] = []
    for row in rows[-limit:]:
        proposal_id = row.get("proposal_id")
        if not proposal_id:
            proposal_statuses.append({"queue_row": row, "status": "invalid_queue_row"})
            continue
        path = proposal_path_for(str(proposal_id))
        if not path.exists():
            proposal_statuses.append(
                {
                    "proposal_id": proposal_id,
                    "status": "missing_proposal_json",
                    "proposal_json": str(path),
                }
            )
            continue
        proposal = read_json(path)
        proposal_statuses.append(
            {
                "proposal_id": proposal_id,
                "created_at": proposal.get("created_at"),
                "recommended_action": proposal.get("recommended_action"),
                "approval_required": bool(proposal.get("approval_required")),
                "decision_state": proposal.get("decision_state") or "",
                "status": infer_status(proposal),
                "risk_class": proposal.get("risk_class"),
                "allowed_fix_class": proposal.get("allowed_fix_class"),
                "decision_recorded_at": proposal.get("decision_recorded_at") or "",
                "source_message_id": proposal.get("decision_source_message_id") or "",
            }
        )
    pending = [item for item in proposal_statuses if item.get("status") == "approval_pending"]
    latest_clean_monitor = next(
        (
            item
            for item in reversed(proposal_statuses)
            if item.get("status") == "monitor_no_action"
            and item.get("recommended_action") == "monitor-recursive-lane"
        ),
        None,
    )
    return {
        "checked_at": now_local(),
        "proposal_count": len(rows),
        "pending_approval_count": len(pending),
        "latest_clean_monitor": latest_clean_monitor,
        "proposals": proposal_statuses,
    }


def is_clean_monitor(proposal: dict[str, Any]) -> bool:
    snapshot = proposal.get("source_snapshot") or {}
    return (
        proposal.get("recommended_action") == "monitor-recursive-lane"
        and not proposal.get("approval_required")
        and int(snapshot.get("service_parity_drift") or 0) == 0
        and int(snapshot.get("truth_drift_count") or 0) == 0
        and bool(snapshot.get("registry_ok"))
        and bool(snapshot.get("coverage_ok"))
    )


def reconcile_clean_monitor(args: argparse.Namespace) -> int:
    rows = queue_rows()
    latest_clean_index = -1
    latest_clean_id = ""
    for index, row in enumerate(rows):
        proposal_id = row.get("proposal_id")
        if not proposal_id:
            continue
        path = proposal_path_for(str(proposal_id))
        if not path.exists():
            continue
        proposal = read_json(path)
        if is_clean_monitor(proposal):
            latest_clean_index = index
            latest_clean_id = str(proposal_id)

    result = {
        "checked_at": now_local(),
        "latest_clean_monitor": latest_clean_id,
        "superseded": [],
    }
    if latest_clean_index < 0:
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print("latest_clean_monitor=")
            print("superseded_count=0")
        return 0

    for row in rows[:latest_clean_index]:
        proposal_id = row.get("proposal_id")
        if not proposal_id:
            continue
        path = proposal_path_for(str(proposal_id))
        if not path.exists():
            continue
        proposal = read_json(path)
        if not proposal.get("approval_required") or proposal.get("decision_state"):
            continue
        recorded_at = now_local()
        proposal["decision_state"] = "superseded_by_clean_monitor"
        proposal["decision"] = "superseded"
        proposal["decision_recorded_at"] = recorded_at
        proposal["decision_source_message_id"] = ""
        proposal["decision_notes"] = (
            f"Superseded by later clean monitor proposal {latest_clean_id}; no execution remains."
        )
        proposal["state_updated_at"] = recorded_at
        write_json(path, proposal)

        event = {
            "event": "proposal_superseded_by_clean_monitor",
            "proposal_id": str(proposal_id),
            "recorded_at": recorded_at,
            "decision": "superseded",
            "decision_state": "superseded_by_clean_monitor",
            "superseded_by": latest_clean_id,
            "recommended_action": proposal.get("recommended_action"),
            "allowed_fix_class": proposal.get("allowed_fix_class"),
            "risk_class": proposal.get("risk_class"),
        }
        append_jsonl(DECISION_LOG, event)
        result["superseded"].append(event)

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"latest_clean_monitor={latest_clean_id}")
        print(f"superseded_count={len(result['superseded'])}")
        for item in result["superseded"]:
            print(f"superseded={item['proposal_id']}")
    return 0


def record_decision(args: argparse.Namespace) -> int:
    proposal_id = resolve_proposal_id(args.proposal_id)
    path = proposal_path_for(proposal_id)
    proposal = read_json(path)
    decision_key = args.decision.strip().lower()
    decision_state = DECISION_TO_STATE[decision_key]
    recorded_at = now_local()

    if not proposal.get("approval_required") and decision_state == "approved":
        raise SystemExit("refusing to approve a proposal that did not require approval")

    event = {
        "event": "decision_recorded",
        "proposal_id": proposal_id,
        "recorded_at": recorded_at,
        "decision": decision_key,
        "decision_state": decision_state,
        "source_message_id": args.source_message_id,
        "notes": args.notes,
        "recommended_action": proposal.get("recommended_action"),
        "allowed_fix_class": proposal.get("allowed_fix_class"),
        "risk_class": proposal.get("risk_class"),
    }

    proposal["decision"] = decision_key
    proposal["decision_state"] = decision_state
    proposal["decision_recorded_at"] = recorded_at
    proposal["decision_source_message_id"] = args.source_message_id
    proposal["decision_notes"] = args.notes
    proposal["state_updated_at"] = recorded_at

    write_json(path, proposal)
    append_jsonl(DECISION_LOG, event)

    if args.json:
        print(json.dumps(proposal, indent=2, sort_keys=True))
    else:
        print(f"proposal_id={proposal_id}")
        print(f"decision_state={decision_state}")
        print(f"decision_log={DECISION_LOG}")
    return 0


def print_status(args: argparse.Namespace) -> int:
    status = collect_status(args.limit)
    if args.json:
        print(json.dumps(status, indent=2, sort_keys=True))
        return 0
    print(f"checked_at={status['checked_at']}")
    print(f"proposal_count={status['proposal_count']}")
    print(f"pending_approval_count={status['pending_approval_count']}")
    for item in status["proposals"]:
        print(
            "proposal_id={proposal_id} status={status} action={recommended_action} "
            "approval_required={approval_required} decision_state={decision_state}".format(
                **item
            )
        )
    latest = status.get("latest_clean_monitor")
    if latest:
        print(f"latest_clean_monitor={latest['proposal_id']}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "record-decision":
        return record_decision(args)
    if args.command == "status":
        return print_status(args)
    if args.command == "reconcile-clean-monitor":
        return reconcile_clean_monitor(args)
    raise SystemExit(f"unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
