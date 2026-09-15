import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import nationaloutreach_mail_cycle as cycle


class InvitationRoutingTests(unittest.TestCase):
    def test_impersonated_invitation_is_not_a_vanessa_task(self):
        for link in ['https://unrelated.example/yes_no/', 'https://paperlesspost.com.attacker.example/card']:
            body = 'Paperless Post\nVIEW THE CARD <' + link + '>\nDinner gathering party'
            result = cycle.classify_message({'subject': 'Dinner invitation', 'from': 'host@example.net'}, body)
            self.assertEqual(result['route'], 'security-guard')
            self.assertEqual(result['send_allowed'], 'no')
            self.assertEqual(cycle.task_flow_persona_for_route(result['route']), 'security-guard')

    def test_provider_and_subdomain_links_are_preserved(self):
        for link in ['https://paperlesspost.com/card', 'https://www.paperlesspost.com/card', 'https://links.paperlesspost.com/card']:
            self.assertFalse(cycle.has_mismatched_invitation_link('Paperless Post\nVIEW THE CARD <' + link + '>'))

    def test_unrelated_events_and_footer_mentions_are_not_flagged(self):
        self.assertFalse(cycle.has_mismatched_invitation_link('Dinner at Whole Foods. https://example.net/'))
        self.assertFalse(cycle.has_mismatched_invitation_link('I previously used Paperless Post. Please add this tasting.'))

    def test_markdown_card_link_is_checked(self):
        self.assertTrue(cycle.has_mismatched_invitation_link('Paperless Post\n[VIEW THE CARD](https://unrelated.example/card)'))


if __name__ == '__main__':
    unittest.main()
