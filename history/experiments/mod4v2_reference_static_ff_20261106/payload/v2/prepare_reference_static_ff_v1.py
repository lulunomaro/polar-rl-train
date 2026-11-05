"""Derive exactly ONE M2 forward T01 case after reviewing independent design.
No existing source/old results changed; validate anchors/AST before fresh prefix.
"""
from pathlib import Path
import ast,json
R=Path(__file__).resolve().parent;D=R/'T01_REFERENCE_STATIC_FF_V1'
runner=(R/'T01_OBSERVABILITY_V1/run_reverse_observe.py').read_text(encoding='utf-8')
runtime=(R/'runtime_v2.py').read_text(encoding='utf-8')
protocol=json.loads((R/'T01_OBSERVABILITY_V1/PROTOCOL.json').read_text(encoding='utf-8'))
design=json.loads((R/'REFERENCE_STATIC_FF_DESIGN_V1/RESULT.json').read_text(encoding='utf-8'))
if design['counts']['target_configurations']!=2 or design['counts']['internal_SDKfree_FK']!=18 or design['q0_trim_consistency_max_Nm']>1e-10:
 raise RuntimeError('Expected completed new two-target public static formula result')
route=protocol['public_route'];route['start_ground_m'],route['goal_ground_m']=route['goal_ground_m'],route['start_ground_m']
if route['start_ground_m'][:2]!=[-9.,-1.]:raise RuntimeError('Expected original forward published start')
route['change']='Original public flat_run start -9,-1 before physics;forward profile as baseline,not prior reverse initialization'
protocol.update(id='MOD4V2_HW300N60_T01_REFERENCE_STATIC_FF_001',status='frozen_before_one_M2_nominal_case',
 controller='coord_soft_MOD4v2_reference_static_ff_v1',direction_sign=1.,
 formal_cases=[dict(id='nominal_static_ref_ff',seed=520141,nominal=True,profile='slow')],
 scope='M2 reference-only static gas/gravity correction,DIFFERENTIAL JOINT component;original common LQR/PD/K and actuator order/gates retained',
 hypothesis=dict(source='REFERENCE_STATIC_FF_DESIGN_V1/RESULT.json',
  finite_nominal_reference_bias=True,unique_contact_failure_cause_proven=False,
  two_target_difference_peak_Nm=max(abs(v)for v in design['delta_required_tau_Nm4']),
  fixed_design_F0_not_measured=True,gas_curve_not_calibrated=True,
  model_phase='zero rates/accelerations/proper(0,0,9.81) STATIC design,not sensor substitution',
  no_measured_or_proxy_force_alpha_or_DR_feedback=True,only_M2_one_case_no_automatic_DR=True))
protocol['slow_command']['forward_m_s']=.3
protocol['observer'].update(controller_candidate='M2_reference_static_ff_only',original_PD_D4_DC_order=True)

def replace(text,old,new):
 if text.count(old)!=1:raise RuntimeError('Nonunique expected anchor:'+repr(old[:100]))
 return text.replace(old,new,1)
runtime=replace(runtime,'from controller_heading_v2 import GroundController','from controller_reference_static_ff_v1 import GroundController')
runtime=replace(runtime,'   self.estimate=None;self.packet=None;self.last_tau=np.zeros(6);self.controls=0',
 '   self.meta.update(reference_static_ff_design=self.controller.reference_ff_design,reference_ff_is_not_measured_force=True)\n   self.estimate=None;self.packet=None;self.last_tau=np.zeros(6);self.controls=0')
runtime='# Derived M2 runtime ONLY; default runtime_v2.py remains unchanged.\n'+runtime
runner=replace(runner,'# ONE new reverse route diagnostic; old thresholds retained,progress projects along public reverse direction.',
 '# ONE M2 forward reference-static FF candidate; original threshold numbers unchanged.')
runner=replace(runner,'import runtime_v2 as runtime','import runtime_reference_static_ff_v1 as runtime')
runner=replace(runner,"meta['planned_reverse_route']", "meta['planned_profile_route']")
runner=replace(runner,"reverse_progress_projection=True", "reverse_progress_projection=False")
runner=replace(runner,"status='NEW_REVERSE_OBSERVABILITY_CASE_NOT_T01_GRADUATION_OR_MATCHED_FORWARD_COMPARISON'", "status='M2_REFERENCE_STATIC_FF_NOMINAL_CASE_NOT_WHOLE_T01_OR_RELIABILITY'")
runner=replace(runner,'                motor_window_summary=p.motor_telemetry_summary,',
 '                motor_window_summary=p.motor_telemetry_summary,\n                reference_static_ff_diagnostic=engine.controller.reference_ff_diag,')
runner=replace(runner,'            observer_data_returned_to_engine_or_controller_or_proxy=False)',
 '''            observer_data_returned_to_engine_or_controller_or_proxy=False,
            reference_static_ff_aggregate=engine.controller.reference_ff_aggregate,
            reference_static_ff_sdkfree_terms_calls=engine.controller.reference_ff.target_terms_calls,
            reference_static_ff_internal_sdkfree_FK_calls=engine.controller.reference_ff.internal_fk_calls,
            new_SDKfree_nominal_model_objects=1,static_assumption_not_measured_acceleration=True)''')
for code in (runner,runtime,(R/'controller_reference_static_ff_v1.py').read_text(encoding='utf-8')):ast.parse(code)
if D.exists()or (R/'runtime_reference_static_ff_v1.py').exists():raise RuntimeError('Fresh prefix/runtime already exists;do not regenerate')
D.mkdir();(R/'runtime_reference_static_ff_v1.py').write_text(runtime,encoding='utf-8')
(D/'run_reference_static_ff_v1.py').write_text(runner,encoding='utf-8')
(D/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2,ensure_ascii=False),encoding='utf-8')
(D/'PREPARATION.json').write_text(json.dumps(dict(new_case='v2_t01_reference_static_ff_nominal_slow_520141_001',
 old_default_runtime_controller_physics_gates_modified=False,physics_steps=0,simulation_model_builds=0,
 design_only_two_targets=True,no_automatic_second_case_or_DR=True,one_nominal_new_case_before_selection=True),indent=2),encoding='utf-8')
print('PREPARED_M2_REFERENCE_STATIC_FF physics0 simulation_model_builds0',flush=True)
