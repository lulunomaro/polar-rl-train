"""UNUSED closing purpose. Signed local+remote900 gate; no extra training.
Original owner terminal/raw fee once, all own wait-out, one new formal transfer.
"""
from pathlib import Path
import hashlib,importlib.util,json,os,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def read(p):return json.loads(Path(p).read_bytes())
def main():
 first=read(R/'ROOT194_FIRSTV2_ACTUAL_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED.json');assert first['passed'] and first['first']['actual_new_PPO_updates']==1
 original=read(R/'ROOT194_FIRSTV2_ORIGINAL72_OWNER_LAUNCH_ACTUAL.json');owner=original['owner'];spec=original['spec']
 current=read(R/'ROOT194_FIRSTV2_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST.json');go=current['owner_current']['go']['h1_210']
 assert go['run_id']==original['run_id'] and go['max_parent_seconds']==7500 and go['literal_jump194_400N50']
 assert go['nominal_end_epoch']-time.time()<=900,'Original signed local earliest900 not yet eligible'
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'collect194_original_formal_cost_normal900_UNUSED_once|start194_literal_JUMP_plane_single4090_FIRST|install194_literal_JUMP194_native_admission|capture194_target_|install_evaluate187_totalplan|collect_E3_source210|collect_ONE178_original' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT194_NORMAL900_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),self_PID=os.getpid(),self_exe=sys.executable,self_argv=sys.argv,exact_CIM=rows))
 put('ROOT194_NORMAL900_ONCE_CONSUMED.json',dict(epoch=time.time(),run_id=original['run_id'],original_owner=owner,original_signed_GO=go,original_owner_wait850=True,one_new_formal_transfer_only=True,no_model4999_or_old_models_or_raw_reads=True))
 wrapper=module('normal194_session',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('normal194_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret);secret=None
  code="""from pathlib import Path
import json,time,hashlib,fcntl,psutil
B=Path(v['owner']['root']);g=v['go'];assert g['nominal_end_epoch']-time.time()<=900
assert json.loads((B/'OWNER_IDENTITY.json').read_bytes())['pid']==v['owner']['pid']
limit=time.time()+850
while time.time()<limit and not (B/'OWNER_EXIT_ACTUAL.json').is_file():time.sleep(2)
assert (B/'COHORT_FINAL.json').is_file() and (B/'OWNER_EXIT_ACTUAL.json').is_file()
final=json.loads((B/'COHORT_FINAL.json').read_bytes());exit=json.loads((B/'OWNER_EXIT_ACTUAL.json').read_bytes())
assert final['original_cost_settled'] and exit['original_cost_settled']
def original_running(identity):
 try:
  p=psutil.Process(identity['pid'])
  if abs(p.create_time()-identity['creation'])>1e-6:return False
  return p.status()!=psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return False
while time.time()<limit and original_running(v['owner']):time.sleep(.5)
assert not original_running(v['owner'])
assert final['go']['h1_210']==g and final['rows']['h1_210']['terminal_all_own_children_waited']
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=p.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None
segments=[a for a in c['completed_segments'] if a.get('owner_parent_pid')==v['owner']['pid']];assert len(segments)==1
s=segments[0];x=s['experts']['h1_210'];assert x['started_epoch']==g['learning_started_epoch'] and x['ended_epoch']>=x['started_epoch'] and x['duration_bound_passed']
assert s['charged_expert_seconds']==x['charged_seconds']
locks=[]
try:
 for n in ['native_floor_supervisor.lock','autonomy_controller.lock']:
  f=(p.parent/n).open('rb+');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);locks.append(f)
finally:
 for f in locks:fcntl.flock(f,fcntl.LOCK_UN);f.close()
texts=[]
for q in sorted(B.iterdir()):
 if not q.is_file() or q.suffix not in ('.json','.log'):continue
 b=q.read_bytes();texts.append(dict(path=str(q),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
print(json.dumps(dict(passed=True,canonical_None=True,original_owner_segment=s,original_one_raw_fee=x['charged_seconds'],raw_fee_sum_once=x['charged_seconds'],closing_balance_snapshot=c['remaining_training_seconds'],original_GO=g,cohort_final=final,owner_exit=exit,original_owner_out_or_nonexecuting_zombie=True,owner_OS_exitcode_not_invented=True,shared_locks_free=True,full_UTF8=texts,no_ledger_write=True)))"""
  try:closed=d.code(client,d.PY72,code,dict(owner=owner,go=go),timeout=900);put('ROOT194_NORMAL900_ORIGINAL_OWNER_COST_CLOSED_ACTUAL.json',closed)
  finally:client.close();client=None
  client=route.connect()
  collect="""from pathlib import Path
import fcntl,hashlib,json,time,psutil
B=Path(v['job']);C=B/'control';limit=time.time()+180
while time.time()<limit and not (C/'NODE_EXIT_ACTUAL.json').is_file():time.sleep(2)
assert (C/'NODE_TERMINAL_ACTUAL.json').is_file() and (C/'NODE_EXIT_ACTUAL.json').is_file()
t=json.loads((C/'NODE_TERMINAL_ACTUAL.json').read_bytes());e=json.loads((C/'NODE_EXIT_ACTUAL.json').read_bytes());assert e['all_own_children_waited'] and e['private_EX_released']
identity=json.loads((C/'NODE_IDENTITY.json').read_bytes())
def original_running(identity):
 try:
  p=psutil.Process(identity['pid'])
  if abs(p.create_time()-identity['creation'])>1e-6:return False
  return p.status()!=psutil.STATUS_ZOMBIE
 except psutil.NoSuchProcess:return False
while time.time()<limit and original_running(identity):time.sleep(.5)
assert not original_running(identity)
lock=Path('/mnt/mod4_linux_durable_20261013/H125_1710n1/OWN_SOURCE_GPU_NATIVE_ONLY.lock').open('rb+');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
texts=[];models=[]
for root in [C,B/'production']:
 for p in sorted(root.rglob('*')):
  if not p.is_file() or any(x in p.relative_to(root).parts for x in ('kit_isolation',)):continue
  if p.suffix=='.pt':models.append(dict(path=str(p),bytes=p.stat().st_size,SHA='producer index only; do not hash other checkpoints'));continue
  if p.suffix not in ('.json','.log'):continue
  b=p.read_bytes();texts.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8','replace')))
final=json.loads((B/'production/FINAL.json').read_bytes()) if (B/'production/FINAL.json').is_file() else None
errors=[str(p) for p in (B/'production').glob('*ERROR*.json')]
qualified=bool(t['row']['returncode']==0 and not t['row']['original_error'] and final and final.get('passed') and not errors)
formal=None
if qualified:
 formal=final['final'];p=Path(formal['path']);assert p.is_relative_to(B/'production') and p.stat().st_size==formal['bytes']
 with p.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 assert sha==formal['SHA'];formal=dict(formal,actual_completed_source_host_SHA=sha)
print(json.dumps(dict(passed_collection=True,qualified_formal=qualified,formal=formal,original_node_terminal=t,original_node_exit=e,original_node_out_or_nonexecuting_zombie=True,node_OS_exitcode_not_invented=True,private_EX_free=True,errors=errors,full_UTF8=texts,other_model_metadata_only=models,no_learner_or_actor_or_ledger_calls=True)))"""
  result=d.code(client,route.PY,collect,dict(job=spec['job_root']),timeout=210)
  put('ROOT194_NORMAL900_ORIGINAL_NODE_AND_COMPLETE_UTF8_ACTUAL.json',result)
  transfer=None
  if result['qualified_formal']:
   f=result['formal'];dest=N/'current_closed194_models/h1_210/formal/model_final.pt';dest.parent.mkdir(parents=True,exist_ok=False)
   sf=client.open_sftp()
   try:sf.get(f['path'],str(dest))
   finally:sf.close()
   with dest.open('rb') as stream:sha=hashlib.file_digest(stream,'sha256').hexdigest()
   assert dest.stat().st_size==f['bytes'] and sha==f['SHA']
   transfer=dict(source=f['path'],path=str(dest),bytes=f['bytes'],SHA=sha,transfers=1,two_host_SHA_equal=True)
  put('ROOT194_COMPLETE_FINAL_OR_FAILURE_ORIGINAL_COST_RETURNED_ACTUAL.json',dict(passed_collection=True,run_id=original['run_id'],owner_closed=closed,source_node=result,formal=transfer,initial_CPU_not_yet_run=True,actual270_skill_not_inferred=True))
  print(json.dumps(dict(qualified_formal=result['qualified_formal'],formal=transfer,raw_fee_sum_once=closed['raw_fee_sum_once'],closing_balance_snapshot=closed['closing_balance_snapshot'])),flush=True)
 finally:
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT194_NORMAL900_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT194_NORMAL900_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_or_automatic_model_promotion=True));raise
