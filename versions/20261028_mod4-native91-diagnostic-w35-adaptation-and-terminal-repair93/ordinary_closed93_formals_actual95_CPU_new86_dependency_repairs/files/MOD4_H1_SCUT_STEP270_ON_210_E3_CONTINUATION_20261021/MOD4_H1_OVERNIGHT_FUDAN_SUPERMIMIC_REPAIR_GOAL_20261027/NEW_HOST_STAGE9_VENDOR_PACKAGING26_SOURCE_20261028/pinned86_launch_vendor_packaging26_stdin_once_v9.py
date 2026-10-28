from pathlib import Path
import json,sys,os,time,socket,hashlib,shlex,traceback
import paramiko
HERE=Path(__file__).resolve().parent;R=HERE/'reports';ROOT='/data/robemo/polar-rl-train';RUN=ROOT+'/setup_runs/W35_PINNED_ENV_STAGE9_VENDOR_PACKAGING26_20261028_V9'
PIN='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b';ABS_DEADLINE=0.
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def progress(v):
 with (R/'STAGE9_EXACT_ORIGINAL_PROGRESS_ACTUAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(v,ensure_ascii=False)+chr(10))
 print(json.dumps(v),flush=True)
def main():
 import argparse
 parser=argparse.ArgumentParser();parser.add_argument('--max-seconds',type=int,default=1800);args=parser.parse_args();assert args.max_seconds in (1800,2400)
 save('STAGE9_STDIN_ENTRY_ENTERED_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve()),maximum_after_stdin_seconds=120,detached_owned_installer_max_seconds=args.max_seconds,secret_only_stdin_memory=True))
 print('READY_FOR_SINGLE_STDIN_JSON',flush=True)
 req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo'
 global ABS_DEADLINE
 ABS_DEADLINE=time.time()+120
 secret=req.pop('password');t=None;sf=None
 try:
  assert time.time()<ABS_DEADLINE-90,'insufficient_time_before_original_closing_lease_boundary'
  sock=socket.create_connection((req['host'],22),timeout=15);t=paramiko.Transport(sock);t.banner_timeout=15;t.auth_timeout=15;t.start_client(timeout=15)
  actual=hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest();assert actual==PIN,'PIN_MISMATCH_BEFORE_AUTH'
  t.auth_password(req['username'],secret,fallback=False);secret=None;progress(dict(stage='PINNED_AUTHENTICATED',epoch=time.time(),host=req['host'],public_hostkey_SHA=actual))
  guard="""from pathlib import Path
import json
R=Path('/data/robemo/polar-rl-train');assert R.resolve()==R and not R.is_symlink()
m=json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['host']=='10.50.0.86' and m['username']=='robemo' and m['authorized_root']==str(R)
S=R/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1';s=json.loads((S/'SETUP_RUN_OWNER.json').read_bytes());assert s['schema']=='mod4.isolated.setup.v1' and s['root']==str(R) and s['new_run']==str(S)
D=R/'setup_runs/W35_PINNED_ENV_STAGE9_VENDOR_PACKAGING26_20261028_V9';assert not D.exists() and D.resolve().is_relative_to(R)
D.mkdir(mode=0o700);(D/'SETUP_RUN_OWNER.json').write_text(json.dumps({'schema':'mod4.isolated.setup.v2','host':'10.50.0.86','root':str(R),'new_run':str(D),'no_GPU_GO':True}))
print(json.dumps({'passed':True,'only_new_root':str(D),'reused_own_venv_only':str(S/'venv')}))
"""
  ch=t.open_session(timeout=15);ch.exec_command('/usr/bin/python3 -B -c '+shlex.quote(guard));ch.settimeout(25);out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();save('STAGE9_OWN_SCOPE_PREINSTALL_ACTUAL.json',dict(returncode=rc,stdout=out,stderr=err));assert rc==0,'ownscope_guard_failed'
  sf=paramiko.SFTPClient.from_transport(t);sf.get_channel().settimeout(30)
  def full_owned_reports(phase,runs):
   import stat
   target=R/('complete_original_UTF8_reports_'+phase);target.mkdir();rows=[]
   for run in runs:
    with sf.open(run+'/SETUP_RUN_OWNER.json','r') as q:marker=json.loads(q.read())
    assert marker['root']==ROOT and marker['new_run']==run
    names=[(run,x) for x in sf.listdir_attr(run) if x.filename.endswith(('.json','.txt','.log')) and stat.S_ISREG(x.st_mode)]
    try:names += [(run+'/logs',x) for x in sf.listdir_attr(run+'/logs') if x.filename.endswith(('.json','.txt','.log')) and stat.S_ISREG(x.st_mode)]
    except FileNotFoundError:pass
    for directory,a in names:
     path=directory+'/'+a.filename;before=sf.stat(path)
     with sf.open(path,'rb') as q:raw=q.read()
     after=sf.stat(path);assert (before.st_size,before.st_mtime)==(after.st_size,after.st_mtime)
     rel=path[len(ROOT)+1:];name=hashlib.sha256(rel.encode()).hexdigest()[:20]+'_'+a.filename;local=target/name
     with local.open('xb') as q:q.write(raw)
     try:raw.decode('utf8');utf8=True
     except UnicodeDecodeError:utf8=False
     rows.append(dict(remote_path=path,local_path=str(local),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),complete_original_bytes=True,UTF8_decodable=utf8))
   save('FULL_ORIGINAL_REPORTS_'+phase+'_MANIFEST_ACTUAL.json',dict(passed=True,rows=rows,no_binary_model_or_download_reread=True))
  # Previous17+Stage4 full reports already locally verified; do not retrieve or hash them again for Git.
  with sf.open(RUN+'/INSTALL_BUDGET.json','wx') as q:q.write(json.dumps(dict(max_seconds=args.max_seconds)).encode())
  src=HERE/'owned_stage9_vendor_packaging26_supervisor_v1.py'
  assert hashlib.sha256(src.read_bytes()).hexdigest()=='aa511ea5786264802c8bd622a2091f644946698e9287eaf3626ec64538822523'
  with src.open('rb') as inp,sf.open(RUN+'/'+src.name,'wx') as f:f.write(inp.read())
  launch="from pathlib import Path\nimport sys,json,subprocess,time,hashlib\nB=Path(v_RUN);sys.path.insert(0,str(B));import owned_stage9_vendor_packaging26_supervisor_v1 as m\nassert hashlib.sha256((B/'owned_stage9_vendor_packaging26_supervisor_v1.py').read_bytes()).hexdigest()==v_SHA\nm.scope();env=m.environment();log=(B/'SUPERVISOR_FULL.log').open('xb')\np=subprocess.Popen(['/usr/bin/python3','-u','-B',str(B/'owned_stage9_vendor_packaging26_supervisor_v1.py'),'--supervise'],cwd=B,env=env,stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,start_new_session=True,close_fds=True);log.close();identity=m.ident(p.pid)\nfor _ in range(100):\n if (B/'OWN_INSTALL_LOCK_ACQUIRED_ACTUAL.json').exists() and (B/'INSTALLER_IDENTITY_ACTUAL.json').exists():break\n assert p.poll() is None,'owned supervisor failed before admission receipt';time.sleep(.05)\nassert (B/'OWN_INSTALL_LOCK_ACQUIRED_ACTUAL.json').exists() and (B/'INSTALLER_IDENTITY_ACTUAL.json').exists()\nvalue=dict(passed_detached_launch_only=True,supervisor=identity,installer=json.loads((B/'INSTALLER_IDENTITY_ACTUAL.json').read_bytes()),own_install_lock=json.loads((B/'OWN_INSTALL_LOCK_ACQUIRED_ACTUAL.json').read_bytes()),root=str(B),no_GPU_model_GO_or_account=True,terminal_not_yet_observed=True)\n(B/'DETACHED_LAUNCH_ACTUAL.json').write_text(json.dumps(value,indent=2));print(json.dumps(value))\n"
  launch='v_RUN='+repr(RUN)+'\nv_SHA='+repr('aa511ea5786264802c8bd622a2091f644946698e9287eaf3626ec64538822523')+'\n'+launch
  ch=t.open_session(timeout=15);ch.exec_command('/usr/bin/python3 -B -c '+shlex.quote(launch));ch.settimeout(30);out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();assert rc==0,err
  value=json.loads(out);assert value['passed_detached_launch_only'];value.update(epoch=time.time(),actual_startup_finite_returned=True,actual_returncode=rc,budget_seconds=args.max_seconds,source_SHA='aa511ea5786264802c8bd622a2091f644946698e9287eaf3626ec64538822523',remote_stderr=err)
  save('STAGE9_DETACHED_INSTALLER_LAUNCHED_RETURNED_ACTUAL.json',value);print(json.dumps(value))
 except BaseException as e:
  msg=str(e)
  if secret:msg=msg.replace(secret,'[REDACTED]')
  save('STAGE9_LOCAL_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error_type=type(e).__name__,error=msg,partial_preserved=True));print(json.dumps(dict(stage='LOCAL_ORIGINAL_ERROR',error_type=type(e).__name__,error=msg)),flush=True);raise
 finally:
  secret=None
  if sf:sf.close()
  if t:t.close()
if __name__=='__main__':main()
