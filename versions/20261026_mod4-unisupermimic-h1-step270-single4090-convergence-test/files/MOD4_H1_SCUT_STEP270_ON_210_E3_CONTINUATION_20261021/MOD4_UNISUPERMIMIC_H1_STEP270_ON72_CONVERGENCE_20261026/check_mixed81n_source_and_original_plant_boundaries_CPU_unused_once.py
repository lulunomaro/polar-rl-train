"""Saved-source/metadata boundaries only. Actual target SDK and real plant still required."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import time

H=Path(__file__).resolve().parent;T=H.parent
P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'
F=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81N_20261026'
B=F/'payloads/e2'
read=lambda p:json.loads(Path(p).read_bytes())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def functions(s):return {n.name:n for n in ast.parse(s).body if isinstance(n,ast.FunctionDef)}
old=(P/'controllers/three_slot_common_v1.py').read_text('utf8');new=(F/'controllers/three_slot_common_v1.py').read_text('utf8')
a,b=functions(old),functions(new)
for name in a:
    if name!='valid_ready':assert ast.dump(a[name])==ast.dump(b[name]),name
ready=copy.deepcopy(b['valid_ready']);assert ast.unparse(ready.body[0].test)=="spec.get('finite_method_test')";ready.body.pop(0)
assert ast.dump(ready)==ast.dump(a['valid_ready'])
assert (F/'controllers/three_slot_finite_owner_v1.py').read_bytes()==(P/'controllers/three_slot_finite_owner_v1.py').read_bytes()
original=(B/'h1_step270_production_worker_v1.py').read_text('utf8')
modified=(B/'h1_unisupermimic_step270_worker_v1.py').read_text('utf8')
for txt in (original,modified):ast.parse(txt)
# Restore the exact approved syntactic differences before comparing the remaining worker.
modified=modified.replace("p.add_argument('--job',type=int,default=0);",'',1)
modified=modified.replace("J/('GO_'+phase.upper()+'.json')","B/('GO_'+phase.upper()+'.json')",1)
modified=modified.replace("assert go['source_qualification_kind']=='UNISUPERMIMIC_ACTUAL_H1_STEP270_CROSSHOST_SOURCE_SDK_CPU'","assert go['actual_H1_step270_scope_admitted'] and not go['actual_H1_prelaunch_v2_scope_admitted']",1)
modified=modified.replace(";sys.path.insert(0,str(B/'source'))",'',1)
ta,tb=ast.parse(original),ast.parse(modified)
for tree in (ta,tb):
    main=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    main.body=[n for n in main.body if not (isinstance(n,ast.FunctionDef) and n.name=='learn')]
assert ast.dump(ta)==ast.dump(tb)
before={r['relative']:r for r in read(F/'payloads/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files']}
after={r['relative']:r for r in read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files']}
protected=[name for name in before if name.startswith(('job0/runtime/','job0/assets/','lib/'))]
assert protected
for name in protected:assert before[name]['SHA']==after[name]['SHA'] and before[name]['bytes']==after[name]['bytes'],name
for name in ['h1_step270_sdk_runtime_candidate.py','h1_step270_path_reward_v1.py','step270_goal_and_scut_rates_candidate.py','h1_production_control_prefix_trace_v1.py','h1_lifetime_goal_counter_v1.py','sampling_trace_npz_lossless_v1.py','h1_prefix_pair_retention_v1.py']:
    assert sha(B/name)==sha(F/'payloads/h1'/name),name
assert sha(B/'same_optimized_source_contract_metadata_candidate_v1.py')=='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e'
ns={'json':json,'hashlib':hashlib}
exec(compile(ast.Module(body=[b['valid_ready']],type_ignores=[]),'<actual_mixed_ready>','exec'),ns)
q=read(F/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json');s=q['specs']['e2']
v=dict(kind='UNISUPERMIMIC_ACTUAL_H1_STEP270_CROSSHOST_SOURCE_SDK_CPU',passed=True,source_SHA=s['source_SHA'],GPU_UUID=s['GPU_UUID'],upstream_revision='faf7818e8abac3ec6abb8f00e6e904d3577f800b',actual_installed_CPU_passed=True,native_joint_states=30,actions=6,source80_actual_cost_models_allout_passed=True,not_production_E2_source_or_skill_qualification=True,actual_H1_source_SDK_CPU_passed=True,original_H1_270_physics_source_exact=True)
def row(value):return dict(key='e2',phase='ready',manifest_SHA=s['manifest_SHA'],closed_source_CPU=dict(value=value,SHA=hashlib.sha256(json.dumps(value,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True))
assert ns['valid_ready'](row(v),s)
rejected=[]
for name,val in [('actual_H1_source_SDK_CPU_passed',False),('original_H1_270_physics_source_exact',False),('source_SHA','0'*64),('GPU_UUID','other'),('upstream_revision','0'*40),('native_joint_states',6),('actions',30),('source80_actual_cost_models_allout_passed',False),('kind','closed_same_backend_policy50_production')]:
    bad=dict(v);bad[name]=val;assert not ns['valid_ready'](row(bad),s);rejected.append(name)
result=dict(epoch=time.time(),passed_source_CPU=True,original_owner_bytes_and_charge_functions_AST_exact=True,original_production_ready_after_removing_exact_new_method_branch_AST_equal=True,worker_outside_exact_parser_GO_and_new_learn_dispatch_AST_equal=True,protected_runtime_assets_lib_files=len(protected),original270_goal_V8_reward_trace_counter_retention_exact=True,metadata_CRLF_exact=True,method_ready_negative_fields=rejected,actual_target_H1_SDK_RSL_whole_source_CPU_still_required=True,real20k_Isaac100Hz_2p5ms_G1_algorithm_policy_update_not_yet_observed=True,no_GO_or_budget_or_GPU_action=True)
with (H/'reports/MIXED81N_SOURCE_ORIGINAL_PLANT_AND_READY_BOUNDARIES_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(result,f,indent=2)
print(json.dumps(dict(source_CPU_passed=True,protected_files=len(protected),negative_cases=len(rejected))))
