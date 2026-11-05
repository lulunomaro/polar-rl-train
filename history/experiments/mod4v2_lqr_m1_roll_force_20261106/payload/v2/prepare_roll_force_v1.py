"""Create one explicitly frozen v2 force-couple candidate; no model/physics.
No source gain, baseline runner, asset, actuation or gate is modified.
"""
from pathlib import Path
import json,ast
R=Path(__file__).resolve().parent;D=R/'T01_ROLL_FORCE_V1';D.mkdir(exist_ok=False)
s=(R/'runtime_v2.py').read_text(encoding='utf-8')
a='from controller_heading_v2 import GroundController';b='from controller_roll_force_v1 import GroundController'
assert s.count(a)==1;s=s.replace(a,b)
a="   # No assignment of old pack.K_6x14: constructor re-solves DARE on fresh v2 Ad/Bd."
assert s.count(a)==1;s=s.replace(a,"   self.meta['roll_force_design']=self.controller.roll_force_design.copy()\n"+a)
with (R/'runtime_roll_force_v1.py').open('x',encoding='utf-8')as f:f.write(s)
p=json.loads((R/'T01_V2/T01_PROTOCOL_V1.json').read_text(encoding='utf-8'))
p.update(id='MOD4V2_HW300N60_T01_ROLL_FORCE_001',controller='coord_soft_MOD4v2_VMC_roll_force_v1',
 formal_cases=[dict(id='nominal_slow',seed=520121,nominal=True,profile='slow')])
p['mechanism']=dict(name='IMU roll PD mapped through actual public leg Jacobians into vertical force couple',
 source='SPR chassis_task.c:919,972-973 structure only; no foreign gains/lengths/gas force formula',
 nominal_mass_kg=14.294140288606286,design_height='abs(public_nominal_wheel_z_in_body)',
 design_Kp='2*m*g*h',design_Kd='2*.7*(m*h*h)*sqrt(g/h)',
 point_mass_approximation_not_identified_COM_or_inertia=True,moment_filter_s=.03,
 force_couple_cap='.2*m*g N per side, equal/opposite',extra_joint_torque_cap_Nm=6.,
 ground_T01_only=True,contact_truth_inputs=False,original_gates_unchanged=True,
 original_K_trim_shaper_heading_PD_D4_DC_robot_collision_unchanged=True,
 hypothesis_not_proven_cause='Existing roll gains are zero; add bounded independent roll force stabilization, not an assertion that contact jitter was caused by missing feedback')
with (D/'T01_PROTOCOL_V1.json').open('x',encoding='utf-8')as f:json.dump(p,f,indent=2)
s=(R/'T01_V2/run_t01_v2.py').read_text(encoding='utf-8')
a='import runtime_v2 as runtime';assert s.count(a)==1;s=s.replace(a,'import runtime_roll_force_v1 as runtime')
a='                estimated_roll=None if engine.estimate is None else float(engine.estimate.roll),'
assert s.count(a)==1;s=s.replace(a,a+"\n                estimated_omega_body=None if engine.estimate is None else engine.estimate.omega_body,\n                estimated_proper_acc_origin=None if engine.estimate is None else engine.estimate.proper_acc_origin,\n                sensor_packet_100Hz=None if engine.packet is None else vars(engine.packet),\n                controller_diagnostic=engine.controller.control_diagnostic,\n                roll_force_diagnostic=engine.controller.roll_force_diag,")
with (D/'run_t01_roll_force.py').open('x',encoding='utf-8')as f:f.write(s)
for path in [R/'controller_roll_force_v1.py',R/'runtime_roll_force_v1.py',D/'run_t01_roll_force.py']:
 ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
print('ONE_ROLL_FORCE_CANDIDATE_PREPARED gates_unchanged=True physics=0 no_old_QA=True',flush=True)
