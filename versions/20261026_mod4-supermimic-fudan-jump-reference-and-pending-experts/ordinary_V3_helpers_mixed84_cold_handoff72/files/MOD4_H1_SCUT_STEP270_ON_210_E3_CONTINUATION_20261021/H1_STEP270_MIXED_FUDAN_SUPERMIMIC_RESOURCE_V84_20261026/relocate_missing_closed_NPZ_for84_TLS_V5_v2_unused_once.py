"""Reserved storage support: run only after this pair actually closes and CPU passes.

Reuse the actually passed TLS/HMAC protocol; fresh manifests, identities and
space are required. This does not prepare a future model or launch training.
"""
from pathlib import Path
import ast,hashlib,importlib.util,json,secrets,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';P=T/'forensic_tls_peer_transfer_V96_V5_NINTH.py'
spec=importlib.util.spec_from_file_location('passed_storage_protocol_controller_definitions',T/'finish_closed_pair5_missing_forensics_direct_TLS_V96_V4_once.py');ops=importlib.util.module_from_spec(spec);spec.loader.exec_module(ops);d=ops.d
ops.BOOT=ops.BOOT.replace('forensic_tls_peer_transfer_V96_V4.py','forensic_tls_peer_transfer_V96_V5_NINTH.py')
read=lambda p:json.loads(Path(p).read_bytes());H=ops.H
sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route;d.t.connect=route.connect
ROOT72='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_CLOSED32_AFTER_CLOSED39_TUCK_V3'
ROOT210='/mnt/mod4_linux_durable_20261013/PEER_TLS_CLOSED32_AFTER_CLOSED39_TUCK_V3'
TARGET=ROOT72+'/retained_control_npz'
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
INVENTORY="\nfrom pathlib import Path\nimport fcntl,hashlib,itertools,json,os,psutil,re,shutil,time\nC=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');canonical=C.read_bytes();c=json.loads(canonical)\nassert c['active_segment'] is None and c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9 and c['remaining_training_seconds']==v['remaining']\nowners=[Path(v['current_owner_root'])]+[Path(x['owner_root']) for x in v['sources']]\nfor owner in owners:assert json.loads((owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']\nroots=owners+[Path(x['source_root']) for x in v['sources']]\nassert not any(p.pid!=os.getpid() and any(any(a.startswith(str(root)+'/') for root in roots) for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))\nfor lock in [C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]+[Path(x['private_lock']) for x in v['sources']]:\n with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\nfree=shutil.disk_usage(v['sources'][0]['source_root']).free;available=[]\nif free<=25*1024**3:\n for batch,src in enumerate(v['sources']):\n  old=Path(src['source_root']);assert json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'];base=old/'job0/production/control_prefix_raw'\n  for row in json.loads((base/'CONTROL_VALID_PREFIX_INDEX_ACTUAL.json').read_bytes())['index']:\n   p=Path(row['path'])\n   if not p.exists():continue\n   assert p.resolve().is_relative_to(base.resolve()) and not p.is_symlink() and re.fullmatch(r'control_prefix_\\d+\\.npz',p.name)\n   s=p.stat();assert s.st_size==row['bytes'] and s.st_nlink==1\n   available.append(dict(path=str(p),bytes=s.st_size,SHA=row['SHA'],mtime_ns=s.st_mtime_ns,inode=s.st_ino,batch=batch))\nbest=None\nfor count in range(1,len(available)+1):\n for combo in itertools.combinations(available,count):\n  total=sum(x['bytes'] for x in combo)\n  if free+total>25*1024**3+v['install_copy_planning_bytes'] and total<=v['max_bytes'] and (best is None or total<sum(x['bytes'] for x in best)):best=combo\n if best is not None:break\nselected=list(best or [])\ncache={r['path']:r for r in v['sha_cache']}\nfor row in selected:\n old=cache.get(row['path'])\n if old and all(old[k]==row[k] for k in ('bytes','SHA','mtime_ns','inode')):continue\n h=hashlib.sha256()\n with Path(row['path']).open('rb') as f:\n  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)\n assert h.hexdigest()==row['SHA']\nassert C.read_bytes()==canonical\nprint(json.dumps(dict(epoch=time.time(),files=selected,total_bytes=sum(x['bytes'] for x in selected),source_free=free,already_above_original_disk25=free>25*1024**3,source_plus_selected_above_original25=free+sum(x['bytes'] for x in selected)>25*1024**3,canonical_SHA=hashlib.sha256(canonical).hexdigest(),actual_allout_and_original_locks_free=True,minimum_file_count_then_minimum_total_bytes=True,unselected_stat_only_no_raw_hash=True)))\n"

READ_SOURCE=r'''
from pathlib import Path
import json,psutil,time
B=Path(v['root']);e=json.loads((B/'SENDER_EXIT_ACTUAL.json').read_bytes());i=e['identity']
try:p=psutil.Process(i['pid']);alive=abs(p.create_time()-i['creation'])<.01
except psutil.NoSuchProcess:alive=False
assert not alive
print(json.dumps(dict(epoch=time.time(),sender_actual_out=True,texts={p.name:p.read_text('utf8') for p in B.iterdir() if p.is_file() and p.suffix in ('.json','.log','.py')})))
'''

def main():
 O=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026'
 proof=read(O/'reports/THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json');current=read(O/'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out']
 sources=[]
 for name,report in [('H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026','THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'),('H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026','HEALTHY_PRODUCTION_PAIR_AND_FAILED_METHOD_ORIGINAL_ALL_COST_CPU_ACTUAL.json'),('H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026','PRODUCTION_PAIR_AND_NATIVE_METHOD_FULLSTATE_ORIGINAL_COST_CPU_ACTUAL.json'),('H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026','THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json')]:
  stage=T/name;oldp=read(stage/'reports'/report);oq=read(stage/'reports/THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json');assert oldp['passed'] and oldp['all_owner_nodes_children_actual_out'] and oldp['original_canonical_cost_settled'];sources.append(dict(source_root=oq['roots']['h1'],owner_root=oq['owner_root'],private_lock=oq['specs']['h1']['private_lock'],stage=name))
 q=read(R/'THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')
 known_payload_bytes=sum(r['bytes'] for r in read(Path(q['payloads']['h1'])/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files'])
 planning_bytes=known_payload_bytes+16*1024**2
 assert read(T/'reports/V96_V4_ACTUAL_TLS_HMAC_FULL_SHA_TRANSPORT_CPU_ACTUAL.json')['passed'];sha=H(P);assert sha=='786064012058a6fb642da821e6fab0c625e6c9077373482fe857a5251fb69545'
 put('CLOSED83B_FOR84V2_MISSING_CLOSED_NPZ_MINIMAL_HEADROOM_STARTED_ACTUAL.json',dict(epoch=time.time(),protocol_source_SHA=sha,reused_actual_TLS_HMAC_CPU_no_reexecution=True,current_paired_closed_CPU=True,original_remaining_snapshot=proof['remaining_actual_snapshot'],combined_preflight_before_any_target_controller=True,known_H1_manifest_bytes=known_payload_bytes,install_copy_planning_bytes=planning_bytes,copy_planning_not_new_training_gate=True))
 cache=dict(files=[])
 m=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(m);m.loader.exec_module(memory);secret=memory.recover();c=None;complete=[]
 try:
  c=d.connect72(secret);capacity=d.code(c,d.PY72,"import shutil,json,time;print(json.dumps(dict(epoch=time.time(),free=shutil.disk_usage('/home/lc01/Zonglin Li/zonglin2/forensic_originals').free)))",{},timeout=30);c.close();c=None
  put('CLOSED83B_FOR84V2_MISSING_CLOSED_NPZ_TARGET_FRESH_CAPACITY_ACTUAL.json',capacity)
  maximum=min(4*1024**3,capacity['free']-25*1024**3-64*1024**2)
  c=d.t.connect();inv=d.code(c,d.t.PY,INVENTORY,dict(sha_cache=cache['files'],sources=sources,current_owner_root=current['owner_root'],remaining=proof['remaining_actual_snapshot'],max_bytes=maximum,install_copy_planning_bytes=planning_bytes),timeout=180);c.close();c=None
  put('CLOSED83B_FOR84V2_MISSING_CLOSED_NPZ_COMBINED_MINIMAL_FRESH_SOURCE_ACTUAL.json',inv)
  if inv['already_above_original_disk25']:
   put('CLOSED83B_FOR84V2_MISSING_CLOSED_NPZ_NO_TRANSFER_NEEDED_ACTUAL.json',dict(epoch=time.time(),source_free=inv['source_free'],no_new_target_or_process=True));return
  if not inv['files'] or not inv['source_plus_selected_above_original25'] or capacity['free']-inv['total_bytes']<=25*1024**3:
   put('CLOSED83B_FOR84V2_MISSING_CLOSED_NPZ_CAPACITY_BLOCKED_NO_TRANSFER_ACTUAL.json',dict(epoch=time.time(),source_above_original_disk25=False,no_target_or_process_created=True,source=inv,target=capacity));return
  for batch,src in enumerate(sources):
   rows=[{k:v for k,v in row.items() if k!='batch'} for row in inv['files'] if row['batch']==batch]
   if not rows:continue
   label=['CLOSED83B_FOR84V2_OLD80_MINIMAL','CLOSED83B_FOR84V2_OLD81O_MINIMAL','CLOSED83B_FOR84V2_OLD82Q_MINIMAL','CLOSED83B_FOR84V2_CURRENT83B_MINIMAL'][batch];root72='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_'+label+'_V4';root210='/mnt/mod4_linux_durable_20261013/PEER_TLS_'+label+'_V4';target=root72+'/retained_control_npz';token=secrets.token_hex(32);ready=None;receiver_result=None;rcfg={};scfg={}
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
  put('CLOSED83B_FOR84V2_MISSING_CLOSED_NPZ_MINIMAL_VERIFIED_RETAINED_ON72_SPACE_RELEASED_ACTUAL.json',dict(epoch=time.time(),passed=True,batches=complete,source_free_after=free,source_above_original_disk25=free>25*1024**3,all_full_SHA_retained_on72=True,canonical_bytes_unchanged=True,all_own_storage_processes_actual_out=True,no_GPU_PPO_or_budget_writer=True))
  print(json.dumps(dict(files=sum(len(x['files']) for x in complete),source_free=free,above_original_disk25=free>25*1024**3)))
 except BaseException:
  put('CLOSED83B_FOR84V2_MISSING_CLOSED_NPZ_MINIMAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),completed_batches=complete,new_missing_only_after_actual_return=True));raise
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':main()
