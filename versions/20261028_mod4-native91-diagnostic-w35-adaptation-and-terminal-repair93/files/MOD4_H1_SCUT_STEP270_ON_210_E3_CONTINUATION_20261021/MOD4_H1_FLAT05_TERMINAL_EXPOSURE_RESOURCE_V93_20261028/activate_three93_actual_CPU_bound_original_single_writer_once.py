"""Install sealed small controllers, start three genuine nodes and one72writer.

All credentials/token stay in memory/stdin. No model/sourceCPU rerun or ledger edit.
"""
from pathlib import Path
import json,sys,hashlib,importlib.util,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(n,v):
 with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
PRE72=r'''from pathlib import Path
import json,hashlib,fcntl,socket,subprocess,psutil,shutil
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw)
assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return' and c['remaining_training_seconds']==v['expected_closed_remaining']>86412.86069250107
for p in (C.parent/'native_floor_supervisor.lock',C.parent/'autonomy_controller.lock'):
 with p.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
with socket.socket() as s:s.bind(('127.0.0.1',29754))
resources={}
for key in ('h1','e2'):
 s=v['experts'][key];gpu=s['GPU_UUID'];apps=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);assert gpu not in apps
 line=subprocess.check_output(['nvidia-smi','-i',gpu,'--query-gpu=uuid,name,memory.free','--format=csv,noheader,nounits'],text=True).strip();a=[x.strip() for x in line.split(',')];assert a[0]==gpu and a[1]=='NVIDIA GeForce RTX 4090' and int(a[2])>15669
 with Path(s['private_lock']).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
 assert psutil.virtual_memory().available>32*1024**3 and shutil.disk_usage(s['job_root']).free>25*1024**3
 resources[key]=dict(GPU_UUID=gpu,GPU_name=a[1],free_MiB=int(a[2]),compute_UUID_only_rows=0)
assert C.read_bytes()==raw
print(json.dumps(dict(passed=True,canonical_None=True,remaining=c['remaining_training_seconds'],canonical_SHA=hashlib.sha256(raw).hexdigest(),resources=resources,no_account_write=True)))'''
INSTALL=r'''from pathlib import Path,PurePosixPath
import json,hashlib
root=Path(v['root']);owned=Path('/mnt/mod4_linux_durable_20261013' if v['backend']=='source210' else '/home/lc01/Zonglin Li/zonglin2/tasks')
assert root.is_relative_to(owned) and not root.exists();root.mkdir(parents=True,mode=0o700)
for row in v['files']:
 rel=PurePosixPath(row['relative']);assert not rel.is_absolute() and '..' not in rel.parts and len(rel.parts)==1
print(json.dumps(dict(passed=True,new_owned_root=str(root))))'''
VERIFY=r'''from pathlib import Path
import json,hashlib,sys
B=Path(v['root']);sys.path.insert(0,str(B))
for row in v['files']:
 p=B/row['relative'];assert p.is_file() and not p.is_symlink() and p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['SHA']
if v['role']=='owner':
 from mixed72_next_protocol_v1 import validate_schedule
 validate_schedule(v['public']);result=dict(owner_protocol_actual_sources_sealed=True)
else:
 spec=v['spec'];job=Path(spec['job_root']);target=job/('TASK.json' if spec['key']=='e2' else 'job0/FLAT90_RUNTIME_GRANT_BINDING.json');assert not target.exists()
 task=v['task']
 with target.open('x',encoding='utf8') as f:json.dump(task,f,indent=2)
 if spec['key']=='e2':
  from E2_next72_protocol_v1 import validate_payload,load_E2_preinstalled_CPU
  validate_payload(spec,B);envelope=load_E2_preinstalled_CPU(spec,B)
 else:
  from mixed72_next_protocol_v1 import module_for
  m=module_for(spec);m.validate_payload(spec,B);envelope=m.load_actual_flat_preinstalled_CPU(spec,B)
  if spec['key']=='h1_210':
   from forwarded_original_owner_control_v1 import verify_dependencies
   verify_dependencies(spec)
 result=dict(actual_CPU_JSON_and_original_wait_reused=True,source_CPU_SHA=envelope['SHA'],runtime_binding_path=str(target))
print(json.dumps(dict(passed=True,**result,no_model_sourceCPU_GPU_or_account_action=True)))'''
LAUNCH=r'''from pathlib import Path
import json,subprocess,os,psutil,time
spec=v['cfg'];root=Path(v['root']);name=v['name'];py=v['python'];assert not (root/('owner_CONSOLE.log' if spec['role']=='owner' else 'node_CONSOLE.log')).exists()
args=[py,'-u','-B',str(root/name)];env=dict(os.environ,CUDA_VISIBLE_DEVICES='',PYTHONDONTWRITEBYTECODE='1',PYTHONUNBUFFERED='1')
p=subprocess.run(args,input=json.dumps(spec),capture_output=True,text=True,env=env,cwd=root,timeout=30);assert p.returncode==0,(p.returncode,p.stderr)
value=json.loads(p.stdout);q=psutil.Process(value['detached_pid']);actual=dict(pid=q.pid,creation=q.create_time(),exe=q.exe(),argv=q.cmdline(),root=q.cwd())
if v['backend']=='target72':
 loader='/home/lc01/Zonglin Li/zonglin2/compat/glibc240/ld-linux-x86-64.so.2';lib='/home/lc01/Zonglin Li/zonglin2/compat/glibc240:/home/lc01/Zonglin Li/zonglin2/envs/mod4/lib';python='/home/lc01/Zonglin Li/zonglin2/envs/mod4/bin/python'
 assert actual['exe']==loader and actual['argv']==[loader,'--library-path',lib,python,'-B','-u','-B',str(root/name)] and actual['root']=='/home/lc01/Zonglin Li/zonglin2'
else:assert actual['exe']==str(Path(py).resolve()) and actual['argv']==args and actual['root']==str(root)
print(json.dumps(dict(passed=True,actual_detached=value,exact_identity=actual,no_READY_GO_or_training_claim_from_launch_only=True)))'''
def main():
 public=json.loads((R/'THREE93_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json').read_bytes());assert set(public['experts'])=={'h1','h1_210','e2'}
 put('THREE93_ACTIVATION_CONSUMED_BEFORE_NETWORK_ACTUAL.json',dict(epoch=time.time(),run_id=public['run_id'],original_one72writer=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('three93_same_authorized_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');sec=importlib.util.module_from_spec(sp);sp.loader.exec_module(sec);secret=sec.recover();c=None
 def files(root):return [dict(relative=p.name,bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(Path(root).iterdir()) if p.is_file()]
 def install(client,python,local,remote,backend,role,spec=None,task=None):
  rows=files(local);d.code(client,python,INSTALL,dict(root=remote,backend=backend,files=rows),timeout=30)
  sf=client.open_sftp();sf.get_channel().settimeout(30)
  try:
   for row in rows:sf.put(str(Path(local)/row['relative']),remote+'/'+row['relative'])
  finally:sf.close()
  return d.code(client,python,VERIFY,dict(root=remote,files=rows,role=role,spec=spec,task=task,public=public),timeout=90)
 try:
  c=d.connect72(secret);pre=d.code(c,d.PY72,PRE72,public,timeout=45);put('THREE93_FRESH_SOLE72_RESOURCE_AND_ACCOUNT_PREACTUAL.json',pre)
  results={};results['owner']=install(c,d.PY72,public['owner_source'],public['owner_root'],'target72','owner')
  for key in ('h1','e2'):
   task=public['task_templates'][key]
   if key=='e2':task['actual_resource_admission']=pre['resources'][key]
   results[key]=install(c,d.PY72,public['node_sources'][key],public['node_roots'][key],'target72','node',public['experts'][key],task)
  c.close();c=None
  c=route.connect();key='h1_210';results[key]=install(c,route.PY,public['node_sources'][key],public['node_roots'][key],'source210','node',public['experts'][key],public['task_templates'][key]);c.close();c=None
  put('THREE93_ACTUAL_ALL_THREE_CONTROLLER_CPU_BINDINGS_RETURNED.json',dict(passed=True,results=results,no_GO_or_account_write_yet=True))
  # One new token, stdin only. It is never serialized into public receipts.
  import secrets
  token=secrets.token_hex(32);owner_cfg=dict(role='owner',experts={k:dict(s,token=token) for k,s in public['experts'].items()},token=token,run_id=public['run_id'],authority_generation=public['authority_generation'],scheduling_authority=public['scheduling_authority'],deferred_experts=[])
  c=d.connect72(secret);again=d.code(c,d.PY72,PRE72,public,timeout=45);assert again['canonical_SHA']==pre['canonical_SHA']
  identities={};identities['owner']=d.code(c,d.PY72,LAUNCH,dict(cfg=owner_cfg,root=public['owner_root'],name=public['owner_name'],python=public['experts']['h1']['python'],backend='target72'),timeout=45)
  put('THREE93_OWNER_ACTUAL_DETACHED_IDENTITY.json',identities['owner'])
  for key in ('h1','e2'):
   cfg=dict(public['experts'][key],role='node',token=token);identities[key]=d.code(c,d.PY72,LAUNCH,dict(cfg=cfg,root=public['node_roots'][key],name=public['node_names'][key],python=cfg['python'],backend='target72'),timeout=45)
   put(key+'_THREE93_ACTUAL_DETACHED_IDENTITY.json',identities[key])
  c.close();c=None
  c=route.connect();key='h1_210';cfg=dict(public['experts'][key],role='node',token=token,owner_ssh_password=secret);identities[key]=d.code(c,route.PY,LAUNCH,dict(cfg=cfg,root=public['node_roots'][key],name=public['node_names'][key],python=cfg['python'],backend='source210'),timeout=45);cfg=None;c.close();c=None
  put('THREE93_ACTUAL_OWNER_AND_THREE_NODES_DETACHED.json',dict(epoch=time.time(),run_id=public['run_id'],identities=identities,owner_root=public['owner_root'],node_roots=public['node_roots'],specs=public['experts'],source_CPU_bindings=results,actual_three_real_nodes_launched=True,token_and_owner_password_memory_stdin_only=True,GO_and_new_policy_pending_actual_observer=True))
  token=None;owner_cfg=None;print(json.dumps(dict(actual_one_owner_three_nodes_detached=True,first_NEW_native_policy_and_E2_PPO_pending=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('THREE93_ACTIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_retry_hotpatch_kill_refund_or_secondwriter=True));raise
