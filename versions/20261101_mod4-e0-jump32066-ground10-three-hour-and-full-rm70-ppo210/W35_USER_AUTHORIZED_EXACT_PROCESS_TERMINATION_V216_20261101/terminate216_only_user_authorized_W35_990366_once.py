"""Human explicitly authorized only original W35 fault PID990366 termination."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';R.mkdir(exist_ok=True)
S=T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031';F=T/'W35_MATERIAL_FAILURE_OWNED_STOP_V215_20261101'
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False,ensure_ascii=False)
def module(name,p):
 q=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(q);sys.modules[name]=m;q.loader.exec_module(m);return m
CODE="""from pathlib import Path
import fcntl,json,psutil,signal,time,hashlib
O=Path(v['owner']['root']);J=Path(v['spec']['job_root']);C=J/'control210v2';P=J/'production'
canonical=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());cur=json.loads((O/'OWNER_CURRENT.json').read_bytes())
assert canonical['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and canonical['active_segment']['owner_parent_pid']==v['owner']['pid']
assert cur['go']==v['go'] and json.loads((O/'OWNER_IDENTITY.json').read_bytes())['creation']==v['owner']['creation']
x=v['worker'];assert x['pid']==990366 and x['creation']==1793463868.49
def get_original():
 try:p=psutil.Process(x['pid'])
 except psutil.NoSuchProcess:return None
 if p.create_time()!=x['creation']:raise RuntimeError('PID reused; no signal authorized')
 if p.status()==psutil.STATUS_ZOMBIE:return None
 assert p.exe()==x['exe'] and p.cmdline()==x['argv'] and p.cwd()==x['root']
 assert str(J/'runtime/isaac/mod4/worker_full208_v3.py') in p.cmdline()
 return p
first_exists=(P/'FIRST_ACTUAL_NEW_PPO_UPDATE.json').is_file()
actions=[];p=get_original()
if p is not None:
 p.send_signal(signal.SIGTERM);actions.append(dict(epoch=time.time(),signal='SIGTERM',pid=x['pid'],creation=x['creation']))
 end=time.time()+30
 while time.time()<end and get_original() is not None:time.sleep(1)
 p=get_original()
 if p is not None:
  p.send_signal(signal.SIGKILL);actions.append(dict(epoch=time.time(),signal='SIGKILL',pid=x['pid'],creation=x['creation'],human_exact_process_termination_authorized=True))
end=time.time()+180
while time.time()<end and (get_original() is not None or not (C/'NODE_EXIT_ACTUAL.json').is_file()):time.sleep(2)
worker_out=get_original() is None
node_exit=json.loads((C/'NODE_EXIT_ACTUAL.json').read_bytes()) if (C/'NODE_EXIT_ACTUAL.json').is_file() else None
node_terminal=json.loads((C/'NODE_TERMINAL_ACTUAL.json').read_bytes()) if (C/'NODE_TERMINAL_ACTUAL.json').is_file() else None
private_free=False
if node_exit and node_exit.get('all_own_children_waited') and node_exit.get('private_EX_released'):
 with Path(v['spec']['private_lock']).open('rb+') as lock:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lock,fcntl.LOCK_UN)
 private_free=True
cur=json.loads((O/'OWNER_CURRENT.json').read_bytes());assert cur['go']==v['go']
texts=[];models=[]
for root in (C,P):
 for path in sorted(root.rglob('*')):
  if not path.is_file() or 'kit_isolation' in path.relative_to(root).parts:continue
  if path.suffix=='.pt':models.append(dict(path=str(path),bytes=path.stat().st_size,SHA='existing producer or unknown; no model read'));continue
  if path.suffix in ('.json','.log'):
   raw=path.read_bytes();texts.append(dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))
print(json.dumps(dict(epoch=time.time(),passed_exact_process_control=worker_out and private_free,worker_out=worker_out,only_signalled_original_PID990366=True,
 actions=actions,first_PPO_present_before_termination=first_exists,original_node_exit=node_exit,original_node_terminal=node_terminal,private_EX_free=private_free,
 E0_not_signalled_or_written=True,current_owner_rows=cur['rows'],canonical_write=False,old_models_or_raw_read=0,full_UTF8=texts,models_metadata_only=models)))
"""
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True);a=parser.parse_args();assert a.root_lease_label.startswith('ROOT216_EXCLUSIVE_AUTHORIZED_TERMINATE_')
 assert read(F/'reports/ROOT215_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 fail=read(F/'reports/ROOT215_ORIGINAL_W35_STARTUP_STOP_AND_FULL_ERRORS_RETURNED_ACTUAL.json');assert fail['startup_only_no_first_PPO'] and fail['original_worker_still_executing']
 launch=read(S/'reports/ROOT210_ORIGINAL_UNIFIED_OWNER_LAUNCH_ACTUAL.json');state=read(S/'reports/ROOT210_UNIFIED_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json')
 worker=state['current']['rows']['w35_72']['worker'];assert worker['pid']==990366
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'terminate216_only_user_authorized_W35_990366_once|stop215_exact_|launch210_|collect210_|prepare212_|install211_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];others=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ROOT216_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,others=others))
 assert len(own)==1 and own[0]['ExecutablePath'].lower()==sys.executable.lower() and own[0]['CreationDate'] and not others
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT216_HUMAN_EXACT_AUTHORIZATION_AND_ONCE_PURPOSE.json',dict(epoch=time.time(),human_exact_reply='授权只终止W35故障进程',question_scope='Only verified original W35 PID990366; E0 three-hour training untouched',
  verified_worker=worker,root_lease_label=a.root_lease_label,allowed_signals='SIGTERM then only if necessary SIGKILL, to this exact PID+creation+exe+argv+cwd only',
  no_group_other_PID_driver_or_lock_delete=True,canonical_writes=0,model_raw_reads=0,original_node_must_wait_and_release=True))
 wrapper=module('terminate216_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py');sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('terminate216_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  result=d.code(client,d.PY72,CODE,dict(owner=launch['owner'],spec=launch['specs']['w35_72'],go=state['current']['go'],worker=worker),timeout=270)
  put('ROOT216_EXACT_W35_TERMINATION_AND_ORIGINAL_NODE_WAIT_RETURNED_ACTUAL.json',result)
  print(json.dumps(dict(passed=result['passed_exact_process_control'],worker_out=result['worker_out'],private_EX_free=result['private_EX_free'],actions=result['actions'],node_exit=result['original_node_exit'],E0_untouched=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT216_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT216_LOCAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_replay=True));raise
