# Recursive Proposal recursive-proposal-20260524-134350-repair-truth-drift

- Created: 2026-05-24 13:43:50
- Recommended action: `repair-truth-drift`
- Approval required: `True`
- Risk class: `medium`
- Allowed fix class: `truth-drift-single-item-repair`

## Why Now

Task Flow truth drift reports 1 contradiction item(s).

## Approval Packet

- What changes if approved: Investigate and repair the single contradiction `Scheduler route candidates present` through the approved Task Flow / Workspaceboard path.
- What will not change: No broad Task Flow closeout mutation, mailbox action, service restart, credential work, or OPS/Portal mutation.
- Proof required: `./scripts/task_flow_truth_drift_check.py --fail-on-drift` returns zero drift, or the exact blocker is recorded.
- Rollback note: If verification fails, stop and record one exact blocker; do not continue into a broader repair class.

## Frank Email

- Subject: `Approval needed: repair-truth-drift`
- Body path: `/Users/werkstatt/ai_workspace/frank/drafts/recursive-proposals/recursive-proposal-20260524-134350-repair-truth-drift.txt`
- HTML body path: `/Users/werkstatt/ai_workspace/frank/drafts/recursive-proposals/recursive-proposal-20260524-134350-repair-truth-drift.html`
- Status: `sent`
- To: `robert@kovaldistillery.com`
- Message-ID: `<177964828163.12510.14353964488768279452@kovaldistillery.com>`
- Sent at: `Sun, 24 May 2026 13:44:41 -0500`
- Template note: upgraded after first send to include richer plain-text context and a formatted HTML body for future proposal emails.

## Decision State

- State: `superseded_by_clean_monitor`
- Decision recorded at: `2026-05-24 13:53:44 CDT`
- Superseded by: `recursive-proposal-20260524-134813-monitor-recursive-lane`
- Note: Superseded by a later clean monitor proposal; no execution remains.

## Source Snapshot

```json
{
  "coverage_ok": true,
  "historical_clean_success": 1.0,
  "proof_closeout_issues": 15,
  "registry_ok": true,
  "service_parity_drift": 0,
  "service_parity_drift_items": [],
  "service_results_checked": 91,
  "truth_drift_count": 1,
  "truth_drifts": [
    {
      "dedupe_key": "",
      "detail": "1 scheduler route candidates in task-flow-report",
      "kind": "scheduler_route_candidates_present",
      "path": "",
      "session_id": "",
      "severity": "medium",
      "title": "Scheduler route candidates present"
    }
  ],
  "truth_managed_sessions": 194,
  "truth_rows_scanned": 500
}
```
