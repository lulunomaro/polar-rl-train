from pathlib import Path
import ast,copy,hashlib,importlib.util,json,shutil
N=Path(__file__).resolve().parent;R=N/'reports';F=N/'controller_three93_source_v3';assert not F.exists();shutil.copytree(N/'controller_three93_source_v2',F)
q=json.loads((R/'NATIVE93_TWO_DISTINCT_TARGET_ALIAS_SOURCE_PREPARED_ACTUAL.json').read_bytes());cpu=json.loads((R/'NATIVE93_TWO_DISTINCT_TARGET_SOURCE_SDK_CPU_RETURNED_ACTUAL.json').read_bytes());fix=json.loads((R/'NATIVE93_SOURCE210_EXACT_BACKEND_METADATA_CORRECTION_RETURNED_ACTUAL.json').read_bytes());assert fix['passed']
with (R/'THREE93_ORIGINAL_TYPED_ROUTING_CPU_LABEL_REJECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(original_error='ValueError actual CPU target/source counters',strict_protocol_correctly_rejected_wrong_target72_literal_on_source210=True,original_fullstate_CPU_not_repeated=True,old_CPU_routing_source_and_partial_spec_retained=True),f,indent=2)
p=F/'h1_210_native93_protocol.py';s=p.read_text('utf8')
s=s.replace("CPU_PATH=JOB+'/job0/FLAT90_SOURCE_SDK_CPU_ACTUAL.json'","CPU_PATH=JOB+'/job0/FLAT93_SOURCE210_BACKEND_LABEL_CORRECTED_CPU_ACTUAL.json'")
s=s.replace("WAITED_PATH=JOB+'/job0/FLAT90_SOURCE_CPU_WAITED_ACTUAL.json'","WAITED_PATH=JOB+'/job0/FLAT93_SOURCE210_BACKEND_LABEL_DERIVED_WAIT_ACTUAL.json'")
meta=fix['value']['metadata_backend_label_correction'];needle="require(v.get('passed') is True";assert s.count(needle)==1
s=s.replace(needle,"require(v.get('metadata_backend_label_correction')=="+repr(meta)+",'exact metadata-only backend correction of original actual sourceCPU')\n "+needle)
needle="require(v.get('actual_waited') is True";assert s.count(needle)==1
s=s.replace(needle,"require(v.get('metadata_only_label_correction') is True and v.get('original_report_SHA')=="+repr(meta['original_report_SHA'])+" and v.get('original_waited_proof_SHA')=="+repr(meta['original_waited_proof_SHA'])+",'original waited CPU identity retained, no invented new execution')\n "+needle)
p.write_text(s,'utf8');ast.parse(s)
for key in ('h1','h1_210'):
 result=cpu['results'][key] if key=='h1' else fix
 spec=dict(q['targets'][key]['spec'],source_CPU_SHA=result['proof']['report_SHA'],CPU_waited_proof_SHA=result['proof_SHA'])
 if key=='h1_210':spec.update(CPU_path=fix['CPU_path'],CPU_proof_path=fix['CPU_proof_path'])
 path=F/(key+'_native93_protocol.py');sp=importlib.util.spec_from_file_location('typed93_corrected_'+key,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 assert m.validate_cpu_value(result['value'],spec);m.validate_waited_value(result['proof'],spec)
 wrong=fix['value'] if key=='h1' else cpu['results']['h1']['value']
 try:m.validate_cpu_value(wrong,spec)
 except ValueError:pass
 else:raise AssertionError('different target CPU must reject')
 out=N/'specs'/key/'NATIVE93_ACTUAL_CPU_BOUND_SPEC_V2_NOT_YET_NODE_SEALED.json';out.parent.mkdir(parents=True,exist_ok=True)
 with out.open('x',encoding='utf8') as f:json.dump(dict(spec=spec,node_controller_manifest_pending=True,actual_target_CPU_reused_no_rerun=True),f,indent=2)
tree=ast.parse((F/'three_slot_common_v1.py').read_bytes());fs=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('terminal','charge_values')];ns={};exec(compile(ast.Module(body=fs,type_ignores=[]),'unchanged_original_accounting_fixture','exec'),ns)
go={k:dict(learning_started_epoch=float(i),max_parent_seconds=3900) for i,k in enumerate(('h1','h1_210','e2'))};c=dict(charged_training_seconds=0.,remaining_training_seconds=2268000.);a=dict(experts={},charged_expert_seconds=0.);rows={k:{} for k in go};rows['e2']=dict(terminal_all_own_children_waited=True,returncode=1,owner_received_terminal_epoch=5.125)
c,a=ns['charge_values'](c,a,go,rows,10.25);assert a['charged_expert_seconds']==10.25+9.25+3.125
c,a=ns['charge_values'](c,a,go,rows,12.5);assert a['charged_expert_seconds']==12.5+11.5+3.125 and a['experts']['e2']['charged_seconds']==3.125
with (R/'THREE93_LABEL_BOUND_ALIAS_ROUTING_ACCOUNTING_V2_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(passed=True,both_actual_target_CPU_and_wait_route_exactly=True,other_target_CPU_rejected=True,original_three_slot_fractional_fee_sum_once_healthy_failure_independent=True,no_model_read_sourceCPU_rerun_GPU_physics_host_or_canonical_IO=True,original_wrong_label_and_old_rejection_preserved=True,actual_controller_GOruntime_pending=True),f,indent=2)
print(json.dumps(dict(passed=True,source_only_controller_v3=True,actual_two_target_CPU_distinct=True)))
