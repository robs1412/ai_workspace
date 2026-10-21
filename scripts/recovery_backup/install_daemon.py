#!/usr/local/bin/python3.13
"""Install the approved backup supervisor. Does not stop an existing backup."""
import json
import os
from pathlib import Path
import plistlib
import shutil
import subprocess

import runner

LABEL='com.koval.recovery-backup'
WORKSPACE=Path('/Users/werkstatt/ai_workspace')
SOURCE=WORKSPACE/'scripts/recovery_backup'
REVIEW=WORKSPACE/'tmp/recovery-backup-review'
HOME_DIR=Path('/Users/werkstatt/.local/recovery-backup/service')
PLIST=Path('/Library/LaunchDaemons')/(LABEL+'.plist')


def definition():
    return {'Label':LABEL,'ProgramArguments':['/usr/local/bin/python3.13',str(HOME_DIR/'runtime/daemon.py'),
             '--state-dir',str(HOME_DIR)],'WorkingDirectory':str(WORKSPACE),
            'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':60,'ExitTimeOut':30,
            'ProcessType':'Background','LowPriorityIO':True,'Nice':10,'Umask':63,
            'EnvironmentVariables':{'PATH':'/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'},
            'StandardOutPath':str(HOME_DIR/'service.log'),'StandardErrorPath':str(HOME_DIR/'service.log')}


def install():
    if os.geteuid()!=0:
        print('Run with sudo to install the system LaunchDaemon.')
        return 1
    current=subprocess.run(['launchctl','print','system/'+LABEL],capture_output=True)
    if current.returncode==0:
        print(json.dumps({'installed':True,'already_loaded':True,'existing_run_preserved':True}))
        return 0
    os.umask(0o077)
    config=json.loads((REVIEW/'disabled-config.json').read_text())
    owner=(REVIEW/'disabled-config.json').stat()
    config['status_owner_uid']=owner.st_uid
    config['status_owner_gid']=owner.st_gid
    proof=json.loads((REVIEW/'readiness.json').read_text())
    runner.validate(config)
    if not config.get('key_escrow_verified_at') or not all(proof.get(k) for k in ['primary_schema_check','postgres_checks']):
        raise RuntimeError('Backup prerequisites missing.')
    runner.private_file(config['password_file'])
    if HOME_DIR.is_symlink():raise RuntimeError('Unexpected installation location.')
    HOME_DIR.mkdir(mode=0o700,parents=True,exist_ok=True)
    os.chown(HOME_DIR,0,0);HOME_DIR.chmod(0o700)
    runtime=HOME_DIR/'runtime';runtime.mkdir(mode=0o700,exist_ok=True)
    for name in ['daemon.py','runner.py','inventory.py','launch_backup.py','primary_mysql.php']:
        target=runtime/name
        if target.is_symlink():raise RuntimeError('Unexpected installed file.')
        shutil.copyfile(SOURCE/name,target);os.chown(target,0,0);target.chmod(0o600)
    # Configuration and runtime survive cleanup of the development review directory.
    for job in config['database_exports']:
        job['argv']=[str(runtime/'primary_mysql.php') if x==str(SOURCE/'primary_mysql.php') else x for x in job['argv']]
    config.setdefault('excluded_paths',[]).append(str(HOME_DIR))
    runner.atomic_json(HOME_DIR/'config.json',config)
    runner.atomic_json(HOME_DIR/'readiness.json',proof)
    # Do not reset an existing supervisor receipt or retry count on reinstallation.
    if not (HOME_DIR/'supervisor.json').exists():runner.atomic_json(HOME_DIR/'supervisor.json',{})
    log=HOME_DIR/'service.log';log.touch(mode=0o600,exist_ok=True)
    temporary=PLIST.with_suffix('.plist.new')
    if temporary.exists() or temporary.is_symlink():raise RuntimeError('Installation temporary file already exists.')
    with temporary.open('xb') as stream:plistlib.dump(definition(),stream)
    os.chown(temporary,0,0);temporary.chmod(0o644);os.replace(temporary,PLIST)
    for command in [['launchctl','enable','system/'+LABEL],['launchctl','bootstrap','system',str(PLIST)]]:
        if subprocess.run(command,capture_output=True).returncode:raise RuntimeError('Service activation failed.')
    result=subprocess.run(['launchctl','print','system/'+LABEL],capture_output=True)
    print(json.dumps({'installed':True,'loaded':result.returncode==0,'existing_run_preserved':True,
                     'automatic_retry_limit':3,'retry_delay_minutes':30,'daily_schedule_enabled':False}))
    return 0 if result.returncode==0 else 1


if __name__=='__main__':
    try:raise SystemExit(install())
    except Exception:
        print('Daemon installation failed; private details suppressed. Existing backup was not stopped.')
        raise SystemExit(1)
