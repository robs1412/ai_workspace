# RyeBirnecker.com Site Update

Date: 2026-07-19 CDT
Status: completed on the live Joomla site; final responsive media-photo crop applied and verified
Owner: Robert
Shared OPS task: `376209` (`Completed`, due/start 2026-07-20, assignees Robert and Codex)

## Requested Changes

- Add a `Reel` section to the Media page using YouTube video `TthmW4A19Pc`.
- Media order: Reel, Films, Piano Demo Clips, Drama Demo Clip.
- Remove the Monologue and Comedy Demo Clip entries.
- Change the final heading from `Drama Demo Clip 1` to `Drama Demo Clip`.
- Replace the site resume with the current AI Cloud file `Rye's Resume.pdf`.
- Replace the bio with:

  > Rye is a dedicated actor who booked the first film role he ever auditioned for and continues to gain experience in film, television, and commercials. His training includes theater, improv, dance, and on-camera technique at respected schools across Chicago, including Second City, Piven Theatre, and Actors Training Center, while his experience in dance and martial arts rounds out his training. Rye is fluent in German and has a valid passport.

- Remove Washington, DC from local-hire availability.
- Change the visible copyright year to `2026`.
- Add Casting Networks at the bottom right using the correct current logo and preserving the existing footer layout.
- Adjust the site photo after the exact desired crop/position/size change is confirmed.

## Final Media Photo Adjustment

- Owner direction received 2026-07-19: move the head up a little on iPhone and substantially more on desktop.
- Live mobile rule now uses `background-position: 50% 50%` with `background-size: auto 105%`, producing a small upward crop while preserving the centered portrait.
- Live desktop rule at `min-width: 960px` uses `background-position: 50% 15%` with the existing cover behavior, producing the larger upward shift.
- Recoverable pre-change backup: Joomla content row `id=2` in `eerlj_content_backup_20260719_media_crop`.
- Live HTTP readback confirmed both responsive rules on `https://www.ryebirnecker.com/`.
- Existing OPS task `376209` reads back `Completed`.

## Final Bio And Resume Logo Correction

- Replaced the live homepage About Rye copy with the owner-provided bio verbatim.
- Replaced the obsolete Resume-page `casting_networks_icon.svg` with the same current `CN_Logo_fixed.svg` used in the bottom-right footer; the Casting Networks profile URL was preserved.
- Recoverable pre-change backup: Joomla content rows `id=2` and `id=6` in `eerlj_content_backup_20260719_bio_resume_cn`.
- Live HTTP readback confirmed the exact bio, two correct Casting Networks logo references on the Resume page, no obsolete Resume-page logo reference, and HTTP `200` for the logo asset.

## Verified Sources

- AI Cloud folder contained one file: `Rye's Resume.pdf`, modified `2026-07-18T21:08:35Z`, size `71,251` bytes.
- Downloaded working asset: `tmp/ryebirnecker-2026-07-19/Rye-Resume.pdf`.
- SHA-256: `d93c54fbf21630ebef50ad7d6f6f40b2233accfff403421bd6da126573a5e944`.
- PDF text readback contains `Servus am Abend / Self / Red Bull Media House`.
- YouTube oEmbed readback identifies video `TthmW4A19Pc` as `Rye Birnecker | Acting Reel` by Rye Birnecker.
- The official Casting Networks homepage currently serves its primary logo as `CN_Logo_fixed.svg`; use an official current asset rather than assuming the older site SVG is correct.

## Access Blocker

- Approved SSH route attempted: shell user `claude` on `koval.lan` / `192.168.55.205` using the approved askpass workflow.
- SSH timed out before authentication.
- Mac mini route state for `192.168.55.205` was `REJECT`; ARP neighbor state was incomplete and direct ping/TCP checks received no host response.
- Public `https://ryebirnecker.com/` redirected to `https://www.ryebirnecker.com/406.shtml`; the destination returned 404. Public content therefore could not be used as a trustworthy source copy.
- No live site files, DNS, router settings, authentication settings, or unrelated local repositories were changed.

## InMotion Readback

- The canonical SSH route `ftp.koval-distillery.com` succeeds as user `koval` on `vps125145.inmotionhosting.com`.
- The domain directory exists at `/home/koval/sites/ryebirnecker.com`.
- The directory is a Joomla/YOOtheme installation and is not a git checkout.
- Joomla DB readback shows content records for Start, About Me, Contact, Gallery, Resume, and Media, plus a published YOOtheme Footer module.
- The InMotion copy already contains older resume/image assets and an older `images/casting_networks_icon.svg`.
- Owner clarification: this Joomla site is outdated. Do not use it as the source of truth or deploy it over the newer site. It is only a possible deployment target after the `.205` source is recovered and compared.

## Resume Point

1. Restore or power on host `reatan` at `192.168.55.205`.
2. Re-run the approved `claude@koval.lan` SSH path and identify the newer RyeBirnecker source/deployment workflow.
3. Compare the `.205` source with `/home/koval/sites/ryebirnecker.com`; do not copy the outdated Joomla tree over the newer site.
4. Make recoverable backups of the actual source and deployment target.
5. Apply the requested media, bio, resume, local-hire, copyright-year, Casting Networks logo, Drama Demo title, and photo changes to the newer source.
6. If InMotion is confirmed as the intended target, deploy only the validated updated source/assets through the working `ftp.koval-distillery.com` SSH route.
7. Verify page order, removed clips, bio, local-hire text, copyright year, footer logo placement, resume download, reel embed, photo treatment, and responsive layout through live HTTP readback.
