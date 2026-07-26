# Avignon Request Samples Guidance

Updated: 2026-07-08

This is the standing Avignon guidance for Sonat sample-request work.

- If Sonat asks Avignon to request samples, create samples, or asks for products, treat it as a regular POS/Samples sample request unless Sonat explicitly says `barrel sample`.
- Regular product/sample requests should use Portal:
  - `https://portal.koval-distillery.com/#/pos-and-samples/sample-request/create`
- If Sonat means a barrel sample, she will say `barrel sample`. Do not infer barrel workflow from a generic request for products.
- If Sonat says `barrel sample`, `barrel`, `reserve`, `select barrel`, `mark sold`, or links/references WH Barrel Program pages, use `BARREL_PROGRAM_GUIDANCE.md` and route the request to Barrel Sales Manager rather than treating it as a generic product/sample request.
- Barrel sample requests are created at `https://portal.koval-distillery.com/#/pos-and-samples/sample-request/create` with the `barrel samples` toggle switched on. In the Notes field, describe the exact barrel samples requested, for example `Rye 55%`, `Rye 50%`, or `Bourbon 55%`. If Sonat says `cask strength`, treat that as `55%`.
- For barrel samples, fill `Date Needed` from the date Sonat gives. If Sonat gives no date, use the next calendar day from the request date. If Sonat requests the samples for herself, use pickup delivery and put Sonat's name in the pickup/shipping details.
- The account field must be the account for whom the samples are requested, not KOVAL or Sonat, unless Sonat explicitly says the samples are for KOVAL/internal use.
- For any Avignon-routed Portal sample request creation, require notification-status verification in the closeout. The Portal worker must state whether regular-sample or barrel-sample notifications were sent. If a helper/direct DB path bypassed the normal Portal notification flow, stop with a blocker or route a Portal-owned notification-send/fix follow-up before reporting the sample request as fully complete.
- The `Process for Sample Requests` SOP/persona instruction is a directive to record this standing guidance, not a blocker requiring Sonat to rediscover the old email.
- The Notes field must begin with a written narrative description of what sample is being requested, who it is for, and the business purpose. Example: `We need to send one bottle of Thresh and Winnow Rye to Danny at M. Shanken for review for a feature.`
- If Sonat provides a needed-by date, include it in the sample request. Translate relative dates such as `next Wednesday` into the exact calendar date before entry.
- If no recipient/shipment phone number is provided, use Robert's phone number for the shipment phone field because the shipper requires a phone number. Do not expose or print the phone number in logs or owner-facing notes beyond the Portal/OPS field where it is required.
- A source `Message-ID` may be added for traceability, but put it at the bottom of the Notes field after the narrative and request details.
- After any sample request, barrel sample or otherwise, Avignon must let Sonat know when the request has been entered in the system. The completion confirmation must include the live request link or request id and the notification proof status.
- For a specific sample request, use a human-readable working packet. Ask only for missing fields needed to complete the Portal entry, such as:
  - account/company or recipient
  - contact/person
  - products/SKUs and quantity
  - purpose or event/use case
  - shipping, pickup, or delivery details
  - needed-by date
  - notes or approval boundary
- Decision/blocker emails must not ask Robert or Sonat to act from Message-IDs alone. Use Message-IDs only as trace references after the human-readable context.
