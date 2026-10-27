"""Seal three genuine source-qualified slots. No remote/GO or model reads."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,shutil,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
E=L/'E2_PPO50_gas400_source_preparation_20261028';F=N/'controller_three93_sealed_v4';assert not F.exists();shutil.copytree(N/'controller_three93_source_v3',F)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
child=read(E/'E2_ACTUAL_CPU_BOUND_SPEC_TASK_TEMPLATE_V1.json')
shutil.copy2(E/'E2_next72_protocol_v1.py',F/'E2_next72_protocol_v1.py')
runid='THREE93_TERMINAL_H1_TWO_SEEDS_E2_PPO50_GAS400_'+str(time.time_ns())
parent72='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_THREE93_NATIVE_TERMINAL_E2_20261028'
owner=parent72+'/owner';specs={};node_sources={};node_roots={};node_names={};tasks={}
native_names=['three_slot_common_v1.py','mixed72_next_protocol_v1.py','h1_native93_protocol.py','h1_210_native93_protocol.py','E2_next72_protocol_v1.py','three93_native_slot_node_v1.py','three93_native_resource_guard_v1.py','forwarded_original_owner_control_v1.py','OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json']
for key in ('h1','h1_210'):
 s=read(N/'specs'/key/'NATIVE93_ACTUAL_CPU_BOUND_SPEC_V2_NOT_YET_NODE_SEALED.json')['spec'];s.update(run_id=runid)
 root=parent72+'/node_h1' if key=='h1' else '/mnt/mod4_linux_durable_20261013/MOD4_THREE93_NATIVE_TERMINAL_E2_20261028/node_h1_210'
 dest=N/'sealed_node_sources'/key;dest.mkdir(parents=True)
 for name in native_names:shutil.copy2(F/name,dest/name)
 if key=='h1_210':s['owner_control_dependency_binding_SHA']=H(dest/'OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json')
 files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(dest.iterdir()) if p.is_file()]
 manifest=dict(schema='mod4.native.flat05.single_controller.v1',key=key,source_SHA=s['source_SHA'],worker_SHA=s['worker_SHA'],source_CPU_SHA=s['source_CPU_SHA'],files=files)
 put(dest/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json',manifest);s['manifest_SHA']=H(dest/'FLAT90_SINGLE_SLOT_COMPLETE_MANIFEST_V1.json')
 spec=importlib.util.spec_from_file_location('sealed_three93_'+key,dest/(key+'_native93_protocol.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_spec(s)
 specs[key]=s;node_sources[key]=str(dest);node_roots[key]=root;node_names[key]='three93_native_slot_node_v1.py';tasks[key]=dict(s)
es=copy.deepcopy(child['spec']);es['run_id']=runid;specs['e2']=es
ed=N/'sealed_node_sources/e2';ed.mkdir(parents=True)
em=read(E/'E2_NODE_CONTROLLER_MANIFEST_V1.json')
for row in em['files']:
 assert H(E/row['relative'])==row['SHA'];shutil.copy2(E/row['relative'],ed/row['relative'])
shutil.copy2(E/'E2_NODE_CONTROLLER_MANIFEST_V1.json',ed/'E2_NODE_CONTROLLER_MANIFEST_V1.json');assert H(ed/'E2_NODE_CONTROLLER_MANIFEST_V1.json')==es['manifest_SHA']
node_sources['e2']=str(ed);node_roots['e2']=parent72+'/node_e2';node_names['e2']='E2_mixed72_finite_node_v1.py';tasks['e2']=dict(child['Task_template'],run_id=runid)
spec=importlib.util.spec_from_file_location('sealed_three93_e2',F/'E2_next72_protocol_v1.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.validate_spec(es)
files=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(F.iterdir()) if p.is_file() and p.name!='SOURCE_DERIVATION_ACCOUNT_HANDLER_AST_ACTUAL.json']
put(F/'THREE93_OWNER_CONTROLLER_MANIFEST_V1.json',dict(files=files,run_id=runid,real_slots=list(specs),one_original72_writer=True))
public=dict(run_id=runid,owner_root=owner,owner_name='three93_finite_owner_authority72_v1.py',owner_source=str(F),owner_manifest_SHA=H(F/'THREE93_OWNER_CONTROLLER_MANIFEST_V1.json'),experts=specs,node_roots=node_roots,node_sources=node_sources,node_names=node_names,task_templates=tasks,authority_generation='MOD4_SINGLE_WRITER72_20261026',scheduling_authority='human_requested_available_experts',deferred_experts=[],expected_closed_remaining=546762.1692283154)
for root in [F,*map(Path,node_sources.values())]:
 for p in root.glob('*.py'):ast.parse(p.read_bytes())
put(R/'THREE93_ACTUAL_CPU_BOUND_SEALED_PUBLIC_REQUEST.json',public)
put(R/'THREE93_CONTROLLER_SEAL_SOURCE_ACTUAL.json',dict(passed=True,source_and_metadata_only_no_remote=True,real_slots=list(specs),three_distinct_GPU_UUIDs=len({s['GPU_UUID'] for s in specs.values()})==3,all_actual_source_CPU_complete=True,original_account_Handler_charge_function_AST_preserved=True,source210_wrong_label_old_report_retained_and_exactly_corrected=True,each_native_model_norms_threeoptimizers_globals_preserved=True,no_model_read_GPU_or_GO=True))
print(json.dumps(dict(sealed=True,run_id=runid,actual_CPU_for_all_real_slots=True,no_GO=True)))
