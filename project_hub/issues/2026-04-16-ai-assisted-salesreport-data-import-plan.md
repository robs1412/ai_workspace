# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260416-SALESREPORT-AI-DATA-IMPORT-PLAN-01`
- Date Opened: `2026-04-16`
- Date Completed: `2026-04-16 17:31 CDT`
- Owner: `Codex`
- Priority: `Medium`
- Status: `Completed`

## Scope

- Plan an AI-assisted workflow for Salesreport data imports currently handled manually from XLS and other source files.
- Define a deterministic preflight that can run before any AI step.
- Identify safe AI assist points that improve speed and accuracy without giving AI write authority.
- Define approval gates before credentials, production data, code changes, emails, commits, or live imports.
- Define the first no-write prototype and owner workspace.

## Owner Workspace

- Primary owner workspace: `ws sales`.
- Planning and policy coordination: `ws ai`.
- Source-side collaborators:
  - `ws importer` only if future work touches shared importer/account import mechanics.
  - `ws bid` only if future work touches BID ETL or BID refresh cadence.
- Role routing:
  - Sales Analyst for data meaning, expected columns, account matching rules, and variance review.
  - Code and Git Manager before any future code-producing task in `salesreport`, `importer`, or `bid`.
  - Security Guard if production credentials, auth/session state, sensitive source files, mailbox attachments, or live database writes enter scope.

## Deterministic Preflight

The preflight must run before any AI enrichment or classification. It should be reproducible, logged, and safe to repeat.

1. Intake inventory
   - Record file name, source owner, received date, report period, distributor/source system, and intended target report/import type.
   - Store only non-secret metadata in planning logs.
   - Do not copy raw private files into git or chat.

2. File integrity
   - Capture local checksum, file size, sheet names, row counts, column counts, and detected encoding/date formats.
   - Reject password-protected, corrupted, macro-enabled, or unexpected binary formats until a human approves handling.

3. Schema fingerprint
   - Normalize headers deterministically.
   - Compare against an approved template registry for each source type.
   - Flag added, missing, renamed, duplicate, hidden, or formula-derived columns.

4. Data quality checks
   - Validate required fields, date ranges, numeric coercion, negative values, blank key fields, duplicate rows, outlier quantities/dollars, and known distributor/account identifiers.
   - Produce a machine-readable exceptions file and a human-readable summary.

5. Target mapping dry run
   - Map source columns to proposed target fields without writing to Salesreport, CRM, BID, importer, or any production table.
   - Record match confidence bands and unresolved identifiers.

6. Reconciliation baseline
   - Compare aggregate totals against source totals where available.
   - Compare period/source/account totals against prior imports or saved reports only in read-only mode after explicit approval for production data access.

## Safe AI Assist Points

AI may assist only after deterministic preflight produces bounded inputs.

- Header/template suggestions: propose likely mappings for renamed or unfamiliar columns, with the deterministic schema diff preserved as the source of truth.
- Exception explanation: summarize why rows failed validation and group similar failures for human review.
- Account/distributor matching candidates: suggest likely matches for unresolved names using read-only exported reference data, never direct production lookup unless approved.
- Transformation notes: generate a proposed import recipe in prose or JSON for human review.
- Test-case generation: propose edge cases based on the schema diff and exceptions.
- Operator checklist drafting: produce a concise checklist for Julia or the import owner to review before any write.

AI must not:

- Directly mutate production Salesreport, CRM, BID, importer, mailbox, Drive, or database records.
- Infer or fabricate missing sales quantities, dollar values, dates, account IDs, or distributor identifiers.
- Read, print, summarize, or store credentials or secret-bearing files.
- Send emails or notifications.
- Commit or deploy code.

## Approval Gates

Approval is required before each boundary below.

- Raw source data access: human approval required before reading actual XLS/CSV contents that may contain customer, account, distributor, pricing, or employee-sensitive data.
- Production read access: human approval required before querying live Salesreport/CRM/BID/importer databases for reference matching or reconciliation.
- Credential use: Security Guard review and explicit approval required before using credentials, tokens, SSH, VPN, Keychain, mailbox, Drive, or database secrets.
- Code changes: Code and Git Manager preflight required before modifying `salesreport`, `importer`, or `bid`; no commit/push/deploy without explicit follow-up scope.
- Any write/import: human approval required after reviewing the no-write dry-run output, exception summary, reconciliation totals, rollback plan, and owner sign-off.
- External communication: explicit approval required before sending any email or notification about import results.
- Production scheduling/automation: explicit approval required before adding recurring jobs, daemons, LaunchAgents, cron entries, or background polling.

## First No-Write Prototype

Goal: prove whether AI assistance improves speed and accuracy without touching production data or code.

Inputs:

- One sanitized or synthetic XLS/CSV example that mirrors a real Salesreport import shape.
- A local template registry file describing expected source headers and target fields.
- A local output folder excluded from git for generated dry-run artifacts if raw or sensitive data is ever used.

Prototype behavior:

1. Run deterministic preflight on the sample file.
2. Emit `schema-diff.json`, `validation-exceptions.json`, and `dry-run-summary.md`.
3. Ask AI only to summarize exceptions, propose header mappings, and draft a human checklist from those deterministic artifacts.
4. Produce a no-write import recipe for review.
5. Compare AI suggestions against a human-reviewed answer key or Julia's expected manual import steps.

Prototype acceptance:

- No production systems accessed.
- No credentials used.
- No source secrets printed.
- No rows written anywhere.
- Every AI suggestion is traceable to a deterministic preflight finding.
- Human reviewer can accept, reject, or edit each proposed mapping or exception group.
- The prototype clearly reports whether it would save manual time, reduce errors, both, or neither.

## Proposed Project Plan

1. Prepare sample and template definitions in `ws sales`.
2. Build or script the deterministic preflight in a local no-write branch only after approval.
3. Run the sample through preflight and generate artifacts.
4. Use AI to summarize only the generated artifacts and propose mappings/checklists.
5. Review results with the Sales Analyst/import owner.
6. Decide whether to proceed to read-only production-reference matching.

## Verification Notes

- This planning slice was docs-only in AI Workspace.
- Existing related context reviewed:
  - `TODO.md` active backlog item for AI-assisted data import.
  - `worker_roles/sales-analyst.md`.
  - Salesreport automation and MemPalace project-hub notes.
- No `salesreport`, `importer`, or `bid` repo files were modified.
- No code, credentials, production data, mailbox data, external systems, email sends, commits, pushes, deploys, imports, or runtime changes were performed.

## Follow-Ups

- Open a `ws sales` task only when Robert approves moving from planning to the no-write prototype.
- Before prototype implementation, run `git status` and safe fast-forward pull in `salesreport`, then coordinate Code and Git Manager if any code files will be touched.
- Ask the human owner to provide or approve a sanitized/synthetic sample import file and expected output/checklist.
