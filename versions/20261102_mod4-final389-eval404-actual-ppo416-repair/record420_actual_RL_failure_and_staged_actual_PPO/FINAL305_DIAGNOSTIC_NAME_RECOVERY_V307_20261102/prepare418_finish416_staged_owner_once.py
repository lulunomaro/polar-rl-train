"""Prepare independent418 dispatch of staged416, original launcher stays consumed."""
from pathlib import Path
import ast
import hashlib
import json
import time

P=Path(__file__).resolve().parent;T=P.parent
N=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102'
C=T/'RL416_STAGED_FIRST_OWNER_RECOVERY_V418_20261102'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
assert not C.exists();C.mkdir();(C/'reports').mkdir()
assert(N/'reports/ROOT416_START_ONCE_CONSUMED_BEFORE_NETWORK.json').exists()
assert not(N/'reports/ROOT416_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').exists()
assert not(N/'reports/ROOT416_ORIGINAL_NODE_LAUNCH_ACTUAL.json').exists()
failure=json.loads((N/'reports/ROOT416_START_ORIGINAL_CALLER_ERROR_1793602324719070900.json').read_bytes())
assert 'FRESH_AUTHORITY_BEFORE_OWNER' in failure['error']
task=json.loads((N/'TASK416_FROZEN.json').read_bytes())
code='''"""First originalowner/node launch for staged416; distinct418 recovery, no replay."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,secrets,subprocess,sys,time,traceback
C=Path(__file__).resolve().parent;T=C.parent;W=T.parent
N=T/'RL_ACTUAL_RESIDUAL_PPO_PRODUCTION_V416_20261102';R=N/'reports'
H=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
read=lambda path:json.loads(path.read_bytes())
def put(name,value):
 with(R/name).open('x',encoding='utf8')as stream:json.dump(value,stream,indent=2,allow_nan=False)
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def main():
 assert sys.version_info[:2]==(3,14)
 p=argparse.ArgumentParser();p.add_argument('--caller-index-SHA',required=True);args=p.parse_args()
 index=C/'INDEX418_STAGED_OWNER_RECOVERY_FROZEN.json';assert H(index)==args.caller_index_SHA
 for row in read(index)['files']:
  path=Path(row['path']);assert path.stat().st_size==row['bytes']and H(path)==row['SHA']
 assert not(R/'ROOT418_STAGED_FIRST_OWNER_ONCE_CONSUMED.json').exists()
 assert not(R/'ROOT416_ORIGINAL_OWNER_LAUNCH_ACTUAL.json').exists()and not(R/'ROOT416_ORIGINAL_NODE_LAUNCH_ACTUAL.json').exists()
 original=module('inert416launcher',N/'launch416_actual_residual_RL_once.py')
 protocol=module('protocol416',N/'teacher_task416.py')
 frozen=N/'INDEX416_SOURCE_TASK_CALLERS_FROZEN.json'
 for row in read(frozen)['files']:
  path=Path(row['path']);assert path.stat().st_size==row['bytes']and H(path)==row['SHA']
 task=read(N/'TASK416_FROZEN.json');protocol.validate_task(task)
 staged=read(R/'ROOT416_ACTUAL_TASK_MANIFEST_READY_SCHEDULE.json');spec=staged['schedule']['experts']['jump_72'];assert staged['run_id']==task['run_id']
 pattern='MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021|RMPOLAR|watch_|collect_generic|run_once_after_resume|prepare_archive|single_gpu|collect_nine|collect_e1|E1_actual|PAIR1|PAIR2|PAIR3|PAIR4'
 query="Get-CimInstance Win32_Process -Filter \\"Name='python.exe' OR Name='ssh.exe'\\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Compress"
 out=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(out.stdout)if out.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()
 assert rows[0]['ExecutablePath'].replace(chr(92),'/').lower()==sys.executable.replace(chr(92),'/').lower()
 put('ROOT418_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),rows=rows,serial_before='FREE'))
 put('ROOT418_STAGED_FIRST_OWNER_ONCE_CONSUMED.json',dict(epoch=time.time(),run=task['run_id'],original416launchrefusalpreserved=True,no_replay_oldlaunch=True,modelreads=0))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 remote=module('remote418',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_payloads.py')
 light=module('light418',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_additions.py')
 transport=previous=client=secret=None
 try:
  transport,previous=module('transport418',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install()
  secret=module('memory418',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover()
  client=d.connect72(secret);secret=None
  put('ROOT418_FRESH_AUTHORITY_BEFORE_FINISH.json',d.code(client,d.PY72,remote.AUTH,{},timeout=45))
  verify="""from pathlib import Path
import hashlib,json
J=Path(v['task']['job_root']);O=Path(v['task']['owner_root'])
assert not(O/'OWNER_IDENTITY.json').exists()and not(O/'owner_CONSOLE.log').exists()
assert not(J/'GO_PRODUCTION.json').exists()and not(J/'production').exists()
assert not(J/'control416/NODE_IDENTITY.json').exists()and not(J/'control416/node_CONSOLE.log').exists()
for row in v['manifest']['files']:
 path=J/row['relative'];raw=path.read_bytes();assert len(raw)==row['bytes']and hashlib.sha256(raw).hexdigest()==row['SHA']
assert json.loads((J/'TASK416.json').read_bytes())['run_id']==v['task']['run_id']
print(json.dumps(dict(passed=True,staged416exact=True,no_originalowner_or_node_or_GO=True,modelreads=0)))"""
  put('ROOT418_EXACT_STAGED_NO_OWNER_NODE_GO.json',d.code(client,d.PY72,verify,dict(task=task,manifest=staged['manifest']),timeout=60))
  resources=d.code(client,d.PY72,light.RESOURCE,dict(job=task['job_root'],GPU_UUID=task['GPU_UUID']),timeout=45)
  put('ROOT418_FRESH_SELECTED_RESOURCE_ACTUAL.json',resources);assert resources['passed']
  put('ROOT418_FRESH_AUTHORITY_IMMEDIATELY_BEFORE_FIRSTOWNER.json',d.code(client,d.PY72,remote.AUTH,{},timeout=45))
  token=secrets.token_hex(32);private=dict(spec,token=token)
  cfg=dict(role='owner',run_id=task['run_id'],token=token,scheduling_authority='human_requested_available_experts',experts={'jump_72':private},deferred_experts=[])
  owner=d.code(client,d.PY72,remote.SPAWN,dict(root=task['owner_root'],module='model2050_240_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg,expected_control_cwd=original.CONTROL_CWD),timeout=30)
  put('ROOT416_ORIGINAL_OWNER_LAUNCH_ACTUAL.json',dict(run_id=task['run_id'],owner=owner,specs={'jump_72':spec},firstdispatchvia418=True))
  node=d.code(client,d.PY72,remote.SPAWN,dict(root=task['job_root']+'/control416',module='model2050_240_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=private,expected_control_cwd=original.CONTROL_CWD),timeout=30)
  put('ROOT416_ORIGINAL_NODE_LAUNCH_ACTUAL.json',dict(run_id=task['run_id'],node=node,firstdispatchvia418=True))
  put('ROOT418_FIRST_416_OWNER_NODE_SNAPSHOT.json',d.code(client,d.PY72,original.SNAPSHOT,dict(job=task['job_root'],owner=task['owner_root']),timeout=60))
  print(json.dumps(dict(passed=True,original416firstowner=owner,firstnode=node,no_replay=True)))
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT418_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT418_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_automatic_replay=True));raise
'''
path=C/'finish418_staged416_first_original_owner_once.py';path.write_text(code,encoding='utf8');ast.parse(code)
task418=dict(epoch=time.time(),run=task['run_id'],source_trainingroot=str(N),
 original416indexSHA=H(N/'INDEX416_SOURCE_TASK_CALLERS_FROZEN.json'),
 actual416refusal='BeforeoriginalownercreationatfreshCNone;noGO/SDK/modelread;Pair4claimedcanonical',
 only_pending_operation='Firstowner/nodecreationforalreadyexactstaged416,notreplaylaunch416',
 unused=True,network=0,modelreads=0,required='Allknowncontrollersactualreleased/serialFREE/freshCNone/private/sharedresourceadmission')
with(C/'TASK418_FROZEN.json').open('x',encoding='utf8')as stream:json.dump(task418,stream,indent=2)
index=C/'INDEX418_STAGED_OWNER_RECOVERY_FROZEN.json'
with index.open('x',encoding='utf8')as stream:json.dump(dict(epoch=time.time(),files=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path))for path in(path,C/'TASK418_FROZEN.json',N/'INDEX416_SOURCE_TASK_CALLERS_FROZEN.json',N/'launch416_actual_residual_RL_once.py')]),stream,indent=2)
with(P/'reports/STATIC418_STAGED416_FIRSTOWNER_RECOVERY_READY.json').open('x',encoding='utf8')as stream:json.dump(dict(task418,passed=True,indexSHA=H(index),root=str(C)),stream,indent=2)
print(json.dumps(dict(passed=True,root=str(C),indexSHA=H(index),unused=True)))
