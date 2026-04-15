# Frank Google Calendar OAuth Setup

Last Updated: 2026-04-09

## Goal

Allow `frank.cannoli@kovaldistillery.com` to access Robert's shared Google Calendar through a supported OAuth path that fits Frank's current local-script and launchd model.

## Recommended Auth Model

- OAuth client type: `Desktop app`
- Google account used for consent: `frank.cannoli@kovaldistillery.com`
- Calendar access model: Robert shares his calendar directly to Frank, then Frank's app accesses it as Frank

This matches Google's installed-app guidance for local desktop scripts and avoids the extra admin overhead of a service account with domain-wide delegation.

## Minimal Scopes

Default Frank scope set for practical assistant use:

- `https://www.googleapis.com/auth/calendar.events`
- `https://www.googleapis.com/auth/calendar.calendarlist`

Why this pair:

- `calendar.events` is the narrowest practical read/write event scope across calendars Frank can access, including Robert's shared calendar.
- `calendar.calendarlist` is needed if Frank must insert Robert's shared calendar into Frank's calendar list so it becomes visible and addressable in the app.

If Frank only needs read-only access, switch the event scope to:

- `https://www.googleapis.com/auth/calendar.events.readonly`

If Robert's calendar is already present in Frank's Calendar UI and no app-side insertion is needed, `calendar.calendarlist` can be omitted.

## Files And Storage

Source-of-truth client file:

- `ai_workspace/.private/google-oauth/frank-calendar-desktop-client.json`

Machine-local token file:

- `~/.frank-launch/private/frank-google-calendar-token.json`

Notes:

- Keep the refresh token machine-local, not in the synced `frank/` workspace.
- The token file should be `0600`.
- The OAuth client JSON can live in `ai_workspace/.private/` for setup convenience, but the refresh token should stay on the active Frank host.

## Console Setup Required

1. Open Google Cloud Console and select or create the Frank calendar project.
2. Enable `Google Calendar API`.
3. Configure the OAuth consent screen.
4. Add the Frank account as a test user if the app is still in testing mode.
5. Create OAuth credentials with application type `Desktop app`.
6. Download the OAuth client JSON and save it as:
   `ai_workspace/.private/google-oauth/frank-calendar-desktop-client.json`

## Google Calendar Sharing Required

1. In Robert's Google Calendar settings, share Robert's calendar with `frank.cannoli@kovaldistillery.com`.
2. Grant the correct permission level:
   `See all event details` for read-only access.
   `Make changes to events` if Frank needs to create or edit events on Robert's calendar.
3. Note Robert's calendar ID from the calendar settings page. For a primary calendar this is usually `robert@kovaldistillery.com`.

## Local OAuth Bootstrap

From `ai_workspace/frank`:

```bash
PYTHONPATH=../scripts python3 ../scripts/frank_google_calendar.py show-config
PYTHONPATH=../scripts python3 ../scripts/frank_google_calendar.py authorize
PYTHONPATH=../scripts python3 ../scripts/frank_google_calendar.py list-calendars
PYTHONPATH=../scripts python3 ../scripts/frank_google_calendar.py ensure-calendar --calendar-id robert@kovaldistillery.com
```

Expected outcome:

- Frank authorizes the desktop app in a browser.
- A refresh token is written to `~/.frank-launch/private/frank-google-calendar-token.json`.
- Robert's shared calendar becomes visible in Frank's calendar list if it was not already inserted.

## OPS Reuse Path

OPS already has a Google OAuth web client and stored refresh tokens.

If you want to reuse OPS instead of creating a new Google Cloud client:

```bash
cd "/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/frank"
PYTHONPATH=../scripts python3 ../scripts/frank_google_calendar.py import-ops --ops-user-id 1
PYTHONPATH=../scripts python3 ../scripts/frank_google_calendar.py list-calendars
PYTHONPATH=../scripts python3 ../scripts/frank_google_calendar.py ensure-calendar --calendar-id robert@kovaldistillery.com
```

This imports:

- the OPS Google OAuth client from `ops/.env`
- the stored OPS refresh token for the chosen OPS user id

Use this only if you intentionally want Frank to operate with the same Google account/token currently connected in OPS.

## Env Vars

Optional overrides:

- `FRANK_GOOGLE_CAL_CLIENT_FILE`
- `FRANK_GOOGLE_CAL_TOKEN_FILE`
- `FRANK_SUPPORT_ROOT`
- `FRANK_PRIVATE_DIR`

## What The User Still Needs To Do

- Create the Google Cloud OAuth desktop client
- Download the client JSON into the expected private path
- Complete one browser-based OAuth consent as `frank.cannoli@kovaldistillery.com`
- Confirm Robert has shared the calendar to Frank with the intended permission level
