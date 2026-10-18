"""One hour timed block, preserving original runtime and physical save-stop protection."""
from pathlib import Path
import os,sys,json,time,getpass,secrets,traceback
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'payload/h1';P=B.parent;E=P/'proposal_ce3_same_candidate_finite_v1';sys.path.insert(0,str(E))
import deploy_human_approved_ce3_new_native_then_one_finite1800_once as d
a=d.a;launch=d.launch
SOURCE='/mnt/mod4_linux_durable_20261013/H1h2_1810p5/owner';TARGET='/home/lc01/Zonglin Li/zonglin2/tasks/H1h2_1810p5'
CREATE=d.CREATE.replace('ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90','fe7780a502743dc12c0826d82f4a5a5a5ee8917f095890c7bfb866c48b600309')
OWNER=d.OWNER.replace('H1mp_1810p2/owner','H1h1_1810p4/owner').replace('ce3c69bbcf56bd6c884681f23f527b9fe9e1884a7b5444ff90d3f7a2e28b2d90','fe7780a502743dc12c0826d82f4a5a5a5ee8917f095890c7bfb866c48b600309').replace("remaining_training_seconds']>1800","remaining_training_seconds']>3900")
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 prep=json.loads((R/'H1_ONE_HOUR_SOURCE_TIMING_CPU_PREPARED_ACTUAL.json').read_bytes());assert prep['passed_CPU_only'] and prep['training_block_GO_to_save_seconds']==3600 and prep['arbitrary24_update_stop_removed'];specs=prep['specs'];assert specs['h1']['max_parent_seconds']==3900 and specs['h1']['source_Adamstep']==648000
 put('H1_ONE_HOUR_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,exact_actual_CIM_alive_only_exclusive_transport=True,requested_one_hour_before_behavior_audit=True,original_total_budget_unchanged=True))
 pw=getpass.getpass('72 H1 one-hour training block (hidden): ');c=None;cfg=None
 try:
  c=a.connect72(pw);put('H1_ONE_HOUR_CURRENT_GPU_RAM_DISK_REAL_LOCKS_OLD_EXIT_ADMISSION.json',a.code(c,a.PY,CREATE,TARGET,specs['h1']['previous_runtime_root'],specs['h1']['GPU_UUID'],timeout=90));sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   made={TARGET,TARGET+'/job0'}
   for p in sorted(Q.rglob('*')):
    if '__pycache__' in p.parts:continue
    remote=TARGET+'/'+p.relative_to(Q).as_posix()
    if p.is_dir():
     if remote not in made:sf.mkdir(remote);made.add(remote)
    else:sf.put(str(p),remote)
  finally:sf.close()
  put('H1_ONE_HOUR_TARGET_FULL_SOURCE_RUNTIME_RSL_SDK_CPU_ACTUAL.json',a.code(c,a.PY,d.d.CPU,TARGET,timeout=180))
  put('H1_ONE_HOUR_TARGET_NO_24_UPDATE_STOP_CPU_ACTUAL.json',a.code(c,a.PY,"from pathlib import Path;import sys,json;B=Path(sys.argv[1]);sys.path.insert(0,str(B));import three_slot_common_v1 as b;from own_H1_storage_finite_guard_v1 import should_save_stop,H1_MAX_COMPLETE_UPDATES;assert b.CAPS['h1']==3900 and H1_MAX_COMPLETE_UPDATES is None;assert all(not should_save_stop('production',k,9*1024**3) for k in (24,25,100));assert should_save_stop('production',25,8*1024**3-1);print(json.dumps(dict(hour3600_plus_exit300=True,no_24_update_limit=True,storage8GiB_retained=True,no_GPU_or_optimizer=True)))",TARGET,timeout=60))
 finally:
  if c:c.close();c=None
 try:
  c=a.t.connect();put('H1_ONE_HOUR_ORIGINAL_CANONICAL_COST_EXIT_REAL_LOCKS_HANDOFF.json',a.code(c,a.t.PY,OWNER,SOURCE,timeout=90));sf=c.open_sftp();names=('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','owner_listener_ready_cpu_reviewed_v1.py')
  try:
   for n in names:sf.put(str(Q/n),SOURCE+'/'+n)
  finally:sf.close()
  put('H1_ONE_HOUR_SOURCE_CONTROLLERS_EXACT_SHA_AST_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import ast,json,hashlib;B=Path("+repr(SOURCE)+");rows="+repr([dict(name=n,SHA=a.H(Q/n)) for n in names])+";[(ast.parse((B/r['name']).read_text('utf8')),None) for r in rows];assert all(hashlib.sha256((B/r['name']).read_bytes()).hexdigest()==r['SHA'] for r in rows);print(json.dumps(dict(passed=True,files=rows)))"))
  cfg=dict(role='owner',experts=specs,run_id='H1_ONE_HOUR_FE778_'+str(time.time_ns()),token=secrets.token_hex(32));owner=launch(a.code,c,a.t.PY,SOURCE,'three_slot_finite_owner_v1.py',cfg);put('H1_ONE_HOUR_ORIGINAL_WRITER_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,no_GO_yet=True))
  put('H1_ONE_HOUR_ORIGINAL_LISTENER_READY_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json;B=Path("+repr(SOURCE)+");sys.path.insert(0,str(B));from owner_listener_ready_cpu_reviewed_v1 import wait_actual;print(json.dumps(wait_actual(B,"+repr(owner['detached_pid'])+",20.)))",timeout=40));d.SOURCE=SOURCE;d.R=R;d.terminal(c,cfg,'e2');d.terminal(c,cfg,'recovery')
 finally:
  if c:c.close();c=None
 try:
  c=a.connect72(pw);pw=None;node=launch(a.code,c,a.PY,TARGET,'three_slot_finite_node_v1.py',dict(specs['h1'],role='node',run_id=cfg['run_id'],token=cfg['token']))
  put('H1_ONE_HOUR_FE778_NATIVE_THEN_TIMED_PRODUCTION_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,node=node,source_owner_root=SOURCE,target_root=TARGET,source_SHA=specs['h1']['source_SHA'],source_Adam648000=True,own_new_source_native180_and_CPU_then_original_owner_GO=True,save_after_GO3600_seconds=True,lifecycle_cap3900_exit_reserve300=True,old24_update_stop_removed=True,original_start25GiB_and_complete_update_storage8GiB_guards=True,E2_E3_hold0worker0GO0charge=True,not_native_CPU_or_PPO_first_pass_yet=True,one_original_writer_actual_account_once_same_total_budget=True,no_behavior_frozen_audit_mid_hour=True,no_automatic_extra_window=True))
  print(json.dumps(dict(owner=owner,node=node,actual_native_chain_dispatched=True,one_hour_timed_production_after_native_CPU=True,old24_update_limit_removed=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('H1_ONE_HOUR_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_partial_before_new_attempt_no_hotpatch=True));raise
