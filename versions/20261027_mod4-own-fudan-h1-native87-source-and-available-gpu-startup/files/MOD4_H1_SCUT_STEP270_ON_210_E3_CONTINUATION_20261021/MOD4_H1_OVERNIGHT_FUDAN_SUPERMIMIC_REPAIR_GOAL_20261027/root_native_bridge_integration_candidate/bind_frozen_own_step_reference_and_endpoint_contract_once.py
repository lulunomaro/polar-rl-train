from pathlib import Path
import json,hashlib,traceback
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent
SOURCE=L/'agent_MOD4_step_reference_conversion_candidate_v2/OWN_STEP_REFERENCE_TABLES_V3_SIDEWALL_REPAIRED_CANDIDATE_NOT_ADMITTED.json'
BASE=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json'
DEST=HERE/'MOD4_OWN_CONVERTED_FUDAN_JUMP_REFERENCE_V1_NOT_ADMITTED.json'
REPORT=L/'reports/OWN_CONVERTED_REFERENCE_NAMED_BINDING_AND_ENDPOINT_ACTUAL.json'
assert not DEST.exists() and not REPORT.exists()
try:
 raw=SOURCE.read_bytes();assert hashlib.sha256(raw).hexdigest()=='9069e57e627549404597be10a65891b77e10b111e3557b8a036984d90134a7db'
 x=json.loads(raw);base=json.loads(BASE.read_bytes())
 x['schema']='mod4.own_step_converted_reference.v1'
 x['metadata']={**x['metadata'],
  'control_dt_s':.01,'foreign_transitions_for_world_model':False,
  'own_step_edge_x_m':.35,'own_platform_height_m':.27,
  'physical_success_unchanged':True,
  'joint_position_range_scale30':base['metadata']['joint_position_range_scale30'],
  'actuator_leg_joint_names':['left_crank','left_hip','right_crank','right_hip'],
  'actuator_wheel_joint_names':['left_wheel_spin','right_wheel_spin'],
  'endpoint_policy':'hold_pose_zero_velocities',
  'before_age0_policy':'fresh ground pose; no negative-age sampling',
  'SDK_joint_order_verified':False,
  'reference_is_a_goal_not_an_applied_action':True,
  'geometric_source_table_SHA':hashlib.sha256(raw).hexdigest(),
  'reference_teacher_source':base['metadata']['source'],
  'native_policy_source_architecture':'new explicit physical30+aux54/static31/obs86/goal146; not same-shape native86 resume',
  'actual_own_step_success':False}
 # Values within301knowncontrols remain byte-for-byte numerical JSON values.
 # Endpoint behavior is implemented by the provider, not by extending sourceair.
 DEST.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':')),'utf8')
 result={'passed':True,'source':{'path':str(SOURCE),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()},
  'derived':{'path':str(DEST),'bytes':DEST.stat().st_size,'SHA':hashlib.sha256(DEST.read_bytes()).hexdigest()},
  'new_table_numeric_states_changed':False,'endpoint_after_age300':'hold pose, set v/w/dq targets0 explicitly',
  'actual_SDK_or_dynamic_skill':False,'root_metadata_only_binding':True,
  'full_body_nonpenetration_and_dynamics':'pending actual source/plant validation'}
except BaseException:
 result={'passed':False,'error':traceback.format_exc(),'all_partial_preserved':True}
 REPORT.write_text(json.dumps(result,indent=2),'utf8');raise
REPORT.write_text(json.dumps(result,indent=2),'utf8')
print(json.dumps({'passed':True,'derived':result['derived']}))

