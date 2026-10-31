"""ROOT-only next sole-owner installer/FIRST. Not executed by source preparer.

Selected343e model is never copied, opened, hashed or stat'ed here. Only the
production worker's pinned read/decode may consume it after the original GO.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import importlib.util
import json
import os
import secrets
import subprocess
import sys
import time
import traceback

N=Path(__file__).resolve().parent
P=N.parent
A=P/'A_PPO_SOURCE'
T=P.parent
W=T.parent
R=N/'reports'
CONTROL_CWD='/home/lc01/Zonglin Li/zonglin2'
sys.path.insert(0,str(A))
from contract227 import SHA,ITER,ADAM,LR,KIND,metadata,qualified,validate_ready
import remote227D_payloads as target
from remote227D_additions import RESOURCE,VERIFY_METADATA


def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(v):return json.dumps(v,indent=2,allow_nan=False).encode()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m


def exact_cim(extra_pattern):
 pattern='launch227D_|collect227D_|review227D_|launch219V3_|launch219V2_|launch219_|collect219_|review219_|collect210_|launch210_|review210_|install21[1-9]_|'+extra_pattern
 query="Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='ssh.exe'\" | Where-Object { $_.CommandLine -match '"+pattern.replace("'","''")+"' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress"
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 return dict(epoch=time.time(),passed=True,PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,other_known_control_finites=other)


def stage(sf,remote,data):
 # Exact successful219V3 mode: Paramiko wx has exclusive creation AND write.
 parent=str(PurePosixPath(remote).parent);cur=''
 for part in parent.split('/'):
  if not part:continue
  cur+='/'+part
  try:sf.mkdir(cur)
  except OSError:sf.stat(cur)
 with sf.file(remote,'wx') as f:f.write(data);f.flush()


def verify_index(index_path,expected_sha):
 assert H(index_path)==expected_sha
 index=read(index_path)
 for row in index['files']:
  p=Path(row['path']) if 'path' in row else index_path.parent/row['relative']
  assert p.suffix in ('.py','.json','.md') and p.stat().st_size==row['bytes'] and H(p)==row['SHA']


def main():
 parser=argparse.ArgumentParser()
 parser.add_argument('--root-lease-label',required=True)
 parser.add_argument('--closing',type=Path,required=True)
 parser.add_argument('--new-w35-cpu',type=Path,required=True)
 parser.add_argument('--auth-provider',type=Path,required=True)
 parser.add_argument('--run-id',required=True)
 parser.add_argument('--remote-run-root',required=True)
 parser.add_argument('--additional-control-pattern',required=True)
 parser.add_argument('--caller-index-SHA',required=True)
 args=parser.parse_args()
 # FIRST gate before transport/auth/CIM/asset/model access.
 closing,cr=metadata(args.closing);cpu,qr=metadata(args.new_w35_cpu)
 qualification=qualified(closing,cpu,qr['SHA'])
 assert args.root_lease_label.startswith('ROOT227D_EXCLUSIVE_W35_SOLO_') and args.additional_control_pattern
 verify_index(A/'INDEX227A_FROZEN.json','b71e3df7327b93c3849eb1ced2ba002e004d714e69b444b0ab08914d18676ed6')
 verify_index(N/'INDEX227D_FROZEN.json',args.caller_index_SHA)
 assert read(R/'CPU227D_SOURCE_AST_INTERFACE_ACTUAL.json')['passed']
 install=read(A/'reports/INSTALL227_SOURCE_ROWS_FROZEN.json')
 control=read(R/'CONTROL227D_A_FROZEN_BINDINGS.json')
 cim=exact_cim(args.additional_control_pattern);put('ROOT227D_START_FRESH_LOCAL_EXACT_CIM.json',cim)
 run=args.run_id;base=PurePosixPath(args.remote_run_root)
 assert base.is_absolute() and base.is_relative_to('/home/lc01/Zonglin Li/zonglin2/tasks')
 J=str(base/'w35_72');O=str(base/'owner72')
 put('ROOT227D_START_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),run_id=run,
  root_lease_label=args.root_lease_label,qualified219_inputs=[cr,qr],roles=['w35_72'],
  source_SHA=SHA,source_iteration=ITER,Adam17=ADAM,LR=LR,finite_learning_seconds=3600,max_parent_seconds=3900,
  selected_model_copy_hash_stat=0,production_worker_source_byte_read=1,production_worker_source_decode=1,
  old_CPU_PT_reads=0,raw_trajectory_reads=0,source_asset_postcopy_once_each_new_training_namespace=True,
  original_constructor_reset_NPZ_and_CAD_NPZ_only=True,one_original_writer=True,no_hotadd_or_new_grant=True,
  FIRST_once=True,max_FIRST_wait_seconds=850,auth_provider_path=str(args.auth_provider)))
 wrapper=module('root227D_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
 import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('root227D_memory_auth',args.auth_provider);secret=sec.recover()
  client=d.connect72(secret)
  first_auth=d.code(client,d.PY72,target.AUTH,{},timeout=45)
  put('ROOT227D_FRESH72_CNONE_RESERVE_THEN_CLOSE72_ACTUAL.json',first_auth)
  client.close();client=None
  client=d.connect72(secret);secret=None
  put('ROOT227D_NEW_UNUSED_NAMESPACES_ACTUAL.json',d.code(client,d.PY72,target.CREATE,dict(job=J,owner=O),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in install['files']:
    assert not row['relative'].endswith('.pt')
    # Root-only declared installation bytes; selected343e is not among rows.
    cur=J
    for part in row['relative'].split('/')[:-1]:
     cur+='/'+part
     try:sf.mkdir(cur)
     except OSError:sf.stat(cur)
    sf.put(row['local_path'],J+'/'+row['relative'])
  finally:sf.close()
  post=d.code(client,d.PY72,target.POSTCOPY_NO_MODEL,dict(job=J,files=install['files']),timeout=180)
  put('ROOT227D_SOURCE_ASSET_POSTCOPY_NO_MODEL_READ_ACTUAL.json',post);assert post['passed']
  resource=d.code(client,d.PY72,RESOURCE,dict(job=J,GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d'),timeout=45)
  put('ROOT227D_FRESH_SELECTED_GPU_PRIVATE_SHARED_LIGHT_ACTUAL.json',resource)
  assert resource['admission_probe_only'] and resource['admission_probe_locks_released_before_return']
  authority=d.code(client,d.PY72,target.AUTH,{},timeout=45)
  put('ROOT227D_FRESH72_CNONE_BEFORE_FROZEN_TASK_ACTUAL.json',authority)
  fresh=dict(kind='ROOT227_FRESH_CNONE_CIM_RESOURCE_ADMISSION',passed=bool(authority['CNone'] and resource['passed'] and cim['passed']),
   run_id=run,new_job_root=J,canonical_path=authority['canonical_path'],canonical_generation=authority['generation'],
   canonical_active=authority['active_segment'],canonical_total_authorized_seconds=authority['total_authorized_seconds'],
   fresh_LOCAL_exact_CIM_passed=cim['passed'],private_EX_probe_free=resource['private_EX_probe_free'],shared_EX_probe_free=resource['shared_EX_probe_free'],
   no_new_writer_grant_copy_refund_or_hotadd=True,CNone_checked_epoch=authority['epoch'],LOCAL_exact_CIM_checked_epoch=cim['epoch'],resource_checked_epoch=resource['epoch'],
   control_snapshot_id='ROOT227D_CNONE_'+authority['SHA']+'_'+str(authority['epoch']),
   fresh_CNone_receipt_SHA=H(R/'ROOT227D_FRESH72_CNONE_BEFORE_FROZEN_TASK_ACTUAL.json'),
   fresh_LOCAL_exact_CIM_receipt_SHA=H(R/'ROOT227D_START_FRESH_LOCAL_EXACT_CIM.json'),
   fresh_resource_receipt_SHA=H(R/'ROOT227D_FRESH_SELECTED_GPU_PRIVATE_SHARED_LIGHT_ACTUAL.json'),
   **{k:resource[k] for k in ('GPU_UUID','GPU_name','GPU_free_MiB','GPU_util_percent','RAM_available_bytes','disk_free_bytes')})
  put('ROOT227D_FRESH_ACTUAL_ADMISSION_FOR_A_TASK.json',fresh)
  merged=dict(install,files=install['files']+post['generated_metadata_rows'])
  put('ROOT227D_INSTALL_ROWS_WITH_ORIGINAL_ASSET_RECEIPT_ACTUAL.json',merged)
  staging=N/'ROOT227D_ACTUAL_TASK_STAGING'
  command=[sys.executable,'-B','-X','utf8',str(A/'prepare227_Task_manifest_Ready_SOURCE_ONLY.py'),
   '--qualified-closing',str(args.closing),'--qualified-cpu',str(args.new_w35_cpu),
   '--fresh-admission',str(R/'ROOT227D_FRESH_ACTUAL_ADMISSION_FOR_A_TASK.json'),
   '--install-rows',str(R/'ROOT227D_INSTALL_ROWS_WITH_ORIGINAL_ASSET_RECEIPT_ACTUAL.json'),
   '--job-root',J,'--run-id',run,'--out',str(staging)]
  completed=subprocess.run(command,capture_output=True,text=True,encoding='utf8')
  put('ROOT227D_A_TASK_GENERATOR_ORIGINAL_RETURNED_ACTUAL.json',dict(returncode=completed.returncode,stdout=completed.stdout,stderr=completed.stderr))
  assert completed.returncode==0
  task=read(staging/'TASK.json');ready=read(staging/'ADMISSION227_READY.json');spec=read(staging/'SPEC227_ORIGINAL_OWNER_FIELDS.json')
  spec.update(private_lock=resource['private_lock'],python=d.PY72,role='node',run_id=run)
  assert validate_ready(ready,spec)
  schedule=dict(run_id=run,scheduling_authority='human_requested_available_experts',owner_root=O,experts=dict(w35_72=spec),deferred_experts=[])
  added={name:(staging/name).read_bytes() for name in ('TASK.json','PRELAUNCH227_ACTUAL_EVIDENCE.json','MANIFEST227.json','ADMISSION227_READY.json')}
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for rel,data in added.items():stage(sf,J+'/'+rel,data)
   for root in (O,J+'/control227'):
    stage(sf,root+'/SCHEDULE_PUBLIC.json',raw(schedule))
    for row in control['files']:stage(sf,root+'/'+row['relative'],Path(row['local_path']).read_bytes())
  finally:sf.close()
  put('ROOT227D_ACTUAL_TASK_MANIFEST_READY_AND_PUBLIC_SCHEDULE.json',dict(epoch=time.time(),run_id=run,task=task,manifest_SHA=spec['manifest_SHA'],
   launch_evidence_SHA=spec['launch_evidence_SHA'],ready=ready,schedule=schedule,model_read_by_join=0))
  verify=d.code(client,d.PY72,VERIFY_METADATA,dict(owner=O,job=J,controls=control['files'],schedule_SHA=H_bytes(raw(schedule)),newmeta={k:H_bytes(v) for k,v in added.items()}),timeout=60)
  put('ROOT227D_CONTROL_AND_NEW_METADATA_POSTCOPY_ACTUAL.json',verify);assert verify['passed']
  put('ROOT227D_FRESH72_CNONE_AGAIN_BEFORE_ORIGINAL_OWNER.json',d.code(client,d.PY72,target.AUTH,{},timeout=45))
  token=secrets.token_hex(32);private_spec=dict(spec,token=token)
  cfg=dict(role='owner',run_id=run,token=token,scheduling_authority='human_requested_available_experts',experts=dict(w35_72=private_spec),deferred_experts=[])
  owner=d.code(client,d.PY72,target.SPAWN,dict(root=O,module='solo227_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg,expected_control_cwd=CONTROL_CWD),timeout=30)
  assert owner['cwd']==CONTROL_CWD and owner['root']==O
  put('ROOT227D_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json',dict(run_id=run,owner=owner,specs=dict(w35_72=spec)))
  node=d.code(client,d.PY72,target.SPAWN,dict(root=J+'/control227',module='solo227_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=private_spec,expected_control_cwd=CONTROL_CWD),timeout=30)
  assert node['cwd']==CONTROL_CWD and node['root']==J+'/control227'
  put('ROOT227D_ORIGINAL_W35_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=node))
  first=d.code(client,d.PY72,target.FIRST,dict(job=J,source_SHA=SHA),timeout=900)
  put('ROOT227D_W35_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',first)
  state=d.code(client,d.PY72,target.OWNER_STATE,dict(owner=owner),timeout=45)
  put('ROOT227D_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json',state)
  assert first['passed'] and state['current_owner_matched'] and set(state['current']['go'])=={'w35_72'}
  print(json.dumps(dict(passed=True,run_id=run,owner=owner,node=node,first=first['first'],GO=state['current']['go']['w35_72'],one_original_writer=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT227D_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))


def H_bytes(data):return hashlib.sha256(data).hexdigest()


if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT227D_START_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_or_GO=True));raise
