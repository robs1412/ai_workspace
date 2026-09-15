import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import nationaloutreach_mail_cycle as cycle

class ReviewedBulkNewsletters(unittest.TestCase):
    def headers(self, **changes):
        return {'from':'Team 1871 <content@1871.com>', 'subject':'Momentum Awards: nominations are open', 'has_list_unsubscribe':'true', **changes}
    def candidate(self, h):
        body='Hi Macee, submit your nomination. Join our event and meet the team. Unsubscribe.'
        return cycle.is_newsletter_no_action_candidate(h, body, cycle.classify_message(h,body))
    def test_promotional_team_and_event_words_do_not_create_staffing_work(self):
        self.assertTrue(self.candidate(self.headers()))
    def test_owner_forward_remains_actionable(self):
        self.assertFalse(self.candidate(self.headers(**{'from':'Robert <robert@kovaldistillery.com>','subject':'Fwd: Momentum Awards'})))
    def test_personal_replies_are_not_matched_by_bulk_rule(self):
        for changes in [{'in_reply_to':'<owner@example.com>'},{'references':'<owner@example.com>'},{'subject':'Re: Momentum Awards'},{'subject':'Fwd: Momentum Awards'}]:
            with self.subTest(changes=changes):
                self.assertFalse(cycle.is_reviewed_bulk_newsletter(self.headers(**changes)))
    def test_missing_list_header_does_not_match(self):
        self.assertFalse(cycle.is_reviewed_bulk_newsletter(self.headers(has_list_unsubscribe='false')))
    def test_unreviewed_sender_does_not_match(self):
        self.assertFalse(cycle.is_reviewed_bulk_newsletter(self.headers(**{'from':'organizer@example.org'})))
    def test_lookalike_domain_does_not_match(self):
        self.assertFalse(cycle.is_reviewed_bulk_newsletter(self.headers(**{'from':'content@1871.com.example.org'})))

    def test_transactional_or_security_subject_is_not_bulk_no_action(self):
        for subject in ['Your registration confirmation', 'Invoice for membership', 'Security alert', 'Event canceled']:
            with self.subTest(subject=subject):
                self.assertFalse(cycle.is_reviewed_bulk_newsletter(self.headers(subject=subject)))

    def test_fetch_files_bulk_mail_without_queuing_an_owner_question(self):
        import json
        import tempfile
        from email.message import EmailMessage
        from unittest.mock import MagicMock, patch
        msg=EmailMessage()
        msg['From']='Team 1871 <content@1871.com>'
        msg['To']='nationaloutreach@kovaldistillery.com'
        msg['Subject']='Team event: what do you need?'
        msg['Message-ID']='<reviewed-bulk@example.org>'
        msg['List-Unsubscribe']='<mailto:unsubscribe@example.org>'
        msg.set_content('Join our team event. Can you help? Unsubscribe.')
        conn=MagicMock()
        conn.search.return_value=('OK',[b'1'])
        conn.fetch.return_value=('OK',[(b'1',msg.as_bytes())])
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(cycle.imaplib,'IMAP4_SSL',return_value=conn), \
             patch.object(cycle,'record_email_trace'), \
             patch.object(cycle.shared_task_flow,'append_event') as event, \
             patch.object(cycle,'queue_owner_question_draft') as question, \
             patch.object(cycle,'queue_routine_reply_draft') as reply:
            root=Path(temp);state=root/'state';state.mkdir();workspace=root/'workspace';workspace.mkdir()
            cycle.fetch_messages({'imap_server':'example.org','imap_port':'993','user':'test@example.org','password':'test-only'},state,workspace,1,'INBOX','ALL',False)
            question.assert_not_called();reply.assert_not_called()
            self.assertEqual(event.call_args.args[1]['status'],'no_action_closed')
            self.assertNotIn('unsubscribe@example.org',(state/'mail-review.jsonl').read_text())

if __name__=='__main__':unittest.main()
