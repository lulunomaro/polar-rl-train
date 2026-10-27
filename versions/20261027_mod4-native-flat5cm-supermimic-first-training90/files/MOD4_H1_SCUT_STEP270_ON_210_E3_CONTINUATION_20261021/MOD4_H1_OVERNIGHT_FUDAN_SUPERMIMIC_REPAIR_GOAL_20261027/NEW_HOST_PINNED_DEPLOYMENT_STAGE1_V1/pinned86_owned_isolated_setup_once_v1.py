from pathlib import Path,PurePosixPath
import sys,os,json,time,hashlib,socket,shlex,traceback
import paramiko
HERE=Path(__file__).resolve().parent
L=HERE.parent
REPORTS=HERE/'reports';REPORTS.mkdir(exist_ok=True)
ROOT='/data/robemo/polar-rl-train'
RUN=ROOT+'/setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1'
PIN='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b'
DEADLINE=1793111880.0
TEMPLATE=L/'new_server_10_50_0_86_frozen_experts_PPO50_gas400_source_preparation_20261027/W35_NEW_HOST_DEPLOYMENT_MANIFEST_TEMPLATE_V1.json'
def save(name,v):
 p=REPORTS/name
 with p.open('x',encoding='utf-8') as f:json.dump(v,f,indent=2)
def progress(v):
 with (REPORTS/'OWNED_ISOLATED_SETUP_PROGRESS_ACTUAL.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(v)+'\n')
 print(json.dumps(v),flush=True)
def main():
 assert len(sys.argv)==1
 save('OWNED_ISOLATED_SETUP_ENTERED_ACTUAL.json',{'own_pid':os.getpid(),'script':str(Path(__file__).resolve()),'epoch':time.time(),'deadline_epoch':DEADLINE,'secret_ingress':'stdin_memory_only'})
 print('READY_FOR_SINGLE_STDIN_JSON',flush=True)
 req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo'
 secret=req.pop('password');transport=None;sftp=None;channel=None
 try:
  assert time.time()<DEADLINE-90,'not_enough_finite_time'
  sock=socket.create_connection((req['host'],22),timeout=15)
  transport=paramiko.Transport(sock);transport.banner_timeout=15;transport.start_client(timeout=15)
  key=transport.get_remote_server_key();actual=hashlib.sha256(key.asbytes()).hexdigest();assert actual==PIN,'HOST_KEY_MISMATCH_BEFORE_AUTH'
  transport.auth_password(req['username'],secret,fallback=False);secret=None
  progress({'stage':'PINNED_AUTHENTICATED','epoch':time.time(),'host':req['host'],'public_hostkey_SHA':actual})
  # Guard current-created exact own marker before the first write. No foreign directory enumeration.
  guard="""import pathlib,json,os
R=pathlib.Path('/data/robemo/polar-rl-train')
assert R.resolve()==R and not R.is_symlink()
m=json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_text())
assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['schema']=='mod4.robemo.frozen_experts.workspace.v1' and m['host']=='10.50.0.86' and m['username']=='robemo' and m['authorized_root']==str(R)
D=R/'setup_runs/W35_PINNED_ENV_STAGE1_20261027_V1'
assert not D.exists()
assert not (R/'staging/W35_frozen_minimum_v1').exists()
for p in [R/'setup_runs',R/'staging']:
 assert not p.is_symlink() and p.resolve().is_relative_to(R)
 p.mkdir(exist_ok=True)
D.mkdir(mode=0o700)
(D/'SETUP_RUN_OWNER.json').write_text(json.dumps({'schema':'mod4.isolated.setup.v1','host':'10.50.0.86','root':str(R),'new_run':str(D),'no_GPU_GO':True}))
print(json.dumps({'passed':True,'new_root':str(D)}))
"""
  ch=transport.open_session(timeout=15);ch.exec_command('/usr/bin/python3 -B -c '+shlex.quote(guard));ch.settimeout(25)
  out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status()
  save('OWN_SCOPE_GUARD_ACTUAL.json',{'returncode':rc,'stdout':out,'stderr':err});assert rc==0,'own_scope_guard_failed'
  sftp=paramiko.SFTPClient.from_transport(transport)
  made={ROOT,ROOT+'/staging',ROOT+'/setup_runs',RUN}
  def mkdir_parent(target):
   p=PurePosixPath(target).parent
   if str(p) in made:return
   mkdir_parent(str(p/'placeholder')) if False else None
   chain=[]
   while str(p) not in made:chain.append(p);p=p.parent
   for d in reversed(chain):
    assert str(d).startswith(ROOT+'/');sftp.mkdir(str(d),mode=0o700);made.add(str(d))
  def upload(src,target):
   assert target.startswith(ROOT+'/') and '..' not in PurePosixPath(target).parts
   mkdir_parent(target)
   with Path(src).open('rb') as inp,sftp.open(target,'wx') as out:
    out.set_pipelined(True)
    while True:
     raw=inp.read(1024*1024)
     if not raw:break
     assert time.time()<DEADLINE-45,'upload_finite_deadline'
     out.write(raw)
  manifest=json.loads(TEMPLATE.read_text());last=0
  for i,r in enumerate(manifest['files']):
   upload(r['source_path'],ROOT+'/'+r['target_relative'])
   if time.time()-last>=20:progress({'stage':'W35_FROZEN_RAW_UPLOAD','epoch':time.time(),'files_uploaded':i+1,'files_total':len(manifest['files']),'no_model_deserialization':True});last=time.time()
  upload(TEMPLATE,RUN+'/W35_DEPLOYMENT_MANIFEST.json')
  upload(HERE/'EXACT72_ISAACLAB_SOURCE_AND_APPS.zip',RUN+'/EXACT72_ISAACLAB_SOURCE_AND_APPS.zip')
  upload(HERE/'remote_owned_isolated_install_v1.py',RUN+'/remote_owned_isolated_install_v1.py')
  progress({'stage':'RAW_PAYLOAD_UPLOAD_COMPLETE','epoch':time.time(),'files':len(manifest['files']),'SDK_source_archive_SHA':'d5b007ff6b4209c3dd1f23a4fd1a1cc66d8cbc564300830c2ba3b24fec98c9cc'})
  channel=transport.open_session(timeout=15);channel.exec_command('/usr/bin/python3 -u -B '+shlex.quote(RUN+'/remote_owned_isolated_install_v1.py'))
  channel.settimeout(1);buf=b'';errbuf=b'';last=time.time()
  while not channel.exit_status_ready() or channel.recv_ready() or channel.recv_stderr_ready():
   if channel.recv_ready():
    buf+=channel.recv(65536)
    while b'\n' in buf:
     line,buf=buf.split(b'\n',1)
     if line:
      try:v=json.loads(line)
      except Exception:v={'stage':'REMOTE_STDOUT_TEXT','text':line.decode(errors='replace')}
      progress(v);last=time.time()
   if channel.recv_stderr_ready():errbuf+=channel.recv_stderr(65536)
   if time.time()-last>=30:progress({'stage':'SAME_HANDLE_REMOTE_WAIT','epoch':time.time()});last=time.time()
   if time.time()>DEADLINE+20:raise TimeoutError('remote_finite_not_returned_before_deadline')
   time.sleep(.2)
  rc=channel.recv_exit_status()
  save('OWNED_ISOLATED_SETUP_RETURNED_ACTUAL.json',{'passed':rc==0,'actual_returncode':rc,'actual_finite_returned':True,'epoch':time.time(),'stderr':errbuf.decode(errors='replace'),'stdout_remaining':buf.decode(errors='replace'),'remote_root':ROOT,'new_setup_run':RUN,'no_GPU_GO':True,'no_ledger_IO':True,'actual_SDK_CUDA_restore_newPPO_pending':True})
  print(json.dumps({'stage':'FINITE_RETURNED','returncode':rc,'report':str(REPORTS/'OWNED_ISOLATED_SETUP_RETURNED_ACTUAL.json')}),flush=True)
 except BaseException as e:
  msg=str(e)
  if secret:msg=msg.replace(secret,'[REDACTED]')
  save('OWNED_ISOLATED_SETUP_ORIGINAL_ERROR_ACTUAL.json',{'error_type':type(e).__name__,'error':msg,'epoch':time.time(),'partial_preserved':True,'no_GPU_GO':True})
  print(json.dumps({'stage':'LOCAL_ORIGINAL_ERROR','error_type':type(e).__name__,'error':msg}),flush=True)
  raise
 finally:
  secret=None
  if sftp:sftp.close()
  if transport:transport.close()
if __name__=='__main__':main()
