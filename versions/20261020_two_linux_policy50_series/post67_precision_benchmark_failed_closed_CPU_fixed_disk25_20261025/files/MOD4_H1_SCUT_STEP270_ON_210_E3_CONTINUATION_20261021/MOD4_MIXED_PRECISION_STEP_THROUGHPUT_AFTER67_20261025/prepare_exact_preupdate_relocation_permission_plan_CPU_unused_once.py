from pathlib import Path
import ast,json,time
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports';N=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025'
index=json.loads((N/'current_pair_closed_text/h1/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes())
files=[r['preupdate_source'] for r in index['index'] if Path(r['path']).stem in ['control_prefix_0','control_prefix_116','control_prefix_117']]
with (R/'PROPOSED_CLOSED67_PREUPDATE_SOURCE_ROWS_NO_PERMISSION_YET.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),candidate_files=files,only_metadata_plan_not_transfer_or_delete=True),f,indent=2)
a=(M/'read_own_failed_benchmark_cache_metadata_unused_once.py').read_text('utf8');s=a.index("base=root/'job0';");e=a.index("'''",s)
a=a[:s]+'''rows=[]
for row in v['files']:
 p=Path(row['path']);assert p.parent==Path('/mnt/mod4_linux_durable_20261013/H1step270_reward_airfeasible5_2510v67/h1/job0/production/control_prefix_raw') and not p.is_symlink()
 st=p.stat();assert stat.S_ISREG(st.st_mode) and st.st_size==row['bytes']
 rows.append(dict(row,mtime_ns=st.st_mtime_ns,inode=st.st_ino,nlink=st.st_nlink,allocated_bytes=st.st_blocks*512))
free=shutil.disk_usage(root).free
print(json.dumps(dict(epoch=time.time(),files=rows,source_free=free,old_benchmark_actual_allout_locks_free=True,canonical_remaining=c['remaining_training_seconds'],no_PT_read_hash_transfer_delete_or_budget_write=True)))
'''+a[e:]
a=a.replace("remaining=proof['original_remaining_closed_snapshot'])","remaining=proof['original_remaining_closed_snapshot'],files=json.loads((R/'PROPOSED_CLOSED67_PREUPDATE_SOURCE_ROWS_NO_PERMISSION_YET.json').read_bytes())['candidate_files'])")
a=a.replace('OWN_FAILED_BENCHMARK_CACHE_METADATA_READ_STARTED_ACTUAL.json','PREUPDATE_RELOCATION_PERMISSION_METADATA_STARTED_ACTUAL.json').replace('OWN_FAILED_BENCHMARK_CACHE_METADATA_210_ACTUAL.json','CLOSED67_PREUPDATE_PERMISSION_SOURCE_STAT_ACTUAL.json')
s=a.index(' print(json.dumps(dict(own_failed_');a=a[:s]+''' c=d.connect72(secret);secret=None
 try:b=d.code(c,d.PY72,"from pathlib import Path;import json,shutil,time; p=Path('/home/lc01/Zonglin Li/zonglin2/forensic_originals'); print(json.dumps(dict(epoch=time.time(),target_parent=str(p),free_bytes=shutil.disk_usage(p).free,no_target_created=True)))",{},timeout=30)
 finally:c.close()
 put('CLOSED67_PREUPDATE_PERMISSION_TARGET_CAPACITY_ACTUAL.json',b)
 cache=json.loads((R/'OWN_FAILED_BENCHMARK_CACHE_METADATA_210_ACTUAL.json').read_bytes());selected=sorted(a['files'],key=lambda r:(r['bytes'],r['path']))[:2];payload=json.loads((R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());mp=Path(payload['payloads']['h1'])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';payload_bytes=sum(r['bytes'] for r in json.loads(mp.read_bytes())['files']);selected_bytes=sum(r['bytes'] for r in selected);cache_allocated=sum(r['allocated_bytes'] for r in cache['files'] if r['regular'] and r['nlink']==1 and not r['symlink']);minimum_plan=a['source_free']+cache_allocated+selected_bytes-payload_bytes-16*1024**2
 assert minimum_plan>25*1024**3 and b['free_bytes']-selected_bytes>25*1024**3
 put('REVIEWABLE_MINIMAL_SPACE_PLAN_REQUIRES_NEW_PT_SCOPE_PERMISSION_ACTUAL.json',dict(epoch=time.time(),classification='PROPOSAL_ONLY_NOT_AUTHORIZED_OR_EXECUTED',selected_preupdate_files=selected,selected_bytes=selected_bytes,own_failed_benchmark_cache_allocated_bytes=cache_allocated,original_disk25=25*1024**3,fresh_source_free=a['source_free'],known_payload_bytes=payload_bytes,copy_planning_margin_only_bytes=16*1024**2,projected_source_after_copy_margin=minimum_plan,target_capacity=b,proposed_target='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_BENCHMARK_AFTER67_PREUPDATE_AUTH_PENDING',must_full_SHA_and_signed_ack_before_only_true_duplicate_release=True,FINAL_latest_source_and_sole_original_preserved=True,why_permission='Human prior scope allowed NPZ relocation and explicitly excluded unapproved PT cleanup; these two preupdate PTs require new scope permission',not_new_training_gate_or_budget_change=True,no_transfer_delete_controller_or_new_GO=True))
 print(json.dumps(dict(proposal_only=True,selected=[Path(r['path']).name for r in selected],selected_bytes=selected_bytes,own_cache_allocated=cache_allocated,projected_source_after_copy_margin=minimum_plan,needs_explicit_PT_scope_permission=True)))
except BaseException:
 put('PREUPDATE_PERMISSION_PLAN_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
'''
ast.parse(a)
with (M/'read_exact_closed67_preupdate_metadata_for_permission_unused_once.py').open('x',encoding='utf8') as f:f.write(a)
B=T/'H1_STEP270_REWARD_PATH_V1_20261022';w=(B/'same_authorized_session_compressed_transport_v58.py').read_text('utf8');needle="        'read_own_failed_benchmark_missing_data_home_metadata_unused_once.py',";assert w.count(needle)==1
with (B/'same_authorized_session_compressed_transport_v59.py').open('x',encoding='utf8') as f:f.write(w.replace(needle,needle+"\n        'read_exact_closed67_preupdate_metadata_for_permission_unused_once.py',"))
print(json.dumps(dict(metadata_only_plan_prepared=True,no_transfer_delete_GO=True)))
