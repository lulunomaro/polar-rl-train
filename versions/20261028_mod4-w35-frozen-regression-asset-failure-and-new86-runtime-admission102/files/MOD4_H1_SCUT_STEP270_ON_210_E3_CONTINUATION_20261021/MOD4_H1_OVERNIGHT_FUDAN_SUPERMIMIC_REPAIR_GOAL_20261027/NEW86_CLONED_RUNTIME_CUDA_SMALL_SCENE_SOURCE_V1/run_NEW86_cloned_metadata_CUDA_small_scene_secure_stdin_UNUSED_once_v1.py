"""One86 stdin-only ingress, exact project-copy SDK, no policy or budget writer."""
from pathlib import Path
import hashlib,json,os,shlex,socket,sys,threading,time,traceback
import paramiko
B=Path(__file__).resolve().parent;R=B/'reports';L=B.parent
COPY='/data/robemo/polar-rl-train/runtime_migrations/proven72_20261028_v1/runtime_copy_v1';STAGE='/data/robemo/polar-rl-train/validation_runs/PROVEN72_CLONE_CUDA_SDK_SCENE_20261028v1'
PIN='8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b';GPU='GPU-90a66ae2-f536-7033-79c0-487536ae36d3'
PRE=r'''
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path('/data/robemo/polar-rl-train');D=Path(v['copy']);J=Path(v['stage']);assert ROOT.resolve()==ROOT and D.resolve()==D and J.resolve()==J and J.is_relative_to(ROOT) and not J.exists()
m=json.loads((ROOT/'.MOD4_NEW_HOST_WORKSPACE_MANIFEST_V1.json').read_bytes());assert m['initial_probe_id']=='MOD4_NEW_HOST_INITIAL_PROBE_1793110077908242700' and m['authorized_root']==str(ROOT)
proof=ROOT/'runtime_migrations/proven72_20261028_v1/extract_relocate_stage_v1/VERIFIED_NEW_COPY_EXTRACT_AND_NARROW_RELOCATION_COMPLETE_ACTUAL.json';raw=proof.read_bytes();assert json.loads(raw)==v['complete_clone'] and v['complete_clone']['passed_verified_extract_and_declared_relocation_only'] and v['complete_clone']['destination']==str(D)
assert (D/'run-python.sh').is_file() and (D/'run-python-compat.sh').is_file();assert shutil.disk_usage(ROOT).free>25*1024**3
line=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True,timeout=15).strip();apps=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True,timeout=15);a=[x.strip() for x in line.split(',')];assert a[0]==v['GPU'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669 and v['GPU'] not in apps,'selected GPU compute busy; untouched'
J.mkdir(parents=True,mode=0o700)
with (J/'OWN_CLONED_SDK_PROBE_MARKER.json').open('x') as f:json.dump(dict(root=str(J),source_copy=str(D),producer_SHA=v['complete_clone']['producer_SHA'],purpose='no-model SDK/CUDA/primitive-body isolation'),f)
print(json.dumps(dict(passed=True,new_stage=str(J),actual_GPU_line=line,selected_compute_UUID_rows=0,actual_clone_proof_SHA=hashlib.sha256(raw).hexdigest(),no_unknown_PID_or_venv_or_budget_change=True)))
'''
RUN=r'''
from pathlib import Path
import fcntl,hashlib,json,os,subprocess,time
ROOT=Path('/data/robemo/polar-rl-train');J=Path(v['stage']);D=Path(v['copy']);assert J.resolve()==J and J.is_relative_to(ROOT)
for row in v['sources']:assert hashlib.sha256((J/row['name']).read_bytes()).hexdigest()==row['SHA']
locks=ROOT/'state/hardware';locks.mkdir(parents=True,exist_ok=True);marker=locks/'OWN_NEW86_GPU_LOCK_SCOPE.json'
if marker.exists():assert json.loads(marker.read_bytes())==dict(root=str(ROOT),GPU_UUID=v['GPU'])
else:
 with marker.open('x') as f:json.dump(dict(root=str(ROOT),GPU_UUID=v['GPU']),f)
lock=(locks/(v['GPU']+'.private.lock')).open('a+b');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);records=[]
def ident(pid):
 p=Path('/proc')/str(pid)
 try:
  raw=(p/'stat').read_text();a=raw[raw.rfind(')')+2:].split();boot=next(int(x.split()[1]) for x in Path('/proc/stat').read_text().splitlines() if x.startswith('btime '));return dict(pid=pid,creation=boot+int(a[19])/os.sysconf('SC_CLK_TCK'),exe=os.readlink(p/'exe'),argv=[os.fsdecode(x) for x in (p/'cmdline').read_bytes().split(bytes([0])) if x],cwd=os.readlink(p/'cwd'),initial_launcher_identity_wrapper_exec_can_follow=True)
 except FileNotFoundError:return dict(pid=pid,original_spawn_already_exited=True,actual_worker_self_identity_in_phase_report_required=True)
try:
 apps=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True,timeout=15);assert v['GPU'] not in apps
 for phase,seconds,name in [('metadata',45,'CLONED_METADATA_AND_IMPORT_ROUTES_ACTUAL.json'),('tensor',90,'CLONED_TORCH_CUDA_TENSOR_EXECUTION_ACTUAL.json'),('scene',240,'CLONED_SDK_SIMPLE_NATIVE_CUDA_SCENE_24_PHYSICS_STEPS_ACTUAL.json')]:
  env=dict(os.environ,CUDA_VISIBLE_DEVICES='' if phase=='metadata' else v['GPU'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y');argv=[str(D/'run-python.sh'),'-u','-B',str(J/'cloned_runtime_tensor_and_small_scene_worker_v1.py'),'--phase',phase]
  with (J/(phase+'_COMPLETE_STDOUT_STDERR.log')).open('xb') as log:
   p=subprocess.Popen(argv,cwd=J,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);own=ident(p.pid);timed=False
   try:rc=p.wait(timeout=seconds)
   except subprocess.TimeoutExpired:
    timed=True;p.terminate()
    try:rc=p.wait(timeout=20)
    except subprocess.TimeoutExpired:p.kill();rc=p.wait(timeout=10)
  result=J/name;errors=[dict(path=str(q),value=json.loads(q.read_bytes())) for q in J.glob('*ORIGINAL_ERROR*.json')];value=json.loads(result.read_bytes()) if result.exists() else None;selfpath=J/(phase+'_OWN_CLONED_WORKER_IDENTITY.json');selfidentity=json.loads(selfpath.read_bytes()) if selfpath.exists() else None;assert selfidentity is None or selfidentity['pid']==p.pid;record=dict(phase=phase,actual_waited=True,returncode=rc,deadline_terminated=timed,initial_launcher_identity=own,actual_worker_self_identity=selfidentity,passed=rc==0 and not timed and value is not None and value['passed'] and selfidentity is not None and not errors,result=value,original_errors=errors);records.append(record)
  with (J/(phase+'_ACTUAL_ORIGINAL_WAITED_RESULT.json')).open('x') as f:json.dump(record,f,indent=2)
  if not record['passed']:break
finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
texts=[]
for p in sorted(J.iterdir()):
 if p.is_file() and p.suffix in {'.json','.log','.jsonl'}:
  raw=p.read_bytes();assert len(raw)<=32*1024**2;texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8')))
passed=len(records)==3 and all(x['passed'] for x in records)
print(json.dumps(dict(passed_cloned_CUDA_and_simple_SDK_scene_only=passed,actual_phase_waits=records,complete_original_UTF8=texts,private_GPU_lock_released=True,source_and_old_venvs_unmodified=True,no_policy_model_MOD4_native24_or_optimizer_or_canonical_IO=True,not_training_or_skill_ready=True)))
'''
def put(n,v):
 R.mkdir(exist_ok=True)
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 R.mkdir(exist_ok=True);index=json.loads((B/'FROZEN_NEW86_CUDA_SMALL_SCENE_SOURCE_INDEX_V1.json').read_bytes());proof=L/'NEW_HOST_VERIFIED_BUNDLE_EXTRACT_RELOCATION_SOURCE_V1/reports/ROOT_VERIFIED_EXTRACT_RELOCATION_RETURNED_ACTUAL.json';raw=proof.read_bytes();assert hashlib.sha256(raw).hexdigest()==index['actual_clone_receipt_SHA'];clone=json.loads(raw);assert clone['passed_extract_relocate_only'] and clone['actual_waited']['actual_waited'] and clone['actual_waited']['returncode']==0 and clone['all_control_SSH_closed']
 put('NEW86_NO_MODEL_SDK_PROBE_ENTRY_ENTERED_BEFORE_STDIN_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),actual_clone_receipt_SHA=index['actual_clone_receipt_SHA'],maximum_control_seconds_after_STDIN=600,no_model_or_budget_operations=True));print('READY_FOR_SINGLE_STDIN_JSON',flush=True);req=json.loads(sys.stdin.readline());assert set(req)=={'host','username','password'} and req['host']=='10.50.0.86' and req['username']=='robemo';secret=req.pop('password');t=None;sf=None;stop=threading.Event();deadline=time.monotonic()+600
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_HANDLE_CLONED_NEW86_CUDA_SMALL_SCENE',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 def run(code,args,timeout):
  remaining=deadline-time.monotonic();assert remaining>0;ch=t.open_session(timeout=min(10,remaining));ch.exec_command('/usr/bin/python3 -B -c '+shlex.quote("import sys,json;v=json.loads(sys.stdin.readline());exec(v['code'])"));ch.settimeout(min(timeout,remaining));inp=ch.makefile_stdin('wb');inp.write((json.dumps(dict(args,code=code))+chr(10)).encode());inp.flush();ch.shutdown_write();out=ch.makefile('rb').read().decode();err=ch.makefile_stderr('rb').read().decode();rc=ch.recv_exit_status();assert rc==0,(err,out);return json.loads(out)
 try:
  sock=socket.create_connection((req['host'],22),timeout=10);t=paramiko.Transport(sock);t.banner_timeout=10;t.auth_timeout=10;t.start_client(timeout=10);assert hashlib.sha256(t.get_remote_server_key().asbytes()).hexdigest()==PIN,'SSH_PIN_MISMATCH_BEFORE_AUTH';t.auth_password(req['username'],secret,fallback=False);secret=None
  put('NEW86_ACTUAL_CLONE_SCOPE_AND_FRESH_GPU_ADMISSION.json',run(PRE,dict(copy=COPY,stage=STAGE,GPU=GPU,complete_clone=clone['complete']),45));sources=[];sf=paramiko.SFTPClient.from_transport(t)
  for name in ['cloned_runtime_tensor_and_small_scene_worker_v1.py','zonglin2_app_launcher.py']:
   p=B/name;data=p.read_bytes();assert hashlib.sha256(data).hexdigest()==index['source_SHAs'][name]
   with sf.open(STAGE+'/'+name,'wx') as f:f.write(data)
   sources.append(dict(name=name,SHA=hashlib.sha256(data).hexdigest()))
  sf.close();sf=None;value=run(RUN,dict(copy=COPY,stage=STAGE,GPU=GPU,sources=sources),500);put('NEW86_CLONED_CUDA_SMALL_SCENE_ORIGINAL_RETURNED_ACTUAL.json',value);print(json.dumps({k:x for k,x in value.items() if k!='complete_original_UTF8'}))
 finally:
  secret=None;stop.set();thread.join(1)
  if sf:sf.close()
  if t:t.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('NEW86_PROBE_ENTRY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_or_model_source_promotion=True));raise
