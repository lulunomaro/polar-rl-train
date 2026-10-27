"""Missing-only recovery of actual221 Windows text case collision.

Original collector/errors/partial files stay intact. New formal models have never
been transferred/decoded. No training, model forward, raw array or budget writes.
"""
from pathlib import Path,PurePosixPath
import json,sys,time,hashlib,traceback,collections,shutil,importlib.util,base64
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
ORIGINAL=R/'NATIVE88_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json'
EXPECTED={'h1':('a9bf6dca376e9d570ef0a6e2c15604f38656c4ebfedaa829a34830ee57c73aaf',256227465),'recovery':('0885f3cfc4413c7a65b4f50448df6cbcdb7427152b4f3a95e47185ecd5e2b2a0',256227465)}
def H(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
REMOTE_GUARD=r'''from pathlib import Path
import hashlib,json,psutil,fcntl
B=Path(v['root']);key=v['key'];q=v['q'];assert B==Path(q['roots'][key])
assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==q['specs'][key]['manifest_SHA']
for r in v['owned']:
 try:p=psutil.Process(r['pid']);assert p.create_time()!=r['creation'],'original own process still alive'
 except psutil.NoSuchProcess:pass
node=json.loads((B/'NODE_TERMINAL_ACTUAL.json').read_bytes());e=json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes());commit=json.loads((B/'job0/production/FINAL.json').read_bytes())
assert node==v['node_terminal'] and e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired']
assert node['row']['terminal_all_own_children_waited'] and node['row']['original_error'] is False and node['row']['returncode']==0 and not node['row']['errors']
assert commit==node['row']['final'] and commit['passed'] and commit['primary_error'] is None and not commit['secondary_errors']
assert commit['final']['SHA']==v['final']['SHA'] and commit['final']['bytes']==v['final']['bytes']
p=Path(v['final']['path']);assert p.is_relative_to(B/'job0/production') and p.name=='native_supermimic_H1_final.pt' and p.is_file() and not p.is_symlink();s=p.stat();assert s.st_size==v['final']['bytes']
paths=[Path(q['specs'][key]['private_lock'])]
if key=='recovery':
 P=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026');c=json.loads((P/'TRAINING_BUDGET_10H.json').read_bytes())
 assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['remaining_training_seconds']==562175.5721518993
 paths.extend([P/'native_floor_supervisor.lock',P/'autonomy_controller.lock',Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock')])
for path in paths:
 with path.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
print(json.dumps(dict(actual_own_processes_out=True,original_locks_free=True,source_formal_FINAL_original_fullSHA_published=True,source_stat=dict(path=str(p),device=s.st_dev,inode=s.st_ino,bytes=s.st_size,mtime_ns=s.st_mtime_ns),no_source_model_rehash_decode_or_GPU_or_budget_write=True)))'''
REMOTE_POSTSTAT=r'''from pathlib import Path
import json
p=Path(v['path']);s=p.stat();now=dict(path=str(p),device=s.st_dev,inode=s.st_ino,bytes=s.st_size,mtime_ns=s.st_mtime_ns);assert now==v['before'],'formal source changed during first transfer';print(json.dumps(now))'''
REMOTE_FRESH_LOG=r'''from pathlib import Path
import base64,hashlib,json
p=Path(v['path']);a=p.stat();raw=p.read_bytes();b=p.stat();assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns);print(json.dumps(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),mtime_ns=b.st_mtime_ns,base64=base64.b64encode(raw).decode())))'''
def matches(p,row):return p.is_file() and p.stat().st_size==row['bytes'] and H(p)==row['SHA']
def text_capture(c,sf,d,py,receipt,key):
 rows=receipt['text_files'];groups=collections.defaultdict(list)
 for row in rows:groups[row['relative'].casefold()].append(row)
 pairs={k:v for k,v in groups.items() if len(v)>1}
 assert len(pairs)==1 and {x['relative'].split('/')[-1] for v in pairs.values() for x in v}=={'NATIVE88_SOURCE_CPU_STARTED_ACTUAL.json','native88_SOURCE_CPU_STARTED_ACTUAL.json'}
 result=[];transferred=0;reused=0;copied_local=0
 for row in rows:
  rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts and rel.parts[0]==key
  assert PurePosixPath(row['path']).is_relative_to(PurePosixPath(receipt['node_terminal']['row']['final']['final']['path']).parents[2])
  assert rel.suffix in ('.py','.json','.jsonl','.log','.txt','.md','.sh','.yaml','.yml','.toml','.csv')
  canonical=N/'current_native88_closed_text'/Path(*rel.parts)
  assert canonical.resolve().is_relative_to(N.resolve()) and not canonical.is_symlink(),'local text containment'
  if rel.as_posix().casefold() in pairs:
   path=N/'current_native88_case_collision_text'/Path(*rel.parts[:-1])/(rel.name+'.'+row['SHA'][:16]+'.case_preserved.json')
  else:path=canonical
  if matches(path,row):result.append(dict(row,local_path=str(path),existing_verified_local_text_reused=True));reused+=1;continue
  assert not path.exists() or path==canonical,'new case-safe destination collision'
  path.parent.mkdir(parents=True,exist_ok=True)
  if path!=canonical and matches(canonical,row):
   assert not path.exists();shutil.copy2(canonical,path);copied_local+=1
   result.append(dict(row,local_path=str(path),case_preserved_original_relative=row['relative'],existing_verified_partial_text_local_copy=True));continue
  if path.exists():
   assert rel.as_posix()==key+'/job0/home/.nvidia-omniverse/logs/omni.processlifetime.log','unexpected existing text mismatch, original retained'
  part=path.with_name(path.name+'.missing_only_transfer.partial');assert not part.exists()
  sf.get(row['path'],str(part));transferred+=1
  if matches(part,row):
   assert not path.exists(),'matching transfer must not replace original existing text'
   part.replace(path);result.append(dict(row,local_path=str(path),missing_only_transferred=True));continue
  # The sole historical allowed mismatch remains scoped to this own log only.
  assert rel.as_posix()==key+'/job0/home/.nvidia-omniverse/logs/omni.processlifetime.log','unexpected new text mismatch; transferred bytes retained'
  report=R/('NATIVE88_'+key+'_PROCESSLIFETIME_LOG_MANIFEST_TRANSFER_AND_FRESH_SNAPSHOT_ACTUAL.json')
  assert not report.exists(),'one fresh own processlifetime snapshot only, no replay'
  original=dict(row,local_path=str(part),transferred_bytes=part.stat().st_size,transferred_SHA=H(part),manifest_time_bytes_not_captured=True)
  fresh=d.code(c,py,REMOTE_FRESH_LOG,dict(path=row['path']),timeout=45);raw=base64.b64decode(fresh.pop('base64'));assert len(raw)==fresh['bytes'] and hashlib.sha256(raw).hexdigest()==fresh['SHA']
  target=path.with_name('omni.processlifetime.fresh_after_manifest_mismatch.log');assert not target.exists()
  with target.open('xb') as f:f.write(raw)
  put(report.name,dict(epoch=time.time(),original=original,fresh=dict(fresh,local_path=str(target)),cause_unknown=True,original_manifest_time_bytes_unavailable=True,no_training_failure_or_refund_inferred=True))
  result.append(dict(row,bytes=fresh['bytes'],SHA=fresh['SHA'],local_path=str(target),original_manifest_and_transferred_log_preserved=original,one_fresh_snapshot_only=True))
 assert len(result)==len(rows)
 return result,dict(texts=len(result),transferred_missing=transferred,reused_verified=reused,local_verified_case_copies=copied_local,case_collision_groups=list(pairs))
def main():
 original=read(ORIGINAL);q=original['detached'];first=read(R/'NATIVE88_FIRST_NEW_POLICY_FINITE_RETURNED_ACTUAL.json')
 assert original['actual_finite_transport_returned'] and original['original_canonical_cost_settled'] and set(original['collection_errors'])=={'h1','recovery'}
 assert all('assert not path.exists()' in x for x in original['collection_errors'].values())
 assert all(not v for v in original['native_H1_method_fullstate'].values()) and not (R/'NATIVE88_INITIAL_CPU_ENTRY_CONSUMED_ACTUAL.json').exists()
 put('NATIVE88C_CASE_SAFE_MISSING_ONLY_TRANSFER_CONSUMED_ACTUAL.json',dict(epoch=time.time(),original_collector_report_SHA=H(ORIGINAL),classification='Windows local case-insensitive STARTED text collision; actual original training/formal save passed',no_original_report_or_partial_overwrite=True,formal_models_initial_transfer_only=True,no_model_decode_raw_GPU_or_account_write=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native88C_case_safe_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);secret=m.recover();c=None;all_texts=list(original['all_texts']);models={k:[] for k in ('h1','recovery')};errors={};audits={}
 try:
  for key in ('h1','recovery'):
   try:
    receipt=original['nodes'][key];final=receipt['node_terminal']['row']['final']['final'];assert (final['SHA'],final['bytes'])==EXPECTED[key]
    owned=[first['targets'][key][name]['actual'] for name in ('node_identity','worker_identity')]
    if key=='recovery':owned.append(q['owner_identity'])
    c=route.connect() if key=='h1' else d.connect72(secret);py=route.PY if key=='h1' else d.PY72
    audit=d.code(c,py,REMOTE_GUARD,dict(root=q['roots'][key],key=key,q=q,owned=owned,node_terminal=receipt['node_terminal'],final=final),timeout=60)
    put('NATIVE88C_'+key.upper()+'_MISSING_ONLY_FRESH_ORIGINAL_SOURCE_OUT_STAT_ACTUAL.json',audit)
    sf=c.open_sftp();sf.get_channel().settimeout(180)
    try:
     texts,textaudit=text_capture(c,sf,d,py,receipt,key);all_texts.extend(texts)
     dest=N/'current_native88_method_fullstate'/key/'formal/native_supermimic_H1_final.pt';part=dest.with_suffix('.pt.partial');dest.parent.mkdir(parents=True,exist_ok=True)
     assert not dest.exists() and not part.exists(),'no original formal-model transfer replay'
     sf.get(final['path'],str(part));assert part.stat().st_size==final['bytes'] and H(part)==final['SHA'],'full new native model SHA/bytes mismatch; partial retained'
     after=d.code(c,py,REMOTE_POSTSTAT,dict(path=final['path'],before=audit['source_stat']),timeout=45)
     part.replace(dest);models[key]=[dict(final,formal_manifest_passed=True,local_path=str(dest),twohost_complete_SHA=True,source_fullSHA_from_original_verified_publication=True,first_model_transfer_stat_before=audit['source_stat'],first_model_transfer_stat_after=after)]
     audits[key]=dict(source=audit,texts=textaudit,new_formal_first_transfer=True)
    finally:sf.close()
    put('NATIVE88C_'+key.upper()+'_CASE_SAFE_MISSING_TEXT_FORMAL_FIRST_TRANSFER_ACTUAL.json',dict(epoch=time.time(),passed=True,audit=audits[key],model=models[key][0]))
   except BaseException:
    errors[key]=traceback.format_exc();put('NATIVE88C_'+key.upper()+'_MISSING_ONLY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(original_error=errors[key],partial_and_other_healthy_role_retained=True,no_retry_or_model_reload=True))
   finally:
    if c:c.close();c=None
  result=dict(original,epoch=time.time(),all_active_node_collection_passed=not errors,all_texts=all_texts,native_H1_method_fullstate=models,collection_errors=errors,original_failed_collector_report_path=str(ORIGINAL),original_failed_collector_report_SHA=H(ORIGINAL),original_collection_errors_preserved=original['collection_errors'],case_safe_missing_only_transfer=True,missing_only_transfer_audits=audits,original_report_and_partial_files_retained=True,not_whole_CPU_or_skill_qualification=True)
  put('NATIVE88C_CASE_SAFE_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_V2_ACTUAL.json',result)
  print(json.dumps(dict(actual_finite_returned=True,case_safe_complete=not errors,formal_models={k:len(v) for k,v in models.items()},errors=list(errors),no_model_decode_or_training=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE88C_CASE_SAFE_ENTRY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(original_error=traceback.format_exc(),no_original_collector_replay=True));raise
