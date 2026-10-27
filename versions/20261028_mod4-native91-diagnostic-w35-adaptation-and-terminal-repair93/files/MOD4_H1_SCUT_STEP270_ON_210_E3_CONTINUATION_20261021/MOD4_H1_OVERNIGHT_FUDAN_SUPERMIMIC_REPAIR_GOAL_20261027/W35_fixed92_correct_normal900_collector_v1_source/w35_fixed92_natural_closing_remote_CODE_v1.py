"""Read-only normal closure of the one real W35 fixed92 slot; never signal it."""
CODE=r'''from pathlib import Path
import json,time,hashlib,fcntl,psutil,base64,zlib
job=Path(v['job_root']);owner=Path(v['owner_root']);node=Path(v['node_root']);out=job/'adaptation'
read=lambda p:json.loads(p.read_bytes())
go=read(job/'GO_PRODUCTION.json')
assert go==v['go'] and go['nominal_end_epoch']-time.time()<=900,'original remote normal900: nominalend-now<=900'
assert go['run_id']==v['actual']['run_id'] and go['original_owner_pid']==v['actual']['owner']['pid']
assert go['max_parent_seconds']==3900 and go['save_deadline']==go['learning_started_epoch']+3600 and go['nominal_end_epoch']==go['learning_started_epoch']+3900
def own_out(row):
 try:
  p=psutil.Process(row['pid']);create=p.create_time()
  if create!=row['creation']:return dict(pid=row['pid'],out_PID_recycled_no_foreign_identity_read=True)
  if p.status()==psutil.STATUS_ZOMBIE:return dict(pid=row['pid'],original_nonexecuting_zombie=True)
  return None
 except psutil.NoSuchProcess:return dict(pid=row['pid'],original_out=True)
worker=read(job/'production_STARTED_ACTUAL.json');known_owner=[v['actual']['owner']];known_nodes=[v['actual']['node'],worker]
begin=time.time()
while not (all((owner/x).is_file() for x in ('COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json')) and all(own_out(x) for x in known_owner)):
 assert time.time()-begin<850,'original owner850 bound';time.sleep(2)
begin=time.time()
while not (node/'NODE_EXIT_ACTUAL.json').is_file() or not all(own_out(x) for x in known_nodes):
 assert time.time()-begin<180,'original node180 bound';time.sleep(2)
cohort=read(owner/'COHORT_FINAL.json');exit=read(owner/'OWNER_EXIT_ACTUAL.json');term=read(node/'NODE_TERMINAL_ACTUAL.json')['row'];nexit=read(node/'NODE_EXIT_ACTUAL.json')
assert cohort['original_cost_settled'] and exit['original_cost_settled'] and set(cohort['scheduled_experts'])=={'w35'}
assert nexit['actual_all_own_children_waited'] and term['terminal_all_own_children_waited']
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None
segments=[s for s in c['completed_segments'] if s['owner_parent_pid']==go['original_owner_pid'] and set(s['experts'])=={'w35'} and s['experts']['w35']['started_epoch']==go['learning_started_epoch']]
assert len(segments)==1;segment=segments[0];slot=segment['experts']['w35']
assert slot['duration_bound_passed'] and slot['charged_seconds']<=3900
assert segment['charged_expert_seconds']==sum(segment['experts'][k]['charged_seconds'] for k in ('w35',))
for p in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock',C.parent.parent/'finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts=[];seen=set();total=0;base=job.parent;paths=[]
paths += [p for d in (owner,node,out) for p in d.rglob('*') if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.log','.txt')]
paths += [p for p in job.iterdir() if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.log','.txt')]
for p in paths:
 rel='w35_slot/'+p.relative_to(base).as_posix()
 if rel in seen:continue
 seen.add(rel);a=p.stat();assert a.st_size<=2*1024**3,'original own text bound';data=p.read_bytes();b=p.stat()
 if (a.st_size,a.st_mtime_ns)!=(b.st_size,b.st_mtime_ns):
  assert p.name=='omni.processlifetime.log' and p.resolve().is_relative_to(base.resolve()),'own text changed after allout '+rel
  # Historical exact-owned-log exception only: retain the first mismatch and its already-read original bytes.
  total+=len(data);assert total<3*1024**3,'original aggregate own text bound'
  texts.append(dict(relative=rel+'.ORIGINAL_CHANGED_READ_RETAINED',original_relative=rel,snapshot_role='original_stat_mismatch_retained',before_stat=dict(bytes=a.st_size,mtime_ns=a.st_mtime_ns),after_stat=dict(bytes=b.st_size,mtime_ns=b.st_mtime_ns),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),zlib_base64=base64.b64encode(zlib.compress(data,1)).decode()))
  a=p.stat();assert a.st_size<=2*1024**3,'original own text bound';data=p.read_bytes();b=p.stat()
  if (a.st_size,a.st_mtime_ns)!=(b.st_size,b.st_mtime_ns):
   print(json.dumps(dict(exact_owned_log_fresh_snapshot_still_changed=True,texts=texts,no_formal_promotion=True)))
   raise AssertionError('one authorized fresh snapshot still changed '+rel)
 total+=len(data);assert total<3*1024**3,'original aggregate own text bound'
 texts.append(dict(relative=rel,bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),zlib_base64=base64.b64encode(zlib.compress(data,1)).decode()))
formal=read(out/'FINAL.json') if (out/'FINAL.json').is_file() else None;published=None
if formal and formal.get('passed') and not term.get('original_error') and not term.get('errors') and term['returncode']==0:
 assert formal['source_SHA']==go['source_SHA'] and not formal['new_branch_skill_qualified']
 row=formal['final'];assert row['new_updates']>0 and row['Adam_step']==646800+20*row['new_updates'] and row['not_skill_qualified']
 p=Path(row['path']);assert p.resolve().is_relative_to(out.resolve()) and p.is_file() and not p.is_symlink()
 a=p.stat();assert a.st_size==row['bytes']
 with p.open('rb') as f:SHA=hashlib.file_digest(f,'sha256').hexdigest()
 b=p.stat();assert SHA==row['SHA'] and (a.st_size,a.st_mtime_ns)==(b.st_size,b.st_mtime_ns)
 published=dict(path=str(p),bytes=a.st_size,SHA=SHA,original_producer=row,source_stat_unchanged=True)
assert C.read_bytes()==raw
print(json.dumps(dict(actual_finite_returned=True,cohort=cohort,owner_exit=exit,node_exit=nexit,terminal=term,unique_original_segment=segment,original_fee_seconds=segment['charged_expert_seconds'],original_fee_by_slot={'w35':slot['charged_seconds']},closing_remaining_snapshot=c['remaining_training_seconds'],canonical_None=True,original_owner_private_shared_locks_free=True,own_processes=[own_out(x) for x in known_owner+known_nodes],texts=texts,text_bytes=total,W35_formal=formal,published=published,no_GPU_or_account_write=True,only_NEW_formal_CPU_still_required=bool(published),skill_regression_and_WM_transition_data_not_completed=True)))
'''
