import ast
from pathlib import Path
import unittest
from unittest import mock
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'frank/runtime-source/frank-launch/scripts/frank_auto_runner.py'


def load_gate(work):
    tree = ast.parse(SOURCE.read_text())
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in
                 {'verified_direct_primary_closeout', 'monitor_direct_primary_action', 'task_flow_status_from_action'}]
    ns = {'urllib': urllib, 'Path': Path, 'get_json': lambda url: {'current_work_state': {'taskflow_key': 'task-test', **work}},
          'DIRECT_PRIMARY_DONE_STATES': set(), 'DIRECT_PRIMARY_PENDING_STATES': {'routed_pending_completion'},
          'direct_primary_closeout_state': lambda *args: '',
          'board_session_status': lambda session: {'status': 'blocked'},
          'board_session_summary': lambda session: {'summary': "Press enter to confirm or esc to cancel"},
          'send_plain_email': mock.Mock(side_effect=AssertionError('Must not send'))}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), 'exec'), ns)
    return ns


class FrankCloseoutProofTests(unittest.TestCase):
    def test_technical_blocker_keeps_work_visible_and_sends_nothing(self):
        ns = load_gate({'work_state': 'blocked', 'owner_question': 'Please approve php -r read', 'blocker_text': 'Press enter to confirm'})
        action = {'current_state': 'routed_pending_completion', 'routed_session_id': 'test', 'dedupe_key': 'task-test'}
        result = ns['monitor_direct_primary_action'](action, {}, '', '', Path('.'), Path('.'), '', '', True, '')
        self.assertFalse(result['archivable_now'])
        self.assertEqual(ns['task_flow_status_from_action'](result), 'queued')
        ns['send_plain_email'].assert_not_called()

    def test_stopped_worker_without_proof_is_not_complete(self):
        ns = load_gate({'work_state': 'closed_with_proof', 'proof_marker': ''})
        self.assertFalse(ns['verified_direct_primary_closeout']('test', False, 'task-test')[0])

    def test_verified_completion_and_real_business_question_are_allowed(self):
        ns = load_gate({'work_state': 'closed_with_proof', 'proof_marker': 'CRM contact381337 created and read back'})
        self.assertTrue(ns['verified_direct_primary_closeout']('test', False, 'task-test')[0])
        ns = load_gate({'work_state': 'blocked', 'owner_question': 'Approve the quoted $250 event fee?', 'escalation_persona': 'Robert'})
        self.assertEqual(ns['verified_direct_primary_closeout']('test', True, 'task-test'), (True, 'Approve the quoted $250 event fee?'))

    def test_shared_worker_proof_for_another_task_is_rejected(self):
        ns = load_gate({'taskflow_key': 'another-task', 'work_state': 'closed_with_proof', 'proof_marker': 'Other task completed'})
        self.assertFalse(ns['verified_direct_primary_closeout']('test', False, 'task-test')[0])

    def test_readback_failure_does_not_generate_owner_question(self):
        ns = load_gate({})
        ns['get_json'] = mock.Mock(side_effect=RuntimeError('offline'))
        self.assertFalse(ns['verified_direct_primary_closeout']('test', True, 'task-test')[0])


if __name__ == '__main__':
    unittest.main()
