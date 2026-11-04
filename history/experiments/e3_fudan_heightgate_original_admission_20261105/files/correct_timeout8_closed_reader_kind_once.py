"""Reinterpret the already-closed metadata with the correct V3 kind; no physical replay."""
from pathlib import Path
import json,hashlib,copy,time
D=Path(__file__).resolve().parent
inputs=[D/'FDNTIMEOUT8_FROZEN_CLOSED_RESULT.json',D/'FDNTIMEOUT8_FROZEN_ORIGINAL_SCOPE_RESULT.json']
outputs=[D/'FDNTIMEOUT8_FROZEN_CLOSED_READER_V2_RESULT.json',D/'FDNTIMEOUT8_FROZEN_ORIGINAL_SCOPE_READER_V2_RESULT.json',D/'FDNTIMEOUT8_FROZEN_COLLECTOR_KIND_ERRATUM_V1.json']
assert not any(p.exists()for p in outputs)
raws=[p.read_bytes()for p in inputs];a,o=[json.loads(raw)for raw in raws];q=o['actual_parent_wait_qualification']
assert a['root']==o['root']and a['closed']is True and q['kind']=='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V3_TIMEOUT8'and q['qualified']is True and q['errors']==[]
assert len(q['checks'])>16 and all(isinstance(v,dict)and v.get('passed')is True for v in q['checks'].values())
assert o['source_binding']['sha256']=='3e64ebca251b0457409fe83521da69c99378f4fedd7726c7d5761c6a39ac868e'
for item in(a,o):
 assert item['execution_qualified']is False and [k for k,v in item['execution_checks'].items()if v is not True]==['FDN_actual_wait_qualified']

def matching_qualification(node):
 if isinstance(node,dict):
  if node==q:return True
  return any(matching_qualification(v)for v in node.values())
 if isinstance(node,list):return any(matching_qualification(v)for v in node)
 return False
assert matching_qualification(a['metadata'])
source=(D/'collect_fudan_timeout8_frozen_original_once.py').read_text(encoding='utf8')
assert source.count('qualification.get("kind") == "FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V2_N20000"')==1
correction=dict(kind='CLOSED_METADATA_READER_KIND_ONLY_ERRATUM_NOT_NATIVE_RETRY',epoch=time.time(),originals=[dict(path=str(p),SHA256=hashlib.sha256(raw).hexdigest())for p,raw in zip(inputs,raws)],old_collector_expected_kind='FDN_ORIGINAL_N80_ACTUAL_WAIT_QUALIFICATION_V2_N20000',actual_and_correct_kind=q['kind'],actual_original_parent_qualified=True,all_actual_parent_checks_passed=len(q['checks']),other_execution_checks_unchanged=True,old_false_files_preserved=True,models_raw_SDK_SSH_GPU_canonical_or_new_qualification_executions=0,skill_or_recipe_rows_changed=False)
for item,out in zip((a,o),outputs[:2]):
 fixed=copy.deepcopy(item);fixed['execution_qualified']=True;fixed['execution_checks']['FDN_actual_wait_qualified']=True
 if 'failed_execution_checks'in fixed:fixed['failed_execution_checks']=[]
 fixed['reader_correction']=correction
 out.write_text(json.dumps(fixed,indent=2,allow_nan=False),encoding='utf8')
outputs[2].write_text(json.dumps(correction,indent=2),encoding='utf8')
s=o['original_worker_outcome_verbatim'];print(json.dumps(dict(outputs=[str(p)for p in outputs],actual_parent_qualified=q['qualified'],corrected_reader_execution_qualified=True,original_first_episode_credits=s['original_first_episode_recovery_credits'],original_request_denominator=s['original_recovery_request_denominator'],physical_or_original_collector_replay=False),indent=2))
