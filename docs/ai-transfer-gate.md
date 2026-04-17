# AI Transfer Gate

Short-lived file transfer gate for cases where the primary AI worker (`Macmini.lan` / `.17`) needs to fetch a file from a front-facing workstation such as the M4 or MacBook.

## Security Model

- The Mac mini key is restricted in `authorized_keys` with a forced command.
- The forced command does not allow a shell, PTY, port forwarding, X11 forwarding, or agent forwarding.
- A local user on the workstation must create a one-time grant from an interactive local terminal.
- The approval code is shown once and is not stored in plaintext.
- Grants expire by default after five minutes and are consumed after one successful fetch.
- The grant approves one exact resolved file path, not a directory browse.
- `~/Downloads - shared` is the one always-allowed folder. Files and folders placed there can be fetched from `.17` without a one-time code.
- Shared-folder access is constrained by resolved paths; `..`, absolute paths, and symlink escapes are rejected or skipped.
- Audit logs record metadata only: timestamps, grant id, file path, basename, size, outcome, and SSH source. They do not record file contents or approval codes.

This does not replace normal SSH hardening. It narrows the Mac mini-to-workstation path for file pulls.

## Receiver Setup

On the M4 or MacBook, install a restricted `authorized_keys` line for the Mac mini public key:

```bash
/Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py install-authorized-key \
  --public-key /path/to/macmini-to-workstation.pub \
  --gate-path /Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py \
  --from-host 192.168.55.17
```

Review the printed line. Then apply:

```bash
/Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py install-authorized-key \
  --public-key /path/to/macmini-to-workstation.pub \
  --gate-path /Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py \
  --from-host 192.168.55.17 \
  --replace-existing \
  --apply
```

The installer creates a timestamped `authorized_keys` backup before replacing any matching key.

## Approve A File

Preferred M4 flow: double-click:

```text
/Users/werkstatt/ai_workspace/scripts/approve_ai_fetch.command
```

It opens a file picker, creates a one-time grant, prints the grant id and code, and copies the grant id/code to the clipboard.
No Python command is required for the normal approval flow.

Terminal flow:

```bash
/Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py approve ~/Desktop/example.pdf
```

It prints a grant id and six-digit code. Share those only for the specific transfer.

## Fetch From Mac Mini

Run on `Macmini.lan`:

```bash
/Users/werkstatt/ai_workspace/scripts/fetch_from_m4.sh \
  1713370000-abcd1234 \
  ~/Downloads/example.pdf
```

Lower-level form:

```bash
/Users/werkstatt/ai_workspace/scripts/ai_transfer_fetch.py \
  kovaladmin@192.168.55.35 \
  1713370000-abcd1234 \
  --identity ~/.ssh/id_ed25519_macmini_to_kovaladmin \
  --output ~/Downloads/example.pdf
```

The helper prompts for the six-digit approval code without echo.

## Always-Allow Shared Folder

On the M4, put files or folders here when `.17` should be able to fetch them without a code:

```text
~/Downloads - shared
```

From `Macmini.lan`, list the shared folder:

```bash
/Users/werkstatt/ai_workspace/scripts/fetch_from_m4.sh --shared-list shared-list.json
```

Fetch one regular file:

```bash
/Users/werkstatt/ai_workspace/scripts/fetch_from_m4.sh \
  --shared "example.pdf" \
  ~/Downloads/example.pdf
```

Fetch a folder or file as a gzip tar archive:

```bash
/Users/werkstatt/ai_workspace/scripts/fetch_from_m4.sh \
  --shared-archive "folder-name" \
  ~/Downloads/folder-name.tar.gz
```

## Cleanup

Expired or consumed grant files can be removed:

```bash
/Users/werkstatt/ai_workspace/scripts/ai_transfer_gate.py cleanup
```
