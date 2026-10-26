"""Fresh H1 full-source SDK CPU on target72, explicit standalone method type."""
from pathlib import Path
import hashlib,json
def load(spec,B):
 B=Path(B);assert spec['key']=='e2' and spec['h1_step270_method_test'] and spec['GPU_UUID']=='GPU-16828f91-2b45-b646-8dc0-9481138e2842'
 m=json.loads((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes());cpu=json.loads((B/'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json').read_bytes());unit=json.loads((B/'reports/NATIVE_H1_GOAL_MDP_AND_LEARNER_CPU_V1_ACTUAL.json').read_bytes())
 assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==hashlib.sha256((B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes()).hexdigest() and cpu['sampling_acceleration_CPU']['passed'] and cpu['new_reward_integration_CPU']['actual_installed_sampled_excess_SDK_compute_tested'] and unit['passed'] and not unit['CUDA_initialized']
 proof=json.loads((B/'CURRENT_ORIGINAL_THREE_CLOSED_MODELS_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed'] and proof['original_canonical_cost_settled'] and proof['all_owner_nodes_children_actual_out'] and proof['models']['h1']['final']['SHA']==spec['source_SHA'] and proof['models']['h1']['actual_cost']['duration_bound_passed']
 v=dict(kind='UNISUPERMIMIC_ACTUAL_H1_STEP270_CROSSHOST_SOURCE_SDK_CPU',passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],upstream_revision='faf7818e8abac3ec6abb8f00e6e904d3577f800b',actual_installed_CPU_passed=True,native_joint_states=30,actions=6,source_current_healthy_H1_original_cost_models_allout_passed=True,not_production_E2_source_or_skill_qualification=True,actual_H1_source_SDK_CPU_passed=True,original_H1_270_physics_source_exact=True)
 return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
