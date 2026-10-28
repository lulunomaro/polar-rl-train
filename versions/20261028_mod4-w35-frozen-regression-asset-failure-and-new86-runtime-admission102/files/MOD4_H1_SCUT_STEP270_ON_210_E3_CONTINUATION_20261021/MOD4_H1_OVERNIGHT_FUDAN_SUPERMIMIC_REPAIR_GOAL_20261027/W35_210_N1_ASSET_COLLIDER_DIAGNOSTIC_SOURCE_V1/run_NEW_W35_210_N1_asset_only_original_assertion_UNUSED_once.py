"""One serial read72->close->source210 finite; no model or account writer."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,sys,threading,time,traceback
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent;T=L.parent;W=T.parent
OLD='/mnt/mod4_linux_durable_20261013/MOD4_W35_ADAPTED40050_FROZEN_PROFILES_20261028v2/w35'
NEW='/mnt/mod4_linux_durable_20261013/MOD4_W35_N1_ASSET_COLLIDER_DIAGNOSTIC_20261028v1/w35'
PRE_OWN=r'''
from pathlib import Path
import json,os
J=Path(v['old'])
def out(row):
 p=Path('/proc')/str(row['pid'])
 try:
  raw=(p/'stat').read_text();a=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));created=boot+int(a[19])/os.sysconf('SC_CLK_TCK')
 except FileNotFoundError:return True
 return created!=row['creation'] or a[0]=='Z'
sup=json.loads((J/'OWN_FINITE_FROZEN_EVAL_SUPERVISOR_IDENTITY.json').read_bytes());assert sup==v['supervisor'];worker=json.loads((J/'OWN_W35_FROZEN_WORKER_EXACT_IDENTITY.json').read_bytes());assert out(sup) and out(worker)
term=json.loads((J/'FROZEN_W35_ORIGINAL_WAITED_TERMINAL_ACTUAL.json').read_bytes());assert term['actual_worker_waited'] and term['private_EX_released'] and not term['passed_frozen_execution']
print(json.dumps(dict(passed_original_V2_ownout=True,supervisor=sup,worker=worker,original_terminal=term,no_unknown_process_inspected=True)))
'''
COPY=r'''
from pathlib import Path
import hashlib,json,os
A=Path(v['old']);B=Path(v['new']);rows=[]
for r in v['rows']:
 rel=r['relative'];assert rel.startswith(('runtime/','lib/')) or rel=='original_run_manifest.json'
 p=A/rel;q=B/rel;assert p.resolve().is_relative_to(A) and q.resolve().is_relative_to(B) and not p.is_symlink();s=p.stat();assert s.st_size==r['bytes'];q.parent.mkdir(parents=True,exist_ok=True)
 if rel.endswith('.npz') or rel=='runtime/assets/source_700N/robot.usd':os.link(p,q);assert os.path.samestat(p.stat(),q.stat())
 else:
  raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==r['SHA'];q.write_bytes(raw)
 assert (s.st_size,s.st_mtime_ns)==(p.stat().st_size,p.stat().st_mtime_ns)
 rows.append(dict(relative=rel,bytes=r['bytes'],producer_SHA=r['SHA']))
print(json.dumps(dict(passed=True,input_rows=rows,no_model_PT_or_output_copied=True,original_source_unchanged=True)))
'''
RUN=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,subprocess,time,traceback
J=Path(v['new']);GPU=v['GPU'];lock=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock').open('rb+');p=None;identity=None;rc=None;timeout=False;error=None
def ident(pid):
 q=psutil.Process(pid);return dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),root=q.cwd())
try:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 apps=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True,timeout=15);line=subprocess.check_output(['nvidia-smi','-i',GPU,'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=15).strip();row=[x.strip() for x in line.split(',')];assert GPU not in apps and row[0]==GPU and row[1]=='NVIDIA GeForce RTX 4090' and int(row[2])>15669
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=GPU,PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for k,n in {'HOME':'home','TMPDIR':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','XDG_STATE_HOME':'state','CUDA_CACHE_PATH':'cache/cuda','TORCH_HOME':'cache/torch'}.items():
  d=J/n;d.mkdir(parents=True,exist_ok=True);env[k]=str(d)
 worker=J/'diagnose_original_W35_N1_asset_colliders_once.py';assert hashlib.sha256(worker.read_bytes()).hexdigest()==v['worker_SHA']
 argv=[v['python'],'-u','-B',str(worker),'--job-root',str(J)]
 with (J/'N1_WORKER_COMPLETE_STDOUT_STDERR.log').open('xb') as f:
  p=subprocess.Popen(argv,env=env,cwd=J,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);identity=ident(p.pid)
  try:rc=p.wait(timeout=180)
  except subprocess.TimeoutExpired:
   timeout=True;assert psutil.Process(p.pid).create_time()==identity['creation'];p.terminate()
   try:rc=p.wait(timeout=30)
   except subprocess.TimeoutExpired:assert psutil.Process(p.pid).create_time()==identity['creation'];p.kill();rc=p.wait(timeout=15)
except BaseException:error=traceback.format_exc()
finally:
 fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
texts=[]
for q in sorted(J.glob('*.json'))+sorted(J.glob('*.log')):
 raw=q.read_bytes();texts.append(dict(path=str(q),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8')))
passed=(J/'N1_ORIGINAL_ENV_BUILD_PASSED.json').exists() and not (J/'N1_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json').exists() and rc==0 and not timeout and error is None
value=dict(epoch=time.time(),passed_original_N1_environment=passed,actual_worker_waited=p is not None and p.poll() is not None,returncode=rc,timeout=timeout,worker=identity,private_EX_released=True,primary_error=error,complete_original_UTF8=texts,no_model_actor_PPO_or_Canonical_write=True,diagnostic_does_not_claim_W35_skill=True)
with (J/'N1_ORIGINAL_WAITED_TERMINAL_ACTUAL.json').open('x') as f:json.dump(value,f,indent=2)
print(json.dumps(value))
'''
def put(n,x):
 R.mkdir(exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 put('N1_ASSET_ONLY_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),no_model_read=True))
 parent=module('N1_original_source210_interfaces_not_main',L/'W35_210_ADAPTED40050_N20K_BOUNDED_SKILL_REGRESSION_SOURCE_V1/install_admit_launch_detached_W35_210_frozen_profiles_UNUSED_once_v1.py')
 manifest=json.loads((L/'W35_210_V2_PRECLOSE_EXCEPTION_DIAGNOSTIC_SOURCE_V1/W35_V2_PRECLOSE_COMPLETE_INPUT_MANIFEST.json').read_bytes())
 actual=json.loads((L/'W35_210_V2_PRECLOSE_EXCEPTION_DIAGNOSTIC_SOURCE_V1/reports/NEW_W35_V2_SOURCE_SDK_AND_FINITE_DIAGNOSTIC_DETACHED_RETURNED_ACTUAL.json').read_bytes())
 owner=json.loads((L/'TWO101_PRODUCER_FIXED_NATIVE20_ORIGINAL_OWNER_SOURCE_V1/reports/TWO101_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json').read_bytes());go=json.loads((L/'TWO101_PRODUCER_FIXED_NATIVE20_FIRST_POLICY_OBSERVER_SOURCE_V1/reports/TWO101_ACTUAL_TWO_GO_OR_ORIGINAL_ERROR_OWNER_RETURNED.json').read_bytes())
 wrapper=module('N1_same_memory_transport_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sec=module('N1_same72_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_HANDLE_W35_N1_ASSET_ONLY',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 try:
  client=d.connect72(secret);secret=None;put('CANONICAL101_KNOWN_CLOSED_OR_ACTIVE_READONLY_ACTUAL.json',d.code(client,d.PY72,parent.OWNER,dict(owner=owner['identities']['owner']['exact_identity'],go=go['go']),timeout=30));client.close();client=None
  client=route.connect();put('V2_ORIGINAL_OWNOUT_AND_TERMINAL_ACTUAL.json',d.code(client,route.PY,PRE_OWN,dict(old=OLD,supervisor=actual['identity']),timeout=20));put('FRESH_N1_RESOURCE_ACTUAL.json',d.code(client,route.PY,parent.PRE,dict(job=NEW,GPU=parent.GPU),timeout=30))
  rows=[r for r in manifest['files'] if r['relative'].startswith(('runtime/','lib/')) or r['relative']=='original_run_manifest.json'];put('N1_RUNTIME_INPUTS_ONLY_ACTUAL.json',d.code(client,route.PY,COPY,dict(old=OLD,new=NEW,rows=rows),timeout=60))
  worker=B/'diagnose_original_W35_N1_asset_colliders_once.py';sf=client.open_sftp()
  try:
   with sf.open(NEW+'/'+worker.name,'wx') as f:f.write(worker.read_bytes())
  finally:sf.close()
  value=d.code(client,route.PY,RUN,dict(new=NEW,GPU=parent.GPU,python=route.PY,worker_SHA=hashlib.sha256(worker.read_bytes()).hexdigest()),timeout=245);put('W35_N1_ORIGINAL_SHAPES_SETTINGS_AND_PRECLOSE_ERROR_RETURNED_ACTUAL.json',value);print(json.dumps({k:x for k,x in value.items() if k!='complete_original_UTF8'}))
 finally:
  secret=None;stop.set();thread.join(1)
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('N1_ASSET_ONLY_ORIGINAL_LOCAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry=True));raise
