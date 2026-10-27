"""One saved-JSON source-selection check only, no model read/stat or rollout."""
from pathlib import Path
import sys,json,hashlib,traceback
D=Path(__file__).resolve().parent;T=D.parent.parent;R=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/reports';sys.path.insert(0,str(D))
from native88C_frozen_acceptance_contract_v1 import select_source,FINAL_SHA
try:
 paths=[R/'NATIVE88C_READER_REPAIRED_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json',R/'NATIVE88C_CASE_SAFE_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_V2_ACTUAL.json']
 cpu,collection=[json.loads(p.read_bytes()) for p in paths];selected=select_source(cpu,collection,{})
 assert selected['selected_key']=='h1' and selected['source']['final']['SHA']==FINAL_SHA and selected['planned_seeds']==[20260928]
 with (D/'FIXED_QUALIFIED_SOURCE_METADATA_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,scope='saved formal qualification/closure JSON source selection only',selected_key='h1',model_SHA_from_qualified_metadata=FINAL_SHA,selection_scope=selected['selection_scope'],seed=20260928,episodes=1,
  input_JSON_pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},actual_model_stat_read_or_hash=False,actual_N1_SDK_or_policy_evaluation=False),f,indent=2)
 print(json.dumps(dict(passed=True,selected_key='h1',source_metadata_only=True)))
except BaseException:
 with (D/'FIXED_SOURCE_METADATA_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,error=traceback.format_exc(),metadata_only=True),f,indent=2)
 raise
