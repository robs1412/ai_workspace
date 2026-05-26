# Login / OPS DB Host Production Fix

Master ID: `AI-INC-20260526-LOGIN-OPS-DBHOST-01`
Date: 2026-05-26
Repos/surfaces: live `/home/koval/public_html/login`, live `/home/koval/public_html/ops`, `ai_workspace` Task Flow

## Current Status

Completed after Robert's final correction at 2026-05-26 11:28 CDT.

Robert asked to change the live DB host back to `localhost`. Live config now reads:

- `/home/koval/public_html/login/.env`: `LOGIN_DB_HOST=localhost`
- `/home/koval/public_html/ops/.env`: `DB_HOST=localhost`

Backups before the localhost restore:

- `/home/koval/public_html/login/.env.pre-localhost-restore-20260526-092825`
- `/home/koval/public_html/ops/.env.pre-localhost-restore-20260526-092825`

Live app-side DB identity proof:

- `db_user=koval_crm2@localhost`
- `current_user=koval_crm2@localhost`
- `db_hostname=vps125145.inmotionhosting.com`

Public proof:

- `https://www.koval-distillery.com/login/index.php?referrer=salesreport` returns `HTTP 200`, title `KOVAL Portal Login`, and hidden referrer `/salesreport`.
- `https://www.koval-distillery.com/salesreport/` returns `302` to login, then `HTTP 200` with hidden referrer `/salesreport`.
- `https://www.koval-distillery.com/ops/start.php` returns `302` to `/login/index.php?referrer=ops%2Fstart.php`, then `HTTP 200` with hidden referrer `/ops/start.php`.

Task Flow packet `taskmode-login-ops-salesreport-dbhost-2026-05-26` has been updated to `closed_with_proof`.

## Superseded Intermediate Status

Robert clarified the DB host must be `koval-distillery.com`, not localhost. Live config was restored accordingly:

- `/home/koval/public_html/login/.env`: `LOGIN_DB_HOST=koval-distillery.com`
- `/home/koval/public_html/ops/.env`: `DB_HOST=koval-distillery.com`

Backups before the restore:

- `/home/koval/public_html/login/.env.pre-live-dbhost-restore-20260526-091230`
- `/home/koval/public_html/ops/.env.pre-live-dbhost-restore-20260526-091230`

Exact current blocker: on the live server, `koval-distillery.com` resolves to `104.247.75.129`, and MySQL denies `koval_crm2` from that host. Public `/login/index.php?referrer=salesreport` now returns `HTTP 500` again with `System is currently unavailable`, matching the required host setting.

Live error proof:

`FATAL: Access denied for user 'koval_crm2'@'104.247.75.129' (using password: YES)`

Task Flow packet `taskmode-login-ops-salesreport-dbhost-2026-05-26` was updated from closeout to blocked with this exact blocker, then later closed again after Robert requested `localhost`.

## Original Summary

Robert reported that `/ops` or `/salesreport` was not working and pointed at:

`https://www.koval-distillery.com/login/index.php?referrer=salesreport`

Live readback showed the issue was the shared login/OPS database bootstrap, not a Salesreport page failure. Browser-like requests to `/login/index.php?referrer=salesreport`, `/login/index.php`, and `/ops/start.php` returned `500 Internal Server Error`.

## Cause

Live error logs matched the request timestamps with:

`FATAL: Access denied for user 'koval_crm2'@'104.247.75.129' (using password: YES)`

Both live `/login/.env` and `/ops/.env` used the public host `www.koval-distillery.com` for database access. On the production host that resolves to `104.247.75.129`, so MySQL saw the connection as public-host access and rejected it. The same non-printed credentials tested successfully against `127.0.0.1` and `localhost`.

## Superseded Fix

The earlier localhost fix is superseded by Robert's correction. It temporarily restored public HTTP behavior but did not match the required DB host. It changed only the non-secret DB host values on live:

- `/home/koval/public_html/login/.env`: `LOGIN_DB_HOST=127.0.0.1`
- `/home/koval/public_html/ops/.env`: `DB_HOST=127.0.0.1`

Backups created before mutation:

- `/home/koval/public_html/login/.env.pre-dbhost-fix-20260526-085347`
- `/home/koval/public_html/ops/.env.pre-dbhost-fix-20260526-085347`

No credential values were printed or changed.

## Superseded Proof

- `https://www.koval-distillery.com/login/index.php?referrer=salesreport` returned `HTTP/1.1 200 OK`, title `KOVAL Portal Login`, and hidden referrer value `/salesreport`.
- `https://www.koval-distillery.com/ops/start.php` returned `302` to `/login/index.php?referrer=ops%2Fstart.php`, then `HTTP/1.1 200 OK`.
- `https://www.koval-distillery.com/salesreport/` returned `302` to `../login/index.php?referrer=salesreport`, then `HTTP/1.1 200 OK` with hidden referrer `/salesreport`.
- Non-secret config readback showed `LOGIN_DB_HOST=127.0.0.1` and `OPS_DB_HOST=127.0.0.1`.
- Task Flow packet: `taskmode-login-ops-salesreport-dbhost-2026-05-26`.

## Remaining

None for the reported login/Salesreport/OPS redirect path.
