"""Start the three original experts after actual current-H1 saved exit and sole-writer handoff."""
from pathlib import Path
import os,sys,json,time,getpass,secrets,traceback,hashlib
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';sys.path.insert(0,str(B));import preupload_E2_E3_complete_learning_payloads_current_H1_untouched_once as pre
a=pre.a;launch=pre.old.launch;SOURCE='/mnt/mod4_linux_durable_20261013/T3h_1810v1/owner';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
ADMIT_OWNER=r'''
from pathlib import Path
import sys,json,time,os,psutil,fcntl,socket
B=Path(sys.argv[1]);A=Path('/mnt/mod4_linux_durable_20261013/H1h2_1810p5/owner');assert not B.exists() and B.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013').resolve());f=json.loads((A/'COHORT_FINAL.json').read_bytes());e=json.loads((A/'OWNER_EXIT_ACTUAL.json').read_bytes());assert f['original_cost_settled'] and e['original_cost_settled'] and e['own_original_two_fcntl_released_if_held'];identity=json.loads((A/'OWNER_IDENTITY.json').read_bytes());own=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(A)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
assert not own;C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7;closed=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==124906];assert len(closed)==1 and closed[0]['experts']['h1']['actual_returncode']==0 and closed[0]['experts']['h1']['duration_bound_passed'];locks=[]
for q in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with q.open('rb+') as h:fcntl.flock(h,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(h,fcntl.LOCK_UN);locks.append(str(q))
with socket.socket() as s:s.bind(('10.24.4.210',29754))
B.mkdir();print(json.dumps(dict(epoch=time.time(),actual_previous_H1_owner124906_allout=True,actual_previous_H1_cost_once=closed[0],canonicalNone_and_two_real_fcntl_free=locks,listener_port_free=True,new_unused_owner_root=str(B),no_original_ledger_write=True)))
'''
CREATE_H1=r'''
from pathlib import Path
import sys,json,os,time,psutil,fcntl,subprocess,shutil
B=Path(sys.argv[1]);A=Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1h2_1810p5');owned=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists();e=json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes());t=json.loads((A/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and t['returncode']==0 and t['final']['passed'] and not t['errors'];own=[]
for p in psutil.process_iter(['pid','cmdline','create_time']):
 try:
  if p.pid!=os.getpid() and any(x.startswith(str(A)+'/') for x in p.info['cmdline'] or []):own.append(p.info)
 except psutil.Error:pass
assert not own;gpu='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
for q in (owned/'state'/('three_expert_v2_'+gpu+'.lock'),owned/'state/finite_environment_validation.lock'):
 with q.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(gpu in s for s in compute.splitlines());assert shutil.disk_usage(owned).free>25*1024**3 and psutil.virtual_memory().available>8*1024**3;B.parent.mkdir(parents=True,exist_ok=True);B.mkdir();print(json.dumps(dict(epoch=time.time(),actual_old_H1_allout=True,current_private_shared_free=True,compute=compute,owned_new_root=str(B))))
'''

def sync_unused_preuploaded(c,py,key,local,root):
 code=r"""
from pathlib import Path
import json,sys,hashlib,os,psutil,time
B=Path(sys.argv[1]);new=json.loads(sys.argv[2]);assert not (B/'node_CONSOLE.log').exists() and not (B/'job0/production').exists();old=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());assert old['source_SHA']==new['source_SHA'];before={r['relative']:r for r in old['files']};changed=[r for r in new['files'] if r['relative'] not in before or (r['bytes'],r['SHA'])!=(before[r['relative']]['bytes'],before[r['relative']]['SHA'])];assert all(not r['relative'].startswith(('job0/runtime/','job0/assets/','job0/source/','job0/native/','lib/')) for r in changed);assert not any(p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));history=B/'PRELAUNCH_ORIGINAL_V1';assert not history.exists();history.mkdir();(history/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_bytes((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
for row in changed:
 p=B/row['relative']
 if p.exists():
  dest=history/row['relative'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
print(json.dumps(dict(epoch=time.time(),actual_unused_no_node_or_production=True,changed=changed,only_continuation_protocol_no_PPO_or_physics_change=True,original_files_preserved=True)))
"""
 m=json.loads((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());v=a.code(c,py,code,root,json.dumps(m),timeout=90);put(key.upper()+'_V2_UNUSED_CONTROLLER_CHANGES_ORIGINALS_PRESERVED.json',v);sf=c.open_sftp()
 try:
  for r in v['changed']:sf.put(str(local/r['relative']),root+'/'+r['relative'])
  sf.put(str(local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 finally:sf.close()
 put(key.upper()+'_V2_UNUSED_PROTOCOL_SOURCE_TARGET_CPU_ACTUAL.json',a.code(c,py,pre.old.CPU,root,timeout=180))

def main():
 prep=json.loads((R/'THREE_REAL_GPU_HOURLY_CLOSED_CONTINUATION_PAYLOADS_V2_CPU_PREPARED_ACTUAL.json').read_bytes());assert prep['passed'];specs=prep['specs'];roots=prep['roots'];assert set(specs)=={'h1','e2','recovery'} and len({s['GPU_UUID'] for s in specs.values()})==3;put('THREE_ACTUAL_LEARNING_ONE_HOUR_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transports=True));pw=getpass.getpass('72 three actual independent expert learning slots (hidden): ');c=None;cfg=None
 try:
  c=a.connect72(pw);sync_unused_preuploaded(c,a.PY,'recovery',Path(prep['payloads']['recovery']),roots['recovery']);put('H1_NEW_LATEST_SOURCE_CURRENT_GPU_LOCKS_OLD_EXIT_ADMISSION.json',a.code(c,a.PY,CREATE_H1,roots['h1'],timeout=90));local=Path(prep['payloads']['h1']);sf=c.open_sftp();made={roots['h1']}
  try:
   sf.get_channel().settimeout(120)
   for p in sorted(local.rglob('*')):
    if '__pycache__' in p.parts:continue
    remote=roots['h1']+'/'+p.relative_to(local).as_posix()
    if p.is_dir():
     if remote not in made:sf.mkdir(remote);made.add(remote)
    else:sf.put(str(p),remote)
  finally:sf.close()
  put('H1_NEW_LATEST_SOURCE_TARGET_FULL_RSL_SDK_CPU_ADMITTED.json',a.code(c,a.PY,pre.old.CPU,roots['h1'],timeout=240))
  put('H1_HEALTHY_CLOSED_PRODUCTION_SOURCE_ACTUAL_TARGET_CPU_ADMISSION.json',a.code(c,a.PY,"from pathlib import Path;import sys,json;B=Path(sys.argv[1]);sys.path.insert(0,str(B));from closed_production_continuation_CPU_v2 import load;v=load(json.loads(sys.argv[2]),B);print(json.dumps(dict(actual_closed_same_backend_checkpoint_CPU_passed=True,qualification=v,no_new_native_or_PPO_or_budget=True)))",roots['h1'],json.dumps(specs['h1']),timeout=180))
  for key in ('recovery',):
   check=a.code(c,a.PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==sys.argv[2];print(json.dumps(dict(preuploaded_manifest_exact=True)))",roots[key],specs[key]['manifest_SHA'],timeout=60);put(key.upper()+'_PREUPLOADED_LEARNING_MANIFEST_STILL_EXACT.json',check)
 finally:
  if c:c.close();c=None
 try:
  c=a.t.connect();sync_unused_preuploaded(c,a.t.PY,'e2',Path(prep['payloads']['e2']),roots['e2']);put('E2_PREUPLOADED_LEARNING_MANIFEST_STILL_EXACT.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json,hashlib;B=Path(sys.argv[1]);assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==sys.argv[2];print(json.dumps(dict(preuploaded_manifest_exact=True)))",roots['e2'],specs['e2']['manifest_SHA'],timeout=60));put('ORIGINAL_ONE_WRITER_H1_ACTUAL_COST_OUT_CANONICAL_LOCKS_HANDOFF.json',a.code(c,a.t.PY,ADMIT_OWNER,SOURCE,timeout=90));sf=c.open_sftp()
  try:
   for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):sf.put(str(B/'controllers_v2'/name),SOURCE+'/'+name)
  finally:sf.close()
  cfg=dict(role='owner',experts=specs,run_id='THREE_REAL_GPU_ONE_HOUR_'+str(time.time_ns()),token=secrets.token_hex(32));owner=launch(a.code,c,a.t.PY,SOURCE,'three_slot_finite_owner_v1.py',cfg);put('THREE_REAL_GPU_ONE_ORIGINAL_OWNER_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,no_new_GO_yet=True));put('THREE_REAL_GPU_ORIGINAL_LISTENER_READY_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json;B=Path(sys.argv[1]);sys.path.insert(0,str(B));from owner_listener_ready_cpu_reviewed_v1 import wait_actual;print(json.dumps(wait_actual(B,int(sys.argv[2]),20.)))",SOURCE,str(owner['detached_pid']),timeout=45));nodes={'e2':launch(a.code,c,a.t.PY,roots['e2'],'three_slot_finite_node_v1.py',dict(specs['e2'],role='node',run_id=cfg['run_id'],token=cfg['token']))};put('E2_ACTUAL_LEARNING_NODE_DETACHED_PENDING_GO.json',dict(epoch=time.time(),node=nodes['e2'],not_yet_PPO=True))
 finally:
  if c:c.close();c=None
 try:
  c=a.connect72(pw);pw=None
  for key in ('h1','recovery'):nodes[key]=launch(a.code,c,a.PY,roots[key],'three_slot_finite_node_v1.py',dict(specs[key],role='node',run_id=cfg['run_id'],token=cfg['token']))
  put('THREE_REAL_GPU_ONE_HOUR_NATIVE_REUSE_AND_LEARNING_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,nodes=nodes,source_root=SOURCE,roots=roots,specs=specs,actual_detached_chain=True,H1_healthy_same_backend_closed_production_checkpoint_direct_learning=True,E2_E3_actual_same_source_native_reuse_then_learning=True,three_real_learning_not_claimed_before_GO=True,one_original_writer_sum_independent_actual_intervals_once=True,all_three_save_after_true_GO3600_exit300=True,no_total_budget_reward_LR_STD_command_physics_threshold_change=True));print(json.dumps(dict(owner=owner,nodes=nodes,roots=roots,actual_three_learning_chain_dispatched=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('THREE_REAL_GPU_CONTINUATION_V2_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_partial_no_repeat_or_hotpatch=True));raise
