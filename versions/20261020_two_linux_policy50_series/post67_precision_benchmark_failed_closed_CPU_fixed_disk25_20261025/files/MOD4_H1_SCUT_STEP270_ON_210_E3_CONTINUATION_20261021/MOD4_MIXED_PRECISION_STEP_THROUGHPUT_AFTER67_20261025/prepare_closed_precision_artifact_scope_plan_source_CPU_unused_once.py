from pathlib import Path
import ast,json,time
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports';N=T/'MOD4_MIXED_PRECISION_PAIRED_RSL_V3_AFTER67_20261025'
rows=[];qs=[]
for stage in [M,N]:
 q=json.loads((stage/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());qs.append(q)
 payload=json.loads((stage/'reports/TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());manifest=json.loads((Path(payload['payloads']['h1'])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 for r in manifest['files']:
  if r['relative'] in ['job0/assets/robot.usd','job0/runtime/isaac/mod4/MOD4_RESET_COLLISION_BANK.npz','job0/source/'+q['specs']['h1']['source_filename']]:rows.append(dict(path=q['roots']['h1']+'/'+r['relative'],bytes=r['bytes'],SHA=r['SHA'],kind='closed_precision_test_input_copy'))
 base=stage/'benchmark_closed_text/h1/job0/production'
 for p in base.glob('*/MODE_COMPLETE_ACTUAL.json'):
  v=json.loads(p.read_bytes());r=v.get('artifact')
  if r:rows.append(dict(r,kind='closed_precision_benchmark_snapshot_not_training_FINAL'))
 for p in base.glob('*/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json'):
  for r in json.loads(p.read_bytes())['index']:
   rows.append(dict(path=r['path'],bytes=r['bytes'],SHA=r['SHA'],kind='closed_precision_saved_control_NPZ'))
   rows.append(dict(r['preupdate_source'],kind='closed_precision_preupdate_PT'))
with (R/'CLOSED_PRECISION_ONLY_ARTIFACT_CANDIDATES_PLAN_NOT_AUTHORIZED.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),rows=rows,only_exact_two_closed_test_roots_not_production67=True),f,indent=2)
a=(M/'read_own_failed_benchmark_cache_metadata_unused_once.py').read_text('utf8');a=a.replace("q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());proof=json.loads((R/'BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())","Q=M.parent/'MOD4_MIXED_PRECISION_PAIRED_RSL_V3_AFTER67_20261025/reports';q=json.loads((Q/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());proof=json.loads((Q/'BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes())")
a=a.replace('OWN_FAILED_BENCHMARK_CACHE_METADATA_READ_STARTED_ACTUAL.json','CLOSED_PRECISION_ONLY_ARTIFACT_PERMISSION_PLAN_STARTED_ACTUAL.json').replace('OWN_FAILED_BENCHMARK_CACHE_METADATA_210_ACTUAL.json','CLOSED_PRECISION_ONLY_ARTIFACT_FRESH_METADATA_210_ACTUAL.json')
needle="base=root/'job0';rows=[];dirs=[]";assert a.count(needle)==1
a=a.replace(needle,"base=root/'job0';rows=[];dirs=[];artifacts=[]\nfor r in v['candidates']:\n p=Path(r['path']);assert any(p.resolve().is_relative_to(Path(x).resolve()) for x in v['exact_closed_test_roots']) and not p.is_symlink()\n if not p.exists():continue\n st=p.stat();assert stat.S_ISREG(st.st_mode) and st.st_size==r['bytes'] and st.st_nlink==1;artifacts.append(dict(r,mtime_ns=st.st_mtime_ns,inode=st.st_ino))")
a=a.replace("directories=dirs,files=rows,logical_bytes=", "directories=dirs,files=rows,artifacts=artifacts,logical_bytes=")
a=a.replace("dict(q=q,key='h1',remaining=proof['original_remaining_closed_snapshot'])","dict(q=q,key='h1',remaining=proof['original_remaining_closed_snapshot'],candidates=json.loads((R/'CLOSED_PRECISION_ONLY_ARTIFACT_CANDIDATES_PLAN_NOT_AUTHORIZED.json').read_bytes())['rows'],exact_closed_test_roots=[x['roots']['h1'] for x in "+repr(qs)+"])")
s=a.index(' print(json.dumps(dict(own_failed_');a=a[:s]+''' c=d.connect72(secret);secret=None
 try:b=d.code(c,d.PY72,"import json,shutil,time;print(json.dumps(dict(epoch=time.time(),free=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2/forensic_originals').free)))",{},timeout=30)
 finally:c.close()
 import itertools
 payload=json.loads((Q/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());mp=Path(payload['payloads']['h1'])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';copy_bytes=sum(r['bytes'] for r in json.loads(mp.read_bytes())['files'])+16*1024**2;best=None
 for count in range(1,len(a['artifacts'])+1):
  valid=[combo for combo in itertools.combinations(a['artifacts'],count) if a['fresh_source_free']+a['allocated_bytes']+sum(r['bytes'] for r in combo)-copy_bytes>25*1024**3 and b['free']-sum(r['bytes'] for r in combo)>25*1024**3]
  if valid:best=min(valid,key=lambda combo:sum(r['bytes'] for r in combo));break
 selected=list(best or []);plan=dict(epoch=time.time(),classification='NEW_PERFORMANCE_ARTIFACT_SCOPE_PROPOSAL_ONLY',selected_files=selected,selected_bytes=sum(r['bytes'] for r in selected),fresh_source_free=a['fresh_source_free'],own_M3_cache_allocated_bytes=a['allocated_bytes'],own_M3_cache_files=a['files'],known_payload_plus16MiB_copy_planning_only=copy_bytes,source_after_copy_plan=a['fresh_source_free']+a['allocated_bytes']+sum(r['bytes'] for r in selected)-copy_bytes,target=b,exact_closed_performance_roots_only=True,production67_FINAL_and_original_source_not_in_scope=True,source_FULL_SHA_and_target_FULL_SHA_signedack_before_true_duplicate_release_required=True,min_file_count_then_min_bytes=True,scope_permission_not_yet_requested_or_received=True,no_hash_transfer_delete_controller_GO_or_budget_write=True,feasible=bool(selected))
 put('REVIEWABLE_CLOSED_PERFORMANCE_ARTIFACT_MINIMAL_TRANSFER_NEW_SCOPE_PLAN_ACTUAL.json',plan)
 print(json.dumps(dict(feasible=bool(selected),selected_count=len(selected),selected_bytes=plan['selected_bytes'],source_free=a['fresh_source_free'],cache_allocated=a['allocated_bytes'],projected_after_copy_plan=plan['source_after_copy_plan'],kinds={k:sum(r['kind']==k for r in selected) for k in {r['kind'] for r in selected}},no_actual_transfer=True)))
except BaseException:
 put('CLOSED_PRECISION_NEW_SCOPE_PLAN_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
'''
ast.parse(a)
with (M/'read_closed_precision_only_artifacts_for_new_scope_plan_unused_once.py').open('x',encoding='utf8') as f:f.write(a)
B=T/'H1_STEP270_REWARD_PATH_V1_20261022';w=(B/'same_authorized_session_compressed_transport_v61.py').read_text('utf8');needle="        'extract_latest67_retained_motion_CPU_unused_once.py',"
with (B/'same_authorized_session_compressed_transport_v62.py').open('x',encoding='utf8') as f:f.write(w.replace(needle,needle+"\n        'read_closed_precision_only_artifacts_for_new_scope_plan_unused_once.py',"))
print(json.dumps(dict(prepared_metadata_only=True,candidate_count=len(rows),no_new_permission_or_transfer=True)))
