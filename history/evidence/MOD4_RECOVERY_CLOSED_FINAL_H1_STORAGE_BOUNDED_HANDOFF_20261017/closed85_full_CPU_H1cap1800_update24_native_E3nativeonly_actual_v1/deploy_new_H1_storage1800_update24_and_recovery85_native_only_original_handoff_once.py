"""New owned roots; H1 paid only after own nativeCPU, recovery native-only, E2 review hold."""
from pathlib import Path
import os,sys,json,time,getpass,secrets,traceback
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';Q=B/'payload';F=W/'MOD4_THREE_EXPERTS_HEALTHY_FOLLOWUP_V3_20261017';sys.path.insert(0,str(F))
import deploy_recovered_three_finals_new_native_then_original_owner_once as d
a=d.a;launch=d.launch
SOURCE='/mnt/mod4_linux_durable_20261013/T3_1710v10hr/owner'
ROOTS=dict(h1='/mnt/mod4_linux_durable_20261013/T3_1710v10hr/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/T3_1710v10hr/recovery')
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
OWNER_ADMISSION=r'''
from pathlib import Path
import sys,json,time,psutil,fcntl,socket,shutil
B=Path(sys.argv[1]);owned=Path('/mnt/mod4_linux_durable_20261013');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists();old=owned/'T3_1710v9r72rec/owner'
assert json.loads((old/'COHORT_FINAL.json').read_bytes())['original_cost_settled'] and json.loads((old/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'];i=json.loads((old/'OWNER_IDENTITY.json').read_bytes())
if psutil.pid_exists(i['pid']):
 p=psutil.Process(i['pid']);assert abs(p.create_time()-i['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());assert v['active_segment'] is None and v['authorized_training_seconds']==1188000 and len(v['budget_extensions'])==7
locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(p))
with socket.socket() as sock:sock.bind(('10.24.4.210',29754))
assert shutil.disk_usage(owned).free>25*1024**3 and shutil.disk_usage(C.parent).free>512*1024**2;B.mkdir(parents=True)
print(json.dumps(dict(epoch=time.time(),old_owner_actual_out_original_cost_settled=True,original_activeNone_two_real_fcntl_free=locks,source_D_free=shutil.disk_usage(owned).free,no_canonical_write=True,new_unused_owner_root=str(B))))
'''
def terminal(c,cfg,key,native_parent):
 code=r'''
from pathlib import Path
import sys,json,time,psutil
B=Path(ROOT);sys.path.insert(0,str(B));import three_slot_common_v1 as b
from three_slot_finite_node_v1 import send
cfg=CONFIG;s=cfg['experts'][KEY];row=dict(key=KEY,phase=PHASE,manifest_SHA=s['manifest_SHA'],native_CPU=None,native_GPU_waited_EXIT0=False,terminal_all_own_children_waited=True,actual_admission_sender_children0=True,returncode=0,original_error=False,no_paid_production_worker_or_GO=True,separate_unpaid_recovery_native_parent=NATIVE_PARENT,admission_sender_identity=b.ident(psutil.Process().pid))
assert not b.valid_ready(row,s);reply=send(dict(s,token=cfg['token'],run_id=cfg['run_id']),row);assert reply['go'] is None;v=dict(epoch=time.time(),row=row,reply=reply,HMAC_verified=True,no_paid_GO_for_this_slot=True);b.put(B/(KEY+'_UNPAID_OR_BEHAVIOR_HOLD_TERMINAL_ACK_ACTUAL.json'),v);print(json.dumps(v))
'''
 # send() is loaded from this immutable node source uploaded alongside the owner.
 code=code.replace('ROOT',repr(SOURCE)).replace('CONFIG',repr(cfg)).replace('KEY',repr(key)).replace('PHASE',repr('frozen_behavior_review_hold_before_worker' if key=='e2' else 'native_only_review_unpaid_no_production_GO')).replace('NATIVE_PARENT',repr(native_parent))
 put(key.upper()+'_ACTUAL_PREGO_HOLD_TERMINAL_ACK.json',a.code(c,a.t.PY,code))
def main():
 proof=json.loads((R/'H1_BOUNDED_ONE_PAID_SLOT_RECOVERY_NATIVE_ONLY_OWNER_HTTP_CPU_ACTUAL.json').read_bytes());assert proof['passed_actual_ownerloop_localhost_CPU'];assert json.loads((R/'RECOVERY_NATIVE_ONLY_PARENT_REAL_FLOW_CPU_ACTUAL.json').read_bytes())['passed_actual_parent_flow_CPU'];prep=json.loads((R/'CLOSED_RECOVERY85_FULL_CPU_H1_BOUNDED_RECOVERY_NATIVE_ONLY_PAYLOADS_PREPARED_ACTUAL.json').read_bytes());assert prep['passed_CPU_only'];specs=proof['specs'];assert specs['h1']['max_parent_seconds']==1800 and specs['h1']['source_Adamstep']==643700 and specs['recovery']['source_Adamstep']==657660
 put('H1_BOUNDED_RECOVERY_NATIVE_ONLY_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),actual_alive_only_exclusive_all_transport=True,source_target_newCPU_before_any_launch=True,no_old_once_replay=True));pw=getpass.getpass('Host72 new source85 native-only review (hidden): ');c=None;cfg=None
 # Extra admission rejects unknown compute on the exact requested GPU before making directories.
 create=d.CREATE.replace(";B.mkdir(parents=True);(B/'job0').mkdir()", ";compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(sys.argv[6] in line for line in compute.splitlines()),compute;B.mkdir(parents=True);(B/'job0').mkdir()")
 assert create!=d.CREATE;d.CREATE=create;d.ROOTS=ROOTS;d.Q=Q;d.put=put
 try:
  c=a.t.connect();d.upload(c,a.t.PY,'h1',specs['h1'])
 finally:a.t.close(c);c=None
 try:
  c=a.connect72(pw);d.upload(c,a.PY,'recovery',specs['recovery']);native=launch(a.code,c,a.PY,ROOTS['recovery'],'recovery_source85_native_only_finite_parent_v1.py',dict(specs['recovery'],role='native_only'));put('RECOVERY_SOURCE85_NATIVE_ONLY_PARENT_DETACHED_ACTUAL.json',dict(epoch=time.time(),parent=native,native_only_zero_PPO_zero_charge=True,not_yet_native_CPU_passed=True))
 finally:
  if c:c.close();c=None
 try:
  c=a.t.connect();put('NEW_H1_ORIGINAL_OWNER_ACTUAL_SOURCE_HANDOFF_ADMISSION.json',a.code(c,a.t.PY,OWNER_ADMISSION,SOURCE))
  sf=c.open_sftp()
  try:
   for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):sf.put(str(B/name),SOURCE+'/'+name)
  finally:sf.close()
  put('NEW_SOURCE_OWNER_FILES_ACTUAL_SHA_AST.json',a.code(c,a.t.PY,"from pathlib import Path;import ast,hashlib,json;B=Path("+repr(SOURCE)+");rows="+repr([dict(name=n,SHA=a.H(B/n)) for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','owner_listener_ready_cpu_reviewed_v1.py')])+";[(ast.parse((B/r['name']).read_text('utf8')),None) for r in rows];assert all(hashlib.sha256((B/r['name']).read_bytes()).hexdigest()==r['SHA'] for r in rows);print(json.dumps(dict(passed_CPU_SHA_AST=True,files=rows)))"))
  cfg=dict(role='owner',experts=specs,run_id='H1_1800_UPDATE24_RECOVERY85_NATIVEONLY_'+str(time.time_ns()),token=secrets.token_hex(32));owner=launch(a.code,c,a.t.PY,SOURCE,'three_slot_finite_owner_v1.py',cfg);put('H1_BOUNDED_ORIGINAL_OWNER_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,no_GO_yet=True))
  put('SOURCE_OWNER_POST_LISTENER_READY_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json;B=Path("+repr(SOURCE)+");sys.path.insert(0,str(B));from owner_listener_ready_cpu_reviewed_v1 import wait_actual;print(json.dumps(wait_actual(B,"+repr(owner['detached_pid'])+",20.)))",timeout=40))
  terminal(c,cfg,'e2',native);terminal(c,cfg,'recovery',native)
  h1=launch(a.code,c,a.t.PY,ROOTS['h1'],'three_slot_finite_node_v1.py',dict(specs['h1'],role='node',run_id=cfg['run_id'],token=cfg['token']))
  put('H1_BOUNDED_NEW_NATIVE_AND_RECOVERY85_NATIVE_ONLY_CHAIN_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,h1node=h1,recovery_native_only_parent=native,source_owner_root=SOURCE,roots=ROOTS,H1_source_SHA=specs['h1']['source_SHA'],H1_source_Adam=643700,H1_cap1800_update24_headroom300_reserve8GiB=True,recovery_source_SHA=specs['recovery']['source_SHA'],recovery_source_Adam=657660,recovery_native_only_zero_GO_PPO_charge=True,E2_behavior_hold_zero_worker_GO=True,new_native_H1_180_recovery336_must_actually_pass_full_CPU=True,actual_dispatch_not_native_CPU_or_PPO_pass=True,one_original_writer_only_H1_actual_paid_interval_no_new_budget=True,credentials_HMAC_SSHstdin_and_childstdin_memory_only=True))
  print(json.dumps(dict(owner=owner,h1node=h1,recovery_native_only_parent=native,actual_detached_not_yet_native_or_PPO_pass=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  a.t.close(c)
if __name__=='__main__':
 try:main()
 except BaseException:put('M_NATIVE_H1_BOUND_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),unknown_actual_first_no_blind_relaunch_or_hotpatch=True));raise
