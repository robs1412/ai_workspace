# Incident / Project Slice Log

Last Updated: 2026-03-07 08:05:34 CST (Machine: RobertMBP-2.local)

- Master Incident ID: AI-INC-20260307-POLICY-HUB-01
- Date Opened: 2026-03-07
- Date Completed:
- Owner: Codex
- Priority: Medium
- Status: Open

## Scope

Standardize module-level `AGENTS.md` files so `ai_workspace` is the canonical policy hub for Codex safety, prompt validation, credential handling, SSH/handoff rules, and project-hub workflow.

## Symptoms

- Global policy has been duplicated across multiple module `AGENTS.md` files.
- Policy duplication creates drift and stale guidance when security or workflow rules change in one place but not another.

## Root Cause

- Module repos accumulated repeated copies of global operating policy instead of deferring to one canonical workspace hub.

## Repo Logs

### ai_workspace

- Repo Log ID: RL-20260307-01
- Commit SHA:
- Commit Date:
- Change Summary: Add canonical policy-hub rule to `AGENTS.md`; track consolidation project in project hub.

### ops, forge, login, bid, lists, importer, salesreport, portal, contactreport, donations, eventmanagement

- Repo Log ID: RL-20260307-02
- Commit SHA:
- Commit Date:
- Change Summary: Add canonical policy-hub section directing module sessions back to `ws ai` for global policy.

## Verification Notes

- Each active module `AGENTS.md`/`agents.md` was inspected before editing.
- Consolidation approach keeps module-specific instructions local while moving global policy authority to `ai_workspace`.

## Rollback Plan

- Remove the added policy-hub sections from module files if the workspace model changes.
- Revert the corresponding `ai_workspace` documentation updates.

## Follow-Ups

- Consider removing duplicated global policy blocks from module files in a later cleanup pass once the hub-and-spoke model is in use.
