"""Verify actual owner-send boundaries without mailbox or network access."""
import ast
from pathlib import Path
import re
import unittest
from unittest.mock import Mock

SOURCE = Path(__file__).resolve().parents[1] / 'avignon/runtime-source/avignon-launch/scripts/avignon_inbox_cycle.py'

def load(path=SOURCE):
    names={'owner_blocker_email_gate','compose_direct_owner_closeout','monitor_direct_owner_action','session_has_pending_approval','session_business_completion_proof','session_blocker_text','session_owner_question_text'}
    tree=ast.parse(path.read_text()); tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
    scope={'re':re};exec(compile(tree,str(path),'exec'),scope);return scope

class OwnerBlockerGateTests(unittest.TestCase):
    def test_technical_and_missing_context_never_compose(self):
        for path in (SOURCE, Path('/Users/admin/.avignon-launch/runtime/scripts/avignon_inbox_cycle.py')):
            if not path.exists(): continue
            s=load(path)
            for text in ("2. Yes, and don't ask again for commands that start with `php -r` Press enter to confirm or esc to cancel", 'Required email-worker-inbox-management skill unavailable in configured local skill locations', 'HTTP 500 updating Portal', 'Permission denied reading source body', 'Worker session closed before proof', ''):
                with self.subTest(runtime=path==SOURCE,text=text):
                    session={'status':'blocked','owner_question':'Please approve this next action?', 'blocker':text} if text else {'status':'blocked'}
                    with self.assertRaises(ValueError):s['compose_direct_owner_closeout']({'subject':'Wendella'},session,True,{'summary':text})

    def test_business_question_preserved_exactly(self):
        s=load();q='Do you approve the proposed tasting date of October 3?'
        self.assertEqual(s['owner_blocker_email_gate']({'owner_question':q},{'summary':'Venue offers October 3.'}), '')
        s.update(normalized_subject=lambda x:x,session_summary_has_active_context=lambda x:False)
        body=s['compose_direct_owner_closeout']({'subject':'Tasting'}, {'owner_question':q},True,{'summary':'Venue offers October 3.'})
        self.assertIn(q,body);self.assertNotIn('workflow to automate',body)

    def test_monitor_keeps_unclassified_blocker_open_without_send(self):
        for path in (SOURCE,Path('/Users/admin/.avignon-launch/runtime/scripts/avignon_inbox_cycle.py')):
            if not path.exists():continue
            s=load(path);send=Mock(side_effect=AssertionError('Must not email'))
            s.update(DIRECT_OWNER_DONE_STATES=set(),DIRECT_OWNER_PENDING_STATES={'routed_pending_completion'},
                direct_owner_closeout_report=lambda *a:{},load_avignon_sent_logs=lambda:[],
                board_session_status=lambda sid:{'status':'blocked'},board_session_summary=lambda sid:{'summary':'No result available'},
                is_internal_route_blocker_text=lambda *a:False,send_avignon_owner_email=send)
            result=s['monitor_direct_owner_action']({'current_state':'routed_pending_completion','routed_session_id':'test'})
            self.assertEqual(result['monitor_state'],'internal-recovery-required');self.assertFalse(result['archivable_now']);send.assert_not_called()

    def test_route_exception_has_no_send_path(self):
        tree=ast.parse(SOURCE.read_text());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='handle_direct_owner_message')
        for node in ast.walk(fn):
            if isinstance(node,ast.ExceptHandler):
                self.assertFalse(any(isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='send_avignon_owner_email' for x in ast.walk(node)))

if __name__=='__main__':unittest.main()
