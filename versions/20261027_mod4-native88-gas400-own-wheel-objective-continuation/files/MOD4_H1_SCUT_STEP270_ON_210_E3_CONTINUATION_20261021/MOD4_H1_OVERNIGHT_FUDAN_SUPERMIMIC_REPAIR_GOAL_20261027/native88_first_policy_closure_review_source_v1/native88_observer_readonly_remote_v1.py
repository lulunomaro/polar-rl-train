"""UNUSED bounded owned-text observer. Prepend pure closing protocol remotely."""
def _small_owned(B,path,errors):
 import json
 try:
  if not path.is_file():return None
  require(not path.is_symlink() and path.resolve().is_relative_to(B.resolve()),'owned small text containment')
  require(path.suffix in ('.json','.jsonl','.log','.txt'),'no model/raw reads')
  if path.suffix=='.json':
   require(path.stat().st_size<8000000,'small JSON bound');return json.loads(path.read_bytes())
  size=path.stat().st_size
  with path.open('rb') as f:f.seek(max(0,size-120000));raw=f.read(120000)
  return dict(bytes=size,text_tail=raw.decode('utf8',errors='replace'),truncated=size>len(raw))
 except Exception as exc:
  value=dict(reader_error=type(exc).__name__+': '+str(exc));errors[str(path)]=value;return value

def _exact_recorded_identity(record):
 import psutil
 if not isinstance(record,dict) or type(record.get('pid')) is not int or not record.get('creation'):
  return dict(passed=False,status='missing_recorded_identity')
 try:
  p=psutil.Process(record['pid']);creation=p.create_time()
  if creation!=record['creation']:return dict(passed=False,status='recorded_process_out_PID_recycled',actual_out=True,no_foreign_exe_or_argv_queried=True)
  actual=dict(pid=p.pid,creation=creation,exe=p.exe(),argv=p.cmdline(),root=p.cwd())
  passed=all(actual[k]==record.get(k) for k in ('pid','creation','exe','argv','root'))
  return dict(passed=passed,status='exact_live_identity' if passed else 'exact_identity_mismatch',actual=actual,recorded=record)
 except psutil.NoSuchProcess:return dict(passed=False,status='actual_own_process_out',actual_out=True,recorded=record)

def observe_owner_readonly(v):
 from pathlib import Path
 import time,traceback,json
 q=v['q'];validate_detached(q);B=Path(q['owner_root']);errors={};files={};current=None;status='pending_actual_GO'
 def collect():
  for name in ('OWNER_CURRENT.json','OWNER_ORIGINAL_ERROR.json','OWNER_EXIT_ACTUAL.json','COHORT_FINAL.json','NO_GO_PARTIAL_REGISTRATION_EXPIRED_ACTUAL.json'):
   value=_small_owned(B,B/name,errors)
   if value is not None:files[name]=value
 try:
  while True:
   identity=_exact_recorded_identity(q['owner_identity']);collect();current=files.get('OWNER_CURRENT.json')
   if not identity['passed']:status='owner_out_or_identity_not_proven';break
   if files.get('OWNER_ORIGINAL_ERROR.json') is not None:status='actual_original_error';break
   if current and set(current.get('go',{}))==set(KEYS):validate_actual_GO_binding(current['go'],q);status='actual_two_GO';break
   if time.time()>=v['deadline_epoch']:status='actual_GO_not_proven_within1200';break
   time.sleep(min(3,max(.01,v['deadline_epoch']-time.time())))
  # Read only the canonical72 account. Never write or inspect old210 ledger.
  c=json.loads(Path(CANONICAL).read_bytes());require(c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026','sole72 generation')
  active=c['active_segment']
  if active is not None:require(active['owner_parent_pid']==q['owner_identity']['pid'],'actual own active account')
  return dict(epoch=time.time(),status=status,current=current,owner_identity=identity,owner_actual_out=identity.get('actual_out',False),existing_own_small_receipts=files,reader_errors=errors,canonical_active=active,remaining_actual_snapshot=c['remaining_training_seconds'],no_budget_write=True)
 except BaseException:
  collect();return dict(epoch=time.time(),status='owner_observation_primary_preserved',current=current,existing_own_small_receipts=files,reader_errors=errors,owner_observation_error=traceback.format_exc(),first_positive_not_proven=True,no_retry_or_budget_write=True)

def observe_target_readonly(v):
 from pathlib import Path
 import hashlib,json,sys,time,subprocess,traceback
 B=Path(v['root']);s=v['spec'];errors={};files={};out=B/'job0/production';immutable={};first=None;index=None;pre=None
 result=dict(key=s['key'],passed=False,passed_live_identity=False,status='pending_first_new_policy',first_metadata_read_count=0,no_PT_raw_or_checkpoint_hash_read=True,unknown_peer_identity_not_queried=True)
 def small(p):return _small_owned(B,p,errors)
 def cache(name,relative):
  if name not in immutable:
   value=small(out/relative)
   if value is not None:
    immutable[name]=value
    if name=='first_positive':result['first_metadata_read_count']+=1
  return immutable.get(name)
 def collect_primary():
  paths=[B/name for name in ('NODE_IDENTITY.json','NODE_CURRENT.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json','node_CONSOLE.log')]
  paths+=[B/'job0/GO_PRODUCTION.json',B/'job0/production_WORKER.log']
  paths+=list(B.glob('NODE_CONTROL_ORIGINAL_ERROR_*.json'))+list(B.glob('NODE_TERMINAL_HANDOFF_ORIGINAL_ERROR_*.json'))+list(out.glob('*ERROR*.json'))
  for p in dict.fromkeys(paths):
   value=small(p)
   if value is not None:files[p.relative_to(B).as_posix()]=value
 try:
  raw=(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes();require(hashlib.sha256(raw).hexdigest()==s['manifest_SHA'],'actual observer manifest')
  pins={r['relative']:r['SHA'] for r in json.loads(raw)['files']}
  for relative in ('native88_closed_source_CPU_v1.py','source/native_own_fudan88_gas400_training_v2.py','source/native_finalization_own88_gas400.py','source/native88_gas400_migration_v1.py'):
   require(hashlib.sha256((B/relative).read_bytes()).hexdigest()==pins[relative]==s['candidate_pins'][relative],'actual pinned native88 source '+relative)
  sys.path.insert(0,str(B));from native88_closed_source_CPU_v1 import expected_exec_identity
  def identity(record,logical):
   expected=expected_exec_identity(s,logical,B)
   if not isinstance(record,dict):return dict(passed=False,status='missing_recorded_identity',expected=expected)
   # Exact source recipe supplies exe when the old b.ident receipt omits it.
   normalized=dict(record);normalized.setdefault('exe',expected['exe'])
   require(normalized.get('argv')==expected['argv'] and normalized.get('root')==expected['root'] and normalized['exe']==expected['exe'],'recorded identity vs exact wrapper recipe')
   value=_exact_recorded_identity(normalized);value['expected']=expected;return value
  while True:
   collect_primary();node=files.get('NODE_IDENTITY.json');row=(files.get('NODE_CURRENT.json') or {}).get('row') or v.get('row') or {}
   require(node and node['pid']==v['detached_node']['detached_pid'],'actual deployed node PID bound')
   ni=identity(node,[s['python'],'-u','-B',str(B/'three_slot_finite_node_v1.py')])
   logical=[s['python'],'-u','-B',str(B/s['production_script']),'--slot',s['key'],'--phase','production','--num-envs','4096','--seed',str(s['seed']),'--source-scope','native_models_only_fresh400N_environment']
   wi=identity(row.get('worker'),logical);result.update(node_identity=ni,worker_identity=wi,row=row)
   first=cache('first_positive','FIRST_NATIVE_SUPERMIMIC_POLICY_UPDATE_POSITIVE_ACTUAL.json')
   pre=cache('actual_GPU_precontrol','NATIVE88_ACTUAL_GPU_PRECONTROL_ADMISSION.json')
   cache('objective','NATIVE_OWN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json');cache('preload','NATIVE88_FIRST_ORIGINAL_PRELOAD_PREWRITE_ACTUAL.json');cache('restore','NATIVE88_RESTORED_SOURCE_AND_CHANGED_PLANT_WINDOW_START_ACTUAL.json')
   if ni['passed'] and not wi['passed'] and wi.get('status')=='missing_recorded_identity' and not row.get('original_error') and 'NODE_EXIT_ACTUAL.json' not in files:
    result['status']='pending_worker_launch'
    if time.time()>=v['deadline_epoch']:result['bounded_wait_expired']=True;break
    time.sleep(min(3,max(.01,v['deadline_epoch']-time.time())));continue
   if not ni['passed'] or not wi['passed'] or row.get('original_error'):
    result['status']='own_process_out_error_or_identity_not_proven';break
   go=files.get('job0/GO_PRODUCTION.json');require(go==v['go'],'actual target GO text differs from owner')
   # FIRST is immutable and read once. Only the naturally published critical
   # index is reread while it catches the preceding publisher metadata.
   if first is not None:index=small(out/'control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json')
   result['status']=publication_index_status(first,index)
   if result['status']=='coherent':
    result['qualification']=validate_first_new_positive(first,index,pre,go,s)
    objective_raw=(out/'NATIVE_OWN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json').read_bytes()
    require(hashlib.sha256(objective_raw).hexdigest()==s['objective_contract_SHA'],'actual installed effective objective contract')
    pid=wi['actual']['pid'];query=['nvidia-smi','-i',s['GPU_UUID'],'--query-compute-apps=pid,gpu_uuid','--format=csv,noheader,nounits']
    lines=subprocess.check_output(query,text=True).splitlines();own=[x for x in lines if x.split(',')[0].strip()==str(pid)]
    require(own and all(x.split(',')[1].strip()==s['GPU_UUID'] for x in own),'selected UUID actual own worker compute proof')
    result.update(passed=True,passed_live_identity=True,status='coherent_first_new_policy',selected_GPU_query=query,own_GPU=own);break
   if time.time()>=v['deadline_epoch']:
    result.update(bounded_wait_expired=True,not_a_training_failure_classification=True);break
   time.sleep(min(3,max(.01,v['deadline_epoch']-time.time())))
 except BaseException:result.update(status='target_observation_primary_preserved',observation_error=traceback.format_exc())
 collect_primary();result.update(epoch=time.time(),first_positive=first,trace_index=index,actual_GPU_precontrol=pre,immutable_metadata=immutable,existing_own_small_receipts=files,reader_errors=errors,no_signal_or_retry=True,not_FINAL_or_skill_or_continuous_alive=True)
 return result
