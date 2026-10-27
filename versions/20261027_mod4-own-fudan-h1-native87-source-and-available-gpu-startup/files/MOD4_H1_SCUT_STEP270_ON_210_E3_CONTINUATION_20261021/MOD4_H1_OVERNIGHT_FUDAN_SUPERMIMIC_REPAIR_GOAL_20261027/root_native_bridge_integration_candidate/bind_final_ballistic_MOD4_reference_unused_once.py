from pathlib import Path
import json,hashlib,traceback
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent
S=L/'agent_MOD4_ballistic_horizontal_reference_v2/MOD4_OWN_BALLISTIC_HORIZONTAL_REFERENCE_V2_FINAL_NOT_ADMITTED.json'
BASE=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json'
O=D/'MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json'
R=L/'reports/FINAL87_BALLISTIC_REFERENCE_SOURCE_BINDING_ACTUAL.json'
assert not O.exists() and not R.exists()
try:
 raw=S.read_bytes();assert hashlib.sha256(raw).hexdigest()=='216838d62209881d78039cd71360355b20689aab09c7fa615813fa2a51e4c373'
 x=json.loads(raw);base=json.loads(BASE.read_bytes())
 x['schema']='mod4.own_step_converted_reference.v1'
 x['metadata'].update(control_dt_s=.01,foreign_transitions_for_world_model=False,
   own_step_edge_x_m=.35,own_platform_height_m=.27,physical_success_unchanged=True,
   joint_position_range_scale30=base['metadata']['joint_position_range_scale30'],
   actuator_leg_joint_names=['left_crank','left_hip','right_crank','right_hip'],
   actuator_wheel_joint_names=['left_wheel_spin','right_wheel_spin'],
   endpoint_policy='hold_pose_zero_velocities',SDK_joint_order_verified=False,
   reference_is_a_goal_not_an_applied_action=True,
   geometric_source_table_SHA=hashlib.sha256(raw).hexdigest(),
   reference_teacher_source=base['metadata']['source'],
   actual_own_step_success=False)
 O.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':')),'utf8')
 result={'passed':True,'source':{'path':str(S),'bytes':len(raw),'SHA':hashlib.sha256(raw).hexdigest()},
  'derived':{'path':str(O),'bytes':O.stat().st_size,'SHA':hashlib.sha256(O.read_bytes()).hexdigest()},
  'numeric_reference_values_changed_by_binding':False,
  'source_transformation':'Original measured foreign jump -> own30joint static retarget -> own contact recovery IK -> physically timed horizontal goal, no foreign action or foreign WM transition',
  'full_flight_horizontal_acceleration':0,'actual_dynamics_not_proven':True,
  'original_reference_V1_control_only_check':'failed at quarter-step; all failures preserved'}
except BaseException:
 result={'passed':False,'error':traceback.format_exc(),'partially_written_retained':True};R.write_text(json.dumps(result,indent=2),'utf8');raise
R.write_text(json.dumps(result,indent=2),'utf8');print(json.dumps(result))

