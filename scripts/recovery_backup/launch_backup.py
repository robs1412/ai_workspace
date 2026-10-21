#!/usr/local/bin/python3.13
"""Administrator-started, detached first backup. All output is metadata only."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import runner

BASE = Path(__file__).resolve().parents[2]
REVIEW = BASE / 'tmp/recovery-backup-review'
CONFIG = REVIEW / 'disabled-config.json'


def receipt(value):
    path = REVIEW / 'activation-status.json'
    runner.atomic_json(path, value)
    owner = CONFIG.stat()
    os.chown(path, owner.st_uid, owner.st_gid)


def run(at):
    os.umask(0o077)
    with (REVIEW / 'activation.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 1
        receipt({'status': 'scheduled', 'start_at': at.isoformat(), 'pid': os.getpid()})
        while datetime.datetime.now().astimezone() < at:
            time.sleep(min(30, max(0, (at-datetime.datetime.now().astimezone()).total_seconds())))
        receipt({'status': 'checking', 'pid': os.getpid()})
        try:
            config = json.loads(CONFIG.read_text())
            runner.validate(config)
            if not config.get('key_escrow_verified_at'):
                raise runner.BackupError('Saved recovery key has not been verified.')
            runner.private_file(config['password_file'])
            proof = json.loads((REVIEW/'readiness.json').read_text())
            if not proof.get('primary_schema_check') or not proof.get('postgres_checks'):
                raise runner.BackupError('Database preflight has not passed.')
            # Fifteen GiB is always reserved. The dump stream enforces it continuously.
            if shutil.disk_usage(BASE).free < 25*1024**3:
                raise runner.BackupError('Need 25 GiB free before starting; no files were deleted.')
            config['execution_enabled'] = True
            config['activation_blockers'] = []
            receipt({'status': 'running', 'pid': os.getpid(), 'started_at': datetime.datetime.now().astimezone().isoformat()})
            result = runner.run_backup(config, allow_database_locks=True)
            receipt(result)
            return 0 if result['status']=='verified_both' else 1
        except Exception as exc:
            message = str(exc) if isinstance(exc, runner.BackupError) else 'Preflight or backup failed; private details suppressed.'
            receipt({'status': 'failed', 'message': message})
            return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    when = parser.add_mutually_exclusive_group(required=True)
    when.add_argument('--now', action='store_true')
    when.add_argument('--at', metavar='HH:MM', help='Next occurrence in the Mac mini local timezone.')
    parser.add_argument('--allow-database-write-locks', action='store_true', required=True)
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if os.geteuid()!=0:
        print('Administrator execution required. Run this helper with sudo; do not change source permissions.')
        return 1
    at = datetime.datetime.now().astimezone()
    if args.at:
        hour, minute = map(int, args.at.split(':'))
        at = at.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if at < datetime.datetime.now().astimezone():
            at += datetime.timedelta(days=1)
    if args.worker:
        return run(at)
    # Test the readiness marker before detaching so a missing prerequisite is visible.
    proof = json.loads((REVIEW/'readiness.json').read_text())
    if not proof.get('primary_schema_check') or not proof.get('postgres_checks'):
        raise runner.BackupError('Database preflight has not passed.')
    command = [sys.executable, str(Path(__file__).resolve()), '--worker', '--allow-database-write-locks']
    command += ['--at', args.at] if args.at else ['--now']
    child = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
    print(json.dumps({'detached_worker_pid':child.pid, 'requested_start':at.isoformat(),
                     'status_file':'tmp/recovery-backup-review/activation-status.json',
                     'note':'Survives SSH disconnect; does not survive a Mac reboot.'}))
    return 0


if __name__=='__main__':
    try:
        sys.exit(main())
    except Exception:
        print('Launch failed; private details suppressed. No successful backup claimed.')
        sys.exit(1)
