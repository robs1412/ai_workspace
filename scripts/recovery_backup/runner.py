#!/usr/local/bin/python3.13
"""Opt-in, two-destination encrypted recovery backups. No scheduler or deletion API.
Estimate never invokes a backup program. Production config defaults to disabled.
Only structured summaries are printed; child output and source paths stay private.
"""
import argparse, contextlib, datetime, gzip, selectors, signal, time, fcntl, hashlib, json, os, re, shlex, shutil, sqlite3, stat, subprocess, sys, tempfile, uuid
from pathlib import Path
from inventory import inventory

class BackupError(Exception): pass

def atomic_json(path, value):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    tmp=path.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2));tmp.chmod(0o600);tmp.replace(path)

def gate(config, action, approved):
    if action!='estimate' and (not approved or not config.get('execution_enabled')):
        raise BackupError('Execution disabled: reviewed configuration and explicit --approved are required.')
    if action!='estimate' and config.get('activation_blockers'):
        raise BackupError('Activation blockers remain in the reviewed configuration.')

def validate(config):
    sources=config.get('sources',[])
    if not sources:raise BackupError('No sources configured.')
    roots=[Path(s['path']).absolute() for s in sources]
    for i,p in enumerate(roots):
        if not p.is_absolute() or p==Path('/'):raise BackupError('Source root is too broad.')
        if any(p==q or p in q.parents or q in p.parents for q in roots[:i]):raise BackupError('Overlapping source roots.')
    destinations=config.get('destinations',[])
    if len(destinations)!=2 or len({d['repository'] for d in destinations})!=2:
        raise BackupError('Two distinct repositories are required.')
    if any(not re.fullmatch('[a-z0-9-]+',d['label']) for d in destinations):raise BackupError('Invalid destination label.')
    stage=Path(config['staging_root']).absolute()
    for p in roots:
        if stage==p or p in stage.parents:raise BackupError('Staging must be outside source roots.')
    if excluded(stage,config):raise BackupError('Staging must not be covered by backup exclusions.')
    for job in config.get('database_exports',[]):
        if not re.fullmatch('[a-z0-9-]+',job.get('label','')):raise BackupError('Invalid database export label.')
    return roots

def private_file(path):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_mode & 0o077:
        raise BackupError('A required protected configuration file is missing or has unsafe permissions.')
    return p

def child_env(config,destination):
    env=dict(os.environ)
    for name in list(env):
        if name.startswith(('RESTIC_','RCLONE_')):env.pop(name)
    env['RESTIC_PASSWORD_FILE']=str(private_file(config['password_file']))
    # Config is private. Values are never printed, included in reports, or put in argv.
    env.update(config.get('environment',{}));env.update(destination.get('environment',{}))
    oauth=destination.get('drive_oauth')
    if oauth:
        client=json.loads(Path(oauth['client_file']).read_text())
        client=client.get('installed',client.get('web',client))
        token=json.loads(Path(oauth['token_file']).read_text())
        # Expired access-token timestamp forces refresh using the existing approved OAuth grant.
        rt={'access_token':token.get('access_token',token.get('token','')), 'refresh_token':token['refresh_token'],
            'token_type':'Bearer','expiry':'2000-01-01T00:00:00Z'}
        env.update(RCLONE_CONFIG='/dev/null',RCLONE_CONFIG_AICLOUD_TYPE='drive',
          RCLONE_CONFIG_AICLOUD_CLIENT_ID=client['client_id'],RCLONE_CONFIG_AICLOUD_CLIENT_SECRET=client['client_secret'],
          RCLONE_CONFIG_AICLOUD_TOKEN=json.dumps(rt),RCLONE_CONFIG_AICLOUD_TEAM_DRIVE=oauth['shared_drive_id'])
    env['GOMAXPROCS']=str(config.get('cpu_threads',2))
    return env

def restic(config,destination,args):
    binary=config.get('restic_binary','restic')
    if not shutil.which(binary):raise BackupError('Restic is not installed at the configured location.')
    command=[binary,'--repo',destination['repository'],'--json','--no-cache',
             '--limit-upload',str(destination.get('upload_kib_per_second',config.get('upload_kib_per_second',2048)))]
    options=list(destination.get('restic_options',[]))
    if os.geteuid()==0 and destination.get('run_transport_as_user'):
        prefix=shlex.join(['/usr/bin/sudo','-H','-u',destination['run_transport_as_user'],'--'])+' '
        options=[('sftp.command='+prefix+x[len('sftp.command='):]) if x.startswith('sftp.command=') else x for x in options]
    command+=options+args
    try:r=subprocess.run(command,env=child_env(config,destination),capture_output=True,text=True,timeout=config.get('timeout_seconds',172800))
    except (OSError,subprocess.TimeoutExpired):raise BackupError('Backup tool could not finish; no success recorded.') from None
    if r.returncode:raise BackupError('Backup tool failed (code %s); incomplete snapshots must not count as successful.'%r.returncode)
    messages=[]
    for line in r.stdout.splitlines():
        try:messages.append(json.loads(line))
        except ValueError:pass
    return messages

def excluded(p,config):
    return any(part in config.get('excluded_names',[]) for part in p.parts) or any(p==Path(x) or Path(x) in p.parents for x in config.get('excluded_paths',[]))

def candidate_files(config):
    for source in config['sources']:
        root=Path(source['path'])
        def err(_):raise BackupError('An included directory cannot be read.')
        if root.is_file():yield root;continue
        for base,dirs,files in os.walk(root,followlinks=False,onerror=err):
            dirs[:]=[d for d in dirs if not excluded(Path(base)/d,config) and not (Path(base)/d).is_symlink()]
            for name in files:
                p=Path(base)/name
                if not p.is_symlink() and not excluded(p,config):yield p

def sqlite_copy(source,target,reserve=0):
    # SQLite online backup includes committed WAL changes without copying open WAL files.
    target.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
    try:
        deadline=time.monotonic()+300
        def progress(status, remaining, total):
            if time.monotonic()>deadline:raise BackupError('SQLite snapshot exceeded its time limit.')
            if shutil.disk_usage(target.parent).free < reserve:raise BackupError('Staging reserve exhausted during SQLite snapshot.')
        with sqlite3.connect(source.absolute().as_uri()+'?mode=ro',uri=True,timeout=30) as src:
            with sqlite3.connect(target,timeout=30) as dest:
                src.backup(dest,pages=256,sleep=0.1,progress=progress)
                if dest.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise BackupError('SQLite consistency check failed.')
    except sqlite3.Error:raise BackupError('SQLite snapshot failed.') from None
    target.chmod(0o600)

def export_database(job,out,reserve):
    process=None
    diagnostic=tempfile.TemporaryFile(dir=out.parent)
    label=job.get('label','database')
    if not re.fullmatch('[a-z0-9-]+',label):label='database'
    try:
        argv=list(job['argv'])
        if os.geteuid()==0 and job.get('run_as_user'):
            argv=['/usr/bin/sudo','-H','--preserve-env=SSH_ASKPASS,SSH_ASKPASS_REQUIRE,DISPLAY','-u',job['run_as_user'],'--']+argv
        process=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=diagnostic,
          env={**os.environ,**job.get('environment',{}),'TMPDIR':str(out.parent.absolute())},start_new_session=True)
        deadline=time.monotonic()+job.get('timeout_seconds',3600);total=0
        with out.open('wb') as raw, gzip.GzipFile(fileobj=raw,mode='wb',compresslevel=3) as compressed, selectors.DefaultSelector() as poll:
            os.chmod(out,0o600);poll.register(process.stdout,selectors.EVENT_READ)
            while True:
                if time.monotonic()>deadline:raise BackupError('Database export timed out.')
                if shutil.disk_usage(out.parent).free < reserve:raise BackupError('Staging reserve exhausted during database export.')
                if not poll.select(timeout=1):continue
                chunk=os.read(process.stdout.fileno(),1024*1024)
                if not chunk:break
                total+=len(chunk);compressed.write(chunk)
            code=process.wait(timeout=10)
            if code or not total:
                diagnostic.seek(0)
                error=diagnostic.read(65536).decode(errors='replace').lower()
                # Only fixed categories may leave the private subprocess stream.
                categories=[term for term in ('access denied','permission denied','unknown variable',
                  'unknown option','connection refused','host key verification failed',
                  'a password is required','illegal option','unrecognized option','command not found',
                  'lost connection','could not resolve hostname') if term in error]
                detail=', '.join(categories) if categories else 'unclassified private error'
                raise BackupError(f'Database export {label} failed (exit {code}, {total} SQL bytes): {detail}. Backup aborted.')
    except (OSError,subprocess.TimeoutExpired):raise BackupError('Database export did not complete.') from None
    finally:
        if process and process.poll() is None:
            os.killpg(process.pid,signal.SIGTERM)
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:os.killpg(process.pid,signal.SIGKILL);process.wait()
        if process and process.stdout:process.stdout.close()
        diagnostic.close()

def stage_data(config,stage,allow_database_locks):
    exclusions=[]; sqlite_map=[]
    if config.get('require_database_exports',True) and not config.get('database_exports'):
        raise BackupError('Database export coverage is required but not configured.')
    for job in config.get('database_exports',[]):
        if shutil.disk_usage(stage).free < config.get('minimum_local_free_bytes',15*1024**3):
            raise BackupError('Staging reserve exhausted; stopping before the next database export.')
        if job.get('requires_write_lock') and not allow_database_locks:
            raise BackupError('Consistent legacy database export requires separately approved write locks.')
        out=stage/'databases'/(job['label']+'.sql.gz');out.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        export_database(job,out,config.get('minimum_local_free_bytes',15*1024**3))
    for source in candidate_files(config):
        if source.suffix.lower() not in ('.db','.sqlite','.sqlite3'):continue
        try:
            with source.open('rb') as f:magic=f.read(16)
        except OSError:raise BackupError('Cannot inspect an included database candidate.') from None
        if magic!=b'SQLite format 3\x00':continue
        target=stage/'sqlite'/source.relative_to(source.anchor)
        sqlite_copy(source,target,config.get('minimum_local_free_bytes',15*1024**3))
        exclusions.extend([str(source),str(source)+'-wal',str(source)+'-shm',str(source)+'-journal'])
        sqlite_map.append({'original':str(source),'snapshot':str(target.relative_to(stage))})
    # Mapping stays inside encrypted backup. Never publish it in the owner report.
    atomic_json(stage/'sqlite-restore-map.json',sqlite_map)
    probe=stage/'restore-probe.bin';probe.write_bytes(os.urandom(4096));probe.chmod(0o600)
    return exclusions,probe

def snapshot_id(messages):
    for m in reversed(messages):
        if isinstance(m,dict) and m.get('snapshot_id'):return m['snapshot_id']
    raise BackupError('No completed snapshot ID returned.')

def restore_probe(config,destination,snapshot,probe,parent):
    target=parent/('restore-'+destination['label'])
    target.mkdir(mode=0o700)
    restic(config,destination,['restore',snapshot,'--target',str(target),'--include',str(probe)])
    restored=target/probe.relative_to(probe.anchor)
    if not restored.is_file() or hashlib.sha256(restored.read_bytes()).digest()!=hashlib.sha256(probe.read_bytes()).digest():
        raise BackupError('Restore probe verification failed.')
    return True

def run_backup(config,allow_database_locks=False):
    validate(config)
    # Verify both existing repositories and key access before any SQL export.
    for destination in config['destinations']:
        restic(config,destination,['snapshots','--tag','macmini-recovery'])
    # A mounted sparsebundle is mutable at block level; do not silently back it up live.
    for mount in config.get('must_be_unmounted',[]):
        if os.path.ismount(mount):raise BackupError('An encrypted volume must be unmounted before its image can be backed up consistently.')
    measured=inventory(config['sources'],config.get('excluded_names',[]),config.get('excluded_paths',[]))
    if measured['unreadable']:raise BackupError('Included sources are unreadable; incomplete coverage is not permitted.')
    root=Path(config['staging_root']);root.mkdir(parents=True,exist_ok=True,mode=0o700)
    if root.is_symlink() or root.stat().st_mode & 0o077:raise BackupError('Staging directory must be private and not a symlink.')
    if shutil.disk_usage(root).free < config.get('minimum_local_free_bytes',15*1024**3):raise BackupError('Insufficient staging reserve.')
    # One controller across init/run/check operations. Never overwrite a prior recovery record.
    with (root/'run.lock').open('a') as lock:
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise BackupError('Another backup is active.') from None
        run_id=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]
        work=root/run_id;work.mkdir(mode=0o700)
        stage=work/'data';stage.mkdir(mode=0o700)
        receipt={'run_id':run_id,'status':'incomplete','destinations':[]}
        atomic_json(work/'receipt.json',receipt)
        try:
            exclusions,probe=stage_data(config,stage,allow_database_locks)
            # No broad --one-file-system: explicit sources can include mounted data.
            args=['backup','--tag','macmini-recovery','--tag',run_id,'--host',config.get('host_label','macmini')]
            for name in config.get('excluded_names',[]):args+=['--exclude',name]
            for path in config.get('excluded_paths',[])+exclusions:args+=['--exclude',path]
            args+=['--']+[s['path'] for s in config['sources']]+[str(stage)]
            for destination in config['destinations']:
                record={'label':destination['label'],'status':'incomplete'};receipt['destinations'].append(record)
                try:
                    sid=snapshot_id(restic(config,destination,args));record['snapshot_id']=sid
                    restic(config,destination,['check','--read-data-subset=1%'])
                    restore_probe(config,destination,sid,probe,work)
                    record.update(status='verified',restore_probe=True)
                except BackupError as exc:record['error']=str(exc)
                atomic_json(work/'receipt.json',receipt)
            if len(receipt['destinations'])==2 and all(d['status']=='verified' for d in receipt['destinations']):receipt['status']='verified_both'
            atomic_json(work/'receipt.json',receipt)
            return receipt
        finally:
            # Only this run's temporary plaintext SQL/SQLite copies and probe restores.
            # Failed snapshots remain explicitly incomplete; original sources untouched.
            shutil.rmtree(stage)
            for d in config['destinations']:
                target=work/('restore-'+d['label'])
                if target.exists():shutil.rmtree(target)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['estimate','init','run','check','retention-preview'])
    parser.add_argument('--config',required=True);parser.add_argument('--approved',action='store_true');parser.add_argument('--allow-database-write-locks',action='store_true')
    args=parser.parse_args()
    try:
        config=json.loads(Path(args.config).read_text());validate(config);gate(config,args.action,args.approved)
        if args.action=='estimate':result=inventory(config['sources'],config.get('excluded_names',[]),config.get('excluded_paths',[]))
        elif args.action=='run':result=run_backup(config,args.allow_database_write_locks)
        else:
            result=[]
            for d in config['destinations']:
                command={'init':['init'],'check':['check','--read-data'],
                  'retention-preview':['forget','--dry-run','--keep-daily','7','--keep-weekly','4','--keep-monthly','6','--tag','macmini-recovery']}[args.action]
                restic(config,d,command);result.append({'destination':d['label'],'action':args.action,'ok':True})
        print(json.dumps(result,indent=2));return 1 if isinstance(result,dict) and result.get('status')=='incomplete' else 0
    except BackupError as exc:print(json.dumps({'ok':False,'message':str(exc)}));return 1
    except Exception:print(json.dumps({'ok':False,'message':'Configuration or operation failed; details suppressed to protect private source information.'}));return 1
if __name__=='__main__':sys.exit(main())
