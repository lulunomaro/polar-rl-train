from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports';B=T/'H1_STEP270_REWARD_PATH_V1_20261022';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V41_20261023'
old=T/'H1_STEP270_REWARD_AIRBORNE_TUCK_V3_RESOURCE_V39_20261023/relocate_missing_closed32_after_closed39_TLS_TUCK_V3_once.py'
text=old.read_text('utf8');start=text.index('INVENTORY=r');end=text.index('\nREAD_SOURCE=',start)
inventory=r'''
from pathlib import Path
import fcntl,hashlib,itertools,json,os,psutil,re,shutil,time
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');canonical=C.read_bytes();c=json.loads(canonical)
assert c['active_segment'] is None and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8 and c['remaining_training_seconds']==v['remaining']
owners=[Path(v['current_owner_root'])]+[Path(x['owner_root']) for x in v['sources']]
for owner in owners:assert json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
roots=owners+[Path(x['source_root']) for x in v['sources']]
assert not any(p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for lock in [C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]+[Path(x['private_lock']) for x in v['sources']]:
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
free=shutil.disk_usage(v['sources'][0]['source_root']).free;available=[]
if free<=25*1024**3:
 for batch,src in enumerate(v['sources']):
  old=Path(src['source_root']);assert json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'];base=old/'job0/production/control_prefix_raw'
  for row in json.loads((base/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes())['index']:
   p=Path(row['path'])
   if not p.exists():continue
   assert p.resolve().is_relative_to(base.resolve()) and not p.is_symlink() and re.fullmatch(r'control_prefix_\d+\.npz',p.name)
   s=p.stat();assert s.st_size==row['bytes'] and s.st_nlink==1
   available.append(dict(path=str(p),bytes=s.st_size,SHA=row['SHA'],mtime_ns=s.st_mtime_ns,inode=s.st_ino,batch=batch))
best=None
for count in range(1,len(available)+1):
 for combo in itertools.combinations(available,count):
  total=sum(x['bytes'] for x in combo)
  if free+total>25*1024**3 and total<=v['max_bytes'] and (best is None or total<sum(x['bytes'] for x in best)):best=combo
 if best is not None:break
selected=list(best or [])
for row in selected:
 h=hashlib.sha256()
 with Path(row['path']).open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 assert h.hexdigest()==row['SHA']
assert C.read_bytes()==canonical
print(json.dumps(dict(epoch=time.time(),files=selected,total_bytes=sum(x['bytes'] for x in selected),source_free=free,already_above_original_disk25=free>25*1024**3,source_plus_selected_above_original25=free+sum(x['bytes'] for x in selected)>25*1024**3,canonical_SHA=hashlib.sha256(canonical).hexdigest(),actual_allout_and_original_locks_free=True,minimum_file_count_then_minimum_total_bytes=True,unselected_stat_only_no_raw_hash=True)))
'''
text=text[:start]+'INVENTORY='+repr(inventory)+'\n'+text[end:]
start=text.index('def main():')
newmain=r'''
def main():
 proof=read(R/'H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json');current=read(R/'H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json')
 assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
 stages=[T/'H1_STEP270_REWARD_REPLAY_V2_RESOURCE_V36_20261023',T/'H1_STEP270_REWARD_BOUNDARY_RESOURCE_V28_20261023'];sources=[]
 for stage in stages:
  oldp=read(stage/'reports/PAIR_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');assert oldp['passed'] and oldp['all_owner_nodes_children_actual_out'] and oldp['original_canonical_cost_settled']
  oq=read(stage/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');sources.append(dict(source_root=oq['roots']['h1'],owner_root=oq['owner_root'],private_lock=oq['specs']['h1']['private_lock'],stage=stage.name))
 assert read(T/'reports/V96_V4_ACTUAL_TLS_HMAC_FULL_SHA_TRANSPORT_CPU_ACTUAL.json')['passed'];sha=H(P);assert sha=='31e6c729fad4c7e73e60843535f602f95ab0eec0b18f2cc24262d1167840dcd7'
 put('CLOSED41_OLD36_28_MINIMAL_HEADROOM_STARTED_ACTUAL.json',dict(epoch=time.time(),protocol_source_SHA=sha,reused_actual_TLS_HMAC_CPU_no_reexecution=True,current_H1_only_closed_CPU=True,original_remaining_snapshot=proof['remaining_actual_snapshot'],combined_preflight_before_any_target_controller=True))
 m=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(m);m.loader.exec_module(memory);secret=memory.recover();c=None;complete=[]
 try:
  c=d.connect72(secret);capacity=d.code(c,d.PY72,"import shutil,json,time;print(json.dumps(dict(epoch=time.time(),free=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2/forensic_originals').free)))",{},timeout=30);c.close();c=None
  put('CLOSED41_OLD36_28_TARGET_FRESH_CAPACITY_ACTUAL.json',capacity)
  maximum=min(4*1024**3,capacity['free']-25*1024**3-64*1024**2)
  c=d.t.connect();inv=d.code(c,d.t.PY,INVENTORY,dict(sources=sources,current_owner_root=current['owner_root'],remaining=proof['remaining_actual_snapshot'],max_bytes=maximum),timeout=180);c.close();c=None
  put('CLOSED41_OLD36_28_COMBINED_MINIMAL_FRESH_SOURCE_ACTUAL.json',inv)
  if inv['already_above_original_disk25']:
   put('CLOSED41_OLD36_28_NO_TRANSFER_NEEDED_ACTUAL.json',dict(epoch=time.time(),source_free=inv['source_free'],no_new_target_or_process=True));return
  if not inv['files'] or not inv['source_plus_selected_above_original25'] or capacity['free']-inv['total_bytes']<=25*1024**3:
   put('CLOSED41_OLD36_28_CAPACITY_BLOCKED_NO_TRANSFER_ACTUAL.json',dict(epoch=time.time(),source_above_original_disk25=False,no_target_or_process_created=True,source=inv,target=capacity));return
  for batch,src in enumerate(sources):
   rows=[{k:v for k,v in row.items() if k!='batch'} for row in inv['files'] if row['batch']==batch]
   if not rows:continue
   label='CLOSED41_OLD'+('36' if batch==0 else '28')+'_MINIMAL';root72='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_'+label+'_V4';root210='/mnt/mod4_linux_durable_20261013/PEER_TLS_'+label+'_V4';target=root72+'/retained_control_npz';token=secrets.token_hex(32);ready=None;receiver_result=None;rcfg={};scfg={}
   manifest=hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()
   try:
    c=d.connect72(secret);d.code(c,d.PY72,ops.INSTALL,dict(root=root72,parent='/home/lc01/Zonglin Li/zonglin2/forensic_originals'),timeout=30)
    sf=c.open_sftp()
    try:sf.put(str(P),root72+'/'+P.name)
    finally:sf.close()
    d.code(c,d.PY72,"from pathlib import Path;import json;B=Path(v['target']);assert not B.exists();B.mkdir();print(json.dumps(dict(new_target=str(B))))",dict(target=target),timeout=30)
    put(label+'_TARGET_SOURCE_AST_ACTUAL.json',d.code(c,d.PY72,ops.CHECK,dict(script=root72+'/'+P.name,SHA=sha),timeout=30))
    rcfg=dict(role='receiver',controller_root=root72,target=target,files=rows,manifest_SHA=manifest,token=token)
    ready=d.code(c,d.PY72,ops.BOOT,dict(root=root72,python=d.PY72,SHA=sha,cfg=rcfg),timeout=45);put(label+'_RECEIVER_READY_ACTUAL.json',ready);c.close();c=None
    c=d.t.connect();d.code(c,d.t.PY,ops.INSTALL,dict(root=root210,parent='/mnt/mod4_linux_durable_20261013'),timeout=30)
    sf=c.open_sftp()
    try:sf.put(str(P),root210+'/'+P.name)
    finally:sf.close()
    put(label+'_SOURCE_AST_ACTUAL.json',d.code(c,d.t.PY,ops.CHECK,dict(script=root210+'/'+P.name,SHA=sha),timeout=30))
    scfg=dict(role='sender',controller_root=root210,source_root=src['source_root'],owner_root=current['owner_root'],private_lock=src['private_lock'],remaining=proof['remaining_actual_snapshot'],files=rows,manifest_SHA=manifest,token=token,address='10.24.0.72',port=ready['port'],TLS_certificate_SHA=ready['TLS_certificate_SHA'])
    sent=d.code(c,d.t.PY,"import runpy;runpy.run_path(v['script'],run_name='__main__',init_globals={'CFG':v['cfg']})",dict(script=root210+'/'+P.name,cfg=scfg),timeout=1300);put(label+'_SOURCE_COMPLETE_ACTUAL.json',sent)
    put(label+'_SOURCE_FULL_TEXT_ALL_OUT_ACTUAL.json',d.code(c,d.t.PY,READ_SOURCE,dict(root=root210),timeout=45));c.close();c=None
    c=d.connect72(secret);receiver_result=d.code(c,d.PY72,ops.READ_RECEIVER,dict(root=root72),timeout=150);c.close();c=None;put(label+'_RECEIVER_FULL_TEXT_ALL_OUT_ACTUAL.json',receiver_result)
    got=json.loads(receiver_result['texts']['RECEIVER_COMPLETE_ACTUAL.json']);assert got['passed'] and receiver_result['all_receiver_processes_actual_out']
    assert {(r['path'],r['bytes'],r['SHA']) for r in got['files']}=={(r['path'],r['bytes'],r['SHA']) for r in sent['files']}
    complete.append(dict(source_stage=src['stage'],target=target,files=sent['files'],source_free_after=sent['source_free_after'],all_own_storage_processes_actual_out=True))
   except BaseException:
    if c:c.close();c=None
    if ready and receiver_result is None:
     try:
      c=d.connect72(secret);receiver_result=d.code(c,d.PY72,ops.READ_RECEIVER,dict(root=root72),timeout=150);c.close();c=None;put(label+'_RECEIVER_ERROR_ALL_OUT_TEXT_ACTUAL.json',receiver_result)
     except BaseException:put(label+'_RECEIVER_OUT_READ_ORIGINAL_ERROR_ACTUAL.json',dict(epoch=time.time(),error=traceback.format_exc(),do_not_assume_out=True))
    raise
   finally:token=None;rcfg.clear();scfg.clear()
  assert complete;free=complete[-1]['source_free_after']
  put('CLOSED41_OLD36_28_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json',dict(epoch=time.time(),passed=True,batches=complete,source_free_after=free,source_above_original_disk25=free>25*1024**3,all_full_SHA_retained_on72=True,canonical_bytes_unchanged=True,all_own_storage_processes_actual_out=True,no_GPU_PPO_or_budget_writer=True))
  print(json.dumps(dict(files=sum(len(x['files']) for x in complete),source_free=free,above_original_disk25=free>25*1024**3)))
 except BaseException:
  put('CLOSED41_OLD36_28_MINIMAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),completed_batches=complete,new_missing_only_after_actual_return=True));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
'''
text=text[:start]+newmain;ast.parse(text)
dest=N/'relocate_missing_closed36_28_after_closed41_TLS_V4_once.py';assert not dest.exists();dest.write_text(text,encoding='utf8')
wrapper=(B/'same_authorized_session_compressed_transport_v6.py').read_text('utf8');needle='extract_new_closed39_actual_tuck_selected_motion_CPU_bounded_once.py';assert wrapper.count(needle)==1
wrapper=wrapper.replace(repr(needle),repr(needle)+','+repr(dest.name));ast.parse(wrapper)
v7=B/'same_authorized_session_compressed_transport_v7.py';assert not v7.exists();v7.write_text(wrapper,encoding='utf8')
with (R/'CLOSED41_TWO_ROOT_MINIMAL_STORAGE_AND_WRAPPER_V7_SOURCE_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_AST_only=True,new_helper=str(dest),helper_SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),byteexact_TLS_core_SHA=hashlib.sha256((T/'forensic_tls_peer_transfer_V96_V4.py').read_bytes()).hexdigest(),combined_source_plus_selected_gt25_target_minus_selected_gt25_before_any_controller=True,minimum_number_then_bytes_subset=True,only_new_wrapper_allowlist_basename=dest.name,no_old_helper_or_batch_rerun=True,no_GPU_native_query_or_budget_write=True),f,indent=2)
print(json.dumps(dict(prepared=True,helper=str(dest),wrapper=str(v7))))
