"""Finish only the verified pre-owner upload interruption, never repeat original deploy."""
from pathlib import Path
import sys, os, json, time, getpass, secrets, traceback
import deploy_human_approved_ce3_new_native_then_one_finite1800_once as d
B=d.B; R=d.R; Q=d.Q; a=d.a; SOURCE=d.SOURCE; TARGET=d.TARGET
PRIOR=B.parent/'paid_mean_public4_v2'

TARGET_CHECK=r'''
from pathlib import Path
import sys,json,time,psutil,fcntl,subprocess,shutil,hashlib,os
B=Path(sys.argv[1]);m=sys.argv[2];gpu=sys.argv[3]
assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==m
v=json.loads((B/'TARGET_FULL_SOURCE_INSTALLED_RSL_SDK_CPU_ADMITTED_ACTUAL.json').read_bytes());assert v['passed_CPU_only'] and v['manifest_SHA']==m
assert not any((B/n).exists() for n in ('NODE_IDENTITY.json','node_CONSOLE.log','GO_PRODUCTION.json','job0/native','job0/production'))
alive=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=os.getpid() and any(s.startswith(str(B)+'/') for s in p.info['cmdline'] or []):alive.append(p.info)
 except psutil.Error:pass
assert not alive,alive
for p in (B.parents[1]/'state'/('three_expert_v2_'+gpu+'.lock'),B.parents[1]/'state/finite_environment_validation.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits']).decode();assert not any(gpu in x for x in compute.splitlines()),compute
assert shutil.disk_usage(B).free>25*1024**3 and psutil.virtual_memory().available>8*1024**3
print(json.dumps(dict(epoch=time.time(),existing_full_CPU_receipt_exact=True,actual_no_node_worker_native_GO=True,private_shared_fcntl_free=True,compute=compute)))
'''
SOURCE_CHECK=r'''
from pathlib import Path
import sys,json,time,psutil,fcntl,socket,hashlib,os
B=Path(sys.argv[1]);expected=json.loads(sys.argv[2]);assert os.path.ismount(B.parents[1])
assert not any((B/n).exists() for n in ('OWNER_IDENTITY.json','owner_CONSOLE.log','OWNER_CURRENT.json','COHORT_FINAL.json'))
alive=[]
for p in psutil.process_iter(['pid','create_time','cmdline']):
 try:
  if p.pid!=os.getpid() and any(s.startswith(str(B)+'/') for s in p.info['cmdline'] or []):alive.append(p.info)
 except psutil.Error:pass
assert not alive,alive
for r in expected:
 p=B/r['name'];assert p.is_file() and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']
old=B.parents[1]/'H1mp_1810p2/owner';assert json.loads((old/'COHORT_FINAL.json').read_bytes())['original_cost_settled'] and json.loads((old/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());assert c['active_segment'] is None and c['authorized_training_seconds']==1188000 and len(c['budget_extensions'])==7
for p in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
with socket.socket() as s:s.bind(('10.24.4.210',29754))
print(json.dumps(dict(epoch=time.time(),partial_three_uploaded_files_SHA_exact=True,no_actual_owner_or_GO=True,original_activeNone_two_fcntl_free=True,previous_cost_settled=True,no_account_write=True)))
'''

def main():
 prep=json.loads((R/'HUMAN_APPROVED_CE3_PREPARED_PAYLOAD_BOUND_DEPLOY_SPEC_ACTUAL.json').read_bytes());grant=json.loads((R/'HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json').read_bytes());assert a.H(R/'HUMAN_EXPLICIT_CE3_SINGLE_FINITE_APPROVAL_ACTUAL.json')==prep['approval_SHA'] and grant['explicit_human_grant_received'] and grant['no_following_window_authorization'];specs=prep['specs'];assert specs['h1']['source_SHA']==grant['source_SHA'] and specs['h1']['source_Adamstep']==646100
 listener=PRIOR/'owner_listener_ready_cpu_reviewed_v1.py';assert listener.is_file()
 original=B.parent.parent/'MOD4_H1_CLOSED24_TARGET72_SAME_SCOPE_FINITE_20261017/owner_listener_ready_cpu_reviewed_v1.py';assert a.H(listener)==a.H(original)
 d.put('CE3_PREOWNER_PARTIAL_V2_FINISH_STARTED_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),argv=sys.argv,original_preowner_error_preserved=True,only_missing_listener_not_old_deployer_reexecution=True,exclusive_transport_only_while_actual_CIM_alive=True))
 pw=getpass.getpass('Host72 finish approved pre-owner upload (hidden): ');c=None;cfg=None
 try:
  c=a.connect72(pw);d.put('CE3_V2_EXISTING_TARGET_CPU_NO_WORKER_ACTUAL.json',a.code(c,a.PY,TARGET_CHECK,TARGET,specs['h1']['manifest_SHA'],specs['h1']['GPU_UUID'],timeout=60))
 finally:
  if c:c.close();c=None
 try:
  c=a.t.connect();rows=[dict(name=n,SHA=a.H(Q/n)) for n in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py')];d.put('CE3_V2_SOURCE_PARTIAL_NO_OWNER_NO_GO_FCNTL_ACTUAL.json',a.code(c,a.t.PY,SOURCE_CHECK,SOURCE,json.dumps(rows),timeout=60))
  sf=c.open_sftp()
  try:
   try:sf.stat(SOURCE+'/'+listener.name)
   except FileNotFoundError:sf.put(str(listener),SOURCE+'/'+listener.name)
   else:raise AssertionError('Missing-listener finisher requires unused listener upload')
  finally:sf.close()
  rows.append(dict(name=listener.name,SHA=a.H(listener)))
  d.put('CE3_V2_ALL_FOUR_SOURCE_CONTROLLERS_SHA_AST_ACTUAL.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json,hashlib,ast;B=Path(sys.argv[1]);rows=json.loads(sys.argv[2]);assert all(hashlib.sha256((B/r['name']).read_bytes()).hexdigest()==r['SHA'] for r in rows);[ast.parse((B/r['name']).read_text('utf8')) for r in rows];print(json.dumps(dict(passed=True,files=rows)))",SOURCE,json.dumps(rows),timeout=40))
  cfg=dict(role='owner',experts=specs,run_id='H1_CE3_EXPLICIT_HUMAN_SINGLE_FINITE_'+str(time.time_ns()),token=secrets.token_hex(32));owner=d.launch(a.code,c,a.t.PY,SOURCE,'three_slot_finite_owner_v1.py',cfg);d.put('CE3_V2_ORIGINAL_OWNER_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,no_GO_yet=True))
  d.put('CE3_V2_SOURCE_LISTENER_ACTUAL_READY.json',a.code(c,a.t.PY,"from pathlib import Path;import sys,json;B=Path("+repr(SOURCE)+");sys.path.insert(0,str(B));from owner_listener_ready_cpu_reviewed_v1 import wait_actual;print(json.dumps(wait_actual(B,"+repr(owner['detached_pid'])+",20.)))",timeout=40));d.terminal(c,cfg,'e2');d.terminal(c,cfg,'recovery')
 finally:
  if c:c.close();c=None
 try:
  c=a.connect72(pw);pw=None;node=d.launch(a.code,c,a.PY,TARGET,'three_slot_finite_node_v1.py',dict(specs['h1'],role='node',run_id=cfg['run_id'],token=cfg['token']))
  d.put('HUMAN_APPROVED_CE3_OWN_NEW_NATIVE_SINGLE_FINITE_CHAIN_DETACHED_ACTUAL.json',dict(epoch=time.time(),owner=owner,node=node,source_owner_root=SOURCE,h1root=TARGET,source_SHA=specs['h1']['source_SHA'],source_Adam=646100,approval_SHA=prep['approval_SHA'],own_new_native180_and_independent_CPU_required_before_GO=True,one_finite1800_headroom300_max24_free8GiB_start25GiB=True,E2_E3_hold_zero_worker_GO_charge=True,no_following_window_authorized=True,original_single_writer_actual_interval_once=True,actual_detached_not_yet_native_or_first_CPU=True,stdin_only_HMAC_not_saved_or_argv=True))
  print(json.dumps(dict(owner=owner,node=node,own_new_ce3_native_chain_dispatched=True,not_yet_native_CPU_or_PPO=True)),flush=True)
 finally:
  pw=None
  if cfg:cfg.clear()
  if c:c.close()

if __name__=='__main__':
 try:main()
 except BaseException:d.put('CE3_V2_FINISH_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),actual_inspection_before_any_retry_no_GPU_replay=True));raise
