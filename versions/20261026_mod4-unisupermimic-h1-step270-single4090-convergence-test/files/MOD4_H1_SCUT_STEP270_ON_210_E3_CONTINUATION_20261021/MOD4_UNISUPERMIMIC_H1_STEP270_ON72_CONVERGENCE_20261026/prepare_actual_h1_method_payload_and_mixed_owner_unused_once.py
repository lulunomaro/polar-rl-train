"""New explicit method payload; untouched H1/E3 production payloads continue separately."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

H=Path(__file__).resolve().parent;T=H.parent
P=T/'H1_STEP270_THREE_EXPERTS_RESOURCE_V80_20261026'
F=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81M_20261026'
J=T/'MOD4_UNISUPERMIMIC_WHEEL_LEG_SINGLE4090_TEST_20261026'
read=lambda p:json.loads(Path(p).read_bytes())
digest=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert read(H/'reports/NATIVE_H1_GOAL_MDP_AND_LEARNER_CPU_V1_ACTUAL.json')['passed']
qpath=F/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json'
q=read(qpath);assert set(q['specs'])=={'h1','recovery'}
B=F/'payloads/e2';assert not B.exists();shutil.copytree(F/'payloads/h1',B)
(B/'source').mkdir()
shutil.copytree(H/'source/supermimic_vendor_v2',B/'source/supermimic_vendor_v2')
shutil.copy2(H/'source/h1_supermimic_bridge_v1.py',B/'source/h1_supermimic_bridge_v1.py')
shutil.copy2(H/'test_native_h1_goal_mdp_and_learner_CPU_v1.py',B/'test_native_h1_goal_mdp_and_learner_CPU_v1.py')

original=(B/'h1_step270_production_worker_v1.py').read_text('utf8')
worker=original.replace("p.add_argument('--phase'","p.add_argument('--job',type=int,default=0);p.add_argument('--phase'",1)
worker=worker.replace("B/('GO_'+phase.upper()+'.json')","J/('GO_'+phase.upper()+'.json')",1)
old="assert go['actual_H1_step270_scope_admitted'] and not go['actual_H1_prelaunch_v2_scope_admitted']"
assert worker.count(old)==1
worker=worker.replace(old,"assert go['source_qualification_kind']=='UNISUPERMIMIC_ACTUAL_H1_STEP270_CROSSHOST_SOURCE_SDK_CPU'",1)
worker=worker.replace("B=Path(__file__).resolve().parent;J=B/'job0'","B=Path(__file__).resolve().parent;J=B/'job0';sys.path.insert(0,str(B/'source'))",1)
start=worker.index(' def learn(runner,n,log_dir):');end=worker.index(' rescue_training.learn=learn',start)
worker=worker[:start]+" def learn(runner,n,log_dir):\n  from h1_supermimic_bridge_v1 import run\n  return run(runner,n,log_dir,B,J,out,task,go,src,phase)\n"+worker[end:]
ast.parse(worker)
(B/'h1_unisupermimic_step270_worker_v1.py').write_text(worker,'utf8')
(B/'reports/H1_ORIGINAL_PRODUCTION_WORKER_REFERENCE_BYTES.txt').write_bytes((B/'h1_step270_production_worker_v1.py').read_bytes())

base_common=(P/'controllers/three_slot_common_v1.py').read_text('utf8')
offline_common=(J/'payload/three_slot_common_v1.py').read_text('utf8')
prefix='def valid_ready(row,spec):\n';start=offline_common.index(prefix)+len(prefix);end=offline_common.index(" if spec.get('policy_hz')==50:",start)
branch=offline_common[start:end]
branch=branch.replace('UNISUPERMIMIC_MOD4_NATIVE30_ACTION6_FINITE_METHOD_TEST','UNISUPERMIMIC_ACTUAL_H1_STEP270_CROSSHOST_SOURCE_SDK_CPU')
branch=branch.replace("v.get('not_production_E2_source_or_skill_qualification')","v.get('not_production_E2_source_or_skill_qualification') and v.get('actual_H1_source_SDK_CPU_passed') and v.get('original_H1_270_physics_source_exact')")
owner_common=base_common.replace(prefix,prefix+branch,1)
(F/'controllers/three_slot_common_v1.py').write_text(owner_common,'utf8')
# Only the method node gets the H1 memory threshold on its selected second-host slot.
node_common=base_common.replace("15669 if spec['key']=='h1' else 7000","15669 if spec['key']=='h1' or spec.get('h1_step270_method_test') else 7000")
(B/'three_slot_common_v1.py').write_text(node_common,'utf8')
resource=(P/'payloads/e2/three_real_gpu_resource_v1.py').read_text('utf8').replace("15669 if spec['key']=='h1' else 7000","15669 if spec['key']=='h1' or spec.get('h1_step270_method_test') else 7000")
(B/'three_real_gpu_resource_v1.py').write_text(resource,'utf8')

guard='''"""Fresh H1 full-source SDK CPU on target72, explicit standalone method type."""
from pathlib import Path
import hashlib,json
def load(spec,B):
 B=Path(B);assert spec['key']=='e2' and spec['h1_step270_method_test'] and spec['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 m=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());cpu=json.loads((B/'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json').read_bytes());unit=json.loads((B/'reports/NATIVE_H1_GOAL_MDP_AND_LEARNER_CPU_V1_ACTUAL.json').read_bytes())
 assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest() and cpu['sampling_acceleration_CPU']['passed'] and cpu['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested'] and unit['passed'] and not unit['CUDA_initialized']
 proof=json.loads((B/'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out'] and proof['models']['h1']['final']['SHA']==spec['source_SHA'] and proof['models']['h1']['actual_cost']['duration_bound_passed']
 v=dict(kind='UNISUPERMIMIC_ACTUAL_H1_STEP270_CROSSHOST_SOURCE_SDK_CPU',passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],upstream_revision='faf7818e8abac3ec6abb8f00e6e904d3577f800b',actual_installed_CPU_passed=True,native_joint_states=30,actions=6,source80_actual_cost_models_allout_passed=True,not_production_E2_source_or_skill_qualification=True,actual_H1_source_SDK_CPU_passed=True,original_H1_270_physics_source_exact=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
'''
(B/'closed_production_continuation_CPU_v2.py').write_text(guard,'utf8')
task=read(B/'job0/TASK.json');task.update(id=F.name+'_H1_UNISUPERMIMIC_ON72',standalone_H1_new_method=True,algorithm='pinned_UniSuperMimic_tensor_learner_with_explicit_goal_root_reference',new_policy_obs128_history10_goal73_not_PPO35=True,not_a_production_E2_or_H1_source=True)
(B/'job0/TASK.json').write_text(json.dumps(task,indent=2),'utf8')
auth=dict(epoch=time.time(),human_requested_H1_step270_convergence_test=True,existing_success_270mm_dualwheel_contact_and_200callbacks_retained=True,unchanged_original_H1_files=[dict(relative=r['relative'],bytes=r['bytes'],SHA=r['SHA']) for r in read(F/'payloads/h1/THREE_SLOT_COMPLETE_MANIFEST_V1.json')['files'] if r['relative'].startswith(('job0/runtime/','job0/assets/','lib/'))],new_root_reference_not_successful_mocap=True,new_actor_input128_vs_PPO35_and_random_initialization_preclude_causal_algorithm_speed_ratio=True,not_explicit_human_approval_of_exact_test_hyperparameters=True,no_original_approval_JSON_rewritten=True)
(B/'H1_SUPERMIMIC_NEW_METHOD_SOURCE_AUTH_ACTUAL.json').write_text(json.dumps(auth,indent=2),'utf8')
m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');before={r['relative']:r for r in m['files']};rows=[]
for p in sorted(B.rglob('*')):
    if not p.is_file() or p.name=='THREE_SLOT_COMPLETE_MANIFEST_V1.json' or '__pycache__' in p.parts:continue
    rel=p.relative_to(B).as_posix()
    if p.suffix=='.py':ast.parse(p.read_text('utf8'))
    # Existing large model/assets retain actual producer hashes; no content reread for preparation.
    sha=before[rel]['SHA'] if p.suffix in ('.pt','.npz','.usd','.stl') else digest(p)
    rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=sha))
m.update(key='e2',files=rows,kind='EXPLICIT_H1_SUPERMIMIC_TEST_ON_TARGET72_NOT_E2_PRODUCTION',not_production_source=True)
(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').write_text(json.dumps(m,indent=2),'utf8')
e2old=read(P/'reports/THREE_EXPERTS_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json')['specs']['e2']
spec=dict(e2old,source_SHA=q['specs']['h1']['source_SHA'],source_Adamstep=q['specs']['h1']['source_Adamstep'],source_filename=q['specs']['h1']['source_filename'],previous_runtime_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_three_experts_2610v80/e2',policy_hz=100,source_policy_hz=100,finite_method_test=True,h1_step270_method_test=True,closed_production_continuation=True,cross_host_qualified_source=False,reward_migration=False,production_script='h1_unisupermimic_step270_worker_v1.py',manifest_SHA=digest(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'))
q['payloads']['e2']=str(B);q['specs']['e2']=spec;q['sources']['e2']=dict(q['sources']['h1']);q['roots']['e2']='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_mixed_supermimic_2610v81m/e2'
assert set(q['specs'])=={'h1','e2','recovery'}
history=F/'preparation_exact_history';history.mkdir();shutil.copy2(qpath,history/'H1_E3_only_pre_method_q.original_bytes.txt')
qpath.write_text(json.dumps(q,indent=2),'utf8')
with (H/'reports/ACTUAL_MIXED81M_THREE_SLOT_PAYLOADS_PREPARED_NO_GO.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),H1_PPO=q['sources']['h1'],H1_UniSuperMimic=q['sources']['e2'],E3_PPO=q['sources']['recovery'],GPU_mapping={k:s['GPU_UUID'] for k,s in q['specs'].items()},one_original_three_slot_writer=True,strict86412_guard_retained=True,no_GO=True,source80_E2_model_retained_not_scheduled_on_test_card=True,new_native_actor_not_a_production_checkpoint=True),f,indent=2)
print(json.dumps(dict(three_slot_mixed_payloads_prepared=True,no_GO=True)))
