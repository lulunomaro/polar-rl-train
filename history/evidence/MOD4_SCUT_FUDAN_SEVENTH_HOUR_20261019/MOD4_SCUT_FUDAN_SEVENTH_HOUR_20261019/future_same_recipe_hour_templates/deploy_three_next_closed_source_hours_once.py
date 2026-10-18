"""One new three-expert hour after actual saved closure, same original writer/accounting."""
from pathlib import Path
import sys,os,json,time,getpass,secrets,traceback,hashlib
B=Path(__file__).resolve().parent;W=B.parent;R=B/'reports';T=W/'MOD4_THREE_GPU_REAL_TRAINING_HOUR_COHORT_20261018';sys.path.insert(0,str(T));import deploy_three_actual_hour_learning_closed_H1_continuation_V2_once as old
a=old.a;H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();SOURCE='/mnt/mod4_linux_durable_20261013/T3sf8_1910v13/owner'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
INSTALL=r'''
from pathlib import Path
import sys,json,os,psutil,fcntl,subprocess,shutil,time
spec=json.loads(sys.argv[1]);B=Path(sys.argv[2]);A=Path(spec['previous_runtime_root']);m=json.loads(sys.argv[3]);owned=Path('/mnt/mod4_linux_durable_20261013' if spec['execution_backend']=='source210' else '/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists();assert spec['execution_backend']!='source210' or owned.is_mount();terminal=json.loads((A/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];e=json.loads((A/'NODE_EXIT_ACTUAL.json').read_bytes());assert terminal['returncode']==0 and not terminal['errors'] and terminal['final']['passed'] and terminal['final']['final']['SHA']==spec['source_SHA'] and terminal['terminal_all_own_children_waited'] and e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'];assert not any(p.pid!=os.getpid() and any(x.startswith(str(A)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));locks=[spec['private_lock']]
if spec['execution_backend']=='target72':locks.append(str(owned/'state/finite_environment_validation.lock'))
for q in locks:
 with Path(q).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(spec['GPU_UUID'] in x for x in compute.splitlines());assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3;B.parent.mkdir(parents=True,exist_ok=True);B.mkdir();before={r['relative']:r for r in json.loads((A/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']};need=[];copied=0
for r in m['files']:
 rel=r['relative'];dest=B/rel;assert dest.resolve().is_relative_to(B.resolve());dest.parent.mkdir(parents=True,exist_ok=True);p=A/rel;o=before.get(rel)
 if o and o['bytes']==r['bytes'] and o['SHA']==r['SHA'] and not rel.endswith('.pt'):
  assert p.is_file() and not p.is_symlink() and p.stat().st_size==r['bytes'];shutil.copy2(p,dest);copied+=1
 else:need.append(r)
print(json.dumps(dict(epoch=time.time(),new_unused_root=str(B),old_full_saved_actual_EXIT0_out=True,actual_private_shared_fcntl_free=locks,durable_free=shutil.disk_usage(owned).free,compute_snapshot=compute,immutable_same_manifest_files_copied=copied,need_upload=need,no_old_PT_or_raw_rehash_or_GPU_replay=True)))
'''
OWNER=r'''
from pathlib import Path
import sys,json,time,os,psutil,fcntl,socket
B=Path(sys.argv[1]);A=Path('/mnt/mod4_linux_durable_20261013/T3sf7_1910v12/owner');assert not B.exists() and B.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013').resolve());final=json.loads((A/'COHORT_FINAL.json').read_bytes());e=json.loads((A/'OWNER_EXIT_ACTUAL.json').read_bytes());assert final['original_cost_settled'] and e['original_cost_settled'] and e['own_original_two_fcntl_released_if_held'];assert not any(p.pid!=os.getpid() and any(x.startswith(str(A)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7;rows=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==270162];assert len(rows)==1 and set(rows[0]['experts'])=={'h1','e2','recovery'} and all(x['actual_returncode']==0 and x['duration_bound_passed'] for x in rows[0]['experts'].values());locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(p))
with socket.socket() as s:s.bind(('10.24.4.210',29754))
B.mkdir();print(json.dumps(dict(epoch=time.time(),original_owner270162_actual_out=True,actual_original_cost_once=rows[0],canonicalNone_two_real_fcntl_free=locks,portfree=True,remaining_snapshot=c['remaining_training_seconds'],no_original_account_write=True)))
'''
def upload(c,py,key,p):
 local=Path(p['payloads'][key]);root=p['roots'][key];m=json.loads((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());v=a.code(c,py,INSTALL,json.dumps(p['specs'][key]),root,json.dumps(m),timeout=180);put(key.upper()+'_NEW_UNUSED_SOURCE_OLD_CLOSED_RESOURCES_INSTALL_ACTUAL.json',v);sf=c.open_sftp();sf.get_channel().settimeout(120)
 try:
  for r in v['need_upload']:sf.put(str(local/r['relative']),root+'/'+r['relative'])
  sf.put(str(local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 finally:sf.close()
 put(key.upper()+'_NEW_SOURCE_TARGET_FULL_INSTALLED_RSL_SDK_CPU_ACTUAL.json',a.code(c,py,old.pre.old.CPU,root,timeout=240));put(key.upper()+'_NEW_SOURCE_ACTUAL_CLOSED_PRODUCTION_CONTINUATION_CPU.json',a.code(c,py,"from pathlib import Path;import sys,json;B=Path(sys.argv[1]);sys.path.insert(0,str(B));from closed_production_continuation_CPU_v2 import load;v=load(json.loads(sys.argv[2]),B);print(json.dumps(dict(qualification=v,actual_same_backend_closed_source_CPU_passed=True,no_native_replay_or_GO=True)))",root,json.dumps(p['specs'][key]),timeout=180))
def main():
 p=json.loads((R/'THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes());assert p['passed'];put('THREE_NEXT_HOUR_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_alive_only_exclusive_all_transport=True));pw=getpass.getpass('72 three closed-source next hours (hidden): ');c=None;cfg=None
 try:
  c=a.connect72(pw)
  for k in ('h1','recovery'):upload(c,a.PY,k,p)
 finally:
  if c:c.close();c=None
 try:
  c=a.t.connect();upload(c,a.t.PY,'e2',p);put('PREVIOUS_THREE_HOUR_ACTUAL_ACCOUNT_OUT_REAL_LOCKS_HANDOFF.json',a.code(c,a.t.PY,OWNER,SOURCE,timeout=90));sf=c.open_sftp()
  try:
   for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):sf.put(str(B/'controllers'/n),SOURCE+'/'+n)
  finally:sf.close()
  cfg=dict(role='owner',experts=p['specs'],run_id='THREE_NEXT_CLOSED_HOUR_'+str(time.time_ns()),token=secrets.token_hex(32));owner=old.launch(a.code,c,a.t.PY,SOURCE,'three_slot_finite_owner_v1.py',cfg);put('THREE_NEXT_HOUR_ONE_ORIGINAL_OWNER_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner));put('THREE_NEXT_HOUR_ORIGINAL_LISTENER_READY_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json;B=Path(sys.argv[1]);sys.path.insert(0,str(B));from owner_listener_ready_cpu_reviewed_v1 import wait_actual;print(json.dumps(wait_actual(B,int(sys.argv[2]),20.)))",SOURCE,str(owner['detached_pid']),timeout=45));nodes={'e2':old.launch(a.code,c,a.t.PY,p['roots']['e2'],'three_slot_finite_node_v1.py',dict(p['specs']['e2'],role='node',run_id=cfg['run_id'],token=cfg['token']))};put('E2_NEXT_HOUR_NODE_DETACHED_ACTUAL.json',dict(epoch=time.time(),node=nodes['e2']))
 finally:
  if c:c.close();c=None
 try:
  c=a.connect72(pw);pw=None
  for k in ('h1','recovery'):nodes[k]=old.launch(a.code,c,a.PY,p['roots'][k],'three_slot_finite_node_v1.py',dict(p['specs'][k],role='node',run_id=cfg['run_id'],token=cfg['token']))
  put('THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,nodes=nodes,source_root=SOURCE,roots=p['roots'],specs=p['specs'],all_three_direct_full_production_source_not_native_replay=True,one_original_writer_independent_intervals_once=True,all_GO_save3600_lifecycle3900_exit300=True,no_total_budget_PPO_reward_LR_STD_physics_threshold_change=True,not_actual_learning_claim_before_GO=True));print(json.dumps(dict(owner=owner,nodes=nodes,next_three_hour_chain_detached=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('THREE_NEXT_HOUR_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_partial_no_repeat_or_hotpatch=True));raise
