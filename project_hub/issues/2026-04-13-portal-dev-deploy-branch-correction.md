# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260413-PORTAL-DEV-DEPLOY-CORRECTION-01`
- Date Opened: 2026-04-13
- Date Completed: 2026-04-13
- Owner: Codex / Robert approval gate
- Priority: Urgent production correction
- Status: Completed; DB verifier paused after login incident triage

## Scope

Correct Portal production branch drift after the shipped-vs-bottled report was deployed from `main` while Portal production is expected to deploy from `dev`. Port only the report/build fixes needed from `main` to `dev`, exclude main-only `TODO.md` deploy-note content from the dev code path, preserve unrelated local state, push corrected `dev`, and deploy from `dev` after Robert approval.

## Symptoms

- Live production had previously run `v20260412-audit-128814b6` from `main`.
- `origin/main` had shipped-vs-bottled report/build commits that were absent from `origin/dev`.
- After the approved `v20260413-dev-34ce6758` dev deploy, login failed in the browser because the frontend image was built without the production frontend environment and attempted requests such as `/undefined/auth/login`.

## Root Cause

- Branch drift: the report/build fixes were initially present on `main`, not on Portal `dev`.
- Deploy build drift: the clean local deploy worktree initially lacked production frontend env at build time, so the frontend compiled an undefined API base into the production bundle.

## Repo Logs

### portal

- Repo Log ID: `PORTAL-DEV-DEPLOY-CORRECTION-20260413`
- Commit SHA: `34ce6758500eeb7b4ac249420d26174a50caef79` (`origin/dev`)
- Commit Date: 2026-04-13
- Change Summary: Ported exact shipped-vs-bottled report and build fixes onto `dev` as commits `7557c00d`, `4063428e`, `f251d3cd`, `7a02c6de`, and `34ce6758`. The `TODO.md` conflict from `main` was excluded from the dev code path. `MetaModelsController.php` conflict was resolved by preserving newer dev behavior and adding only the needed report column-qualification/filter fix.

## Verification Notes

- `php -l backend/app/Http/Controllers/MetaModels/MetaModelsController.php` passed in the dev port worktree.
- `git diff --check origin/dev..HEAD` passed before pushing.
- Frontend production Docker build completed with pre-existing lint/asset-size warnings.
- Pushed `origin/dev` to `34ce6758500eeb7b4ac249420d26174a50caef79`.
- Deployed from dev with backend/frontend tag `v20260413-dev-34ce6758`.
- Login incident triage found backend auth reachable: credential-free `POST /auth/login` returned `422` validation-required response.
- Rebuilt frontend only with production frontend env and deployed tag `v20260413-dev-34ce6758-envfix`.
- Final live containers: backend `koval-crm-backend:v20260413-dev-34ce6758`; frontend `koval-crm-frontend:v20260413-dev-34ce6758-envfix`.
- Fresh browser-like `https://portal.koval-distillery.com/` request returned `200`; direct `http://portal.koval-distillery.com:8082/` returned `200`.
- Fresh app bundle `js/app.ab1a4eda.js` and vendor bundle `js/chunk-vendors.da1edf29.js` returned `200`.
- Bundle scan found no `/undefined` API signature and found the expected Portal API base.
- Backend nginx logs after the env-fix deploy showed normal API traffic and a real `POST /auth/login` returning `202`.
- One mobile client still emitted stale `/undefined/user/profile/settings` and `/undefined/logs` requests shortly after the frontend swap, consistent with an old in-memory tab because the freshly served bundle did not contain the `/undefined` signature. A follow-up 30-second frontend log window was clean for `/undefined`, `auth/login`, and `404` matches.
- Backend PHP-FPM logs still showed `pm.max_children` pressure during traffic; monitor separately if login reports continue.

## Rollback Plan

- If the env-fix frontend regresses, redeploy the prior known frontend image tag only; backend remained on the corrected dev image and was not changed during the env-fix.
- If the dev report code regresses, revert the five dev port commits on a new branch and redeploy from approved dev state after review.
- Do not force-push or deploy from `main`; keep Portal deploys on `dev` unless Robert explicitly changes the policy.

## Follow-Ups

- Keep the DB/view verifier paused until Robert confirms login is stable or asks to resume the shipped-vs-bottled SQL/permission verification.
- Harden `deploy/scripts/build.sh` so missing production env files fail the build early and cannot print a false success.
- Consider increasing backend PHP-FPM capacity or reviewing request bursts because production logs hit `pm.max_children`.
