# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260520-LOGIN-2FA-REGRESSION-01`
- Date Opened: `2026-05-20`
- Date Completed: `2026-05-20`
- Owner: `Security Guard` / `login` owner
- Priority: `High`
- Status: Completed

## Scope

Record the confirmed 2FA/login regression behind OPS task `369936` and hand the fix to the security/login owner lane.

## Symptoms

- OPS task `369936` was created as `2FA issue`.
- The source email said token logins were broken.
- The general login flow had been sending an unexpected 2FA message instead of the normal `/portal`-triggered one.
- The live Portal backend was patched to force `admin` through 2FA and route the login flow through Portal MI.
- The live backend container is now running the fixed image `koval-crm-backend:authfix-20260520`.

## Durable Proof

- Workspaceboard session `285827f3` is already closed with proof for the blocker state.
- Closeout proof marker: `taskflow-a3e78256e12bda66 blocked: OPS 369936 2FA/login regression with live verification code captured; Security Guard or login owner review required before any reply or filing.`
- OPS task `369936` was then silently completed after the live fix was deployed and verified on the host.

## Follow-Up

- Keep the fix with Security Guard / login owner for any follow-up review.
- The repair has been recorded against the same OPS task and proof trail rather than creating a second identity for the same issue.
