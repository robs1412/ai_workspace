import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from frank_fintech_ack import approved_submission_ack


class FintechAckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'approvals.json'
        self.entry = dict(lane='dist', owner_approved=True, customer_id='Example Shop', retailer_name='Example Shop LLC', street='12 North Main Street', submitted_at_text='09/10/2026 05:08 PM', proof_ref='dist-account:123')
        self.path.write_text(json.dumps([self.entry]))
        self.message = {'from': 'activation@fintech.com', 'subject': 'Processing Relationship Request Submitted', 'body': 'The following request to begin processing invoice payments electronically was submitted through KOVAL, INC. on 09/10/2026 05:08 PM for Example Shop LLC. Example Shop 12 North Main Street'}

    def test_verified_receipt_matches(self):
        self.assertEqual(approved_submission_ack(self.message, self.path)['verification_readback'], 'dist-account:123')

    def test_unknown_request_or_different_identity_stays_open(self):
        for original, replacement in [('05:08 PM', '05:09 PM'), ('12 North Main Street', '14 North Main Street'), ('Example Shop LLC', 'Another Shop LLC')]:
            with self.subTest(original=original):
                msg={**self.message, 'body': self.message['body'].replace(original,replacement)}
                self.assertFalse(approved_submission_ack(msg,self.path))

    def test_sender_subject_and_action_required_are_not_receipts(self):
        for change in [{'from':'activation@other.example'}, {'subject':'Processing Relationship Request Approved'}, {'body':self.message['body']+' Action required'}, {'body':self.message['body']+' Payment failed'}]:
            with self.subTest(change=change):
                self.assertFalse(approved_submission_ack({**self.message,**change},self.path))

    def test_missing_malformed_unapproved_or_wrong_lane_proof_stays_open(self):
        for value in ['invalid', '{}', json.dumps([{**self.entry,'owner_approved':False}]), json.dumps([{**self.entry,'lane':'satla'}]), json.dumps([{**self.entry,'proof_ref':''}])]:
            self.path.write_text(value)
            self.assertFalse(approved_submission_ack(self.message,self.path))
        self.path.unlink()
        self.assertFalse(approved_submission_ack(self.message,self.path))

if __name__=='__main__':unittest.main()
