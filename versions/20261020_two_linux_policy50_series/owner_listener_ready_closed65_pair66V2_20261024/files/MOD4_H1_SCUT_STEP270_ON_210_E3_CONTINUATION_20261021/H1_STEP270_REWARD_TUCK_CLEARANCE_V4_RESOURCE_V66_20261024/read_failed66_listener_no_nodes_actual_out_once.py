from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
read=lambda p:json.loads(p.read_bytes())
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
SOURCE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,time
q=v['q'];owner=Path(q['owner_root']);h1=Path(q['roots']['h1']);until=time.monotonic()+180
def own():
 rows=[]
 for p in psutil.process_iter(['pid','cmdline','create_time','exe']):
  try:
   if p.pid!=os.getpid() and any(a.startswith((str(owner)+'/',str(h1)+'/')) for a in p.info['cmdline'] or []):rows.append(p.info)
  except psutil.Error:pass
 return rows
initial=own()
while own():
 assert time.monotonic()<until,'Owner has not actually returned; do not assume out or launch replacement'
 time.sleep(2)
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9 and c['remaining_training_seconds']==v['remaining'] and hashlib.sha256(raw).hexdigest()==v['canonical_SHA']
locks=[]
for lock in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(q['specs']['h1']['private_lock'])):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(lock))
current=json.loads((owner/'OWNER_CURRENT.json').read_bytes());exit=json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes());expired=json.loads((owner/'NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json').read_bytes())
assert current['go']=={} and current['rows']=={} and not current['original_canonical_active'] and not current['original_two_fcntl_held'] and exit['original_cost_settled'] and expired['observed']==[]
assert not (h1/'job0/production').exists() and not (h1/'NODE_IDENTITY.json').exists()
texts={}
for key,root in (('owner',owner),('h1',h1)):
 for p in root.rglob('*'):
  if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.jsonl','.log','.txt','.yaml','.yml','.sh','.md','.toml','.csv'):texts[key+'/'+p.relative_to(root).as_posix()]=p.read_text('utf8',errors='strict')
assert C.read_bytes()==raw
print(json.dumps(dict(epoch=time.time(),initial_own_process_snapshot=initial,all_owner_H1_processes_actual_out=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),canonical_unchanged_no_new_segment_or_charge=True,remaining_snapshot=c['remaining_training_seconds'],original_locks_actual_free=locks,current=current,owner_exit=exit,expired=expired,no_actual_GO_or_fee=True,no_H1_node_identity=(not (h1/'NODE_IDENTITY.json').exists()),no_H1_worker_or_model=True,texts=texts)))
'''
TARGET=r'''
from pathlib import Path
import fcntl,json,os,psutil,time
q=v['q'];root=Path(q['roots']['recovery']);rows=[]
for p in psutil.process_iter(['pid','cmdline','create_time','exe']):
 try:
  if p.pid!=os.getpid() and any(a.startswith(str(root)+'/') for a in p.info['cmdline'] or []):rows.append(p.info)
 except psutil.Error:pass
assert not rows;locks=[]
for lock in (Path(q['specs']['recovery']['private_lock']),Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(lock))
texts={p.relative_to(root).as_posix():p.read_text('utf8',errors='strict') for p in root.rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts and p.suffix in ('.py','.json','.jsonl','.log','.txt','.yaml','.yml','.sh','.md','.toml','.csv')}
assert not (root/'NODE_IDENTITY.json').exists()
print(json.dumps(dict(epoch=time.time(),all_E3_processes_actual_out=True,no_node_identity=True,private_shared_locks_actual_free=locks,texts=texts)))
'''
try:
 q=read(R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');proof=read(T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V65_20261024/reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');cap=read(T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V65_20261024/reports/PEER_FORENSICS_FRESH_SOURCE_ACTUAL.json')
 put('FAILED66_LISTENER_READONLY_PROBE_STARTED_ACTUAL.json',dict(epoch=time.time(),finite_wait_own_owner_only=True,no_signal_or_retry_or_budget_write=True))
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);secret=m.recover();c=d.t.connect()
 try:a=d.code(c,d.t.PY,SOURCE,dict(q=q,remaining=proof['remaining_actual_snapshot'],canonical_SHA=cap['canonical_SHA']),timeout=210)
 finally:c.close()
 put('FAILED66_LISTENER_SOURCE_OWNER_NO_GO_ALL_OUT_ACTUAL.json',a);c=d.connect72(secret);secret=None
 try:b=d.code(c,d.PY72,TARGET,dict(q=q),timeout=60)
 finally:c.close()
 put('FAILED66_LISTENER_TARGET_NO_NODE_ALL_OUT_ACTUAL.json',b)
 put('FAILED66_LISTENER_NO_NODES_NO_GO_TWOHOST_ALL_OUT_ACTUAL.json',dict(epoch=time.time(),passed=True,source_owner_and_H1_actual_out=a['all_owner_H1_processes_actual_out'],target_E3_actual_out=b['all_E3_processes_actual_out'],canonical_SHA=a['canonical_SHA'],no_actual_GO_or_fee=True,canonical_unchanged_no_new_segment_or_charge=True,owner_no_registration_expired=a['expired'],original_error_preserved=True,no_same_root_retry_or_hotpatch_or_signal=True))
 print(json.dumps(dict(passed=True,both_hosts_actual_out=True,no_actual_GO_or_fee=True,canonical_unchanged=True)))
except BaseException:
 put('FAILED66_LISTENER_PROBE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),do_not_assume_out=True));raise
