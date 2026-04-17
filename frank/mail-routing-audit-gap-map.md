# Mail Routing Audit and Gap Map

Last Updated: 2026-04-17 10:59 CDT

Scope: local audit document for Frank task `366218` / `366219` / `366220` / `366221`.

## Guardrails

- This document was produced from local Frank workspace notes only.
- No email was sent.
- No mailbox, Google Admin, CPanel, Portal, Forge, Lists, or credential path was accessed.
- No forwarder, group, user, alias, mailbox, filter, or routing rule was created, edited, or deleted.
- Any live admin check or cleanup action below requires explicit approval plus a safe export/read path.

## Local Evidence Used

- `TODO.md` open item dated 2026-04-10 for the mail-routing audit and gap map.
- `HANDOFF.md` Angele cleanup and marketing-forwarder audit notes from 2026-04-10.
- Robert's later confirmation recorded in `TODO.md` that the Abby/Jordan old-user alias and marketing-alias routing items were fixed externally.
- Frank guardrails in `AGENTS.md` and `WHAT_TO_DO.md`.

## Known Routing Layers

| Layer | Domain or system | Current known role | Locally confirmed facts | Main gaps |
| --- | --- | --- | --- | --- |
| CPanel forwarders | `koval-distillery.com` | Legacy/general alias forwarding for old-user and shared addresses | TODO notes current examples: `marketing@koval-distillery.com -> abby.boler@kovaldistillery.com` and `marketing@koval-distillery.com -> ashley.mccarron@kovaldistillery.com` | Need current full CPanel forwarder export. Need to verify whether `sales@`, `marketing@`, `all@`, old-user aliases, and catch-all/default handling still exist and do not silently fail. |
| Google Workspace routing | `kovaldistillery.com` | Primary Google-hosted mailbox/user/group routing | TODO notes: check Google default routing; check users and additional email accounts; Sonat now gets both marketing aliases | Need current Google Admin routing export, user alias export, group membership export, and default routing configuration. |
| Google user aliases | `kovaldistillery.com` plus possible alternate-domain aliases | User-specific alias coverage for people who may have old-domain addresses | TODO says current strategy is to add default routing in Gmail for users who only have an account at `@koval-distillery.com` | Need compare list of active users against aliases on both domains. Need identify users with only legacy-domain addresses or no active destination. |
| Google groups / shared groups | Likely `kovaldistillery.com` | Preferred long-term route for group communication if managed centrally | TODO notes group definitions may now live in Portal for mailings instead of manually maintained CPanel forwarders | Need actual group list, group aliases, member exports, external posting settings, moderation settings, and owner list. |
| Portal groups | Portal | Possible source of truth for operational/user groups | TODO says group-mail strategy should tie into Portal/Forge/Lists | Need Portal group export and rule for which Portal groups are allowed to generate email audiences. |
| Forge / Lists | Forge and Lists workspaces | Intended systems for structured group communication and mailing definitions | TODO says group communication should really happen there | Need owner decision: which groups belong in Portal, which belong in Lists, and which aliases must remain mail-in aliases. |
| Mailbox filters and historical catch-alls | Gmail/mailboxes | Possible residual routing into retired mailboxes such as Angele | Handoff shows Angele received alias-routed marketing/old-user mail, including Abby/Jordan-related paths before Robert's external fixes | Need export or controlled header samples after the external fixes to verify residual delivery. |

## Address Map From Local Notes

| Address or pattern | Known or suspected destination | Status from local notes | Required verification |
| --- | --- | --- | --- |
| `marketing@koval-distillery.com` | Abby and Ashley were listed in TODO examples; Sonat now reportedly gets both marketing aliases | Historically active in CPanel or equivalent legacy routing | Confirm current CPanel forwarder and Google routing. Confirm intended final owner list. |
| `marketing@kovaldistillery.com` | Recent Angele header samples delivered to Abby; older samples delivered to Jordan; TODO says Sonat now gets both marketing aliases | Prior routing changed over time; Robert later confirmed marketing-alias item fixed externally | Confirm current Google alias/group/default routing and send test only after approval. |
| `sales@koval-distillery.com` | Unknown | Named as general forwarder to include in map | Need CPanel export and intended owner list. |
| `sales@kovaldistillery.com` | Unknown | Named as general forwarder family to include in map | Need Google/group export and intended owner list. |
| `all@...` | Unknown | Named as general forwarder/group to include in map | Need group/forwarder export, sender restrictions, and owner review because broad aliases create high spam and accidental-send risk. |
| `abby.boler@kovaldistillery.com` | Active destination or alias path involved in marketing routing | Angele cleanup found many Abby-alias hits; Robert later confirmed Abby old-user alias issue was fixed externally | Confirm no mail still routes into retired/incorrect mailbox. |
| `jordan.wimby@kovaldistillery.com` | Active destination or historical alias path involved in marketing routing | Angele cleanup found Jordan-alias hits; Robert later confirmed Jordan old-user alias issue was fixed externally | Confirm no mail still routes into retired/incorrect mailbox. |
| Old-user aliases at `@koval-distillery.com` | Unknown per user | TODO says make sure old users are covered and do not fail | Need active-user list plus old-domain address list. |
| `no-reply@koval-distillery.com` inquiry stubs | Inquiry/contact-form traffic | Handoff says residual Angele clutter included no-reply inquiry stubs | Need determine whether these are form-generated copies, CRM notifications, or real replies needing owner routing. |

## Gap Map

| Gap | Risk | How to identify failure | Safe next evidence |
| --- | --- | --- | --- |
| No current CPanel forwarder inventory in local workspace | Legacy-domain mail may fail, duplicate, or route to stale people | Bounce reports, missing expected mail, or headers showing delivery into retired mailbox | Export all CPanel forwarders for `koval-distillery.com` as CSV/text. |
| No current Google routing/default-routing export | Primary-domain mail may depend on unknown default route or aliases | Headers show unexpected envelope recipient, or users receive mail only through catch-all behavior | Export Google Admin routing/default-routing settings and user aliases. |
| Old-user aliases not reconciled against active users | Former staff mail may keep landing in shared/retired inboxes or disappear | High alias hits in legacy mailboxes, customers replying to former employees, support/vendor threads unanswered | Build user-by-user matrix: old address, active destination, owner, action. |
| General forwarders not owner-reviewed | `sales@`, `marketing@`, `all@` may have wrong recipients, too many recipients, or no accountable owner | Duplicate handling, missed ownership, spam spread, accidental broad mail exposure | Owner-approved recipient list for each shared address. |
| Domain interaction unclear | Same local part may behave differently on `koval-distillery.com` and `kovaldistillery.com` | Mail sent to same local part on both domains reaches different people | Compare aliases/forwarders by local part across both domains. |
| Portal/Forge/Lists group strategy undecided | Manual CPanel/Google groups may drift from operational user groups | Lists sent to stale people, Portal teams do not match email audiences | Export group definitions from Portal/Forge/Lists and choose source of truth per group. |
| Cleanup/delete actions lack approval package | Removing old accounts/forwarders could break vendor/customer replies | Lost replies after deletion, bounces, or inability to recover historical context | Prepare proposed deletion list with last-seen mail/header evidence and owner approval. |

## Verification Package Needed From Robert or Admin Export

1. CPanel forwarder export for `koval-distillery.com`, including destination addresses and any default/catch-all behavior.
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

1. Ask Robert/admin for the export package above rather than logging into admin systems from Frank.
2. Populate an address registry from those exports.
3. Compare local parts across `koval-distillery.com` and `kovaldistillery.com`.
4. Mark each address as `keep`, `move to Google group`, `move to Portal/Forge/Lists workflow`, `needs owner decision`, or `delete after approval`.
5. For high-risk shared addresses, verify with header samples or approved test messages before any deletion.

## Current Local Conclusion

The local gap map is complete enough to guide the next admin/export review. The largest unresolved risks are not coding issues; they are missing current administrative inventories and owner decisions for shared/general addresses. Frank should not attempt live admin login, credential access, email sending, or routing changes for this task without a separate approval.
