"""UNUSED finite activation. Exactly h1/recovery R4; e2 remains deferred."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import hashlib,importlib.util,json,secrets,time,traceback
T=Path(r'C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021')
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';W=T.parent;R=N/'reports';HERE=Path(__file__).resolve().parent
sys.path.insert(1,str(N/'controllers_r4'))
import native87_install_activate_support_v1 as original
from native87_available_two_activation_support_v1 import *
PREFIX='AVAILABLE_TWO_NATIVE87R4_'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
 with (R/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
def main():
 prepared=R/'AVAILABLE_TWO_NATIVE87R4_SOURCE_PREPARED_ACTUAL.json';q=json.loads(prepared.read_bytes())
 cpu_path=R/'AVAILABLE_TWO_NATIVE87R4_ACTUAL_SOURCE_CPU_RETURNED_ACTUAL.json';cpu=json.loads(cpu_path.read_bytes())
 boundary_path=R/'NATIVE87_DUAL72_ACTUAL_GPU_RESOURCE_BOUNDARY_RETURNED_ACTUAL.json';boundary=json.loads(boundary_path.read_bytes())
 assert q['controllers_relative']=='controllers_r4'
 controllers=(N/q['controllers_relative']).resolve();assert controllers.is_relative_to(N.resolve()) and controllers.is_dir() and not controllers.is_symlink()
 sys.path.insert(0,str(controllers));import native87_protocol_v1 as protocol
 validate_prepared(q,protocol,boundary,H(boundary_path));validate_CPU(cpu,q,protocol,H(prepared))
 previous_path=R/PREVIOUS_R3_REPORT;previous= json.loads(previous_path.read_bytes())
 validate_launch_closed_receipt(q,previous,H(previous_path))
 assert H(controllers/BOUNDARY_NAME)==H(boundary_path),'owner-bound boundary must be byteexact original report'
 for name in (OWNER_SCRIPT,'native87_available_two_schedule_v1.py'):
  assert H(controllers/name)==H(HERE/name),'exact reviewed two-active owner/validator required'
 # Bind copied shared controllers to BOTH freshly admitted payload manifests;
 # inspect only JSON and these Python sources, never local model bytes.
 for key in KEYS:
  payload=Path(q['payloads'][key]).resolve()
  assert payload==(N/'payloads_r4'/key).resolve() and payload.is_relative_to(N.resolve())
  manifest=payload/'THREE_SLOT_COMPLETE_MANIFEST_V1.json';assert H(manifest)==q['specs'][key]['manifest_SHA']
  rows={row['relative']:row for row in json.loads(manifest.read_bytes())['files']}
  for name in original.OWNER_FILES:
   if name=='three_slot_finite_owner_V86_authority72.py':continue
   path=controllers/name;assert path.is_file() and not path.is_symlink()
   assert H(path)==rows[name]['SHA'] and path.stat().st_size==rows[name]['bytes']
 specs=cpu['specs_with_preinstalled_CPU_proof']
 cfg=dict(role='owner',experts=specs,scheduling_authority='human_requested_available_experts',deferred_experts=list(DEFERRED),
    resource_boundary_relative=BOUNDARY_NAME,resource_boundary_SHA=H(boundary_path),
    authority_generation='MOD4_SINGLE_WRITER72_20261026',run_id='AVAILABLE_TWO_H1_OWN_FUDAN_NATIVE87R4_'+str(time.time_ns()),token=secrets.token_hex(32))
 from native87_available_two_schedule_v1 import validate_schedule
 assert validate_schedule(cfg)
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native87R4_existing72_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 secret=memory.recover();client=None;nodes={};owner=None;identity=None
 put(PREFIX+'ACTIVATION_STARTED_ACTUAL.json',dict(epoch=time.time(),active_keys=list(KEYS),deferred_experts=list(DEFERRED),both_R4_actual_source_CPU_passed=True,prepared_source_report_SHA=H(prepared),actual_CPU_report_SHA=H(cpu_path),resource_boundary_SHA=H(boundary_path),launch_remaining_snapshot=LAUNCH_REMAINING_SNAPSHOT,previousR3costreportSHA=H(previous_path),historical_resource_snapshot_not_current_balance=True,sole72_authority=True,no_canonical_copy_or_second_writer=True))
 try:
  client=route.connect()
  pre=d.code(client,route.PY,original.REMOTE_PREACTIVATE_NODE,dict(root=ROOTS['h1'],expected_roots=ROOTS,spec=specs['h1'],ready_envelope=cpu['results']['h1']['ready_envelope']),timeout=60)
  put(PREFIX+'H1_PREACTIVATION_RESOURCE_ACTUAL.json',pre);client.close();client=None
  client=d.connect72(secret)
  account=d.code(client,d.PY72,REMOTE_ACCOUNT,{},timeout=45)
  put(PREFIX+'SOLE72_PREACTIVATION_ACCOUNT_ACTUAL.json',account)
  pre=d.code(client,d.PY72,original.REMOTE_PREACTIVATE_NODE,dict(root=ROOTS['recovery'],expected_roots=ROOTS,spec=specs['recovery'],ready_envelope=cpu['results']['recovery']['ready_envelope']),timeout=60)
  put(PREFIX+'RECOVERY_PREACTIVATION_RESOURCE_ACTUAL.json',pre)
  created=d.code(client,d.PY72,REMOTE_OWNER_CREATE,dict(owner_root=q['owner_root'],expected_owner=OWNER),timeout=45)
  put(PREFIX+'UNUSED_OWNER_ROOT_CREATED_ACTUAL.json',created)
  # Original control files remain exact payload-bound bytes. Only standalone
  # owner scheduling assertions/import differ; additional validator pins boundary.
  owner_files=[(name,controllers/name) for name in original.OWNER_FILES if name!='three_slot_finite_owner_V86_authority72.py']
  owner_files.extend([(OWNER_SCRIPT,controllers/OWNER_SCRIPT),('native87_available_two_schedule_v1.py',controllers/'native87_available_two_schedule_v1.py'),(BOUNDARY_NAME,controllers/BOUNDARY_NAME)])
  pins=[];sf=client.open_sftp()
  try:
   for name,path in owner_files:
    assert path.is_file() and not path.is_symlink() and Path(name).name==name
    pins.append(dict(name=name,bytes=path.stat().st_size,SHA=H(path)));sf.put(str(path),q['owner_root']+'/'+name)
  finally:sf.close()
  verified=d.code(client,d.PY72,original.REMOTE_OWNER_VERIFY,dict(root=q['owner_root'],files=pins),timeout=45)
  put(PREFIX+'OWNER_CONTROLLER_FULLSHA_ACTUAL.json',dict(files=pins,**verified))
  owner=d.launch(client,d.PY72,q['owner_root'],q['owner_script'],cfg)
  identity=d.code(client,d.PY72,original.REMOTE_OWNER_READY,dict(root=q['owner_root'],pid=owner['detached_pid'],script=q['owner_script']),timeout=40)
  put(PREFIX+'ACTUAL_OWNER_READY.json',dict(epoch=time.time(),owner=owner,owner_root=q['owner_root'],owner_identity=identity['owner_identity'],run_id=cfg['run_id']))
  node=dict(specs['recovery'],role='node',run_id=cfg['run_id'],token=cfg['token'])
  try:nodes['recovery']=d.launch(client,d.PY72,ROOTS['recovery'],'three_slot_finite_node_v1.py',node)
  finally:node.clear()
  put(PREFIX+'RECOVERY_NODE_DETACHED_ACTUAL.json',nodes['recovery'])
  client.close();client=None;client=route.connect()
  node=dict(specs['h1'],role='node',run_id=cfg['run_id'],token=cfg['token'],owner_ssh_password=secret)
  try:nodes['h1']=d.launch(client,route.PY,ROOTS['h1'],'three_slot_finite_node_v1.py',node)
  finally:node.clear()
  result=dict(epoch=time.time(),owner=owner,owner_root=q['owner_root'],owner_identity=identity['owner_identity'],nodes=nodes,
      roots=ROOTS,specs=specs,sources=q['sources'],payloads=q['payloads'],run_id=cfg['run_id'],sole72authority=True,
      active_keys=list(KEYS),deferred_experts=list(DEFERRED),resource_boundary_SHA=H(boundary_path),launch_remaining_snapshot=LAUNCH_REMAINING_SNAPSHOT,previousR3costreportSHA=H(previous_path),
      authority_generation='MOD4_SINGLE_WRITER72_20261026',no_secret=True,
      no_learning_or_actual_GPU_precontrol_claim_before_signed_GO_and_real_worker_checks=True)
  put(PREFIX+'ACTUAL_OWNER_NODES_DETACHED.json',result)
  print(json.dumps(dict(owner=owner,nodes=nodes,run_id=cfg['run_id'],active_keys=list(KEYS),deferred_experts=list(DEFERRED),actual_GO_precontrol_and_updates_pending=True)))
 finally:
  secret=None;cfg.clear()
  if client:client.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put(PREFIX+'ACTIVATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_rearm_refund_or_second_writer=True));raise
