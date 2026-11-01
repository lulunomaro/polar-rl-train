"""ROOT sole72 owner: source-qualified2050 -> literal400N50, original one-hour cap."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,importlib.util,json,os,secrets,subprocess,sys,time,traceback
T=Path(__file__).resolve().parent;W=T.parent;N=T/'MODEL2050_LITERAL_JUMP_400N50_ADAPT_V240_20261101';R=N/'reports'
GPU='GPU-16828f91-2b45-b646-8dc0-9481138e2842';ROLE='jump_72';CONTROL_CWD='/home/lc01/Zonglin Li/zonglin2'
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
B=Path(v['job']);C=B/'control240';f=B/'production/FIRST_ACTUAL_NEW_PPO_UPDATE.json';end=time.time()+850
while time.time()<end and not f.is_file() and not(C/'NODE_TERMINAL_ACTUAL.json').is_file():time.sleep(2)
paths=[C/n for n in ['NODE_IDENTITY.json','WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json','NODE_CURRENT.json','ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json','NODE_ORIGINAL_ERROR.json','NODE_TERMINAL_ACTUAL.json','NODE_EXIT_ACTUAL.json']]
paths+=[B/'GO_PRODUCTION.json',B/'FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json']
paths+=[B/'production'/n for n in ['ACTUAL240_CUDA_FULLSTATE_RESTORE_BEFORE_NEW_CONTROL.json','NATIVE24_MODEL2050_ACTUAL.json','FIRST_ACTUAL_NEW_PPO_UPDATE.json','latest_complete.json','LATEST_PROGRESS.json','ORIGINAL_ERROR.json','FINAL.json','ACTUAL240_MODEL_SOURCE_FINAL_READ_COUNTS_BEFORE_LEARNING.json','APP240_CLOSING.json']]
rows=[]
for p in paths:
 if p.is_file():
  b=p.read_bytes();rows.append(dict(path=str(p),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8')))
value=json.loads(f.read_bytes()) if f.is_file()else None
nr=B/'production/NATIVE24_MODEL2050_ACTUAL.json';native=json.loads(nr.read_bytes()) if nr.is_file()else None
restore=B/'production/ACTUAL240_CUDA_FULLSTATE_RESTORE_BEFORE_NEW_CONTROL.json';restored=json.loads(restore.read_bytes())if restore.is_file()else None
log=C/'production_WORKER.log';prefix=None;material=[]
if log.is_file():
 with log.open('rb')as f:b=f.read(log.stat().st_size)
 text=b.decode('utf8','replace');material=[x for x in text.splitlines()if'PxPhysics::createMaterial'in x and'64K'in x]
 prefix=dict(path=str(log),bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=text,scope='ONE actual FIRST source+owned stdout snapshot, not final or skill')
passed=bool(value and value.get('passed') and value.get('source_SHA')==v['source_SHA'] and value.get('actual_new_PPO_updates')==1
 and value.get('initial_Adam_step')==41240 and value.get('new_Adam_step')==41260 and value.get('new_environment_transitions')==480000
 and value['first_complete']['saved_iteration']==2051 and value['first_complete']['Adam_min']==value['first_complete']['Adam_max']==41260
 and native and native.get('passed') and native.get('controls')==24 and native.get('physics_callbacks')==192 and native.get('feedback_samples')==48
 and restored and restored['passed'] and restored['source_byte_reads']==restored['source_GPU_decodes']==1 and not material)
print(json.dumps(dict(epoch=time.time(),passed=passed,first=value,native24=native,source_restore=restored,full_selected_UTF8=rows,original_stdout_prefix=prefix,
 actual_material_limit_error_count=len(material),original_material_error_lines=material,single_first_wait850=True,snapshot_not_final_or_skill=True)))
'''
def main():
 assert sys.version_info[:2]==(3,14)
 parser=argparse.ArgumentParser();parser.add_argument('--caller-index-SHA',required=True);args=parser.parse_args()
 index=N/'INDEX240_FROZEN_BEFORE_PRODUCTION.json';assert H(index)==args.caller_index_SHA
 for row in read(index)['files']:
  f=Path(row['path']);assert f.stat().st_size==row['bytes'] and H(f)==row['SHA']
 install=read(R/'INSTALL240_SOURCE_ASSET_MANIFEST.json');task=install['task'];J=install['job_root'];O=install['owner_root']
 source_cpu=read(R/'ROOT240_SELECTED2050_FULLPPO_SOURCE_AND_ONNX_CPU_QUALIFIED_ACTUAL.json')
 admit=read(R/'ROOT240_ACTUAL_TARGET80V2_NATIVE8_0PT_OR_ORIGINAL_ERROR_RETURNED.json')
 assert source_cpu['passed'] and source_cpu['human_selected_ONNX_actor_identity_passed'] and read(R/'ROOT240_NEW_SOURCE_TaskGO_CPU_RETURNED_ACTUAL.json')['passed']
 assert admit['passed_execution'] and admit['returncode']==0 and admit['private_and_validation_EX_released'] and admit['all_own_children_waited']
 assert read(R/'ROOT240_ADMIT80V2_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_control_client_lease']=='FREE'
 for r in install['controls']:
  assert Path(r['local_path']).stat().st_size==r['bytes'] and H(r['local_path'])==r['SHA']
 for r in install['files']:
  if Path(r['relative']).suffix in ('.py','.json'):assert Path(r['local_path']).stat().st_size==r['bytes'] and H(r['local_path'])==r['SHA']
 pattern='start240_|install240_|transfer240_|read240_|run_ROOT240_|launch_e2_solo_|collect_e2_solo_|run_ROOT_latest32481_|run_ROOT238_|admit238_|run_actual'
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 q=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True);rows=json.loads(q.stdout)if q.stdout.strip()else[];rows=rows if isinstance(rows,list)else[rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];assert len(rows)==len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower()
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 cim=dict(epoch=time.time(),passed=True,PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows)
 put('ROOT240_START_FRESH_LOCAL_EXACT_CIM.json',cim)
 run='MODEL2050_LITERAL40050_JUMP240_'+str(time.time_ns())
 put('ROOT240_START_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),run_id=run,role=ROLE,source_SHA=task['source_SHA'],source_CPU_report_SHA=task['source_CPU_report_SHA'],
  source_iteration=2050,source_Adam17=41240,source_LR=task['source_LR'],native80_actual_source_admission_passed=True,
  production_source_byte_decode_max=1,old_E0_native_or_normal86_PT_reads=0,source_model_uploads_this_entry=0,
  one_original_writer=True,save_seconds=3600,max_parent_seconds=3900,exit_headroom_seconds=300,new_grant=False,single_FIRST_wait850=True))
 protocol=module('root240_typed_protocol',N/'control240/model2050_task240.py')
 wrapper=module('root240_start_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 remote=module('root240_original_remote_helpers',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_payloads.py')
 light=module('root240_original_light_probe',T/'E2_PLAN_MIMIC01_ADMISSION_KIND_ROOT_V4_20261101/remote_e2_solo_additions.py')
 client=transport=previous=secret=None
 try:
  transport,previous=wrapper.install();sec=module('root240_start_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret);secret=None
  authority=d.code(client,d.PY72,remote.AUTH,{},timeout=45);put('ROOT240_START_FRESH72_CNONE_RESERVE_ACTUAL.json',authority)
  resource=d.code(client,d.PY72,light.RESOURCE,dict(job=J,GPU_UUID=GPU),timeout=45);put('ROOT240_START_SELECTED_GPU_AND_PRIVATE_SHARED_LIGHT_ACTUAL.json',resource)
  assert resource['passed'] and resource['admission_probe_locks_released_before_return']
  # The source manifest deliberately excludes all model and large asset contents.
  mf=dict(kind='MODEL2050_LITERAL40050_SOURCE_TASK_MANIFEST240',source_SHA=task['source_SHA'],
   files=[{k:r[k]for k in ('relative','bytes','SHA')}for r in install['files']if Path(r['relative']).suffix.lower()in('.py','.json','.txt','.sh','.md','.cfg','.ini')])
  manifest_raw=raw(mf);manifest_SHA=hashlib.sha256(manifest_raw).hexdigest()
  ready=dict(passed=True,kind=protocol.READY_KIND,manifest_SHA=manifest_SHA,source_SHA=task['source_SHA'],source_iteration=2050,Adam_step=41240,
   source_LR=task['source_LR'],source_hidden=[128,64,32],source_ONNX_actor_identity_passed=True,all_actor_critic_optimizer_tensors_finite=True,
   actual_35_38_6_shapes=True,source_CPU_report_SHA=task['source_CPU_report_SHA'],source_fullPPO_CPU_report_actual_passed=True,
   target_GPU0PT_actual_waited_RC=0,actual_native_controls=8,actual_physics_callbacks=64,actual_feedback_samples=16,
   literal_reward_text_identity19=True,target80_private_and_validation_EX_released=True,ground_envs=2000,jump_envs=18000,
   fresh_CNone_CIM_resources_actual=True,mimic_rad=.01,actual_target0PT_report_SHA=H(R/'ROOT240_ACTUAL_TARGET80V2_NATIVE8_0PT_OR_ORIGINAL_ERROR_RETURNED.json'),
   fresh_actual_CNone=authority['CNone'],actual_global_CIM_epoch=cim['epoch'],actual_resource_epoch=resource['epoch'],
   CUDA_fullrestore_and_native24_required_before_FIRST=True,not_native_loaded_model_qualification=True)
  spec=dict(key=ROLE,role='node',run_id=run,job_root=J,execution_backend='target72',GPU_UUID=GPU,private_lock=resource['private_lock'],python=d.PY72,
   worker_script='run240_model2050_mixed_literal_worker.py',manifest_file='MANIFEST240.json',manifest_SHA=manifest_SHA,
   source_SHA=task['source_SHA'],source_CPU_report_SHA=task['source_CPU_report_SHA'],num_envs=20000,max_parent_seconds=3900,exit_headroom_seconds=300,
   ground_envs=2000,jump_envs=18000,literal_original_fudan_JUMP=True)
  actual_ready_row_for_validation=dict(key=ROLE,phase='ready',manifest_SHA=manifest_SHA,original_error=False,closed_source_CPU=dict(value=ready,SHA=hashlib.sha256(raw(ready)).hexdigest()))
  assert protocol.valid_ready(actual_ready_row_for_validation,spec)
  schedule=dict(run_id=run,scheduling_authority='human_requested_available_experts',owner_root=O,experts={ROLE:spec},deferred_experts=[]);assert protocol.validate_schedule(schedule)
  added={'MANIFEST240.json':manifest_raw,'FULLSTATE_REUSE_ADMISSION_ACTUAL_V2.json':raw(ready)}
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for name,b in added.items():stage(sf,J+'/'+name,b)
   for root in (O,J+'/control240'):
    stage(sf,root+'/SCHEDULE_PUBLIC.json',raw(schedule))
    for row in install['controls']:stage(sf,root+'/'+row['relative'],Path(row['local_path']).read_bytes())
  finally:sf.close()
  put('ROOT240_ACTUAL_TASK_MANIFEST_READY_AND_PUBLIC_SCHEDULE.json',dict(epoch=time.time(),run_id=run,task=task,manifest=mf,manifest_SHA=manifest_SHA,ready=ready,schedule=schedule,
   Ready_entire_VALUE_SHA_for_GO_source_CPU=hashlib.sha256(raw(ready)).hexdigest(),source_model_reads_this_join=0))
  verify=light.VERIFY_METADATA.replace('/control_e2_solo','/control240')
  put('ROOT240_CONTROL_AND_READY_POSTCOPY_ACTUAL.json',d.code(client,d.PY72,verify,dict(owner=O,job=J,controls=install['controls'],schedule_SHA=hashlib.sha256(raw(schedule)).hexdigest(),newmeta={k:hashlib.sha256(v).hexdigest()for k,v in added.items()}),timeout=60))
  put('ROOT240_START_FRESH72_CNONE_AGAIN_BEFORE_ORIGINAL_OWNER.json',d.code(client,d.PY72,remote.AUTH,{},timeout=45))
  token=secrets.token_hex(32);private_spec=dict(spec,token=token)
  cfg=dict(role='owner',run_id=run,token=token,scheduling_authority='human_requested_available_experts',experts={ROLE:private_spec},deferred_experts=[])
  owner=d.code(client,d.PY72,remote.SPAWN,dict(root=O,module='model2050_240_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg,expected_control_cwd=CONTROL_CWD),timeout=30)
  assert owner['cwd']==CONTROL_CWD;put('ROOT240_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json',dict(run_id=run,owner=owner,specs={ROLE:spec}))
  node=d.code(client,d.PY72,remote.SPAWN,dict(root=J+'/control240',module='model2050_240_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=private_spec,expected_control_cwd=CONTROL_CWD),timeout=30)
  assert node['cwd']==CONTROL_CWD;put('ROOT240_ORIGINAL_JUMP_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=node))
  first=d.code(client,d.PY72,FIRST,dict(job=J,source_SHA=task['source_SHA']),timeout=900);put('ROOT240_FIRST_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',first)
  state=d.code(client,d.PY72,remote.OWNER_STATE,dict(owner=owner),timeout=45);put('ROOT240_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json',state)
  assert first['passed'] and state['current_owner_matched'] and set(state['current']['go'])=={ROLE}
  go=state['current']['go'][ROLE];protocol.validate_go(go,run,task,time.time())
  print(json.dumps(dict(passed=True,run_id=run,owner=owner,node=node,first=first['first'],GO=go,one_original_writer=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT240_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT240_START_ORIGINAL_CALLER_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry_or_GO=True));raise
