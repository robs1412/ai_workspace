# Incident / Project Slice Log

- Master Incident ID: `AI-INC-20260411-BARREL-SALES-AUDIENCE-01`
- Date Opened: 2026-04-11
- Date Completed: 2026-04-11
- Owner: Codex workspace worker `a7a6d9f5`
- Priority: Normal
- Status: Completed

## Scope

Build the barrel-buyer re-engagement list from internal Salesreport data only, create and sync the downstream Forge/PHPList audience, document the exact creation path, and send the review list from Avignon to Sonat.

## Symptoms

AI Workspace ToDo-append requested a barrel-sales audience/list workflow in `salesreport`, with no importer dependency, excluding recently managed barrel buyers and requiring downstream Forge, PHPList, Markdown documentation, and Avignon review routing.

## Root Cause

No defect. This was a data-workflow build from an append-queue intake item. The source-of-truth barrel sales data already existed in Salesreport barrel program tables and needed to be transformed into an auditable Forge/PHPList audience.

## Repo Logs

### salesreport

- Repo Log ID: `SALESREPORT-BARREL-AUDIENCE-20260411`
- Commit SHA: `f90f9fc801c18c71a22d362a53d21ed2ab8dbc6b` (latest), preceded by `18858eacb2b1c84b63b251c0d44ee7d912491b4f`.
- Commit Date: 2026-04-11 local work performed on `RobertMBP-2.local`; pushed to `origin/master` and pulled to live.
- Change Summary:
  - Added `scripts/build_barrel_sales_forge_audience.php`.
  - Added `doc/barrel-sales-audience-2026-04-11.md`.
  - Updated `TODO.md` with the completed barrel-sales audience workflow.
  - Used internal Salesreport barrel program tables only; no importer path was used.
  - Created Forge audience `#40`, Forge planner/list item `#82`, PHPList list `#140`, and final Forge snapshot `#42`.
  - Synced `49` primary contact rows / `49` distinct PHPList members.
  - Created PHPList draft campaign `#549` for list `#140`; draft only, no send timestamps, no recipient send rows, and no attachments added.
  - Documented `84` reviewed accounts, `35` accounts with no eligible synced contact, `31` accounts with no CRM contacts, and `262` contacts blocked by PHPList suppression before snapshot sync.
  - Tightened the contact source and dedupe rule: use Portal `contact2account` links plus legacy direct `vtiger_contactdetails.accountid` links, then sync one unsuppressed primary contact per account; alternates stay in review details only.
  - Excluded internal/test/sample account prefixes from the outreach audience: KOVAL, KOVALTEST, Sample/Samples.
  - Added `/salesreport/quick_contact.php` as a faster authenticated Salesreport contact intake surface for this cleanup workflow.
  - Added `/salesreport/barrel_contact_review.php` as the barrel-specific manual review surface; it saves first name, last name, email, title/source note against the selected account row, creates/updates Portal contacts by email, links the contact to the account, and records an audit note.
  - Pushed `salesreport/master` to `origin` and fast-forwarded live `/home/koval/public_html/salesreport` to `18858eacb2b1c84b63b251c0d44ee7d912491b4f`.
  - Follow-up commit `f90f9fc801c18c71a22d362a53d21ed2ab8dbc6b`: widened `barrel_contact_review.php` add fields, made visible add fields blank/required, added saved-row reload/highlight behavior, and updated `quick_contact.php` so contacts cannot be saved against free-text account input. Quick contact now requires selecting an existing Portal account or creating a new Portal account first, then saving/linking the contact to that selected account.
  - Follow-up commit `5f7d078` after Sonat replied to Avignon: updated `scripts/build_barrel_sales_forge_audience.php` to classify the barrel review rows into cleaned buyer, Japan/Fuyuko, distributor/direct-to-distributor review-only, and ignored rows.
  - Created `doc/barrel-sales-cleaned-sonat-review-2026-04-11.md`, `doc/barrel-sales-japan-fuyuko-review-2026-04-11.md`, and `doc/barrel-sales-distributor-review-2026-04-11.md`.
  - Rebuilt Forge audience `#40` with snapshot `#44` and replaced PHPList list `#140` with the cleaned buyer segment only: `62` cleaned buyer review rows, `35` eligible synced contacts, `8` Japan rows, `13` distributor/direct-to-distributor rows, and `1` ignored U.S. Embassy Tokyo row.

### ai_workspace

- Repo Log ID: `AI-WORKSPACE-BARREL-AUDIENCE-20260411`
- Commit SHA: Not a git repository in the synced workspace path.
- Commit Date: 2026-04-11 local synced-file update on `RobertMBP-2.local`.
- Change Summary:
  - Moved the barrel-sales append intake from `In Progress` to `Done` in `TODO.md`.
  - Added this project-hub log and updated `project_hub/INDEX.md`.
  - Wrote Avignon drafts at `avignon/drafts/barrel-sales-audience-sonat-review-2026-04-11.txt` and `avignon/drafts/barrel-sales-audience-sonat-review-2026-04-11.html`.
  - Sent final review email from Avignon to Sonat via Mac mini single-writer route, then resent a corrected HTML-table version after the initial plain-text Markdown table rendered poorly.
  - Resent the updated deduped `49` contact review list from Avignon to Sonat with subject `Barrel buyer re-engagement list for review (updated 49-contact list)` and task id `barrel-sales-audience-sonat-review-2026-04-11-updated-list`; PHPList draft `#549` remained draft-only.
  - Sent the live barrel contact review page link to Sonat via Avignon with subject `Barrel contact review page is live`; message id `<177593904087.80246.12670705934468577662@kovaldistillery.com>`.
  - Recorded PHPList draft campaign `#549` with an explicit placeholder note for the missing Thresh & Winnow information/bottle picture assets.

## Verification Notes

- Startup policy checks:
  - Read Salesreport `AGENTS.md`, Salesreport `TODO.md`, Salesreport `ToDo-append.md`, AI Workspace `AGENTS.md`, AI Workspace `codex-agent-safety.md`, and AI Workspace `ToDo-append.md`.
  - Salesreport git status was clean before start, so `git pull --ff-only` was run and fast-forwarded to `321b7e463a75f72e9472dfa7ce49d7827f79ab63`.
- Script validation:
  - `php -l scripts/build_barrel_sales_forge_audience.php` returned no syntax errors.
  - Initial run created Forge snapshot `#42`; Sonat follow-up split run created Forge snapshot `#44`.
- Data verification:
  - Initial snapshot `#42`: `49` members and `49` distinct emails.
  - Follow-up snapshot `#44`: `35` cleaned buyer members and `35` distinct emails after separating Japan rows, distributor/direct-to-distributor rows, and the ignored U.S. Embassy Tokyo row.
  - PHPList list `#140`: `35` members after the follow-up split.
  - Suppressed PHPList contacts were filtered before snapshot sync so suppressed contacts were not re-added by the replace-mode sync.
  - `quick_contact.php` lints cleanly and is linked from the Salesreport menu as `Quick Contact Add`.
  - `barrel_contact_review.php` lints cleanly, loads from CLI without fatal errors, and is linked from the Salesreport menu as `Barrel Contact Review`.
  - Live host `/home/koval/public_html/salesreport` is clean at `f90f9fc801c18c71a22d362a53d21ed2ab8dbc6b`; live PHP lint passed for `barrel_contact_review.php` and `quick_contact.php` after the quick-contact follow-up, and previously for `scripts/build_barrel_sales_forge_audience.php` and `_menu.php`.
  - Browser-style live URL check for `https://www.koval-distillery.com/salesreport/barrel_contact_review.php` returns the expected Salesreport login redirect. Plain curl without a browser user agent can be blocked by the site security layer.
  - Browser-style live URL check for `https://www.koval-distillery.com/salesreport/quick_contact.php` returns the expected Salesreport login redirect.
  - Live CLI verification of `quick_contact.php` rejects contact save without selected account and renders the contact save button disabled until an account is selected/created.
  - Tastingroom archive check: local imapsync logs confirm `UserArchive/Chelsea_Lovett` exists and show relevant folder names, but the available local logs are folder listings, not message exports. Message-level archive search needs an approved searchable mailbox session/export path for `tastingroom@kovaldistillery.com`.
- PHPList draft verification:
  - Campaign `#549` subject: `Reconnecting: Award-winning spirits with a sustainable heart`.
  - Linked list: `#140` / `Forge: Barrel Buyers Re-Engagement (10y, excluding last 12m)`.
  - Draft edit URL: `http://localhost:8888/lists/admin/?page=send&id=549`.
  - Safety state: `status=draft`, `sendstart=NULL`, `sent=NULL`, `processed=0`, zero attachment rows, zero `phplist_usermessage` rows.
  - No asset attachments were invented; the draft includes a visible note to add approved Thresh & Winnow information and bottle picture before sending.
- Email guardrails:
  - Verified work was running on `RobertMBP-2.local`, not Mac mini.
  - Checked Mac mini `com.koval.frank-auto` LaunchAgent state and found no active send/check lock.
  - Transferred only the non-secret Avignon draft to the Mac mini state path.
  - Sent from Avignon to `sonat@kovaldistillery.com` on the Mac mini with subject `Barrel buyer re-engagement list for review`.
  - Message ID: `<177593347071.78670.13080383981128895677@kovaldistillery.com>`.
  - Resent from Avignon to `sonat@kovaldistillery.com` on the Mac mini with subject `Barrel buyer re-engagement list for review (HTML table resend)` because the original body used a plain-text Markdown pipe table.
  - HTML resend message ID: `<177593420564.79113.15399117273173041174@kovaldistillery.com>`.
  - Resent the updated deduped `49` contact list from Avignon to `sonat@kovaldistillery.com` on the Mac mini with subject `Barrel buyer re-engagement list for review (updated 49-contact list)`.
  - Updated-list resend task id: `barrel-sales-audience-sonat-review-2026-04-11-updated-list`.
  - Sent live link from Avignon to `sonat@kovaldistillery.com` with subject `Barrel contact review page is live`, message id `<177593904087.80246.12670705934468577662@kovaldistillery.com>`, and link `https://www.koval-distillery.com/salesreport/barrel_contact_review.php`.
  - Sent Sonat the cleaned barrel buyer review as an HTML-table Avignon reply with subject `Re: Barrel buyer re-engagement list for review (updated 49-contact list)`, task id `barrel-sales-cleaned-sonat-review-2026-04-11`, and message id `<177594059920.19790.9796655772015102457@kovaldistillery.com>`.
  - Wrote a Japan/Fuyuko draft only at `avignon/drafts/barrel-sales-japan-fuyuko-draft-2026-04-11.txt`; no Fuyuko send was prepared or sent.
  - Distributor/direct-to-distributor contacts were separated for review only; no distributor sends were prepared.
  - Confirmed the temporary Mac mini credential file was removed after send.

## Rollback Plan

- To stop use without deleting history: mark Forge audience `#40` inactive and disable/send-hold the linked planner/list item `#82`.
- To remove PHPList targeting: clear or remove PHPList list `#140` memberships, or rerun the script after changing audience rules because the sync mode is replace.
- To revise membership: update `scripts/build_barrel_sales_forge_audience.php` rules and rerun; the Forge/PHPList path is idempotent for the named audience and linked list.

## Follow-Ups

- Review Sonat's feedback on the Avignon email and update the Markdown table review details if contacts or account exclusions change.
- After contact cleanup through `quick_contact.php` or `barrel_contact_review.php`, rerun `php scripts/build_barrel_sales_forge_audience.php` so Forge audience `#40` and PHPList list `#140` include the maximum valid contacts before PHPList draft `#549` is approved or sent.
- Commit/push Salesreport script/doc/TODO changes when ready for source-control publication.
