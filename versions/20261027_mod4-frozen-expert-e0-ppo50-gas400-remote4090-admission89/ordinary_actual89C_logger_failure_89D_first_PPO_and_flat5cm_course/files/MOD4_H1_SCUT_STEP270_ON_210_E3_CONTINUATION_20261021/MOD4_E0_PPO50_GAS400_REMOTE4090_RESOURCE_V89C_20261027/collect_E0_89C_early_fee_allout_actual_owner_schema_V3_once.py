"""Early-original-error forensic, not the normal FINAL900-gate collector."""
from pathlib import Path
import json,time,sys,importlib.util,traceback,base64,hashlib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
ROOT='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_PPO50_GAS400_2610v89c'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CODE='''from pathlib import Path
import json,time,psutil,fcntl,hashlib,base64
B=Path(v['root']);owner=B/'owner';node=B/'node_e0';job=B/'e0';out=job/'adaptation'
need=[owner/'COHORT_FINAL.json',owner/'OWNER_EXIT_ACTUAL.json',node/'NODE_EXIT_ACTUAL.json',node/'NODE_TERMINAL_ACTUAL.json']
start=time.time()
while not all(p.is_file() for p in need):
 assert time.time()-start<180,'original owner/node ending still pending; no mutation'
 time.sleep(2)
read=lambda p:json.loads(p.read_bytes());terminal=read(node/'NODE_TERMINAL_ACTUAL.json')['row'];assert terminal['terminal_all_own_children_waited'] and terminal['original_error']
assert read(node/'NODE_EXIT_ACTUAL.json')['actual_all_own_children_waited']
own=[]
for record in v['known_own']:
 try:
  p=psutil.Process(record['pid']);creation=p.create_time()
  if creation!=record['creation']:own.append(dict(pid=record['pid'],original_out_PID_recycled_no_foreign_identity_read=True));continue
  assert p.status()==psutil.STATUS_ZOMBIE,'known own original process still alive'
  own.append(dict(pid=record['pid'],original_creation=creation,original_nonexecuting_zombie=True))
 except psutil.NoSuchProcess:own.append(dict(pid=record['pid'],original_out=True))
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);assert c['active_segment'] is None
cohort=read(owner/'COHORT_FINAL.json');go=cohort['go']['e0'];assert go['run_id']==v['run_id'] and go['original_owner_pid']==v['known_own'][0]['pid'] and go['original_owner_creation']==v['known_own'][0]['creation']
segments=[s for s in c['completed_segments'] if s.get('owner_parent_pid')==go['original_owner_pid'] and (s.get('experts',{}).get('e0') or {}).get('started_epoch')==go['learning_started_epoch']];assert len(segments)==1;segment=segments[0];assert set(segment['experts'])=={'e0'}
assert segment['charged_expert_seconds']==segment['experts']['e0']['charged_seconds']
for path in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock',C.parent.parent/'three_expert_v2_GPU-c27eecbd-6838-7290-1cd2-37e34522213d.lock'):
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
texts=[];large=[];total=0
for root in (owner,node,job):
 for p in sorted(root.rglob('*')):
  if not p.is_file() or p.is_symlink() or '__pycache__' in p.parts:continue
  rel=p.relative_to(B).as_posix();st=p.stat()
  # Runtime/source was already fullSHA admitted/captured; here only ending/error
  # and saved startup receipts/console, never repeat source/model hashes.
  if rel.startswith(('e0/runtime/','e0/source/','e0/home/','e0/tmp/','e0/cache/','e0/config/','e0/data/')):continue
  if p.suffix.lower() not in ('.json','.log','.txt','.yaml','.yml'):
   if p.name.endswith(('.pt','.pt.partial')):large.append(dict(path=str(p),bytes=st.st_size,SHA=None,incomplete_unpublished_startup_save_no_producer_SHA=True))
   continue
  assert st.st_size<8000000
  data=p.read_bytes();after=p.stat();assert (st.st_size,st.st_mtime_ns)==(after.st_size,after.st_mtime_ns)
  data.decode('utf8');total+=len(data);assert total<32000000
  texts.append(dict(path=str(p),relative=rel,bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),base64=base64.b64encode(data).decode()))
assert C.read_bytes()==raw
print(json.dumps(dict(actual_early_error_ending_returned=True,original_error_not_skill_result=True,terminal=terminal,owner_cohort_final=read(owner/'COHORT_FINAL.json'),owner_exit=read(owner/'OWNER_EXIT_ACTUAL.json'),own_process_out_or_nonexecuting_zombie=own,canonical_None=True,C_SHA=hashlib.sha256(raw).hexdigest(),closed_remaining_snapshot=c['remaining_training_seconds'],unique_original_segment=segment,original_fee_seconds=segment['charged_expert_seconds'],all_original_locks_free=True,normal900_FINAL_collector_not_run_or_weakened=True,no_model_GPU_or_account_write=True,texts=texts,unpublished_incomplete_binaries=large)))
'''
def main():
 put('E0_89C_EARLY_FEE_READER_V3_REAL_OWNER_SCHEMA_CONSUMED_ACTUAL.json',dict(epoch=time.time(),purpose='Already observed real logger original error before firstPPO; wait original owner terminal and collect fee/text only',not_normal900_FINAL_collector=True))
 source=json.loads((R/'E0_FIRST_ACTUAL_4090_PPO_V4_FULLRESTORE_CLOCK_GAS400_RETURNED_ACTUAL.json').read_bytes());assert source['passed_first_PPO'] is False and source['original_errors']
 known=[dict(pid=x['pid'],creation=x['creation']) for x in source['snapshot']['known_own_processes']]
 request=json.loads((R/'E0_SINGLE72_PUBLIC_BOUND_LAUNCH_REQUEST_ACTUAL.json').read_bytes())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sp=importlib.util.spec_from_file_location('E0_early_ending_secret_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();c=None
 try:
  c=d.connect72(secret);secret=None;result=d.code(c,d.PY72,CODE,dict(root=ROOT,known_own=known,run_id=request['run_id']),timeout=210)
  target=N/'actual_89C_early_failure_text';target.mkdir();rows=[]
  for row in result.pop('texts'):
   raw=base64.b64decode(row.pop('base64'));assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['SHA']
   # Preserve all original logical paths via index; case-safe physical filenames.
   p=target/(hashlib.sha256(row['relative'].encode()).hexdigest()[:16]+'_'+Path(row['relative']).name)
   with p.open('xb') as f:f.write(raw)
   rows.append(dict(**row,local_path=str(p)))
  result['all_ending_original_text_files']=rows
  put('E0_89C_ORIGINAL_LOGGER_FAILURE_SETTLED_FEE_ALLOUT_V3_RETURNED_ACTUAL.json',result)
  print(json.dumps({k:result[k] for k in ('actual_early_error_ending_returned','original_fee_seconds','closed_remaining_snapshot','canonical_None','all_original_locks_free','unpublished_incomplete_binaries')}))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('E0_EARLY_FEE_ALLOUT_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc(),no_kill_or_refund_or_second_writer=True));raise
