# Frank Drive Metadata Bundle

Local reviewed Mac mini adaptation of Claude Task `#1326`.

Included:

- `CLAUDE.md`
- `drive.py`
- `authorize_frank_drive.py`
- `list.sh`
- `test.sh`

Deliberately not included in the first local slice:

- `download.sh`
- broad upload helper scripts

Robert later approved a narrow read/write test on 2026-04-26. The reviewed helper now includes `drive.py upload-text` for one text-file upload to the approved shared Drive target.

Expected env/paths before live use:

- `INFISICAL_MACHINE_ENV_FILE` or a local equivalent of the machine-identity env
- `GOOGLE_DRIVE_REFRESH_TOKEN_SECRET_NAME=GOOGLE_DRIVE_FRANK_REFRESH_TOKEN`
- temporary local mode: `GOOGLE_DRIVE_USE_LOCAL_TOKEN=1`
- temporary local token file: `.private/google-oauth/frank-google-drive-token.json`
- optional `GOOGLE_DRIVE_SCOPE` override only if the default scope needs to be restated
- optional `GOOGLE_DRIVE_TEST_DRIVE_ID=0AP-Yf32mH4IHUk9PVA` to restate the approved shared Drive target

Default behavior:

- `drive.py list` and `list.sh` default to the approved shared Drive ID, not a broad Drive listing.
- `drive.py upload-text` uploads one local text file to the approved shared Drive ID by default.
- Broad listing is disabled unless `GOOGLE_DRIVE_ALLOW_BROAD_LIST=1` is explicitly set; do not set it for Frank's first slice.
- `authorize_frank_drive.py show-config --json` is safe for config inspection.
- `authorize_frank_drive.py authorize` is gated because it starts OAuth and writes a temporary token file.

Next live actions outside this repo patch:

1. complete Frank OAuth consent
2. write `GOOGLE_DRIVE_FRANK_REFRESH_TOKEN` to Infisical
3. run `test.sh`
4. run `list.sh 0AP-Yf32mH4IHUk9PVA --json`

Temporary local status:

- Frank OAuth was completed locally on 2026-04-26.
- Avignon OAuth was completed locally on 2026-04-26.
- Frank and Avignon were re-consented for `drive.file` on 2026-04-26.
- Use `.private/venvs/gdrive/bin/python` plus `GOOGLE_DRIVE_USE_LOCAL_TOKEN=1` until Infisical is wired.
- For Avignon, set `GOOGLE_DRIVE_LOCAL_TOKEN_FILE=/Users/werkstatt/ai_workspace/.private/google-oauth/avignon-google-drive-token.json`.
- Do not move passwords into shared folders.
