"""ROOT-only E2 installer/original sole-owner FIRST. Source preparer never runs it.

Selected b3ae stays at the qualified path: no installer source PT stat,hash,
copy,open or decode. Original worker alone owns its one pinned byte/decode.
"""
from pathlib import Path,PurePosixPath
import argparse,os,secrets,subprocess,sys,time,traceback
from caller_common import *
from e2_solo_contract import metadata,qualified_cpu,scoped232,fresh,valid_ready_value
from e2_solo_protocol import validate_schedule
import remote_e2_solo_payloads as target
from remote_e2_solo_additions import RESOURCE,VERIFY_METADATA

def exact_cim(extra_pattern):
 pattern='launch_e2_solo_|collect_e2_solo_|review_e2_solo_|launch227D_|collect227D_|review227D_|launch219V3_|launch219V2_|launch219_|collect219_|review219_|collect210_|launch210_|review210_|install21[1-9]_|'+extra_pattern
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern.replace("'","''")+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=__import__('json').loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 return dict(epoch=time.time(),passed=True,PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,other_known_control_finites=other)

def stage(sf,remote,data):
 parent=str(PurePosixPath(remote).parent);cur=''
 for part in parent.split('/'):
  if not part:continue
  cur+='/'+part
  try:sf.mkdir(cur)
  except OSError:sf.stat(cur)
 with sf.file(remote,'wx') as f:f.write(data);f.flush()

def main():
 p=argparse.ArgumentParser()
 for name in ('root-lease-label','run-id','remote-job-root','remote-owner-root','GPU-UUID','additional-control-pattern','caller-index-SHA'):p.add_argument('--'+name,required=True)
 for name in ('saved-e2-cpu','scoped-actual232','auth-provider'):p.add_argument('--'+name,type=Path,required=True)
 a=p.parse_args()
 # Actual saved qualification and actual232 scoped proof precede transport/auth.
 cpu,cr=metadata(a.saved_e2_cpu);qualified_cpu(cpu,cr['SHA'])
 scope,sr=metadata(a.scoped_actual232);scoped232(scope)
 assert not cpu.get('synthetic_fixture_only') and not scope.get('synthetic_fixture_only')
 assert a.root_lease_label.startswith('ROOT_E2_SOLO_EXCLUSIVE_START_') and a.additional_control_pattern and a.GPU_UUID in GPUS
 verify_index(SOURCE/'INDEX_E2_SOLO_PPO_SOURCE_FROZEN.json',SOURCE_INDEX_SHA)
 verify_index(FINITE/'INDEX_E2_FINITE_V2_FROZEN.json',FINITE_INDEX_SHA)
 verify_index(N/INDEX,a.caller_index_SHA)
 assert read(R/'CPU_E2_SOLO_CALLERS_NEW_INTERFACE_ACTUAL.json')['passed']
 install=read(FINITE/'reports/INSTALL_E2_SOLO_ORIGINAL_SOURCE_V2.json')
 control=read(SOURCE/'reports/CONTROL_E2_SOLO_FROZEN_BINDINGS.json')
 assert install['before_use_worker_finite_V2'] and all(not x['relative'].endswith(('.pt','.partial','.active')) for x in install['files'])
 run=a.run_id;j=PurePosixPath(a.remote_job_root);o=PurePosixPath(a.remote_owner_root)
 base=PurePosixPath(CONTROL_CWD)/'tasks'
 assert all(q.is_absolute() and q.is_relative_to(base) and q!=base for q in (j,o))
 assert j!=o and not j.is_relative_to(o) and not o.is_relative_to(j) and str(j)!=str(PurePosixPath(MODEL).parent.parent)
 J=str(j);O=str(o)
 cim=exact_cim(a.additional_control_pattern);put('ROOT_E2_SOLO_START_FRESH_LOCAL_EXACT_CIM.json',cim)
 put('ROOT_E2_SOLO_START_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),run_id=run,root_lease_label=a.root_lease_label,
  saved_qualified_CPU_ref=cr,actual232_scoped_ref=sr,roles=[ROLE],source_SHA=SHA,source_bytes=BYTES,source_iteration=ITER,Adam17=ADAM,LR=LR,
  finite_learning_seconds=3600,max_parent_seconds=3900,exit_headroom_seconds=300,selected_model_stat_hash_copy_open_decode=0,
  production_worker_source_byte_read=1,production_worker_source_decode=1,old_CPU_PT_reads=0,raw_trajectory_reads=0,
  source_asset_postcopy_once_each_new_namespace=True,original_constructor_reset_NPZ_only=True,one_original_writer=True,
  no_hotadd_or_new_grant=True,FIRST_once=True,max_FIRST_wait_seconds=850,auth_provider_path=str(a.auth_provider)))
 wrapper=module('root_e2_solo_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
 import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('root_e2_solo_memory_auth',a.auth_provider);secret=sec.recover();client=d.connect72(secret)
  put('ROOT_E2_SOLO_FRESH72_CNONE_RESERVE_THEN_CLOSE72_ACTUAL.json',d.code(client,d.PY72,target.AUTH,{},timeout=45))
  client.close();client=None
  client=d.connect72(secret);secret=None
  put('ROOT_E2_SOLO_NEW_UNUSED_NAMESPACES_ACTUAL.json',d.code(client,d.PY72,target.CREATE,dict(job=J,owner=O),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in install['files']:
    assert not row['relative'].endswith(('.pt','.partial','.active'))
    cur=J
    for part in row['relative'].split('/')[:-1]:
     cur+='/'+part
     try:sf.mkdir(cur)
     except OSError:sf.stat(cur)
    sf.put(row['local_path'],J+'/'+row['relative'])
  finally:sf.close()
  post=d.code(client,d.PY72,target.POSTCOPY_NO_MODEL,dict(job=J,files=install['files']),timeout=180)
  put('ROOT_E2_SOLO_SOURCE_ASSET_POSTCOPY_NO_MODEL_READ_ACTUAL.json',post);assert post['passed']
  resource=d.code(client,d.PY72,RESOURCE,dict(job=J,GPU_UUID=a.GPU_UUID),timeout=45)
  put('ROOT_E2_SOLO_FRESH_SELECTED_GPU_PRIVATE_SHARED_LIGHT_ACTUAL.json',resource)
  assert resource['admission_probe_only'] and resource['admission_probe_locks_released_before_return']
  authority=d.code(client,d.PY72,target.AUTH,{},timeout=45);put('ROOT_E2_SOLO_FRESH72_CNONE_BEFORE_FROZEN_TASK_ACTUAL.json',authority)
  refs=[]
  for name in ('ROOT_E2_SOLO_START_FRESH_LOCAL_EXACT_CIM.json','ROOT_E2_SOLO_FRESH_SELECTED_GPU_PRIVATE_SHARED_LIGHT_ACTUAL.json','ROOT_E2_SOLO_FRESH72_CNONE_BEFORE_FROZEN_TASK_ACTUAL.json'):
   _,r=metadata(R/name);refs.append(r)
  admission=dict(kind='ROOT_E2_SOLO_FRESH_CNONE_CIM_RESOURCE_ACTUAL',passed=bool(authority['CNone'] and resource['passed'] and cim['passed']),
   run_id=run,job_root=J,fresh_current_CNone=authority['CNone'],canonical_active=authority['active_segment'],generation=authority['generation'],
   total_authorized_seconds=authority['total_authorized_seconds'],fresh_LOCAL_exact_CIM_passed=cim['passed'],
   original_private_EX_probe_free=resource['private_EX_probe_free'],original_shared_locks_probe_free=resource['shared_EX_probe_free'],
   no_new_writer_grant_copy_refund_or_hotadd=True,checked_epoch=authority['epoch'],
   CNone_checked_epoch=authority['epoch'],LOCAL_exact_CIM_checked_epoch=cim['epoch'],resource_checked_epoch=resource['epoch'],
   control_snapshot_id='ROOT_E2_SOLO_CNONE_'+authority['SHA']+'_'+str(authority['epoch']),actual_report_refs=refs,
   **{k:resource[k] for k in ('GPU_UUID','GPU_name','GPU_free_MiB','GPU_util_percent','RAM_available_bytes','disk_free_bytes')})
  fresh(admission);put('ROOT_E2_SOLO_FRESH_ACTUAL_ADMISSION_FOR_TASK.json',admission)
  staging=N/'ROOT_E2_SOLO_ACTUAL_TASK_STAGING'
  command=[sys.executable,'-B','-X','utf8',str(SOURCE/'prepare_e2_solo_Task_manifest_Ready_SOURCE_ONLY.py'),
   '--saved-cpu',str(a.saved_e2_cpu),'--scoped-actual232',str(a.scoped_actual232),
   '--fresh-admission',str(R/'ROOT_E2_SOLO_FRESH_ACTUAL_ADMISSION_FOR_TASK.json'),
   '--install',str(FINITE/'reports/INSTALL_E2_SOLO_ORIGINAL_SOURCE_V2.json'),
   '--job-root',J,'--run-id',run,'--out-new',str(staging)]
  completed=subprocess.run(command,capture_output=True,text=True,encoding='utf8')
  put('ROOT_E2_SOLO_TASK_GENERATOR_ORIGINAL_RETURNED_ACTUAL.json',dict(returncode=completed.returncode,stdout=completed.stdout,stderr=completed.stderr));assert completed.returncode==0
  task=read(staging/'TASK.json');ready=read(staging/'ADMISSION_E2_SOLO_READY.json');spec=read(staging/'E2_SOLO_ORIGINAL_OWNER_SPEC_FIELDS.json')
  spec.update(private_lock=resource['private_lock'],python=d.PY72,role='node',run_id=run);assert valid_ready_value(ready,spec)
  schedule=dict(run_id=run,scheduling_authority='human_requested_available_experts',owner_root=O,experts={ROLE:spec},deferred_experts=[]);validate_schedule(schedule)
  added={name:(staging/name).read_bytes() for name in ('TASK.json','PRELAUNCH_E2_SOLO_ACTUAL_EVIDENCE.json','E2_SOLO_MANIFEST.json','ADMISSION_E2_SOLO_READY.json')}
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for rel,data in added.items():stage(sf,J+'/'+rel,data)
   for root in (O,J+'/control_e2_solo'):
    stage(sf,root+'/SCHEDULE_PUBLIC.json',raw(schedule))
    for row in control['files']:stage(sf,root+'/'+row['relative'],Path(row['local_path']).read_bytes())
  finally:sf.close()
  put('ROOT_E2_SOLO_ACTUAL_TASK_MANIFEST_READY_AND_PUBLIC_SCHEDULE.json',dict(epoch=time.time(),run_id=run,task=task,manifest_SHA=spec['manifest_SHA'],
   launch_evidence_SHA=spec['launch_evidence_SHA'],ready=ready,schedule=schedule,selected_model_read_by_join=0))
  verify=d.code(client,d.PY72,VERIFY_METADATA,dict(owner=O,job=J,controls=control['files'],schedule_SHA=__import__('hashlib').sha256(raw(schedule)).hexdigest(),newmeta={k:__import__('hashlib').sha256(v).hexdigest() for k,v in added.items()}),timeout=60)
  put('ROOT_E2_SOLO_CONTROL_AND_NEW_METADATA_POSTCOPY_ACTUAL.json',verify);assert verify['passed']
  put('ROOT_E2_SOLO_FRESH72_CNONE_AGAIN_BEFORE_ORIGINAL_OWNER.json',d.code(client,d.PY72,target.AUTH,{},timeout=45))
  token=secrets.token_hex(32);private_spec=dict(spec,token=token)
  cfg=dict(role='owner',run_id=run,token=token,scheduling_authority='human_requested_available_experts',experts={ROLE:private_spec},deferred_experts=[])
  owner=d.code(client,d.PY72,target.SPAWN,dict(root=O,module='e2_solo_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg,expected_control_cwd=CONTROL_CWD),timeout=30)
  assert owner['cwd']==CONTROL_CWD and owner['root']==O;put('ROOT_E2_SOLO_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json',dict(run_id=run,owner=owner,specs={ROLE:spec}))
  node=d.code(client,d.PY72,target.SPAWN,dict(root=J+'/control_e2_solo',module='e2_solo_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=private_spec,expected_control_cwd=CONTROL_CWD),timeout=30)
  assert node['cwd']==CONTROL_CWD and node['root']==J+'/control_e2_solo';put('ROOT_E2_SOLO_ORIGINAL_E2_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=node))
  first=d.code(client,d.PY72,target.FIRST,dict(job=J,source_SHA=SHA),timeout=900);put('ROOT_E2_SOLO_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',first)
  state=d.code(client,d.PY72,target.OWNER_STATE,dict(owner=owner),timeout=45);put('ROOT_E2_SOLO_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json',state)
  assert first['passed'] and state['current_owner_matched'] and set(state['current']['go'])=={ROLE};validate_original_go(state['current']['go'][ROLE],run)
  print(__import__('json').dumps(dict(passed=True,run_id=run,owner=owner,node=node,first=first['first'],GO=state['current']['go'][ROLE],one_original_writer=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT_E2_SOLO_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))

if __name__=='__main__':
 try:main()
 except BaseException:put('ROOT_E2_SOLO_START_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_or_GO=True));raise
