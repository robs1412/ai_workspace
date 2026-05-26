from __future__ import annotations

import importlib.util
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS_DIR = Path("/Users/werkstatt/ai_workspace/frank/runtime-source/frank-launch/scripts")
MODULE_PATH = SCRIPTS_DIR / "frank_auto_runner.py"


def load_module():
    sys.path.insert(0, str(SCRIPTS_DIR))
    frank_autodraft = types.ModuleType("frank_autodraft")
    frank_autodraft.build_receipt_draft = lambda *args, **kwargs: {}
    frank_autodraft.load_recipient_map = lambda *args, **kwargs: {}
    frank_autodraft.parse_receipt_message = lambda *args, **kwargs: {}
    frank_autodraft.write_draft_file = lambda *args, **kwargs: Path("/tmp/draft.txt")
    sys.modules["frank_autodraft"] = frank_autodraft

    frank_inbox_monitor = types.ModuleType("frank_inbox_monitor")
    frank_inbox_monitor.load_credentials = lambda *args, **kwargs: ("", "")
    frank_inbox_monitor.load_sent_log = lambda *args, **kwargs: {}
    frank_inbox_monitor.normalize_message_id = lambda value: str(value or "").strip()
    sys.modules["frank_inbox_monitor"] = frank_inbox_monitor

    frank_paths = types.ModuleType("frank_paths")
    frank_paths.bid_recipients_file = lambda: Path("/tmp/recipients.json")
    frank_paths.frank_automation_log = lambda: Path("/tmp/automation-log.jsonl")
    frank_paths.frank_creds_file = lambda: Path("/tmp/creds.json")
    frank_paths.frank_drafts_dir = lambda: Path("/tmp/drafts")
    frank_paths.frank_sent_log = lambda: Path("/tmp/sent-log.jsonl")
    frank_paths.frank_cycle_lock_dir = lambda: Path("/tmp/lock")
    frank_paths.machine_label = lambda: "test-machine"
    sys.modules["frank_paths"] = frank_paths

    send_frank_email = types.ModuleType("send_frank_email")
    send_frank_email.PROFILES = {"frank": {"signature": "Best,\n\nFrank"}}
    send_frank_email.append_sent_log = lambda *args, **kwargs: None
    send_frank_email.build_message = lambda *args, **kwargs: {"Message-ID": "<test-message-id>", "Date": "Mon, 25 May 2026 09:00:00 -0500", "From": "Frank Cannoli <frank.cannoli@kovaldistillery.com>"}
    send_frank_email.send_message = lambda *args, **kwargs: None
    sys.modules["send_frank_email"] = send_frank_email

    spec = importlib.util.spec_from_file_location("frank_auto_runner_under_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


class FrankAutoRunnerTests(unittest.TestCase):
    def test_primary_input_route_passes_state_dir_to_direct_primary_router(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            creds = tmp / "creds.json"
            sent_log = tmp / "sent-log.jsonl"
            automation_log = tmp / "automation-log.jsonl"
            recipients = tmp / "recipients.json"
            drafts_dir = tmp / "drafts"
            lock_dir = tmp / "lock"
            message = {
                "message_id": "<direct-primary@example.com>",
                "date": "Mon, 25 May 2026 09:00:00 -0500",
                "from": "Robert Birnecker <robert@kovaldistillery.com>",
                "to": "Frank Cannoli <frank.cannoli@kovaldistillery.com>",
                "cc": "",
                "subject": "Need a worker route",
                "body": "Please handle this in Frank.",
            }
            argv = [
                "frank_auto_runner.py",
                "--dry-run",
                "--json",
                "--creds-file",
                str(creds),
                "--sent-log",
                str(sent_log),
                "--automation-log",
                str(automation_log),
                "--recipients-file",
                str(recipients),
                "--drafts-dir",
                str(drafts_dir),
                "--cycle-lock-dir",
                str(lock_dir),
            ]
            with mock.patch.object(sys, "argv", argv):
                with mock.patch.object(module, "load_credentials", return_value=("frank.cannoli@kovaldistillery.com", "pw")):
                    with mock.patch.object(module, "load_sent_log", return_value={}):
                        with mock.patch.object(module, "load_automation_log", return_value={}):
                            with mock.patch.object(module, "fetch_unseen_messages", return_value=[message]):
                                with mock.patch.object(module, "run_task_flow_due_runner", return_value=None):
                                    with mock.patch.object(module, "record_task_flow_event"):
                                        with mock.patch.object(module, "record_frank_email_trace_event"):
                                            with mock.patch.object(module, "route_direct_primary_message", autospec=True) as route_mock:
                                                route_mock.side_effect = lambda action, *_args: action.update({
                                                    "decision": "routed-primary-ack-held-pending-completion",
                                                    "routed_session_id": "test-session",
                                                })
                                                exit_code = module.main()

            self.assertEqual(exit_code, 0)
            self.assertEqual(route_mock.call_count, 1)
            self.assertEqual(route_mock.call_args.args[5], automation_log.parent)
            self.assertEqual(route_mock.call_args.args[6], sent_log)


if __name__ == "__main__":
    unittest.main()
