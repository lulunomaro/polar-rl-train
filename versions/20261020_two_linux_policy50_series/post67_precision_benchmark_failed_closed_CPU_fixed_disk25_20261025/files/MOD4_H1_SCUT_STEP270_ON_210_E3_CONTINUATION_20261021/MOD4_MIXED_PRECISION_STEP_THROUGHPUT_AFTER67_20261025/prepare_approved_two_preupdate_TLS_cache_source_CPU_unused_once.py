from pathlib import Path
import ast,hashlib,json,time
M=Path(__file__).resolve().parent;T=M.parent;R=M/'reports';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
plan=json.loads((R/'REVIEWABLE_MINIMAL_SPACE_PLAN_REQUIRES_NEW_PT_SCOPE_PERMISSION_ACTUAL.json').read_bytes());files=plan['selected_preupdate_files']
put('HUMAN_EXPLICIT_TWO_PREUPDATE_RELOCATION_AND_OWN_FAILED_CACHE_CLEANUP_APPROVAL_ACTUAL.json',dict(epoch=time.time(),approved=True,human_reply='批准这两份配套快照转存及本次缓存清理',question_scope=plan,selected_PT_paths=[r['path'] for r in files],no_other_PT_cache_FINAL_or_source_scope=True))
p=T/'forensic_tls_peer_transfer_V96_V5_NINTH.py';a=p.read_text('utf8')
allow={Path(r['path']).name:dict(path=r['path'],bytes=r['bytes'],SHA=r['SHA']) for r in files}
helper='''def exact_approved_rows(rows):
 expected=APPROVED_FILES
 actual={Path(r['path']).name:{k:r[k] for k in ('path','bytes','SHA')} for r in rows}
 assert len(rows)==len(actual)==2 and actual==expected

'''
b=a.replace('def receiver(cfg):',f'APPROVED_FILES={allow!r}\n\n'+helper+'def receiver(cfg):\n    exact_approved_rows(cfg[\'files\'])')
b=b.replace('def sender(cfg):','def sender(cfg):\n    exact_approved_rows(cfg[\'files\'])')
b=b.replace("re.fullmatch(r'control_prefix_\\d+\\.npz',name)","name in APPROVED_FILES").replace("re.fullmatch(r'control_prefix_\\d+\\.npz',p.name)","p.name in APPROVED_FILES")
b=b.replace('only_target_full_SHA_verified_NPZ_duplicates_removed=True,no_FINAL_model_source_text_or_error_touched=True','only_human_approved_two_preupdate_PT_duplicates_removed=True,no_FINAL_latest_source_text_or_error_touched=True')
ast.parse(b)
pn='forensic_tls_peer_transfer_APPROVED_TWO_PREUPDATE_AFTER67_V1.py'
with (M/pn).open('x',encoding='utf8') as f:f.write(b)
old=(M/'relocate_missing_current67_old30_after_closed67_TLS_V5_unused_once.py').read_text('utf8')
old=old.replace("T=Path(__file__).resolve().parent.parent;N=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025';W=T.parent;R=N/'reports';P=T/'forensic_tls_peer_transfer_V96_V5_NINTH.py'",f"M=Path(__file__).resolve().parent;T=M.parent;N=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025';W=T.parent;R=M/'reports';P=M/{pn!r}")
old=old.replace("ops.BOOT=ops.BOOT.replace('forensic_tls_peer_transfer_V96_V4.py','forensic_tls_peer_transfer_V96_V5_NINTH.py')",f"ops.BOOT=ops.BOOT.replace('forensic_tls_peer_transfer_V96_V4.py',{pn!r})")
s=old.index('INVENTORY=');e=old.index('\nREAD_SOURCE=',s)
inv=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,stat,shutil,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');canonical=C.read_bytes();c=json.loads(canonical)
assert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9 and c['remaining_training_seconds']==v['remaining']
roots=[Path(v['benchmark_owner_root']),Path(v['benchmark_h1_root']),Path(v['source_root'])]
assert json.loads((roots[0]/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
for root in roots[1:]:assert json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']
assert not any(p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for lock in [C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['private_lock'])]:
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
cache=[]
for row in v['cache_files']:
 p=Path(row['path']);assert p.resolve().is_relative_to(roots[1].resolve()) and not p.is_symlink();st=p.stat();assert stat.S_ISREG(st.st_mode) and (st.st_size,st.st_mtime_ns,st.st_ino,st.st_nlink)==(row['bytes'],row['mtime_ns'],row['inode'],1)
 assert any(p.resolve().is_relative_to(x.resolve()) for x in [roots[1]/'job0/cache',roots[1]/'job0/home/.nv/ComputeCache',roots[1]/'job0/tmp'])
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 cache.append(dict(row,SHA=h.hexdigest()))
selected=[]
for row in v['selected']:
 p=Path(row['path']);assert p.parent==roots[2]/'job0/production/control_prefix_raw' and not p.is_symlink();st=p.stat();assert stat.S_ISREG(st.st_mode) and st.st_size==row['bytes'] and st.st_nlink==1
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 assert h.hexdigest()==row['SHA'];selected.append(dict(row,mtime_ns=st.st_mtime_ns,inode=st.st_ino))
free=shutil.disk_usage(roots[2]).free;assert free+sum(r['allocated_bytes'] for r in cache)+sum(r['bytes'] for r in selected)-v['copy_planning_bytes']>25*1024**3
assert C.read_bytes()==canonical
print(json.dumps(dict(epoch=time.time(),files=selected,cache_files=cache,total_bytes=sum(r['bytes'] for r in selected),source_free=free,original_canonical_SHA=hashlib.sha256(canonical).hexdigest(),allout_original_locks_and_exact_narrow_approved_paths=True,no_cache_delete_yet=True)))
'''
old=old[:s]+'INVENTORY='+repr(inv)+'\n'+old[e:]
s=old.index(' proof=read(');e=old.index(' m=importlib.util',s)
old=old[:s]+''' approval=read(R/'HUMAN_EXPLICIT_TWO_PREUPDATE_RELOCATION_AND_OWN_FAILED_CACHE_CLEANUP_APPROVAL_ACTUAL.json');assert approval['approved'] and approval['human_reply']=='批准这两份配套快照转存及本次缓存清理'
 proof=read(R/'BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');assert proof['original_canonical_cost_settled'] and proof['owner_node_workers_all_actual_out']
 current=read(R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');oldq=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');src=dict(source_root=oldq['roots']['h1'],private_lock=oldq['specs']['h1']['private_lock'],stage=N.name);sources=[src]
 assert read(T/'reports/V96_V4_ACTUAL_TLS_HMAC_FULL_SHA_TRANSPORT_CPU_ACTUAL.json')['passed'];sha=H(P)
 cache=read(R/'OWN_FAILED_BENCHMARK_CACHE_METADATA_210_ACTUAL.json');selected=approval['question_scope']['selected_preupdate_files']
 put('APPROVED_TWO_PT_AND_OWN_CACHE_EXECUTION_STARTED_ACTUAL.json',dict(epoch=time.time(),protocol_SHA=sha,TLS_HMAC_implementation_reused_no_new_network_CPU=True,only_explicit_two_PT_and30_own_cache_files=True))
'''+old[e:]
old=old.replace("dict(sha_cache=cache['files'],sources=sources,current_owner_root=current['owner_root'],remaining=proof['remaining_actual_snapshot'],max_bytes=maximum,install_copy_planning_bytes=80253658)","dict(benchmark_owner_root=current['owner_root'],benchmark_h1_root=current['roots']['h1'],source_root=src['source_root'],private_lock=src['private_lock'],remaining=proof['original_remaining_closed_snapshot'],cache_files=cache['files'],selected=selected,copy_planning_bytes=approval['question_scope']['known_payload_bytes']+16*1024**2)")
s=old.index("  if inv['already_above_original_disk25']:");e=old.index('  for batch,src',s)
old=old[:s]+"  assert inv['total_bytes']<maximum and capacity['free']-inv['total_bytes']>25*1024**3\n"+old[e:]
old=old.replace("rows=[{k:v for k,v in row.items() if k!='batch'} for row in inv['files'] if row['batch']==batch]","rows=inv['files']")
old=old.replace("label=['CLOSED67_CURRENT67_MINIMAL','CLOSED67_OLD30_MINIMAL'][batch]","label='BENCHMARK_AFTER67_APPROVED_TWO_PREUPDATE'")
old=old.replace("proof['remaining_actual_snapshot']","proof['original_remaining_closed_snapshot']")
s=old.index("  assert complete;free=");e=old.index(' except BaseException:',s)
old=old[:s]+'''  assert complete;free=complete[-1]['source_free_after']
  c=d.t.connect()
  try:clean=d.code(c,d.t.PY,CLEAN_CACHE,dict(root=current['roots']['h1'],owner=current['owner_root'],files=inv['cache_files'],canonical_SHA=inv['original_canonical_SHA'],private_lock=src['private_lock']),timeout=90)
  finally:c.close();c=None
  put('ONLY_APPROVED_OWN_FAILED_BENCHMARK30_COMPILED_CACHE_CLEANUP_ACTUAL.json',clean)
  put('APPROVED_TWO_PREUPDATE_RETAINED_ON72_AND_OWN_CACHE_COMPLETE_ACTUAL.json',dict(epoch=time.time(),passed=True,batches=complete,cache_cleanup=clean,source_free_after=clean['source_free_after'],all_full_SHA_retained_on72=True,canonical_bytes_unchanged=True,all_own_storage_processes_actual_out=True,no_GPU_PPO_or_budget_writer=True))
  print(json.dumps(dict(files=sum(len(x['files']) for x in complete),cache_files=clean['removed_files'],source_free=clean['source_free_after'],above_original_disk25=clean['source_free_after']>25*1024**3)))
'''+old[e:]
cleanup=r'''
from pathlib import Path
import fcntl,hashlib,json,os,psutil,shutil,stat,time
B=Path(v['root']);owner=Path(v['owner']);C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
assert hashlib.sha256(C.read_bytes()).hexdigest()==v['canonical_SHA'] and json.loads(C.read_bytes())['active_segment'] is None
assert json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'] and json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
assert not any(p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in (B,owner)) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
locks=[]
for p in [C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['private_lock'])]:
 f=p.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
before=shutil.disk_usage(B).free;actions=[]
for row in v['files']:
 p=Path(row['path']);assert any(p.resolve().is_relative_to(x.resolve()) for x in [B/'job0/cache',B/'job0/home/.nv/ComputeCache',B/'job0/tmp']) and not p.is_symlink()
 st=p.stat();assert stat.S_ISREG(st.st_mode) and (st.st_size,st.st_mtime_ns,st.st_ino,st.st_nlink)==(row['bytes'],row['mtime_ns'],row['inode'],1)
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 assert h.hexdigest()==row['SHA'];p.unlink();actions.append(row)
assert hashlib.sha256(C.read_bytes()).hexdigest()==v['canonical_SHA']
print(json.dumps(dict(epoch=time.time(),removed_files=len(actions),actions=actions,source_free_before=before,source_free_after=shutil.disk_usage(B).free,only_explicit_own_failed_benchmark_regenerable_cache=True,no_model_raw_FINAL_source_error_log_touched=True,canonical_SHA_unchanged=True)))
for f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()
'''
old=old.replace('def main():','CLEAN_CACHE='+repr(cleanup)+'\n\ndef main():')
ast.parse(old)
with (M/'relocate_approved_two_preupdate_and_cleanup_own_benchmark_cache_unused_once.py').open('x',encoding='utf8') as f:f.write(old)
w=(B/'same_authorized_session_compressed_transport_v59.py').read_text('utf8');needle="        'read_exact_closed67_preupdate_metadata_for_permission_unused_once.py',"
with (B/'same_authorized_session_compressed_transport_v60.py').open('x',encoding='utf8') as f:f.write(w.replace(needle,needle+"\n        'relocate_approved_two_preupdate_and_cleanup_own_benchmark_cache_unused_once.py',"))
put('APPROVED_TWO_PREUPDATE_TLS_PROTOCOL_NARROW_SOURCE_CPU_ACTUAL.json',dict(epoch=time.time(),passed_AST=True,protocol_path=str(M/pn),SHA=hashlib.sha256(b.encode()).hexdigest(),exact_approved_two_files=allow,crypto_and_original_budget_lock_guard_reused=True,helper_AST=True,no_execution_yet=True))
print(json.dumps(dict(prepared=True,protocol=pn,wrapper='v60',no_transfer_yet=True)))
