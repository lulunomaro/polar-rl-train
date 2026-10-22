from pathlib import Path
import hashlib, importlib.util, json, secrets, sys, time, traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

H1_INSTALL=d.INSTALL.replace("key=='e2'", "key=='h1'").replace("key!='e2'", "key!='h1'").replace("assert int(line.split(',')[-1])>7000", "assert int(line.split(',')[-1])>15669")
H1_INSTALL=H1_INSTALL.replace("assert not B.exists();B.mkdir", """
mount=subprocess.check_output(['findmnt','-n','-o','UUID,FSTYPE,OPTIONS','--target',str(owned)],text=True).strip()
assert 'EF3105C85DD986BD' in mount.upper() and 'ntfs3' in mount and 'rw' in mount.split()[-1].split(',')
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());previous_owner=Path(v['previous_owner'])
assert c['active_segment'] is None and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8 and c['remaining_training_seconds']>82512.86069250107
assert json.loads((previous_owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled'] and json.loads((previous_owner/'COHORT_FINAL.json').read_bytes())['original_cost_settled']
assert not any(p.pid!=os.getpid() and any(x.startswith(str(previous_owner)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for lock in (C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
assert not B.exists();B.mkdir""")
def install_h1(c,q):
 spec=q['specs']['h1'];root=q['roots']['h1'];local=Path(q['payloads']['h1'])
 manifest=json.loads((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
 result=d.code(c,d.t.PY,H1_INSTALL,dict(root=root,spec=spec,manifest=manifest,source=q['sources']['h1'],previous_owner=q['previous_owner_root']),timeout=120)
 put('H1_FRESH_RESOURCE_UNUSED_ROOT_SOURCE_INSTALL_ACTUAL.json',result)
 sf=c.open_sftp();sf.get_channel().settimeout(90)
 try:
  for row in result['need_upload']:sf.put(str(local/row['relative']),root+'/'+row['relative'])
  sf.put(str(local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
 finally:sf.close()
 cpu=d.code(c,d.t.PY,"import runpy,sys;sys.argv=['target_H1_step270_closed_source_sdk_cpu_review_v1.py',v['root']];runpy.run_path(v['root']+'/target_H1_step270_closed_source_sdk_cpu_review_v1.py',run_name='__main__')",dict(root=root),timeout=240)
 put('H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json',cpu)
 admitted=d.code(c,d.t.PY,"from pathlib import Path;import sys,json;sys.path.insert(0,v['root']);from closed_production_continuation_CPU_v2 import load;print(json.dumps(load(v['spec'],Path(v['root']))))",dict(root=root,spec=spec),timeout=90)
 put('H1_CLOSED_SAME_STEP270_PHASE_PRODUCTION_CPU_ADMITTED_ACTUAL.json',admitted)
 owner_ready=d.code(c,d.t.PY,"from pathlib import Path;import sys,json;sys.path.insert(0,v['root']);from three_slot_common_v1 import valid_ready;q=v['admitted'];s=v['spec'];row=dict(key='h1',phase='ready',closed_source_CPU=q,manifest_SHA=s['manifest_SHA'],original_error=False);assert s['reward_migration'] and valid_ready(row,s);print(json.dumps(dict(passed=True,original_valid_ready_actual_CPU=True,kind=q['value']['kind'],controller_unchanged=True)))",dict(root=root,spec=spec,admitted=admitted),timeout=60)
 put('H1_INSTALLED_ORIGINAL_OWNER_REWARD_MIGRATION_VALID_READY_CPU_ACTUAL.json',owner_ready)


OWNER_CPU="from pathlib import Path\nimport ast,hashlib,json\nB=Path(v['root']);old=(Path(v['reference'])/'three_slot_finite_owner_v1.py').read_text('utf8');s=(B/'three_slot_finite_owner_v1.py').read_text('utf8');assert hashlib.sha256(s.encode()).hexdigest()==v['scheduler']['owner_SHA']\nfor a,z in reversed(v['scheduler']['changes']):s=s.replace(z,a)\nassert ast.dump(ast.parse(s))==ast.dump(ast.parse(old))\nassert (B/'three_slot_common_v1.py').read_bytes()==(Path(v['reference'])/'three_slot_common_v1.py').read_bytes()\nprint(json.dumps(dict(passed=True,original_account_auth_AST_exact=True,reserve7800=True,no_ledger_write_or_GO=True)))"
def main():
 q=json.loads((R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes());receipt=json.loads((R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').read_bytes());scheduler=json.loads((R/'H1_ONLY_ORIGINAL_ACCOUNT_SCHEDULER_CPU_ACTUAL.json').read_bytes())
 assert scheduler['passed'] and scheduler['admission_reserve_seconds']==7800 and set(q['specs'])=={'h1'}
 put('H1_ONLY_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),source=q['sources'],E3_no_GO_resource_deferred=True,reserve7800=True));c=d.t.connect();cfg=None
 try:
  install_h1(c,q)
  boundary=d.code(c,d.t.PY,d.OWNER,dict(root=q['owner_root'],receipt=receipt),timeout=90);put('H1_ONLY_FRESH_ORIGINAL_CANONICAL_LOCKS_ACTUAL.json',boundary)
  sf=c.open_sftp()
  try:
   for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py'):sf.put(str(N/'controllers'/name),q['owner_root']+'/'+name)
  finally:sf.close()
  remote=d.code(c,d.t.PY,OWNER_CPU,dict(root=q['owner_root'],reference='/mnt/mod4_linux_durable_20261013/H1step270_rewardmigration_2210v18/owner',scheduler=scheduler),timeout=60);put('H1_ONLY_INSTALLED_OWNER_ACCOUNT_AUTH_AST_CPU_ACTUAL.json',remote)
  cfg=dict(role='owner',experts=q['specs'],scheduling_authority='human_requested_available_experts',deferred_experts=['e2','recovery'],run_id='H1_REWARD_E3_RESOURCE_DEFERRED_ORIGINAL_'+str(time.time_ns()),token=secrets.token_hex(32))
  owner=d.launch(c,d.t.PY,q['owner_root'],'three_slot_finite_owner_v1.py',cfg)
  ready=d.code(c,d.t.PY,"from pathlib import Path;import json,socket,time;B=Path(v['root']);until=time.monotonic()+20\nwhile not (B/'OWNER_IDENTITY.json').exists():\n assert time.monotonic()<until;time.sleep(.1)\nwith socket.create_connection(('10.24.4.210',29754),timeout=5):pass\nprint(json.dumps(dict(owner=json.loads((B/'OWNER_IDENTITY.json').read_bytes()),listener_ready=True)))",dict(root=q['owner_root']),timeout=30);put('H1_ONLY_OWNER_ACTUAL_READY.json',ready)
  node=d.launch(c,d.t.PY,q['roots']['h1'],'three_slot_finite_node_v1.py',dict(q['specs']['h1'],role='node',run_id=cfg['run_id'],token=cfg['token']))
  result=dict(epoch=time.time(),owner=owner,owner_identity=ready['owner'],nodes=dict(h1=node),roots=q['roots'],owner_root=q['owner_root'],specs=q['specs'],sources=q['sources'],run_id=cfg['run_id'],E3_no_GO_resource_deferred=True,reserve_seconds=7800,not_learning_until_actual_GO_PPO=True)
  put('H1_ONLY_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json',result);print(json.dumps(dict(owner=owner,node=node,not_learning_until_GO_PPO=True)))
 finally:
  if cfg:cfg.clear()
  c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('H1_ONLY_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_same_root_or_refund=True));raise
