"""New reader purpose; preserve original226/V1/V2 and actual231false."""
from pathlib import Path
import hashlib,json,time,traceback

N=Path(__file__).resolve().parent
T=N.parent
BASE=T/'E2_QUALIFIED_METADATA_TASK_READY_SOURCE_V226_20261101'
V2=T/'E2_TARGET_METADATA_TYPED_EVIDENCE_SOURCE_FROM226_V2_20261101'
PROBE_NAME='probe_e2_from226_v3_target_metadata_ROOT_ONLY.py'
EXPECTED_NAME='EXPECTED_E2_FROM226_V3_TARGET_METADATA.json'
KIND='NEW_E2_FROM226_V3_LEXICAL_SOURCE_SDK_METADATA'
ONCE='METADATA_E2_FROM226_V3_ONCE_CONSUMED.json'


def H(data):return hashlib.sha256(data).hexdigest()
def ref(p):
 b=p.read_bytes();return dict(path=str(p),bytes=len(b),SHA=H(b))
def write(p,b):
 with p.open('xb') as f:f.write(b)
def put(p,v):write(p,json.dumps(v,indent=2,allow_nan=False).encode())
def once(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)


def main():
 purpose=json.loads((N/'reports/DERIVE_V3_PURPOSE_FROZEN.json').read_bytes())
 for row in purpose['inputs']:assert ref(Path(row['path']))==row
 oldprobe=BASE/'probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py'
 source=oldprobe.read_text(encoding='utf8')
 old='assert len(hook)==len(invoke)==len(actor)==len(step)==1 and hook[0].lineno<invoke[0].lineno and actor[0].lineno<step[0].lineno'
 new='assert len(hook)==len(invoke)==len(actor)==len(step)==1 and (hook[0].lineno,hook[0].col_offset)<(invoke[0].lineno,invoke[0].col_offset) and (actor[0].lineno,actor[0].col_offset)<(step[0].lineno,step[0].col_offset)'
 source=once(source,old,new)
 source=source.replace('NEW226_E2_213_SOURCE_AND_SDK_METADATA',KIND)
 source=source.replace('EXPECTED226_TARGET_METADATA.json',EXPECTED_NAME)
 source=source.replace('METADATA226_ONCE_CONSUMED.json',ONCE)
 source=source.replace('ORIGINAL226_TARGET_METADATA_ERROR_','ORIGINAL_E2_FROM226_V3_TARGET_METADATA_ERROR_')
 write(N/PROBE_NAME,source.encode())
 probe_ref=ref(N/PROBE_NAME)
 expected=json.loads((BASE/'source_payload226/EXPECTED226_TARGET_METADATA.json').read_bytes())
 expected['kind']=KIND
 oldname='probe226_E2_NEW_TARGET_METADATA_UNUSED_once.py'
 for key in ('installed_rows','source_rows'):
  selected=[r for r in expected[key] if r['relative']==oldname];assert len(selected)==1
  for row in selected:row.update(relative=PROBE_NAME,bytes=probe_ref['bytes'],SHA=probe_ref['SHA'])
 assert expected['AST_selected_rows'].count(oldname)==1
 expected['AST_selected_rows']=[PROBE_NAME if x==oldname else x for x in expected['AST_selected_rows']]
 expected['scope']='NEW V3 reader-only lexical-order repair;original213/SDK/method/ground checks unchanged;not actual GPU or skill proof'
 put(N/EXPECTED_NAME,expected)
 expected_ref=ref(N/EXPECTED_NAME)
 contract=(V2/'contract_e2_from226.py').read_text(encoding='utf8')
 contract=once(contract,"EXPECTED='529a1bd09cc671bf018ebcfabd1a52f3139935656e8d310850bf5a1c8350445c'","EXPECTED='"+expected_ref['SHA']+"'")
 contract=once(contract,"PROBE='2bbc8657e3fccf26b9e317ebdadf72dc67f25586aad88457dfe2cbc49414d5d9'","PROBE='"+probe_ref['SHA']+"'")
 contract=once(contract,"KIND='NEW226_E2_213_SOURCE_AND_SDK_METADATA'","KIND='"+KIND+"'")
 write(N/'contract_e2_from226.py',contract.encode())
 for name in ('run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py','finalize_e2_from226_actual_evidence_ROOT_ONLY.py'):
  text=(V2/name).read_text(encoding='utf8')
  text=text.replace(oldname,PROBE_NAME).replace('EXPECTED226_TARGET_METADATA.json',EXPECTED_NAME).replace('METADATA226_ONCE_CONSUMED.json',ONCE)
  write(N/name,text.encode())
 install=json.loads((BASE/'source_payload226/INSTALL226_EXACT_SOURCE_BINDINGS.json').read_bytes())
 selected=[r for r in install['files'] if r['relative']==oldname];assert len(selected)==1
 row=selected[0];row.update(relative=PROBE_NAME,local_path=str(N/PROBE_NAME),bytes=probe_ref['bytes'],SHA=probe_ref['SHA'])
 install.update(status='V3_SOURCE_MAP_ONLY_NEW_ROOT_NAMESPACE_REQUIRED',new_reader_purpose=KIND,
  expected_metadata=dict(relative=EXPECTED_NAME,**expected_ref),old231_result_preserved=True)
 put(N/'reports/INSTALL226_DERIVED_V3_EXACT_SOURCE_BINDINGS.json',install)
 interface=[]
 for name in ('contract_e2_from226.py','run_e2_from226_target_metadata_and_wait_ROOT_ONLY.py','finalize_e2_from226_actual_evidence_ROOT_ONLY.py'):
  interface.append(dict(relative=name,**ref(N/name)))
 put(N/'reports/INSTALL_SOURCE_V3.json',dict(status='SOURCE_ONLY_NOT_INSTALLED_NOT_EXECUTED',files=interface,
  selected_probe=dict(relative=PROBE_NAME,**probe_ref),selected_expected=dict(relative=EXPECTED_NAME,**expected_ref),
  selected_KIND=KIND,selected_probe_once=ONCE,original213_worker_SHA=expected['worker_SHA'],
  CPU_witness_SHA=expected['CPU_witness_SHA'],SDK_versions=expected['versions'],same_213_Task_ABI=True,
  no_signal_timeout_V2_retained=True,model_asset_reads=0))
 actual=T/'E2_ACTUAL_TARGET_METADATA_AND_FULL_WORLD_CASE_V231_20261101/reports/ROOT231_ACTUAL_E2_METADATA_AND_ORIGINAL_MEAN_CASE_RETURNED.json'
 actual_value=json.loads(actual.read_bytes());assert actual_value['passed_execution'] is False
 put(N/'reports/BEFORE_USE_V3_ORIGINAL231_FALSE_AND_LEXICAL_REPAIR.json',dict(epoch=time.time(),
  original231_report=ref(actual),original231_passed_execution=False,
  old_reader_false='Original226 actor.lineno<step.lineno rejected the real same-line actor then step',
  repair='Keep all four exact call counts1 and strict ordering;compare(lineno,col_offset),not lineno alone',
  original_worker_reward_physics_TaskABI_SDK_method_ground_checks_unchanged=True,
  original226_V1_V2_and231_sources_or_reports_overwritten=False,
  ROOT_new_namespace_new_authority_CIM_and_purpose_required=True,old_probe_or_fixture_replays=0,
  model_asset_raw_Torch_SDK_GPU_network_Git_calls=0))


if __name__=='__main__':
 try:main()
 except BaseException:
  put(N/'reports/DERIVE_V3_ORIGINAL_ERROR.json',dict(error=traceback.format_exc(),no_automatic_retry=True));raise
