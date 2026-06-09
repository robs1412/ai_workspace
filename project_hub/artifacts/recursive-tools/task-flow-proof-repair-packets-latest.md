# Task Flow Proof Repair Packets

- Recorded: 2026-06-09 09:25:39 CDT
- Packet count: `5`
- Mutation allowed: `False`

| dedupe_key | proof_kind | status | approval | action |
| --- | --- | --- | --- | --- |
| taskflow-5cfd58716334576b | failed_approved_send_artifact | duplicate_no_action | required | recovered sent proof exists; no resend |
| taskflow-760a7508ffeabfe5 | failed_approved_send_artifact | blocked | required | no Message-ID or approved resend |
| taskflow-1db47dff91264646 | failed_approved_send_artifact | blocked | required | no Message-ID or approved resend |
| taskflow-3981bd77dabf07ce | failed_approved_send_artifact | blocked | required | no Message-ID or approved resend |
| taskflow-1513f992055a281d | failed_approved_send_artifact | blocked | required | no Message-ID or approved resend |

## Boundary

- Packets are read-only next-action records. They do not send email or update Task Flow, OPS, or Portal state.
