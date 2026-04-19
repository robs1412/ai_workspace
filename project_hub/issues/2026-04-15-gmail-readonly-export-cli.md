# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260415-GMAIL-READONLY-EXPORT-CLI-01`
- Date Opened: 2026-04-15
- Date Completed:
- Owner: Robert / Codex
- Priority: Medium
- Status: Open - Gmail readonly auth verified; ERTC discovery exports and checklist created

## Scope

Create a local read-only Gmail export path for case-work email exports, starting with the 2026 ERTC work folder.

## Symptoms

Google Drive Docs were exported locally, but Gmail messages still need a searchable/readable local export path for upcoming case review.

## Root Cause

Native Gmail content is not represented as local files through Google Drive for Desktop. A Gmail API OAuth path is needed for targeted read-only export.

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-INC-20260415-GMAIL-READONLY-EXPORT-CLI-01-ai_workspace`
- Commit SHA: pending
- Commit Date: pending
- Change Summary: Added `scripts/gmail_export.py` and `scripts/GMAIL_EXPORT.md`; uses Gmail readonly scope only and stores token separately from Drive exporter.

## Verification Notes

- `python3 -m py_compile` passed with `PYTHONPYCACHEPREFIX=/tmp/gmail-export-pycache`.
- `python3 scripts/gmail_export.py --help` displays authorize/search/export commands.
- Gmail readonly OAuth completed and token stored locally under `~/.config/koval-gmail-export/`.
- Read-only search for ERTC-related terms returned hashed message IDs only.
- No Gmail message content exported yet; target query/output remains a user decision.

## Rollback Plan

Remove `scripts/gmail_export.py`, `scripts/GMAIL_EXPORT.md`, and any local `~/.config/koval-gmail-export/token.json` if Gmail access should be revoked locally. Also revoke the OAuth grant in Google account security settings if needed.

## Follow-Ups

- Enable Gmail API for the OAuth project if not already enabled.
- Choose explicit Gmail search query and export output directory before exporting message content.

## 2026-04-15 Discovery Export Update

Discovery export completed from local ERTC communication tables and local Gmail `.eml` archive. Output written under `/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/discovery_export`. Counts: 233 table/archive matched messages total, 224 production non-privileged, 9 privileged Alan Borlack, 321 attachments saved. No source messages were deleted or modified.

Direct Gmail Borlack catch-all export also completed under the privileged bucket: 500 messages, 500 attachments, query `aborlack@bbn-law.com OR Borlack`. This is intentionally broad and must remain attorney-review material.

Discovery request/checklist review completed from the April 6, 2026 Defendant request document and related comment/interrogatory drafts. Working checklist written to `/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/discovery_review/DISCOVERY_CHECKLIST.md`. Main gap identified: complete 2018-2023 quarter-by-quarter payroll tax return/amendment set, plus Leyton contract/SOW, refund/recovery proof, final damages workbook, and production privilege review.

## 2026-04-16 Oleg Gmail ERTC Export

Oleg Gmail read-only OAuth completed and token retained locally under `~/.config/koval-gmail-export/token-oleg.json` per Robert's instruction; token contents were not printed. The uncapped ERTC/Leyton/Levin query exported 420 matching messages to `/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/gmail-export-oleg`. The folder contains 420 `.eml` files, 420 per-message metadata sidecars, `gmail-export-oleg-manifest.csv`, and `gmail-export-oleg-summary.json`.

Attachment extraction completed into `/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/gmail-export-oleg-attachments`. The extractor saved 139 likely real attachments with `attachments-manifest.csv` and skipped 1,657 inline/signature-like files without exporting their binaries. Saved attachment types: 112 PDF, 12 XLSX, 10 DOCX, 4 HTML, 1 ZIP.

## 2026-04-16 Sebastian Gmail ERTC Export

Sebastian Gmail read-only OAuth completed and token retained locally under `~/.config/koval-gmail-export/token-sebastian.json`; token contents were not printed. The same uncapped ERTC/Leyton/Levin query exported 153 matching messages to `/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/gmail-export-sebastian`. The folder contains 153 `.eml` files, 153 per-message metadata sidecars, `gmail-export-sebastian-manifest.csv`, and `gmail-export-sebastian-summary.json`.

Attachment extraction completed into `/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/gmail-export-sebastian-attachments`. The extractor saved 56 likely real attachments with `attachments-manifest.csv` and skipped 426 inline/signature-like files without exporting their binaries. Saved attachment types: 38 PDF, 7 XLSX, 6 ICS, 4 DOCX, 1 ZIP.

## 2026-04-16 Mark Gmail ERTC Export

Mark Gmail read-only OAuth completed and token retained locally under `~/.config/koval-gmail-export/token-mark.json`; token contents were not printed. The same uncapped ERTC/Leyton/Levin query exported 499 matching messages to `/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/gmail-export-mark`. The folder contains 499 `.eml` files, 499 per-message metadata sidecars, `gmail-export-mark-manifest.csv`, and `gmail-export-mark-summary.json`.

Attachment extraction completed into `/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/gmail-export-mark-attachments`. The extractor saved 111 likely real attachments with `attachments-manifest.csv` and skipped 2,054 inline/signature-like files without exporting their binaries. Saved attachment types: 68 PDF, 23 XLSX, 12 DOCX, 6 JPG, 1 HEIC, 1 ICS.
