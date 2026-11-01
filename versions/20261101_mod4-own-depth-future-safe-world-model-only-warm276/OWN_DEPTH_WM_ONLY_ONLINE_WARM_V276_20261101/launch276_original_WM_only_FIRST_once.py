"""ROOT sole original72 finite writer, live WM-only warm from frozen2135."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,importlib.util,json,os,secrets,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports';ROLE='jump_72';CONTROL_CWD='/home/lc01/Zonglin Li/zonglin2'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(v):return json.dumps(v,indent=2,allow_nan=False).encode()
def put(n,v):
 with(R/n).open('x',encoding='utf8')as f:json.dump(v,f,indent=2,allow_nan=False)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def stage(sf,p,b):
 cur=''
 for bit in str(PurePosixPath(p).parent).split('/'):
  if not bit:continue
  cur+='/'+bit
  try:sf.mkdir(cur)
  except OSError:sf.stat(cur)
 with sf.file(p,'wx')as f:f.write(b);f.flush()
FIRST=r'''from pathlib import Path
import json,time,hashlib
B=Path(v['job']);C=B/'control276';f=B/'production/FIRST_ACTUAL_NEW_WM_UPDATE.json';end=time.time()+850
while time.time()<end and not f.is_file()and not(C/'NODE_TERMINAL_ACTUAL.json').is_file():time.sleep(2)
paths=[C/n for n in ['NODE_IDENTITY.json','WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json','NODE_CURRENT.json','ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json']]
paths +=[B/'GO_PRODUCTION.json',B/'FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json']
paths +=[B/'production'/n for n in ['ACTUAL272_CAMERA_AND_PLANT_CONFIG.json','ACTUAL272_FROZEN2135_ACTOR_ONE_READ.json','ACTUAL276_FRESH_MEASURED_SCHEMA_BINDING.json','ACTUAL276_FROZEN_TEACHER_FULLSTATE_AND_NEW_WM_BEFORE_CONTROL.json','NATIVE24_WM_WARM276_ACTUAL.json','FIRST_ACTUAL_NEW_WM_UPDATE.json','latest_complete.json','LATEST_PROGRESS.json','ORIGINAL_ERROR.json','FINAL.json','APP276_CLOSING.json']]
rows=[]
for p in paths:
 if p.is_file():
  b=p.read_bytes();rows.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8')))
value=json.loads(f.read_bytes())if f.is_file()else None
q=B/'production/NATIVE24_WM_WARM276_ACTUAL.json';native=json.loads(q.read_bytes())if q.is_file()else None
q=B/'production/ACTUAL276_FROZEN_TEACHER_FULLSTATE_AND_NEW_WM_BEFORE_CONTROL.json';restore=json.loads(q.read_bytes())if q.is_file()else None
log=C/'production_WORKER.log';prefix=None;material=[]
if log.is_file():
 with log.open('rb')as f:b=f.read(log.stat().st_size)
 text=b.decode('utf8','replace');material=[x for x in text.splitlines()if'PxPhysics::createMaterial'in x and'64K'in x];prefix=dict(path=str(log),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=text,scope='one actual FIRST snapshot only')
passed=bool(value and value.get('passed')and value.get('actual_new_WM_updates')==1 and value.get('actual_new_PPO_updates')==0 and value.get('actual_Pi_Critic_teacher_updates')==0 and value['first_complete']['teacher_iteration']==2135 and value['first_complete']['teacher_Adam_step']==42940 and native and native['passed']and native['controls']==24 and native['physics_callbacks']==192 and native['feedback_samples']==48 and restore and restore['passed']and restore['source_byte_reads']==restore['source_GPU_decodes']==1 and not material)
print(json.dumps(dict(epoch=time.time(),passed=passed,first=value,native24=native,source_restore=restore,full_selected_UTF8=rows,original_stdout_prefix=prefix,actual_material_limit_error_count=len(material),snapshot_not_final_policy_or_skill=True,single_first_wait850=True)))'''
def main():
 assert sys.version_info[:2]==(3,14)
 p=argparse.ArgumentParser();p.add_argument('--caller-index-SHA',required=True);a=p.parse_args();index=N/'INDEX276_WM_ONLY_WARM_SOURCE_CALLERS_FROZEN.json';assert H(index)==a.caller_index_SHA
 for row in read(index)['files']:
  q=Path(row['path']);assert q.stat().st_size==row['bytes']and H(q)==row['SHA']
 task=read(N/'TASK276_FROZEN.json');J=task['job_root'];O=task['owner_root'];GPU=task['GPU_UUID'];run=task['run_id']
 protocol=module('root276_protocol',N/'control276/wm_task275.py');protocol.validate_task(task)
 assert read(R/'ROOT276_LIVE_WORKER_TaskGO_SOURCE_CPU_NEW_JOIN.json')['passed']
 actual274=read(T/'NEW272_FUTURE_SAFE_WM_CUDA_ADMISSION_V274V3_20261101/reports/ROOT274_NEW272_ACTUAL_H32_CUDA_OR_ORIGINAL_ERROR_RETURNED.json');assert actual274['passed']and actual274['result']['actual_WM_updates']==0
 pattern='launch276_|collect276_|run_ROOT274_|run_ROOT272_|collect270_exact_|run_ROOT270_|run_ROOT269_|run_ROOT267_|run_ROOT266_|run_ROOT261_|run_ROOT246_|run_ROOT242_|collect243_|collect240_|human241_|start240_|install240_|transfer240_|read240_|run_ROOT_latest32481_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(p.stdout)if p.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 assert len(rows)==1 and rows[0]['ProcessId']==os.getpid()and rows[0]['CreationDate']and rows[0]['ExecutablePath'].lower()==sys.executable.lower()and str(Path(__file__).resolve()).lower().replace('\\','/')in rows[0]['CommandLine'].lower().replace('\\','/')
 cim=dict(epoch=time.time(),passed=True,rows=rows,exe=sys.executable,argv=sys.argv);put('ROOT276_START_FRESH_LOCAL_EXACT_CIM.json',cim)
 put('ROOT276_START_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),run_id=run,task=task,one_new_teacher_GPU_byte_decode_allowed=1,old_E0_native_raw_reads=0,new_WM_Adam_only=True,teacher_frozen=True,one_original_writer=True,save3600_exit300=True,new_grant=False))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 remote=module('root276_remote',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_payloads.py');light=module('root276_light',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_additions.py')
 transport=previous=client=secret=None
 try:
  transport,previous=module('root276_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py').install();secret=module('root276_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py').recover();client=d.connect72(secret);secret=None
  authority=d.code(client,d.PY72,remote.AUTH,{},timeout=45);put('ROOT276_START_FRESH72_CNONE_RESERVE_ACTUAL.json',authority)
  mkdir="from pathlib import Path\nimport json\np=Path(v['job']);assert p.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks').resolve());p.mkdir(parents=True,exist_ok=False);print(json.dumps(dict(passed=True,new_namespace=str(p),model_reads=0)))"
  put('ROOT276_NEW_NAMESPACE_ACTUAL.json',d.code(client,d.PY72,mkdir,dict(job=J),timeout=45))
  resource=d.code(client,d.PY72,light.RESOURCE,dict(job=J,GPU_UUID=GPU),timeout=45);put('ROOT276_START_SELECTED_GPU_PRIVATE_SHARED_LIGHT_ACTUAL.json',resource);assert resource['passed']and resource['admission_probe_locks_released_before_return']
  files=[dict(relative='source/'+str(q.relative_to(N/'source')).replace('\\','/'),bytes=q.stat().st_size,SHA=H(q),local_path=str(q))for q in sorted((N/'source').rglob('*.py'))]
  files.append(dict(relative='TASK276.json',bytes=(N/'TASK276_FROZEN.json').stat().st_size,SHA=H(N/'TASK276_FROZEN.json'),local_path=str(N/'TASK276_FROZEN.json')))
  manifest=dict(kind='OWN_WM_ONLY_WARM276_SOURCE_TASK_MANIFEST',source_SHA=task['source_SHA'],files=[{k:r[k]for k in('relative','bytes','SHA')}for r in files]);manifest_bytes=raw(manifest);manifest_SHA=hashlib.sha256(manifest_bytes).hexdigest()
  spec=dict(task,key=ROLE,role='node',execution_backend='target72',private_lock=resource['private_lock'],python=d.PY72,worker_script='source/worker276_online_WM_only.py',manifest_file='MANIFEST276.json',manifest_SHA=manifest_SHA)
  ready=dict(task,passed=True,kind=protocol.READY_KIND,manifest_SHA=manifest_SHA,Adam_step=42940,teacher_fullstate_CPU_passed=True,actor35_critic38_STD6_full17Adam_finite=True,actual272_complete_current_packet_PASS=True,actual274_CUDA_H32_no_step_PASS=True,fresh_CNone_CIM_resources_actual=True,target_private_and_validation_EX_probe_released=True,actual_resource_admission_SHA=H(R/'ROOT276_START_SELECTED_GPU_PRIVATE_SHARED_LIGHT_ACTUAL.json'),admission_optimizer_steps=0,supported_start_candidates=actual274['result']['supported_start_candidates'],node_held_resource_SHA_bound_in_producer_after_GO=True)
  row=dict(key=ROLE,phase='ready',manifest_SHA=manifest_SHA,original_error=False,closed_source_CPU=dict(value=ready,SHA=protocol.ready_value_SHA(ready)));assert protocol.valid_ready(row,spec)
  schedule=dict(run_id=run,scheduling_authority='human_requested_available_experts',owner_root=O,experts={ROLE:spec},deferred_experts=[]);protocol.validate_schedule(schedule)
  controls=[dict(relative=q.name,bytes=q.stat().st_size,SHA=H(q),local_path=str(q))for q in sorted((N/'control276').glob('*.py'))]
  added={'MANIFEST276.json':manifest_bytes,'FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json':raw(ready)}
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for r in files:stage(sf,J+'/'+r['relative'],Path(r['local_path']).read_bytes())
   for name,b in added.items():stage(sf,J+'/'+name,b)
   for root in(O,J+'/control276'):
    stage(sf,root+'/SCHEDULE_PUBLIC.json',raw(schedule))
    for r in controls:stage(sf,root+'/'+r['relative'],Path(r['local_path']).read_bytes())
  finally:sf.close()
  put('ROOT276_ACTUAL_TASK_MANIFEST_READY_PUBLIC_SCHEDULE.json',dict(epoch=time.time(),run_id=run,task=task,manifest=manifest,manifest_SHA=manifest_SHA,ready=ready,schedule=schedule,Ready_entire_VALUE_SHA_for_GO_source_CPU=protocol.ready_value_SHA(ready),controls=controls,model_copy_stat_hash_reads=0))
  verify="""from pathlib import Path
import hashlib,json
for r in v['files']:
 p=Path(v['job'])/r['relative'];b=p.read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['SHA']
for root in(v['owner'],v['job']+'/control276'):
 for r in v['controls']:
  b=(Path(root)/r['relative']).read_bytes();assert len(b)==r['bytes']and hashlib.sha256(b).hexdigest()==r['SHA']
 assert hashlib.sha256((Path(root)/'SCHEDULE_PUBLIC.json').read_bytes()).hexdigest()==v['schedule_SHA']
for name,SHA in v['added'].items():assert hashlib.sha256((Path(v['job'])/name).read_bytes()).hexdigest()==SHA
print(json.dumps(dict(passed=True,source_only_postcopy=True,model_raw_reads=0)))"""
  put('ROOT276_SOURCE_READY_CONTROLS_POSTCOPY_ACTUAL.json',d.code(client,d.PY72,verify,dict(job=J,owner=O,files=files,controls=controls,schedule_SHA=hashlib.sha256(raw(schedule)).hexdigest(),added={k:hashlib.sha256(v).hexdigest()for k,v in added.items()}),timeout=60))
  put('ROOT276_START_FRESH72_CNONE_AGAIN_BEFORE_OWNER.json',d.code(client,d.PY72,remote.AUTH,{},timeout=45))
  token=secrets.token_hex(32);private_spec=dict(spec,token=token);cfg=dict(role='owner',run_id=run,token=token,scheduling_authority='human_requested_available_experts',experts={ROLE:private_spec},deferred_experts=[])
  owner=d.code(client,d.PY72,remote.SPAWN,dict(root=O,module='model2050_240_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg,expected_control_cwd=CONTROL_CWD),timeout=30);assert owner['cwd']==CONTROL_CWD;put('ROOT276_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json',dict(run_id=run,owner=owner,specs={ROLE:spec}))
  node=d.code(client,d.PY72,remote.SPAWN,dict(root=J+'/control276',module='model2050_240_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=private_spec,expected_control_cwd=CONTROL_CWD),timeout=30);assert node['cwd']==CONTROL_CWD;put('ROOT276_ORIGINAL_WM_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=node))
  first=d.code(client,d.PY72,FIRST,dict(job=J),timeout=900);put('ROOT276_FIRST_NEW_WM_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',first)
  state=d.code(client,d.PY72,remote.OWNER_STATE,dict(owner=owner),timeout=45);put('ROOT276_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json',state)
  assert first['passed']and state['current_owner_matched']and set(state['current']['go'])=={ROLE}
  go=state['current']['go'][ROLE];protocol.validate_go(go,run,task,time.time());protocol.validate_ready_go(go,ready,spec);protocol.validate_first(first['first'],task,go)
  print(json.dumps(dict(passed=True,run_id=run,owner=owner,node=node,first=first['first'],GO=go,WM_only=True,teacher_frozen=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT276_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT276_START_ORIGINAL_CALLER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry_or_GO=True));raise
