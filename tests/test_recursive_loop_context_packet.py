#!/usr/local/bin/python3.13
"""Regression coverage for recursive loop context packets."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "recursive_loop_context_packet.py"


def load_module():
    spec = importlib.util.spec_from_file_location("recursive_loop_context_packet", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def status_payload(candidate_path: Path, packet_path: Path) -> dict:
    return {
        "generated_at": "2026-06-09 11:30:00 CDT",
        "next_action": "review_proof_repair_packets_for_approval",
        "workspaceboard_monitor": {"ok": True, "count": 18},
        "git_hygiene": {"dirty_repo_count": 2},
        "recursive": {
            "truth_drift": {"drift_count": 0, "proof_issue_count": 5},
            "proof_repair_candidates": {
                "candidate_count": 5,
                "source": {"path": str(candidate_path)},
            },
            "proof_repair_packets": {
                "packet_count": 5,
                "needs_approval_count": 5,
                "source": {"path": str(packet_path)},
            },
        },
        "proof_repair_packet_reviews": {
            "pending_review_count": 5,
            "packets": [{"status": "needs_approval"}, {"status": "approved"}],
        },
        "degraded_sources": [],
    }


class RecursiveLoopContextPacketTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context_packet = load_module()

    def test_packet_summarizes_state_and_blocks_mutation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            candidate_path = temp / "candidates.json"
            packet_path = temp / "packets.json"
            status_path = temp / "loop-status.json"
            candidate_path.write_text("{}", encoding="utf-8")
            packet_path.write_text("{}", encoding="utf-8")
            status_path.write_text(json.dumps(status_payload(candidate_path, packet_path)), encoding="utf-8")

            packet = self.context_packet.build_packet(status_path, max_age_hours=24)

        self.assertFalse(packet["mutation_allowed"])
        self.assertEqual(packet["next_safe_action"], "review_proof_repair_packets_for_approval")
        self.assertEqual(packet["current_state"]["packet_pending_review_count"], 5)
        self.assertTrue(packet["approval_gates"]["approval_required_for_packet_execution"])
        self.assertEqual(packet["approval_gates"]["approved_packet_count"], 1)
        self.assertEqual(packet["stale_source_count"], 0)

    def test_stale_or_missing_sources_force_refresh_next_action(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            missing_candidate_path = temp / "missing-candidates.json"
            packet_path = temp / "packets.json"
            status_path = temp / "loop-status.json"
            packet_path.write_text("{}", encoding="utf-8")
            status_path.write_text(
                json.dumps(status_payload(missing_candidate_path, packet_path)),
                encoding="utf-8",
            )

            packet = self.context_packet.build_packet(status_path, max_age_hours=24)

        self.assertEqual(packet["next_safe_action"], "refresh_loop_status_before_execution")
        self.assertGreater(packet["stale_source_count"], 0)

    def test_markdown_includes_startup_and_stop_condition(self):
        packet = {
            "generated_at": "2026-06-09 11:30:00 CDT",
            "schema_version": 1,
            "next_safe_action": "monitor_mode",
            "startup_files": ["/Users/werkstatt/ai_workspace/AGENTS.md"],
            "current_state": {
                "loop_status_generated_at": "2026-06-09 11:29:00 CDT",
                "workspaceboard_monitor_ok": True,
                "workspaceboard_monitor_count": 18,
                "truth_drift_count": 0,
                "proof_issue_count": 0,
                "proof_repair_packet_count": 0,
                "packet_pending_review_count": 0,
                "dirty_repo_count": 0,
                "next_action": "monitor_mode",
            },
            "source_artifacts": [
                {"path": "/tmp/status.json", "exists": True, "mtime": "now", "stale": False},
            ],
            "approval_gates": {
                "external_send_allowed": False,
                "production_mutation_allowed": False,
                "approval_required_for_packet_execution": False,
                "approved_packet_count": 0,
                "boundary": "No mutation.",
            },
            "stop_condition": "Refresh stale context.",
        }

        report = self.context_packet.render_markdown(packet)

        self.assertIn("Startup", report)
        self.assertIn("Stop Condition", report)
        self.assertIn("No mutation", report)


if __name__ == "__main__":
    unittest.main()
