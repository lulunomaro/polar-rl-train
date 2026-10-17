"""Public4-only auxiliary repair: new native and full CPU before one new finite GO."""
from pathlib import Path
import os,sys,json,time,getpass,secrets,traceback
B=Path(__file__).resolve().parent;W=B.parent.parent;R=B/'reports';M=W/'MOD4_RECOVERY_CLOSED_FINAL_H1_STORAGE_BOUNDED_HANDOFF_20261017';F=W/'MOD4_THREE_EXPERTS_HEALTHY_FOLLOWUP_V3_20261017';sys.path.insert(0,str(F));import deploy_recovered_three_finals_new_native_then_original_owner_once as d
a=d.a;launch=d.launch
SOURCE='/mnt/mod4_linux_durable_20261013/H1mp_1810p2/owner';TARGET='/home/lc01/Zonglin Li/zonglin2/tasks/H1mp_1810p2'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=r'''
from pathlib import Path
import sys,json,time,psutil,subprocess,shutil,fcntl
B=Path(sys.argv[1]);old=Path(sys.argv[2]);owned=Path('/home/lc01/Zonglin Li/zonglin2');gpu=sys.argv[3];assert B.resolve().is_relative_to(owned.resolve()) and old.resolve().is_relative_to(owned.resolve()) and not B.exists() and len(str(B/'job0/tmp'))<100
e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());t=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and t['returncode']==0 and t['final']['passed'] and not t['original_error']
alive=[]
for p in psutil.process_iter(['pid','cmdline','create_time']):
 try:
  if p.pid!=__import__('os').getpid() and any(s.startswith(str(old)+'/') for s in p.info['cmdline'] or []):alive.append(p.info)
 except psutil.Error:pass
assert not alive,alive
for p in (owned/'state'/('three_expert_v2_'+gpu+'.lock'),owned/'state/finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(gpu in line for line in compute.splitlines()),compute
g=subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits']).decode();line=next(x for x in g.splitlines() if gpu in x);free=shutil.disk_usage(owned).free;assert int(line.split(',')[-1])>7000 and psutil.virtual_memory().available>8*1024**3 and free>25*1024**3;B.mkdir(parents=True);(B/'job0').mkdir()
print(json.dumps(dict(epoch=time.time(),new_root=str(B),previous_same_GPU_scope_actual_out=True,actual_private_and_shared_validation_fcntl_free=True,selected_GPU_resource=line,target_durable_free=free,compute_snapshot=compute,no_GPU_or_GO_yet=True)))
'''
OWNER=r'''
from pathlib import Path
import sys,json,time,psutil,fcntl,socket,shutil,os
B=Path(sys.argv[1]);owned=Path('/mnt/mod4_linux_durable_20261013');assert os.path.ismount(owned), 'Original authorized D must actually be mounted before metadata owner';old=owned/'H1mb_1810p1/owner';assert B.resolve().is_relative_to(owned.resolve()) and not B.exists();assert json.loads((old/'COHORT_FINAL.json').read_bytes())['original_cost_settled'] and json.loads((old/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
i=json.loads((old/'OWNER_IDENTITY.json').read_bytes())
if psutil.pid_exists(i['pid']):
 p=psutil.Process(i['pid']);assert abs(p.create_time()-i['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());assert v['active_segment'] is None and v['authorized_training_seconds']==1188000 and len(v['budget_extensions'])==7 and v['remaining_training_seconds']>1800;locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(p))
with socket.socket() as s:s.bind(('10.24.4.210',29754))
assert shutil.disk_usage(owned).free>1024**3 and shutil.disk_usage(C.parent).free>512*1024**2;B.mkdir(parents=True)
print(json.dumps(dict(epoch=time.time(),previous_P1_original_cost_settled_all_children_out=True,actual_original_activeNone_two_fcntl_free=locks,source_metadata_only_not_GPU_admission=True,D_free=shutil.disk_usage(owned).free,original_budget_remaining_snapshot=v['remaining_training_seconds'],no_canonical_write=True)))
'''
def terminal(c,cfg,key):
 code=r'''
from pathlib import Path
import sys,time,json,os
B=Path(ROOT);sys.path.insert(0,str(B));import three_slot_common_v1 as b
from three_slot_finite_node_v1 import send
cfg=CONFIG;key=KEY;s=cfg['experts'][key];row=dict(key=key,phase='frozen_behavior_review_hold_before_worker' if key=='e2' else 'frozen_selfrescue_review_hold_before_worker',manifest_SHA=s['manifest_SHA'],native_CPU=None,native_GPU_waited_EXIT0=False,terminal_all_own_children_waited=True,actual_admission_sender_children0=True,returncode=0,original_error=False,no_paid_production_worker_or_GO=True,admission_sender_identity=b.ident(os.getpid()));assert not b.valid_ready(row,s);reply=send(dict(s,token=cfg['token'],run_id=cfg['run_id']),row);assert reply['go'] is None;out=dict(epoch=time.time(),row=row,reply=reply,no_GPU_child_or_paid_GO=True);b.put(B/(key+'_PREGO_REVIEW_HOLD_ACK_ACTUAL.json'),out);print(json.dumps(out))
'''
  # Config travels only as SSH program stdin, never argv or a saved file.
 put(key.upper()+'_ACTUAL_PREGO_REVIEW_HOLD_ACK.json',a.code(c,a.t.PY,code.replace('ROOT',repr(SOURCE)).replace('CONFIG',repr(cfg)).replace('KEY',repr(key))))
def main():
 prep=json.loads((R/'PUBLIC4_REPAIR_V2_H1_FINITE_NEW_SOURCE_NATIVE_PAYLOAD_CPU_ACTUAL.json').read_bytes());assert prep['passed_CPU_only'];toy=json.loads((B.parent/'reports/ACTUAL_PUBLIC4_PPO_UPDATE_AST_NORMAL_ZERO_MIXED_GRADIENT_CPU_ACTUAL.json').read_bytes());assert toy['actual_normal_only_update_actor_STD_bitexact_to_original'] and len(toy['negative_cases'])==11;specs=prep['specs'];assert specs['h1']['source_Adamstep']==645620 and specs['h1']['max_parent_seconds']==1800 and specs['h1']['execution_backend']=='target72'
 put('PUBLIC4_REPAIR_V2_H1_NEW_FINITE_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_all_host_transport=True,actual_newsource_native_required_no_old_GPU_replay=True));pw=getpass.getpass('Host72 human-requested H1 new finite training (hidden): ');c=None;cfg=None
 try:
  c=a.connect72(pw);put('H1_TARGET72_ACTUAL_NEW_ROOT_RESOURCE_OSLOCK_ADMISSION.json',a.code(c,a.PY,CREATE,TARGET,specs['h1']['previous_runtime_root'],specs['h1']['GPU_UUID'],timeout=60));sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   dest=B/'payload/h1';paths=[*sorted(dest.rglob('*'))];created={TARGET,TARGET+'/job0'}
   for p in paths:
    if '__pycache__' in p.parts:continue
    rel=p.relative_to(dest).as_posix();remote=TARGET+'/'+rel
    if p.is_dir():
     if remote not in created:sf.mkdir(remote);created.add(remote)
    elif p.is_file():sf.put(str(p),remote)
  finally:sf.close()
  put('H1_TARGET72_FULL_MANIFEST_SOURCE_ACTUAL_RSL_SDK_CPU_ADMITTED.json',a.code(c,a.PY,d.CPU,TARGET,timeout=180))
  put('PUBLIC4_OWNED_PPO_TARGET_ACTUAL_IMPORT_GRADIENT_CPU.json',a.code(c,a.PY,"from pathlib import Path;import sys,json,torch;B=Path(sys.argv[1]);sys.path.insert(0,str(B/'job0/runtime/isaac/mod4'));import owned_h1_public4_mean_overflow_ppo_v2 as owned;from h1_public4_mean_overflow_loss_v2 import public4_mean_overflow_loss;x=torch.full((2,6),-100.,requires_grad=True);p=torch.zeros(2,35);p[0,28]=1;p[1,32]=1;v=public4_mean_overflow_loss(x,p);v.backward();assert not x.grad[0].any() and (x.grad[1]<0).all() and not torch.cuda.is_initialized();print(json.dumps(dict(actual_owned_public4_PPO_module=owned.PPO.__module__,normal_direct_aux_grad0=True,public4_overflow_grad_correct=True,no_optimizer_or_CUDA=True)))",TARGET,timeout=90))
 finally:
  if c:c.close();c=None
 try:
  c=a.t.connect();put('H1_NEW_ORIGINAL_O_WRITER_ACTUAL_HANDOFF_ADMISSION.json',a.code(c,a.t.PY,OWNER,SOURCE,timeout=60));sf=c.open_sftp()
  try:
   for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):sf.put(str(B/n),SOURCE+'/'+n)
  finally:sf.close()
  put('H1_TARGET72_SOURCE_OWNER_FILES_SHA_AST_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import ast,hashlib,json;B=Path("+repr(SOURCE)+");rows="+repr([dict(name=n,SHA=a.H(B/n)) for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','owner_listener_ready_cpu_reviewed_v1.py')])+";[(ast.parse((B/r['name']).read_text('utf8')),None) for r in rows];assert all(hashlib.sha256((B/r['name']).read_bytes()).hexdigest()==r['SHA'] for r in rows);print(json.dumps(dict(passed_CPU_SHA_AST=True,files=rows)))"))
  cfg=dict(role='owner',experts=specs,run_id='H1_TARGET72_CLOSED24_FINITE_'+str(time.time_ns()),token=secrets.token_hex(32));owner=launch(a.code,c,a.t.PY,SOURCE,'three_slot_finite_owner_v1.py',cfg);put('H1_TARGET72_NEW_ORIGINAL_OWNER_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,no_GO_yet=True))
  put('H1_TARGET72_SOURCE_LISTENER_ACTUAL_READY.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json;B=Path("+repr(SOURCE)+");sys.path.insert(0,str(B));from owner_listener_ready_cpu_reviewed_v1 import wait_actual;print(json.dumps(wait_actual(B,"+repr(owner['detached_pid'])+",20.)))",timeout=40));terminal(c,cfg,'e2');terminal(c,cfg,'recovery')
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);pw=None;node=launch(a.code,c,a.PY,TARGET,'three_slot_finite_node_v1.py',dict(specs['h1'],role='node',run_id=cfg['run_id'],token=cfg['token']));put('PUBLIC4_REPAIR_V2_H1_STRICT_NATIVE_REUSE_NEW_FINITE_PPO_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,node=node,source_owner_root=SOURCE,h1root=TARGET,H1_source_SHA=specs['h1']['source_SHA'],H1_source_Adam645620=True,H1_72GPU0_own_newsource_native180_full_CPU_required_before_any_GO=True,cap1800_updates24_headroom300_8GiB_reserve_25GiB_start_guard_unchanged=True,E2_and_recovery_hold_no_worker_or_GO=True,actual_detached_not_yet_immutable_first_local_CPU=True,original_sole_writer_original_budget_sum_actual_once_unchanged=True,stdin_only_HMAC_not_saved_or_argv=True));print(json.dumps(dict(owner=owner,node=node,new_H1_finite_node_dispatched_GO_only_after_strict_same_source_native_reuse=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_TARGET72_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_actual_first_no_blind_relaunch_or_hotpatch=True));raise
