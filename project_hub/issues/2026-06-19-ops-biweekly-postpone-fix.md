# 2026-06-19 OPS Bi-Weekly Postpone Fix

## Issue

Robert reported that postponing a bi-weekly recurring OPS task only advanced it by one week on `https://www.koval-distillery.com/ops/`.

## Cause

The OPS dashboard PHP helper only checked for `biweek`, so the label `bi-weekly` fell through to the later `weekly` check and generated a hidden `next_due_date` one week ahead. The server action trusted the submitted `next_due_date`.

## Fix

- OPS commit: `47d7e54` (`fix(tasks): postpone bi-weekly tasks by two weeks`)
- Updated `start.php` dashboard postpone target logic to normalize spaces, underscores, and hyphens before matching bi-weekly labels.
- Updated `action_handler.php` so `postpone_task` only trusts a submitted client `next_due_date` when it matches the server-computed cadence date; otherwise it uses the server-computed date.

## Deployment

- Pushed OPS `main` to GitHub.
- Live OPS fast-forwarded from `a03b802` to `47d7e54`.

## Verification

- Local syntax: `php -l start.php`, `php -l action_handler.php`.
- Local cadence check confirmed `bi-weekly` maps to `+14 days`.
- Live syntax: `php -l start.php`, `php -l action_handler.php`.

No credentials, tokens, cookies, or private session material were printed or changed.
