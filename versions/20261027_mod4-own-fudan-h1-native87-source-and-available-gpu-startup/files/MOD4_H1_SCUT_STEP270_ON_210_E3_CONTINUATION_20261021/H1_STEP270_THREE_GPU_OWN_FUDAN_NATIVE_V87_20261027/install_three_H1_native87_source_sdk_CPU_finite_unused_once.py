"""UNUSED finite serial source install + exactly one actual target CPU per role."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
from native87_install_activate_support_v1 import *
T=Path(r'C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021')
N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';W=T.parent;R=N/'reports'
def put(name,v):
 with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 q=json.loads((R/'THREE_H1_NATIVE87_LOCAL_BOUND_SOURCE_PREPARED_ACTUAL.json').read_bytes())
 sys.path.insert(0,str(N/'controllers'));import native87_protocol_v1 as protocol
 validate_prepared(q,protocol)
 old=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/reports'
 typed=json.loads((old/'THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());authority=json.loads((old/'THREE_GPU86B_CLOSED_AUTHORITY72_ORIGINAL_COST_ACTUAL.json').read_bytes())
 assert typed['passed'] and typed['original_canonical_cost_settled'] and not typed['errors'] and authority['all_authority72_owner_children_actual_out'] and authority['canonical_active_segment'] is None
 closure=dict(passed=True,allout_and_cost_settled=True,typed_report_SHA=hashlib.sha256((old/'THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes()).hexdigest())
 sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'));import deploy_two50_reconciled_original_writer_once as d
 sys.path.insert(0,str(T/'MOD4_MOE_T2Z_SINGLE4090_QUANTIZED_PREPARATION_20261025'));import strict_user_forwarded_original210_transport_v1 as route
 sp=importlib.util.spec_from_file_location('native87_existing_memory_only',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py');memory=importlib.util.module_from_spec(sp);sp.loader.exec_module(memory)
 secret=memory.recover();client=None;results={};proof_specs={};account=None
 put('THREE_H1_NATIVE87_ACTUAL_INSTALL_CPU_STARTED_ACTUAL.json',dict(epoch=time.time(),serial_order=list(KEYS),no_owner_node_GO_or_fee=True))
 try:
  for key in KEYS:
   s=q['specs'][key];assert not s.get('preinstalled_CPU_proof_SHA')
   value=q['payloads'][key];local=Path(value if isinstance(value,str) else value['payload'])
   manifest=json.loads((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());assert hashlib.sha256((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest()==s['manifest_SHA']
   client=route.connect() if key=='h1' else d.connect72(secret);python=route.PY if key=='h1' else d.PY72
   if key!='h1':account=d.code(client,python,REMOTE_ACCOUNT,{},timeout=45)
   transferred=d.code(client,python,REMOTE_INSTALL,dict(key=key,root=q['roots'][key],expected_roots=ROOTS,spec=s,manifest=manifest,source=q['sources'][key],previous86_close=closure,current_account=account),timeout=120)
   put(key.upper()+'_NATIVE87_EXACT_COPY_RESOURCE_ACTUAL.json',transferred)
   sf=client.open_sftp();sf.get_channel().settimeout(90)
   try:
    for row in transferred['need_upload']:sf.put(str(local/row['relative']),q['roots'][key]+'/'+row['relative'])
    sf.put(str(local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),q['roots'][key]+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
   finally:sf.close()
   verify=d.code(client,python,REMOTE_VERIFY,dict(root=q['roots'][key],spec=s,manifest=manifest),timeout=240)
   put(key.upper()+'_NATIVE87_FULLSHA_AFTER_PAYLOAD_ACTUAL.json',verify)
   actual=d.code(client,python,REMOTE_CPU,dict(root=q['roots'][key],spec=s),timeout=900)
   put(key.upper()+'_NATIVE87_TARGET_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',dict(actual_finite_returned=True,root=q['roots'][key],**actual))
   assert actual['passed'],actual.get('original_error')
   proof=d.code(client,python,"from pathlib import Path;import hashlib,json;B=Path(v['root']);p=B/'job0/NATIVE87_PREINSTALLED_CPU_PROOF_ACTUAL.json';x=json.loads(p.read_bytes());assert x['not_synthetic'] and x['actual_CPU_waited_EXIT0'] and x['manifest_SHA']==v['manifest_SHA'];print(json.dumps(dict(SHA=hashlib.sha256(p.read_bytes()).hexdigest(),value=x)))",dict(root=q['roots'][key],manifest_SHA=s['manifest_SHA']),timeout=45)
   actual['preinstalled_CPU_proof_SHA']=proof['SHA'];actual['preinstalled_CPU_proof']=proof['value'];results[key]=actual
   proof_specs[key]=dict(s,preinstalled_CPU_proof_SHA=proof['SHA'])
   client.close();client=None
  summary=dict(epoch=time.time(),passed=True,actual_finite_returned=True,results=results,specs_with_preinstalled_CPU_proof=proof_specs,
      prepared_source_report_SHA=hashlib.sha256((R/'THREE_H1_NATIVE87_LOCAL_BOUND_SOURCE_PREPARED_ACTUAL.json').read_bytes()).hexdigest(),
      actual_target_CPU_once_each=True,proof_pins_are_root_side_external_to_remote_proof=True,no_owner_node_GO_or_fee=True)
  validate_CPU(summary,q,protocol);put('THREE_H1_NATIVE87_TARGET_SOURCE_SDK_CPU_RETURNED_ACTUAL.json',summary)
  print(json.dumps(dict(actual_finite_returned=True,all3_actual_source_CPU_passed=True,activation_not_executed=True)))
 finally:
  secret=None
  if client:client.close()
if __name__=='__main__':
 try:main()
 except BaseException:
  put('THREE_H1_NATIVE87_INSTALL_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(epoch=time.time(),error=traceback.format_exc(),no_retry_same_namespace=True,no_owner_GO_or_account_write=True));raise
