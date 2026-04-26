# Google Drive Tool: Frank Metadata-Only Slice

This is the locally reviewed Mac mini adaptation of Claude Task `#1326` for the first Frank execution slice.

Approved first-slice contract:

- execution identity: `frank.cannoli@kovaldistillery.com`
- OAuth app: `KOVAL Agents Drive`
- client id: `872255708765-krtm0oc44ajdbi7sivqb5kpp2hpanjqg.apps.googleusercontent.com`
- scope: `drive.metadata.readonly` only
- target shared Drive: `0AP-Yf32mH4IHUk9PVA`
- no file-content reads
- no uploads
- no deletes
- no permission changes

Expected secrets:

- `GOOGLE_DRIVE_CLIENT_ID`
- `GOOGLE_DRIVE_CLIENT_SECRET`
- `GOOGLE_DRIVE_FRANK_REFRESH_TOKEN`

Mac mini adaptation points versus the server bundle:

- secret-source path is configurable instead of hardcoded to `/srv/secrets/machine-identity.env`
- refresh-token secret name is configurable
- OAuth scope is configurable and defaults to metadata-only
- `test` is narrowed to the approved shared Drive instead of broad recent-file listing
- `list` defaults to the approved shared Drive instead of broad Drive listing
- broad listing is opt-in via `GOOGLE_DRIVE_ALLOW_BROAD_LIST=1` and must remain off for Frank's first slice

OAuth helper boundary:

- `authorize_frank_drive.py show-config --json` may be used for non-secret config inspection
- `authorize_frank_drive.py authorize` starts live OAuth and writes a temporary local token file, so it must not be run until the OAuth/token gates are explicitly open

This bundle is implementation-prep only until:

1. Frank OAuth consent is completed
2. Frank refresh token is written to Infisical
3. the local machine-identity/Infisical path is approved and present
