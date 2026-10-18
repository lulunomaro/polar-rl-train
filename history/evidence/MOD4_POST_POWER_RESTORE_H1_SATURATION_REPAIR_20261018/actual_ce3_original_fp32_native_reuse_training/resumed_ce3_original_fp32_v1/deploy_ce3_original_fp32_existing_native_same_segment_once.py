"""Continue existing ce3 finite task with original formal FP32 audit; no native replay."""
from pathlib import Path
import os,sys,json,time,getpass,secrets,traceback,importlib.util
B=Path(__file__).resolve().parent;R=B/'reports';Q=B/'payload/h1';ROOT=B.parent;E=ROOT/'proposal_ce3_same_candidate_finite_v1';sys.path.insert(0,str(E))
import deploy_human_approved_ce3_new_native_then_one_finite1800_once as d
a=d.a;launch=d.launch
SOURCE='/mnt/mod4_linux_durable_20261013/H1cr_1810p3/owner';TARGET='/home/lc01/Zonglin Li/zonglin2/tasks/H1cr_1810p3'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
CREATE=d.CREATE.replace("B.mkdir(parents=True);(B/'job0').mkdir()",r'''
cq=owned/'tasks/H1cq_1810p3';assert json.loads((cq/'NODE_EXIT_ACTUAL.json').read_bytes())['actual_all_own_children_waited'];t=json.loads((cq/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert t['original_error'] and t['terminal_all_own_children_waited'];assert not (cq/'job0/production').exists() and not (cq/'GO_PRODUCTION.json').exists()
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:assert p.pid==__import__('os').getpid() or not any(s.startswith(str(cq)+'/') for s in p.info['cmdline'] or [])
 except psutil.Error:pass
B.mkdir(parents=True);(B/'job0').mkdir()
''')
OWNER=r'''
from pathlib import Path
import sys,json,time,psutil,fcntl,socket,shutil,os
B=Path(sys.argv[1]);owned=Path('/mnt/mod4_linux_durable_20261013');assert os.path.ismount(owned);old=owned/'H1cq_1810p3/owner';assert B.resolve().is_relative_to(owned.resolve()) and not B.exists()
v=json.loads((old/'COHORT_FINAL.json').read_bytes());assert v['original_cost_settled'] and v['go']=={} and json.loads((old/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'];i=json.loads((old/'OWNER_IDENTITY.json').read_bytes())
if psutil.pid_exists(i['pid']):
 p=psutil.Process(i['pid']);assert abs(p.create_time()-i['creation'])>.01 or p.status()==psutil.STATUS_ZOMBIE
for p in psutil.process_iter(['pid','cmdline','create_time']):
 try:assert p.pid==os.getpid() or not any(s.startswith(str(old)+'/') for s in p.info['cmdline'] or [])
 except psutil.Error:pass
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');v=json.loads(C.read_bytes());assert v['active_segment'] is None and v['authorized_training_seconds']==1188000 and len(v['budget_extensions'])==7 and v['remaining_training_seconds']>1800
assert not any(x.get('owner_parent_pid')==81434 for x in v['completed_segments']);locks=[]
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN);locks.append(str(p))
with socket.socket() as s:s.bind(('10.24.4.210',29754))
assert shutil.disk_usage(owned).free>1024**3 and shutil.disk_usage(C.parent).free>512*1024**2;B.mkdir(parents=True)
print(json.dumps(dict(epoch=time.time(),old_owner_identity=i,old_failed_native_cohort_actual_out_zero_GO_zero_charge=True,actual_canonicalNone_two_real_fcntlFree=locks,original_remaining_snapshot=v['remaining_training_seconds'],D_free=shutil.disk_usage(owned).free,source_metadata_only_not_GPU_admission=True,no_canonical_write=True)))
'''
def main():
 prep=json.loads((R/'CE3_ORIGINAL_FP32_NATIVE_REUSE_PAYLOAD_CPU_ACTUAL.json').read_bytes());assert prep['passed_CPU_only'] and len(prep['positive_and13_negatives'])==13;specs=prep['specs']
 put('CE3_ORIGINAL_FP32_FINITE_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,actual_CIM_alive_only_exclusive_all_transport=True,scope='same unstarted ce3 finite task, original FP32 audit restored',no_new_budget_or_automatic_following_window=True))
 pw=getpass.getpass('Host72 existing ce3 training continuation (hidden): ');c=None;cfg=None
 try:
  c=a.connect72(pw);put('TARGET_CURRENT_RESOURCE_OLD_NATIVE_OUT_REAL_LOCKS_ACTUAL.json',a.code(c,a.PY,CREATE,TARGET,specs['h1']['previous_runtime_root'],specs['h1']['GPU_UUID'],timeout=60))
  sf=c.open_sftp();sf.get_channel().settimeout(120)
  try:
   created={TARGET,TARGET+'/job0'}
   for p in sorted(Q.rglob('*')):
    if '__pycache__' in p.parts:continue
    rel=p.relative_to(Q).as_posix();remote=TARGET+'/'+rel
    if p.is_dir():
     if remote not in created:sf.mkdir(remote);created.add(remote)
    elif p.is_file():sf.put(str(p),remote)
  finally:sf.close()
  put('TARGET_COMPLETE_SOURCE_RUNTIME_INSTALLED_RSL_SDK_CPU_ACTUAL.json',a.code(c,a.PY,d.d.CPU,TARGET,timeout=180))
  code="from pathlib import Path;import sys,json;B=Path(sys.argv[1]);sys.path.insert(0,str(B));import three_slot_common_v1 as b;from h1_ce3_original_fp32_native_reuse_v1 import reuse_H1_native;s="+repr(specs['h1'])+";v=reuse_H1_native(s,b,B);assert b.valid_ready(dict(key='h1',phase='ready',native_GPU_waited_EXIT0=True,native_CPU=v,manifest_SHA=s['manifest_SHA']),s);print(json.dumps(dict(passed_exact_native_reuse_and_original_FP32_ready=True,native_CPU=v,no_GPU_or_raw_PT_hash_replay=True)))"
  put('TARGET_STRICT_CE3_NATIVE_ORIGINAL_FP32_REUSE_CPU_ACTUAL.json',a.code(c,a.PY,code,TARGET,timeout=180))
 finally:
  if c:c.close();c=None
 try:
  c=a.t.connect();put('ORIGINAL_OWNER_CURRENT_CANONICAL_COST0_FCNTL_HANDOFF_ACTUAL.json',a.code(c,a.t.PY,OWNER,SOURCE,timeout=60));sf=c.open_sftp()
  names=('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','owner_listener_ready_cpu_reviewed_v1.py')
  try:
   for n in names:sf.put(str(Q/n),SOURCE+'/'+n)
  finally:sf.close()
  put('ORIGINAL_OWNER_CONTROLLERS_EXACT_SHA_AST_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import json,hashlib,ast;B=Path("+repr(SOURCE)+");rows="+repr([dict(name=n,SHA=a.H(Q/n)) for n in names])+";[(ast.parse((B/r['name']).read_text('utf8')),None) for r in rows];assert all(hashlib.sha256((B/r['name']).read_bytes()).hexdigest()==r['SHA'] for r in rows);print(json.dumps(dict(passed=True,rows=rows)))"))
  cfg=dict(role='owner',experts=specs,run_id='CE3_ORIGINAL_FP32_CONTINUATION_'+str(time.time_ns()),token=secrets.token_hex(32));owner=launch(a.code,c,a.t.PY,SOURCE,'three_slot_finite_owner_v1.py',cfg);put('CE3_ORIGINAL_WRITER_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,no_GO_yet=True))
  put('CE3_ORIGINAL_WRITER_LISTENER_READY_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json;B=Path("+repr(SOURCE)+");sys.path.insert(0,str(B));from owner_listener_ready_cpu_reviewed_v1 import wait_actual;print(json.dumps(wait_actual(B,"+repr(owner['detached_pid'])+",20.)))",timeout=40))
  d.SOURCE=SOURCE;d.R=R;d.terminal(c,cfg,'e2');d.terminal(c,cfg,'recovery')
 finally:
  if c:c.close();c=None
 try:
  c=a.connect72(pw);pw=None;node=launch(a.code,c,a.PY,TARGET,'three_slot_finite_node_v1.py',dict(specs['h1'],role='node',run_id=cfg['run_id'],token=cfg['token']))
  put('CE3_ORIGINAL_FP32_SAME_SEGMENT_FINITE_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,node=node,source_owner_root=SOURCE,target_root=TARGET,source_SHA=specs['h1']['source_SHA'],Adam=646100,manifest_SHA=specs['h1']['manifest_SHA'],native_reused_same_source_backend_GPU_no_replay=True,original_FP32_reference_absolute1e4_restored=True,original_dual_FP64_false_and_failed_node_preserved=True,cap1800_headroom300_max24_start25GiB_savedstop8GiB=True,E2_E3_hold0worker0GO0charge=True,production_first_local_CPU_not_yet=True,stdin_only_HMAC_not_argv_log_or_file=True))
  print(json.dumps(dict(owner=owner,node=node,actual_detached=True,native_not_replayed=True,first_PPO_CPU_pending=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('CE3_ORIGINAL_FP32_DEPLOY_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),inspect_actual_before_any_retry_no_hotpatch=True));raise
