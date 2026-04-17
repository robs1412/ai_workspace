# Google Docs Export CLI

`google_docs_export.py` exports Google Drive for Desktop pointer files (`.gdoc`, `.gsheet`, `.gslides`) into local files that Codex and other tools can read.

## OAuth Setup

Create an OAuth desktop client in Google Cloud with Drive API enabled and save the downloaded client JSON locally, for example:

```bash
mkdir -p ~/.config/koval-google-doc-export
# place the downloaded OAuth desktop client JSON here:
# ~/.config/koval-google-doc-export/client_secret.json
chmod 600 ~/.config/koval-google-doc-export/client_secret.json
```

Authorize once:

```bash
python3 scripts/google_docs_export.py authorize
```

The CLI opens a browser authorization URL and stores a refresh token at:

```text
~/.config/koval-google-doc-export/token.json
```

Do not paste OAuth tokens or client secrets into chat.

## Scan

```bash
python3 scripts/google_docs_export.py scan \
  "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work"
```

## Dry Run

```bash
python3 scripts/google_docs_export.py export \
  "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work" \
  --dry-run
```

## Export

```bash
python3 scripts/google_docs_export.py export \
  "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work" \
  --output "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/00_README_AND_INDEX/google-doc-exports"
```

Defaults:

- `.gdoc` -> `.txt`
- `.gsheet` -> `.csv`
- `.gslides` -> `.txt`

Optional formats:

- `.gdoc`: `--gdoc-format txt|docx|pdf|html`
- `.gsheet`: `--gsheet-format csv|xlsx|pdf`
- `.gslides`: `--gslides-format txt|pptx|pdf`

Each exported file gets a `.source.json` sidecar with non-secret source metadata. The sidecar stores a hash of the Google file ID, not the raw ID.
