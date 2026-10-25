"""New human-requested strict-pinned210 reconnection; current own text only."""
from pathlib import Path
import importlib.util,json,os,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE=r'''
from pathlib import Path
import errno,fcntl,json,os,psutil,time
q=v['q'];meta=v['metadata'];owner=Path(q['owner_root']);h1=Path(q['roots']['h1'])
assert str(owner)=='/mnt/mod4_linux_durable_20261013/H1step270_reward_sagtuck6a_2510v68/owner'
assert q['run_id']=='H1_STEP270_RECOVERY_ORIGINAL_1792908227707693100'
snapshots={}
for label,p in [('owner_identity',owner/'OWNER_IDENTITY.json'),('owner_current',owner/'OWNER_CURRENT.json'),('cohort_final',owner/'COHORT_FINAL.json'),('owner_exit',owner/'OWNER_EXIT_ACTUAL.json'),('H1_node_current',h1/'NODE_CURRENT.json'),('H1_node_terminal',h1/'NODE_TERMINAL_ACTUAL.json'),('H1_node_exit',h1/'NODE_EXIT_ACTUAL.json'),('H1_FINAL',h1/'job0/production/FINAL.json'),('H1_latest',h1/'job0/production/latest_complete.json')]:
 if p.is_file():snapshots[label]=dict(path=str(p),read_epoch=time.time(),value=json.loads(p.read_bytes()))
 else:snapshots[label]=dict(path=str(p),exists=False)
identities={}
for label,expected in [('owner',q['owner_identity']),('H1_node',meta['source210']['H1_node']),('H1_worker',meta['source210']['H1_worker'])]:
 row=dict(expected_pid=expected['pid'],expected_creation=expected['creation'],expected_own_identity_alive=False)
 try:
  p=psutil.Process(expected['pid'])
  if p.create_time()==expected['creation']:
   argv=p.cmdline();assert argv==expected['argv'];row.update(expected_own_identity_alive=True,actual_own_exe=p.exe(),actual_own_argv=argv)
 except psutil.Error:pass
 identities[label]=row
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes())
assert c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9
segments=[x for x in c['completed_segments'] if x.get('owner_parent_pid')==q['owner_identity']['pid'] and x.get('started_epoch',0)>=q['owner_identity']['creation']]
budget=dict(authorized_seconds=c['authorized_training_seconds'],extension_count=len(c['budget_extensions']),remaining_actual_snapshot=c['remaining_training_seconds'],charged_actual_snapshot=c['charged_training_seconds'],active_segment=c['active_segment'],current68_completed_original_segments=segments,no_canonical_copy_write_regrant_or_reconciliation=True)
locks=[]
if c['active_segment'] is None and not any(x['expected_own_identity_alive'] for x in identities.values()):
 for p in [C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(q['specs']['h1']['private_lock'])]:
  row=dict(path=str(p),free=False)
  with p.open('rb+') as f:
   try:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);row['free']=True
   except BlockingIOError:pass
  locks.append(row)
print(json.dumps(dict(epoch=time.time(),strict_pinned_connection_succeeded=True,run_id=q['run_id'],snapshots=snapshots,actual_own_process_identity_snapshot=identities,original_account_summary=budget,original_lock_snapshot=locks,no_GPU_PT_raw_native_query_mutation_or_training_stop=True,not_complete_model_CPU_or_skill_proof=True)))
'''
try:
 put('HUMAN_REQUESTED_CURRENT68_RECONNECT_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,human='继续尝试一下连接'))
 q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());meta=json.loads((R/'PAIR_ACTUAL_GO_POSITIVE_PPO_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json').read_bytes())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 c=d.t.connect()
 try:result=d.code(c,d.t.PY,CODE,dict(q=q,metadata=meta),timeout=45)
 finally:c.close()
 put('HUMAN_REQUESTED_CURRENT68_RECONNECT_RETURNED_ACTUAL.json',result)
 print(json.dumps(result))
except BaseException:
 put('HUMAN_REQUESTED_CURRENT68_RECONNECT_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_remote_mutation_or_new_writer=True));raise
