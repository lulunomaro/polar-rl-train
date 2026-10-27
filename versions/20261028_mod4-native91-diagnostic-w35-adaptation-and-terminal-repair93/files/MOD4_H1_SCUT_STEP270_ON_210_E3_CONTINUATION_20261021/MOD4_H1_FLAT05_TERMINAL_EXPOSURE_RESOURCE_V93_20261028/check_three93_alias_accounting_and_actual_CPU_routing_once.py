"""Bounded CPU source checks. No model/SDK/host/physics/account IO."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json
N=Path(__file__).resolve().parent;F=N/'controller_three93_source_v2';R=N/'reports'
q=json.loads((R/'NATIVE93_TWO_DISTINCT_TARGET_ALIAS_SOURCE_PREPARED_ACTUAL.json').read_bytes())
cpu=json.loads((R/'NATIVE93_TWO_DISTINCT_TARGET_SOURCE_SDK_CPU_RETURNED_ACTUAL.json').read_bytes());assert cpu['passed']
scopes=[]
for key in ('h1','h1_210'):
 spec=q['targets'][key]['spec'];result=cpu['results'][key]
 spec=dict(spec,source_CPU_SHA=result['proof']['report_SHA'],CPU_waited_proof_SHA=result['proof_SHA'])
 p=F/(key+'_native93_protocol.py');s=importlib.util.spec_from_file_location('source_only_'+key,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 assert m.validate_cpu_value(result['value'],spec)
 m.validate_waited_value(result['proof'],spec)
 other='h1_210' if key=='h1' else 'h1'
 try:m.validate_cpu_value(cpu['results'][other]['value'],spec)
 except ValueError:scopes.append(key+'_rejects_other_target_CPU')
 else:raise AssertionError('foreign target CPU proof accepted')
 scopes.append(key+'_actual_target_CPU_and_wait_routed_exactly')
 spath=N/'specs'/key/'NATIVE93_ACTUAL_CPU_BOUND_SPEC_NOT_YET_NODE_SEALED.json';spath.parent.mkdir(parents=True,exist_ok=True)
 with spath.open('x',encoding='utf8') as f:json.dump(dict(spec=spec,node_controller_manifest_pending=True,actual_target_CPU_reused_no_rerun=True),f,indent=2)
tree=ast.parse((F/'three_slot_common_v1.py').read_bytes())
fs=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('terminal','charge_values')]
space={};exec(compile(ast.Module(body=fs,type_ignores=[]),'original_unchanged_accounting_fixture','exec'),space)
go={k:dict(learning_started_epoch=float(i),max_parent_seconds=3900) for i,k in enumerate(('h1','h1_210','e2'))}
c=dict(charged_training_seconds=0.,remaining_training_seconds=2268000.)
a=dict(experts={},charged_expert_seconds=0.)
rows={k:{} for k in go};rows['e2']=dict(terminal_all_own_children_waited=True,returncode=1,owner_received_terminal_epoch=5.125)
c,a=space['charge_values'](c,a,go,rows,10.25)
expected=10.25+9.25+3.125
assert a['charged_expert_seconds']==expected and a['experts']['e2']['actual_returncode']==1
assert a['experts']['h1']['charged_seconds']==10.25 and a['experts']['h1_210']['charged_seconds']==9.25
c,a=space['charge_values'](c,a,go,rows,12.5)
assert a['experts']['e2']['charged_seconds']==3.125 and a['charged_expert_seconds']==12.5+11.5+3.125
scopes+=['three_independent_actual_GO_intervals_sum_once_fractional_no_rounding','failed_E2_terminal_stops_its_fee_only_healthy_H1_continue']
with (R/'THREE93_ALIAS_ROUTING_AND_UNCHANGED_ACCOUNTING_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,scopes=scopes,source_only_controller_not_launched=True,actual_source_CPU_evidence_used_as_metadata_only=True,no_model_GPU_SDK_remote_physics_or_canonical_IO=True,accounting_function_literal_original=True),f,indent=2)
print(json.dumps(dict(passed=True,scopes=len(scopes),actual_target_CPU_never_cross_projected=True)))
