import datetime
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]/'scripts/recovery_backup'))
import launch_backup


class LaunchSafety(unittest.TestCase):
    def exercise(self, escrow=True, space=30, failure=False):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            config=base/'config.json'
            config.write_text(json.dumps({'key_escrow_verified_at':'verified' if escrow else None,
                                          'password_file':'fixture'}))
            (base/'readiness.json').write_text(json.dumps({'primary_schema_check':True,'postgres_checks':True}))
            with patch.multiple(launch_backup,BASE=base,REVIEW=base,CONFIG=config), \
                 patch.object(launch_backup.runner,'validate'), \
                 patch.object(launch_backup.runner,'private_file'), \
                 patch.object(launch_backup.shutil,'disk_usage') as usage, \
                 patch.object(launch_backup.runner,'run_backup') as backup:
                usage.return_value.free=space*1024**3
                if failure:
                    backup.side_effect=RuntimeError('PRIVATE SENTINEL MUST NOT APPEAR')
                else:
                    backup.return_value={'status':'verified_both'}
                code=launch_backup.run(datetime.datetime.now().astimezone())
                result=(base/'activation-status.json').read_text()
                self.assertNotIn('PRIVATE SENTINEL',result)
                return code, json.loads(result), backup.call_count

    def test_unverified_key_blocks_export(self):
        code,result,calls=self.exercise(escrow=False)
        self.assertEqual((code,result['status'],calls),(1,'failed',0))

    def test_low_space_blocks_export(self):
        code,result,calls=self.exercise(space=24)
        self.assertEqual((code,result['status'],calls),(1,'failed',0))

    def test_failure_does_not_disclose_private_errors(self):
        code,result,calls=self.exercise(failure=True)
        self.assertEqual((code,result['status'],calls),(1,'failed',1))

    def test_verified_result_is_preserved(self):
        code,result,calls=self.exercise()
        self.assertEqual((code,result['status'],calls),(0,'verified_both',1))
