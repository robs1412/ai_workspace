import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import nationaloutreach_mail_cycle as cycle
class FailedSendRecoveryTests(unittest.TestCase):
    def fixture(self,root):
        root=Path(root);draft={'source_ref':'source@example.com','to':['owner@example.com'],'subject':'Result','task_packet':{'dedupe_key':'business-primary'}}
        failed=root/'reply.failed-10.json';failed.write_text(json.dumps(draft));packet=cycle.failed_send_task_packet({'draft':str(failed)})
        marker=root/'send-failure-recovery'/(packet['dedupe_key']+'.json');cycle.write_json(marker,packet)
        sent=root/'reply.sent-20.json';sent.write_text(json.dumps(draft));return root,sent,marker,packet
    def test_verified_delivery_closes_once_and_keeps_business_parent(self):
        with tempfile.TemporaryDirectory() as root,patch.object(cycle.shared_task_flow,'append_event') as event:
            root,sent,marker,packet=self.fixture(root)
            self.assertEqual(packet['parent_packet_dedupe_key'],'business-primary')
            normalized=cycle.shared_task_flow.build_packet(**packet)
            self.assertEqual(normalized['result_email_required'],'false')
            self.assertEqual(normalized['owner_question_required'],'false')
            self.assertEqual(normalized['output_channel'],'internal')
            result={'draft':str(sent),'message_id':'<sent@example.com>'}
            self.assertTrue(cycle.resolve_failed_send_task(root,result))
            self.assertFalse(cycle.resolve_failed_send_task(root,result))
            saved=json.loads(marker.read_text());self.assertEqual(saved['status'],'completed');self.assertEqual(saved['completion_or_blocker_email'],'<sent@example.com>');self.assertEqual(saved['parent_packet_dedupe_key'],'business-primary')
            event.assert_called_once();self.assertEqual(event.call_args.args[2],'email_send_failure_resolved')
            normalized=cycle.shared_task_flow.build_packet(**saved)
            self.assertEqual(normalized['result_email_required'],'false')
    def test_missing_message_id_or_different_recipient_cannot_close(self):
        with tempfile.TemporaryDirectory() as root,patch.object(cycle.shared_task_flow,'append_event') as event:
            root,sent,marker,packet=self.fixture(root)
            self.assertFalse(cycle.resolve_failed_send_task(root,{'draft':str(sent)}))
            draft=json.loads(sent.read_text());draft['to']=['different@example.com'];sent.write_text(json.dumps(draft))
            self.assertFalse(cycle.resolve_failed_send_task(root,{'draft':str(sent),'message_id':'<sent@example.com>'}));self.assertEqual(json.loads(marker.read_text())['status'],'blocked');event.assert_not_called()
    def test_success_without_prior_failure_does_not_create_repair_task(self):
        with tempfile.TemporaryDirectory() as root,patch.object(cycle.shared_task_flow,'append_event') as event:
            root,sent,marker,packet=self.fixture(root);marker.unlink()
            self.assertFalse(cycle.resolve_failed_send_task(root,{'draft':str(sent),'message_id':'<sent@example.com>'}));event.assert_not_called()
if __name__=='__main__':unittest.main()
