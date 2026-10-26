"""Activate the admitted three slots through the existing sole72 authority."""
from pathlib import Path
import hashlib,importlib.util,json,secrets,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
def put(name,value):
 with (R/name).open('x',encoding='utf8') as out:json.dump(value,out,indent=2)
def main():
 q=json.loads((R/'THREE_GPU86B_SOURCE_ADMITTED_PREPARED_ACTUAL.json').read_bytes());assert q['passed'] and q['actual_three_target_source_SDK_CPU_passed'] and set(q['specs'])=={'h1','e2','recovery'}
 sys.path.insert(0,str(N/'controllers_v2'));from mixed86_protocol_v1 import validate_schedule
 cfg=dict(role='owner',experts=q['specs'],scheduling_authority=q['scheduling_authority'],deferred_experts=[],authority_generation=q['authority_generation'],run_id='THREE_GPU_NATIVE85_CONTINUATION_V86B_'+str(time.time_ns()),token=secrets.token_hex(32));assert validate_schedule(cfg)
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('approved72_password_in_memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 secret=memory.recover();client=None;put('THREE_GPU86B_ACTIVATION_STARTED_ACTUAL.json',dict(epoch=time.time(),actual_source_SDK_admitted=True,sole72_authority=True,no_canonical_creation_or_copy=True))
 try:
  client=route.connect()
  pre="from pathlib import Path;import fcntl,hashlib,json,psutil,shutil,subprocess,time;B=Path(v['root']);s=v['spec'];assert B.is_dir() and B.resolve().is_relative_to(Path('/mnt/mod4_linux_durable_20261013').resolve());assert not any((B/name).exists() for name in ('NODE_IDENTITY.json','NODE_TERMINAL_ACTUAL.json','NODE_CURRENT.json','job0/GO_PRODUCTION.json'));assert hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==s['manifest_SHA'];assert (B/'NORMAL86_INSTALLED_SOURCE_SDK_CPU_ADMITTED_ACTUAL.json').is_file()\nwith Path(s['private_lock']).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\nmount=json.loads(subprocess.check_output(['findmnt','--json','--target','/mnt/mod4_linux_durable_20261013','--output','UUID,OPTIONS'],text=True))['filesystems'][0];assert mount['uuid']=='EF3105C85DD986BD' and 'rw' in mount['options'].split(',');compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(s['GPU_UUID'] in line for line in compute.splitlines());gpu=next(line for line in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in line);assert int(gpu.split(',')[-1])>15669 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(B).free>25*1024**3;print(json.dumps(dict(epoch=time.time(),H1_single_target_unused_resource_CPU_ready=True,GPU_line=gpu,private_H1_lease_free=True,durable_UUID_rw=True,no_retired210_canonical_IO=True)))"
  h1_pre=d.code(client,route.PY,pre,dict(root=q['roots']['h1'],spec=q['specs']['h1']),timeout=45);put('THREE_GPU86B_H1_PREACTIVATION_RESOURCE_ACTUAL.json',h1_pre);client.close();client=None
  client=d.connect72(secret)
  pre="from pathlib import Path;import fcntl,hashlib,json,psutil,shutil,socket,subprocess,time;B=Path(v['owner']);owned=Path('/home/lc01/Zonglin Li/zonglin2');assert B.resolve().is_relative_to(owned.resolve()) and not B.exists();P=owned/'state/mod4_single_canonical_authority_20261026';c=json.loads((P/'TRAINING_BUDGET_10H.json').read_bytes());assert c['active_segment'] is None and c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026' and c['budget_mode']=='finite_original_limits_restored_after_single4090_return' and c['remaining_training_seconds']==587957.6840648651 and c['remaining_training_seconds']>86412.86069250107\nfor name in ('native_floor_supervisor.lock','autonomy_controller.lock'):\n with (P/name).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\nfor key in ('e2','recovery'):\n root=Path(v['roots'][key]);s=v['specs'][key];assert not any((root/name).exists() for name in ('NODE_IDENTITY.json','NODE_TERMINAL_ACTUAL.json','NODE_CURRENT.json','job0/GO_PRODUCTION.json'));assert hashlib.sha256((root/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==s['manifest_SHA']\n with Path(s['private_lock']).open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\n compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(s['GPU_UUID'] in line for line in compute.splitlines());gpu=next(line for line in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in line);assert int(gpu.split(',')[-1])>(15669 if key=='e2' else 7000) and shutil.disk_usage(root).free>25*1024**3\nassert psutil.virtual_memory().available>8*1024**3\nwith (owned/'state/finite_environment_validation.lock').open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)\nwith socket.socket() as s:s.bind(('127.0.0.1',29754))\nB.mkdir(parents=True);print(json.dumps(dict(epoch=time.time(),unused_owner_root=str(B),sole72_canonical_None=True,authority_generation=c['authority_generation'],budget_mode=c['budget_mode'],remaining_tracking=c['remaining_training_seconds'],original_two_owner_and_two_private_shared_locks_free=True,no_budget_write=True)))"
  ready_pre=d.code(client,d.PY72,pre,dict(owner=q['owner_root'],roots=q['roots'],specs=q['specs']),timeout=60);put('THREE_GPU86B_SOLE72_OWNER_PREACTIVATION_ACTUAL.json',ready_pre)
  sf=client.open_sftp()
  try:
   for name in ('three_slot_common_v1.py',q['owner_script'],'single_writer72_authority_V85M_source.py','mixed84_protocol_v1.py','mixed86_protocol_v1.py'):sf.put(str(N/'controllers_v2'/name),q['owner_root']+'/'+name)
  finally:sf.close()
  owner=d.launch(client,d.PY72,q['owner_root'],q['owner_script'],cfg)
  code="from pathlib import Path;import json,psutil,socket,time;B=Path(v['root']);until=time.monotonic()+25\nwhile not (B/'OWNER_IDENTITY.json').exists() and time.monotonic()<until:time.sleep(.1)\np=psutil.Process(v['pid']);assert str(B/v['script']) in p.cmdline()\nwhile True:\n try:\n  with socket.create_connection(('127.0.0.1',29754),timeout=5):pass\n  break\n except ConnectionRefusedError:\n  assert time.monotonic()<until;time.sleep(.1)\nprint(json.dumps(dict(owner=json.loads((B/'OWNER_IDENTITY.json').read_bytes()),actual_listener_ready=True)))"
  identity=d.code(client,d.PY72,code,dict(root=q['owner_root'],pid=owner['detached_pid'],script=q['owner_script']),timeout=40)
  put('THREE_GPU86B_ACTUAL_OWNER_READY.json',dict(epoch=time.time(),owner=owner,owner_root=q['owner_root'],owner_identity=identity['owner'],run_id=cfg['run_id']))
  nodes={}
  for key in ('recovery','e2'):
   node=dict(q['specs'][key],role='node',run_id=cfg['run_id'],token=cfg['token'])
   try:nodes[key]=d.launch(client,d.PY72,q['roots'][key],'three_slot_finite_node_v1.py',node)
   finally:node.clear()
   put(key.upper()+'_THREE_GPU86B_NODE_DETACHED_ACTUAL.json',nodes[key])
  client.close();client=None
  client=route.connect();node=dict(q['specs']['h1'],role='node',run_id=cfg['run_id'],token=cfg['token'],owner_ssh_password=secret)
  try:nodes['h1']=d.launch(client,route.PY,q['roots']['h1'],'three_slot_finite_node_v1.py',node)
  finally:node.clear()
  result=dict(epoch=time.time(),owner=owner,owner_root=q['owner_root'],owner_identity=identity['owner'],nodes=nodes,roots=q['roots'],specs=q['specs'],sources=q['sources'],payloads=q['payloads'],run_id=cfg['run_id'],authority_generation=q['authority_generation'],deferred_experts=[],sole_writer72=True,no_actual_learning_claim_until_signed_GO_and_positive_update=True)
  put('THREE_GPU86B_ACTUAL_OWNER_NODES_DETACHED.json',result);print(json.dumps(dict(owner=owner,nodes=nodes,run_id=cfg['run_id'],actual_GO_and_positive_updates_pending=True)))
 finally:
  secret=None;cfg.clear()
  if client:client.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('THREE_GPU86B_ACTIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_rearm_or_second_writer_or_refund=True));raise
