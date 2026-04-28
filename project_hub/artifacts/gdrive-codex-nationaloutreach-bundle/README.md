# Codex / National Outreach Drive API Bundle

Status: OAuth completed locally; no token printed or stored in git
Created: 2026-04-27 CDT

This bundle wires the existing reviewed Google Drive helper for the `nationaloutreach@kovaldistillery.com` Google account, with `codex@kovaldistillery.com` as the Codex send-from alias on the same mailbox route.

## Identity

- OAuth login account: `nationaloutreach@kovaldistillery.com`
- Codex send-from alias: `codex@kovaldistillery.com`
- Worker role: Codex Local Agent / Email Coordinator
- Not Frank
- Not Macee

## Scope

Default OAuth scopes:

- `https://www.googleapis.com/auth/drive.metadata.readonly`
- `https://www.googleapis.com/auth/drive.file`

This is narrower than full Drive access. It supports metadata reads plus app-created/explicit file access. Do not widen to full Drive without a separate approval.

## Private Paths

- OAuth client: `.private/google-oauth/frank-drive-desktop-client.json`
- Local token: `.private/google-oauth/nationaloutreach-google-drive-token.json`
- Future Infisical refresh-token secret: `GOOGLE_DRIVE_CODEX_NATIONALOUTREACH_REFRESH_TOKEN`

Do not print, email, commit, or paste token values.

## Commands

Authorize from an interactive browser session:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/authorize.sh
```

Inspect safe resolved config:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/show-config.sh
```

Run metadata test after OAuth:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/test.sh
```

Confirm the authenticated Drive identity without listing shared-drive content:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/whoami.sh
```

List the approved shared Drive target after OAuth:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/list.sh --json
```

## Boundaries

- No Google Drive folder/permission mutation is implied by this setup.
- No broad Drive listing unless explicitly approved.
- No token migration to Infisical until the local OAuth token exists and the target secret path is confirmed.
- No private file content download/upload automation beyond explicitly approved `drive.file` test behavior.

## Working OAuth Method

The working Mac mini path is `manual-authorize`, not a browser callback relay.

1. Run `project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/authorize.sh`.
2. Open the printed Google consent URL.
3. After Google redirects to the broken `127.0.0.1:58080` callback, copy the full address bar including `code=`.
4. Paste that full URL into `.private/google-oauth/nationaloutreach-callback-url.txt`.
5. The helper exchanges the code privately, writes `.private/google-oauth/nationaloutreach-google-drive-token.json`, and clears the callback file.

Do not paste callback URLs, codes, tokens, or token file contents into chat, email, docs, git, or logs.

Current verification:

- `whoami.sh` confirms auth for `nationaloutreach@kovaldistillery.com`.
- `test.sh` currently fails with `teamDriveMembershipRequired` for shared Drive `0AP-Yf32mH4IHUk9PVA`, which means shared-drive membership/access is still missing for this account.
