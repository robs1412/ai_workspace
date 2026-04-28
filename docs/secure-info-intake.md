# Secure Info Intake

Approved private root:

`/Users/werkstatt/ai_workspace/.private/ai-workspace/secure-info/`

Folders:

- `inbox/`: put raw files here for intake.
- `archive/`: original files are copied here and kept.
- `processed/`: dated working copy, using a `YYYYMMDD-` filename prefix.
- `metadata/`: one JSON sidecar per processed file.

Run:

```bash
cd /Users/werkstatt/ai_workspace
scripts/secure_info_intake.py --source-system manual_upload --owner robert --tag source-info --notes "non-secret note"
```

Allowed `--source-system` values:

`google_drive`, `gmail_frank`, `gmail_avignon`, `papers`, `manual_upload`, `workspace_export`, `other`

The helper does not print file contents. It records only paths, SHA-256, MIME type, owner, source system, tags, timestamp, and a non-secret note. It does not upload to Drive, read mailboxes, call Papers, or mutate external systems.
