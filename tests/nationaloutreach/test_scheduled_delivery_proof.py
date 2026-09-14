"""Regression for delivered reminders rejected by the Task Flow proof gate."""
import ast
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[2]


def load_helper(path):
    tree = ast.parse(path.read_text())
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'scheduled_delivery_packet')
    namespace = {}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(path), 'exec'), namespace)
    return namespace['scheduled_delivery_packet']


def php_accepts_sent_proof(packet):
    source = (ROOT / 'scripts/task_flow_mysql_recorder.php').read_text()
    functions = []
    for name in ['task_flow_packet_json', 'task_flow_has_sent_proof']:
        start = source.index('function ' + name + '(')
        end = source.index('\nfunction ', start + 1)
        functions.append(source[start:end])
    code = '\n'.join(functions) + '\necho json_encode(task_flow_has_sent_proof(json_decode(stream_get_contents(STDIN),true)));'
    return json.loads(subprocess.check_output(['php', '-r', code], input=json.dumps(packet), text=True))


class ScheduledDeliveryProofTests(unittest.TestCase):
    def setUp(self):
        self.fix = load_helper(ROOT / 'scripts/nationaloutreach_mail_cycle.py')
        self.message = '<delivery-proof@example.com>'
        self.packet = {'status': 'reported', 'intake_channel': 'scheduled-action:nationaloutreach',
                       'scheduled_action': 'dated-notification-123',
                       'completion_or_blocker_email': self.message,
                       'verification_readback': 'generated from live OPS Outreach event data for same-day sending',
                       'next_update': 'Pending approved send cycle', 'ops_portal_or_domain_task': '367971'}

    def test_successful_occurrence_passes_real_php_proof_gate(self):
        self.assertFalse(php_accepts_sent_proof(self.packet))
        fixed = self.fix(self.packet, self.message, 'dated-notification-123')
        self.assertTrue(php_accepts_sent_proof(fixed))
        self.assertEqual(fixed['ops_portal_or_domain_task'], '367971')
        self.assertEqual(self.packet['next_update'], 'Pending approved send cycle')

    def test_acknowledgement_and_owner_question_remain_open(self):
        for status in ['waiting', 'clarification_sent']:
            p = dict(self.packet, status=status)
            self.assertEqual(self.fix(p, self.message, 'dated-notification-123'), p)

    def test_other_task_or_missing_delivery_cannot_gain_proof(self):
        for message, action in [('', 'dated-notification-123'), (self.message, ''),
                                (self.message, 'different-occurrence'), ('<wrong@example.com>', 'dated-notification-123')]:
            self.assertEqual(self.fix(self.packet, message, action), self.packet)



if __name__ == '__main__':
    unittest.main()
