# Asher and Venetia Email Worker Setup

Status: live body-read polling active; approved send automation active; filing/deletes still gated
Created: 2026-04-27 CDT

Robert provided credentials through the approved private file path. The credential values were split into per-worker owner-only files under `.private/email-workers/` and were not printed.

Workers:

- Asher: `asher@thecultivater.com`
- Venetia: `venetia@thecultivater.com`

Verification:

- IMAP SSL login succeeded for both workers.
- IMAP STARTTLS login succeeded for both workers.
- SMTP SSL login succeeded for both workers.
- SMTP STARTTLS login succeeded for both workers.
- No mailbox contents were listed, read, moved, filed, or sent during verification.
- System LaunchDaemons `com.koval.asher-auto` and `com.koval.venetia-auto` are installed under `/Library/LaunchDaemons/`, run as `admin`, and are configured for 60-second intervals.
- Read-only launchd check on 2026-04-27 showed both labels registered with repeated runs and last exit code `0`.
- Runtime logs show body-read polling for both workers. Approved send automation is active through the worker runtime; filing, deletes, and routine authority remain gated.

Management rule:

- Avignon manages both workers by default.
- They may share Frank/Avignon mechanics, not persona.
- Their personas/directives are now written separately from Sonat's Cultivater editor packet.

Remaining activation blocker:

- Need explicit policy approval before filing mail, deleting mail, or routine action authority beyond approved task-specific sends.
- The current live runtime includes body reads and approved send behavior, while filing and delete/archive actions remain gated.

## Persona Packet

Sonat sent the editor/persona source on 2026-04-27 in `The Cultivater Editors Asher and Venetia`, with attachment `Asher Wilde and Venetia Tempest-Dunn.docx`.

The attachment was retrieved from Avignon's handled mailbox source into private local storage and converted to reusable worker guidance:

- Asher canonical YAML persona: `worker_roles/asher-wilde/persona.yaml`
- Venetia canonical YAML persona: `worker_roles/venetia-tempest-dunn/persona.yaml`
- Asher: `asher/PERSONA.md`
- Venetia: `venetia/PERSONA.md`
- Role registry: `worker_roles/asher.md`, `worker_roles/venetia.md`, and `worker_roles/send-from-personas.md`

When Asher or Venetia is called by a worker, prompt, send-from review, or editorial drafting workflow, use the YAML persona in `worker_roles/` as the canonical persona source. The workspace `PERSONA.md` files remain readable companion notes and activation-boundary references.

Do not paste the full private source attachment into chat, email, public docs, or git logs. Keep the source under `.private/email-workers/asher-venetia/`.

## Duplicate / Loop Clarification

Robert clarified on 2026-04-27 that Asher and Venetia should remain separate workers, not a combined worker lane. Treat the current intended state as two distinct worker identities:

- Asher has one Asher mailbox, one Asher local workspace, and one Asher body-read polling route.
- Venetia has one Venetia mailbox, one Venetia local workspace, and one Venetia body-read polling route.

Do not create duplicate worker accounts, duplicate local workspaces, or duplicate LaunchDaemon routes for either worker unless Robert explicitly approves a replacement or migration. Do not merge Asher and Venetia into one shared persona, inbox, workspace, or route.

Robert also clarified that no loop was recorded on Mac mini `.230` for this setup thread. Do not open a runtime-loop incident from this source alone. If duplicate or loop symptoms appear later, first audit the existing account/workspace/LaunchDaemon/sent-log state before creating anything new or changing runtime behavior.

## Sonat Introduction Emails

Sent on 2026-04-27:

- Asher -> Sonat, subject `Introduction: Asher email worker`, Message-ID `<177729951721.95902.8196008921447369271@thecultivater.com>`.
- Venetia -> Sonat, subject `Introduction: Venetia email worker`, Message-ID `<177729951781.95902.18220196148763024057@thecultivater.com>`.

Both messages included non-secret setup status and the requested directive/persona information needed before activation. No credentials or private mailbox content were included.

## Claude Setup Notice

Frank sent Claude the non-secret setup summary on 2026-04-27.

- To: `claude@koval-distillery.com`
- Cc: `dmytro.klymentiev@kovaldistillery.com`, `sonat@kovaldistillery.com`, `robert@kovaldistillery.com`
- Subject: `New email workers: Asher and Venetia setup`
- Message-ID: `<177729955852.97301.15376795770445347612@kovaldistillery.com>`
- Local body: `frank/drafts/claude-asher-venetia-email-worker-setup-2026-04-27.txt`

The note described only accounts, setup state, Avignon management, inactive runtime state, and activation blockers. No credentials or private mailbox content were included.
