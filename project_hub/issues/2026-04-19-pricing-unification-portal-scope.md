# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260419-PRICING-UNIFICATION-PORTAL-01`
- Date Opened: 2026-04-19
- Date Completed:
- Owner: Codex / OPS
- Priority: High
- Status: scoped and shared with Sonat; OPS/Portal task ID pending task-create auth recovery

## Scope

Robert requested a large OPS/Codex TODO for pricing unification and using KOVAL pricing in the Portal, plus a Sonat-facing share.

This slice created the planning scope and shared the concise business summary with Sonat. It did not implement pricing logic or mutate pricing data.

## Symptoms

KOVAL pricing appears to need a unified source of truth before Portal surfaces, sales workflows, reports, imports, or manual processes can reliably use the same approved pricing data.

## Root Cause

Not applicable yet. This is a planning and alignment slice. Discovery must inventory current pricing sources, Portal pricing surfaces, owners, exception rules, and approval paths before implementation.

## Repo Logs

### ops

- Repo Log ID: `ops-pricing-unification-portal-2026-04-19`
- Commit SHA:
- Commit Date:
- Change Summary: Added local scope artifact `docs/2026-04-19-pricing-unification-portal-scope.md` defining the pricing source inventory, Portal surface inventory, canonical pricing model, migration/backfill plan, verification/UAT plan, Sonat/sales communication needs, and production approval gates.

### ai_workspace / avignon

- Repo Log ID: `ops-pricing-unification-portal-2026-04-19`
- Commit SHA:
- Commit Date:
- Change Summary: Added Avignon Sonat-facing draft at `avignon/drafts/sonat-pricing-unification-portal-scope-2026-04-19.txt` and sent it to Sonat through the approved Avignon sender path.

## Verification Notes

- Scope artifact exists at `/Users/werkstatt/ops/docs/2026-04-19-pricing-unification-portal-scope.md`.
- OPS TODO/HANDOFF updated with local task key and Sonat share status.
- Avignon email sent:
  - To: Sonat
  - Subject: `Pricing unification and Portal pricing scope`
  - Task ID: `ops-pricing-unification-portal-2026-04-19`
  - Message-ID: `<177661177342.12519.5475020165538054926@kovaldistillery.com>`
  - No Cc/Bcc
- Silent OPS/Portal task creation was attempted through the existing helper and a session-backed path, but no task ID was created because the current Portal task-create auth path failed before creation.
- No production pricing data, Portal pricing behavior, customer terms, credentials, deploy, push, live pull, or pricing/CRM records were changed.

## Rollback Plan

If the scope should be withdrawn, mark the local OPS TODO/HANDOFF/project-hub entries superseded and send Sonat a brief correction through Avignon. No pricing or Portal rollback is needed because no pricing data or Portal behavior changed.

If an OPS/Portal task is later created in duplicate, keep one canonical task and close the duplicate silently with notifications disabled.

## Follow-Ups

- Recover or choose an approved OPS/Portal task-registration path, then create the real Codex-owned OPS/Portal task and update this log with the task ID.
- Start read-only discovery: current pricing sources, Portal pricing surfaces, owners, exception rules, and high-priority sales workflows.
- Ask Sonat to identify the current business-reference pricing source and pilot sales users.
- Do not perform production pricing inserts, updates, deletes, imports, or Portal behavior cutover without explicit Robert approval.
