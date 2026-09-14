"""A worker follow-up is not daemon-owned merely because it names Vanessa."""
import ast
import json
from pathlib import Path
import subprocess
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_policy(path=None):
    path = path or ROOT / 'scripts/task_flow_due_runner.py'
    tree = ast.parse(path.read_text())
    names = {'registered_scheduled_action_ids', 'is_daemon_owned_due_item', 'workspace_for_task_flow_item'}
    functions = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
    ns = {'subprocess': subprocess, 'json': json, '_registered_scheduled_action_ids': None,
          'DAEMON_OWNED_DUE_WORKSPACES': {'nationaloutreach'}}
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), 'exec'), ns)
    return ns


class DaemonOwnershipTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_policy()
        self.ns['_registered_scheduled_action_ids'] = frozenset({'vanessa-day-of-cot-event-details-2026-09-14-0800'})
        self.item = {'owner_lane': 'nationaloutreach', 'responsible_worker_or_persona': 'Vanessa Sterling'}

    def test_business_followups_are_not_silently_skipped(self):
        for action in ["Check the exact thread for Michael's tasting-date response",
                       'Recheck coverage for open COTeam shift6054',
                       'Vanessa files the OOO-only source without reply']:
            self.assertFalse(self.ns['is_daemon_owned_due_item'](dict(self.item, scheduled_action=action)))

    def test_registered_notification_stays_with_sender(self):
        item = dict(self.item, scheduled_action='vanessa-day-of-cot-event-details-2026-09-14-0800')
        self.assertTrue(self.ns['is_daemon_owned_due_item'](item))
        self.assertFalse(self.ns['is_daemon_owned_due_item'](dict(item, recurrence_rule='owner_reply_daily_repeat')))
        self.assertFalse(self.ns['is_daemon_owned_due_item'](dict(item, owner_lane='frank', responsible_worker_or_persona='frank')))

    def test_lookup_failure_does_not_invent_ownership_or_route_notifications(self):
        self.ns['_registered_scheduled_action_ids'] = None
        with mock.patch.object(subprocess, 'run', side_effect=subprocess.TimeoutExpired('php', 20)):
            with self.assertRaises(subprocess.TimeoutExpired):
                self.ns['is_daemon_owned_due_item'](dict(self.item, scheduled_action='registered-but-not-loaded'))
        self.assertIsNone(self.ns['_registered_scheduled_action_ids'])


if __name__ == '__main__':
    unittest.main()
