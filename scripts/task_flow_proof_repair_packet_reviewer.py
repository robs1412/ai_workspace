#!/usr/local/bin/python3.13
"""Record review decisions for Task Flow proof-repair packets.

This command is intentionally non-executing. It updates packet review state and
appends a durable decision event, but it does not send email or mutate Task
Flow, OPS, Portal, or mailbox state.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


ROOT = Path("/Users/werkstatt/ai_workspace")
PACKET_DIR = ROOT / "project_hub/artifacts/recursive-tools/proof-repair-packets"
DECISION_LOG = ROOT / "project_hub/artifacts/recursive-tools/task-flow-proof-repair-packet-decisions.jsonl"
CANDIDATE_JSON = ROOT / "project_hub/artifacts/recursive-tools/task-flow-proof-repair-candidates-latest.json"

DECISIONS = {
    "approved",
    "rejected",
    "duplicate_no_action",
    "needs_owner_question",
    "blocked",
}


def now_local() -> datetime:
    return datetime.now().astimezone()


def now_text() -> str:
    return now_local().strftime("%Y-%m-%d %H:%M:%S %Z")


def default_expiry() -> str:
    return (now_local() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S %Z")


def read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing packet JSON: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid packet JSON: {path}: {exc}") from exc


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(row, sort_keys=True) + "\n")


def packet_files(packet_dir: Path) -> list[Path]:
    if not packet_dir.exists():
        return []
    return sorted(packet_dir.glob("*.json"))


def resolve_packet_path(packet_ref: str, packet_dir: Path) -> Path:
    direct = Path(packet_ref)
    if direct.exists():
        return direct
    if not direct.is_absolute():
        candidate = packet_dir / packet_ref
        if candidate.exists():
            return candidate
        if not packet_ref.endswith(".json"):
            candidate = packet_dir / f"{packet_ref}.json"
            if candidate.exists():
                return candidate

    matches: list[Path] = []
    for path in packet_files(packet_dir):
        packet = read_json(path)
        if (
            packet_ref == packet.get("dedupe_key")
            or packet_ref == f"{packet.get('dedupe_key')}.{packet.get('proof_kind')}"
            or path.name.startswith(packet_ref)
        ):
            matches.append(path)
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        joined = ", ".join(path.name for path in matches)
        raise SystemExit(f"ambiguous packet reference {packet_ref!r}: {joined}")
    raise SystemExit(f"no packet found for {packet_ref!r}")


def review_state(decision: str) -> str:
    return {
        "approved": "approved",
        "rejected": "rejected",
        "duplicate_no_action": "duplicate_no_action",
        "needs_owner_question": "needs_owner_question",
        "blocked": "blocked",
    }[decision]


def validate_record_args(args: argparse.Namespace, packet: dict[str, Any]) -> None:
    if args.decision == "approved":
        if not args.approved_by:
            raise SystemExit("--approved-by is required for approved packets")
        if args.external_send_allowed and not args.allowed_sender_path:
            raise SystemExit("--allowed-sender-path is required when --external-send-allowed is set")
        if args.production_mutation_allowed and not args.allowed_mutation_surface:
            raise SystemExit(
                "--allowed-mutation-surface is required when --production-mutation-allowed is set"
            )
    if args.decision in {"blocked", "needs_owner_question", "rejected"} and not args.notes:
        raise SystemExit(f"--notes is required for decision {args.decision}")
    approval = packet.get("approval") if isinstance(packet.get("approval"), dict) else {}
    if args.decision == "approved" and not approval.get("required"):
        raise SystemExit("packet does not require approval; record duplicate_no_action or rejected instead")


def approval_contract(args: argparse.Namespace, packet: dict[str, Any], recorded_at: str) -> dict[str, Any]:
    if args.decision != "approved":
        return {}
    required_after_action = []
    verification = packet.get("verification") if isinstance(packet.get("verification"), dict) else {}
    if isinstance(verification.get("required_after_action"), list):
        required_after_action = verification["required_after_action"]
    return {
        "approved_by": args.approved_by,
        "approved_at": recorded_at,
        "expires_at": args.expires_at or default_expiry(),
        "allowed_action": args.allowed_action or packet.get("proposed_action") or "",
        "allowed_sender_path": args.allowed_sender_path or "",
        "allowed_mutation_surface": args.allowed_mutation_surface or "none",
        "external_send_allowed": bool(args.external_send_allowed),
        "production_mutation_allowed": bool(args.production_mutation_allowed),
        "required_readback": args.required_readback or required_after_action,
    }


def record_decision(args: argparse.Namespace) -> int:
    packet_path = resolve_packet_path(args.packet, args.packet_dir)
    packet = read_json(packet_path)
    validate_record_args(args, packet)

    recorded_at = now_text()
    contract = approval_contract(args, packet, recorded_at)
    packet["status"] = review_state(args.decision)
    packet["review"] = {
        "decision": args.decision,
        "reviewed_at": recorded_at,
        "reviewed_by": args.reviewed_by or args.approved_by or "",
        "source_ref": args.source_ref,
        "notes": args.notes,
    }
    if contract:
        packet["approval_contract"] = contract
        packet["approval"]["external_send_allowed"] = contract["external_send_allowed"]
        packet["approval"]["production_mutation_allowed"] = contract["production_mutation_allowed"]
    packet["state_updated_at"] = recorded_at
    write_json(packet_path, packet)

    event = {
        "event": "task_flow_proof_repair_packet_reviewed",
        "recorded_at": recorded_at,
        "packet_path": str(packet_path),
        "dedupe_key": packet.get("dedupe_key"),
        "proof_kind": packet.get("proof_kind"),
        "decision": args.decision,
        "status": packet["status"],
        "source_ref": args.source_ref,
        "notes": args.notes,
        "approval_contract": contract,
    }
    append_jsonl(args.decision_log, event)

    if args.json:
        print(json.dumps({"packet": packet, "event": event}, indent=2, sort_keys=True))
    else:
        print(f"packet={packet_path}")
        print(f"status={packet['status']}")
        print(f"decision_log={args.decision_log}")
    return 0


def collect_status(args: argparse.Namespace) -> dict[str, Any]:
    packets = []
    for path in packet_files(args.packet_dir):
        packet = read_json(path)
        packets.append(
            {
                "packet_path": str(path),
                "dedupe_key": packet.get("dedupe_key"),
                "proof_kind": packet.get("proof_kind"),
                "subject": packet.get("subject"),
                "status": packet.get("status"),
                "decision": (packet.get("review") or {}).get("decision", ""),
                "approval_required": bool((packet.get("approval") or {}).get("required")),
                "external_send_allowed": bool((packet.get("approval") or {}).get("external_send_allowed")),
                "production_mutation_allowed": bool(
                    (packet.get("approval") or {}).get("production_mutation_allowed")
                ),
            }
        )
    pending = [packet for packet in packets if packet.get("status") in {"needs_approval", "ready_for_review"}]
    return {
        "ok": True,
        "checked_at": now_text(),
        "packet_count": len(packets),
        "pending_review_count": len(pending),
        "packets": packets,
    }


def status(args: argparse.Namespace) -> int:
    payload = collect_status(args)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print(f"packet_count={payload['packet_count']}")
    print(f"pending_review_count={payload['pending_review_count']}")
    for packet in payload["packets"]:
        print(f"{packet['status']} {packet['dedupe_key']} {packet['proof_kind']}")
    return 0


def refresh_candidates() -> dict[str, Any]:
    import subprocess

    proc = subprocess.run(
        [
            "/usr/local/bin/python3.13",
            "scripts/task_flow_proof_repair_candidates.py",
            "--print-json",
        ],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    if proc.returncode != 0:
        raise SystemExit(f"candidate detector failed: {proc.stderr or proc.stdout}")
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"candidate detector returned invalid JSON: {exc}") from exc
    return payload if isinstance(payload, dict) else {}


def load_candidate_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.refresh_candidates:
        return refresh_candidates()
    return read_json(args.candidate_json)


def unresolved_candidate_matches(packet: dict[str, Any], payload: dict[str, Any]) -> bool:
    dedupe_key = packet.get("dedupe_key")
    proof_kind = packet.get("proof_kind")
    for candidate in payload.get("candidates") or []:
        if not isinstance(candidate, dict):
            continue
        if candidate.get("dedupe_key") == dedupe_key and candidate.get("proof_kind") == proof_kind:
            return True
    return False


def verify_packet(args: argparse.Namespace) -> int:
    packet_path = resolve_packet_path(args.packet, args.packet_dir)
    packet = read_json(packet_path)
    candidates = load_candidate_payload(args)
    still_unresolved = unresolved_candidate_matches(packet, candidates)
    state = "unresolved" if still_unresolved else "resolved"
    recorded_at = now_text()
    verification = {
        "verified_at": recorded_at,
        "state": state,
        "candidate_count": candidates.get("candidate_count", 0),
        "candidate_generated_at": candidates.get("generated_at", ""),
        "candidate_json": str(args.candidate_json),
        "refreshed_candidates": bool(args.refresh_candidates),
        "required_readback_met": not still_unresolved,
    }
    packet["post_action_verification"] = verification
    packet["state_updated_at"] = recorded_at
    write_json(packet_path, packet)
    event = {
        "event": "task_flow_proof_repair_packet_verified",
        "recorded_at": recorded_at,
        "packet_path": str(packet_path),
        "dedupe_key": packet.get("dedupe_key"),
        "proof_kind": packet.get("proof_kind"),
        "verification_state": state,
        "candidate_count": candidates.get("candidate_count", 0),
        "candidate_generated_at": candidates.get("generated_at", ""),
    }
    append_jsonl(args.decision_log, event)
    if args.json:
        print(json.dumps({"packet": packet, "event": event}, indent=2, sort_keys=True))
    else:
        print(f"packet={packet_path}")
        print(f"verification_state={state}")
        print(f"candidate_count={candidates.get('candidate_count', 0)}")
    return 0


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet-dir", type=Path, default=PACKET_DIR)
    parser.add_argument("--decision-log", type=Path, default=DECISION_LOG)
    subparsers = parser.add_subparsers(dest="command", required=True)

    record = subparsers.add_parser("record", help="Record a packet review decision.")
    record.add_argument("--packet", required=True, help="Packet path, filename, dedupe key, or dedupe.proof ref.")
    record.add_argument("--decision", required=True, choices=sorted(DECISIONS))
    record.add_argument("--reviewed-by", default="", help="Reviewer identity for non-approval decisions.")
    record.add_argument("--approved-by", default="", help="Approver identity; required for approved.")
    record.add_argument("--source-ref", default="", help="Non-secret approval/request source reference.")
    record.add_argument("--notes", default="", help="Short non-secret review note.")
    record.add_argument("--expires-at", default="", help="Approval expiry; defaults to 24 hours for approved.")
    record.add_argument("--allowed-action", default="", help="Approved action; defaults to packet proposed_action.")
    record.add_argument("--allowed-sender-path", default="", help="Approved sender path when external send is allowed.")
    record.add_argument(
        "--allowed-mutation-surface",
        default="",
        help="Approved mutation surface when production mutation is allowed.",
    )
    record.add_argument("--external-send-allowed", action="store_true")
    record.add_argument("--production-mutation-allowed", action="store_true")
    record.add_argument(
        "--required-readback",
        action="append",
        default=[],
        help="Required proof after execution; may be repeated.",
    )
    record.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Show packet review status.")
    status_parser.add_argument("--json", action="store_true")

    verify = subparsers.add_parser(
        "verify",
        help="Verify whether a reviewed packet still appears in proof-repair candidates.",
    )
    verify.add_argument("--packet", required=True, help="Packet path, filename, dedupe key, or dedupe.proof ref.")
    verify.add_argument("--candidate-json", type=Path, default=CANDIDATE_JSON)
    verify.add_argument("--refresh-candidates", action=argparse.BooleanOptionalAction, default=True)
    verify.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "record":
        return record_decision(args)
    if args.command == "status":
        return status(args)
    if args.command == "verify":
        return verify_packet(args)
    raise SystemExit(f"unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
