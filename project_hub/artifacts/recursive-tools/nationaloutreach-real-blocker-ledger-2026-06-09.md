# National Outreach Real Blocker Ledger - 2026-06-09

Source: Workspaceboard DB work-state readback after stale-session cleanup.

Status: recursive cleanup stopped. Remaining National Outreach rows are real blockers or distinct owner questions, not duplicate/stale wrappers.

## Missing Source Or Details

- `9eea75bb` - Child Link Spirit Social / Isabel
  - Block: no actual Spirit Social brand-use question is visible.
  - Needed: Isabel's specific KOVAL brand-use/promotion question, or approval for Vanessa/Marketing to ask Isabel for details.

- `96fa4904` - Outlook source body/action missing
  - Block: classified-only source; Message-ID body/action not found in active inbox or sent log.
  - Needed: full source body or exact Outreach Coordinator action for Message-ID `ch4pr10mb8227663d92b097a07cdb876db61d2@ch4pr10mb8227.namprd10.prod.outlook.com`.

- `abbb9e24` - Marianos tasting source missing
  - Block: source row is classified outreach-coordinator, but task/domain/action and body path are missing.
  - Needed: source body/details or target OPS/Outreach event fields for Message-ID `<CAAtX44aYFkzh4AbW3ads_RdNKeaFYMuUhnv-b73qhKwLsfqdww@mail.gmail.com>`.

- `71ab86bb` - Wisconsin Work With market calendar
  - Block: missing attachment/details.
  - Proof: blocker email sent, Message-ID `178032730549.68468.9572280042463436334@kovaldistillery.com`.
  - Needed: dates, times, locations, and Capital Husting rep details.

## Approved-Send Or Mail Runtime Repair

- `c0821fde` - Cancellation instructions confirmation
  - Block: local fallback script updated, but approved same-thread confirmation failed with RuntimeError; no sent Message-ID.
  - Needed: repair/restart National Outreach approved email send path, resend prepared confirmation to Sonat, close with Message-ID.

- `5bae2106` - OPS1055 / Benjamin reply
  - Block: OPS1055 and shift5584 created; National Outreach completion draft failed with RuntimeError; no sent Message-ID.
  - Needed: verify whether same-thread reply to Benjamin was delivered; if not, repair mail auth/Sent Mail and resend OPS link.

- `9d95f495` - Ravenswood On Tap Robert status reply
  - Block: approved-send retry failed; artifact `status-reply-taskflow-6ea601be2d0823f4-ravenswood-on-tap.retry-20260608-1728.failed-1780957848.json`.
  - Needed: repair or approve alternate send path for Vanessa/National Outreach status reply.

## Security Guard Or Credential Boundary

- `164508a9` - ChiTown Liquors thread
  - Block: source route is security-guard and `send_allowed=no`; National Outreach cannot reply/file.
  - Needed: Security Guard/Task Manager review and approve a same-thread response or provide exact blocker.

- `5b02c522` - BID credential migration follow-up
  - Block: security-gated option-a implementation; source asks who places Square env vars into `/srv/bid/.env`.
  - Needed: owner for placing env vars without exposing credential values.

- `8718bfbe` - Shelly login-reset follow-up
  - Block: security-gated, `send_allowed=no`; National Outreach cannot send or reset credentials.
  - Needed: Security Guard handles directly or provides approved non-secret response path.

- `fd3b95b2` - Chat access instructions
  - Block: security/access-gated; National Outreach cannot send or file because source is security-guard `send_allowed=no`.
  - Needed: Security/access owner sends or approves Chat access instructions, then National Outreach can file after proof.

## Email-Coordinator Approval Or Internal Routing

- `6e0c9519` - Codex/Claude role setup messages
  - Block: active inbox remains email-coordinator with approval-required; National Outreach is not authorized to send.
  - Needed: Task Manager/email-coordinator route to Codex/AI Manager or approve exact reply path.

- `7884de1b` - Internal alias-routing response
  - Block: source state is email-coordinator, approval-required; no sent-log completion.
  - Needed: route to email-coordinator/AI Manager or explicitly authorize National Outreach/Codex to send.

- `99dc582f` - Internal Robert work instruction
  - Block: source is internal Robert instruction classified email-coordinator, approval-required.
  - Needed: route to correct AI Manager/BID/internal worker or explicitly approve National Outreach send path.

- `b4440b1c` - Tech Update owner reply
  - Block: approval-required, classified email-coordinator; National Outreach must not send routine acknowledgement/external reply.
  - Needed: email-coordinator/Task Manager route correct internal worker or approve National Outreach reply.

- `bc6eac4c` - BID COTeam bonus cross-check
  - Block: internal Robert instruction routed to email-coordinator, approval-required; National Outreach cannot send/respond.
  - Needed: route to BID/finance worker and return proof or exact finance blocker.

- `dc68812e` - Cultivater internal instruction
  - Block: routed to email-coordinator, approval-required; National Outreach cannot send/respond.
  - Needed: route/authorize internal Robert Cultivater instruction to correct worker, with proof or exact blocker.

## Portal/Auth Or Finance Adjacent

- `b096524c` - Portal overdue report 7989
  - Block: Portal draft 7989 created for overdue notification 6147835, but Portal submit failed.
  - Needed: restore/refresh approved Codex Portal submit path or clear service-account password reset/session gate so reviewer notifications can send.

## Event/OPS/Payroll Decisions

- `4dce4d0b` - Shelly Eataly shift/payroll
  - Block: Eataly shift 5542 assigned to Shelly user 1255; no matching $10 parking reimbursement row found.
  - Needed: approve Vanessa/finance to enter Shelly time and $10 parking, or leave task 370507 for manual review.

- `39f9dc71` - Mitch June tasting schedule draft approval
  - Block: Robert requested draft approval before external reply.
  - Proof: Vanessa sent approval draft with June OPS readback, Message-ID `<178032310399.46433.6296845353690111335@kovaldistillery.com>`.
  - Needed: approve draft or provide edits.

- `6369e6d4` - Ravenswood On Tap staffing/details
  - Block: OPS placeholders 866/867 exist and Sonat confirmed drink plan; event hours and staffing/coverage details missing.
  - Needed: whether to add COTeam shifts, hours, people per day, and whether to keep last year's mixer/RNDC plan.

## Implementation Routing

- `4e4fa6f7` - Planner task #1782 Square-to-PHPList automation
  - Block: owner reply asks for Square-to-PHPList automation; no `tour-review-worker.py` found and no matching Task Flow queue row.
  - Needed: route task #1782 to Lists/PHPList implementation worker with access to `koval-distillery.com`, or provide deployed script/proof.

