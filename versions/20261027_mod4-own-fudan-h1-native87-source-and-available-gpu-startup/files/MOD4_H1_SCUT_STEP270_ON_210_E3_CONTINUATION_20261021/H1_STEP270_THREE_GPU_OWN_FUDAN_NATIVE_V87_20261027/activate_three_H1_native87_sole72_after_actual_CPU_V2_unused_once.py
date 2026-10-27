"""UNUSED activation: all actual preinstalled CPU proofs required before sole72 owner."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import hashlib,importlib.util,json,secrets,sys,time,traceback
from native87_install_activate_support_v1 import *
T=Path(r'C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021')
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';W=T.parent;R=N/'reports'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 prepared=R/'THREE_H1_NATIVE87_LOCAL_BOUND_SOURCE_PREPARED_ACTUAL.json';q=json.loads(prepared.read_bytes())
 cpu=json.loads((R/'THREE_H1_NATIVE87_TARGET_SOURCE_SDK_CPU_RETURNED_ACTUAL.json').read_bytes())
 sys.path.insert(0,str(N/'controllers'));import native87_protocol_v1 as protocol
 validate_prepared(q,protocol);validate_CPU(cpu,q,protocol)
 assert cpu['prepared_source_report_SHA']==hashlib.sha256(prepared.read_bytes()).hexdigest()
 specs=cpu['specs_with_preinstalled_CPU_proof'];assert set(specs)==set(KEYS)
 for key in KEYS:
  assert {k:v for k,v in specs[key].items() if k!='preinstalled_CPU_proof_SHA'}==q['specs'][key]
  assert specs[key]['preinstalled_CPU_proof_SHA']==cpu['results'][key]['preinstalled_CPU_proof_SHA']
  assert len(specs[key]['preinstalled_CPU_proof_SHA'])==64
 cfg=dict(role='owner',experts=specs,scheduling_authority='human_requested_available_experts',deferred_experts=[],
    authority_generation='MOD4_SINGLE_WRITER72_20261026',run_id='THREE_H1_OWN_FUDAN_NATIVE87_'+str(time.time_ns()),token=secrets.token_hex(32))
 assert protocol.validate_schedule(cfg)
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native87_existing72_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 secret=memory.recover();client=None;nodes={};owner=None;identity=None
 put('THREE_H1_NATIVE87_ACTIVATION_STARTED_ACTUAL.json',dict(epoch=time.time(),all3_actual_source_CPU_passed=True,sole72_authority=True,no_canonical_copy_or_second_writer=True))
 try:
  client=route.connect()
  pre=d.code(client,route.PY,REMOTE_PREACTIVATE_NODE,dict(root=ROOTS['h1'],expected_roots=ROOTS,spec=specs['h1'],ready_envelope=cpu['results']['h1']['ready_envelope']),timeout=60)
  put('H1_NATIVE87_PREACTIVATION_RESOURCE_ACTUAL.json',pre);client.close();client=None
  client=d.connect72(secret)
  account=d.code(client,d.PY72,REMOTE_ACCOUNT,{},timeout=45)
  put('SOLE72_NATIVE87_PREACTIVATION_ACCOUNT_ACTUAL.json',account)
  for key in ('e2','recovery'):
   pre=d.code(client,d.PY72,REMOTE_PREACTIVATE_NODE,dict(root=ROOTS[key],expected_roots=ROOTS,spec=specs[key],ready_envelope=cpu['results'][key]['ready_envelope']),timeout=60)
   put(key.upper()+'_NATIVE87_PREACTIVATION_RESOURCE_ACTUAL.json',pre)
  created=d.code(client,d.PY72,REMOTE_OWNER_CREATE,dict(owner_root=q['owner_root'],expected_owner=OWNER),timeout=45)
  put('NATIVE87_UNUSED_OWNER_ROOT_CREATED_ACTUAL.json',created)
  # Full new controller set includes current native87 protocol + dispatcher.
  owner_files=[q['owner_script'] if name=='three_slot_finite_owner_V86_authority72.py' else name for name in OWNER_FILES]
  pins=[];sf=client.open_sftp()
  try:
   for name in owner_files:
    path=N/'controllers'/name;assert path.is_file() and not path.is_symlink() and Path(name).name==name
    pins.append(dict(name=name,bytes=path.stat().st_size,SHA=hashlib.sha256(path.read_bytes()).hexdigest()))
    sf.put(str(path),q['owner_root']+'/'+name)
  finally:sf.close()
  verified=d.code(client,d.PY72,REMOTE_OWNER_VERIFY,dict(root=q['owner_root'],files=pins),timeout=45)
  put('NATIVE87_OWNER_CONTROLLER_FULLSHA_ACTUAL.json',dict(files=pins,**verified))
  owner=d.launch(client,d.PY72,q['owner_root'],q['owner_script'],cfg)
  identity=d.code(client,d.PY72,REMOTE_OWNER_READY,dict(root=q['owner_root'],pid=owner['detached_pid'],script=q['owner_script']),timeout=40)
  put('THREE_H1_NATIVE87_ACTUAL_OWNER_READY.json',dict(epoch=time.time(),owner=owner,owner_root=q['owner_root'],owner_identity=identity['owner_identity'],run_id=cfg['run_id']))
  for key in ('e2','recovery'):
   node=dict(specs[key],role='node',run_id=cfg['run_id'],token=cfg['token'])
   try:nodes[key]=d.launch(client,d.PY72,ROOTS[key],'three_slot_finite_node_v1.py',node)
   finally:node.clear()
   put(key.upper()+'_THREE_H1_NATIVE87_NODE_DETACHED_ACTUAL.json',nodes[key])
  client.close();client=None;client=route.connect()
  node=dict(specs['h1'],role='node',run_id=cfg['run_id'],token=cfg['token'],owner_ssh_password=secret)
  try:nodes['h1']=d.launch(client,route.PY,ROOTS['h1'],'three_slot_finite_node_v1.py',node)
  finally:node.clear()
  result=dict(epoch=time.time(),owner=owner,owner_root=q['owner_root'],owner_identity=identity['owner_identity'],nodes=nodes,
      roots=ROOTS,specs=specs,sources=q['sources'],payloads=q['payloads'],run_id=cfg['run_id'],sole72authority=True,
      authority_generation='MOD4_SINGLE_WRITER72_20261026',no_secret=True,
      no_learning_or_actual_GPU_precontrol_claim_before_signed_GO_and_real_worker_checks=True)
  put('THREE_H1_NATIVE87_ACTUAL_OWNER_NODES_DETACHED.json',result)
  print(json.dumps(dict(owner=owner,nodes=nodes,run_id=cfg['run_id'],actual_GO_precontrol_and_updates_pending=True)))
 finally:
  secret=None;cfg.clear()
  if client:client.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('THREE_H1_NATIVE87_ACTIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_rearm_refund_or_second_writer=True));raise
