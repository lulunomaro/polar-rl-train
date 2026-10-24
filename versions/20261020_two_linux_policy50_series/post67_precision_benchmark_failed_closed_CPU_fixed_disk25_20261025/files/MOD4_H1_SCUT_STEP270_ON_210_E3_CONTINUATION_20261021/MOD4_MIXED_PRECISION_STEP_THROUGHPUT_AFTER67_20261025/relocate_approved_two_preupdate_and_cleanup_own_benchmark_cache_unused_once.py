"""Reserved storage support: run only after this pair actually closes and CPU passes.

Reuse the actually passed TLS/HMAC protocol; fresh manifests, identities and
space are required. This does not prepare a future model or launch training.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,secrets,sys,time,traceback
M=Path(__file__).resolve().parent;T=M.parent;N=T/'H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025';W=T.parent;R=M/'reports';P=M/'forensic_tls_peer_transfer_APPROVED_TWO_PREUPDATE_AFTER67_V1.py'
spec=importlib.util.spec_from_file_location('passed_storage_protocol_controller_definitions',T/'finish_closed_pair5_missing_forensics_direct_TLS_V96_V4_once.py');ops=importlib.util.module_from_spec(spec);spec.loader.exec_module(ops);d=ops.d
ops.BOOT=ops.BOOT.replace('forensic_tls_peer_transfer_V96_V4.py','forensic_tls_peer_transfer_APPROVED_TWO_PREUPDATE_AFTER67_V1.py')
read=lambda p:json.loads(Path(p).read_bytes());H=ops.H
ROOT72='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_CLOSED32_AFTER_CLOSED39_TUCK_V3'
ROOT210='/mnt/mod4_linux_durable_20261013/PEER_TLS_CLOSED32_AFTER_CLOSED39_TUCK_V3'
TARGET=ROOT72+'/retained_control_npz'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
INVENTORY="\nfrom pathlib import Path\nimport fcntl,hashlib,json,os,psutil,stat,shutil,time\nC=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');canonical=C.read_bytes();c=json.loads(canonical)\nassert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9 and c['remaining_training_seconds']==v['remaining']\nroots=[Path(v['benchmark_owner_root']),Path(v['benchmark_h1_root']),Path(v['source_root'])]\nassert json.loads((roots[0]/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']\nfor root in roots[1:]:assert json.loads((root/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited']\nassert not any(p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))\nfor lock in [C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['private_lock'])]:\n with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\ncache=[]\nfor row in v['cache_files']:\n p=Path(row['path']);assert p.resolve().is_relative_to(roots[1].resolve()) and not p.is_symlink();st=p.stat();assert stat.S_ISREG(st.st_mode) and (st.st_size,st.st_mtime_ns,st.st_ino,st.st_nlink)==(row['bytes'],row['mtime_ns'],row['inode'],1)\n assert any(p.resolve().is_relative_to(x.resolve()) for x in [roots[1]/'job0/cache',roots[1]/'job0/home/.nv/ComputeCache',roots[1]/'job0/tmp'])\n h=hashlib.sha256()\n with p.open('rb') as f:\n  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)\n cache.append(dict(row,SHA=h.hexdigest()))\nselected=[]\nfor row in v['selected']:\n p=Path(row['path']);assert p.parent==roots[2]/'job0/production/control_prefix_raw' and not p.is_symlink();st=p.stat();assert stat.S_ISREG(st.st_mode) and st.st_size==row['bytes'] and st.st_nlink==1\n h=hashlib.sha256()\n with p.open('rb') as f:\n  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)\n assert h.hexdigest()==row['SHA'];selected.append(dict(row,mtime_ns=st.st_mtime_ns,inode=st.st_ino))\nfree=shutil.disk_usage(roots[2]).free;assert free+sum(r['allocated_bytes'] for r in cache)+sum(r['bytes'] for r in selected)-v['copy_planning_bytes']>25*1024**3\nassert C.read_bytes()==canonical\nprint(json.dumps(dict(epoch=time.time(),files=selected,cache_files=cache,total_bytes=sum(r['bytes'] for r in selected),source_free=free,original_canonical_SHA=hashlib.sha256(canonical).hexdigest(),allout_original_locks_and_exact_narrow_approved_paths=True,no_cache_delete_yet=True)))\n"

READ_SOURCE=r'''
from pathlib import Path
import json,psutil,time
B=Path(v['root']);e=json.loads((B/'SENDER_EXIT_ACTUAL.json').read_bytes());i=e['identity']
try:p=psutil.Process(i['pid']);alive=abs(p.create_time()-i['creation'])<.01
except psutil.NoSuchProcess:alive=False
assert not alive
print(json.dumps(dict(epoch=time.time(),sender_actual_out=True,texts={p.name:p.read_text('utf8') for p in B.iterdir() if p.is_file() and p.suffix in ('.json','.log','.py')})))
'''

CLEAN_CACHE="\nfrom pathlib import Path\nimport fcntl,hashlib,json,os,psutil,shutil,stat,time\nB=Path(v['root']);owner=Path(v['owner']);C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')\nassert hashlib.sha256(C.read_bytes()).hexdigest()==v['canonical_SHA'] and json.loads(C.read_bytes())['active_segment'] is None\nassert json.loads((B/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'] and json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']\nassert not any(p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in (B,owner)) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))\nlocks=[]\nfor p in [C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock'),Path(v['private_lock'])]:\n f=p.open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)\nbefore=shutil.disk_usage(B).free;actions=[]\nfor row in v['files']:\n p=Path(row['path']);assert any(p.resolve().is_relative_to(x.resolve()) for x in [B/'job0/cache',B/'job0/home/.nv/ComputeCache',B/'job0/tmp']) and not p.is_symlink()\n st=p.stat();assert stat.S_ISREG(st.st_mode) and (st.st_size,st.st_mtime_ns,st.st_ino,st.st_nlink)==(row['bytes'],row['mtime_ns'],row['inode'],1)\n h=hashlib.sha256()\n with p.open('rb') as f:\n  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)\n assert h.hexdigest()==row['SHA'];p.unlink();actions.append(row)\nassert hashlib.sha256(C.read_bytes()).hexdigest()==v['canonical_SHA']\nprint(json.dumps(dict(epoch=time.time(),removed_files=len(actions),actions=actions,source_free_before=before,source_free_after=shutil.disk_usage(B).free,only_explicit_own_failed_benchmark_regenerable_cache=True,no_model_raw_FINAL_source_error_log_touched=True,canonical_SHA_unchanged=True)))\nfor f in reversed(locks):fcntl.flock(f,fcntl.LOCK_UN);f.close()\n"

def main():
 approval=read(R/'HUMAN_EXPLICIT_TWO_PREUPDATE_RELOCATION_AND_OWN_FAILED_CACHE_CLEANUP_APPROVAL_ACTUAL.json');assert approval['approved'] and approval['human_reply']=='批准这两份配套快照转存及本次缓存清理'
 proof=read(R/'BENCHMARK_TEXT_CANONICAL_AND_ORIGINAL_COST_RETURNED_ACTUAL.json');assert proof['original_canonical_cost_settled'] and proof['owner_node_workers_all_actual_out']
 current=read(R/'PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');oldq=read(N/'reports/PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');src=dict(source_root=oldq['roots']['h1'],private_lock=oldq['specs']['h1']['private_lock'],stage=N.name);sources=[src]
 assert read(T/'reports/V96_V4_ACTUAL_TLS_HMAC_FULL_SHA_TRANSPORT_CPU_ACTUAL.json')['passed'];sha=H(P)
 cache=read(R/'OWN_FAILED_BENCHMARK_CACHE_METADATA_210_ACTUAL.json');selected=approval['question_scope']['selected_preupdate_files']
 put('APPROVED_TWO_PT_AND_OWN_CACHE_EXECUTION_STARTED_ACTUAL.json',dict(epoch=time.time(),protocol_SHA=sha,TLS_HMAC_implementation_reused_no_new_network_CPU=True,only_explicit_two_PT_and30_own_cache_files=True))
 m=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(m);m.loader.exec_module(memory);secret=memory.recover();c=None;complete=[]
 try:
  c=d.connect72(secret);capacity=d.code(c,d.PY72,"import shutil,json,time;print(json.dumps(dict(epoch=time.time(),free=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2/forensic_originals').free)))",{},timeout=30);c.close();c=None
  put('CLOSED67_CURRENT67_OLD30_TARGET_FRESH_CAPACITY_ACTUAL.json',capacity)
  maximum=min(20*1024**3,capacity['free']-25*1024**3-64*1024**2)
  c=d.t.connect();inv=d.code(c,d.t.PY,INVENTORY,dict(benchmark_owner_root=current['owner_root'],benchmark_h1_root=current['roots']['h1'],source_root=src['source_root'],private_lock=src['private_lock'],remaining=proof['original_remaining_closed_snapshot'],cache_files=cache['files'],selected=selected,copy_planning_bytes=approval['question_scope']['known_payload_bytes']+16*1024**2),timeout=180);c.close();c=None
  put('CLOSED67_CURRENT67_OLD30_COMBINED_MINIMAL_FRESH_SOURCE_ACTUAL.json',inv)
  assert inv['total_bytes']<maximum and capacity['free']-inv['total_bytes']>25*1024**3
  for batch,src in enumerate(sources):
   rows=inv['files']
   if not rows:continue
   label='BENCHMARK_AFTER67_APPROVED_TWO_PREUPDATE';root72='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_'+label+'_V4';root210='/mnt/mod4_linux_durable_20261013/PEER_TLS_'+label+'_V4';target=root72+'/retained_control_npz';token=secrets.token_hex(32);ready=None;receiver_result=None;rcfg={};scfg={}
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
    scfg=dict(role='sender',controller_root=root210,source_root=src['source_root'],owner_root=current['owner_root'],private_lock=src['private_lock'],remaining=proof['original_remaining_closed_snapshot'],files=rows,manifest_SHA=manifest,token=token,address='10.24.0.72',port=ready['port'],TLS_certificate_SHA=ready['TLS_certificate_SHA'])
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
  c=d.t.connect()
  try:clean=d.code(c,d.t.PY,CLEAN_CACHE,dict(root=current['roots']['h1'],owner=current['owner_root'],files=inv['cache_files'],canonical_SHA=inv['original_canonical_SHA'],private_lock=src['private_lock']),timeout=90)
  finally:c.close();c=None
  put('ONLY_APPROVED_OWN_FAILED_BENCHMARK30_COMPILED_CACHE_CLEANUP_ACTUAL.json',clean)
  put('APPROVED_TWO_PREUPDATE_RETAINED_ON72_AND_OWN_CACHE_COMPLETE_ACTUAL.json',dict(epoch=time.time(),passed=True,batches=complete,cache_cleanup=clean,source_free_after=clean['source_free_after'],all_full_SHA_retained_on72=True,canonical_bytes_unchanged=True,all_own_storage_processes_actual_out=True,no_GPU_PPO_or_budget_writer=True))
  print(json.dumps(dict(files=sum(len(x['files']) for x in complete),cache_files=clean['removed_files'],source_free=clean['source_free_after'],above_original_disk25=clean['source_free_after']>25*1024**3)))
 except BaseException:
  put('CLOSED67_CURRENT67_OLD30_MINIMAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),completed_batches=complete,new_missing_only_after_actual_return=True));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
