from pathlib import Path
import ast,base64,hashlib,importlib.util,json,sys,time,traceback,zlib
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports';C=L/'TWO106_FUDAN270_20S_ACTUAL_CPU_BOUND_ORIGINAL_OWNER_SOURCE_V1'
CODE=r'''from pathlib import Path
import json,time,psutil,fcntl,hashlib,base64,zlib
read=lambda p:json.loads(Path(p).read_bytes())
owner=Path(v['public']['owner_root']);specs=v['public']['experts'];go=v['first']['go'];assert set(go)=={'h1','h1_seed28'} and all(v['first']['results'][k]['errors'] for k in go)
def out(row):
 try:
  p=psutil.Process(row['pid'])
  if p.create_time()!=row['creation']:return True
  return p.status()==psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return True
known=[x['exact_identity'] for x in v['actual']['identities'].values()]
begin=time.time()
while not all((owner/n).is_file() for n in ['COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json']) or not all(out(x) for x in known):
 assert time.time()-begin<850;time.sleep(2)
cohort=read(owner/'COHORT_FINAL.json');ending=read(owner/'OWNER_EXIT_ACTUAL.json');assert cohort['original_cost_settled'] and ending['original_cost_settled'] and cohort['go']==go
nodes={};workers=[]
for key,s in specs.items():
 node=Path(v['public']['node_roots'][key]);ex=read(node/'NODE_EXIT_ACTUAL.json');term=cohort['rows'][key];assert ex['actual_all_own_children_waited'] and term['terminal_all_own_children_waited'] and term['original_error']
 assert not (term.get('final') or {}).get('passed',False);nodes[key]=ex;workers.append(read(Path(s['job_root'])/'production_STARTED_ACTUAL.json'))
assert all(out(x) for x in known+workers)
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();account=read(C);assert account['active_segment'] is None and account['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'
segments=[s for s in account['completed_segments'] if s['owner_parent_pid']==go['h1']['original_owner_pid'] and set(s['experts'])==set(go) and all(s['experts'][k]['started_epoch']==go[k]['learning_started_epoch'] for k in go)];assert len(segments)==1;seg=segments[0]
assert seg['charged_expert_seconds']==sum(seg['experts'][k]['charged_seconds'] for k in go)
for key in go:assert seg['experts'][key]['duration_bound_passed'] and 0<seg['experts'][key]['charged_seconds']<=3900
for p in [C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock',C.parent.parent/'finite_environment_validation.lock',*[Path(s['private_lock']) for s in specs.values()]]:
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
paths=set(p for root in [owner,*[Path(x) for x in v['public']['node_roots'].values()]] for p in root.rglob('*') if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.log','.txt'))
partials=[]
for s in specs.values():
 job=Path(s['job_root']);paths.update(p for p in (job/'job0/production').rglob('*') if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.log','.txt'))
 paths.update(p for base in [job,job/'job0'] for p in base.iterdir() if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.log','.txt'))
 for p in (job/'job0/production').rglob('*.partial'):
  if p.is_file() and ('.pt' in p.name or '.native_' in p.name):partials.append(dict(path=str(p),bytes=p.stat().st_size,SHA=None,no_content_read=True,original_retained=True))
texts=[];total=0
for p in sorted(paths):
 a=p.stat();assert a.st_size<2*1024**3;data=p.read_bytes();b=p.stat();assert (a.st_size,a.st_mtime_ns)==(b.st_size,b.st_mtime_ns),'own text still changed '+str(p);data.decode('utf8');total+=len(data);assert total<3*1024**3
 texts.append(dict(path=str(p),bytes=len(data),SHA=hashlib.sha256(data).hexdigest(),zlib_base64=base64.b64encode(zlib.compress(data,1)).decode()))
assert C.read_bytes()==raw
print(json.dumps(dict(actual_finite_returned=True,early_failure_original_owner_exit_not_normal900_closing=True,cohort=cohort,owner_exit=ending,node_exits=nodes,unique_original_segment=seg,original_fee_by_slot={k:seg['experts'][k]['charged_seconds'] for k in go},original_fee_seconds=seg['charged_expert_seconds'],closing_remaining_snapshot=account['remaining_training_seconds'],canonical_None=True,all_original_own_processes_out=True,original_private_shared_locks_free=True,texts=texts,partial_binary_index=partials,no_model_read_transfer_GPU_or_account_write=True)))'''
ast.parse(CODE)
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def main():
 public=json.loads((C/'reports/TWO106_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());actual=json.loads((C/'reports/TWO106_ACTUAL_OWNER_AND_TWO_NODES_DETACHED.json').read_bytes());first=json.loads((L/'TWO106_FUDAN270_20S_FIRST_CLOSING_INITIAL_CPU_SOURCE_V1/reports/TWO106_ALL_FIRST_POLICY_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json').read_bytes())
 assert all(not x['passed_first_NEW_native_policy'] and x.get('errors') for x in first['results'].values());put('ACTUAL106_EARLY_FAILURE_ORIGINAL_COLLECTION_CONSUMED_ACTUAL.json',dict(epoch=time.time(),run_id=public['run_id'],only_original_natural_exit_fee_and_errors=True))
 m=module('compressed100_failure_definitions',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');transport,previous=m.install();sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sec=module('authorized100_failure_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=None
 try:
  client=d.connect72(secret);secret=None;value=d.code(client,d.PY72,CODE,dict(public=public,actual=actual,first=first),timeout=1140);folder=N/'complete_original106_failure_texts';folder.mkdir();rows=[]
  for x in value.pop('texts'):
   data=zlib.decompress(base64.b64decode(x.pop('zlib_base64')));assert len(data)==x['bytes'] and hashlib.sha256(data).hexdigest()==x['SHA'];p=folder/(hashlib.sha256(x['path'].encode()).hexdigest()[:20]+'_'+Path(x['path']).name)
   with p.open('xb') as f:f.write(data)
   rows.append(dict(**x,local_path=str(p)))
  value['full_original_texts']=rows;put('ACTUAL106_ORIGINAL_EARLY_FAILURE_ALL_COST_ALLOUT_FULLTEXTS_RETURNED_ACTUAL.json',value);print(json.dumps(dict(actual_returned=True,original_fee_by_slot=value['original_fee_by_slot'],original_fee_seconds=value['original_fee_seconds'],closing=value['closing_remaining_snapshot'],no_new_policy_or_formal=True)))
 finally:
  secret=None
  if client:client.close()
  transport.SESSION=previous
if __name__=='__main__':
 try:main()
 except BaseException:put('ACTUAL106_FAILURE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_retry_or_account_mutation=True));raise
