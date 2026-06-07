#!/usr/local/bin/python3.13
"""Generate approval-gated recursive improvement proposal packets."""

from __future__ import annotations

import argparse
import html
import json
import subprocess
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path("/Users/werkstatt/ai_workspace")
PROPOSAL_DIR = ROOT / "project_hub/artifacts/recursive-tools/proposals"
QUEUE_LOG = ROOT / "project_hub/artifacts/recursive-tools/recursive-proposal-queue.jsonl"
FRANK_DRAFT_DIR = ROOT / "frank/drafts/recursive-proposals"
HISTORICAL_BENCHMARK_DIR = ROOT / "sandboxes/recursive-improve-pilot-target-313"
RECURSIVE_IMPROVE_PYTHON = ROOT / "sandboxes/recursive-improve/.venv313/bin/python"
RECURSIVE_IMPROVE_BIN = ROOT / "sandboxes/recursive-improve/.venv313/bin/recursive-improve"
HISTORICAL_BENCHMARK_RUNNER = HISTORICAL_BENCHMARK_DIR / "run_historical_recommendation_benchmark.py"
HISTORICAL_EVAL = (
    HISTORICAL_BENCHMARK_DIR / "eval/historical-recommendation-benchmark/eval_results.json"
)
LIVE_SNAPSHOT_REPORT = (
    ROOT / "project_hub/artifacts/recursive-tools/recursive-live-recommendation-snapshot-2026-05-24.md"
)


@dataclass(frozen=True)
class Proposal:
    proposal_id: str
    created_at: str
    recommended_action: str
    approval_required: bool
    risk_class: str
    allowed_fix_class: str
    why_now: str
    what_changes_if_approved: str
    what_will_not_change: str
    proof_required: str
    rollback_note: str
    frank_email_subject: str
    frank_email_body_path: str
    frank_email_html_body_path: str
    source_snapshot: dict[str, Any]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print proposal JSON to stdout.")
    parser.add_argument(
        "--proposal-dir",
        type=Path,
        default=PROPOSAL_DIR,
        help="Directory for proposal JSON and markdown artifacts.",
    )
    parser.add_argument(
        "--frank-draft-dir",
        type=Path,
        default=FRANK_DRAFT_DIR,
        help="Directory for rendered Frank approval email bodies.",
    )
    parser.add_argument(
        "--skip-historical-benchmark-refresh",
        action="store_true",
        help="Use existing historical benchmark results instead of refreshing traces and eval.",
    )
    return parser.parse_args()


def run_json_command(command: list[str], *, cwd: Path = ROOT) -> dict[str, Any]:
    proc = subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"{' '.join(command)} failed: {(proc.stderr or proc.stdout).strip()}")
    return json.loads(proc.stdout)


def run_command(command: list[str], *, cwd: Path = ROOT, timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, check=False, capture_output=True, text=True, timeout=timeout)


def refresh_historical_benchmark() -> dict[str, Any]:
    trace_run = run_command(
        [str(RECURSIVE_IMPROVE_PYTHON), str(HISTORICAL_BENCHMARK_RUNNER.name)],
        cwd=HISTORICAL_BENCHMARK_DIR,
    )
    if trace_run.returncode != 0:
        raise RuntimeError(
            f"historical trace generation failed: {(trace_run.stderr or trace_run.stdout).strip()}"
        )
    eval_run = run_command(
        [
            str(RECURSIVE_IMPROVE_BIN),
            "eval",
            "eval/historical-recommendation-traces",
            "--output-dir",
            "eval/historical-recommendation-benchmark",
        ],
        cwd=HISTORICAL_BENCHMARK_DIR,
    )
    if eval_run.returncode != 0:
        raise RuntimeError(f"historical benchmark eval failed: {(eval_run.stderr or eval_run.stdout).strip()}")
    return {
        "historical_benchmark_refreshed": True,
        "historical_trace_stdout_tail": trace_run.stdout[-500:],
        "historical_eval_stdout_tail": eval_run.stdout[-500:],
    }


def load_checker_snapshot(*, refresh_historical: bool = False) -> dict[str, Any]:
    refresh_proof: dict[str, Any] = {"historical_benchmark_refreshed": False}
    if refresh_historical:
        refresh_proof = refresh_historical_benchmark()

    with tempfile.TemporaryDirectory(prefix="recursive-proposal-") as temp_dir:
        temp_root = Path(temp_dir)
        service_json = temp_root / "service.json"
        truth_json = temp_root / "truth.json"

        subprocess.run(
            ["./scripts/service_parity_check.py", "--mode", "all", "--json", str(service_json)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            ["./scripts/task_flow_truth_drift_check.py", "--json", str(truth_json)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        service = json.loads(service_json.read_text(encoding="utf-8"))
        truth = json.loads(truth_json.read_text(encoding="utf-8"))

    registry = run_json_command(["./scripts/recursive_registry_lint.py", "--json"])
    historical_eval = {}
    if HISTORICAL_EVAL.exists():
        historical_eval = json.loads(HISTORICAL_EVAL.read_text(encoding="utf-8"))

    service_drift_items = [
        item
        for item in service.get("results", [])
        if item.get("status") in {"drift", "fix-failed"}
    ]
    truth_drifts = truth.get("drifts", [])
    historical_clean_success = (
        historical_eval.get("metrics", {})
        .get("clean_success_rate", {})
        .get("value")
    )

    historical_run_id = historical_eval.get("run_id") or ""
    historical_trace_count = int(historical_eval.get("trace_count") or 0)

    return {
        "service_parity_drift": len(service_drift_items),
        "service_parity_drift_items": service_drift_items[:10],
        "truth_drift_count": int(truth.get("drift_count") or 0),
        "truth_drifts": truth_drifts[:10],
        "registry_ok": bool(registry.get("ok")),
        "coverage_ok": any(
            item.get("name") == "recursive_checker_coverage" and item.get("status") == "ok"
            for item in registry.get("results", [])
        ),
        "historical_clean_success": historical_clean_success,
        "historical_benchmark_refreshed": bool(refresh_proof.get("historical_benchmark_refreshed")),
        "historical_benchmark_run_id": historical_run_id,
        "historical_benchmark_trace_count": historical_trace_count,
        "service_results_checked": len(service.get("results", [])),
        "truth_rows_scanned": int(truth.get("task_flow_rows_scanned") or 0),
        "truth_managed_sessions": int(truth.get("managed_sessions") or 0),
        "proof_closeout_issues": int(truth.get("proof_closeout_issues") or 0),
        **refresh_proof,
    }


def choose_action(snapshot: dict[str, Any]) -> tuple[str, bool, str, str, str]:
    historical_ok = snapshot.get("historical_clean_success") in {1, 1.0, None}
    if not snapshot["registry_ok"] or not snapshot["coverage_ok"]:
        return (
            "repair-registry-contract",
            True,
            "low",
            "registry-metadata-fix",
            "Registry or coverage validation is failing, so later recursive readbacks are not trustworthy.",
        )
    if int(snapshot["service_parity_drift"]) > 0:
        return (
            "fix-service-parity-drift",
            True,
            "medium",
            "source-runtime-parity-fix",
            f"Service parity reports {snapshot['service_parity_drift']} drift item(s).",
        )
    if int(snapshot["truth_drift_count"]) > 0:
        return (
            "repair-truth-drift",
            True,
            "medium",
            "truth-drift-single-item-repair",
            f"Task Flow truth drift reports {snapshot['truth_drift_count']} contradiction item(s).",
        )
    if not historical_ok:
        return (
            "repair-recommendation-benchmark",
            True,
            "low",
            "recommendation-corpus-fix",
            "Historical recommendation benchmark is not clean.",
        )
    return (
        "monitor-recursive-lane",
        False,
        "low",
        "no-op-monitoring",
        "Recursive checkers and recommendation benchmarks are currently clean.",
    )


def proposal_id_for(action: str, created_at: str) -> str:
    stamp = created_at.replace("-", "").replace(":", "").replace(" ", "-")[:15]
    return f"recursive-proposal-{stamp}-{action}"


def snapshot_context_lines(snapshot: dict[str, Any]) -> list[str]:
    lines = [
        f"Service parity drift: {snapshot.get('service_parity_drift')}",
        f"Truth drift count: {snapshot.get('truth_drift_count')}",
        f"Registry lint: {'ok' if snapshot.get('registry_ok') else 'not ok'}",
        f"Coverage manifest: {'ok' if snapshot.get('coverage_ok') else 'not ok'}",
        f"Historical recommendation benchmark: {snapshot.get('historical_clean_success')}",
    ]
    truth_drifts = snapshot.get("truth_drifts") or []
    if truth_drifts:
        first = truth_drifts[0]
        lines.append(f"Current drift kind: {first.get('kind', 'unknown')}")
        detail = str(first.get("detail") or "").strip()
        if detail:
            lines.append(f"Current drift detail: {detail}")
    return lines


def build_email_body(proposal: Proposal) -> str:
    decision_line = (
        "Reply YES to approve this fix, or NO to leave it as a recorded recommendation."
        if proposal.approval_required
        else "No approval is required right now; this is a monitoring readback."
    )
    context = "\n".join(f"- {line}" for line in snapshot_context_lines(proposal.source_snapshot))
    return (
        "Robert,\n\n"
        f"Point: Frank recommends approving `{proposal.recommended_action}` for the recursive improvement lane.\n\n"
        "Why this is coming to you:\n"
        f"{proposal.why_now} The proposal queue is approval-gated, so Codex will not execute this repair until you answer yes.\n\n"
        "Current readback:\n"
        f"{context}\n\n"
        "What approval allows:\n"
        f"{proposal.what_changes_if_approved}\n\n"
        "Boundaries:\n"
        f"{proposal.what_will_not_change}\n\n"
        f"Risk class: {proposal.risk_class}\n"
        f"Allowed fix class: {proposal.allowed_fix_class}\n\n"
        "Proof required after execution:\n"
        f"{proposal.proof_required}\n\n"
        "Rollback/stop rule:\n"
        f"{proposal.rollback_note}\n\n"
        f"Decision needed: {decision_line}\n"
    )


def build_email_html(proposal: Proposal) -> str:
    def esc(value: object) -> str:
        return html.escape(str(value or ""))

    context_items = "\n".join(
        f"<li>{esc(line)}</li>" for line in snapshot_context_lines(proposal.source_snapshot)
    )
    decision = (
        "Reply <strong>YES</strong> to approve this fix, or <strong>NO</strong> to leave it as a recorded recommendation."
        if proposal.approval_required
        else "No approval is required right now; this is a monitoring readback."
    )
    return f"""<!doctype html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; color: #1f2933; line-height: 1.45; margin: 0; padding: 0;">
  <div style="max-width: 760px; margin: 0 auto; padding: 20px 0;">
    <p>Robert,</p>
    <h2 style="font-size: 20px; margin: 0 0 12px;">Approval needed: {esc(proposal.recommended_action)}</h2>
    <p style="font-size: 16px; margin: 0 0 18px;"><strong>Point:</strong> Frank recommends approving this bounded recursive-improvement repair. Codex will not execute it unless you reply yes.</p>

    <h3 style="font-size: 15px; margin: 20px 0 8px;">Why this is coming to you</h3>
    <p style="margin: 0 0 14px;">{esc(proposal.why_now)}</p>

    <h3 style="font-size: 15px; margin: 20px 0 8px;">Current readback</h3>
    <ul style="margin: 0 0 14px; padding-left: 22px;">
      {context_items}
    </ul>

    <h3 style="font-size: 15px; margin: 20px 0 8px;">What approval allows</h3>
    <p style="margin: 0 0 14px;">{esc(proposal.what_changes_if_approved)}</p>

    <h3 style="font-size: 15px; margin: 20px 0 8px;">Boundaries</h3>
    <p style="margin: 0 0 14px;">{esc(proposal.what_will_not_change)}</p>

    <h3 style="font-size: 15px; margin: 20px 0 8px;">Risk and proof</h3>
    <ul style="margin: 0 0 14px; padding-left: 22px;">
      <li><strong>Risk class:</strong> {esc(proposal.risk_class)}</li>
      <li><strong>Allowed fix class:</strong> {esc(proposal.allowed_fix_class)}</li>
      <li><strong>Proof after execution:</strong> {esc(proposal.proof_required)}</li>
      <li><strong>Stop rule:</strong> {esc(proposal.rollback_note)}</li>
    </ul>

    <p style="font-size: 16px; margin: 22px 0 0;"><strong>Decision needed:</strong> {decision}</p>
  </div>
</body>
</html>
"""


def build_markdown(proposal: Proposal) -> str:
    lines = [
        f"# Recursive Proposal {proposal.proposal_id}",
        "",
        f"- Created: {proposal.created_at}",
        f"- Recommended action: `{proposal.recommended_action}`",
        f"- Approval required: `{proposal.approval_required}`",
        f"- Risk class: `{proposal.risk_class}`",
        f"- Allowed fix class: `{proposal.allowed_fix_class}`",
        "",
        "## Why Now",
        "",
        proposal.why_now,
        "",
        "## Approval Packet",
        "",
        f"- What changes if approved: {proposal.what_changes_if_approved}",
        f"- What will not change: {proposal.what_will_not_change}",
        f"- Proof required: {proposal.proof_required}",
        f"- Rollback note: {proposal.rollback_note}",
        "",
        "## Frank Email",
        "",
        f"- Subject: `{proposal.frank_email_subject}`",
        f"- Body path: `{proposal.frank_email_body_path}`",
        f"- HTML body path: `{proposal.frank_email_html_body_path}`",
        "",
        "## Source Snapshot",
        "",
        "```json",
        json.dumps(proposal.source_snapshot, indent=2, sort_keys=True),
        "```",
    ]
    return "\n".join(lines) + "\n"


def build_proposal(snapshot: dict[str, Any], proposal_dir: Path, frank_draft_dir: Path) -> Proposal:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    action, approval_required, risk_class, fix_class, why_now = choose_action(snapshot)
    proposal_id = proposal_id_for(action, now)
    frank_body_path = frank_draft_dir / f"{proposal_id}.txt"
    frank_html_body_path = frank_draft_dir / f"{proposal_id}.html"

    if action == "repair-truth-drift":
        first = (snapshot.get("truth_drifts") or [{}])[0]
        title = first.get("title") or "the remaining truth-drift item"
        change = f"Investigate and repair the single contradiction `{title}` through the approved Task Flow / Workspaceboard path."
        no_change = "No broad Task Flow closeout mutation, mailbox action, service restart, credential work, or OPS/Portal mutation."
        proof = "`./scripts/task_flow_truth_drift_check.py --fail-on-drift` returns zero drift, or the exact blocker is recorded."
    elif action == "fix-service-parity-drift":
        change = "Repair only the reported source/runtime parity drift items that are writable and do not require service restarts."
        no_change = "No LaunchDaemon edits, service restarts, mailbox actions, credential work, or broad runtime redeploy."
        proof = "`./scripts/service_parity_check.py --mode all --fail-on-drift` returns zero drift."
    elif action == "repair-registry-contract":
        change = "Update recursive checker registry or coverage metadata so validation passes."
        no_change = "No live service, mailbox, OPS, Portal, or Task Flow data mutation."
        proof = "`./scripts/recursive_registry_lint.py --json` returns `ok: true`."
    elif action == "repair-recommendation-benchmark":
        change = "Repair the recommendation corpus or benchmark logic so historical replay matches expected outcomes."
        no_change = "No live service, mailbox, OPS, Portal, or Task Flow data mutation."
        proof = "`recursive-improve eval eval/historical-recommendation-traces --output-dir eval/historical-recommendation-benchmark` returns `clean_success_rate=100%`."
    else:
        change = "No change proposed. Keep the recursive lane in monitoring mode."
        no_change = "No execution or approval request will be sent for this no-op monitor proposal."
        proof = "Current checker readback remains clean."

    proposal = Proposal(
        proposal_id=proposal_id,
        created_at=now,
        recommended_action=action,
        approval_required=approval_required,
        risk_class=risk_class,
        allowed_fix_class=fix_class,
        why_now=why_now,
        what_changes_if_approved=change,
        what_will_not_change=no_change,
        proof_required=proof,
        rollback_note="If verification fails, stop and record one exact blocker; do not continue into a broader repair class.",
        frank_email_subject=f"Approval needed: {action}" if approval_required else f"Recursive monitor: {action}",
        frank_email_body_path=str(frank_body_path),
        frank_email_html_body_path=str(frank_html_body_path),
        source_snapshot=snapshot,
    )
    return proposal


def write_outputs(proposal: Proposal, proposal_dir: Path, frank_draft_dir: Path) -> None:
    proposal_dir.mkdir(parents=True, exist_ok=True)
    frank_draft_dir.mkdir(parents=True, exist_ok=True)

    json_path = proposal_dir / f"{proposal.proposal_id}.json"
    md_path = proposal_dir / f"{proposal.proposal_id}.md"
    email_path = Path(proposal.frank_email_body_path)
    html_email_path = Path(proposal.frank_email_html_body_path)

    json_path.write_text(json.dumps(asdict(proposal), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(build_markdown(proposal), encoding="utf-8")
    email_path.write_text(build_email_body(proposal), encoding="utf-8")
    html_email_path.write_text(build_email_html(proposal), encoding="utf-8")

    QUEUE_LOG.parent.mkdir(parents=True, exist_ok=True)
    with QUEUE_LOG.open("a", encoding="utf-8") as handle:
        handle.write(
            json.dumps(
                {
                    "proposal_id": proposal.proposal_id,
                    "created_at": proposal.created_at,
                    "recommended_action": proposal.recommended_action,
                    "approval_required": proposal.approval_required,
                    "risk_class": proposal.risk_class,
                    "allowed_fix_class": proposal.allowed_fix_class,
                    "proposal_json": str(json_path),
                    "proposal_md": str(md_path),
                    "frank_email_body": str(email_path),
                    "frank_email_html_body": str(html_email_path),
                },
                sort_keys=True,
            )
            + "\n"
        )


def main() -> int:
    args = parse_args()
    snapshot = load_checker_snapshot(refresh_historical=not args.skip_historical_benchmark_refresh)
    proposal = build_proposal(snapshot, args.proposal_dir, args.frank_draft_dir)
    write_outputs(proposal, args.proposal_dir, args.frank_draft_dir)
    if args.json:
        print(json.dumps(asdict(proposal), indent=2, sort_keys=True))
    else:
        print(f"proposal_id={proposal.proposal_id}")
        print(f"recommended_action={proposal.recommended_action}")
        print(f"approval_required={proposal.approval_required}")
        print(f"risk_class={proposal.risk_class}")
        print(f"frank_email_body={proposal.frank_email_body_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
