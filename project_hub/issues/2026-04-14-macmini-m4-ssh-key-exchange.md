# Macmini, M4, And MacBook SSH Key Exchange

- Master Incident ID: `AI-INC-20260414-MACMINI-M4-SSH-KEY-EXCHANGE-01`
- Date Opened: 2026-04-14
- Date Completed:
- Owner: Codex / Robert
- Priority: Medium
- Status: Macmini <-> M4 complete; M4 <-> MacBook complete

## Scope

Establish key-based SSH between `Macmini.lan` / `192.168.55.17` as user `admin` and the M4 Mac at `192.168.55.35` as user `kovaladmin`, then establish bidirectional key-based SSH between the M4 Mac and the MacBook.

## Symptoms

Robert requested a fresh machine-to-machine SSH key exchange. The default `~/.ssh/id_ed25519` key already existed on `Macmini.lan`, so Codex created a purpose-named key instead of overwriting the existing default identity.

## Root Cause

No root cause. This is access setup / workstation migration plumbing.

## Repo Logs

### ai_workspace

- Repo Log ID: `AI-INC-20260414-MACMINI-M4-SSH-KEY-EXCHANGE-01-ai_workspace`
- Commit SHA:
- Commit Date:
- Change Summary: Created this project-hub audit note. No repo code changes.

## Verification Notes

- 2026-04-14 12:47 CDT: Confirmed this session is on `Macmini.lan`, user `admin`, with local `en0` IP `192.168.55.17`.
- 2026-04-14 12:47 CDT: Confirmed `~/.ssh/id_ed25519` and `~/.ssh/id_ed25519.pub` already existed, so they were not overwritten.
- 2026-04-14 12:47 CDT: Generated `~/.ssh/id_ed25519_macmini_to_kovaladmin` with public key `~/.ssh/id_ed25519_macmini_to_kovaladmin.pub`, comment `macmini-to-kovaladmin`, and fingerprint `SHA256:F+eXrJ3kVmBB3K33Ey3Cq2S8jv98FDJIZZ2DQGP2W7E`.
- Private key contents were not printed, copied, or moved.
- 2026-04-14 12:49 CDT: SSH to `kovaladmin@192.168.55.35` succeeded using existing access. Created remote backup `/Users/kovaladmin/.ssh/authorized_keys.bak.20260414124930`, appended the `macmini-to-kovaladmin` public key to `/Users/kovaladmin/.ssh/authorized_keys`, and preserved remote permissions as `700` on `.ssh` and `600` on `authorized_keys`.
- 2026-04-14 12:49 CDT: Verified fresh key path with `ssh -i ~/.ssh/id_ed25519_macmini_to_kovaladmin -o IdentitiesOnly=yes -o BatchMode=yes kovaladmin@192.168.55.35`, returning host `Mac.lan` and user `kovaladmin`.
- 2026-04-14 12:51 CDT: Confirmed MacBook endpoint as `MacBookPro.lan`, user `robert`, IP `192.168.55.38`.
- 2026-04-14 12:51 CDT: On M4, generated purpose key `/Users/kovaladmin/.ssh/id_ed25519_m4_to_macbook`, public key `/Users/kovaladmin/.ssh/id_ed25519_m4_to_macbook.pub`, comment `m4-to-macbook`, fingerprint `SHA256:aJPvnNKu4jIRW6Vk0fz8MUhcrTj5Dk1j7ftwEI+F9HA`.
- 2026-04-14 12:51 CDT: On MacBook, generated purpose key `/Users/robert/.ssh/id_ed25519_macbook_to_m4`, public key `/Users/robert/.ssh/id_ed25519_macbook_to_m4.pub`, comment `macbook-to-m4`, fingerprint `SHA256:r7IG11t0+bo4XbJr6CGXja1HVjglMHwLX1MOzwgwC1w`.
- 2026-04-14 12:51 CDT: Appended M4 public key to `/Users/robert/.ssh/authorized_keys` on MacBook after backup `/Users/robert/.ssh/authorized_keys.bak.20260414125129`.
- 2026-04-14 12:51 CDT: Appended MacBook public key to `/Users/kovaladmin/.ssh/authorized_keys` on M4 after backup `/Users/kovaladmin/.ssh/authorized_keys.bak.20260414125130`.
- 2026-04-14 12:51 CDT: Verified M4 -> MacBook using `ssh -i ~/.ssh/id_ed25519_m4_to_macbook -o IdentitiesOnly=yes -o BatchMode=yes robert@192.168.55.38`, returning host `MacBookPro.lan` and user `robert`.
- 2026-04-14 12:51 CDT: Verified MacBook -> M4 using `ssh -i ~/.ssh/id_ed25519_macbook_to_m4 -o IdentitiesOnly=yes -o BatchMode=yes kovaladmin@192.168.55.35`, returning host `Mac.lan` and user `kovaladmin`.
- 2026-04-14 12:52 CDT: On M4, generated purpose key `/Users/kovaladmin/.ssh/id_ed25519_m4_to_macmini`, public key `/Users/kovaladmin/.ssh/id_ed25519_m4_to_macmini.pub`, comment `m4-to-macmini`, fingerprint `SHA256:LL73S8ka7ElnRPZz5L+Y49Tpy7doLdEshcGHkLHVmXw`.
- 2026-04-14 12:52 CDT: Appended M4 public key to `/Users/admin/.ssh/authorized_keys` on Mac mini after backup `/Users/admin/.ssh/authorized_keys.bak.20260414125247`.
- 2026-04-14 12:52 CDT: Verified M4 -> Mac mini using `ssh -i ~/.ssh/id_ed25519_m4_to_macmini -o IdentitiesOnly=yes -o BatchMode=yes admin@192.168.55.17`, returning host `Macmini.lan` and user `admin`.

## Rollback Plan

Remove the relevant public key lines from each target machine's `authorized_keys` file, or restore from the timestamped backups listed above. Then remove the matching purpose-named private/public key pair from the source machine if Robert decides that direction should not remain.

## Follow-Ups

- None for the requested key exchange. Optional later work: add friendly SSH host aliases on each machine so the purpose-named keys are selected automatically.
