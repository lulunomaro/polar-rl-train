"""One sole72 owner, one genuine209 branch, one original FIRST collection."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,os,secrets,subprocess,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def read(p):return json.loads(Path(p).read_bytes())
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
AUTH="""from pathlib import Path
import hashlib,json,time
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=p.read_bytes();c=json.loads(raw)
assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['authorized_training_seconds']==2268000 and c['new_authority_budget_extensions']==[] and c['active_segment'] is None
assert c['remaining_training_seconds']>86412.86069250107+3900
print(json.dumps(dict(epoch=time.time(),CNone=True,remaining_snapshot=c['remaining_training_seconds'],reserve_required=3900,SHA=hashlib.sha256(raw).hexdigest(),account_write=False)))"""
SPAWN="""from pathlib import Path
import importlib.util,sys,os,json,psutil
B=Path(v['root']);sys.path.insert(0,str(B));p=B/v['module'];s=importlib.util.spec_from_file_location('owned209_launch',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
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
B=Path(v['job']);C=B/'control209';f=B/'production/FIRST_ACTUAL_NEW_PPO_UPDATE.json';end=time.time()+850
while time.time()<end and not f.is_file() and not (C/'NODE_TERMINAL_ACTUAL.json').is_file():time.sleep(2)
paths=[C/'NODE_IDENTITY.json',C/'WORKER_ORIGINAL_IDENTITY_BEFORE_WAIT.json',C/'NODE_CURRENT.json',C/'ACTUAL_COLD_START_RESOURCE_PRIVATE_EX.json',C/'NODE_ORIGINAL_ERROR.json',C/'NODE_TERMINAL_ACTUAL.json',C/'NODE_EXIT_ACTUAL.json',B/'GO_PRODUCTION.json',B/'production/ACTUAL209_CUDA_FULLSTATE_RESTORE_BEFORE_NEW_CONTROL.json',f,B/'production/latest_complete.json',B/'production/LATEST_PROGRESS.json',B/'production/ORIGINAL_ERROR.json',B/'production/FINAL.json',B/'production/ACTUAL_SOURCE209_LITERAL_REWARD_AND_TARGET_PLANT_BEFORE_ACTION.json']
rows=[]
for p in paths:
 if not p.is_file():continue
 raw=p.read_bytes();rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8')))
value=json.loads(f.read_bytes()) if f.is_file() else None
log=C/'production_WORKER.log';prefix=None
if log.is_file():
 size=log.stat().st_size
 with log.open('rb') as stream:raw=stream.read(size)
 prefix=dict(path=str(log),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),UTF8=raw.decode('utf8','replace'),scope='Original stdout prefix at one FIRST collection, not final log or continued liveness')
print(json.dumps(dict(epoch=time.time(),passed=bool(value and value.get('passed') and value.get('actual_new_PPO_updates')==1),first=value,full_selected_UTF8=rows,original_stdout_prefix=prefix,single_first_wait850=True,snapshot_not_final_or_skill=True)))"""

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root-lease-label',required=True);args=parser.parse_args()
 assert args.root_lease_label.startswith('ROOT209_EXCLUSIVE_SINGLE_START_')
 assert read(R/'ROOT209_OWNER_WORKER_ACTUAL_ADMISSION_JOIN_CPU_ACTUAL.json')['passed']
 assert read(R/'ACTUAL209_ADMIT_ALL_SSH_CLOSED_SESSION_RESTORED.json')['global_serial_control_client_lease']=='FREE'
 schedule=read(N/'SCHEDULE_PUBLIC.json');spec=schedule['experts']['e0_72'];J=spec['job_root'];OWNER=schedule['owner_root']
 assert set(schedule['experts'])=={'e0_72'} and spec['source_iteration']==32066
 controls=read(N/'CONTROL209_MANIFEST.json')
 for row in controls['files']:assert H(row['local_path'])==row['SHA']
 assert H(N/'PACKAGE209_MANIFEST.json')==spec['manifest_SHA']
 query=r'''Get-CimInstance Win32_Process -Filter "Name='python.exe' OR Name='ssh.exe'" | Where-Object { $_.CommandLine -match 'launch209_original_single_writer_mixed_FIRST_once|install209_|collect209_|install208_|launch208_|launch197_|collect197_|install207_|evaluate207_|human196_|collect194_|start194_|install195_|run189_W35_saved_cycle' } | Select-Object Name,ProcessId,CreationDate,ExecutablePath,CommandLine | ConvertTo-Json -Depth 5 -Compress'''
 p=subprocess.run(['pwsh.exe','-NoProfile','-Command',query],capture_output=True,text=True,encoding='utf8',check=True)
 rows=json.loads(p.stdout) if p.stdout.strip() else [];rows=rows if isinstance(rows,list) else [rows]
 own=[x for x in rows if x['ProcessId']==os.getpid()];other=[x for x in rows if x['ProcessId']!=os.getpid()]
 put('ROOT209_START_FRESH_LOCAL_EXACT_CIM.json',dict(epoch=time.time(),PID=os.getpid(),exe=sys.executable,argv=sys.argv,rows=rows,other_known_finites=other))
 assert len(own)==1 and own[0]['CreationDate'] and own[0]['ExecutablePath'].lower()==sys.executable.lower() and not other
 assert str(Path(__file__).resolve()).lower().replace('\\','/') in own[0]['CommandLine'].lower().replace('\\','/')
 put('ROOT209_START_ONCE_CONSUMED_BEFORE_NETWORK.json',dict(epoch=time.time(),root_exclusive_lease_label=args.root_lease_label,roles=['e0_72'],
  source_SHA=spec['source_SHA'],source_iteration=32066,Adam17=642840,
  necessary_new_training_GPU_input_byte_reads=1,necessary_new_training_GPU_decode=1,old_CPU_model_reads=0,raw_cases_reads=0,
  reset_NPZ_original_constructor_only=True,one_original_writer=True,source_runtime_node_integrity_one_training_purpose=True,
  finite_learning_seconds=3600,max_parent_seconds=3900,no_second_writer_or_grant=True))
 wrapper=module('mixed209_transport',T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v227.py')
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 client=None;transport=None;previous=None;secret=None
 try:
  transport,previous=wrapper.install();sec=module('mixed209_memory_auth',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');secret=sec.recover();client=d.connect72(secret)
  put('ROOT209_FRESH72_CNONE_BEFORE_CONTROL_STAGE.json',d.code(client,d.PY72,AUTH,{},timeout=45))
  create="""from pathlib import Path
import json,time,shutil,psutil
O=Path(v['owner']);J=Path(v['job']);owned=Path('/home/lc01/Zonglin Li/zonglin2').resolve()
assert O.resolve().is_relative_to(owned/'tasks') and J.resolve().is_relative_to(owned/'tasks') and J.is_dir()
assert not O.exists() and not (J/'control209').exists() and not (J/'ADMISSION209_READY.json').exists()
assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(J).free>25*1024**3
O.mkdir(parents=True);(J/'control209').mkdir()
print(json.dumps(dict(passed=True,owner=str(O),node=str(J/'control209'),no_model_GPU_read_or_account_write=True)))"""
  put('ROOT209_NEW_CONTROL_NAMESPACES_ACTUAL.json',d.code(client,d.PY72,create,dict(owner=OWNER,job=J),timeout=30))
  sf=client.open_sftp();sf.get_channel().settimeout(90)
  try:
   for base in (OWNER,J+'/control209'):
    sf.put(str(N/'SCHEDULE_PUBLIC.json'),base+'/SCHEDULE_PUBLIC.json')
    for row in controls['files']:sf.put(row['local_path'],base+'/'+row['relative'])
   sf.put(str(N/'ADMISSION209_READY.json'),J+'/ADMISSION209_READY.json')
  finally:sf.close()
  verify="""from pathlib import Path
import hashlib,json
for root in (v['owner'],v['job']+'/control209'):
 B=Path(root)
 for row in v['files']:
  p=B/row['relative'];assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
 assert hashlib.sha256((B/'SCHEDULE_PUBLIC.json').read_bytes()).hexdigest()==v['schedule_SHA']
print(json.dumps(dict(passed=True,control_source_postcopy_passes=1,roots=2)))"""
  put('ROOT209_ACTUAL_CONTROL_POSTCOPY_INTEGRITY.json',d.code(client,d.PY72,verify,dict(owner=OWNER,job=J,files=controls['files'],schedule_SHA=H(N/'SCHEDULE_PUBLIC.json')),timeout=45))
  put('ROOT209_FRESH72_CNONE_AGAIN_BEFORE_OWNER.json',d.code(client,d.PY72,AUTH,{},timeout=45))
  token=secrets.token_hex(32);run='ONE209_E0_GROUND10_JUMP90_'+str(time.time_ns())
  spec.update(role='node',run_id=run,token=token)
  cfg=dict(role='owner',run_id=run,token=token,scheduling_authority='human_requested_available_experts',experts={'e0_72':spec},deferred_experts=[])
  owner=d.code(client,d.PY72,SPAWN,dict(root=OWNER,module='mixed209_finite_owner_authority72.py',console='owner_CONSOLE.log',role='owner',config=cfg),timeout=30)
  put('ROOT209_ORIGINAL_OWNER_LAUNCH_ACTUAL.json',dict(run_id=run,owner=owner,spec={k:v for k,v in spec.items() if k!='token'}))
  node=d.code(client,d.PY72,SPAWN,dict(root=J+'/control209',module='mixed209_fullstate_slot_node.py',console='node_CONSOLE.log',role='node',config=spec),timeout=30)
  put('ROOT209_ORIGINAL_NODE_LAUNCH_ACTUAL.json',dict(run_id=run,node=node))
  first=d.code(client,d.PY72,FIRST,dict(job=J),timeout=900)
  put('ROOT209_FIRST_ACTUAL_NEW_PPO_OR_ORIGINAL_ERROR_RETURNED.json',first)
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
  put('ROOT209_ORIGINAL_OWNER_AND_CANONICAL_AFTER_FIRST.json',state)
  assert first['passed'] and first['first']['new_Adam_step']==642860 and first['first']['first_complete']['saved_iteration']==32067
  assert state['current_owner_matched']
  print(json.dumps(dict(passed=True,run_id=run,owner=owner,node=node,first=first['first'],GO=state['current']['go']['e0_72'],one_owner=True)),flush=True)
 finally:
  secret=None
  if client is not None:client.close();client=None
  if transport is not None:transport.SESSION=previous
  put('ROOT209_START_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json',dict(epoch=time.time(),all_owned_SSH_closed=client is None,SESSION_restored=transport is None or transport.SESSION is previous,global_serial_control_client_lease='FREE'))
if __name__=='__main__':
 try:main()
 except BaseException:
  put('ROOT209_START_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_replay_or_GO=True));raise
