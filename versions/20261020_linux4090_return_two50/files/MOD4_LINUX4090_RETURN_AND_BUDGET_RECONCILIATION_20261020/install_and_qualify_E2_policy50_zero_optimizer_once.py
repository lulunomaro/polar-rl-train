from pathlib import Path,PurePosixPath
import hashlib,json,os,sys,time,traceback
import strict_original_Linux_transport_memory as t
B=Path(__file__).resolve().parent;R=B/'reports';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
INSTALL=r'''
from pathlib import Path
import fcntl,json,os,psutil,shutil,subprocess,time
root=Path(v['root']);owned=Path('/mnt/mod4_linux_durable_20261013');old=Path(v['spec']['previous_runtime_root']);assert root.resolve().is_relative_to(owned.resolve()) and owned.is_mount() and not root.exists();assert not any(p.pid!=os.getpid() and any(x.startswith(str(old)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));exit=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());assert exit['actual_all_own_children_waited'];canonical=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(canonical.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7
for q in (Path(v['spec']['private_lock']),canonical.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
gpu=v['spec']['GPU_UUID'];compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(gpu in line for line in compute.splitlines());line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if gpu in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
before={x['relative']:x for x in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};root.mkdir(parents=True);need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];p=old/rel;q=root/rel;assert q.resolve().is_relative_to(root.resolve());q.parent.mkdir(parents=True,exist_ok=True);previous=before.get(rel)
 if previous and previous['SHA']==row['SHA'] and previous['bytes']==row['bytes'] and p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and p.suffix!='.pt':shutil.copy2(p,q);copied+=1
 else:need.append(row)
print(json.dumps(dict(epoch=time.time(),root=str(root),need_upload=need,immutable_source_files_copied=copied,GPU_line=line,durable_free=shutil.disk_usage(owned).free,no_GPU_or_canonical_write=True)))
'''
QUALIFY=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,subprocess,time,traceback
B=Path(v['root']);spec=v['spec'];sys=__import__('sys');sys.path.insert(0,str(B));import three_slot_common_v1 as common
assert not (B/'job0/clock_native50').exists();lock=Path(spec['private_lock']).open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);p=None
try:
 gpu=spec['GPU_UUID'];compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(gpu in x for x in compute.splitlines());line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if gpu in x);assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B).free>25*1024**3
 env=common.environment(spec);log=B/'job0/policy50_native_WORKER.log';p=subprocess.Popen([spec['python'],'-u','-B',str(B/'native_admission_worker.py'),'--job','0','--phase','native'],cwd=B,env=env,stdout=log.open('xb'),stderr=subprocess.STDOUT,start_new_session=True,close_fds=True);identity=common.ident(p.pid);common.put(B/'POLICY50_NATIVE_WORKER_STARTED_ACTUAL.json',identity);rc=p.wait(timeout=540);common.put(B/'POLICY50_NATIVE_WORKER_WAITED_EXIT_ACTUAL.json',dict(epoch=time.time(),pid=p.pid,returncode=rc,actual_waited=True));out=B/'job0/clock_native50';errors=[str(x) for x in out.glob('*ORIGINAL_ERROR*.json')];assert rc==0 and not errors,(rc,errors);final=json.loads((out/'FINAL.json').read_bytes());clock=json.loads((out/'CLOCK_NATIVE24_COMPLETE.json').read_bytes());assert final['passed'] and final['final']['updates']==0 and clock['controls']==24 and clock['callbacks']==192 and clock['maximum_target_error']<=1e-6
 import torch;torch.set_num_threads(2);source=torch.load(B/'job0/source'/spec['source_filename'],map_location='cpu',weights_only=False);z=torch.load(final['final']['path'],map_location='cpu',weights_only=False);counts=[0,0]
 def finite(x):
  if torch.is_tensor(x):counts[0]+=1;counts[1]+=int(x.is_floating_point());assert not x.is_floating_point() or torch.isfinite(x).all()
  elif isinstance(x,dict):
   for y in x.values():finite(y)
  elif isinstance(x,(tuple,list)):
   for y in x:finite(y)
 def exact(a,b):
  if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
  if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(exact(a[k],b[k]) for k in a)
  if isinstance(a,(tuple,list)):return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
  return a==b
 finite(z);assert counts==[175,98] and z['policy_clock']['policy_hz']==50
 for key in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(source[key],z[key]),key
 assert {int(x['step']) for x in z['optimizer_state_dict']['state'].values()}=={772320};health=list((out/'logs').glob('*/CLOCK_TRAINING_HEALTH.json'));assert len(health)==1;h=json.loads(health[0].read_bytes());assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==192 and h['integrity_task_reset_events']==h['unknown_task_reset_events']==0 and not h['nonfinite_observed'] and h['max_mimic_error_rad']<=.01 and not h['stop_reason'];assert not torch.cuda.is_initialized();proof=dict(epoch=time.time(),passed=True,source_SHA=spec['source_SHA'],source_Adamstep=772320,whole_tensor_counts=counts,all_core_actor9_critic8_STD17Adam_literal_exact=True,clock=clock,health=h,actual_worker=identity,actual_worker_waited_EXIT0=True,zero_optimizer_updates=True,no_GO_or_PPO_or_original_canonical_write=True,not_skill_qualification=True);common.put(B/'POLICY50_CLOCK_NATIVE24_ALL_STATE_CPU_ADMITTED_ACTUAL.json',proof)
except BaseException:
 common.put(B/'POLICY50_NATIVE_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),worker=common.ident(p.pid) if p else None,no_automatic_retry=True));raise
finally:fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
print(json.dumps(dict(proof=proof,private_fcntl_released=True,actual_finite_returned=True)))
'''
def main():
 q=json.loads((R/'E2_POLICY50_FULL_PAYLOAD_CPU_PREPARED_ACTUAL.json').read_bytes());assert q['passed_source_CPU'];put('E2_POLICY50_TARGET_INSTALL_NATIVE_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,qualification_only_no_production_GO=True));payload=Path(q['payload']);m=json.loads((payload/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());c=t.connect();sf=None
 try:
  installed=t.code(c,INSTALL,dict(root=q['new_unused_root'],spec=q['spec'],manifest=m),timeout=90);put('E2_POLICY50_NEW_UNUSED_ROOT_RESOURCE_INSTALL_ACTUAL.json',installed);sf=c.open_sftp();sf.get_channel().settimeout(90)
  for row in installed['need_upload']:sf.put(str(payload/row['relative']),q['new_unused_root']+'/'+row['relative'])
  sf.put(str(payload/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),q['new_unused_root']+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json');sf.close();sf=None
  cpu=t.code(c,"import json,runpy,sys;sys.argv=['target_policy50_full_source_sdk_cpu_review.py',v['root']];runpy.run_path(v['root']+'/target_policy50_full_source_sdk_cpu_review.py',run_name='__main__')",dict(root=q['new_unused_root']),timeout=240);put('E2_POLICY50_TARGET_FULL_MANIFEST_RSL_SDK_CPU_ACTUAL.json',cpu)
  v=t.code(c,QUALIFY,dict(root=q['new_unused_root'],spec=q['spec']),timeout=600);put('E2_POLICY50_ACTUAL_NATIVE24_ALL_STATE_AND_HEALTH_CPU_ACTUAL.json',v);sf=c.open_sftp();sf.get_channel().settimeout(90);texts=[]
  for rel in ('POLICY50_NATIVE_WORKER_STARTED_ACTUAL.json','POLICY50_NATIVE_WORKER_WAITED_EXIT_ACTUAL.json','POLICY50_CLOCK_NATIVE24_ALL_STATE_CPU_ADMITTED_ACTUAL.json','job0/policy50_native_WORKER.log','job0/clock_native50/POLICY50_ACTUAL_CLOCK_AND_INHERITANCE.json','job0/clock_native50/STARTUP_SOURCE_ACTUAL.json','job0/clock_native50/CLOCK_NATIVE24_COMPLETE.json','job0/clock_native50/FINAL.json'):
   p=B/'E2_native24_actual_text'/Path(*PurePosixPath(rel).parts);p.parent.mkdir(parents=True,exist_ok=True);sf.get(q['new_unused_root']+'/'+rel,str(p));texts.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)))
  put('E2_POLICY50_NATIVE_TARGET_FINITE_RETURNED_ACTUAL.json',dict(epoch=time.time(),actual_finite_transport_returned=True,actual=v,collected_texts=texts,no_production_GO_or_PPO_or_account_write=True));print(json.dumps(dict(E2_native50_clock_passed=True,tensor_counts=[175,98],zero_optimizer=True,production_GO=False)),flush=True)
 finally:
  if sf:sf.close()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E2_POLICY50_NATIVE_INSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_replay_root_or_once=True));raise
