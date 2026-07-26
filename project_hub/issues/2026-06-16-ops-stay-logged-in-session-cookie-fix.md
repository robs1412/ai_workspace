# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260616-OPS-STAY-LOGGED-IN-SESSION-COOKIE-01`
- Date Opened: `2026-06-16`
- Date Completed: `2026-06-16`
- Owner: `Codex`
- Priority: `High`
- Status: `Pushed; live pull blocked`

## Scope

Fix the local Login/OPS session persistence path behind Robert's report that OPS dashboard task creation can show `Not authenticated.` after a few hours while the logout page still recognizes a logged-in session.

## Symptoms

- OPS AJAX/auth checks can lose authenticated identity and return `Not authenticated.`
- The login/logout surface can still see enough session state to say the browser is logged in.
- Recent OPS auth logs showed repeated `require_authentication_entry` events with no `myusername`, no `userid`, and no remember-cookie recovery on affected local requests.

## Root Cause

The shared login helper had two ordering/state bugs in the cookie recovery paths:

- `ensureSessionStarted()` retried with the incoming `PHPSESSID` after an empty alias session, but it did not recompute whether the retried session had auth before diagnostics and alias-cookie handling.
- `completeLogin()`, `remember_try_silent_login()`, and `ops_sso_apply_ops_session()` refreshed the canonical/alias session cookies before writing authenticated identity into `$_SESSION`.

Together those paths could preserve or re-emit a stale empty session id even when a later path could recover identity, causing OPS and Login to disagree about whether the browser was authenticated.

## Repo Logs

### login

- Repo Log ID: `AI-INC-20260616-OPS-STAY-LOGGED-IN-SESSION-COOKIE-01`
- Commit SHA: `669b448`
- Commit Date: `2026-06-16`
- Change Summary:
  - Added `login_session_has_auth()` so session auth checks are consistent.
  - Recomputed auth state after the `PHPSESSID` retry in `ensureSessionStarted()`.
  - Only mirrors alias cookies from `ensureSessionStarted()` after the active session has auth.
  - Moved session-cookie refresh in `completeLogin()` and `remember_try_silent_login()` to after authenticated identity is written.
  - Moved OPS SSO cookie refresh in `ops_sso_apply_ops_session()` to after authenticated identity is written.

## Verification Notes

- `php -l /Users/werkstatt/login/auth_helpers.php`
- `php -l /Users/werkstatt/login/sso_helpers.php`
- `php -r 'require "/Users/werkstatt/login/auth_helpers.php"; echo function_exists("login_session_has_auth") ? "helper ok\n" : "missing\n";'`
- `git -C /Users/werkstatt/login diff -- auth_helpers.php sso_helpers.php`
- `git -C /Users/werkstatt/login log -1 --oneline` returned `669b448 fix(auth): refresh session cookies after identity hydration`
- `git -C /Users/werkstatt/login ls-remote origin refs/heads/master` confirmed origin `master` at `669b44860d72...`
- `nc -vz -w 5 ftp.koval-distillery.com 22` succeeded.
- SSH command execution to `ftp.koval-distillery.com` and `koval@ftp.koval-distillery.com` timed out or exited `255` with no remote output before live checkout readback.

## Rollback Plan

- Revert the local changes to `/Users/werkstatt/login/auth_helpers.php` and `/Users/werkstatt/login/sso_helpers.php`.
- No live rollback is required unless this local patch is later committed, pushed, and deployed.

## Deployment State

- Local commit `669b448` pushed to `origin/master`.
- Live pull is blocked by SSH command execution failure before checkout readback.
- No live pull, credential change, password change, session database mutation, or production session mutation performed.

## 2026-06-19 Follow-up: Active OPS Session Keepalive

Robert reported that `/ops` can still hit session-not-authenticated behavior and land on `/login/logout.php`'s `Confirm sign out` screen, and clarified that the real goal is to stay logged in while actively using OPS rather than recovering after a failed action.

Local patches:

- Updated `/Users/werkstatt/login/logout.php` so the confirmation page's `Stay signed in` link routes through `/login/index.php?referrer=...` instead of directly to `/ops/start.php`.
- The link preserves a safe `/ops/...` return target when present, otherwise it defaults to `/ops/start.php`.
- Explicit logout still requires the existing POST + CSRF confirmation and was not weakened.
- Added `/Users/werkstatt/ops/keepalive.php`, an authenticated JSON endpoint that refreshes the active Login/OPS session cookies, updates the active-session timestamp, and attempts Portal JWT hydration without exposing secrets.
- Updated `/Users/werkstatt/ops/footer.php` to call the keepalive endpoint after 30 seconds, every 5 minutes after that, and when a hidden OPS tab becomes visible again.

Verification:

- `php -l /Users/werkstatt/login/logout.php`
- `php -l /Users/werkstatt/ops/keepalive.php`
- `php -l /Users/werkstatt/ops/footer.php`
- Local no-cookie request to `/ops/session_keepalive.php` before the live-safe rename returned `401 Unauthorized` JSON with `need_login=true`, confirming the heartbeat path fails quietly as JSON when PHP handles the request unauthenticated.

Deployment state:

- Local OPS commits pushed: `83ef794` (`fix(auth): keep OPS sessions warm`) and `bcba6f8` (`fix(auth): use keepalive endpoint name`).
- Local Login commit pushed: `217de44` (`fix(auth): route stay-signed-in through login recovery`).
- Live OPS fast-forwarded from `ced1e07` to `bcba6f8`; live readback: branch `main`, HEAD `bcba6f8`, syntax checks passed for `keepalive.php` and `footer.php`.
- Live Login fast-forwarded from `d7783c6` to `217de44`; live readback: branch `master`, HEAD `217de44`, syntax checks passed for `logout.php`, `auth_helpers.php`, and `sso_helpers.php`.
- Live Login still has pre-existing runtime-local dirty files `.login.env` and `logs/sso_ops_token.log`; no destructive cleanup was performed.
- Public no-cookie probes to live `/ops/keepalive.php` and `/ops/start.php` return the site security filter's `406`, so final behavior should be verified from an already-authenticated browser tab where the same-origin heartbeat includes OPS cookies.
- No credential change, password change, session database mutation, or production session mutation performed.

## 2026-06-19 Follow-up: Receipt Capture Live Pull And Automation Session Recovery

Robert asked to pull the receipt-login/receipt-capture change live and reported that `/automation` remembered-login tokens such as `robert_login` no longer work.

Receipt capture:

- Local OPS commit pushed: `a03b802` (`fix(receipts): preserve statement date prefill`).
- Live OPS fast-forwarded to `a03b802`; live readback: HEAD `a03b802`, syntax check passed for `receipt_capture.php`.
- Change scope: `receipt_capture.php` now accepts `statement_date` prefill and uses it for the hidden QBO statement date, falling back to the existing `statement` value.

Automation:

- Local Automation commits pushed: `63b62ed` (`fix(auth): reuse login session recovery`) and `c1c6e34` (`fix(auth): match live automation header`).
- Live `/home/koval/public_html/automation` is not a git checkout, so no git pull was possible there.
- Backed up live `/home/koval/public_html/automation/header.php` to `header.php.bak-20260619-auth`.
- Patched only the live `header.php` opening auth block to require shared Login `auth_helpers.php`, call `ensureSessionStarted()`, then try `ops_sso_try_auto_login()` and `remember_try_silent_login()` before redirecting to `/login/index.php?referrer=automation`.
- Live syntax check passed for `/home/koval/public_html/automation/header.php`.
- Public and server-local no-cookie probes to `/automation/` return the site security filter's `406`, consistent with earlier `/ops` no-cookie probes; final remembered-login behavior should be verified from an already-authenticated browser with cookies.

No token values, cookies, credentials, password changes, session database mutations, or destructive live operations were performed.

## 2026-06-19 Follow-up: Robert Shortcut Confirmation Link Delivery Fixed

Robert reported that the Robert automation shortcut redirected to the normal Login page instead of sending/landing on the new one-time confirmation-link flow.

Login patches:

- `08366a1` (`fix(auth): deliver token confirmation links reliably`)
  - Corrected the Portal `send-email` payload keys for the existing Portal mail endpoint.
  - Added PHP mail fallback diagnostics with masked recipient metadata only.
  - Added an envelope sender for PHP `mail()`.
- `036cac2` (`fix(auth): use configured token confirmation recipient`)
  - Stored the configured confirmation recipient in the token confirmation finalize payload when the CRM identity lookup does not expose an email.
- `b45831e` / `ec94c9a`
  - Added metadata-only branch diagnostics for token confirmation creation and send-link failure points.
- `02f07df` (`fix(auth): reuse legacy db handle for token confirmations`)
  - Fixed token confirmation creation when `datalogin.php` had already been loaded and the active DB handle was only available through the legacy global handle.

Live deployment:

- Live Login fast-forwarded to `02f07df`.
- Live syntax checks passed for `auth_helpers.php` and `token_confirm.php`.

Verification:

- Controlled live helper run reported `confirm_delivery=sent`.
- Sanitized live auth-flow readback showed:
  - `token_login_confirm_create` result `created`
  - `token_login_mail_send` method `php_mail`, result `sent`
  - `token_login_confirm_link_send` sent `true`
- No passcodes, raw confirmation links, cookies, credentials, private token material, or 2FA codes were printed or recorded in this note.

Remaining hardening:

- The live shortcut passcode variables are not currently exposed as non-empty environment variables to PHP; the legacy source fallback is still what keeps the existing shortcut working. Move shortcut passcodes into the live Login environment as a separate credential-setup task, then remove source fallbacks.

## 2026-06-19 Follow-up: Confirmation Consume, Redirect Handoff, and Screen Shortcut

Robert reported that the emailed token confirmation link rendered "Login unavailable" and pasted a live token into chat. The pasted token was treated as exposed and not repeated.

Login patches:

- `d8c69a1` (`fix(auth): reuse legacy db handle for token confirmation consume`)
  - Fixed `token_confirm.php` consume path to reuse the live legacy DB handle instead of failing when `$GLOBALS['db']` is not populated.
- `38478cb` (`fix(auth): require confirmation link for screen shortcut`)
  - Added the same confirmation-link flow to `screen_login`.
  - Screen confirmation recipient is `production@kovaldistillery.com`.
- `6481cb4` (`fix(auth): preserve token-confirm session during redirect`)
  - Token confirmation now rotates the session id without destroying the previous session during the immediate redirect, preventing `/ops/login_router.php` from losing auth if the browser presents the pre-rotation cookie on the next hop.
- `a616abc` (`fix(auth): keep token-confirm session id for redirect`)
  - Follow-up readback showed preserving the old session file was insufficient because auth was written only after rotation; token-confirm redirects now keep the existing session id for the immediate Automation handoff.
- `2692b80` (`fix(auth): skip session rotation for token confirm`)
  - Corrected the actual `completeLogin()` regeneration line so `preserve_old_session` skips session id rotation for token-confirm flows.

Live deployment:

- Live Login fast-forwarded to `2692b80`.
- Live syntax checks passed for `auth_helpers.php`, `screen_login.php`, and `token_confirm.php`.

Verification and token hygiene:

- Active Robert confirmation rows were expired after the token was pasted in chat.
- Fresh Robert confirmation email sent after the consume/redirect fixes.
- Screen confirmation-link test returned `screen_delivery=sent`.
- Fresh Robert confirmation email sent after the final session-id handoff fix.
- Fresh screen confirmation email sent after the final session-id handoff fix.
- After `2692b80`, active Robert/screen confirmation rows were expired and fresh Robert plus screen confirmation emails were sent from the final deployed build.
- Sanitized live auth-flow readback showed screen token creation, PHP mail send to the masked production recipient, and `sent=true`.
- No raw confirmation links, passcodes, cookies, credentials, or 2FA codes were recorded in this note.

## 2026-06-19 Follow-up: Robert Shortcut Uses One-Time Confirmation Link

Robert approved replacing direct auto-login with a more secure no-password/no-manual-2FA flow: after the shortcut passcode is accepted, send a one-time confirmation link that completes Login into Automation.

Login patch:

- Local Login commit pushed: `5c1b29b` (`fix(auth): require email confirmation for Robert shortcut`).
- Replaced Robert `auto_login` config with `confirm_link` plus the Robert confirmation email.
- Added `token_confirm.php`.
- Added server-side confirmation-token storage in `koval_additionaluser.login_token_confirmations`.
- Confirmation token behavior: raw token only appears in the emailed link, DB stores only SHA-256 hash, default expiry 10 minutes, link is consumed before `completeLogin()` redirects to Automation.
- If sending the confirmation link fails, the flow fails closed and does not log in.
- `screen` and `generic` token configs remain unchanged.

Verification:

- `php -l /Users/werkstatt/login/auth_helpers.php`
- `php -l /Users/werkstatt/login/token_confirm.php`
- Local config readback confirmed `robert_confirm_link=1`, `robert_auto_login=0`, `screen_confirm_link=0`.
- Local invalid-token check rendered the invalid-link page without creating/sending a token.
- Live Login fast-forwarded from `0248edd` to `5c1b29b`; live readback: HEAD `5c1b29b`, syntax checks passed for `auth_helpers.php` and `token_confirm.php`, config readback confirmed `robert_confirm_link=1`, `robert_auto_login=0`, `screen_confirm_link=0`.

No token values, cookies, credentials, password changes, session database mutations beyond creating/inserting confirmation-token rows during actual use, or destructive live operations were performed.

## 2026-06-19 Follow-up: Robert Token Shortcut Is True Auto-Login

Robert clarified that the point of `robert_login` is to create an auto-login shortcut, not to reuse remembered sessions conditionally or launch 2FA.

Login patch:

- Local Login commit pushed: `0248edd` (`fix(auth): make Robert token shortcut auto-login`).
- Added explicit `auto_login => true` to the `robert` token-login config only.
- `login_begin_token_login()` now completes login immediately after passcode validation and identity resolution when the token config has `auto_login`.
- `screen` and `generic` token configs remain on their existing non-auto-login behavior.

Verification:

- `php -l /Users/werkstatt/login/auth_helpers.php`
- Local config readback confirmed Robert auto-login enabled and screen unchanged.
- Live Login fast-forwarded from `246bb7f` to `0248edd`; live readback: HEAD `0248edd`, syntax check passed for `auth_helpers.php`, `robert_auto_login=1`, `screen_auto_login=0`.

No token values, cookies, credentials, password changes, session database mutations, or destructive live operations were performed.

## 2026-06-19 Follow-up: Token Login Uses Remembered Same-User Session First

Robert clarified that `robert_login` sending or failing 2FA is not the point; the shortcut should not force an interactive Login/2FA path when the browser already has a valid remembered/authenticated Login session for the configured shortcut user.

Login patch:

- Local Login commit pushed: `246bb7f` (`fix(auth): reuse remembered token-login sessions`).
- Added `login_current_session_matches_identity()` in `auth_helpers.php`.
- `login_begin_token_login()` now validates the shortcut passcode and resolves the configured identity, then tries existing SSO/remembered session recovery and completes login immediately when the recovered/current session matches that configured identity.
- If no matching remembered/authenticated same-user session exists, the existing Portal MI 2FA challenge remains the fallback.

Verification:

- `php -l /Users/werkstatt/login/auth_helpers.php`
- CLI simulation confirmed same-user session returns true and wrong-user session returns false.
- Live Login fast-forwarded from `217de44` to `246bb7f`; live readback: HEAD `246bb7f`, syntax check passed for `auth_helpers.php`, helper present.

No token values, cookies, credentials, password changes, session database mutations, or destructive live operations were performed.
