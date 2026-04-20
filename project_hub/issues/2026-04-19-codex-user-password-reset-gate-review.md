# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260419-CODEX-PASSWORD-RESET-GATE-01`
- Date Opened: 2026-04-19
- Date Completed: 2026-04-20
- Owner: Robert / Task Manager / Login worker
- Priority: High
- Status: Completed for approved password/reset-flag operation; access flags unchanged

## Scope

Read-only Login/Security review of the Codex user password-reset gate that blocked OPS task creation with `Portal access requires the mandatory security password reset`.

Source Message-ID: `<CAAtX44bsQgSRQbpS4126g-DtLhDoyXvYK0=f0t9FM5us-mvvwQ@mail.gmail.com>`

Continuation approval Source Message-ID: `<CAAtX44ZkNyOX=hQM0oHNNc60U7q2oTJge4BsPq+ZBK07f-_ncQ@mail.gmail.com>`

Routed session id: `3b39ab64`

Dedupe key: `frank-direct-email:CAAtX44bsQgSRQbpS4126g-DtLhDoyXvYK0=f0t9FM5us-mvvwQ@mail.gmail.com:codex-user-password-reset-gate-review`

## Symptoms

OPS task creation for the Codex automation user is blocked because the shared Login/Portal rollout requires a mandatory password reset before normal Portal/OPS access resumes.

## Root Cause

The Login Portal security rollout gate checks the CRM username against `koval_additionaluser.login_portal_security_rollout.reset_required` joined to the CRM user and access matrix records. For a Portal-enabled user with `reset_required = 1`, Login routes authenticated users to the forced password reset flow instead of completing normal access.

## Repo Logs

### login

- Repo Log ID: `LOGIN-CODEX-PASSWORD-RESET-GATE-REVIEW-20260419`
- Commit SHA: none
- Commit Date: none
- Change Summary: Read-only code review plus local documentation only. No password, credential, auth flag, DB row, production session, code path, deploy, commit, push, or live pull was changed.

- Repo Log ID: `LOGIN-CODEX-PASSWORD-RESET-APPROVED-20260420`
- Commit SHA: none
- Commit Date: none
- Change Summary: After Robert approval, updated only CRM/OPS Codex user id `1332` password verifier fields using the approved local credential source and Login's existing hashing helper behavior, then cleared/verified only that user's rollout reset flag. No password, token, hash, `.env` content, unrelated user, accessmatrix flag, code, commit, push, deploy, live session, routing, DNS/TLS, or auth policy change was performed.

## Read-Only Findings

- User/account scope: CRM/OPS Codex user id `1332`.
- Password mutation target if later approved: `koval_crm.vtiger_users.id = 1332`, fields `user_password`, `user_password_new`, and `password_algorithm`.
- Reset flag mutation target if later approved after password update succeeds: `koval_additionaluser.login_portal_security_rollout.user_id = 1332`, field `reset_required`.
- Portal eligibility/access check: `koval_additionaluser.accessmatrix.matrixuserid = 1332`, including `koval_portal` and `portal_status`; this should remain read-only unless a separate access change is approved.
- Enforcement files reviewed:
  - `/Users/werkstatt/login/auth_helpers.php`
  - `/Users/werkstatt/login/checklogin.php`
  - `/Users/werkstatt/login/reset_password.php`
  - `/Users/werkstatt/login/scripts/portal_security_rollout.php`
- The user-facing block text is in `login_portal_rollout_block_message()`.
- Normal login completion calls `login_portal_rollout_requires_reset_for_username()` and redirects reset-required users to `/login/reset_password.php`.
- `reset_password.php` updates the CRM password hashes via `login_update_vtiger_password()` and then clears the rollout flag via `login_clear_portal_rollout_reset()`.
- `scripts/portal_security_rollout.php complete <username>` only clears `reset_required`; it must not be used by itself for this request because Robert requested password change plus flag removal, not a reset bypass.
- This is a Login/shared-auth mutation with Portal/OPS access impact, not an OPS business/task-record mutation.

## Approval Checklist

- Robert/Task Manager explicitly approves changing the Codex CRM/OPS user id `1332` password.
- Robert/Task Manager explicitly approves clearing the reset-required flag for user id `1332` only after the password update succeeds.
- Robert/Task Manager names the approved password delivery/storage channel outside chat/logs/repo docs, and confirms no password should be printed or generated in chat.
- Robert/Task Manager confirms whether automation should use the existing Login web reset flow or a direct operational transaction using the same hashing/flag-clearing behavior.
- Robert/Task Manager approves any live DB/session verification before it is run.

## Safe Execution Recommendation

Use the existing Login reset flow where possible:

1. Authenticate as the Codex user using the approved current machine-local automation credential.
2. Complete 2FA using the existing approved process.
3. Let Login redirect to `/login/reset_password.php`.
4. Submit the new password from the approved secure channel.
5. Allow `reset_password.php` to update the CRM password verifier fields and clear `login_portal_security_rollout.reset_required` for the same user id.

If web flow is impossible, use an approved targeted operational transaction that exactly mirrors `login_update_vtiger_password()` followed by `login_clear_portal_rollout_reset()` for user id `1332`. Do not run a flag-only completion command as a shortcut.

## Verification Notes

- Code paths were inspected locally only.
- No `.env`, credential file, password hash, token, 2FA secret, live DB result, production session, or mailbox content was printed or inspected.
- 2026-04-20: Targeted operation completed after approval. Non-secret verification reported user id `1332`, `password_algorithm=modern`, `reset_required=0`, credential source `local_env_non_secret`, and `access_flags_changed=0`.
- 2026-04-20: A first guarded transaction attempt was rolled back because it required Portal-enabled status; subsequent non-secret metadata showed user id `1332` is active with 2FA enabled, already `reset_required=0`, and has `koval_portal=0`, `koval_ops=0`, and blank `portal_status`. Those access flags were not changed because they were outside the approved password/reset-flag target.
- No login/2FA browser verification or OPS task-creation write test was run because that would create live session/task side effects outside this bounded operation.

## Rollback Plan

- If password update succeeds but reset-flag clear fails, keep the gate closed and retry or investigate the flag clear only after confirming the password update.
- If the reset flag is cleared without confirmed password update, immediately re-set `koval_additionaluser.login_portal_security_rollout.reset_required = 1` for user id `1332` and report the incident.
- If the new password is misplaced or rejected, use the same approved secure channel to rotate again; never recover or expose stored hashes/secrets in chat.

## Follow-Ups

- If OPS task creation is still blocked, review the non-secret access metadata first. Any change to `koval_additionaluser.accessmatrix` flags for user id `1332` requires separate explicit approval because this operation intentionally did not change Portal/OPS access flags.
