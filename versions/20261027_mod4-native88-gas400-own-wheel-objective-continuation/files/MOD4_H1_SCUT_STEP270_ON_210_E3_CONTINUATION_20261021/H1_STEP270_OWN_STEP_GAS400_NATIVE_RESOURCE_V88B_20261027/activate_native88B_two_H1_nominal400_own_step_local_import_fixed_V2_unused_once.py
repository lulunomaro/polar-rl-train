"""Activate exactly two freshly admitted H1 native88B slots; one original writer."""
from pathlib import Path
import sys,json,time,hashlib,secrets,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
P=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native88_two_available_H1_runtime_protocol_source_v1'
sys.path[:0]=[str(N/'controllers'),str(P)]
from native88_protocol_v1 import validate_schedule,validate_spec,native88_valid_ready
from native88_install_activate_support_v1 import REMOTE_ACCOUNT
sys.path.insert(0,str(T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'))
import native87_install_activate_support_v1 as original
OWNER_SCRIPT='three_slot_finite_owner_NATIVE88_AVAILABLE_TWO_authority72.py'
REMOTE_PRE=original.REMOTE_PREACTIVATE_NODE.replace('NATIVE87_POLICY_ONLY_FRESH4096_SOURCE_SDK_CPU_ACTUAL.json','NATIVE88_CHANGED_PLANT_SOURCE_SDK_CPU_ACTUAL.json').replace('native87_closed_source_CPU_v1','native88_closed_source_CPU_v1').replace('native87_protocol_v1','native88_protocol_v1')
old="compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(s['GPU_UUID'] in line for line in compute.splitlines())"
new="compute=subprocess.check_output(['nvidia-smi','-i',s['GPU_UUID'],'--query-compute-apps=gpu_uuid','--format=csv,noheader,nounits'],text=True);assert s['GPU_UUID'] not in compute"
assert REMOTE_PRE.count(old)==1;REMOTE_PRE=REMOTE_PRE.replace(old,new,1)
old="gpu=next(line for line in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in line)"
new="gpu=subprocess.check_output(['nvidia-smi','-i',s['GPU_UUID'],'--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).strip();assert gpu.split(',')[0].strip()==s['GPU_UUID']"
assert REMOTE_PRE.count(old)==1;REMOTE_PRE=REMOTE_PRE.replace(old,new,1)
REMOTE_CREATE=r'''from pathlib import Path
import json,socket
B=Path(v['owner_root']);assert str(B)==v['expected_owner'] and not B.exists()
assert B.resolve().is_relative_to(Path('/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_step_gas400_native_2610v88b').resolve())
with socket.socket() as s:s.bind(('127.0.0.1',29754))
B.mkdir(parents=True);print(json.dumps(dict(owner_root=str(B),unused_unique_owner=True,no_account_copy_or_write=True)))'''
REMOTE_OWNER_READY=r'''from pathlib import Path
import json,psutil,socket,time
B=Path(v['root']);until=time.monotonic()+25
while not (B/'OWNER_IDENTITY.json').exists():assert time.monotonic()<until;time.sleep(.1)
recorded=json.loads((B/'OWNER_IDENTITY.json').read_bytes());assert recorded['pid']==v['pid']
p=psutil.Process(v['pid']);assert p.create_time()==recorded['creation']
actual=dict(pid=p.pid,creation=p.create_time(),exe=p.exe(),argv=p.cmdline(),root=p.cwd())
assert all(actual[k]==v['expected'][k] for k in ('exe','argv','root'))
while True:
 try:
  with socket.create_connection(('127.0.0.1',29754),timeout=5):pass
  break
 except ConnectionRefusedError:assert time.monotonic()<until;time.sleep(.1)
print(json.dumps(dict(owner_identity=actual,actual_listener_ready=True)))'''
REMOTE_GO=r'''from pathlib import Path
import json,time,psutil
B=Path(v['owner_root']);until=time.monotonic()+60
while True:
 if (B/'OWNER_CURRENT.json').is_file():
  x=json.loads((B/'OWNER_CURRENT.json').read_bytes());g=x.get('go',{})
  if set(g)=={'h1','recovery'}:break
 assert time.monotonic()<until,'both original signed GO not yet available'
 time.sleep(.2)
for k,row in g.items():assert row['run_id']==v['run_id'] and row['source_SHA']==v['source_SHAs'][k] and row['max_parent_seconds']==3900 and row['exit_headroom_seconds']==300
print(json.dumps(dict(actual_owner_signed_GO_read=True,run_id=v['run_id'],go=g,no_first_policy_or_GPU_claim=True)))'''
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 prepared=R/'NATIVE88_TWO_PAYLOADS_SOURCE_PREPARED_ACTUAL.json';q=json.loads(prepared.read_bytes());cp=R/'NATIVE88_ACTUAL_TWO_SOURCE_CPU_AND_RESOURCE_RETURNED_ACTUAL.json';cpu=json.loads(cp.read_bytes());assert cpu['passed'] and cpu['prepared_source_report_SHA']==H(prepared)
 specs=cpu['specs_with_preinstalled_CPU_proof'];controllers=N/'controllers';boundary=R/'NATIVE88_SELECTED_RESOURCE_BOUNDARY_ACTUAL.json';assert H(boundary)==cpu['resource_boundary_SHA']==H(controllers/boundary.name)
 for k,s in specs.items():
  validate_spec(s);assert native88_valid_ready(dict(key=k,phase='ready',manifest_SHA=s['manifest_SHA'],closed_source_CPU=cpu['results'][k]['ready_envelope'],original_error=False),s)
 cfg=dict(role='owner',experts=specs,scheduling_authority='human_requested_available_experts',deferred_experts=['e2'],resource_boundary_relative=boundary.name,resource_boundary_SHA=H(boundary),last_closed_remaining_snapshot=569553.363275528,authority_generation='MOD4_SINGLE_WRITER72_20261026',run_id='AVAILABLE_TWO_H1_GAS400_OWN_STEP_NATIVE88B_'+str(time.time_ns()),token=secrets.token_hex(32));validate_schedule(cfg)
 from native88_closed_source_CPU_v1 import expected_exec_identity
 expected=expected_exec_identity(specs['recovery'],[specs['recovery']['python'],'-u','-B',q['owner_root']+'/'+OWNER_SCRIPT],q['owner_root'])
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native88B_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 secret=m.recover();client=None;nodes={};owner=None
 put('NATIVE88B_ACTIVATION_CONSUMED_BEFORE_REMOTE_ACTUAL.json',dict(epoch=time.time(),prepared_SHA=H(prepared),actual_source_CPU_report_SHA=H(cp),source_kind='qualified_R5_changed400N_own_step_objective',sole72_original_finite_authority=True))
 try:
  client=route.connect();pre=d.code(client,route.PY,REMOTE_PRE,dict(root=q['roots']['h1'],expected_roots=q['roots'],spec=specs['h1'],ready_envelope=cpu['results']['h1']['ready_envelope']),timeout=60);put('NATIVE88B_H1_FRESH_PREACTIVATION_ACTUAL.json',pre);client.close();client=None
  client=d.connect72(secret);account=d.code(client,d.PY72,REMOTE_ACCOUNT,{},timeout=45);put('NATIVE88B_SOLE72_FRESH_PREACTIVATION_ACCOUNT_ACTUAL.json',account)
  pre=d.code(client,d.PY72,REMOTE_PRE,dict(root=q['roots']['recovery'],expected_roots=q['roots'],spec=specs['recovery'],ready_envelope=cpu['results']['recovery']['ready_envelope']),timeout=60);put('NATIVE88B_RECOVERY_FRESH_PREACTIVATION_ACTUAL.json',pre)
  created=d.code(client,d.PY72,REMOTE_CREATE,dict(owner_root=q['owner_root'],expected_owner=q['owner_root']),timeout=45);put('NATIVE88B_UNUSED_OWNER_ROOT_CREATED_ACTUAL.json',created)
  files=[p for p in controllers.iterdir() if p.is_file() and p.suffix in ('.py','.json')];pins=[];sf=client.open_sftp()
  try:
   for p in files:
    pins.append(dict(name=p.name,bytes=p.stat().st_size,SHA=H(p)));sf.put(str(p),q['owner_root']+'/'+p.name)
  finally:sf.close()
  verified=d.code(client,d.PY72,original.REMOTE_OWNER_VERIFY,dict(root=q['owner_root'],files=pins),timeout=45);put('NATIVE88B_OWNER_CONTROLLER_FULLSHA_ACTUAL.json',dict(files=pins,**verified))
  owner=d.launch(client,d.PY72,q['owner_root'],OWNER_SCRIPT,cfg)
  identity=d.code(client,d.PY72,REMOTE_OWNER_READY,dict(root=q['owner_root'],pid=owner['detached_pid'],expected=expected),timeout=40)
  put('NATIVE88B_ACTUAL_OWNER_READY.json',dict(epoch=time.time(),owner=owner,owner_root=q['owner_root'],owner_identity=identity['owner_identity'],run_id=cfg['run_id']))
  node=dict(specs['recovery'],role='node',run_id=cfg['run_id'],token=cfg['token'])
  try:nodes['recovery']=d.launch(client,d.PY72,q['roots']['recovery'],'three_slot_finite_node_v1.py',node)
  finally:node.clear()
  put('NATIVE88B_RECOVERY_NODE_DETACHED_ACTUAL.json',nodes['recovery']);client.close();client=None
  client=route.connect();node=dict(specs['h1'],role='node',run_id=cfg['run_id'],token=cfg['token'],owner_ssh_password=secret)
  try:nodes['h1']=d.launch(client,route.PY,q['roots']['h1'],'three_slot_finite_node_v1.py',node)
  finally:node.clear()
  detached=dict(epoch=time.time(),owner=owner,owner_root=q['owner_root'],owner_identity=identity['owner_identity'],nodes=nodes,roots=q['roots'],specs=specs,sources=q['sources'],payloads=q['payloads'],run_id=cfg['run_id'],sole72authority=True,active_keys=['h1','recovery'],deferred_experts=['e2'],resource_boundary_SHA=H(boundary),launch_remaining_snapshot=account['remaining'],authority_generation='MOD4_SINGLE_WRITER72_20261026',no_secret=True,no_GO_or_firstpolicy_claim_from_detached_only=True)
  put('NATIVE88B_ACTUAL_OWNER_NODES_DETACHED.json',detached);client.close();client=None
  client=d.connect72(secret);go=d.code(client,d.PY72,REMOTE_GO,dict(owner_root=q['owner_root'],run_id=cfg['run_id'],source_SHAs={k:s['source_SHA'] for k,s in specs.items()}),timeout=70);put('NATIVE88B_ACTUAL_SIGNED_TWO_GO_METADATA_ACTUAL.json',dict(epoch=time.time(),**go))
  print(json.dumps(dict(actual_finite_returned=True,two_actual_signed_GO=True,run_id=cfg['run_id'],actual_new_policy_and_400N_PhysX_readback_pending=True)))
 finally:
  secret=None;cfg.clear()
  if client:client.close()
if __name__=='__main__':
 try:main()
 except BaseException:put('NATIVE88B_ACTIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),original_error=traceback.format_exc(),no_rearm_or_second_writer_or_refund=True));raise
