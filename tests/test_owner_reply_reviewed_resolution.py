import ast
import json
import subprocess
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock


class ReviewedResolutionTests(unittest.TestCase):
    def setUp(self):
        source = Path(__file__).resolve().parents[1] / 'scripts/ai_health_check.py'
        tree = ast.parse(source.read_text())
        wanted = {'owner_reply_has_reviewed_resolution', 'record_owner_reply_task_flow'}
        functions = ast.Module(body=[n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted], type_ignores=[])
        self.process = SimpleNamespace(run=Mock(), TimeoutExpired=subprocess.TimeoutExpired)
        self.ns = dict(json=json, subprocess=self.process, argparse=SimpleNamespace(Namespace=object),
                       normalize_message_id=lambda v: str(v or '').strip('<>').lower(),
                       task_flow_owner_reply_key=lambda r: 'exact-wrapper')
        exec(compile(functions, str(source), 'exec'), self.ns)
        self.reply = {'source_message_id': 'source@example.test'}
        self.row = dict(status='filed_no_action', source_ref='source@example.test')
        self.proof = dict(source_ref='source@example.test', disposition='acknowledgement_only',
                          reviewed_at='2026-09-15', source_excerpt='Thank you!')

    def check(self, expected):
        self.row['packet_json'] = json.dumps({'owner_reply_resolution': self.proof})
        self.process.run.return_value = SimpleNamespace(returncode=0, stdout=json.dumps(self.row))
        self.assertEqual(self.ns['owner_reply_has_reviewed_resolution'](self.reply), expected)

    def test_reviewed_ack_skips_recorder_and_nudges(self):
        self.check(True)
        self.assertEqual(self.ns['record_owner_reply_task_flow'](object(), self.reply),
                         (True, 'proof-backed-primary:exact-wrapper'))

    def test_explicit_owner_closure(self):
        self.row['status'] = 'closed_with_proof'
        self.proof['disposition'] = 'owner_explicitly_closed'
        self.check(True)

    def test_generic_filed_label_is_insufficient(self):
        self.proof = {}
        self.check(False)

    def test_later_reply_cannot_inherit_older_resolution(self):
        self.proof['source_ref'] = 'older@example.test'
        self.check(False)

    def test_reopened_work_is_not_suppressed(self):
        self.row['status'] = 'working'
        self.check(False)

    def test_blocker_email_is_not_resolution(self):
        self.proof['disposition'] = 'technical_blocker_sent'
        self.check(False)

    def test_database_failure_does_not_claim_resolution(self):
        self.process.run.return_value = SimpleNamespace(returncode=1, stdout='')
        self.assertFalse(self.ns['owner_reply_has_reviewed_resolution'](self.reply))


if __name__ == '__main__':
    unittest.main()
