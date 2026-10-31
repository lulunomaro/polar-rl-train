"""OriginalW35 startup-only graceful interrupt after actual64K material failure.
E0 is untouched. No new writer/model/raw/hash/kill/lock deletion occurs.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';R.mkdir(exist_ok=True)
S=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,p):
 q=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(q);sys.modules[name]=m;q.loader.exec_module(m);return m
CODE="""from pathlib import Path
import json,psutil,signal,time,hashlib
O=Path(v['owner']['root']);J=Path(v['spec']['job_root']);C=J/'control210v2';P=J/'production'
canonical=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());current=json.loads((O/'OWNER_CURRENT.json').read_bytes())
assert canonical['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and canonical['active_segment']['owner_parent_pid']==v['owner']['pid']
assert json.loads((O/'OWNER_IDENTITY.json').read_bytes())['creation']==v['owner']['creation'] and current['go']==v['go']
expected=v['worker'];p=psutil.Process(expected['pid'])
def same(p):
 return p.create_time()==expected['creation'] and p.exe()==expected['exe'] and p.cmdline()==expected['argv'] and p.cwd()==expected['root']
assert same(p) and str(J/'runtime/isaac/mod4/worker_full208_v3.py') in p.cmdline() and p.status()!=psutil.STATUS_ZOMBIE
stop=P/'STOP_AFTER_SAVE.json';assert not stop.exists()
stop.write_text(json.dumps(dict(epoch=time.time(),reason='Root actual215: original W35 startup PhysX64K material limit, original saved source immutable; stop only this role after complete save if any PPO'),indent=2))
actions=[dict(epoch=time.time(),action='original_STOP_AFTER_SAVE_interface',path=str(stop),worker=expected)]
deadline=time.time()+15
while time.time()<deadline and p.is_running() and p.status()!=psutil.STATUS_ZOMBIE and not (C/'NODE_EXIT_ACTUAL.json').is_file():time.sleep(1)
startup_only=not (P/'FIRST_ACTUAL_NEW_PPO_UPDATE.json').exists()
if startup_only and p.is_running() and p.status()!=psutil.STATUS_ZOMBIE and not (C/'NODE_EXIT_ACTUAL.json').is_file():
 assert same(p)
 # One Python KeyboardInterrupt, invoking the worker's original exception/
 # App.close finally. No SIGTERM/SIGKILL, process-group or unknown PID action.
 p.send_signal(signal.SIGINT);actions.append(dict(epoch=time.time(),action='single_SIGINT_to_original_verified_startup_only_worker',new_PPO_first_present=False))
deadline=time.time()+180
while time.time()<deadline and not (C/'NODE_EXIT_ACTUAL.json').is_file():time.sleep(2)
node_exit=json.loads((C/'NODE_EXIT_ACTUAL.json').read_bytes()) if (C/'NODE_EXIT_ACTUAL.json').is_file() else None
terminal=json.loads((C/'NODE_TERMINAL_ACTUAL.json').read_bytes()) if (C/'NODE_TERMINAL_ACTUAL.json').is_file() else None
def alive(x):
 try:q=psutil.Process(x['pid']);return q.create_time()==x['creation'] and q.status()!=psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return False
worker_still_executing=alive(expected)
texts=[];models=[]
for root in (C,P):
 for path in sorted(root.rglob('*')):
  if not path.is_file() or 'kit_isolation' in path.relative_to(root).parts:continue
  if path.suffix=='.pt':models.append(dict(path=str(path),bytes=path.stat().st_size,SHA='existing producer or unknown; no model read'));continue
  if path.suffix in ('.json','.log'):
   raw=path.read_bytes();texts.append(dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
current=json.loads((O/'OWNER_CURRENT.json').read_bytes())
assert current['go']==v['go']
print(json.dumps(dict(epoch=time.time(),passed_control_scope=True,actions=actions,verified_original_worker=expected,
 startup_only_no_first_PPO=startup_only,original_worker_still_executing=worker_still_executing,original_node_exit=node_exit,original_node_terminal=terminal,
 original_W35_training_success=False,E0_not_signalled_or_modified=True,current_owner_rows=current['rows'],full_UTF8=texts,models_metadata_only=models,
 no_account_write_or_model_or_raw_read=True)))
"""
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True);a=parser.parse_args();assert a.root_lease_label.startswith('ROOT215_EXCLUSIVE_OWNED_STOP_')
 previous=read(S/'reports/ROOT210_PARALLEL_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json');assert previous['global_serial_control_client_lease']=='FREE'
 first=read(S/'reports/ROOT210_W35_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json');assert not first['passed']
 log=first['original_stdout_prefix'];assert 'PxPhysics::createMaterial: limit of 64K materials reached' in log['UTF8']
 launch=read(S/'reports/ROOT210_ORIGINAL_UNIFIED_OWNER_LAUNCH_ACTUAL.json');state=read(S/'reports/ROOT210_UNIFIED_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
 expected=state['current']['rows']['w35_72']['worker'];assert expected['pid']==990366 and expected['creation']==1793463868.49
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'stop215_exact_owned_W35_material_failure_once|launch210_|collect210_|prepare212_|install211_|install209_|launch209_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);cim=json.loads(p.stdout) if p.stdout.strip() else [];cim=cim if isinstance(cim,list) else [cim]
 own=[x for x in cim if x['ProcessId']==os.getpid()];others=[x for x in cim if x['ProcessId']!=os.getpid()]
 put('ROOT215_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=cim,other_known_control_finites=others))
 assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower() and own[0]['CreationDate'] and not others
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT215_OWNED_STOP_PURPOSE_ONCE_CONSUMED.json',dict(epoch=time.time(),root_lease_label=a.root_lease_label,actual_material_error_source=log['path'],actual_material_error_source_SHA=log['SHA'],
  verified_original_worker=expected,one_original_STOP_interface_then_only_if_no_first_PPO_one_SIGINT=True,NO_SIGTERM_SIGKILL_or_unknown_PID_or_process_group=True,
  full_source_checkpoint_immutable=True,E0_not_modified=True,canonical_writes=0,model_raw_reads=0,maximum_node_wait_seconds=180))
 wrapper=module('owned215_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;prior=None;secret=None
 try:
  transport,prior=wrapper.install();sec=module('owned215_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  result=d.code(client,d.PY72,CODE,dict(owner=launch['owner'],spec=launch['specs']['w35_72'],go=state['current']['go'],worker=expected),timeout=240)
  put('ROOT215_ORIGINAL_W35_STARTUP_STOP_AND_FULL_ERRORS_RETURNED_ACTUAL.json',result)
  print(json.dumps(dict(passed_control_scope=result['passed_control_scope'],startup_only=result['startup_only_no_first_PPO'],worker_still_executing=result['original_worker_still_executing'],node_exit=result['original_node_exit'],E0_untouched=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=prior
  put('ROOT215_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is prior,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT215_LOCAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_replay=True));raise
