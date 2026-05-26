# AI Cloud Google Drive / Docs Write Path How-To

Updated: 2026-05-19

## Goal

Use the working local Google OAuth token path for read/write Google Docs and Drive work in this workspace instead of re-deriving scopes through `gcloud` every time.

## Working Path

- OAuth client:
  - `/Users/werkstatt/ai_workspace/.private/google-oauth/frank-drive-desktop-client.json`
- OAuth token:
  - `/Users/werkstatt/ai_workspace/.private/google-oauth/frank-google-drive-token.json`
- Token fields used:
  - `access_token`
  - `refresh_token`
  - `scope`
  - `token_type`
  - `expires_at`
  - `client_id` / `client_secret` from the desktop client JSON

## Libraries

- Python Google auth:
  - `google.oauth2.credentials.Credentials`
  - `google.auth.transport.requests.Request`
- Google API client:
  - `googleapiclient.discovery.build`

## Recommended Pattern

1. Load the desktop client JSON and the workspace token JSON.
2. Build `Credentials` from the stored access token plus refresh token and client metadata.
3. Reuse the token's recorded `scope` string when possible.
4. Refresh only when needed.
5. Build either:
   - `docs` for `documents().get()` / `documents().batchUpdate()`
   - `drive` for file listing / create / metadata work
6. Read back the live doc or file after write to confirm the change landed.

## What Not To Do

- Do not assume `gcloud auth print-access-token` is the write path for Docs/Drive.
- Do not treat a missing `gcloud` Docs scope as proof that the workspace has no writable Google integration.
- Do not re-check token scope availability from scratch unless the local token file has actually changed.

## Verification Rule

- For Docs writes, confirm by reading the live document back with the same Google API flow.
- For Drive writes, confirm by a metadata readback or file listing in the approved shared Drive.

## Workspace Note

- This path is now the default documented workflow for local Google integration in `ai_workspace` and the broader AI Cloud workflow.
- Treat it as the starting point for any Google Docs or Drive work in AI Cloud unless a different approved identity or token path is explicitly required.
