#!/usr/local/bin/python3.13
"""Regression coverage for read-only Task Flow proof repair candidates."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "scripts"
SCRIPT_PATH = SCRIPT_DIR / "task_flow_proof_repair_candidates.py"


def load_module():
    sys.path.insert(0, str(SCRIPT_DIR))
    spec = importlib.util.spec_from_file_location("task_flow_proof_repair_candidates", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TaskFlowProofRepairCandidatesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.detector = load_module()

    def test_failed_approved_send_artifact_candidate_uses_task_packet_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            failed_dir = Path(temp_dir)
            artifact = failed_dir / "example.failed-123.json"
            artifact.write_text(
                json.dumps(
                    {
                        "subject": "Cancellation instructions",
                        "body": "body must not be copied",
                        "task_packet": {
                            "owner_lane": "outreach-coordinator",
                            "responsible_worker_or_persona": "vanessa.sterling@kovaldistillery.com",
                            "ops_portal_or_domain_task": "OPS Outreach event 1054",
                            "next_update": "Review failed draft.",
                        },
                    }
                ),
                encoding="utf-8",
            )
            rows = [
                {
                    "dedupe_key": "taskflow-example",
                    "intake_channel": "approved-send:nationaloutreach",
                    "status": "blocked",
                    "source_ref": "example.failed-123.json",
                    "missing_fields": ["owner_lane", "ops_portal_or_domain_task"],
                }
            ]

            candidates = self.detector.find_failed_artifact_candidates(rows, failed_dir)

        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.proof_kind, "failed_approved_send_artifact")
        self.assertEqual(candidate.owner_lane, "outreach-coordinator")
        self.assertEqual(candidate.ops_portal_or_domain_task, "OPS Outreach event 1054")
        self.assertIn("no sent Message-ID", candidate.completion_or_blocker_email)
        self.assertNotIn("body must not be copied", candidate.verification_readback)

    def test_avignon_timeout_candidate_uses_matching_event_metadata(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            events = Path(temp_dir) / "task-flow-events.jsonl"
            events.write_text(
                json.dumps(
                    {
                        "logged_at": "2026-06-07T12:34:54-0500",
                        "event": "avignon_message_action",
                        "action": {
                            "dedupe_key": "avignon-direct-owner-sonat-example",
                            "classification": "direct-owner-route-local-retry",
                            "subject": "Follow up",
                            "decision": "direct-owner-route-blocked-local-no-email",
                            "current_state": "captured_route_blocked_local_retry",
                            "route_blocker": "timed out",
                            "archived": False,
                            "completion_target": "visible-worker-completion-or-blocker",
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            rows = [
                {
                    "dedupe_key": "avignon-direct-owner-sonat-example",
                    "source_ref": "<message@example.test>",
                    "intake_channel": "email:avignon",
                    "owner_lane": "sonat",
                    "responsible_worker_or_persona": "avignon",
                    "status": "blocked",
                    "approval_gates": "previously-logged-direct-owner-pending",
                    "verification_readback": "not-pending",
                    "source_links": "Follow up",
                    "missing_fields": ["completion_or_blocker_email", "ops_portal_or_domain_task"],
                }
            ]

            candidates = self.detector.find_avignon_timeout_candidates(rows, events)

        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate.proof_kind, "avignon_route_timeout_blocker")
        self.assertEqual(candidate.ops_portal_or_domain_task, "avignon-direct-owner-sonat-example")
        self.assertIn("timed out", candidate.completion_or_blocker_email)
        self.assertIn("archived False", candidate.verification_readback)

    def test_already_proven_avignon_row_is_not_reproposed(self):
        rows = [
            {
                "dedupe_key": "avignon-direct-owner-sonat-example",
                "intake_channel": "email:avignon",
                "owner_lane": "sonat",
                "responsible_worker_or_persona": "avignon",
                "ops_portal_or_domain_task": "avignon-direct-owner-sonat-example",
                "status": "blocked",
                "approval_gates": "previously-logged-direct-owner-pending",
                "verification_readback": "not-pending",
                "completion_or_blocker_email": "Blocked locally: already proven.",
                "missing_fields": [],
            }
        ]

        self.assertEqual(self.detector.find_avignon_timeout_candidates(rows, Path("/missing")), [])


if __name__ == "__main__":
    unittest.main()
