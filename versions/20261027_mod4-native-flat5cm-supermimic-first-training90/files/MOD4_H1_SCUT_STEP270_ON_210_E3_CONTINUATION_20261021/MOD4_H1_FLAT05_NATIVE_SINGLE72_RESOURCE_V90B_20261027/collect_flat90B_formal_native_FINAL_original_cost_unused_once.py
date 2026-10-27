"""Normal once-only close. Original local+remote900, owner850 then node180."""
from pathlib import Path
import sys,time,json,hashlib,base64,zlib,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
CODE=r'''from pathlib import Path
import json,time,hashlib,fcntl,psutil,base64,zlib
root=Path('/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_H1_FLAT05_NATIVE_2610v90b');owner=root/'owner';node=root/'node_h1';job=root/'h1';out=job/'job0/production'
read=lambda p:json.loads(p.read_bytes())
g=read(job/'job0/GO_PRODUCTION.json');assert g==v['go'] and g['nominal_end_epoch']-time.time()<=900,'original remote900 gate'
begin=time.time()
def own_out(row):
 try:
  p=psutil.Process(row['pid']);create=p.create_time()
  if create!=row['creation']:return dict(pid=row['pid'],out_PID_recycled_no_foreign_identity_read=True)
  if p.status()==psutil.STATUS_ZOMBIE:return dict(pid=row['pid'],original_nonexecuting_zombie=True)
  return None
 except psutil.NoSuchProcess:return dict(pid=row['pid'],original_out=True)
while True:
 ready=all((owner/x).is_file() for x in ('COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json')) and all(own_out(x) for x in v['owner_known'])
 if ready:break
 assert time.time()-begin<850,'original owner850 bound';time.sleep(2)
start=time.time()
while not (node/'NODE_EXIT_ACTUAL.json').is_file() or not all(own_out(x) for x in v['node_known']):
 assert time.time()-start<180,'original node180 bound';time.sleep(2)
cohort=read(owner/'COHORT_FINAL.json');exit=read(owner/'OWNER_EXIT_ACTUAL.json');terminal=read(node/'NODE_TERMINAL_ACTUAL.json')['row'];node_exit=read(node/'NODE_EXIT_ACTUAL.json')
assert cohort['original_cost_settled'] and exit['original_cost_settled'] and node_exit['actual_all_own_children_waited'] and terminal['terminal_all_own_children_waited']
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None
segments=[s for s in c['completed_segments'] if s['owner_parent_pid']==g['original_owner_pid'] and s['experts']['h1']['started_epoch']==g['learning_started_epoch']];assert len(segments)==1 and set(segments[0]['experts'])=={'h1'}
for p in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock',C.parent.parent/'finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts=[];seen=set();total=0
paths=[p for d in (owner,node) for p in d.rglob('*') if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.log','.txt')]
paths += [p for d in (job,job/'job0') for p in d.iterdir() if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.log','.txt')]
paths += [p for p in out.rglob('*') if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.log','.txt')]
for p in paths:
 rel=p.relative_to(root).as_posix()
 if rel in seen:continue
 seen.add(rel);a=p.stat();assert a.st_size<=2*1024**3,'own text collection bound';data=p.read_bytes();b=p.stat();assert (a.st_size,a.st_mtime_ns)==(b.st_size,b.st_mtime_ns),'own text changed after allout '+rel
 total+=len(data);assert total<3*1024**3,'aggregate own text collection bound'
 texts.append(dict(relative=rel,bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),zlib_base64=base64.b64encode(zlib.compress(data,1)).decode()))
formal=read(out/'FINAL.json') if (out/'FINAL.json').is_file() else None;published=None
if formal and formal.get('passed') and not terminal.get('original_error') and not terminal.get('errors') and terminal['returncode']==0:
 row=formal['final'];p=Path(row['path']);assert p.resolve().is_relative_to(out.resolve()) and p.is_file() and not p.is_symlink()
 a=p.stat();assert a.st_size==row['bytes']
 with p.open('rb') as f:SHA=hashlib.file_digest(f,'sha256').hexdigest()
 b=p.stat();assert SHA==row['SHA'] and (a.st_size,a.st_mtime_ns)==(b.st_size,b.st_mtime_ns)
 published=dict(path=str(p),bytes=a.st_size,SHA=SHA,original_producer=row,source_stat_unchanged=True)
assert C.read_bytes()==raw
print(json.dumps(dict(actual_finite_returned=True,cohort=cohort,owner_exit=exit,node_exit=node_exit,terminal=terminal,unique_original_segment=segments[0],original_fee_seconds=segments[0]['charged_expert_seconds'],closing_remaining_snapshot=c['remaining_training_seconds'],canonical_None=True,original_owner_private_shared_locks_free=True,own_processes=[own_out(x) for x in v['owner_known']+v['node_known']],texts=texts,text_bytes=total,formal=formal,published=published,no_GPU_or_account_write=True,formal_model_CPU_still_required=True)))'''
def main():
 first=json.loads((R/'FLAT90_FIRST_ACTUAL_NATIVE_POLICY_RETURNED_ACTUAL.json').read_bytes());go=first['go'];assert go['nominal_end_epoch']-time.time()<=900,'original local900 gate earliest22:41:19.276166BJT'
 put('FLAT90B_NORMAL_CLOSING_CONSUMED_ACTUAL.json',dict(epoch=time.time(),local900=True,owner850_node180=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('flat90Bclose_secretmemory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None
  v=d.code(c,d.PY72,CODE,dict(go=go,owner_known=[first['owner']],node_known=[first['node'],first['worker']]),timeout=1140)
  target=N/'closed_actual_text';target.mkdir();rows=[]
  for row in v.pop('texts'):
   data=zlib.decompress(base64.b64decode(row.pop('zlib_base64')));assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['SHA']
   p=target/(hashlib.sha256(row['relative'].encode()).hexdigest()[:20]+'_'+Path(row['relative']).name)
   with p.open('xb') as f:f.write(data)
   rows.append(dict(**row,local_path=str(p)))
  v['all_original_texts_full_case_safe']=rows
  published=v['published']
  if published:
   p=N/'current_native_flat_method_fullstate/formal/native_supermimic_H1_final.pt';p.parent.mkdir(parents=True);sf=c.open_sftp();sf.get_channel().settimeout(180)
   try:a=sf.stat(published['path']);sf.get(published['path'],str(p));b=sf.stat(published['path'])
   finally:sf.close()
   assert a.st_size==b.st_size==published['bytes'] and a.st_mtime==b.st_mtime
   with p.open('rb') as f:SHA=hashlib.file_digest(f,'sha256').hexdigest()
   assert SHA==published['SHA'];published.update(local_path=str(p),twohost_complete_SHA=True)
  put('FLAT90B_COMPLETE_FINAL_OR_PARTIAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json',v)
  print(json.dumps(dict(actual_closed=True,formal_model_collected=bool(published),fee=v['original_fee_seconds'],closing=v['closing_remaining_snapshot'],initial_whole_CPU_still_required=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('FLAT90B_CLOSING_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_retry_kill_refund_or_second_writer=True));raise
