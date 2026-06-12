from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


SCRIPTS_DIR = Path("/Users/werkstatt/ai_workspace/scripts")
MODULE_PATH = SCRIPTS_DIR / "email_worker_header_poll.py"


def load_module():
    sys.path.insert(0, str(SCRIPTS_DIR))
    spec = importlib.util.spec_from_file_location("email_worker_header_poll_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class CultivaterOwnerRoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_asher_robert_review_packet_redirects_to_sonat(self) -> None:
        to_addrs, cc_addrs, bcc_addrs, reason = self.module.normalize_cultivater_owner_recipients(
            "asher",
            {},
            ["Robert Birnecker <robert@kovaldistillery.com>"],
            [],
            ["sonat@kovaldistillery.com"],
        )

        self.assertEqual(to_addrs, ["sonat@kovaldistillery.com"])
        self.assertEqual(cc_addrs, [])
        self.assertEqual(bcc_addrs, [])
        self.assertEqual(reason, "robert_recipient_redirected_to_sonat")

    def test_venetia_robert_cc_redirects_to_sonat(self) -> None:
        to_addrs, cc_addrs, bcc_addrs, reason = self.module.normalize_cultivater_owner_recipients(
            "venetia",
            {},
            ["draft-review@example.com"],
            ["robert@kovaldistillery.com"],
            [],
        )

        self.assertEqual(to_addrs, ["sonat@kovaldistillery.com", "draft-review@example.com"])
        self.assertEqual(cc_addrs, [])
        self.assertEqual(bcc_addrs, [])
        self.assertEqual(reason, "robert_recipient_redirected_to_sonat")

    def test_explicit_robert_recipient_opt_in_is_preserved(self) -> None:
        to_addrs, cc_addrs, bcc_addrs, reason = self.module.normalize_cultivater_owner_recipients(
            "asher",
            {"allow_robert_recipient": "true"},
            ["robert@kovaldistillery.com"],
            [],
            [],
        )

        self.assertEqual(to_addrs, ["robert@kovaldistillery.com"])
        self.assertEqual(cc_addrs, [])
        self.assertEqual(bcc_addrs, [])
        self.assertEqual(reason, "")


if __name__ == "__main__":
    unittest.main()
