"""ROOT one NEW latest-E0 N1 mean-policy case, fresh CNone, fixedSI35/mode action-flow/readcounts."""

from pathlib import Path

import hashlib,importlib.util,json,os,subprocess,sys,time,traceback

N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'

S=N/'source_V2_FLOAT_FIRST'

J='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E0_ACTION_OPTIMIZER_META228V2_CNONE_20261101/case'

def read(p):return json.loads(Path(p).read_bytes())

def put(n,v):

 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)

def module(n,p):

 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m

AUTH="""from pathlib import Path

import json,hashlib,time

raw=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes();c=json.loads(raw)

assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[]and c['active_segment']is None

print(json.dumps(dict(passed=True,epoch=time.time(),fresh_CNone=True,canonical_SHA=hashlib.sha256(raw).hexdigest(),account_writes=0)))

"""

EXEC="""from pathlib import Path

import contextlib,hashlib,io,json,runpy,sys,time,traceback

B=Path(v['job']);rows=v['files']

for r in rows:

 p=B/r['relative'];raw=p.read_bytes();assert len(raw)==r['bytes']and hashlib.sha256(raw).hexdigest()==r['SHA']

capture=io.StringIO();error=None

try:

 sys.argv=[str(B/'target228_single_N1_parent_UNUSED.py'),'--task',str(B/'TASK228.json')]

 with contextlib.redirect_stdout(capture):runpy.run_path(sys.argv[0],run_name='__main__')

except BaseException:error=traceback.format_exc()

if error:

 with(B/'ROOT228V2_REMOTE_WRAPPER_ORIGINAL_ERROR.json').open('x',encoding='utf8')as f:json.dump(dict(error=error,no_auto_retry=True),f,indent=2)

p=B/'ACTUAL228_ORIGINAL_PARENT_RETURNED.json';value=json.loads(p.read_bytes())if p.is_file()else None

texts=[]

for folder in(B,B/'actual_capture'):

 for p in sorted(folder.iterdir())if folder.is_dir()else[]:

  if p.is_file()and p.suffix in('.json','.log'):

   raw=p.read_bytes();texts.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace')))

print(json.dumps(dict(epoch=time.time(),passed_execution=bool(not error and value and value['passed_execution']),original_parent=value,

 wrapper_error=error,original_parent_stdout=capture.getvalue(),full_UTF8=texts,model_copies=0,artifact_transfers=0,GUI=False)))

"""

def main():

 task=read(S/'TASK228.json');pack=read(S/'PACKAGE228_SOURCE_AND_TASK.json')
 q=read(T/'E0_JUMP32066_GROUND10_THREE_HOUR_V210_20261031/reports/ROOT210_TWO_NEW_FORMALS_INITIAL_WHOLE_CPU_RETURNED_ACTUAL.json')
 assert q['passed']and q['roles']['e0_72']['SHA']==task['model_SHA']and q['roles']['e0_72']['save_at_or_after_requested_deadline']
 assert read(T/'W35_SOLO_INSTALL_FIRST_AND_CLOSED_READERS_SOURCE_V219_20261101/reports/ROOT219V3_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL.json')['owner_closed']['canonical_None']

 assert task['model_SHA']=='e6291fc50e692b9921dfe8ddcbfcc678e9b5916441229c2fd7a4f2c2cc75a538'and task['model_iteration']==32341

 for r in pack['files']:

  p=S/r['relative'];assert p.stat().st_size==r['bytes']and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']

 assert read(T/'W35_FULL_RM70_CLOSED_SKILL_SOURCE_V222_20261101/reports/ROOT222_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'

 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'run_ROOT228V2_action_optimizer_metadata_once|run_ROOT228_action_optimizer_metadata_once|launch219V3_|launch219V2_|collect219_|collect210_|run207_zero|run_ROOT221_|collect219V3_|run_ROOT228_|run_ROOT222_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''

 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]

 own=[r for r in rows if r['ProcessId']==os.getpid()];other=[r for r in rows if r['ProcessId']!=os.getpid()]

 put('ROOT228V2_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,other=other))

 assert len(own)==1 and own[0]['CreationDate']and own[0]['ExecutablePath'].lower()==sys.executable.lower()and not other

 assert str(Path(__file__).resolve()).lower().replace('\\','/')in own[0]['CommandLine'].lower().replace('\\','/')

 put('ROOT228V2_NEW_N1_PURPOSE_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),source_package=pack,Task=task,

  GPU_model_byte_reads=0,GPU_model_decodes=0,old_source_model_reads=0,local_PT_reads=0,original_constructor_RESET_NPZ=1,NN_constructors_for_optimizer_identity=2,neural_forwards=0,

  own_loaded_wheel_geometry_metadata_queries_max=0,Stage_Open_calls=0,extra_PhysX_getters=0,

  new_case_controls_max=0,physics_callbacks_max=0,feedback_max=0,source_package_POSTCOPY_passes=1,asset_copies=0,

  NPZ_transfers_or_reads=0,GUI=False,account_writes=0))

 wrapper=module('case228_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')

 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d

 client=transport=previous=secret=None

 try:

  transport,previous=wrapper.install();sec=module('case228_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()

  client=d.connect72(secret)

  put('ROOT228V2_FRESH72_CNONE_BEFORE_N1_ACTUAL.json',d.code(client,d.PY72,AUTH,dict(binding=task['current_authority_binding']),timeout=45))

  client.close();client=None

  client=d.connect72(secret);secret=None

  create="""from pathlib import Path

import json

B=Path(v['job']);assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());B.mkdir(parents=True,exist_ok=False)

print(json.dumps(dict(passed=True,new_root=str(B),no_old_task_modified=True)))"""

  put('ROOT228V2_NEW_NAMESPACE_ACTUAL.json',d.code(client,d.PY72,create,dict(job=J),timeout=30))

  sf=client.open_sftp();sf.get_channel().settimeout(120)

  try:

   for r in pack['files']+[dict(relative='PACKAGE228_SOURCE_AND_TASK.json')]:

    cur=J

    for bit in r['relative'].split('/')[:-1]:

     cur+='/'+bit

     try:sf.mkdir(cur)

     except OSError:sf.stat(cur)

    sf.put(str(S/r['relative']),J+'/'+r['relative'])

  finally:sf.close()

  actual=d.code(client,d.PY72,EXEC,dict(job=J,files=pack['files']),timeout=1800)

  put('ROOT228V2_ORIGINAL_N1_PARENT_CASE_OR_ERROR_RETURNED_ACTUAL.json',actual)

  case=(actual.get('original_parent')or{}).get('result')or{}

  print(json.dumps(dict(passed_execution=actual['passed_execution'],wrapper_error=actual['wrapper_error'],

   controls=case.get('controls'),seconds=case.get('seconds'),terminal_flags=case.get('terminal_flags'),

   endpoint_flight_evidence=case.get('endpoint_flight_evidence'),metrics=case.get('eval_only_zero_yaw'),

   result_keys=list(case))),flush=True)

 finally:

  secret=None

  if client is not None:client.close();client=None

  if transport is not None:transport.SESSION=previous

  put('ROOT228V2_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))

if __name__=='__main__':

 try:main()

 except BaseException:put('ROOT228V2_LOCAL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_auto_retry=True));raise

