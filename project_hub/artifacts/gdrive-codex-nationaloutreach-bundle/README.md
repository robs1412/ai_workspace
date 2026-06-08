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

Google Chat uses a separate local token file so the working Drive token is not overwritten. Approved Chat scopes:

- `https://www.googleapis.com/auth/chat.messages.create`
- `https://www.googleapis.com/auth/chat.messages.readonly`
- `https://www.googleapis.com/auth/chat.spaces.readonly`

## Private Paths

- OAuth client: `.private/google-oauth/frank-drive-desktop-client.json`
- Local token: `.private/google-oauth/nationaloutreach-google-drive-token.json`
- Local Chat token: `.private/google-oauth/nationaloutreach-google-chat-token.json`
- Future Infisical refresh-token secret: `GOOGLE_DRIVE_CODEX_NATIONALOUTREACH_REFRESH_TOKEN`
- Future Chat refresh-token secret: `GOOGLE_CHAT_CODEX_NATIONALOUTREACH_REFRESH_TOKEN`

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

Authorize Google Chat read access:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/authorize-chat.sh
```

After the browser redirects to the broken localhost callback, copy the full
address bar and run this in a second terminal:

```sh
pbpaste | project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/paste-chat-callback.sh
```

Run the Chat spaces metadata test:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/chat-test.sh
```

Read only the approved Chat readback set:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/chat-readback.sh --list-allowed
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/chat-readback.sh --target robert@kovaldistillery.com --limit 5
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/chat-readback.sh --target "KOVAL Codex" --limit 5
```

Approved readback is limited to direct messages with Robert, Sonat, Mark, Dmytro,
and Sebastian, plus the named spaces `KOVAL Agents` and `KOVAL Codex`. Do not
scan or summarize other direct messages, group chats, or spaces from this token.

Send to only the same approved Chat target set:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/chat-send.sh --target "KOVAL Codex" --message "Message text"
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/chat-send.sh --target robert@kovaldistillery.com --message-file /path/to/message.txt
```

Approved send targets are identical to the readback allowlist: direct messages
with Robert, Sonat, Mark, Dmytro, and Sebastian, plus `KOVAL Agents`,
`KOVAL Codex`, and `Outreach Team`. The sender refuses all other direct
messages, group chats, and spaces even if the token can see them.

Run the adaptive Chat checker:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/chat-watch.sh
```

The checker polls only the approved allowlist. It runs every 60 seconds while
idle, switches to 15 seconds after a new message is detected, and returns to 60
seconds after 4 minutes without another new message. Its state and event log are
local runtime files under `nationaloutreach/runtime/`; polling does not use
model tokens unless a separate worker routes a message into Codex for reasoning.

Route actionable Chat messages through AI Manager and Task Manager:

```sh
project_hub/artifacts/gdrive-codex-nationaloutreach-bundle/chat-task-router.sh
```

The router consumes `google-chat-watch-events.jsonl`, ignores Codex's own
outgoing Chat sender, skips short acknowledgements by default, and keeps
ordinary question-style messages as discussion-only with no worker. When a
message contains substantive work/action language, it captures the request as an
AI Manager daily input and replies in the same approved Chat target asking for
explicit approval. A worker is not created or focused until Robert replies
`Approve` in that same Chat target. After approval, the router hands the task to
Task Manager with a finish contract and replies with the route state, worker
session id when available, Task Flow key, and first check / ETA.

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
