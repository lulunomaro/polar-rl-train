"""Actual saved JSON/source only; never executes observer or reads a model."""
from pathlib import Path
import sys,json,ast,hashlib,copy,traceback
D=Path(__file__).resolve().parent;T=D.parent.parent;N=T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88B_20261027';R=N/'reports';sys.path.insert(0,str(D))
from native88_closing_protocol_v1 import bind_prepared_detached,validate_detached,validate_actual_GO_binding,closing_gate
def read(p):return json.loads(p.read_bytes())
def main():
 paths=[R/'NATIVE88_TWO_PAYLOADS_SOURCE_PREPARED_ACTUAL.json',R/'NATIVE88B_ACTUAL_OWNER_NODES_DETACHED.json',R/'NATIVE88B_ACTUAL_SIGNED_TWO_GO_METADATA_ACTUAL.json',R/'NATIVE88_ACTUAL_TWO_SOURCE_CPU_AND_RESOURCE_RETURNED_ACTUAL.json']
 prepared,raw,gv,cpu=map(read,paths);before=copy.deepcopy(raw);q=bind_prepared_detached(raw,prepared);assert raw==before
 assert validate_detached(q,prepared) and validate_actual_GO_binding(gv['go'],q)
 assert closing_gate(gv['go'],max(x['nominal_end_epoch'] for x in gv['go'].values())-900)
 try:closing_gate(gv['go'],max(x['nominal_end_epoch'] for x in gv['go'].values())-901)
 except AssertionError:pass
 else:raise AssertionError('901 gate accepted')
 assert cpu['passed'] and set(cpu['results'])=={'h1','recovery'}
 for key in ('h1','recovery'):
  v=cpu['results'][key]['ready_envelope']['value'];assert v['passed'] and v['source_SHA']==q['specs'][key]['source_SHA'] and v['actual_GPU_runtime_readback_passed'] is False
 # Imported source references remain source reads, not model/actor imports.
 fee_source=(D.parent/'native87R5_closing_typed_source/native87R5_closing_protocol_v1.py').read_bytes();new_source=(D/'native88_closing_protocol_v1.py').read_bytes()
 fun=lambda raw,name:next(x for x in ast.parse(raw).body if isinstance(x,ast.FunctionDef) and x.name==name)
 assert ast.dump(fun(fee_source,'validate_fees'))==ast.dump(fun(new_source,'validate_fees'))
 for p in D.glob('*.py'):ast.parse(p.read_bytes())
 no_enumeration={}
 for name in ('native88_observer_readonly_remote_v1.py','native88_close_readonly_remote_v1.py'):
  tree=ast.parse((D/name).read_bytes());assert not any(isinstance(n,ast.Attribute) and n.attr=='process_iter' for n in ast.walk(tree));no_enumeration[name]=True
 value=dict(passed=True,count=8,scope='actual saved88B receipt/schema/AST source only',run_id=q['run_id'],actual_GO_epoch={k:v['learning_started_epoch'] for k,v in gv['go'].items()},
  original_actual_receipts_not_modified=True,owner_script_enriched_from_prepared_only=True,own_children_optional_receipts_not_invented=True,
  required_closing_evidence='actual node PID/create from own NODE_IDENTITY matched to deployed PID; original worker/child-wait receipts; owner72 additionally waits recovery node+worker out',
  V1_own_children_required_negative_is_superseded=True,original_fee_function_AST_exact=True,active_helpers_no_process_enumeration=no_enumeration,
  input_pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},source_pins={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in D.glob('*.py')},
  actual_observer_collector_reviewer_executed=False,network_GPU_model_or_raw_access=False)
 with (D/'ACTUAL88B_RECEIPT_INTERFACE_SOURCE_INCREMENT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
 print(json.dumps(dict(passed=True,count=8,run_id=q['run_id'])))
if __name__=='__main__':
 try:main()
 except BaseException:
  with (D/'ACTUAL88B_RECEIPT_INTERFACE_SOURCE_INCREMENT_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,error=traceback.format_exc(),source_metadata_only=True),f,indent=2)
  raise
