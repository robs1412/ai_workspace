# Recursive Proposal recursive-proposal-20260608-223415-review-source-backed-proof-repair-candidates

- Created: 2026-06-08 22:34:15 CDT
- Recommended action: `review-source-backed-proof-repair-candidates`
- Approval required: `True`
- Risk class: `low`
- Allowed fix class: `source-backed-proof-repair-candidate`

## Why Now

The proof candidate detector found 5 source-backed Task Flow repair candidate(s).

## Approval Packet

- What changes if approved: Review `taskflow-5cfd58716334576b` from `failed_approved_send_artifact` and, if approved, perform only the lane-aware Task Flow proof repair described by the candidate source metadata.
- What will not change: No generic auto-mutation, mailbox send, message-body copying, service restart, credential work, or OPS/Portal mutation. The detector itself remains read-only.
- Proof required: `./scripts/task_flow_proof_repair_candidates.py --print-json` shows the candidate source, and post-repair `./scripts/task_flow_truth_drift_check.py --fail-on-drift` keeps drift at zero.
- Rollback note: If verification fails, stop and record one exact blocker; do not continue into a broader repair class.

## Frank Email

- Subject: `Approval needed: review-source-backed-proof-repair-candidates`
- Body path: `/Users/werkstatt/ai_workspace/frank/drafts/recursive-proposals/recursive-proposal-20260608-223415-review-source-backed-proof-repair-candidates.txt`
- HTML body path: `/Users/werkstatt/ai_workspace/frank/drafts/recursive-proposals/recursive-proposal-20260608-223415-review-source-backed-proof-repair-candidates.html`

## Source Snapshot

```json
{
  "coverage_ok": true,
  "historical_benchmark_refreshed": false,
  "historical_benchmark_run_id": "4b1934a45c5b",
  "historical_benchmark_trace_count": 7,
  "historical_clean_success": 1.0,
  "proof_closeout_issues": 7,
  "proof_issue_class_counts": {
    "blocked_needs_owner_question_proof": 5
  },
  "proof_issue_count": 5,
  "proof_issue_samples": [
    {
      "dedupe_key": "taskflow-5cfd58716334576b",
      "detail": "blocked row is routed-needs-owner-question and needs owner-question/blocker proof",
      "kind": "blocked_needs_owner_question_proof",
      "missing_fields": [
        "owner_lane",
        "clarification_or_blocker_email"
      ],
      "owner_lane": "",
      "session_id": "",
      "severity": "blocked",
      "title": "taskflow-5cfd58716334576b"
    },
    {
      "dedupe_key": "taskflow-bf15206feb1385cf",
      "detail": "blocked row is routed-needs-owner-question and needs owner-question/blocker proof",
      "kind": "blocked_needs_owner_question_proof",
      "missing_fields": [
        "owner_lane",
        "clarification_or_blocker_email"
      ],
      "owner_lane": "",
      "session_id": "",
      "severity": "blocked",
      "title": "taskflow-bf15206feb1385cf"
    },
    {
      "dedupe_key": "taskflow-a151053058c9c6c0",
      "detail": "blocked row is routed-needs-owner-question and needs owner-question/blocker proof",
      "kind": "blocked_needs_owner_question_proof",
      "missing_fields": [
        "owner_lane",
        "clarification_or_blocker_email"
      ],
      "owner_lane": "",
      "session_id": "",
      "severity": "blocked",
      "title": "taskflow-a151053058c9c6c0"
    },
    {
      "dedupe_key": "taskflow-760a7508ffeabfe5",
      "detail": "blocked row is routed-needs-owner-question and needs owner-question/blocker proof",
      "kind": "blocked_needs_owner_question_proof",
      "missing_fields": [
        "owner_lane",
        "clarification_or_blocker_email"
      ],
      "owner_lane": "",
      "session_id": "",
      "severity": "blocked",
      "title": "taskflow-760a7508ffeabfe5"
    },
    {
      "dedupe_key": "taskflow-1db47dff91264646",
      "detail": "blocked row is routed-needs-owner-question and needs owner-question/blocker proof",
      "kind": "blocked_needs_owner_question_proof",
      "missing_fields": [
        "owner_lane",
        "clarification_or_blocker_email"
      ],
      "owner_lane": "",
      "session_id": "",
      "severity": "blocked",
      "title": "taskflow-1db47dff91264646"
    }
  ],
  "proof_repair_candidate_count": 5,
  "proof_repair_candidates": [
    {
      "completion_or_blocker_email": "Failed approved-send artifact exists at naomi-weekly-finance-june8-corrected-pdfs-20260608.failed-1780966535.json; no sent Message-ID was produced. Review and resend only through the approved sender path.",
      "confidence": "source-backed",
      "dedupe_key": "taskflow-5cfd58716334576b",
      "intake_channel": "approved-send:nationaloutreach",
      "mutation_allowed": false,
      "next_update": "sent; recovered from runtime failure with Sent Mail readback",
      "ops_portal_or_domain_task": "OPS 368746",
      "owner_lane": "naomi-finance",
      "proof_kind": "failed_approved_send_artifact",
      "responsible_worker_or_persona": "naomi.stern@kovaldistillery.com",
      "source_event": "failed_send_artifact",
      "source_logged_at": "",
      "source_path": "/Users/admin/.nationaloutreach-launch/state/failed/naomi-weekly-finance-june8-corrected-pdfs-20260608.failed-1780966535.json",
      "status": "blocked",
      "subject": "Weekly finance update with QBO PDFs - June 8",
      "verification_readback": "Failed artifact metadata readback: owner_lane=naomi-finance; responsible_worker_or_persona=naomi.stern@kovaldistillery.com; ops_portal_or_domain_task=OPS 368746."
    },
    {
      "completion_or_blocker_email": "Failed approved-send artifact exists at vanessa-sonat-tasting-selection-cancellation-rules-taskflow-owner-reply-a02995c7547f63de.failed-1780958297.json; no sent Message-ID was produced. Review and resend only through the approved sender path.",
      "confidence": "source-backed",
      "dedupe_key": "taskflow-760a7508ffeabfe5",
      "intake_channel": "approved-send:nationaloutreach",
      "mutation_allowed": false,
      "next_update": "Same-thread Vanessa confirmation queued for approved send cycle.",
      "ops_portal_or_domain_task": "taskflow-owner-reply-a02995c7547f63de / Sonat tasting-selection and cancellation rules",
      "owner_lane": "outreach-coordinator",
      "proof_kind": "failed_approved_send_artifact",
      "responsible_worker_or_persona": "vanessa.sterling@kovaldistillery.com",
      "source_event": "failed_send_artifact",
      "source_logged_at": "",
      "source_path": "/Users/admin/.nationaloutreach-launch/state/failed/vanessa-sonat-tasting-selection-cancellation-rules-taskflow-owner-reply-a02995c7547f63de.failed-1780958297.json",
      "status": "blocked",
      "subject": "Re: Instructions needed: tasting selection and cancellation automation",
      "verification_readback": "Failed artifact metadata readback: owner_lane=outreach-coordinator; responsible_worker_or_persona=vanessa.sterling@kovaldistillery.com; ops_portal_or_domain_task=taskflow-owner-reply-a02995c7547f63de / Sonat tasting-selection and cancellation rules."
    },
    {
      "completion_or_blocker_email": "Failed approved-send artifact exists at status-reply-taskflow-6ea601be2d0823f4-ravenswood-on-tap.retry-20260608-1728.failed-1780957848.json; no sent Message-ID was produced. Review and resend only through the approved sender path.",
      "confidence": "source-backed",
      "dedupe_key": "taskflow-1db47dff91264646",
      "intake_channel": "approved-send:nationaloutreach",
      "mutation_allowed": false,
      "next_update": "Ravenswood On Tap remains recorded as OPS planning placeholders until exact coverage times and staffing details are confirmed.",
      "ops_portal_or_domain_task": "OPS outreach events 866, 867",
      "owner_lane": "outreach-coordinator",
      "proof_kind": "failed_approved_send_artifact",
      "responsible_worker_or_persona": "vanessa.sterling@kovaldistillery.com",
      "source_event": "failed_send_artifact",
      "source_logged_at": "",
      "source_path": "/Users/admin/.nationaloutreach-launch/state/failed/status-reply-taskflow-6ea601be2d0823f4-ravenswood-on-tap.retry-20260608-1728.failed-1780957848.json",
      "status": "blocked",
      "subject": "Re: Fwd: Ravenswood On Tap 2026 - Drinks",
      "verification_readback": "Failed artifact metadata readback: owner_lane=outreach-coordinator; responsible_worker_or_persona=vanessa.sterling@kovaldistillery.com; ops_portal_or_domain_task=OPS outreach events 866, 867."
    },
    {
      "completion_or_blocker_email": "Failed approved-send artifact exists at benjamin-bottles-cans-too-ops1055-completion.failed-1780935440.json; no sent Message-ID was produced. Review and resend only through the approved sender path.",
      "confidence": "source-backed",
      "dedupe_key": "taskflow-3981bd77dabf07ce",
      "intake_channel": "approved-send:nationaloutreach",
      "mutation_allowed": false,
      "next_update": "Complete after same-thread link reply is sent.",
      "ops_portal_or_domain_task": "OPS Outreach event 1055 / shift 5584 / Google UID ops-outreach-1055@koval-distillery.com",
      "owner_lane": "outreach-coordinator",
      "proof_kind": "failed_approved_send_artifact",
      "responsible_worker_or_persona": "vanessa.sterling@kovaldistillery.com",
      "source_event": "failed_send_artifact",
      "source_logged_at": "",
      "source_path": "/Users/admin/.nationaloutreach-launch/state/failed/benjamin-bottles-cans-too-ops1055-completion.failed-1780935440.json",
      "status": "blocked",
      "subject": "Re: New tasting",
      "verification_readback": "Failed artifact metadata readback: owner_lane=outreach-coordinator; responsible_worker_or_persona=vanessa.sterling@kovaldistillery.com; ops_portal_or_domain_task=OPS Outreach event 1055 / shift 5584 / Google UID ops-outreach-1055@koval-distillery.com."
    },
    {
      "completion_or_blocker_email": "Failed approved-send artifact exists at wild-onion-shift-time-update-ops1054-20260608.failed-1780929775.json; no sent Message-ID was produced. Review and resend only through the approved sender path.",
      "confidence": "source-backed",
      "dedupe_key": "taskflow-1513f992055a281d",
      "intake_channel": "approved-send:nationaloutreach",
      "mutation_allowed": false,
      "next_update": "sent",
      "ops_portal_or_domain_task": "OPS event 1054 / TrackTime shift 5582 / Google outreach UID ops-outreach-1054@koval-distillery.com",
      "owner_lane": "outreach-coordinator",
      "proof_kind": "failed_approved_send_artifact",
      "responsible_worker_or_persona": "vanessa.sterling@kovaldistillery.com",
      "source_event": "failed_send_artifact",
      "source_logged_at": "",
      "source_path": "/Users/admin/.nationaloutreach-launch/state/failed/wild-onion-shift-time-update-ops1054-20260608.failed-1780929775.json",
      "status": "blocked",
      "subject": "Re: Wild Onion Market 2nd Anniversary Event",
      "verification_readback": "Failed artifact metadata readback: owner_lane=outreach-coordinator; responsible_worker_or_persona=vanessa.sterling@kovaldistillery.com; ops_portal_or_domain_task=OPS event 1054 / TrackTime shift 5582 / Google outreach UID ops-outreach-1054@koval-distillery.com."
    }
  ],
  "registry_ok": true,
  "service_parity_drift": 0,
  "service_parity_drift_items": [],
  "service_results_checked": 93,
  "truth_drift_count": 0,
  "truth_drifts": [],
  "truth_managed_sessions": 108,
  "truth_rows_scanned": 500
}
```
