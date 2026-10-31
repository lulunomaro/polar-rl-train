"""ROOT-reviewed delegated launch. One original writer, two actual PPO slots."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,posixpath,secrets,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
E=T/'E0_82_LITERAL_FUDAN_JUMP72_ONE_HOUR_SOURCE_V198_20261031'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
AUTH="""from pathlib import Path
import json,time,hashlib
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=p.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[] and c['active_segment'] is None
assert c['remaining_training_seconds']>86412.86069250107+v['total_caps']
print(json.dumps(dict(epoch=time.time(),CNone=True,remaining_snapshot=c['remaining_training_seconds'],reserve_required=v['total_caps'],SHA=hashlib.sha256(raw).hexdigest(),account_write=False)))"""
SPAWN="""from pathlib import Path
import importlib.util,sys,os,json,psutil
B=Path(v['root']);sys.path.insert(0,str(B));p=B/v['module'];s=importlib.util.spec_from_file_location('owned197_launch',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
assert not (B/v['console']).exists();pid=os.fork()
if pid:
 q=psutil.Process(pid);print(json.dumps(dict(pid=pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),cwd=q.cwd(),root=str(B),role=v['role'])),flush=True)
else:
 os.setsid();fd=os.open(str(B/v['console']),os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.dup2(fd,1);os.dup2(fd,2);os.close(fd);fd=os.open('/dev/null',os.O_RDONLY);os.dup2(fd,0);os.close(fd)
 if v['role']=='owner':m.owner(v['config'])
 else:m.node(v['config'])
"""
FIRST="""from pathlib import Path
import json,time,hashlib
B=Path(v['job']);C=B/'control197';f=B/'production/FIRST_ACTUAL_NEW_PPO_UPDATE.json';end=time.time()+850
while time.time()<end and not f.is_file() and not (C/'NODE_TERMINAL_ACTUAL.json').is_file():time.sleep(2)
paths=[C/'NODE_IDENTITY.json',C/'WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json',C/'NODE_CURRENT.json',C/'ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json',C/'NODE_ORIGINAL_ERROR.json',C/'NODE_TERMINAL_ACTUAL.json',C/'NODE_EXIT_ACTUAL.json',B/'GO_PRODUCTION.json',B/('production/'+v['restore']),f,B/'production/latest_complete.json',B/'production/LATEST_PROGRESS.json',B/'production/ORIGINAL_ERROR.json',B/'production/FINAL.json']
rows=[]
for p in paths:
 if not p.is_file():continue
 raw=p.read_bytes();rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8')))
value=json.loads(f.read_bytes()) if f.is_file() else None
log=C/'production_WORKER.log';prefix=None
if log.is_file():
 size=log.stat().st_size
 with log.open('rb') as stream:raw=stream.read(size)
 prefix=dict(path=str(log),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace'),scope='Original stdout prefix at one FIRST collection, not final full log or continued liveness')
print(json.dumps(dict(epoch=time.time(),key=v['key'],passed=bool(value and value.get('passed') and value.get('actual_new_PPO_updates')==1),first=value,full_selected_UTF8=rows,original_stdout_prefix=prefix,single_first_wait850=True,snapshot_not_final_or_skill=True)))"""
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True);args=parser.parse_args()
 assert args.root_lease_label.startswith('ROOT197_EXCLUSIVE_UNIFIED_START_')
 schedule=read(N/'SCHEDULE_PUBLIC.json');specs=schedule['experts'];OWNER=schedule['owner_root'];total=sum(s['max_parent_seconds'] for s in specs.values())
 assert read(R/'ROOT197_TWO_ROLE_TaskGO_SOURCE_CPU_ACTUAL.json')['passed'] and read(R/'ROOT197_SAVED194_INITIAL_CPU_RETURNED_ACTUAL.json')['passed']
 assert read(E/'reports/ACTUAL198_TARGET72_CPU_NATIVE64_ADMISSION_RETURNED.json')['passed_execution']
 assert read(E/'reports/ACTUAL198_ADMIT_ALL_SSH_CLOSED_SESSION_RESTORED.json')['global_serial_control_client_lease']=='FREE'
 primary=read(N/'PRIMARY197_COMPLETE_MANIFEST.json');controls=read(N/'CONTROL197_MANIFEST.json')
 for row in primary['files']:
  p=N/row['local_relative'];assert p.stat().st_size==row['bytes']
  if p.suffix.lower() not in ('.usd','.usda','.npz','.npy'):assert H(p)==row['SHA']
 for row in controls['files']:assert H(row['local_path'])==row['SHA']
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'launch197_unified_194_remaining_and_E0_hour_FIRST_once|request197_original194_saved_handoff|install198_E0_72_source_CPU_native64_admission_once|human196_194_one_saved_progress|collect194_original|start194_literal|install195_literal|start195_literal|collect195_original|run189_W35_saved_cycle|install_capture193_|install_evaluate191_' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ROOT197_UNIFIED_START_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,exact_CIM=rows,other_known_finites=other))
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT197_UNIFIED_START_ONCE_CONSUMED_BEFORE_GO.json',dict(epoch=time.time(),root_lease_label=args.root_lease_label,
  roles=list(specs),old194_actual_full_close_and_saved_CPU_passed=True,old194_normal900_entry_not_used=True,
  primary_remaining_seconds=specs['h1_210']['remaining_primary_seconds'],E0_train_seconds=3600,total_reserved_caps=total,
  maximum_source194_GPU_reads=1,maximum_E0_GPU_reads=1,new_CPU_model_reads=0,raw_old_cases=0,
  reset_NPZ_original_constructor_only=True,one_owner_original_sum_distinct_actual_fees=True,first_collector_per_role_once=True,
  no_budget_grant_or_second_writer_or_canonical_copy=True))
 wrapper=module('unified197_session',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('unified197_memory_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover()
  client=d.connect72(secret)
  try:put('ROOT197_FRESH72_CNONE_RESERVE_BEFORE_STAGE.json',d.code(client,d.PY72,AUTH,dict(total_caps=total),timeout=45))
  finally:client.close();client=None
  client=route.connect();J=specs['h1_210']['job_root']
  pre="""from pathlib import Path
import json,subprocess
B=Path(v['job']);m=json.loads(subprocess.check_output(['findmnt','--json','--target','/mnt/mod4_linux_durable_20261013','-o','UUID,OPTIONS'],text=True))['filesystems'][0]
assert str(m['uuid']).upper()=='EF3105C85DD986BD' and 'rw' in m['options'].split(',')
B.mkdir(parents=True,exist_ok=False);(B/'control197').mkdir()
print(json.dumps(dict(passed=True,new_root=str(B),UUID_rw=m)))"""
  put('ROOT197_PRIMARY_NEW_UUID_NAMESPACE.json',d.code(client,route.PY,pre,dict(job=J),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(120)
  try:
   made=set()
   for row in primary['files']:
    cur=J
    for bit in posixpath.dirname(row['relative']).split('/'):
     if not bit:continue
     cur+='/'+bit
     if cur not in made:
      try:sf.mkdir(cur)
      except OSError:sf.stat(cur)
      made.add(cur)
    sf.put(str(N/row['local_relative']),J+'/'+row['relative'])
   sf.put(str(N/'PRIMARY197_COMPLETE_MANIFEST.json'),J+'/PRIMARY197_COMPLETE_MANIFEST.json')
   sf.put(str(N/'ADMISSION197_READY_h1_210.json'),J+'/ADMISSION197_READY.json')
   sf.put(str(N/'SCHEDULE_PUBLIC.json'),J+'/control197/SCHEDULE_PUBLIC.json')
   for row in controls['files']:sf.put(row['local_path'],J+'/control197/'+row['relative'])
  finally:sf.close()
  client.close();client=None
  client=d.connect72(secret)
  stage="""from pathlib import Path
import json
B=Path(v['owner']);B.mkdir(parents=True,exist_ok=False)
J=Path(v['E0job']);assert json.loads((J/'ADMISSION198_ACTUAL.json').read_bytes())['passed']
(J/'control197').mkdir()
print(json.dumps(dict(passed=True,owner_root=str(B),E0_existing_admission=True)))"""
  put('ROOT197_OWNER_AND_E0_NODE_NAMESPACES.json',d.code(client,d.PY72,stage,dict(owner=OWNER,E0job=specs['e0_72']['job_root']),timeout=30))
  sf=client.open_sftp()
  try:
   for base in (OWNER,specs['e0_72']['job_root']+'/control197'):
    sf.put(str(N/'SCHEDULE_PUBLIC.json'),base+'/SCHEDULE_PUBLIC.json')
    for row in controls['files']:sf.put(row['local_path'],base+'/'+row['relative'])
   sf.put(str(N/'ADMISSION197_READY_e0_72.json'),specs['e0_72']['job_root']+'/ADMISSION197_READY.json')
  finally:sf.close()
  put('ROOT197_FRESH72_CNONE_AGAIN_BEFORE_OWNER.json',d.code(client,d.PY72,AUTH,dict(total_caps=total),timeout=45))
  token=secrets.token_hex(32);run='PARALLEL197_194REMAIN_E0JUMP_'+str(time.time_ns())
  for key,spec in specs.items():
   spec.update(role='node',run_id=run,token=token)
   if key=='h1_210':spec.update(owner_ssh_password=secret,owner_control_dependency_binding_SHA=H(N/'control/OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json'))
  cfg=dict(role='owner',run_id=run,token=token,scheduling_authority='human_requested_available_experts',experts=specs,deferred_experts=[])
  owner=d.code(client,d.PY72,SPAWN,dict(root=OWNER,module='parallel197_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg),timeout=30)
  clean={k:{name:value for name,value in s.items() if name not in ('token','owner_ssh_password')} for k,s in specs.items()}
  put('ROOT197_ORIGINAL_UNIFIED_OWNER_LAUNCH_ACTUAL.json',dict(run_id=run,owner=owner,specs=clean))
  nodeE=d.code(client,d.PY72,SPAWN,dict(root=specs['e0_72']['job_root']+'/control197',module='parallel197_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=specs['e0_72']),timeout=30)
  put('ROOT197_E0_72_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=nodeE))
  client.close();client=None
  client=route.connect()
  nodeH=d.code(client,route.PY,SPAWN,dict(root=J+'/control197',module='parallel197_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=specs['h1_210']),timeout=30)
  put('ROOT197_PRIMARY210_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=nodeH))
  firstH=d.code(client,route.PY,FIRST,dict(key='h1_210',job=J,restore='ACTUAL197_CUDA_FULLSTATE_RESTORE_BEFORE_NEW_CONTROL.json'),timeout=900)
  put('ROOT197_PRIMARY210_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',firstH)
  client.close();client=None
  client=d.connect72(secret)
  firstE=d.code(client,d.PY72,FIRST,dict(key='e0_72',job=specs['e0_72']['job_root'],restore='ACTUAL198_CUDA_FULLSTATE_RESTORE_BEFORE_NEW_CONTROL.json'),timeout=900)
  put('ROOT197_E0_72_FIRST_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json',firstE)
  proof="""from pathlib import Path
import json,time
B=Path(v['owner']);c=json.loads(Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json').read_bytes());a=c['active_segment'];current=json.loads((B/'OWNER_CURRENT.json').read_bytes())
if a is not None:assert a['owner_parent_pid']==v['pid']
files={}
for name in ['OWNER_IDENTITY.json','OWNER_CURRENT.json','COHORT_FINAL.json','OWNER_EXIT_ACTUAL.json','OWNER_ORIGINAL_ERROR.json']:
 p=B/name
 if p.is_file():files[name]=json.loads(p.read_bytes())
print(json.dumps(dict(epoch=time.time(),current_owner_matched=a is not None and a['owner_parent_pid']==v['pid'],canonical_None=a is None,current=current,files=files,no_account_write=True)))"""
  state=d.code(client,d.PY72,proof,dict(owner=OWNER,pid=owner['pid']),timeout=45)
  put('ROOT197_UNIFIED_OWNER_AND_CANONICAL_AFTER_FIRST_ACTUAL.json',state)
  print(json.dumps(dict(run_id=run,primary_FIRST=firstH['passed'],E0_FIRST=firstE['passed'],owner=owner,nodes=dict(primary=nodeH,E0=nodeE),GO=state['current']['go'],one_owner=state['current_owner_matched'])),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT197_UNIFIED_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT197_UNIFIED_START_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry_or_extra_GO=True));raise
