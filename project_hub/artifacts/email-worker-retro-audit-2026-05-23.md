# Email Worker Retro Audit - 2026-05-23

Scope: retroactive 14-day audit across National Outreach, Frank, and Avignon to verify that owner instructions and worker sends were not silently lost.

## What Was Repaired

- Normalized `209` Frank/Avignon packets that had already been archived with `archive_reason = safe_archive_no_action_closed` but still showed `status = blocked`.
- Normalized `31` Frank/Avignon packets that were correctly classified in automation/task-flow as `logged-no-action` or `filed-previously-logged-to-handled` but still showed `status = blocked`.
- Closed `4` safe false-open packets after source-first review:
  - `taskflow-owner-reply-0ef99b8c164d6590`
  - `taskflow-7fba0fdba9d00a31`
  - `taskflow-owner-reply-de99929b43fb2dd8`
  - `taskflow-5b72a43f6bd7785b`

## What The Audit Found

- The largest retroactive issue was stale packet state, not missing outgoing sends.
- Frank and Avignon had many rows that were already effectively no-action or archived, but Task Flow still displayed them as `blocked`.
- National Outreach had a smaller number of genuine owner-work threads that still needed separate proof-or-blocker review.

## Remaining Real Residue

These items were not auto-closed by the retro audit because they are not clearly no-action:

- `taskflow-2f53b534ef557c97`
  - Frank scheduler-bridge packet
  - `frank-salesreport-illinois-account-invoice-lookup-2026-05-21`
  - current state: `blocked`
  - blocker: scheduler bridge timed out before creating a visible worker session

- `taskflow-f47e9a2fad1849bb`
  - Frank scheduler-bridge packet
  - `frank-claude-papers-write-permission-nudge-2026-05-20`
  - current state: `blocked`
  - blocker: scheduler bridge timed out before creating a visible worker session

- `taskflow-ops-ai-worker-pickup-368752`
  - Frank recurring EOD wrapper
  - current state: `waiting`
  - reason left open: no truthful Robert-facing EOD Message-ID proof is attached yet

- `taskflow-ops-ai-worker-pickup-368753`
  - Avignon recurring EOD wrapper
  - current state: `waiting`
  - reason left open: no truthful Sonat-facing EOD Message-ID proof is attached yet

- `ai-manager-route-34b945fb-90e`
  - National Outreach recurring route
  - current state: `working`
  - note: old daily check-in worker route residue, not evidence of a lost send by itself

- `ai-manager-route-10d10821-4d4`
  - Avignon recurring route
  - current state: `working`
  - note: old daily EOD route residue, not evidence of a lost send by itself

## High-Risk Manual Review Threads

These were the notable National Outreach threads that still looked like real owner-work and were not safe to auto-close during this pass:

- `Re: Koval Tasting for Wild Onion Market`
- `Fwd: Koval Tasting for Wild Onion Market`
- `Re: Another Event for the calendar`
- `Re: Fwd: Social Media and Table Assignments`

Those threads need thread-specific proof-or-blocker handling, not generic retro normalization.
