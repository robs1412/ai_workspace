#!/usr/local/bin/python3.13
"""Persistent supervisor for the approved first dual backup, not a daily schedule."""
import argparse
import datetime
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import signal
import time
from types import SimpleNamespace

import launch_backup
import runner

WORKSPACE = Path('/Users/werkstatt/ai_workspace')
LEGACY = WORKSPACE/'tmp/recovery-backup-review'
MAX_ATTEMPTS = 3
RETRY_SECONDS = 1800


class Shutdown(BaseException):
    pass


def read_json(path, default=None):
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return {} if default is None else default


def busy(path):
    with path.open('a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
    return False


def decision(state, legacy, legacy_busy, now, lock_allowed=True):
    if legacy_busy:
        return 'watching_existing_run'
    if state.get('complete') or (not state.get('attempts') and legacy.get('status')=='verified_both'):
        return 'complete'
    if not lock_allowed:
        return 'needs_database_backup_privilege'
    if state.get('attempts',0)>=MAX_ATTEMPTS:
        return 'needs_attention'
    if now < state.get('next_attempt_at',0):
        return 'retry_scheduled'
    return 'run'


def cleanup_interrupted(config):
    """Only controller-created staging, after confirming no controller holds its lock."""
    root=Path(config['staging_root'])
    if not root.exists():
        return
    if root.is_symlink() or root.stat().st_mode & 0o077:
        raise runner.BackupError('Unsafe staging directory; recovery stopped.')
    with (root/'run.lock').open('a') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise runner.BackupError('A backup controller still owns the staging lock.')
        for work in root.iterdir():
            if not re.fullmatch(r'\d{8}T\d{6}Z-[a-f0-9]{8}',work.name) or work.is_symlink() or not work.is_dir():
                continue
            record=read_json(work/'receipt.json')
            if record.get('run_id')!=work.name:
                continue
            for name in ['data']+['restore-'+d['label'] for d in config['destinations']]:
                target=work/name
                if target.is_symlink():
                    raise runner.BackupError('Unexpected staging symlink; recovery stopped.')
                if target.is_dir():
                    shutil.rmtree(target)


def publish(state, phase, owner):
    runner.atomic_json(LEGACY/'daemon-status.json',{
        'phase':phase,'pid':os.getpid(),'attempts':state.get('attempts',0),
        'next_attempt_at':state.get('next_attempt_at'),'last_result':state.get('last_result'),
        'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'recurring_schedule_enabled':False})
    os.chown(LEGACY/'daemon-status.json',owner.st_uid,owner.st_gid)


def supervise(home):
    launch_backup.BASE=WORKSPACE
    launch_backup.REVIEW=home
    launch_backup.CONFIG=home/'config.json'
    config=read_json(launch_backup.CONFIG)
    runner.validate(config)
    owner=SimpleNamespace(st_uid=config['status_owner_uid'],st_gid=config['status_owner_gid'])
    if not LEGACY.exists():
        LEGACY.mkdir(parents=True,mode=0o700)
        os.chown(LEGACY,owner.st_uid,owner.st_gid)
    state_path=home/'supervisor.json'
    state=read_json(state_path)
    with (home/'supervisor.lock').open('a') as lock:
        try:
            fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        try:
            while True:
                legacy=read_json(LEGACY/'activation-status.json')
                proof=read_json(home/'readiness.json')
                phase=decision(state,legacy,busy(LEGACY/'activation.lock'),time.time(),
                               proof.get('global_read_lock_allowed') is True)
                if phase=='complete':
                    state['complete']=True
                    if not state.get('last_result'):state['last_result']=legacy
                    runner.atomic_json(state_path,state)
                publish(state,phase,owner)
                if phase!='run':
                    time.sleep(30)
                    continue
                # Persist before beginning: even SIGKILL/reboot counts toward bounded retries.
                state.update(attempts=state.get('attempts',0)+1,next_attempt_at=time.time()+RETRY_SECONDS)
                runner.atomic_json(state_path,state)
                publish(state,'running',owner)
                try:
                    cleanup_interrupted(config)
                    launch_backup.run(datetime.datetime.now().astimezone())
                    result=read_json(home/'activation-status.json')
                except Exception:
                    result={'status':'failed','message':'Supervisor preflight failed; private details suppressed.'}
                state['last_result']=result
                state['complete']=result.get('status')=='verified_both'
                state['next_attempt_at']=time.time()+RETRY_SECONDS
                runner.atomic_json(state_path,state)
        except Shutdown:
            publish(state,'interrupted_will_restart',owner)


def stop(signum, frame):
    raise Shutdown()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir',required=True,type=Path)
    args=parser.parse_args()
    if os.geteuid()!=0:
        raise RuntimeError('Administrator service required.')
    os.umask(0o077)
    signal.signal(signal.SIGTERM,stop)
    signal.signal(signal.SIGINT,stop)
    supervise(args.state_dir)


if __name__=='__main__':
    try:
        main()
    except Shutdown:
        pass
    except Exception:
        # launchd restarts the supervisor; no raw exception or configuration logging.
        print('Backup supervisor could not start; private details suppressed.',flush=True)
        raise SystemExit(1)
