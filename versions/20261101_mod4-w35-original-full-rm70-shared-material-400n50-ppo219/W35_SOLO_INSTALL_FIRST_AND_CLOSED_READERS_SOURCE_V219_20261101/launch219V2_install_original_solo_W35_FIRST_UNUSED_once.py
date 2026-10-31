"""ROOT ONLY unused installer + original sole owner/node + ONE FIRST.

No network/import of transport until matching210 normal closure/new CPU pass.
"""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,secrets,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(N/'source'))
from bridge219 import load_closed_e0,closed_bridge,CLOSING,CPU
from contract218 import KIND,SHA,ITER,ADAM,LR,validate_task,validate_manifest,validate_ready
import remote219_payloads as target


def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def raw(v):return json.dumps(v,indent=2).encode()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m


def exact_cim():
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'launch219V2_|launch219_|collect219_|review219_|collect210_|launch210_|review210_|install21[1-9]_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 return dict(epoch=time.time(),passed=True,PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,other_known_control_finites=other)


def stage(sf,remote,data):
 parent=str(Path(remote).parent).replace('\\','/');parts=parent.split('/');cur=''
 for part in parts:
  if not part:continue
  cur+='/'+part
  try:sf.mkdir(cur)
  except OSError:sf.stat(cur)
 with sf.file(remote,'wx') as f:f.write(data);f.flush()


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True)
 parser.add_argument('--closing',type=Path,default=CLOSING);parser.add_argument('--new-e0-cpu',type=Path,default=CPU)
 args=parser.parse_args()
 e0=load_closed_e0(args.closing,args.new_e0_cpu)  #FIRST gate;nothing remote/assets/PT precedes it.
 assert args.root_lease_label.startswith('ROOT219_EXCLUSIVE_W35_SOLO_')
 assert read(R/'CPU219_NEW_CALLER_METADATA_ACTUAL.json')['passed']
 assert H(N/'INDEX219_FROZEN.json')=='dfc17386feee6ebdeabd73a27e927d4d00a933c30a7e1c8ca9e34ae970bf0043'
 index=read(N/'INDEX219_FROZEN.json')
 for row in index['files']:assert H(N/row['relative'])==row['SHA']
 install=read(R/'INSTALL219_SOURCE_ROWS_FROZEN.json');control=read(R/'CONTROL219_FROZEN_MANIFEST.json')
 cim=exact_cim();put('ROOT219_START_FRESH_LOCAL_EXACT_CIM.json',cim)
 run='W35_SHARED214_SOLO219_'+str(time.time_ns())
 base='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_SHARED214_SOLO219_'+str(time.time_ns())
 J=base+'/w35_72';O=base+'/owner72'
 put('ROOT219_START_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),run_id=run,
  root_lease_label=args.root_lease_label,closed210_inputs=e0['refs'],roles=['w35_72'],
  source_SHA=SHA,source_iteration=ITER,Adam17=ADAM,LR=LR,finite_learning_seconds=3600,max_parent_seconds=3900,
  necessary_old_W35_input_streamcopy=1,worker_new_copy_physical_byte_read_decode=1,
  old_CPU_PT_reads=0,raw_trajectory_reads=0,source_asset_postcopy_once_each_new_training_namespace=True,
  original_constructor_reset_NPZ_and_CAD_NPZ_only=True,one_original_writer=True,no_hotadd210_or_new_grant=True,
  FIRST_once=True,max_FIRST_wait_seconds=850))
 wrapper=module('root219_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('root219_memory_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret)
  put('ROOT219_FRESH72_CNONE_RESERVE_THEN_CLOSE72_ACTUAL.json',d.code(client,d.PY72,target.AUTH,{},timeout=45))
  client.close();client=None  #Authority control closed before the target control client.
  client=d.connect72(secret);secret=None
  put('ROOT219_NEW_UNUSED_NAMESPACES_ACTUAL.json',d.code(client,d.PY72,target.CREATE,dict(job=J,owner=O),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for row in install['files']:
    assert not row['relative'].endswith('.pt')
    #Actual root installer purpose owns these source/asset transfers;child never did them.
    cur=J
    for part in row['relative'].split('/')[:-1]:
     cur+='/'+part
     try:sf.mkdir(cur)
     except OSError:sf.stat(cur)
    sf.put(row['local_path'],J+'/'+row['relative'])
  finally:sf.close()
  post=d.code(client,d.PY72,target.POSTCOPY_AND_SOURCE_COPY,dict(job=J,files=install['files'],source=install['source_model']),timeout=180)
  put('ROOT219_SOURCE_ASSET_POSTCOPY_AND_SINGLE_W35_INPUT_COPY_ACTUAL.json',post);assert post['passed']
  authority=d.code(client,d.PY72,target.AUTH,{},timeout=45)
  put('ROOT219_FRESH72_CNONE_BEFORE_FROZEN_TASK_ACTUAL.json',authority)
  bridge=closed_bridge(e0,authority,cim);put('ROOT219_CLOSED210_MATCHING_CPU_FRESH_ADMISSION_BRIDGE_ACTUAL.json',bridge)
  bridge_bytes=raw(bridge);bridge_sha=hashlib.sha256(bridge_bytes).hexdigest()
  evidence=dict(schema='mod4.218.closed_actual_selectors.v1',status='CLOSED_ACTUAL_ONLY',
   reports=dict(closed=dict(relative='closed_evidence/ROOT219_CLOSED_BRIDGE_ACTUAL.json',bytes=len(bridge_bytes),SHA=bridge_sha,complete=True)),
   facts={k:dict(report='closed',pointer='/facts/'+k) for k in bridge['facts']})
  eb=raw(evidence);esha=hashlib.sha256(eb).hexdigest()
  p218=T/'W35_SHARED_MATERIAL_NEXT_SOLO_SOURCE_V218_20261101'
  task=read(p218/'reports/TASK218_TEMPLATE_NOT_ACTIVE.json')
  task.update(status='ROOT_ACTUAL_FROZEN_NEXT_W35_TASK',run_id=run,GPU_UUID='GPU-c27eecbd-6838-7290-1cd2-37e34522213d',
   actual_private_EX_held_by_parent=True,launch_evidence_SHA=esha,manifest_file='PACKAGE219_MANIFEST.json')
  assert validate_task(task)
  tb=raw(task)
  added={'TASK.json':tb,'PRELAUNCH218_CLOSED_EVIDENCE.json':eb,'closed_evidence/ROOT219_CLOSED_BRIDGE_ACTUAL.json':bridge_bytes}
  rows=[{k:v for k,v in x.items() if k in ('relative','bytes','SHA','asset_relative')} for x in install['files']]
  rows+=post['generated_metadata_rows']
  rows += [dict(relative=k,bytes=len(v),SHA=hashlib.sha256(v).hexdigest()) for k,v in added.items()]
  manifest=dict(kind=KIND,files=rows,input_model_metadata=dict(SHA=SHA,bytes=17619013,iteration=ITER,Adam17=ADAM))
  assert validate_manifest(manifest);mb=raw(manifest);msha=hashlib.sha256(mb).hexdigest()
  spec=dict(key='w35_72',execution_backend='target72',GPU_UUID=task['GPU_UUID'],source_SHA=SHA,source_iteration=ITER,
   source_Adamstep=ADAM,source_kind=KIND,max_parent_seconds=3900,exit_headroom_seconds=300,num_envs=20000,no_physics_change=True,
   prelaunch_control_snapshot_id=bridge['facts']['fresh_control_snapshot_id'],manifest_SHA=msha,launch_evidence_SHA=esha,
   manifest_file='PACKAGE219_MANIFEST.json',worker_script='worker_full218.py',job_root=J,
   private_lock='/home/lc01/Zonglin Li/zonglin2/state/three_expert_v2_'+task['GPU_UUID']+'.lock',python=d.PY72,role='node',run_id=run)
  ready=read(p218/'reports/READY218_TEMPLATE_NOT_ACTIVE.json')
  ready.update(passed=True,status='ROOT_CLOSED_ACTUAL_READY_NEW_W35_WINDOW',manifest_SHA=msha,launch_evidence_SHA=esha,
   E0_210_closed_new_formal_CPU_and_fresh_CNone=True)
  assert validate_ready(ready,spec)
  schedule=dict(run_id=run,scheduling_authority='human_requested_available_experts',owner_root=O,experts=dict(w35_72=spec),deferred_experts=[])
  added.update({'PACKAGE219_MANIFEST.json':mb,'ADMISSION218_READY.json':raw(ready)})
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   for rel,data in added.items():stage(sf,J+'/'+rel,data)
   for root in (O,J+'/control219'):
    stage(sf,root+'/SCHEDULE_PUBLIC.json',raw(schedule))
    for row in control['files']:stage(sf,root+'/'+row['relative'],Path(row['local_path']).read_bytes())
  finally:sf.close()
  put('ROOT219_ACTUAL_TASK_MANIFEST_READY_AND_PUBLIC_SCHEDULE.json',dict(epoch=time.time(),run_id=run,task=task,manifest_SHA=msha,
   launch_evidence_SHA=esha,ready=ready,schedule=schedule,model_read_by_join=0))
  verify='''from pathlib import Path
import hashlib,json
for root in (v['owner'],v['job']+'/control219'):
 for r in v['controls']:
  p=Path(root)/r['relative'];assert p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['SHA']
 assert hashlib.sha256((Path(root)/'SCHEDULE_PUBLIC.json').read_bytes()).hexdigest()==v['schedule_SHA']
for rel,sha in v['newmeta'].items():assert hashlib.sha256((Path(v['job'])/rel).read_bytes()).hexdigest()==sha
print(json.dumps(dict(passed=True,control_source_postcopy_passes=1,model_reads=0)))'''
  put('ROOT219_CONTROL_AND_NEW_METADATA_POSTCOPY_ACTUAL.json',d.code(client,d.PY72,verify,dict(owner=O,job=J,controls=control['files'],schedule_SHA=hashlib.sha256(raw(schedule)).hexdigest(),newmeta={k:hashlib.sha256(v).hexdigest() for k,v in added.items()}),timeout=60))
  put('ROOT219_FRESH72_CNONE_AGAIN_BEFORE_ORIGINAL_OWNER.json',d.code(client,d.PY72,target.AUTH,{},timeout=45))
  token=secrets.token_hex(32);private_spec=dict(spec,token=token)
  cfg=dict(role='owner',run_id=run,token=token,scheduling_authority='human_requested_available_experts',experts=dict(w35_72=private_spec),deferred_experts=[])
  owner=d.code(client,d.PY72,target.SPAWN,dict(root=O,module='solo219_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg),timeout=30)
  put('ROOT219_ORIGINAL_SOLO_OWNER_LAUNCH_ACTUAL.json',dict(run_id=run,owner=owner,specs=dict(w35_72=spec)))
  node=d.code(client,d.PY72,target.SPAWN,dict(root=J+'/control219',module='solo219_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=private_spec),timeout=30)
  put('ROOT219_ORIGINAL_W35_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=node))
  first=d.code(client,d.PY72,target.FIRST,dict(job=J,source_SHA=SHA),timeout=900)
  put('ROOT219_W35_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',first)
  state=d.code(client,d.PY72,target.OWNER_STATE,dict(owner=owner),timeout=45)
  put('ROOT219_ORIGINAL_SOLO_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json',state)
  assert first['passed'] and state['current_owner_matched']
  assert set(state['current']['go'])=={'w35_72'}
  print(json.dumps(dict(passed=True,run_id=run,owner=owner,node=node,first=first['first'],GO=state['current']['go']['w35_72'],one_original_writer=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT219_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))


if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT219_START_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_or_GO=True));raise
