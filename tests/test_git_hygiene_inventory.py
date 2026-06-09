#!/usr/local/bin/python3.13
"""Regression coverage for read-only Git hygiene action planning."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "git_hygiene_inventory.py"


def load_module():
    spec = importlib.util.spec_from_file_location("git_hygiene_inventory", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def row(repo: str, *, ahead_behind: str = "", tracked_dirty: int = 1, untracked: int = 0):
    return {
        "repo": repo,
        "branch": "main",
        "head": "abc1234",
        "remote": "git@example.test/repo.git",
        "ahead_behind": ahead_behind,
        "tracked_dirty": tracked_dirty,
        "untracked": untracked,
        "sample_tracked": [" M app.py"] if tracked_dirty else [],
        "sample_untracked": ["?? tmp.txt"] if untracked else [],
        "tracked_groups": [],
        "untracked_groups": [],
    }


class GitHygieneInventoryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = load_module()

    def test_ahead_behind_counts_parses_status_fragment(self):
        counts = self.inventory.ahead_behind_counts("ahead 2, behind 1")

        self.assertEqual(counts, {"ahead": 2, "behind": 1})

    def test_action_plan_never_allows_execution(self):
        plan = self.inventory.build_action_plan(
            [row("/Users/werkstatt/ai_workspace", ahead_behind="ahead 1")],
            {"/Users/werkstatt/ai_workspace"},
            "task-mode-chat-3031",
        )

        operations = plan["repos"][0]["operations"]

        self.assertTrue(plan["approval_required"])
        self.assertFalse(any(operation["allowed_to_execute"] for operation in operations))
        self.assertEqual(plan["repos"][0]["live_update_policy"], "no_live_pull")

    def test_salesreport_live_pull_requires_clean_live_readback(self):
        plan = self.inventory.build_action_plan(
            [row("/Users/werkstatt/salesreport", ahead_behind="ahead 1", tracked_dirty=0)],
            {"salesreport"},
            "task-mode-chat-3031",
        )

        salesreport = plan["repos"][0]
        pull_live = next(operation for operation in salesreport["operations"] if operation["operation"] == "pull_live")

        self.assertEqual(salesreport["live_update_policy"], "live_pull")
        self.assertEqual(salesreport["live_dirty_state"], "unknown_not_checked")
        self.assertIn("live_dirty_state_unknown_not_checked", pull_live["blockers"])

    def test_bid_live_pull_is_excluded_by_push_only_policy(self):
        plan = self.inventory.build_action_plan(
            [row("/Users/werkstatt/bid", ahead_behind="ahead 1")],
            {"bid"},
            "task-mode-chat-3031",
        )

        bid = plan["repos"][0]
        pull_live = next(operation for operation in bid["operations"] if operation["operation"] == "pull_live")

        self.assertEqual(bid["live_update_policy"], "push_only_no_live_pull")
        self.assertIn("live_policy_push_only_no_live_pull", pull_live["exclusions"])


if __name__ == "__main__":
    unittest.main()
