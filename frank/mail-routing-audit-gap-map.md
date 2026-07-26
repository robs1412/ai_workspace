# Mail Routing Audit and Gap Map

Last Updated: 2026-06-17 16:48 CDT

Scope: local audit document for Frank task `366218` / `366219` / `366220` / `366221`.

## Guardrails

- This document was initially produced from local Frank workspace notes only. The 2026-06-17 CPanel section below adds a read-only live alias-file inventory.
- No email was sent.
- No mailbox, Google Admin, Portal, Forge, Lists, or credential path was accessed. CPanel forwarder evidence came from read-only SSH access to the live alias file, not from interactive CPanel credential work.
- No forwarder, group, user, alias, mailbox, filter, or routing rule was created, edited, or deleted.
- Any live admin check or cleanup action below requires explicit approval plus a safe export/read path.

## Local Evidence Used

- `TODO.md` open item dated 2026-04-10 for the mail-routing audit and gap map.
- `HANDOFF.md` Angele cleanup and marketing-forwarder audit notes from 2026-04-10.
- Robert's later confirmation recorded in `TODO.md` that the Abby/Jordan old-user alias and marketing-alias routing items were fixed externally.
- Frank guardrails in `AGENTS.md` and `WHAT_TO_DO.md`.
- 2026-06-17 closeout readback: OPS overdue-worker list still showed `OPS 366220 | due 2026-04-18 | Not Started | frank | Document mail routing map and gap analysis`; Workspaceboard session `20e36b9e` was routed for the same title with packet `ai-manager-route-2dd13eb3-705`.
- 2026-06-17 CPanel readback for OPS `366218`: read-only SSH as `koval` on `vps125145.inmotionhosting.com` showed `/etc/valiases/koval-distillery.com` is readable and contains 148 rows.

## 2026-06-17 Closeout Status

- OPS task `366220` asks for a documented mail routing map and gap analysis. This artifact satisfies that local documentation request from available non-secret Frank workspace evidence.
- The map remains an audit/gap document, not a live routing inventory. No CPanel, Google Admin, mailbox, Portal, Forge, Lists, credential, or production routing surface was accessed during this closeout.
- The next work should be an approved admin-export review, not an unscoped Frank login or routing change. Required exports and owner decisions are listed below.
- Workspaceboard route: session `20e36b9e`, packet `ai-manager-route-2dd13eb3-705`, Task Flow key `taskflow-ops-ai-worker-pickup-366220`.

## 2026-06-17 CPanel Forwarder Inventory Readback

Read-only source: `/etc/valiases/koval-distillery.com` on `ftp.koval-distillery.com`, host readback `vps125145.inmotionhosting.com`, user readback `koval`.

No forwarder, mailbox, filter, routing rule, CPanel account, DNS record, credential, or production setting was created, edited, deleted, printed, or changed.

Current counts:

- 148 total CPanel alias rows for `koval-distillery.com`, including the catch-all row.
- 2 fail rows: `claude@koval-distillery.com` intentionally fails with a note to use the non-hyphen address, and `*` fails unknown users with `No such person at this address`.
- 6 rows include CPanel autoresponder pipes: `accounting@`, `chelsea.lovett@`, `donations@`, `kate.zuckerman@`, `robert@`, and `sonat@`.
- 81 rows still forward to at least one `@koval-distillery.com` destination, so many legacy-domain routes are chained through other legacy-domain aliases rather than directly into the primary `@kovaldistillery.com` domain.
- 3 rows include non-KOVAL external destinations: `cotmembers@`, `oona@`, and `store@`.
- 17 broad/shared sources exist in this CPanel file: `barrelsales@`, `barrelsamples@`, `cotmembers@`, `customerservice@`, `donations@`, `events@`, `group@`, `info@`, `jobs@`, `marketing@`, `orders@`, `production@`, `receipts@`, `sales@`, `samplerequest@`, `store@`, and `tours@`.
- 3 test-like rows are still present: `phptest@`, `testforwarder123@`, and `testfwd2@`.

Key address readback:

- `abby.boler@koval-distillery.com` forwards to Sonat at the primary domain.
- `jordan.wimby@koval-distillery.com` forwards to Sonat at the primary domain.
- `marketing@koval-distillery.com` forwards to Sonat at the primary domain.
- `sales@koval-distillery.com` still fans out to a mixed list of primary-domain and legacy-domain destinations.
- There is no `all@koval-distillery.com` row in the live CPanel alias file.

Audit conclusion from the CPanel side: the old-domain forwarder file is active and not merely historical. The biggest remaining cleanup risks are legacy-domain destination chaining, broad/shared aliases with many recipients, external personal-email destinations, and test rows. Cleanup still needs owner-approved intended destinations plus cross-checks against Google Workspace routing before deletion or consolidation.

## Known Routing Layers

| Layer | Domain or system | Current known role | Locally confirmed facts | Main gaps |
| --- | --- | --- | --- | --- |
| CPanel forwarders | `koval-distillery.com` | Legacy/general alias forwarding for old-user and shared addresses | 2026-06-17 live alias-file readback found 148 rows. `marketing@` routes to Sonat, `sales@` fans out to a mixed primary/legacy-domain list, catch-all fails unknown users, and no `all@koval-distillery.com` row exists. | Need owner-approved destination review and Google Workspace comparison before cleanup. |
| Google Workspace routing | `kovaldistillery.com` | Primary Google-hosted mailbox/user/group routing | TODO notes: check Google default routing; check users and additional email accounts; Sonat now gets both marketing aliases | Need current Google Admin routing export, user alias export, group membership export, and default routing configuration. |
| Google user aliases | `kovaldistillery.com` plus possible alternate-domain aliases | User-specific alias coverage for people who may have old-domain addresses | TODO says current strategy is to add default routing in Gmail for users who only have an account at `@koval-distillery.com` | Need compare list of active users against aliases on both domains. Need identify users with only legacy-domain addresses or no active destination. |
| Google groups / shared groups | Likely `kovaldistillery.com` | Preferred long-term route for group communication if managed centrally | TODO notes group definitions may now live in Portal for mailings instead of manually maintained CPanel forwarders | Need actual group list, group aliases, member exports, external posting settings, moderation settings, and owner list. |
| Portal groups | Portal | Possible source of truth for operational/user groups | TODO says group-mail strategy should tie into Portal/Forge/Lists | Need Portal group export and rule for which Portal groups are allowed to generate email audiences. |
| Forge / Lists | Forge and Lists workspaces | Intended systems for structured group communication and mailing definitions | TODO says group communication should really happen there | Need owner decision: which groups belong in Portal, which belong in Lists, and which aliases must remain mail-in aliases. |
| Mailbox filters and historical catch-alls | Gmail/mailboxes | Possible residual routing into retired mailboxes such as Angele | Handoff shows Angele received alias-routed marketing/old-user mail, including Abby/Jordan-related paths before Robert's external fixes | Need export or controlled header samples after the external fixes to verify residual delivery. |

## Address Map From Local Notes

| Address or pattern | Known or suspected destination | Status from local notes | Required verification |
| --- | --- | --- | --- |
| `marketing@koval-distillery.com` | Sonat at the primary domain | 2026-06-17 CPanel alias-file readback confirms the legacy-domain forwarder exists and points to Sonat. | Confirm matching Google routing and intended final owner list. |
| `marketing@kovaldistillery.com` | Recent Angele header samples delivered to Abby; older samples delivered to Jordan; TODO says Sonat now gets both marketing aliases | Prior routing changed over time; Robert later confirmed marketing-alias item fixed externally | Confirm current Google alias/group/default routing and send test only after approval. |
| `sales@koval-distillery.com` | Mixed primary-domain and legacy-domain destination list | 2026-06-17 CPanel alias-file readback confirms a broad fan-out list remains active. | Need owner-approved intended recipient list and Google routing comparison. |
| `sales@kovaldistillery.com` | Unknown | Named as general forwarder family to include in map | Need Google/group export and intended owner list. |
| `all@...` | No `all@koval-distillery.com` row found in the CPanel alias file | CPanel side checked on 2026-06-17; Google/group side still unknown. | Need Google/group export, sender restrictions, and owner review because broad aliases create high spam and accidental-send risk. |
| `abby.boler@kovaldistillery.com` | Active destination or alias path involved in marketing routing | Angele cleanup found many Abby-alias hits; Robert later confirmed Abby old-user alias issue was fixed externally | Confirm no mail still routes into retired/incorrect mailbox. |
| `jordan.wimby@kovaldistillery.com` | Active destination or historical alias path involved in marketing routing | Angele cleanup found Jordan-alias hits; Robert later confirmed Jordan old-user alias issue was fixed externally | Confirm no mail still routes into retired/incorrect mailbox. |
| Old-user aliases at `@koval-distillery.com` | Unknown per user | TODO says make sure old users are covered and do not fail | Need active-user list plus old-domain address list. |
| `no-reply@koval-distillery.com` inquiry stubs | Inquiry/contact-form traffic | Handoff says residual Angele clutter included no-reply inquiry stubs | Need determine whether these are form-generated copies, CRM notifications, or real replies needing owner routing. |

## Gap Map

| Gap | Risk | How to identify failure | Safe next evidence |
| --- | --- | --- | --- |
| Current CPanel forwarder inventory now exists but is not owner-reviewed | Legacy-domain mail may fail, duplicate, or route to stale people | Bounce reports, missing expected mail, or headers showing delivery into retired mailbox | Review the 2026-06-17 alias-file inventory against intended owners and Google Workspace routes. |
| No current Google routing/default-routing export | Primary-domain mail may depend on unknown default route or aliases | Headers show unexpected envelope recipient, or users receive mail only through catch-all behavior | Export Google Admin routing/default-routing settings and user aliases. |
| Old-user aliases not reconciled against active users | Former staff mail may keep landing in shared/retired inboxes or disappear | High alias hits in legacy mailboxes, customers replying to former employees, support/vendor threads unanswered | Build user-by-user matrix: old address, active destination, owner, action. |
| General forwarders not owner-reviewed | `sales@`, `marketing@`, `all@` may have wrong recipients, too many recipients, or no accountable owner | Duplicate handling, missed ownership, spam spread, accidental broad mail exposure | Owner-approved recipient list for each shared address. |
| Domain interaction unclear | Same local part may behave differently on `koval-distillery.com` and `kovaldistillery.com` | Mail sent to same local part on both domains reaches different people | Compare aliases/forwarders by local part across both domains. |
| Portal/Forge/Lists group strategy undecided | Manual CPanel/Google groups may drift from operational user groups | Lists sent to stale people, Portal teams do not match email audiences | Export group definitions from Portal/Forge/Lists and choose source of truth per group. |
| Cleanup/delete actions lack approval package | Removing old accounts/forwarders could break vendor/customer replies | Lost replies after deletion, bounces, or inability to recover historical context | Prepare proposed deletion list with last-seen mail/header evidence and owner approval. |

## Verification Package Needed From Robert or Admin Export

1. Owner-reviewed CPanel forwarder disposition for `koval-distillery.com`, using the 2026-06-17 alias-file inventory and including decisions on broad aliases, external destinations, test rows, and legacy-domain destination chains.
2. Google Admin routing/default-routing export for `kovaldistillery.com`.
3. Google user list with primary email, aliases, suspended/deleted status, and additional email accounts.
4. Google group list with aliases, members, owners, posting permissions, and moderation settings.
5. Portal group export for employee/team/group definitions used for internal communication.
6. Forge/Lists audience definitions if they are intended to replace hand-maintained email groups.
7. A reviewed owner list for `sales@`, `marketing@`, `all@`, and any other shared/general addresses.

## Proposed Target Model

- Use Google Workspace groups or approved Google aliases for live inbound shared mail where mailbox delivery is required.
- Use Portal/Forge/Lists as the source of truth for structured internal or marketing audiences, then sync or export intentionally rather than hand-maintaining CPanel forwarders.
- Keep CPanel forwarders only for legacy-domain compatibility that cannot yet move into Google Workspace.
- Maintain a simple address registry with these fields: address, domain, system of record, current destinations, owner, purpose, last verified date, and deletion/review status.
- Do not delete legacy accounts, forwarders, or aliases until the registry shows intended owner, replacement route, last evidence, and explicit approval.

## Immediate Safe Next Steps

1. Ask Robert/admin for owner decisions and the remaining non-CPanel exports above rather than logging into admin systems from Frank.
2. Populate an address registry from the 2026-06-17 CPanel readback plus the remaining exports.
3. Compare local parts across `koval-distillery.com` and `kovaldistillery.com`.
4. Mark each address as `keep`, `move to Google group`, `move to Portal/Forge/Lists workflow`, `needs owner decision`, or `delete after approval`.
5. For high-risk shared addresses, verify with header samples or approved test messages before any deletion.

## Current Local Conclusion

The local gap map is complete enough to guide the next admin/export review. The CPanel side now has a current read-only inventory; the largest unresolved risks are missing Google/group inventories and owner decisions for shared/general addresses, external destinations, legacy-domain chains, and test rows. Frank should not attempt interactive admin login, credential access, email sending, or routing changes for this task without a separate approval.
