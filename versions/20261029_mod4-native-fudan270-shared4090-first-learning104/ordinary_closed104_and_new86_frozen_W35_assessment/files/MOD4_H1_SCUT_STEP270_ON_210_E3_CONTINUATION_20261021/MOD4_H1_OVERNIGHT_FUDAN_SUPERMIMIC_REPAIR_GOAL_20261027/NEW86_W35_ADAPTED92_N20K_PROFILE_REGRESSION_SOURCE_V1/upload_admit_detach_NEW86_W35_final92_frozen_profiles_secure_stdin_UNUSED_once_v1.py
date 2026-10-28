"""SOURCE ONLY until root runs: serial72-readonly then one pinned86SSH, no GO."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,importlib.util,json,os,shlex,socket,sys,threading,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
PIN='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b'
COPY='/data/robemo/polar-rl-train/runtime_migrations/proven72_20261028_v1/runtime_copy_v1'
STAGE='/data/robemo/polar-rl-train/evaluation_runs/W35_ADAPTED92_N20K_PROFILE_20261029v1/w35'
AUTH=r'''
from pathlib import Path
import hashlib,json,psutil,time
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'
assert c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[] and c['remaining_training_seconds']>86412.86069250107
active=c['active_segment'];known=v['known_binding'];bound=None
if active is not None:
 assert known is not None and set(known)=={'owner','run_id','go'}
 expected=known['owner'];assert active['owner_parent_pid']==expected['pid'] and set(active['experts'])==set(known['go'])
 p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'];actual=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd());assert actual==expected
 assert all(g['run_id']==known['run_id'] and active['experts'][key]['started_epoch']==g['learning_started_epoch'] for key,g in known['go'].items())
 bound=dict(owner=actual,run_id=known['run_id'],genuine_slots=sorted(known['go']))
print(json.dumps(dict(passed_readonly_original72_finite_authority=True,epoch=time.time(),canonical_path=str(C),canonical_SHA=hashlib.sha256(raw).hexdigest(),generation=c['authority_generation'],remaining_snapshot=c['remaining_training_seconds'],CNone=active is None,known_active_binding=bound,no_account_lock_copy_write_GO_or_secondwriter=True)))
'''
def H(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(n,x):
 R.mkdir(exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--known72-binding-json',type=Path);a=p.parse_args();R.mkdir(exist_ok=True)
 index=json.loads((B/'FROZEN_NEW86_W35_FROZEN_PROFILE_SOURCE_INDEX_V1.json').read_bytes());mf=B/'W35_NEW86_COMPLETE_INPUT_MANIFEST_V1.json';assert H(mf)==index['manifest_SHA'];manifest=json.loads(mf.read_bytes())
 for name,want in index['executable_source_SHAs'].items():assert H(B/name)==want,name
 clonepath=L/'NEW_HOST_VERIFIED_BUNDLE_EXTRACT_RELOCATION_SOURCE_V1/reports/ROOT_VERIFIED_EXTRACT_RELOCATION_RETURNED_ACTUAL.json';assert H(clonepath)==index['clone_receipt_SHA'];clone=json.loads(clonepath.read_bytes());assert clone['passed_extract_relocate_only'] and clone['actual_waited']['actual_waited'] and clone['actual_waited']['returncode']==0 and clone['all_control_SSH_closed']
 sdkpath=L/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V2_LIGHT_POLICY/reports/NEW86_NORMAL_H1_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json';assert H(sdkpath)==index['actual_clone_CUDA_SDK_receipt_SHA'];normal=json.loads(sdkpath.read_bytes());assert normal['passed_actual_wholeCPU_CUDA_fullrestore_native24_only'] and normal['private_EX_released']
 known=json.loads(a.known72_binding_json.read_bytes()) if a.known72_binding_json else None
 if known is not None:assert set(known)=={'owner','run_id','go'}
 put('NEW86_W35_ADMISSION_ENTRY_CONSUMED_BEFORE_STDIN.json',dict(epoch=time.time(),pid=os.getpid(),new_stage=STAGE,manifest_SHA=index['manifest_SHA'],maximum_seconds_after_stdin=600,no_training_GO_or_ledger_write=True))
 print('READY_FOR_SINGLE_STDIN_JSON',flush=True);req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo';secret=req.pop('password');deadline=time.monotonic()+600;stop=threading.Event();client=None;t=None;sf=None;transport=None;previous=None
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_FINITE_NEW86_W35_SOURCE_CPU_DETACHED_PROFILES',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 def remote(action,extra,seconds):
  remaining=deadline-time.monotonic();assert remaining>0;source=(B/'remote_W35_new86_profile_install_and_detach_v1.py').read_bytes().decode('utf8');assert hashlib.sha256(source.encode()).hexdigest()==index['executable_source_SHAs']['remote_W35_new86_profile_install_and_detach_v1.py'];v=dict(action=action,stage=STAGE,copy=COPY,manifest_SHA=index['manifest_SHA'],source_SHA=manifest['typed_source_SHA'],remote_code_SHA=hashlib.sha256(source.encode()).hexdigest(),**extra)
  ch=t.open_session(timeout=min(10,remaining));ch.exec_command('/usr/bin/python3 -B -c '+shlex.quote("import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])"));ch.settimeout(min(seconds,remaining))
  try:
   inp=ch.makefile_stdin('wb');inp.write((json.dumps(dict(v,code=source))+chr(10)).encode());inp.flush();ch.shutdown_write();out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();assert rc==0,(rc,err,out);return json.loads(out)
  finally:ch.close()
 try:
  wrapper=module('NEW86_W35_same_compressed_memory_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
  sec=module('NEW86_W35_original72_readonly_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');s72=sec.recover()
  try:client=d.connect72(s72);s72=None;authority=d.code(client,d.PY72,AUTH,dict(known_binding=known),timeout=30);put('ORIGINAL72_AUTHORITY_READONLY_BEFORE_CLOSE_AND_NEW86.json',authority)
  finally:
   s72=None
   if client:client.close();client=None
   if transport is not None:transport.SESSION=previous;transport=None
  # No simultaneous control SSH: source72 is closed before the86 socket exists.
  sock=socket.create_connection((req['host'],22),timeout=10);t=paramiko.Transport(sock);t.banner_timeout=10;t.auth_timeout=10;t.start_client(timeout=10);assert hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest()==PIN,'PIN_MISMATCH_BEFORE_AUTH';t.auth_password(req['username'],secret,fallback=False);secret=None
  put('NEW86_PROJECT_AND_PROVEN_RUNTIME_PRE_ACTUAL.json',remote('pre',dict(clone_complete=clone['complete'],normal_whole_result=normal),45))
  sf=paramiko.SFTPClient.from_transport(t);sf.get_channel().settimeout(30);made={STAGE}
  try:
   for i,row in enumerate(manifest['files']):
    assert deadline-time.monotonic()>150,'Upload not complete with original CPU/GPU wait reserve; partial retained'
    relative=PurePosixPath(row['relative']);assert not relative.is_absolute() and '..' not in relative.parts;target=PurePosixPath(STAGE)/relative;parents=[];q=target.parent
    while str(q) not in made:parents.append(q);q=q.parent
    for q in reversed(parents):sf.mkdir(str(q),mode=0o700);made.add(str(q))
    source=Path(row['local_path']);assert source.resolve().is_relative_to(W.resolve()) and source.stat().st_size==row['bytes'];digest=hashlib.sha256();sent=0
    with source.open('rb') as f,sf.open(str(target),'wx') as out:
     out.set_pipelined(True)
     while True:
      block=f.read(1024**2)
      if not block:break
      assert deadline-time.monotonic()>150;out.write(block);digest.update(block);sent+=len(block)
    assert sent==row['bytes'] and digest.hexdigest()==row['SHA'],row['relative']
    if i%100==0:print(json.dumps(dict(stage='NEW86_EXACT_INPUT_UPLOAD',complete_files=i+1,total_files=len(manifest['files']))),flush=True)
   with sf.open(STAGE+'/W35_NEW86_COMPLETE_INPUT_MANIFEST_V1.json','wx') as f:f.write(mf.read_bytes())
  finally:sf.close();sf=None
  put('NEW86_ALL_INPUT_POSTCOPY_FULLSHA_RETURNED_ACTUAL.json',remote('verify',{},60))
  assert deadline-time.monotonic()>150,'No CPU/model start without full original bounded wait reserve'
  value=remote('run',dict(authority=authority),150);put('NEW86_W35_WHOLECPU_CUDA_NATIVE24_ORIGINAL_RETURNED_ACTUAL.json',value);print(json.dumps({k:v for k,v in value.items() if k not in ('complete_original_UTF8','actual_phase_waits')},ensure_ascii=False))
 finally:
  secret=None;stop.set();thread.join(1)
  if sf:sf.close()
  if t:t.close()
  if client:client.close()
  if transport is not None:transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('NEW86_W35_ADMISSION_ORIGINAL_LOCAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_automatic_retry_or_training_GO=True));raise
