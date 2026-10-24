from pathlib import Path
import importlib.util,json,sys,time,traceback
M=Path(__file__).resolve().parent;T=M.parent;W=T.parent;R=M/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
CODE=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,subprocess,time,stat
q=v['q'];key=v['key'];root=Path(q['roots'][key]);owner=Path(q['owner_root'])
assert json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
roots=[root]+([owner] if key=='h1' else [])
assert not any(p.pid!=os.getpid() and any(any(a.startswith(str(r)+'/') for r in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
locks=[Path(q['specs'][key]['private_lock'])]
if key=='h1':
 C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9 and c['remaining_training_seconds']==v['remaining']
 assert json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'];locks+=[C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]
else:locks.append(Path('/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'))
for p in locks:
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
rows=[]
for row in v['files']:
 p=Path(row['path']);assert p.parent==Path('/mnt/mod4_linux_durable_20261013/H1step270_reward_airfeasible5_2510v67/h1/job0/production/control_prefix_raw') and not p.is_symlink()
 st=p.stat();assert stat.S_ISREG(st.st_mode) and st.st_size==row['bytes']
 rows.append(dict(row,mtime_ns=st.st_mtime_ns,inode=st.st_ino,nlink=st.st_nlink,allocated_bytes=st.st_blocks*512))
free=shutil.disk_usage(root).free
print(json.dumps(dict(epoch=time.time(),files=rows,source_free=free,old_benchmark_actual_allout_locks_free=True,canonical_remaining=c['remaining_training_seconds'],no_PT_read_hash_transfer_delete_or_budget_write=True)))
'''
try:
 q=json.loads((R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json').read_bytes());proof=json.loads((R/'BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert proof['owner_node_workers_all_actual_out'] and proof['original_canonical_cost_settled']
 put('PREUPDATE_RELOCATION_PERMISSION_METADATA_STARTED_ACTUAL.json',dict(epoch=time.time(),only_after_benchmark_actual_closed=True,reason='Metadata-only inventory of own failed benchmark cache to resolve original disk25 guard; no protected model/raw/log/source reads'))
 s=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(s);s.loader.exec_module(memory);secret=memory.recover()
 c=d.t.connect()
 try:a=d.code(c,d.t.PY,CODE,dict(q=q,key='h1',remaining=proof['original_remaining_closed_snapshot'],files=json.loads((R/'PROPOSED_CLOSED67_PREUPDATE_SOURCE_ROWS_NO_PERMISSION_YET.json').read_bytes())['candidate_files']),timeout=60)
 finally:c.close()
 put('CLOSED67_PREUPDATE_PERMISSION_SOURCE_STAT_ACTUAL.json',a)
 c=d.connect72(secret);secret=None
 try:b=d.code(c,d.PY72,"from pathlib import Path;import json,shutil,time; p=Path('/home/lc01/Zonglin Li/zonglin2/forensic_originals'); print(json.dumps(dict(epoch=time.time(),target_parent=str(p),free_bytes=shutil.disk_usage(p).free,no_target_created=True)))",{},timeout=30)
 finally:c.close()
 put('CLOSED67_PREUPDATE_PERMISSION_TARGET_CAPACITY_ACTUAL.json',b)
 cache=json.loads((R/'OWN_FAILED_BENCHMARK_CACHE_METADATA_210_ACTUAL.json').read_bytes());selected=sorted(a['files'],key=lambda r:(r['bytes'],r['path']))[:2];payload=json.loads((R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());mp=Path(payload['payloads']['h1'])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';payload_bytes=sum(r['bytes'] for r in json.loads(mp.read_bytes())['files']);selected_bytes=sum(r['bytes'] for r in selected);cache_allocated=sum(r['allocated_bytes'] for r in cache['files'] if r['regular'] and r['nlink']==1 and not r['symlink']);minimum_plan=a['source_free']+cache_allocated+selected_bytes-payload_bytes-16*1024**2
 assert minimum_plan>25*1024**3 and b['free_bytes']-selected_bytes>25*1024**3
 put('REVIEWABLE_MINIMAL_SPACE_PLAN_REQUIRES_NEW_PT_SCOPE_PERMISSION_ACTUAL.json',dict(epoch=time.time(),classification='PROPOSAL_ONLY_NOT_AUTHORIZED_OR_EXECUTED',selected_preupdate_files=selected,selected_bytes=selected_bytes,own_failed_benchmark_cache_allocated_bytes=cache_allocated,original_disk25=25*1024**3,fresh_source_free=a['source_free'],known_payload_bytes=payload_bytes,copy_planning_margin_only_bytes=16*1024**2,projected_source_after_copy_margin=minimum_plan,target_capacity=b,proposed_target='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_BENCHMARK_AFTER67_PREUPDATE_AUTH_PENDING',must_full_SHA_and_signed_ack_before_only_true_duplicate_release=True,FINAL_latest_source_and_sole_original_preserved=True,why_permission='Human prior scope allowed NPZ relocation and explicitly excluded unapproved PT cleanup; these two preupdate PTs require new scope permission',not_new_training_gate_or_budget_change=True,no_transfer_delete_controller_or_new_GO=True))
 print(json.dumps(dict(proposal_only=True,selected=[Path(r['path']).name for r in selected],selected_bytes=selected_bytes,own_cache_allocated=cache_allocated,projected_source_after_copy_margin=minimum_plan,needs_explicit_PT_scope_permission=True)))
except BaseException:
 put('PREUPDATE_PERMISSION_PLAN_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc()));raise
