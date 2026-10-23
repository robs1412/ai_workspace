import ast
import json
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]


def policy():
    tree=ast.parse((ROOT/'scripts/task_flow_due_runner.py').read_text())
    names={'existing_handoff_keys','reminder_key','route_due_items_to_worker'}
    ns={'Path':Path,'json':json,'time':time,'os':os,'FanoutGuard':object,
        'registered_scheduled_action_ids':lambda:frozenset({'scheduled-1'}),
        'is_daemon_owned_due_item':lambda item:item.get('scheduled_action')=='scheduled-1',
        'workspace_for_task_flow_item':lambda item:'nationaloutreach',
        'build_worker_handoff_message':lambda items:'Review exact sources',
        'DEFAULT_WORKSPACEBOARD_URL':'http://127.0.0.1:17878',
        'is_owner_reply_daily_item':lambda item:False}
    exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names],type_ignores=[]),'policy','exec'),ns)
    return ns


class DueQueueRecoveryTests(unittest.TestCase):
    def test_old_false_daemon_skip_does_not_count_as_worker_delivery(self):
        ns=policy()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'handoffs.jsonl'
            p.write_text('\n'.join(json.dumps(r) for r in [
                {'event':'daemon_owned_due_item_skipped','handoff_key':'business|today|Check the tasting reply'},
                {'event':'daemon_owned_due_item_skipped','handoff_key':'auto|today|scheduled-1'},
                {'event':'worker_handoff_routed','handoff_key':'real|today|Check another reply'}]))
            self.assertEqual(ns['existing_handoff_keys'](p),{'auto|today|scheduled-1','real|today|Check another reply'})

    def test_dry_run_does_not_record_a_delivery(self):
        ns=policy()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);result=ns['route_due_items_to_worker'](p/'recorder',p,[{'dedupe_key':'auto','scheduled_action':'scheduled-1'}],mock.Mock(),dry_run=True)
            self.assertEqual(result['reason'],'daemon_owned_items_handled_in_runtime')
            self.assertFalse((p/'task-flow-worker-handoffs.jsonl').exists())

    def test_existing_worker_does_not_starve_an_unrouted_task(self):
        ns=policy();guard=mock.Mock();guard.can_create.return_value=(True,'ok')
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);items=[{'dedupe_key':'existing','workspaceboard_session':'old-worker'}, {'dedupe_key':'fresh'}]
            result=ns['route_due_items_to_worker'](p/'recorder',p,items,guard,dry_run=True)
            self.assertTrue(any(r.get('dry_run') and r['items']==['fresh'] for r in result['items']))
            self.assertEqual(guard.can_create.call_args.args[0],[items[1]])

    def test_pending_prompt_is_recorded_without_retry_or_success_receipt(self):
        ns=policy();guard=mock.Mock();guard.can_create.return_value=(True,'ok')
        ns['create_worker_route_session']=mock.Mock(return_value=('pending-worker',{}))
        ns['deliver_worker_route_message']=mock.Mock(side_effect=RuntimeError('HTTP 409: prompt_pending_in_composer'))
        ns['record_blocked_packet']=mock.Mock(return_value={'ok':True})
        ns['record_routed_packet']=mock.Mock()
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            result=ns['route_due_items_to_worker'](p/'recorder',p,[{'dedupe_key':'due'}],guard)
            self.assertFalse(result['routed'])
            self.assertEqual(result['items'][0]['failed_session_id'],'pending-worker')
            self.assertEqual(ns['record_blocked_packet'].call_args.kwargs['session_id'],'pending-worker')
            ns['deliver_worker_route_message'].assert_called_once()
            ns['record_routed_packet'].assert_not_called()
            self.assertFalse((p/'task-flow-worker-handoffs.jsonl').exists())

    def test_creation_failure_does_not_abort_other_workspaces(self):
        ns=policy();guard=mock.Mock();guard.can_create.return_value=(True,'ok')
        ns['workspace_for_task_flow_item']=lambda item:item['workspace']
        ns['create_worker_route_session']=mock.Mock(side_effect=[RuntimeError('unavailable'),('accepted-worker',{})])
        ns['deliver_worker_route_message']=mock.Mock(return_value={'prompt_delivery':{'ok':True}})
        ns['record_blocked_packet']=mock.Mock(return_value={'ok':True})
        ns['record_routed_packet']=mock.Mock(return_value={'ok':True})
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            items=[{'dedupe_key':'failed','workspace':'ai'},{'dedupe_key':'good','workspace':'bid'}]
            result=ns['route_due_items_to_worker'](p/'recorder',p,items,guard)
            self.assertTrue(result['routed'])
            self.assertFalse(result['items'][0]['routed'])
            self.assertEqual(result['items'][1]['session_id'],'accepted-worker')
            rows=[json.loads(line) for line in (p/'task-flow-worker-handoffs.jsonl').read_text().splitlines()]
            self.assertEqual([r['dedupe_key'] for r in rows],['good'])

    def test_blocked_packet_retains_created_worker_for_followthrough(self):
        tree=ast.parse((ROOT/'scripts/task_flow_due_runner.py').read_text())
        fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='record_blocked_packet')
        shared=mock.Mock();shared.build_packet.side_effect=lambda **kw:kw
        ns={'Path':Path,'shared_task_flow':shared,'record_task_flow_packet':lambda recorder,packet,event:packet}
        exec(compile(ast.Module(body=[fn],type_ignores=[]),'blocked','exec'),ns)
        packet=ns['record_blocked_packet'](Path('unused'),{'dedupe_key':'due'},'pending','inspect',session_id='worker')
        self.assertEqual(packet['workspaceboard_session'],'worker')
        self.assertEqual(packet['status'],'blocked')


if __name__=='__main__':unittest.main()
