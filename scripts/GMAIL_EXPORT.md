# Gmail Export CLI

`gmail_export.py` is a read-only Gmail API exporter. It uses OAuth scope:

```text
https://www.googleapis.com/auth/gmail.readonly
```

It can search Gmail with an explicit Gmail query and export matching messages as `.eml` files with `.json` metadata sidecars.

## Token Storage

The CLI reuses the local OAuth client JSON from the Google Docs exporter by default:

```text
~/.config/koval-google-doc-export/client_secret.json
```

It stores a separate Gmail token here:

```text
~/.config/koval-gmail-export/token.json
```

Do not paste tokens, client secrets, auth codes, or message contents into chat.

## Enable API

Enable Gmail API for the OAuth project if needed:

```text
https://console.developers.google.com/apis/api/gmail.googleapis.com/overview?project=261057116535
```

## Authorize

```bash
cd /Users/werkstatt/ai_workspace
python3 scripts/gmail_export.py authorize
```

## Search

```bash
python3 scripts/gmail_export.py search \
  --query 'ERTC OR ERC OR Leyton OR "Levin Levy" OR "Levin&Levy"' \
  --limit 20
```

Search output uses hashed message IDs only.

## Export

```bash
python3 scripts/gmail_export.py export \
  --query 'ERTC OR ERC OR Leyton OR "Levin Levy" OR "Levin&Levy"' \
  --output "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/gmail-export"
```

Use `--dry-run` before exporting broad queries. Add `--limit N` only for a deliberate test run; uncapped export is the default for final case lists.

## Extract Attachments

```bash
python3 scripts/gmail_extract_attachments.py \
  --input "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/gmail-export-oleg" \
  --output "/Users/kovaladmin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026 ERTC work/02_Communications/gmail-export-oleg-attachments"
```

The attachment extractor saves normal attachments under `attachments/`, writes `attachments-manifest.csv`, and records skipped inline/signature-like images in `skipped-signature-inline-manifest.csv` without exporting those skipped image/logo files.
