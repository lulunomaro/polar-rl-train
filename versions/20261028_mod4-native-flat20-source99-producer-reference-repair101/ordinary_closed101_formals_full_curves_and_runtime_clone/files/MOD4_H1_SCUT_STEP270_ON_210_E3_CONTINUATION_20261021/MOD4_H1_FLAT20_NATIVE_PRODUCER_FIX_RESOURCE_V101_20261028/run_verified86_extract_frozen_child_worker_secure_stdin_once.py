"""Root-only credential ingress for the child's frozen extraction worker; no GPU or model actions."""
from pathlib import Path
import hashlib,importlib.util,json,os,shlex,socket,sys,threading,time,traceback
import paramiko
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
B=L/'NEW_HOST_VERIFIED_BUNDLE_EXTRACT_RELOCATION_SOURCE_V1';R=B/'reports';STAGE='/data/robemo/polar-rl-train/runtime_migrations/proven72_20261028_v1/extract_relocate_stage_v1'
CALLER=L/'NEW_HOST_DIRECT_HTTPS_BUNDLE_PULL_CANDIDATE_SOURCE_V1/reports/DIRECT_ALL29_ARTIFACT_PULL_AND_ORIGINAL_ENDING_RETURNED_ACTUAL.json'
PIN72='301a9837e8503b664fa4cedde20407769d8f1b86ae59d9a54afb236bdfa41795';PIN86='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b'
SRC='/home/lc01/Zonglin Li/zonglin2';PY72=[SRC+'/compat/glibc240/ld-linux-x86-64.so.2','--library-path',SRC+'/compat/glibc240:'+SRC+'/envs/mod4/lib',SRC+'/envs/mod4/bin/python','-S','-B','-u']
PRE=r'''
from pathlib import Path
import json,shutil
R=Path('/data/robemo/polar-rl-train');BASE=R/'runtime_migrations/proven72_20261028_v1';B=Path(v['root']);assert R.resolve()==R and BASE.resolve()==BASE and B.resolve()==B and B==BASE/'extract_relocate_stage_v1' and not B.exists() and not (BASE/'runtime_copy_v1').exists()
m=json.loads((R/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['host']=='10.50.0.86' and m['username']=='robemo' and m['authorized_root']==str(R)
assert shutil.disk_usage(R).free>v['logical']+1024**3
B.mkdir(mode=0o700)
with (B/'OWN_EXTRACT_RELOCATE_STAGE_MARKER.json').open('x') as f:json.dump(dict(request_id=v['request_id'],root=str(B)),f)
for n in ['home','tmp','cache','config','data','state']:(B/n).mkdir(mode=0o700)
print(json.dumps(dict(passed=True,root=str(B),request_id=v['request_id'],actual_free_bytes=shutil.disk_usage(R).free)))
'''
VERIFY=r'''
from pathlib import Path
import hashlib,json
B=Path(v['root']);assert B.resolve()==B
for name,sha in v['files'].items():
 p=B/name;assert p.resolve()==p and hashlib.sha256(p.read_bytes()).hexdigest()==sha
print(json.dumps(dict(passed=True,exact_uploaded_files=v['files'])))
'''
TEXTS=r'''
from pathlib import Path
import hashlib,json
B=Path(v['root']);assert B.resolve()==B and json.loads((B/'OWN_EXTRACT_RELOCATE_STAGE_MARKER.json').read_bytes())['request_id']==v['request_id']
rows=[];total=0
for p in sorted(B.iterdir()):
 if not p.is_file() or p.suffix not in ('.json','.jsonl','.log'):continue
 assert p.resolve()==p and not p.is_symlink();a=p.stat();assert a.st_size<128*1024**2;raw=p.read_bytes();b=p.stat();assert (a.st_size,a.st_mtime_ns)==(b.st_size,b.st_mtime_ns);total+=len(raw);assert total<256*1024**2
 rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8'),stable=True))
print(json.dumps(dict(root=str(B),all_original_UTF8=rows,read_no_runtime_binary_or_model=True)))
'''
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
def mod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def main():
 index=B/'FROZEN_VERIFIED_EXTRACT_RELOCATION_SOURCE_INDEX_V1.json';assert hashlib.sha256(index.read_bytes()).hexdigest()=='fa6484e5bc18c91b400316cc4b80baeb847afde6a2e875bd8d58c493a04e2978'
 worker=B/'target86_verify_extract_narrow_relocate_UNUSED_once_v1.py';assert hashlib.sha256(worker.read_bytes()).hexdigest()=='e7369e81c36e9e5b3e86c7f444ae3b3db052b3ec371978be9fe7d64aed7d88f3'
 raw=CALLER.read_bytes();actual=json.loads(raw);assert actual['passed_all_artifacts_only'] and actual['worker_waited']['returncode']==0 and actual['source_and_target_SSH_sequential_and_closed']
 put('ROOT_EXTRACT_INGRESS_ENTERED_BEFORE_STDIN_ACTUAL.json',dict(epoch=time.time(),local_pid=os.getpid(),actual_bulk_receipt_SHA=hashlib.sha256(raw).hexdigest(),worker_SHA=hashlib.sha256(worker.read_bytes()).hexdigest(),source72_then_target86_SSH_serial=True,original_local_bound_seconds=1900,no_GPU_model_or_account=True))
 print('READY_FOR_SINGLE_STDIN_JSON',flush=True);login=json.loads(sys.stdin.readline());assert set(login)=={'host','username','password'} and login['host']=='10.50.0.86' and login['username']=='robemo';secret86=login.pop('password');deadline=time.monotonic()+1900;client=None;sf=None;request=None
 wrapper=mod('extract_ingress_same_transport_definitions',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
 def left():
  value=deadline-time.monotonic();assert value>0,'original1900s ingress bound';return value
 def connect(host,user,password,pin):
  sock=socket.create_connection((host,22),timeout=min(10,left()));c=paramiko.Transport(sock)
  try:c.banner_timeout=min(10,left());c.auth_timeout=min(10,left());c.start_client(timeout=min(10,left()));assert hashlib.sha256(c.get_remote_server_key().asbytes()).hexdigest()==pin,'SSH hostpin before auth';c.auth_password(user,password,fallback=False);return c
  except BaseException:c.close();raise
 def run(c,python,code,v):
  ch=c.open_session(timeout=min(10,left()));ch.exec_command(' '.join(shlex.quote(x) for x in python+['-c',"import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])"]));ch.settimeout(min(30,left()));inp=ch.makefile_stdin('wb');inp.write((json.dumps(dict(v,code=code))+chr(10)).encode());inp.flush();ch.shutdown_write();out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();assert rc==0,(out,err);return json.loads(out)
 try:
  recover=mod('extract_ingress_existing72_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret72=recover.recover()
  try:client=connect('10.24.0.72','lc01',secret72,PIN72)
  finally:secret72=None
  pack=json.loads((L/'NEW_HOST_PROVEN72_RUNTIME_BUNDLE_READONLY_COLLECTION_SOURCE_V1/reports/PROVEN72_RUNTIME_EXPORT_FIRST_COLLECTION_FOOTPRINT_ABI_ACTUAL.json').read_bytes());pre=mod('frozen_extract_known_source_preflight',B/'source72_all_recorded_ownout_preflight_CODE_v1.py')
  value=run(client,PY72,pre.CODE,dict(producer=pack['producer'],caller_receipt_SHA=hashlib.sha256(raw).hexdigest(),source_service_terminal=actual['source_service_ending']['terminal']));put('FRESH_SOURCE72_ALL_RECORDED_OWNOUT_BEFORE_EXTRACT_ACTUAL.json',value);client.close();client=None;assert value['passed'] and value['all_known_recorded_out']
  builder=mod('frozen_extract_public_request_builder',B/'build_public_extract_request_from_actual_proofs_UNUSED_once_v1.py');request=builder.build(R/'FRESH_SOURCE72_ALL_RECORDED_OWNOUT_BEFORE_EXTRACT_ACTUAL.json');put('ACTUAL_PROOFS_BOUND_PUBLIC_EXTRACT_REQUEST_UNUSED.json',request)
  client=connect('10.50.0.86','robemo',secret86,PIN86);secret86=None;put('TARGET86_NEW_EXTRACT_STAGE_ADMITTED_ACTUAL.json',run(client,['/usr/bin/python3','-B'],PRE,dict(root=STAGE,logical=request['logical_input_bytes'],request_id=request['request_id'])))
  files=[worker,B/'strict_archive_and_narrow_relocation_core_v1.py',B/'EXACT_ORIGINAL_LAUNCHERS_AND_FIVE_EDITABLE_BINDING_V1.json',R/'ACTUAL_PROOFS_BOUND_PUBLIC_EXTRACT_REQUEST_UNUSED.json'];hashes={}
  sf=paramiko.SFTPClient.from_transport(client);sf.get_channel().settimeout(min(30,left()))
  for p in files:
   data=p.read_bytes();hashes[p.name]=hashlib.sha256(data).hexdigest()
   with sf.open(STAGE+'/'+p.name,'wx') as f:f.write(data)
  sf.close();sf=None;put('TARGET86_FROZEN_EXTRACT_FILES_RECONCILED_ACTUAL.json',run(client,['/usr/bin/python3','-B'],VERIFY,dict(root=STAGE,files=hashes)))
  env={'CUDA_VISIBLE_DEVICES':'','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1','HOME':STAGE+'/home','TMPDIR':STAGE+'/tmp','XDG_CACHE_HOME':STAGE+'/cache','XDG_CONFIG_HOME':STAGE+'/config','XDG_DATA_HOME':STAGE+'/data','XDG_STATE_HOME':STAGE+'/state'}
  cmd='cd '+shlex.quote(STAGE)+' && '+' '.join(shlex.quote(x) for x in ['/usr/bin/env','-u','PYTHONPATH','-u','PYTHONHOME','-u','LD_LIBRARY_PATH','-u','LD_PRELOAD']+[k+'='+v for k,v in env.items()]+['/usr/bin/python3','-u','-B',STAGE+'/'+worker.name]);ch=client.open_session(timeout=min(10,left()));ch.set_combine_stderr(True);ch.exec_command(cmd);ch.settimeout(1);inp=ch.makefile_stdin('wb');inp.write((json.dumps(request)+chr(10)).encode());inp.flush();ch.shutdown_write();timer=threading.Timer(left(),client.close);timer.daemon=True;timer.start();last=0;size=0;started=time.time()
  try:
   with (R/'ROOT_TARGET86_EXTRACT_FULL_STDOUT_STDERR_UTF8.log').open('xb') as log:
    while True:
     left()
     try:block=ch.recv(65536)
     except socket.timeout:block=None
     if block:size+=len(block);assert size<32*1024**2;log.write(block);log.flush();print(block.decode('utf8'),end='',flush=True)
     elif block==b'':break
     if time.time()-last>=30:print(json.dumps(dict(stage='SAME_HANDLE_FROZEN_CHILD_EXTRACT',epoch=time.time(),elapsed_seconds=time.time()-started,no_GPU_or_other_SSH=True)),flush=True);last=time.time()
    rc=ch.recv_exit_status();waited=dict(epoch=time.time(),actual_waited=True,returncode=rc,command=cmd,request_id=request['request_id']);put('ROOT_TARGET86_EXTRACT_ACTUAL_WAITED.json',waited)
  finally:timer.cancel()
  texts=run(client,['/usr/bin/python3','-B'],TEXTS,dict(root=STAGE,request_id=request['request_id']));put('ROOT_TARGET86_EXTRACT_ALL_ORIGINAL_UTF8_ACTUAL.json',texts);client.close();client=None
  objects={Path(x['path']).name:json.loads(x['UTF8']) for x in texts['all_original_UTF8'] if x['path'].endswith('.json')};complete=objects.get('VERIFIED_NEW_COPY_EXTRACT_AND_NARROW_RELOCATION_COMPLETE_ACTUAL.json');terminal=objects.get('EXTRACT_RELOCATE_TERMINAL_ACTUAL.json');passed=bool(rc==0 and complete and complete['passed_verified_extract_and_declared_relocation_only'] and terminal and terminal['passed_extract_and_relocate_only']);put('ROOT_VERIFIED_EXTRACT_RELOCATION_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed_extract_relocate_only=passed,actual_waited=waited,complete=complete,terminal=terminal,source72_closed_before_target86=True,all_control_SSH_closed=True,no_SDK_CUDA_model_or_training_readiness_proved=True));print(json.dumps(dict(passed_extract_relocate_only=passed,no_SDK_ready=True,all_control_SSH_closed=True)),flush=True)
  if not passed:raise SystemExit(2)
 finally:
  secret86=None
  if sf:sf.close()
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except SystemExit:raise
 except BaseException:
  put('ROOT_EXTRACT_INGRESS_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),original_inputs_and_partial_copy_retained=True,no_retry_rearm_or_cleanup=True));raise
