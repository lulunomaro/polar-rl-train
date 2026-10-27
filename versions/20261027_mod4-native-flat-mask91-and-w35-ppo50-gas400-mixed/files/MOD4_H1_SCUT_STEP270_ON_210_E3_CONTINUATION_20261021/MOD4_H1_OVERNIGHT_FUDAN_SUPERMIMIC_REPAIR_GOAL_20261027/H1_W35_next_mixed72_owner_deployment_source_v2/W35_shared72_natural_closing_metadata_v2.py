"""Read-only natural shared-cohort closing and W35 formal-source producer metadata."""
from pathlib import Path
import json,time,hashlib,fcntl,psutil
from W35_first_real_GPU_PPO_metadata_observer_v2 import JOB,SOURCE,CPU,snapshot
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json')

def read(p):return json.loads(p.read_bytes()) if p.is_file() else None

def own_out(identity):
 assert identity.get('pid') and isinstance(identity.get('creation'),(int,float))
 try:
  p=psutil.Process(identity['pid'])
  if p.create_time()!=identity['creation']:return dict(out=True,reason='recorded PID reused; original own process out')
  status=p.status()
  return dict(out=status in (psutil.STATUS_ZOMBIE,psutil.STATUS_DEAD),own_identity_only=True,status=status,pid=p.pid,creation=p.create_time(),exe=p.exe() if status not in (psutil.STATUS_ZOMBIE,psutil.STATUS_DEAD) else None)
 except psutil.NoSuchProcess:return dict(out=True,reason='original owned PID absent')

def final_metadata(request):
 owner=Path(request['owner_root']);cohort=read(owner/'COHORT_FINAL.json');oe=read(owner/'OWNER_EXIT_ACTUAL.json')
 assert cohort and oe and cohort['original_cost_settled'] is True and oe['original_cost_settled'] is True
 assert set(cohort['scheduled_experts'])=={'h1','w35'} and set(cohort['go']).issubset({'h1','w35'})
 go=cohort['go'];g=go.get('w35')
 if g:assert g['run_id']==request['run_id'] and g['source_SHA']==SOURCE and g['source_CPU_SHA']==CPU
 nodes={}
 for key,spec in request['specs'].items():
  node=Path(request['node_roots'][key]);t=read(node/'NODE_TERMINAL_ACTUAL.json');e=read(node/'NODE_EXIT_ACTUAL.json');identity=read(node/'NODE_IDENTITY.json')
  assert t and e and t['row']['terminal_all_own_children_waited'] is True and e['actual_all_own_children_waited'] is True
  assert t['row']['manifest_SHA']==spec['manifest_SHA'] and t['row']['key']==key
  out=own_out(identity);assert out['out'];nodes[key]=dict(terminal=t,exit=e,owned_process_out=out)
 ownerid=read(owner/'OWNER_IDENTITY.json');out=own_out(ownerid);assert out['out']
 raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
 # Actual ledger schema has no promised top-level run_id. Bind original owner PID + each real GO start.
 candidates=[a for a in c['completed_segments'] if a.get('owner_parent_pid')==ownerid['pid'] and set(a.get('experts',{}))==set(go) and all(a['experts'][k]['started_epoch']==go[k]['learning_started_epoch'] for k in go)]
 if not go:
  assert not candidates
  return dict(passed=False,no_GO_by_either_registered_slot=True,no_model_load_or_promotion=True,no_segment_or_fee_invented=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),remaining=c['remaining_training_seconds'],nodes=nodes,owner_out=out)
 assert len(candidates)==1;segment=candidates[0]
 assert all(segment['experts'][k]['duration_bound_passed'] is True and segment['experts'][k]['charged_seconds']<=3900 for k in go)
 assert abs(segment['charged_expert_seconds']-sum(segment['experts'][k]['charged_seconds'] for k in go))<1e-5 # Same original ledger invariant tolerance.
 for lock in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock'):
  with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 for spec in request['specs'].values():
  with Path(spec['private_lock']).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 row=nodes['w35']['terminal']['row'];final=read(JOB/'adaptation/FINAL.json')
 if g is None or row.get('original_error') or row['returncode']!=0 or not final or not final.get('passed'):
  return dict(passed=False,original_error_or_partial=True,formal_model_not_loaded_or_promoted=True,original_segment=segment,canonical_SHA=hashlib.sha256(raw).hexdigest(),remaining=c['remaining_training_seconds'],nodes=nodes,owner_out=out)
 assert not row['errors'];r=final['final'];n=r['new_updates'];assert n>0 and r['Adam_step']==646800+20*n
 p=Path(r['path']).resolve();assert p.is_relative_to(JOB/'adaptation') and p.is_file() and p.stat().st_size==r['bytes']
 # Worker fullsave SHA reused; transport may hash a NEW copied output once. No reader here.
 return dict(passed=True,source_SHA=SOURCE,new_formal_producer=r,original_segment=segment,canonical_SHA=hashlib.sha256(raw).hexdigest(),remaining=c['remaining_training_seconds'],nodes=nodes,owner_out=out,original_locks_all_free=True,no_model_load_or_hash=True,not_skill_qualified=True,not_WM_dataset=True)

def watch(request,max_wait_seconds=780,emit=None):
 assert 0<max_wait_seconds<=780
 # Preserve the established900s admission to a normal closing observer.
 go=read(Path(request['owner_root'])/'OWNER_CURRENT.json')['go']
 if go:assert time.time()>=max(g['learning_started_epoch'] for g in go.values())+900
 deadline=time.time()+max_wait_seconds;last=0
 while True:
  owner=Path(request['owner_root']);cohort=read(owner/'COHORT_FINAL.json');exit=read(owner/'OWNER_EXIT_ACTUAL.json')
  if cohort and exit:
   try:return final_metadata(request)
   except (AssertionError,BlockingIOError):
    if time.time()>=deadline:raise
  if emit and time.time()-last>=25:emit(dict(stage='MIXED_NATURAL_CLOSING_WAIT',epoch=time.time(),W35=snapshot(request)));last=time.time()
  if time.time()>=deadline:return dict(passed=False,pending_natural_save_exit_terminal=True,no_STOP_kill_hotpatch_account_write_or_promotion=True)
  time.sleep(3)
