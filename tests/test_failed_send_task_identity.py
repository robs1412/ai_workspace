import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import nationaloutreach_mail_cycle as cycle

class FailedSendTaskIdentityTests(unittest.TestCase):
    def packet(self, root, name, draft):
        p=Path(root)/name
        p.write_text(json.dumps(draft) if draft is not None else 'invalid json')
        return cycle.failed_send_task_packet({'draft':str(p),'error_type':'SMTPException'})
    def test_repeated_failure_is_one_repair_task_with_latest_attempt_path(self):
        with tempfile.TemporaryDirectory() as root:
            draft={'source_ref':'<original@example.com>','subject':'Re: Request','to':['owner@example.com'],'body':'First reply','task_packet':{'dedupe_key':'primary'}}
            a=self.packet(root,'reply.failed-100.json',draft)
            draft['body']='Revised reply'
            b=self.packet(root,'reply.failed-200.json',draft)
            self.assertEqual(a['dedupe_key'],b['dedupe_key'])
            self.assertNotEqual(a['failed_draft_path'],b['failed_draft_path'])
            self.assertEqual(b['parent_task_key'],'primary')
            self.assertEqual(b['source_ref'],'<original@example.com>')
            self.assertNotEqual(b['dedupe_key'],'primary')
            self.assertEqual(b['status'],'blocked')
    def test_distinct_recipients_and_actions_remain_separate(self):
        with tempfile.TemporaryDirectory() as root:
            draft={'source_ref':'source','to':['one@example.com'],'action_id':'first'}
            a=self.packet(root,'a.json',draft)
            draft['to']=['two@example.com'];b=self.packet(root,'b.json',draft)
            self.assertNotEqual(a['dedupe_key'],b['dedupe_key'])
            draft['action_id']='second';c=self.packet(root,'c.json',draft)
            self.assertNotEqual(b['dedupe_key'],c['dedupe_key'])
    def test_recipient_order_does_not_create_a_second_task(self):
        with tempfile.TemporaryDirectory() as root:
            draft={'source_ref':'source','to':['one@example.com','two@example.com']}
            a=self.packet(root,'a.json',draft);draft['to'].reverse();b=self.packet(root,'b.json',draft)
            self.assertEqual(a['dedupe_key'],b['dedupe_key'])
    def test_malformed_retry_files_group_without_disappearing(self):
        with tempfile.TemporaryDirectory() as root:
            a=self.packet(root,'reply.failed-100.json',None);b=self.packet(root,'reply.failed-200.json',None)
            self.assertEqual(a['dedupe_key'],b['dedupe_key'])
            self.assertEqual(a['status'],'blocked')
            self.assertNotEqual(a['dedupe_key'],self.packet(root,'other.failed-100.json',None)['dedupe_key'])
if __name__=='__main__':unittest.main()
