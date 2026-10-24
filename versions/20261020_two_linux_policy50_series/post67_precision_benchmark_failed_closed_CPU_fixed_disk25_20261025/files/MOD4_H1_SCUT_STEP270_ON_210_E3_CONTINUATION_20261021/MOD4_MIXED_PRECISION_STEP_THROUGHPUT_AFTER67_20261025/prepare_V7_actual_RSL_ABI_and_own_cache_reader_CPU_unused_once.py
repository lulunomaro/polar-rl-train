from pathlib import Path
import ast,hashlib,json,time
M=Path(__file__).resolve().parent;R=M/'reports';T=M.parent
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
a=(M/'mixed_precision_step_benchmark_runtime_v6.py').read_text('utf8')
helper='''def actual_logger_timing(original_log,args,kwargs):
 bound=inspect.signature(original_log).bind(*args,**kwargs)
 return float(bound.arguments['collect_time']),float(bound.arguments['learn_time'])

'''
b=a.replace('class ExclusivePhaseTimers:',helper+'class ExclusivePhaseTimers:')
old="locs=aa[0] if aa and isinstance(aa[0],dict) else kk.get('locs');assert isinstance(locs,dict)"
assert b.count(old)==1
b=b.replace(old,'collect_time,learn_time=actual_logger_timing(original_log,aa,kk)').replace("float(locs['collection_time'])",'collect_time').replace("float(locs['learn_time'])",'learn_time')
assert 'locs' not in b
ast.parse(b)
with (M/'mixed_precision_step_benchmark_runtime_v7.py').open('x',encoding='utf8') as f:f.write(b)
checker=(M/'check_new_AMP_benchmark_V6_original_clock_only_source_CPU_unused_once.py').read_text('utf8').replace('runtime_v6.py','runtime_v7.py').replace('AMP_BENCHMARK_V6_SCALER','AMP_BENCHMARK_V7_SCALER')
with (M/'check_new_AMP_benchmark_V7_actual_clock_scaler_CPU_unused_once.py').open('x',encoding='utf8') as f:f.write(checker)
old=(M/'read_actual_RSL_logger_API_and_closed_benchmark_resources_unused_once.py').read_text('utf8')
start=old.index("runner=Path(v['runner']);")
end=old.index("'''",start)
new='''base=root/'job0';rows=[];dirs=[]
for p in [base/'cache',base/'home/.nv/ComputeCache',base/'tmp']:
 if not p.exists():dirs.append(dict(path=str(p),exists=False));continue
 assert not p.is_symlink() and p.resolve().is_relative_to(root.resolve())
 for parent,children,names in os.walk(p,followlinks=False):
  pp=Path(parent);children[:]=[n for n in children if not (pp/n).is_symlink()]
  for name in names:
   f=pp/name;s=f.lstat()
   rows.append(dict(path=str(f),bytes=s.st_size,allocated_bytes=s.st_blocks*512,mtime_ns=s.st_mtime_ns,inode=s.st_ino,nlink=s.st_nlink,symlink=f.is_symlink(),regular=stat.S_ISREG(s.st_mode)))
 dirs.append(dict(path=str(p),exists=True))
print(json.dumps(dict(epoch=time.time(),root=str(root),directories=dirs,files=rows,logical_bytes=sum(r['bytes'] for r in rows),allocated_bytes=sum(r['allocated_bytes'] for r in rows),fresh_source_free=shutil.disk_usage(root).free,old_benchmark_actual_allout_locks_free=True,canonical_SHA=hashlib.sha256(C.read_bytes()).hexdigest(),canonical_remaining=c['remaining_training_seconds'],metadata_only_no_hash_copy_delete_or_GPU=True)))
'''
old=old[:start]+new+old[end:]
old=old.replace('import fcntl,hashlib,json,os,psutil,shutil,subprocess,time','import fcntl,hashlib,json,os,psutil,shutil,subprocess,time,stat')
begin=old.index(" hs=json.loads(");end=old.index(" s=importlib.util",begin)
old=old[:begin]+old[end:]
old=old.replace('ACTUAL_RSL_LOGGER_SOURCE_AND_RESOURCE_READ_STARTED_ACTUAL.json','OWN_FAILED_BENCHMARK_CACHE_METADATA_READ_STARTED_ACTUAL.json')
old=old.replace("reason='Fix keyword Logger.log ABI and H1-vs-E3 callback counters before new unused GPU benchmark'","reason='Metadata-only inventory of own failed benchmark cache to resolve original disk25 guard; no protected model/raw/log/source reads'")
old=old.replace("dict(q=q,key='h1',runner=hpath,remaining=proof['original_remaining_closed_snapshot'])","dict(q=q,key='h1',remaining=proof['original_remaining_closed_snapshot'])")
end=old.index(" c=d.connect72(secret)")
old=old[:end]+" print(json.dumps(dict(own_failed_benchmark_cache_bytes=a['logical_bytes'],allocated_bytes=a['allocated_bytes'],source_free=a['fresh_source_free'])))\nexcept BaseException:\n put('OWN_BENCHMARK_CACHE_READER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_same_once=True));raise\n"
old=old.replace("put('ACTUAL_RSL_RUNNER_LOGGER_SOURCE_AND_RESOURCE_210_ACTUAL.json',a)","put('OWN_FAILED_BENCHMARK_CACHE_METADATA_210_ACTUAL.json',a)")
ast.parse(old)
with (M/'read_own_failed_benchmark_cache_metadata_unused_once.py').open('x',encoding='utf8') as f:f.write(old)
B=T/'H1_STEP270_REWARD_PATH_V1_20261022';w=(B/'same_authorized_session_compressed_transport_v56.py').read_text('utf8');needle="        'read_actual_RSL_logger_API_and_closed_benchmark_resources_unused_once.py',"
assert w.count(needle)==1;v=w.replace(needle,needle+"\n        'read_own_failed_benchmark_cache_metadata_unused_once.py',")
assert v.replace("\n        'read_own_failed_benchmark_cache_metadata_unused_once.py',",'')==w
with (B/'same_authorized_session_compressed_transport_v57.py').open('x',encoding='utf8') as f:f.write(v)
put('LOCAL_READ_PATH_AND_RG_GLOB_ORIGINAL_ERRORS_PRESERVED_ACTUAL.json',dict(epoch=time.time(),errors=[dict(classification='FileNotFoundError',path=str(B/'forensic_tls_peer_transfer_V96_V5_NINTH.py'),correction_actual_path=str(T/'forensic_tls_peer_transfer_V96_V5_NINTH.py')),dict(classification='rg os error123',argument='literal payloads/h1/run_h1*',correction='rg recursive directory and explicit file glob')],no_remote_or_budget_change=True))
put('V7_ACTUAL_RSL_LOGGER_ABI_AND_CACHE_READER_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),passed=True,runtime_SHA=hashlib.sha256(b.encode()).hexdigest(),original_V6_preserved=True,actual_RSL_log_collect_time_keyword_not_locs=True,CPU_actual_runner_integration_required_before_GO=True,cache_reader_metadata_only_exact_own_failed_root=True,no_cache_cleanup_or_transfer_authorized_by_reader=True,no_new_payload_Task_GO_or_fee=True))
print(json.dumps(dict(prepared_V7=True,cache_reader='read_own_failed_benchmark_cache_metadata_unused_once.py',wrapper='v57',no_GO=True)))
