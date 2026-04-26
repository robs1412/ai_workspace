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
- `upload.sh`

Those remain outside the approved first-slice scope because Frank is approved only for metadata listing and auth verification.

Expected env/paths before live use:

- `INFISICAL_MACHINE_ENV_FILE` or a local equivalent of the machine-identity env
- `GOOGLE_DRIVE_REFRESH_TOKEN_SECRET_NAME=GOOGLE_DRIVE_FRANK_REFRESH_TOKEN`
- optional `GOOGLE_DRIVE_SCOPE` override only if the metadata-only default needs to be restated
- optional `GOOGLE_DRIVE_TEST_DRIVE_ID=0AP-Yf32mH4IHUk9PVA` to restate the approved shared Drive target

Default behavior:

- `drive.py list` and `list.sh` default to the approved shared Drive ID, not a broad Drive listing.
- Broad listing is disabled unless `GOOGLE_DRIVE_ALLOW_BROAD_LIST=1` is explicitly set; do not set it for Frank's first slice.
- `authorize_frank_drive.py show-config --json` is safe for config inspection.
- `authorize_frank_drive.py authorize` is gated because it starts OAuth and writes a temporary token file.

Next live actions outside this repo patch:

1. complete Frank OAuth consent
2. write `GOOGLE_DRIVE_FRANK_REFRESH_TOKEN` to Infisical
3. run `test.sh`
4. run `list.sh 0AP-Yf32mH4IHUk9PVA --json`
