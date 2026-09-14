import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import shared_task_flow as flow

class ScheduledSendTaskLinkTests(unittest.TestCase):
    def test_sent_action_without_ops_id_can_finish(self):
        packet = flow.packet_from_scheduled_action({'id':'vanessa-checkin-2026-09-14','ops_task_id':0})
        packet.update(status='reported', completion_or_blocker_email='<test@example.com>', verification_readback='Sent proof recorded via Message-ID in sent-log.')
        guarded, info = flow.guard_packet(packet, 'email_sent')
        self.assertEqual(guarded['ops_portal_or_domain_task'], 'scheduled-action:vanessa-checkin-2026-09-14')
        self.assertTrue(info['closeout_allowed'], info)
        self.assertEqual(guarded['status'], 'reported')

    def test_existing_domain_link_is_preserved(self):
        for field, value in [('ops_portal_or_domain_task','portal:48'), ('ops_task_id',378183), ('portal_task_id',42)]:
            packet = flow.packet_from_scheduled_action({'id':'send-instance',field:value})
            self.assertEqual(packet['ops_portal_or_domain_task'], str(value))

    def test_missing_action_id_and_send_proof_still_block(self):
        packet = flow.packet_from_scheduled_action({'source_ref':'source-only','ops_task_id':'0'})
        packet['status']='reported'
        guarded, info = flow.guard_packet(packet, 'email_sent')
        self.assertFalse(info['closeout_allowed'])
        self.assertIn('ops_portal_or_domain_task', info['missing_fields'])
        self.assertIn('completion_or_blocker_email', info['missing_fields'])
        self.assertEqual(guarded['status'],'blocked')

if __name__ == '__main__': unittest.main()
