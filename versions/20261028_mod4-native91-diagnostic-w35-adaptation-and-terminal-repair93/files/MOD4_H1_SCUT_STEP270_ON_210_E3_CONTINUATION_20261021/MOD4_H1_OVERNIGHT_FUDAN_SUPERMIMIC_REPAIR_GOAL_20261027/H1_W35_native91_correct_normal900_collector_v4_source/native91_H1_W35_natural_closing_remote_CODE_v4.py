"""Exact two-slot natural FINAL collection: signed nominalend-now<=900, no control writes."""
CODE=r"""from pathlib import Path
import json,time,hashlib,fcntl,psutil,base64,zlib
hjob=Path(v['h1_job']);wjob=Path(v['w35_job']);owner=Path(v['owner_root']);hn=Path(v['h1_node_root']);wn=Path(v['w35_node_root']);hout=hjob/'job0/production';wout=wjob/'adaptation'
read=lambda p:json.loads(p.read_bytes())
go={'h1':read(hjob/'job0/GO_PRODUCTION.json'),'w35':read(wjob/'GO_PRODUCTION.json')}
assert go==v['go'] and max(g['nominal_end_epoch'] for g in go.values())-time.time()<=900,'original remote normal900 = nominalend-now<=900'
def own_out(row):
 try:
  p=psutil.Process(row['pid']);create=p.create_time()
  if create!=row['creation']:return dict(pid=row['pid'],out_PID_recycled_no_foreign_identity_read=True)
  if p.status()==psutil.STATUS_ZOMBIE:return dict(pid=row['pid'],original_nonexecuting_zombie=True)
  return None
 except psutil.NoSuchProcess:return dict(pid=row['pid'],original_out=True)
known_owner=[v['actual']['owner']]
known_nodes=[v['actual']['nodes']['h1'],v['actual']['nodes']['w35'],v['h1_worker']]
wstamp=read(wjob/'production_STARTED_ACTUAL.json');known_nodes.append(wstamp)
begin=time.time()
while True:
 ready=all((owner/x).is_file() for x in ('COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json')) and all(own_out(x) for x in known_owner)
 if ready:break
 assert time.time()-begin<850,'original owner850 bound';time.sleep(2)
start=time.time()
while not all((n/'NODE_EXIT_ACTUAL.json').is_file() for n in (hn,wn)) or not all(own_out(x) for x in known_nodes):
 assert time.time()-start<180,'original node180 bound';time.sleep(2)
cohort=read(owner/'COHORT_FINAL.json');exit=read(owner/'OWNER_EXIT_ACTUAL.json');term={k:read(n/'NODE_TERMINAL_ACTUAL.json')['row'] for k,n in [('h1',hn),('w35',wn)]};nexit={k:read(n/'NODE_EXIT_ACTUAL.json') for k,n in [('h1',hn),('w35',wn)]}
assert cohort['original_cost_settled'] and exit['original_cost_settled'] and set(cohort['scheduled_experts'])=={'h1','w35'}
assert all(nexit[k]['actual_all_own_children_waited'] and term[k]['terminal_all_own_children_waited'] for k in term)
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None
segments=[s for s in c['completed_segments'] if s['owner_parent_pid']==go['h1']['original_owner_pid'] and set(s['experts'])=={'h1','w35'} and all(s['experts'][k]['started_epoch']==go[k]['learning_started_epoch'] for k in go)]
assert len(segments)==1;segment=segments[0]
assert all(segment['experts'][k]['duration_bound_passed'] and segment['experts'][k]['charged_seconds']<=3900 for k in go)
assert segment['charged_expert_seconds']==sum(segment['experts'][k]['charged_seconds'] for k in go) # Original raw values, original slot order; no rounding/tolerance.
assert segment['experts']['w35']['charged_seconds']==488.166357755661
for p in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',C.parent.parent/'three_expert_v2_GPU-16828f91-2b45-b646-8dc0-9481138e2842.lock',C.parent.parent/'finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts=[];seen=set();total=0;paths=[]
for prefix,base,node,job,out in [('h1_slot',hjob.parent,hn,hjob,hout),('w35_slot',wjob.parent,wn,wjob,wout)]:
 dirs=[node,out]+([owner] if prefix=='h1_slot' else [])
 paths += [(prefix,base,p) for d in dirs for p in d.rglob('*') if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.log','.txt')]
 paths += [(prefix,base,p) for d in [job]+([job/'job0'] if (job/'job0').is_dir() else []) for p in d.iterdir() if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.log','.txt')]
for prefix,base,p in paths:
 rel=prefix+'/'+p.relative_to(base).as_posix()
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
formal=read(hout/'FINAL.json') if (hout/'FINAL.json').is_file() else None;published=None
if formal and formal.get('passed') and not term['h1'].get('original_error') and not term['h1'].get('errors') and term['h1']['returncode']==0:
 row=formal['final'];p=Path(row['path']);assert p.resolve().is_relative_to(hout.resolve()) and p.is_file() and not p.is_symlink()
 a=p.stat();assert a.st_size==row['bytes']
 with p.open('rb') as f:SHA=hashlib.file_digest(f,'sha256').hexdigest()
 b=p.stat();assert SHA==row['SHA'] and (a.st_size,a.st_mtime_ns)==(b.st_size,b.st_mtime_ns)
 published=dict(path=str(p),bytes=a.st_size,SHA=SHA,original_producer=row,source_stat_unchanged=True)
# W35 rawrc0 is explicitly a failed startup: retain errors and never require/publish its formal.
assert term['w35'].get('original_error') and term['w35'].get('errors') and not term['w35'].get('final') and not (wout/'FINAL.json').exists()
assert C.read_bytes()==raw
print(json.dumps(dict(actual_finite_returned=True,cohort=cohort,owner_exit=exit,node_exits=nexit,terminals=term,unique_original_segment=segment,original_fee_seconds=segment['charged_expert_seconds'],original_fee_by_slot={k:x['charged_seconds'] for k,x in segment['experts'].items()},closing_remaining_snapshot=c['remaining_training_seconds'],canonical_None=True,original_owner_private_shared_locks_free=True,own_processes=[own_out(x) for x in known_owner+known_nodes],texts=texts,text_bytes=total,H1_formal=formal,published=published,W35_failed_rawrc0_not_success=True,no_GPU_or_account_write=True,H1_NEW_formal_CPU_still_required=True)))
"""
