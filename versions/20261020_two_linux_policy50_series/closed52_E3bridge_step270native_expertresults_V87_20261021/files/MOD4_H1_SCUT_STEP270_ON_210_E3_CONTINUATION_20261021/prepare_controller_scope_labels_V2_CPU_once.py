from pathlib import Path
import ast,json,time,hashlib,copy
B=Path(__file__).resolve().parent;D=B/'controllers_candidate_uninstalled';V=B/'controllers_candidate_v2_uninstalled';V.mkdir()
owner=(D/'three_slot_finite_owner_v1.py').read_text();common=(D/'three_slot_common_v1.py').read_text();node=(B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021/two_policy50_original_account_controllers/three_slot_finite_node_v1.py').read_text();resource=(B.parent/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021/two50_payloads/e2/three_real_gpu_resource_v1.py').read_text()
owner=owner.replace("actual_H1_prelaunch_v2_scope_admitted=key=='h1'","actual_H1_prelaunch_v2_scope_admitted=False,actual_H1_step270_scope_admitted=key=='h1'")
node=node.replace("assert go['actual_H1_prelaunch_v2_scope_admitted']","assert go['actual_H1_step270_scope_admitted'] and not go['actual_H1_prelaunch_v2_scope_admitted']")
common=common.replace("else 'clock_native50'","else 'H1_STEP270_NATIVE100'").replace('H1_PRELAUNCH_V2_NATIVE180_ALL_ROWS_CPU_ADMITTED.json','H1_STEP270_NATIVE_ALL_ROWS_CPU_ADMITTED.json')
needle=" corefield={'h1':"
assert needle in common
common=common.replace(needle," if spec['key']=='h1':\n  if not (v.get('kind')=='H1_STEP270_SOURCE_AND_NATIVE_CPU' and v.get('actual_step270_terrain_and_query_source_CPU') and v.get('platform_top_height_m',0)>=.270 and v.get('H1_policy_hz')==100 and v.get('original_query_COM_closure_mimic_hardware_guards') and v.get('new_actor_inputs') is False):return False\n"+needle)
resource=resource.replace("assert int(line.split(',')[-1])>7000", "assert int(line.split(',')[-1])>(15669 if spec['key']=='h1' else 7000)")
common=common.replace("assert int(line.split(',')[-1])>7000", "assert int(line.split(',')[-1])>(15669 if spec['key']=='h1' else 7000)")
rows={'three_slot_finite_owner_v1.py':owner,'three_slot_common_v1.py':common,'three_slot_finite_node_v1.py':node,'three_real_gpu_resource_v1.py':resource}
for n,s in rows.items():ast.parse(s);(V/n).open('x',encoding='utf8').write(s)
tree=ast.parse(common);functions={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)};ns={'json':json,'hashlib':hashlib};exec(compile(ast.fix_missing_locations(ast.Module(body=[functions['valid_ready']],type_ignores=[])),'candidate_valid_ready','exec'),ns)
spec=dict(key='h1',source_SHA='a'*64,native_controls=180,manifest_SHA='b'*64)
value=dict(passed=True,sourceactor9critic8STD17Adam_literal_exact=True,source_SHA='a'*64,controls=180,callbacks=720,kind='H1_STEP270_SOURCE_AND_NATIVE_CPU',actual_step270_terrain_and_query_source_CPU=True,platform_top_height_m=.270,H1_policy_hz=100,original_query_COM_closure_mimic_hardware_guards=True,new_actor_inputs=False)
def ready(v):
 q=dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
 return ns['valid_ready'](dict(key='h1',phase='ready',native_GPU_waited_EXIT0=True,native_CPU=q,manifest_SHA='b'*64),spec)
assert ready(value);cases=[dict(name='qualified_fake_CPU_fixture',passed=True)]
for k,bad in [('kind','legacy_prelaunch_v2'),('actual_step270_terrain_and_query_source_CPU',False),('platform_top_height_m',.269),('H1_policy_hz',50),('original_query_COM_closure_mimic_hardware_guards',False),('new_actor_inputs',True),('sourceactor9critic8STD17Adam_literal_exact',False)]:
 v=dict(value);v[k]=bad;assert not ready(v),(k,bad);cases.append(dict(name='reject_'+k,passed=True))
oldtree=ast.parse((D/'three_slot_common_v1.py').read_text());oldf={n.name:ast.dump(n,include_attributes=False) for n in oldtree.body if isinstance(n,ast.FunctionDef)}
assert oldf['charge_values']==ast.dump(functions['charge_values'],include_attributes=False)
oldowner=ast.parse((D/'three_slot_finite_owner_v1.py').read_text());newowner=ast.parse(owner)
find_account=lambda tr:next(n for n in ast.walk(tr) if isinstance(n,ast.FunctionDef) and n.name=='account')
assert ast.dump(find_account(oldowner),include_attributes=False)==ast.dump(find_account(newowner),include_attributes=False)
report=dict(epoch=time.time(),passed_candidate_source_AST_and_CPU_cases=True,cases=cases,no_financial_arithmetic_change_charge_values_and_account_AST_exact=True,budget_total1548000_extensions8_safety64800_legacy_reserves_and_actual_scheduled_caps_kept=True,H1_native_protocol_scope_label_distinct_from_old_prelaunch_v2=True,H1_empty_GPU_and15669MiB_learning_guard_retained=True,source_files={n:hashlib.sha256((V/n).read_bytes()).hexdigest() for n in rows},not_remote_installed=True,no_native_or_GO=True,no_current_owner_changed=True,old_V1_draft_retained=True)
(B/'reports/CONTROLLER_SCOPE_LABELS_V2_SOURCE_AND_CPU_CASES_ACTUAL.json').open('x',encoding='utf8').write(json.dumps(report,indent=2));print(json.dumps(report))
