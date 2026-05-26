# Workspaceboard Open Tasks Card Fix - 2026-05-24

Robert reported that `https://wb.koval.lan/workspaceboard/dashboard.php` showed about 330 open tasks.

## Finding

The dashboard `Open Tasks` card was reading `taskReport.totals.open` before the normalized stats read model. That value is a raw Task Flow DB bucket and still includes historical packets whose effective status is closed, completed, reported, or otherwise normalized elsewhere.

Live readback at 2026-05-24 19:34 CDT:

- `/api/stats` `open_items`: 174
- `/api/stats` `blocked_count`: 45
- `/api/stats` `waiting_count`: 117
- `/api/stats` `task_flow.counts.open`: 174
- `/api/stats` `task_flow.totals.open`: 343
- `/api/stats` `task_flow.totals.shown`: 174

## Change

Updated the `Open Tasks` dashboard card to prefer the normalized read model:

1. `stats.open_items`
2. `stats.task_flow.counts.open`
3. `taskReport.counts.open`

The card no longer falls back to `taskReport.totals.shown` because `shown` is a row/page limit in the `mode=all` report and can incorrectly display `500`. It also no longer falls back to raw `taskReport.totals.open` because that is the all-packet historical bucket, not the actionable dashboard count.

The PHP stats endpoint was also aligned with the normalized read model by publishing:

- top-level `open_items`
- top-level `blocked_count`
- top-level `waiting_count`
- `task_flow.counts.open` from the queue-visible normalized count

Files updated:

- `/Users/werkstatt/workspaceboard/assets/mi-pages.js`
- `/Users/werkstatt/workspaceboard/api/stats`
- `/Users/admin/.workspaceboard-launch/runtime/app/assets/mi-pages.js`
- dashboard/static asset query versions were bumped to `20260524.6` so the corrected script is visible as `JS 2026-05-24.6`

## Verification

- `node --check /Users/werkstatt/workspaceboard/assets/mi-pages.js`
- `node --check /Users/admin/.workspaceboard-launch/runtime/app/assets/mi-pages.js`
- `php -l /Users/werkstatt/workspaceboard/api/stats`
- `curl http://127.0.0.1:17878/assets/mi-pages.js` shows the served runtime asset uses `openTasks`.
- `curl http://127.0.0.1:17878/dashboard.html` shows `assets/mi-pages.js?v=20260524.6`.
- `curl http://127.0.0.1:17878/api/stats` confirms normalized open remains `174` while raw Task Flow open remains `342`.
