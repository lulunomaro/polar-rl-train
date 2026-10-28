"""One new source210 frozen case; known72 authority read only, no GO/writer."""
from pathlib import Path,PurePosixPath
import argparse,base64,hashlib,importlib.util,json,os,sys,threading,time,traceback
B=Path(__file__).resolve().parent;L=B.parent;T=L.parent;W=T.parent;R=B/'reports'
JOB='/mnt/mod4_linux_durable_20261013/MOD4_E0_ADAPTED40050_FROZEN_20261028v1/e0'
GPU='GPU-937bdb0b-0d8f-aa3d-a10e-1b24969a5d4e'
OWNER=r'''
from pathlib import Path
import hashlib,json,psutil,time
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);expected=v['owner'];go=v['go']
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c.get('budget_mode',c.get('mode'))=='finite_original_limits_restored_after_single4090_return'
assert c['remaining_training_seconds']>86412.86069250107 and c['authorized_training_seconds']==2268000 and c['historical_budget_extension_count']==9 and c['new_authority_budget_extensions']==[]
a=c['active_segment'];active=a is not None
if active:
 assert a['owner_parent_pid']==expected['pid'] and set(a['experts'])<=set(go)
 p=psutil.Process(expected['pid']);assert p.create_time()==expected['creation'];actual=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd());assert actual==expected
else:
 candidates=[x for x in c['completed_segments'] if x['owner_parent_pid']==expected['pid'] and set(x['experts'])==set(go) and all(x['experts'][k]['started_epoch']==go[k]['learning_started_epoch'] for k in go)]
 assert len(candidates)==1 and candidates[0].get('ended_epoch') is not None
print(json.dumps(dict(passed=True,epoch=time.time(),canonical_path=str(C),canonical_SHA=hashlib.sha256(raw).hexdigest(),generation=c['authority_generation'],known_original_owner=expected,known_original_GO=go,original_known_owner_active=active,known_original_closed_if_not_active=not active,remaining_snapshot=c['remaining_training_seconds'],no_authority_copy_lock_or_write=True,no_second_writer_or_new_GO=True)))
'''
PRE=r'''
from pathlib import Path
import json,subprocess,shutil,psutil,time
J=Path(v['job']);mount=Path('/mnt/mod4_linux_durable_20261013');assert mount.is_mount() and not J.parent.exists() and J.resolve().is_relative_to(mount.resolve())
m=json.loads(subprocess.check_output(['findmnt','--json','--target',str(mount),'-o','UUID,OPTIONS'],text=True))['filesystems'][0];assert str(m['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in m['options'].split(',')
apps=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);assert v['GPU'] not in apps,'selected GPU compute busy: left untouched'
line=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-gpu=uuid,name,memory.free,utilization.gpu','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip() for x in line.split(',')];assert a[0]==v['GPU'] and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(mount).free>25*1024**3
J.mkdir(parents=True,mode=0o700);print(json.dumps(dict(passed=True,epoch=time.time(),GPU_line=line,selected_compute_UUID_rows=0,no_unknown_PID_or_argv_read=True,mount=m,job=str(J))))
'''
RUN=r'''
from pathlib import Path
import base64,fcntl,hashlib,importlib.metadata as md,importlib.util,json,math,os,psutil,subprocess,time
J=Path(v['job']);lockpath=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock')
def H(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def put(n,x):
 with (J/n).open('x',encoding='utf8') as f:json.dump(x,f,indent=2)
for row in v['files']:
 p=(J/row['relative']).resolve();assert p.is_relative_to(J) and not p.is_symlink() and p.stat().st_size==row['bytes'] and H(p)==row['SHA']
versions={k:md.version(k) for k in ['torch','isaacsim','isaaclab','rsl-rl-lib']};assert versions=={'torch':'2.10.0+cu128','isaacsim':'6.0.1.0','isaaclab':'6.1.14','rsl-rl-lib':'5.0.1'}
rsl=Path(importlib.util.find_spec('rsl_rl').origin).parent;lab=Path(importlib.util.find_spec('isaaclab').origin).parent
for row in v['RSL_sources']:assert (rsl/row['relative']).stat().st_size==row['bytes'] and H(rsl/row['relative'])==row['SHA']
assert H(lab/'utils/math.py')==v['SDK_math_SHA']
assert (J/'runtime/assets/import_contract.json').read_bytes()==(J/'runtime/isaac/mod4/import_contract.json').read_bytes()
from pxr import Usd,UsdPhysics
stage=Usd.Stage.Open(str(J/'runtime/assets/robot.usd'));assert stage
for name in ['left_gas_slide','right_gas_slide']:
 p=stage.GetPrimAtPath('/Robot/joints/'+name);d=UsdPhysics.DriveAPI.Get(p,'linear');q=UsdPhysics.PrismaticJoint(p)
 assert d.GetStiffnessAttr().Get()==2000 and d.GetDampingAttr().Get()==3 and math.isclose(q.GetUpperLimitAttr().Get(),.020639440248416612,abs_tol=1e-8)
cpu=dict(passed=True,epoch=time.time(),scope='new target SDK source metadata and USD CPU, existing E0 formal wholeCPU reused; no policy model decode',versions=versions,RSL_source_bytes_exact=True,SDK_math_source_bytes_exact=True,asset_parent_contract_route_exact=True,nominal400_USD_composition=True,source_model_GPU_fullrestore_still_pending=True)
put('ACTUAL_SOURCE210_SOURCE_SDK_CPU_NO_MODEL_ADMISSION.json',cpu)
lock=lockpath.open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
try:
 apps=subprocess.check_output(['nvidia-smi','-i',v['GPU'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);assert v['GPU'] not in apps
 env=dict(os.environ,CUDA_VISIBLE_DEVICES=v['GPU'],PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1',OMNI_KIT_ACCEPT_EULA='YES',ISAACSIM_ACCEPT_EULA='Y')
 for key,value in {'HOME':'home','TMPDIR':'tmp','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','TORCH_HOME':'cache/torch','CUDA_CACHE_PATH':'cache/cuda'}.items():
  path=J/value;path.mkdir(parents=True,exist_ok=True);env[key]=str(path)
 task=dict(kind='MOD4_E0_ADAPTED40050_ORIGINAL_N20K_FROZEN_REGRESSION_V1',source_SHA='a92c9e8d7cb3dbda9828b6c37bb38dd63183818e91b1aa3f7746c2c46379c74a',num_envs=20000,controls=120,maximum_worker_seconds=480,no_optimizer_steps=True,actual_source210_SDK_admission_passed=True,actual_private_GPU_EX_held_by_parent=True,canonical72_known_owner_readonly_passed=v['authority']['passed'],known72_readonly_authority=v['authority'],full_WM_tap_included=False)
 put('FROZEN_CASE_TASK.json',task);argv=[v['python'],'-u','-B',str(J/'evaluate_E0_adapted40050_originalN20K_mean_frozen_once_v1.py'),'--job-root',str(J)]
 with (J/'FROZEN_CASE_CONSOLE_FULL.log').open('xb') as out:
  p=subprocess.Popen(argv,env=env,cwd=J,stdout=out,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);q=psutil.Process(p.pid);identity=dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),root=q.cwd());put('FROZEN_CASE_EXACT_OWN_PROCESS_STARTED.json',identity);timed=False
  try:rc=p.wait(timeout=540)
  except subprocess.TimeoutExpired:
   timed=True;p.terminate()
   try:rc=p.wait(timeout=30)
   except subprocess.TimeoutExpired:p.kill();rc=p.wait(timeout=15)
 result=J/'frozen_regression/BOUNDED_FROZEN_E0_MEAN_REGRESSION_ACTUAL.json';errors=[dict(path=str(p),text=p.read_text()) for p in (J/'frozen_regression').glob('*ORIGINAL_ERROR*.json')] if (J/'frozen_regression').is_dir() else []
 value=dict(actual_returned=True,actual_waited=True,returncode=rc,deadline_terminated=timed,identity=identity,passed=rc==0 and result.is_file() and not errors and not timed,regression=json.loads(result.read_bytes()) if result.is_file() else None,original_errors=errors,no_optimizer_or_budget_write=True,skill_graduation=False,complete_WM_dataset=False)
 put('FROZEN_E0_210_ORIGINAL_WAITED_RESULT.json',value)
finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
texts=[]
for root in [J]:
 if root.is_dir():
  for p in sorted(root.rglob('*')):
   if p.is_file() and p.suffix.lower() in ('.json','.log','.txt') and 'runtime' not in p.relative_to(J).parts:
    data=p.read_bytes();texts.append(dict(relative=p.relative_to(J).as_posix(),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),base64=base64.b64encode(data).decode()))
value.update(full_original_texts=texts,actual_private_EX_released=True);print(json.dumps(value))
'''
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def main():
 R.mkdir(exist_ok=True);put('E0_210_FROZEN_CASE_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),own_pid=os.getpid(),no_training_GO_or_secondwriter=True))
 parser=argparse.ArgumentParser();parser.add_argument('--known-owner-report',type=Path,default=L/'TWO97_H1_E3_NEW_FULL_CPU_OWNER_SOURCE_V1/reports/TWO97_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json');parser.add_argument('--known-go-report',type=Path,default=L/'TWO97_H1_E3_COMBINED_FIRST_INLINE_SOURCE_V1/reports/TWO97_ACTUAL_TWO_GO_OWNER_METADATA_RETURNED.json');args=parser.parse_args();payload=json.loads((B/'E0_FROZEN_CASE_COMPLETE_INPUT_MANIFEST_V2.json').read_bytes());actual=read_json(args.known_owner_report);first=read_json(args.known_go_report);assert actual['run_id']==next(iter(first['go'].values()))['run_id']
 wrapper=module('E0_frozen_same_compressed_install_only',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=wrapper.install()
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sec=module('E0_same_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None;stop=threading.Event()
 def progress():
  while not stop.wait(25):print(json.dumps(dict(stage='SAME_FINITE_E0_FROZEN_REGRESSION',epoch=time.time())),flush=True)
 thread=threading.Thread(target=progress,daemon=True);thread.start()
 try:
  client=d.connect72(secret);secret=None;authority=d.code(client,d.PY72,OWNER,dict(owner=actual['identities']['owner']['exact_identity'],go=first['go']),timeout=30);put('E0_CURRENT97_CANONICAL72_KNOWN_OWNER_READONLY_ADMISSION_ACTUAL.json',authority);client.close();client=None
  client=route.connect();pre=d.code(client,route.PY,PRE,dict(job=JOB,GPU=GPU),timeout=30);put('E0_210_FRESH_UUID_MOUNT_RESOURCE_ACTUAL.json',pre)
  sf=client.open_sftp();sf.get_channel().settimeout(30);made={JOB}
  try:
   for row in payload['files']:
    path=PurePosixPath(JOB)/row['relative'];assert '..' not in path.parts;parents=[];q=path.parent
    while str(q) not in made:parents.append(q);q=q.parent
    for q in reversed(parents):sf.mkdir(str(q),mode=0o700);made.add(str(q))
    with Path(row['local_path']).open('rb') as source,sf.open(str(path),'wx') as out:
     out.set_pipelined(True)
     while True:
      block=source.read(1024**2)
      if not block:break
      out.write(block)
  finally:sf.close()
  value=d.code(client,route.PY,RUN,dict(job=JOB,GPU=GPU,python=route.PY,files=[{k:r[k] for k in ('relative','bytes','SHA')} for r in payload['files']],RSL_sources=payload['RSL_sources'],SDK_math_SHA=payload['SDK_math_SHA'],authority=authority),timeout=630)
  target=R/'complete_original_UTF8_texts';target.mkdir();rows=[]
  for row in value.pop('full_original_texts'):
   data=base64.b64decode(row.pop('base64'));assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['SHA'];p=target/(hashlib.sha256(row['relative'].encode()).hexdigest()[:20]+'_'+Path(row['relative']).name)
   with p.open('xb') as f:f.write(data)
   rows.append(dict(**row,local_path=str(p)))
  value['full_original_texts']=rows
  if value.get('regression'):
   row=value['regression']['trace'];p=R/'selected32_actual_before_and_terminal_prefix.npz';sf=client.open_sftp()
   try:sf.get(row['path'],str(p))
   finally:sf.close()
   with p.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['SHA']
   row['local_path']=str(p);row['twohost_SHA']=True
  put('E0_210_BOUNDED_FROZEN_REGRESSION_ORIGINAL_RESULT_RETURNED_ACTUAL.json',value);print(json.dumps(dict(passed=value['passed'],actual_returned=True,regression=value.get('regression'),skill_graduation=False,complete_WM_dataset=False)))
 finally:
  secret=None;stop.set();thread.join(1)
  if client:client.close()
  transport.SESSION=previous
def read_json(p):return json.loads(Path(p).read_bytes())
if __name__=='__main__':
 try:main()
 except BaseException:put('E0_210_FROZEN_CASE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_or_oldsource_promotion=True));raise
