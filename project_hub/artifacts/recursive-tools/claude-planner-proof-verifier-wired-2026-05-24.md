# Claude Planner Proof Verifier Wired

Timestamp: 2026-05-24 15:25 CDT.

Papers: `https://papers.koval.lan/542f8733-3aef-4cde-ad65-0da61d6b9781`

## Decision

Codex now has a read-only verifier for the planned Claude Planner `/proof` export and AI Health now reports that verifier on the normal cadence.

This keeps the recursive bridge honest: `/api/tasks/{id}` and `/api/tasks/{id}/chain` remain context-only, while only `/api/tasks/{id}/proof` or `/api/proof?plan_guid={guid}` can satisfy cross-system Planner proof.

## Implementation

- Standalone checker: `scripts/claude_planner_proof_check.py`
- AI Health integration: `scripts/ai_health_check.py`
- Default Planner base URL: `https://planner.koval.lan`
- Default task id: `1725`
- Optional plan-guid mode: `--plan-guid <guid>` maps to `/api/proof?plan_guid=<guid>`
- AI Health output artifacts:
  - `tmp/ai-health-manager/claude-planner-proof-latest.json`
  - `tmp/ai-health-manager/claude-planner-proof-latest.md`
  - `tmp/ai-health-manager/latest.json`
  - `tmp/ai-health-manager/latest.md`

## Verifier Rules

- Accept only dedicated `/proof` routes as proof.
- Reject volatile fields anywhere in the payload:
  - `previous_status`
  - `session_id`
  - `context_summary`
- Require stable task fields:
  - `id`
  - `status`
  - `tags`
- Count proof-comment surfaces from proof, verification, delivery, or comments arrays.

## Verification

Compile check passed:

```bash
python3.13 -m py_compile scripts/claude_planner_proof_check.py scripts/ai_health_check.py
```

Direct checker readback:

```json
{
  "status": "not-ready",
  "http_status": 0,
  "proof_url": "https://planner.koval.lan/api/tasks/1725/proof",
  "context_url": "https://planner.koval.lan/api/tasks/1725",
  "reason": "<urlopen error timed out>",
  "forbidden_fields": []
}
```

AI Health dry-run readback:

```json
{
  "claude_planner_proof": "not-ready",
  "claude_planner_proof_http_status": 0,
  "claude_planner_proof_forbidden_fields": 0,
  "claude_planner_proof_comments": 0,
  "recursive_proposals": "passed"
}
```

Canonical status now includes:

```text
Claude Planner proof not-ready
```

## Current State

The verifier is wired and reporting, but Planner proof is not yet proven from this workstation. The current blocker is endpoint reachability or endpoint availability: the local read times out at `https://planner.koval.lan/api/tasks/1725/proof`.

This is not a failure of the verifier wiring. It means Codex should continue to report `not-ready` until Claude task `#1725` exposes `/proof` and this workstation can read it.

## Next Step

When Claude task `#1725` is complete or Planner connectivity is fixed, rerun:

```bash
python3.13 scripts/claude_planner_proof_check.py --timeout-seconds 8 --json tmp/ai-health-manager/claude-planner-proof-latest.json --report tmp/ai-health-manager/claude-planner-proof-latest.md --fail-on-not-ready
```

Expected pass condition: HTTP JSON from `/proof`, no volatile fields, required stable fields present, and proof comments visible when available.
