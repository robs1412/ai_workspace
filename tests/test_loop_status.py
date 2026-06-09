#!/usr/local/bin/python3.13
"""Regression coverage for read-only loop status schema and board projection."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "loop_status.py"


def load_module():
    spec = importlib.util.spec_from_file_location("loop_status", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LoopStatusTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.loop_status = load_module()

    def test_build_board_status_is_compact_and_read_only(self):
        status = {
            "schema_version": self.loop_status.SCHEMA_VERSION,
            "generated_at": "2026-06-09 09:30:00 CDT",
            "mode": "read-only-loop-status",
            "mutation_allowed": False,
            "next_action": "review_proof_repair_packets_for_approval",
            "workspaceboard_monitor": {
                "ok": True,
                "count": 18,
                "by_status": {"green": 18},
                "error": "",
            },
            "recursive": {
                "proof_repair_packets": {
                    "packet_count": 5,
                    "needs_approval_count": 5,
                },
                "truth_drift": {"drift_count": 0},
            },
            "proof_repair_packet_reviews": {"pending_review_count": 5},
            "git_dirty_reviews": {"pending_review_count": 0, "blocked_review_count": 0},
            "degraded_sources": [],
        }

        board = self.loop_status.build_board_status(status)

        self.assertEqual(board["schema_version"], self.loop_status.SCHEMA_VERSION)
        self.assertFalse(board["mutation_allowed"])
        self.assertEqual(board["proof_repair"]["pending_review_count"], 5)
        self.assertEqual(board["git_dirty_reviews"]["pending_review_count"], 0)
        self.assertEqual(board["workspaceboard_monitor"]["by_status"], {"green": 18})
        self.assertNotIn("proposal_executor", board)

    def test_render_markdown_includes_degraded_error_and_source_timestamps(self):
        status = {
            "schema_version": self.loop_status.SCHEMA_VERSION,
            "generated_at": "2026-06-09 09:30:00 CDT",
            "mode": "read-only-loop-status",
            "mutation_allowed": False,
            "next_action": "repair_or_classify_workspaceboard_monitor_status",
            "workspaceboard_monitor": {
                "ok": False,
                "checked_at": "2026-06-09 09:30:01 CDT",
                "count": 0,
                "by_status": {},
                "error": "timeout",
            },
            "proposal_executor": {"approved_unexecuted_count": 0, "blocked_execution_count": 0},
            "git_hygiene": {"repo_count": 31, "dirty_repo_count": 2, "buckets": {}},
            "recursive": {
                "proof_repair_candidates": {
                    "candidate_count": 5,
                    "source": {"mtime": "2026-06-09 09:29:00 CDT"},
                },
                "proof_repair_packets": {
                    "packet_count": 5,
                    "needs_approval_count": 5,
                    "source": {"mtime": "2026-06-09 09:29:00 CDT"},
                },
                "truth_drift": {"drift_count": 0, "proof_issue_count": 5},
            },
            "proof_repair_packet_reviews": {"pending_review_count": 5},
            "git_dirty_reviews": {"pending_review_count": 0, "blocked_review_count": 0},
            "degraded_sources": [{"section": "workspaceboard_monitor", "url": "http://example", "error": "timeout"}],
        }

        report = self.loop_status.render_markdown(status)

        self.assertIn("Schema version", report)
        self.assertIn("candidates_source_mtime", report)
        self.assertIn("timeout", report)

    def test_next_action_uses_packet_review_pending_count(self):
        status = {
            "workspaceboard_monitor": {"ok": True},
            "proposal_executor": {"approved_unexecuted_count": 0},
            "git_hygiene": {"dirty_repo_count": 0},
            "recursive": {
                "proof_repair_candidates": {"candidate_count": 5},
                "proof_repair_packets": {"packet_count": 5, "needs_approval_count": 5},
                "truth_drift": {"drift_count": 0},
            },
            "proof_repair_packet_reviews": {"pending_review_count": 0},
            "git_dirty_reviews": {"pending_review_count": 0},
        }

        action = self.loop_status.next_action(status)

        self.assertEqual(action, "monitor_mode")

    def test_next_action_uses_dirty_repo_review_pending_count(self):
        status = {
            "workspaceboard_monitor": {"ok": True},
            "proposal_executor": {"approved_unexecuted_count": 0},
            "git_hygiene": {"dirty_repo_count": 3},
            "recursive": {
                "proof_repair_candidates": {"candidate_count": 0},
                "proof_repair_packets": {"packet_count": 0, "needs_approval_count": 0},
                "truth_drift": {"drift_count": 0},
            },
            "proof_repair_packet_reviews": {"pending_review_count": 0},
            "git_dirty_reviews": {"pending_review_count": 0},
        }

        action = self.loop_status.next_action(status)

        self.assertEqual(action, "monitor_mode")

    def test_next_action_stays_on_dirty_review_when_repos_are_pending(self):
        status = {
            "workspaceboard_monitor": {"ok": True},
            "proposal_executor": {"approved_unexecuted_count": 0},
            "git_hygiene": {"dirty_repo_count": 3},
            "recursive": {
                "proof_repair_candidates": {"candidate_count": 0},
                "proof_repair_packets": {"packet_count": 0, "needs_approval_count": 0},
                "truth_drift": {"drift_count": 0},
            },
            "proof_repair_packet_reviews": {"pending_review_count": 0},
            "git_dirty_reviews": {"pending_review_count": 1},
        }

        action = self.loop_status.next_action(status)

        self.assertEqual(action, "review_dirty_repositories")


if __name__ == "__main__":
    unittest.main()
