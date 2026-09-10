# Fintech submission acknowledgments

Robert approved this Frank runtime rule on 2026-09-10 after the Rogers Park Provisions request generated an unnecessary decision email.

The exact subject `Processing Relationship Request Submitted` from `activation@fintech.com` is routine only when its body matches an owner-approved request in the runtime state's `fintech-submission-approvals.json`: exact retailer name, customer ID, street, submission date/time, DIST lane, and a durable proof reference. The request worker must register those non-secret facts after FMS creation/readback. Do not add entries based only on an incoming email.

Log matching receipts as `fintech-approved-submission-ack`, file them to Handled, and suppress decision emails. Keep the underlying relationship's Waiting on Retailer status in DIST until live FMS verifies activation. This receipt does not prove activation, invoice submission, or payment.

Missing proof, a different request, a changed subject or sender, rejection, cancellation, failure, or action-required wording must use normal review. No external replies or invoice/payment actions are authorized by this rule.
