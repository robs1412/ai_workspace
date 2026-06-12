#!/usr/local/bin/python3.13
"""Regression coverage for AI health cleanup/report orchestration."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "ai_health_check.py"


def load_module():
    spec = importlib.util.spec_from_file_location("ai_health_check", SCRIPT_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AIHealthCheckTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.health = load_module()

    def sprawl_args(self, log_dir: str, *, dry_run: bool = False) -> Namespace:
        return Namespace(
            enable_session_sprawl_governor=True,
            dry_run=dry_run,
            max_non_standing_open=2,
            session_sprawl_governor_interval_seconds=0,
            session_sprawl_governor_batch_size=4,
            log_dir=log_dir,
            timeout=1,
            status_url="http://127.0.0.1:17878/api/status",
        )

    def test_sprawl_governor_reconciles_one_stale_candidate_under_memory_pressure(self):
        classification = {
            "review_ready_sessions": [],
            "stale_waiting_sessions": [{"id": "stale-waiting-1"}],
            "stale_working_sessions": [{"id": "stale-working-1"}],
            "active_waiting_sessions": [{"id": "active-waiting-1"}],
        }
        management_health = {
            "non_standing_open_count": 9,
            "issues": [{"id": "server-health-memory"}],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(self.health, "post_workspaceboard_json", return_value=(True, {"changed": 0, "actions": []})) as post:
                result = self.health.session_sprawl_governor(
                    self.sprawl_args(tmpdir),
                    classification,
                    management_health,
                    {},
                )

        self.assertEqual(result["action"], "none")
        self.assertEqual(result["changed"], 0)
        self.assertEqual(result["candidate_ids"], ["stale-waiting-1"])
        self.assertEqual(result["skipped_candidate_count"], 2)
        post.assert_called_once()

    def test_sprawl_governor_limits_memory_pressure_batch_to_review_ready(self):
        classification = {
            "review_ready_sessions": [{"id": "ready-1"}, {"id": "ready-2"}],
            "stale_waiting_sessions": [{"id": "stale-waiting-1"}],
            "stale_working_sessions": [],
            "active_waiting_sessions": [{"id": "active-waiting-1"}],
        }
        management_health = {
            "non_standing_open_count": 9,
            "issues": [{"id": "server-health-memory"}],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            with patch.object(self.health, "post_workspaceboard_json", return_value=(True, {"changed": 1, "actions": []})) as post:
                result = self.health.session_sprawl_governor(
                    self.sprawl_args(tmpdir),
                    classification,
                    management_health,
                    {},
                )

        self.assertEqual(result["action"], "reconcile-stale")
        self.assertEqual(result["batch_size"], 1)
        self.assertEqual(result["candidate_ids"], ["ready-1"])
        self.assertEqual(result["skipped_candidate_count"], 3)
        post.assert_called_once()

    def test_allianz_stop_ship_weekly_report_check_maps_dry_run_due(self):
        payload = {
            "sent": False,
            "task_due": True,
            "task_id": 371818,
            "task_due_date": "2026-06-11",
            "stop_ship_count": 2,
        }
        proc = Namespace(returncode=0, stdout=json.dumps(payload), stderr="")
        args = Namespace(
            enable_allianz_stop_ship_weekly_report=True,
            allianz_stop_ship_weekly_report_script=str(SCRIPT_PATH),
            dry_run=True,
            allianz_stop_ship_weekly_report_timeout_seconds=90,
        )

        with patch.object(self.health.subprocess, "run", return_value=proc) as run:
            result = self.health.allianz_stop_ship_weekly_report_check(args)

        self.assertEqual(result["status"], "dry-run-due")
        self.assertEqual(result["action"], "would-email")
        self.assertEqual(result["stop_ship_count"], 2)
        self.assertIn("--dry-run", run.call_args.args[0])

    def test_allianz_stop_ship_weekly_report_check_maps_sent(self):
        payload = {
            "sent": True,
            "task_due": True,
            "task_id": 371818,
            "task_due_date": "2026-06-11",
            "stop_ship_count": 1,
            "advanced_to": "2026-06-18",
            "message_id": "<sent@example.test>",
        }
        proc = Namespace(returncode=0, stdout=json.dumps(payload), stderr="")
        args = Namespace(
            enable_allianz_stop_ship_weekly_report=True,
            allianz_stop_ship_weekly_report_script=str(SCRIPT_PATH),
            dry_run=False,
            allianz_stop_ship_weekly_report_timeout_seconds=90,
        )

        with patch.object(self.health.subprocess, "run", return_value=proc):
            result = self.health.allianz_stop_ship_weekly_report_check(args)

        self.assertEqual(result["status"], "sent")
        self.assertEqual(result["action"], "emailed")
        self.assertEqual(result["advanced_to"], "2026-06-18")
        self.assertEqual(result["message_id"], "<sent@example.test>")


if __name__ == "__main__":
    unittest.main()
