"""Complete only the previously unused H1 upload and remaining new slots; no replay."""
from pathlib import Path
import os,sys,json,time,getpass,secrets,traceback
import deploy_three_next_closed_source_hours_once as d
B=d.B;R=d.R;a=d.a
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CHECK=r'''
from pathlib import Path
import sys,json,os,psutil,fcntl,subprocess,time
B=Path(sys.argv[1]);oldSHA=sys.argv[2];m=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());import hashlib
assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==oldSHA
assert not any((B/n).exists() for n in ('NODE_IDENTITY.json','NODE_CURRENT.json','GO_PRODUCTION.json','node_CONSOLE.log','job0/native','job0/production','job0/GO_PRODUCTION.json'))
assert not any(p.pid!=os.getpid() and any(x.startswith(str(B)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
q=json.loads((B/'TARGET_FULL_SOURCE_INSTALLED_RSL_SDK_CPU_ADMITTED_ACTUAL.json').read_bytes());assert q['passed_CPU_only'] and q['source_SHA']==m['source_SHA'];paths=json.loads(sys.argv[3])
for name in paths:
 with Path(name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert 'GPU-16828f91' not in compute
print(json.dumps(dict(epoch=time.time(),actual_no_owner_node_native_worker_GO=True,H1_only_full_upload_and_CPU_completed=True,actual_private_shared_locks_free=paths,source_SHA=m['source_SHA'],old_manifest_SHA=oldSHA,compute_snapshot=compute)))
'''
def main():
 p=json.loads((R/'THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_PORTABLE_PATH_V2_ACTUAL.json').read_bytes());prior=json.loads((R/'THREE_NEXT_CLOSED_SOURCES_ONE_HOUR_CPU_PREPARED_ACTUAL.json').read_bytes());put('PARTIAL_H1_READER_FIX_V2_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,exclusive_finite_all_transport_only_while_actual_alive=True));pw=getpass.getpass('72 continue only unused H1 reader fix (hidden): ');c=None;cfg=None
 try:
  c=a.connect72(pw);spec=p['specs']['h1'];root=p['roots']['h1'];local=Path(p['payloads']['h1']);put('H1_FAILED_V1_PARTIAL_NO_NODE_NO_GO_ACTUAL_RECHECK_V2.json',a.code(c,a.PY,CHECK,root,prior['specs']['h1']['manifest_SHA'],json.dumps([spec['private_lock'],'/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock']),timeout=60))
  sf=c.open_sftp()
  try:
   sf.put(str(local/'closed_production_continuation_CPU_v2.py'),root+'/closed_production_continuation_CPU_v2.py');sf.put(str(local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
  finally:sf.close()
  put('H1_NEW_SOURCE_TARGET_FULL_INSTALLED_RSL_SDK_CPU_PORTABLE_V2_ACTUAL.json',a.code(c,a.PY,d.old.pre.old.CPU,root,timeout=240));put('H1_NEW_SOURCE_ACTUAL_REWARD_MIGRATION_CPU_PORTABLE_V2.json',a.code(c,a.PY,"from pathlib import Path;import sys,json;B=Path(sys.argv[1]);sys.path.insert(0,str(B));from closed_production_continuation_CPU_v2 import load;print(json.dumps(load(json.loads(sys.argv[2]),B)))",root,json.dumps(spec),timeout=180));d.upload(c,a.PY,'recovery',p)
 finally:
  if c:c.close();c=None
 try:
  c=a.t.connect();d.upload(c,a.t.PY,'e2',p);put('PREVIOUS_THREE_HOUR_ACTUAL_ACCOUNT_OUT_REAL_LOCKS_HANDOFF.json',a.code(c,a.t.PY,d.OWNER,d.SOURCE,timeout=90));sf=c.open_sftp()
  try:
   for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','owner_listener_ready_cpu_reviewed_v1.py'):sf.put(str(B/'controllers'/n),d.SOURCE+'/'+n)
  finally:sf.close()
  cfg=dict(role='owner',experts=p['specs'],run_id='SCUT_FUDAN_THREE_HOUR_'+str(time.time_ns()),token=secrets.token_hex(32));owner=d.old.launch(a.code,c,a.t.PY,d.SOURCE,'three_slot_finite_owner_v1.py',cfg);put('THREE_NEXT_HOUR_ONE_ORIGINAL_OWNER_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner));put('THREE_NEXT_HOUR_ORIGINAL_LISTENER_READY_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json;B=Path(sys.argv[1]);sys.path.insert(0,str(B));from owner_listener_ready_cpu_reviewed_v1 import wait_actual;print(json.dumps(wait_actual(B,int(sys.argv[2]),20.)))",d.SOURCE,str(owner['detached_pid']),timeout=45));nodes={'e2':d.old.launch(a.code,c,a.t.PY,p['roots']['e2'],'three_slot_finite_node_v1.py',dict(p['specs']['e2'],role='node',run_id=cfg['run_id'],token=cfg['token']))};put('E2_NEXT_HOUR_NODE_DETACHED_ACTUAL.json',dict(epoch=time.time(),node=nodes['e2']))
 finally:
  if c:c.close();c=None
 try:
  c=a.connect72(pw);pw=None
  for k in ('h1','recovery'):nodes[k]=d.old.launch(a.code,c,a.PY,p['roots'][k],'three_slot_finite_node_v1.py',dict(p['specs'][k],role='node',run_id=cfg['run_id'],token=cfg['token']))
  put('THREE_NEXT_HOUR_CLOSED_SOURCE_LEARNING_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,nodes=nodes,source_root=d.SOURCE,roots=p['roots'],specs=p['specs'],H1_reward_migration_SCUT_Fudan=True,first_deployer_no_node_or_GO_actual_rechecked=True,one_original_writer_independent_intervals_once=True,all_GO_save3600_lifecycle3900_exit300=True,no_total_budget_PPO_LR_STD_physics_threshold_change=True,reward_change_H1_only=True,not_actual_learning_claim_before_GO=True));print(json.dumps(dict(owner=owner,nodes=nodes,next_three_reward_hour_chain_detached=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('PARTIAL_H1_READER_FIX_V2_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_partial_no_repeat=True));raise
