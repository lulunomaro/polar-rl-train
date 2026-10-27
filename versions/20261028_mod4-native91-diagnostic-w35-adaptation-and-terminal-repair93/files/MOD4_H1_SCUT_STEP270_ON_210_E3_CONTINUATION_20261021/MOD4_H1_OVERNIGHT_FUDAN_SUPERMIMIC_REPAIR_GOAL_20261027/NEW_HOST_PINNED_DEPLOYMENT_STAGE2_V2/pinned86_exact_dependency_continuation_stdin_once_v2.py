from pathlib import Path
import json,sys,os,time,socket,hashlib,shlex,traceback
import paramiko
HERE=Path(__file__).resolve().parent;R=HERE/'reports';ROOT='/data/robemo/polar-rl-train';RUN=ROOT+'/setup_runs/W35_PINNED_ENV_STAGE2_20261028_V2'
PIN='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b';ABS_DEADLINE=1793118000.
def save(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
def progress(v):
 with (R/'STAGE2_EXACT_ORIGINAL_PROGRESS_ACTUAL.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(v,ensure_ascii=False)+chr(10))
 print(json.dumps(v),flush=True)
def main():
 assert len(sys.argv)==1;save('STAGE2_STDIN_ENTRY_ENTERED_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),script=str(Path(__file__).resolve()),deadline_epoch=ABS_DEADLINE,secret_only_stdin_memory=True))
 print('READY_FOR_SINGLE_STDIN_JSON',flush=True)
 req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo'
 secret=req.pop('password');t=None;sf=None
 try:
  assert time.time()<ABS_DEADLINE-90,'insufficient_time_before_original_closing_lease_boundary'
  sock=socket.create_connection((req['host'],22),timeout=15);t=paramiko.Transport(sock);t.banner_timeout=15;t.start_client(timeout=15)
  actual=hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest();assert actual==PIN,'PIN_MISMATCH_BEFORE_AUTH'
  t.auth_password(req['username'],secret,fallback=False);secret=None;progress(dict(stage='PINNED_AUTHENTICATED',epoch=time.time(),host=req['host'],public_hostkey_SHA=actual))
  guard="""from pathlib import Path
import json
R=Path('/data/robemo/polar-rl-train');assert R.resolve()==R and not R.is_symlink()
m=json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['host']=='10.50.0.86' and m['username']=='robemo' and m['authorized_root']==str(R)
S=R/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1';s=json.loads((S/'SETUP_RUN_OWNER.json').read_bytes());assert s['schema']=='mod4.isolated.setup.v1' and s['root']==str(R) and s['new_run']==str(S)
D=R/'setup_runs/W35_PINNED_ENV_STAGE2_20261028_V2';assert not D.exists() and D.resolve().is_relative_to(R)
D.mkdir(mode=0o700);(D/'SETUP_RUN_OWNER.json').write_text(json.dumps({'schema':'mod4.isolated.setup.v2','host':'10.50.0.86','root':str(R),'new_run':str(D),'no_GPU_GO':True}))
print(json.dumps({'passed':True,'only_new_root':str(D),'reused_own_venv_only':str(S/'venv')}))
"""
  ch=t.open_session(timeout=15);ch.exec_command('/usr/bin/python3 -B -c '+shlex.quote(guard));ch.settimeout(25);out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();save('STAGE2_OWN_SCOPE_PREINSTALL_ACTUAL.json',dict(returncode=rc,stdout=out,stderr=err));assert rc==0,'ownscope_guard_failed'
  sf=paramiko.SFTPClient.from_transport(t);sf.get_channel().settimeout(30)
  src=HERE/'remote_new86_exact_dependency_continuation_v2.py'
  with src.open('rb') as inp,sf.open(RUN+'/'+src.name,'wx') as f:f.write(inp.read())
  ch=t.open_session(timeout=15);ch.exec_command('/usr/bin/python3 -u -B '+shlex.quote(RUN+'/'+src.name));ch.settimeout(1);buf=b'';stderr=b'';last=time.time()
  while not ch.exit_status_ready() or ch.recv_ready() or ch.recv_stderr_ready():
   if ch.recv_ready():
    buf+=ch.recv(65536)
    while b'\n' in buf:
     line,buf=buf.split(b'\n',1)
     if line:
      try:v=json.loads(line)
      except Exception:v=dict(stage='REMOTE_RAW_STDOUT_TEXT',text=line.decode(errors='replace'))
      progress(v);last=time.time()
   if ch.recv_stderr_ready():stderr+=ch.recv_stderr(65536)
   if time.time()-last>=30:progress(dict(stage='SAME_HANDLE_REMOTE_WAIT',epoch=time.time()));last=time.time()
   assert time.time()<ABS_DEADLINE+20,'own remote finite not returned before hard boundary'
   time.sleep(.2)
  rc=ch.recv_exit_status();value=dict(passed=rc==0,actual_finite_returned=True,actual_returncode=rc,epoch=time.time(),stderr=stderr.decode(errors='replace'),stdout_remaining=buf.decode(errors='replace'),new_setup_root=RUN,no_GPU_model_GO_or_ledger=True,actual_newhost_SDK_CUDA_model_restore_PPO_pending=True)
  save('STAGE2_EXACT_DEPENDENCY_SETUP_RETURNED_ACTUAL.json',value);print(json.dumps(value))
 except BaseException as e:
  msg=str(e)
  if secret:msg=msg.replace(secret,'[REDACTED]')
  save('STAGE2_LOCAL_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error_type=type(e).__name__,error=msg,partial_preserved=True));print(json.dumps(dict(stage='LOCAL_ORIGINAL_ERROR',error_type=type(e).__name__,error=msg)),flush=True);raise
 finally:
  secret=None
  if sf:sf.close()
  if t:t.close()
if __name__=='__main__':main()
