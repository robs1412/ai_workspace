import json
from pathlib import Path
import plistlib
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts/recovery_backup'))
import daemon
import install_daemon


class RecoverySupervisor(unittest.TestCase):
    def test_active_backup_is_adopted_without_duplicate(self):
        self.assertEqual(daemon.decision({}, {}, True, 100,False),'watching_existing_run')

    def test_success_survives_restart_without_another_dump(self):
        self.assertEqual(daemon.decision({'complete':True}, {}, False,100),'complete')
        self.assertEqual(daemon.decision({}, {'status':'verified_both'},False,100),'complete')

    def test_interrupted_attempt_obeys_persisted_backoff(self):
        state=json.loads(json.dumps({'attempts':1,'next_attempt_at':200}))
        self.assertEqual(daemon.decision(state,{},False,100),'retry_scheduled')
        self.assertEqual(daemon.decision(state,{},False,201),'run')

    def test_failures_are_bounded(self):
        self.assertEqual(daemon.decision({'attempts':3},{},False,100),'needs_attention')

    def test_known_privilege_failure_does_not_retry(self):
        self.assertEqual(daemon.decision({}, {},False,100,False),'needs_database_backup_privilege')

    def test_only_receipted_staging_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);root.chmod(0o700)
            name='20261021T200000Z-1234abcd'
            work=root/name;work.mkdir();(work/'data').mkdir()
            (work/'data'/'fixture').write_text('temporary fixture')
            (work/'receipt.json').write_text(json.dumps({'run_id':name,'status':'incomplete'}))
            unrelated=root/'unrelated';unrelated.mkdir();(unrelated/'keep').write_text('keep')
            daemon.cleanup_interrupted({'staging_root':str(root),'destinations':[]})
            self.assertFalse((work/'data').exists())
            self.assertTrue((work/'receipt.json').exists())
            self.assertTrue((unrelated/'keep').exists())

    def test_launchd_definition_roundtrips_and_supervises_foreground(self):
        value=plistlib.loads(plistlib.dumps(install_daemon.definition()))
        self.assertTrue(value['RunAtLoad'])
        self.assertTrue(value['KeepAlive'])
        self.assertNotIn('--worker',value['ProgramArguments'])
        self.assertNotIn('StartCalendarInterval',value)
        self.assertNotIn('AbandonProcessGroup',value)
