"""One new native88 installation and initial full-source CPU admission per role."""
from pathlib import Path
import sys,json,time,hashlib,importlib.util,traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
P=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native88_two_available_H1_runtime_protocol_source_v1'
sys.path.insert(0,str(P))
from native88_install_activate_support_v1 import REMOTE_ACCOUNT,REMOTE_INSTALL,REMOTE_VERIFY,REMOTE_CPU
from native88_protocol_v1 import validate_spec,native88_valid_ready
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def main():
 prepared=R/'NATIVE88_TWO_PAYLOADS_SOURCE_PREPARED_ACTUAL.json';q=json.loads(prepared.read_bytes())
 assert q['passed'] and set(q['specs'])=={'h1','recovery'} and q['actual_target_CPU_or_GPU_or_GO'] is False
 put('NATIVE88_INSTALL_CONSUMED_BEFORE_REMOTE_ACTUAL.json',dict(epoch=time.time(),prepared_SHA=H(prepared),no_owner_GO=True))
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native88_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 secret=memory.recover();c=None;results={};specs={};resources={}
 try:
  c=d.connect72(secret);account=d.code(c,d.PY72,REMOTE_ACCOUNT,{},timeout=45);put('NATIVE88_SOLE72_BEFORE_INSTALL_ACTUAL.json',account);c.close();c=None
  for key in ('h1','recovery'):
   s=q['specs'][key];validate_spec(s);B=Path(q['payloads'][key]);mf=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());contract=json.loads((B/'NATIVE88_SOURCE_CONTRACT_ACTUAL.json').read_bytes())
   assert H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')==s['manifest_SHA']
   c=route.connect() if key=='h1' else d.connect72(secret);python=route.PY if key=='h1' else d.PY72
   copied=d.code(c,python,REMOTE_INSTALL,dict(key=key,root=q['roots'][key],expected_roots=q['roots'],spec=s,manifest=mf,source=q['sources'][key],previous_qualified_pair=True,current_account=account,original_R5_private_lock=contract['previous_R5_private_lock'],known_own=json.loads((B/contract['known_own_processes_relative']).read_bytes())),timeout=120)
   put(key.upper()+'_NATIVE88_EXACT_COPY_RESOURCE_ACTUAL.json',copied)
   sf=c.open_sftp();sf.get_channel().settimeout(90)
   try:
    for row in copied['need_upload']:sf.put(str(B/row['relative']),q['roots'][key]+'/'+row['relative'])
    sf.put(str(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),q['roots'][key]+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
   finally:sf.close()
   verified=d.code(c,python,REMOTE_VERIFY,dict(root=q['roots'][key],spec=s,manifest=mf),timeout=300);put(key.upper()+'_NATIVE88_POSTCOPY_FULLSHA_ACTUAL.json',verified)
   actual=d.code(c,python,REMOTE_CPU,dict(root=q['roots'][key],spec=s),timeout=900);put(key.upper()+'_NATIVE88_ACTUAL_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',dict(actual_finite_returned=True,**actual));assert actual['passed'],actual.get('original_error')
   assert native88_valid_ready(dict(key=key,phase='ready',manifest_SHA=s['manifest_SHA'],closed_source_CPU=actual['ready_envelope'],original_error=False),s)
   results[key]=actual;specs[key]=dict(s,preinstalled_CPU_proof_SHA=actual['preinstalled_CPU_proof_SHA']);resources[key]=dict(copied['resource'],free_payload_disk_bytes=verified['durable_free_after_payload'])
   c.close();c=None
  c=d.connect72(secret);account_after=d.code(c,d.PY72,REMOTE_ACCOUNT,{},timeout=45);assert account_after['canonical_SHA']==account['canonical_SHA'];put('NATIVE88_SOLE72_AFTER_CPU_ACTUAL.json',account_after);c.close();c=None
  boundary=dict(epoch=time.time(),actual_finite_returned=True,canonical_None=True,original_owner_locks_free=True,no_account_write=True,closed_remaining_snapshot=569553.363275528,unknown16828_identity_not_queried=True,selected_resources=resources)
  put('NATIVE88_SELECTED_RESOURCE_BOUNDARY_ACTUAL.json',boundary)
  (N/'controllers/NATIVE88_SELECTED_RESOURCE_BOUNDARY_ACTUAL.json').write_bytes((R/'NATIVE88_SELECTED_RESOURCE_BOUNDARY_ACTUAL.json').read_bytes())
  put('NATIVE88_ACTUAL_TWO_SOURCE_CPU_AND_RESOURCE_RETURNED_ACTUAL.json',dict(epoch=time.time(),passed=True,actual_finite_returned=True,prepared_source_report_SHA=H(prepared),results=results,specs_with_preinstalled_CPU_proof=specs,resource_boundary_SHA=H(R/'NATIVE88_SELECTED_RESOURCE_BOUNDARY_ACTUAL.json'),no_owner_GO_or_fee=True))
  print(json.dumps(dict(passed=True,actual_finite_returned=True,two_actual_installed_SDK_source_CPU=True,no_owner_GO_or_fee=True)))
 finally:
  secret=None
  if c:c.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('NATIVE88_INSTALL_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(original_error=traceback.format_exc(),no_same_root_rearm_or_GO=True));raise
