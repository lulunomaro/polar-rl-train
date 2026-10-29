"""Synthetic analytical source audit after NEW108; no saved model/raw/physics."""
from pathlib import Path
import hashlib,importlib.util,json,sys,time,traceback
import torch
S=Path(__file__).resolve().parent;T=S.parent
src=T/'MOD4_H1_FUDAN270_EPISODE20_PRODUCER_FIX_RESOURCE_V107_20261029/payloads_v2/seed27/source'
out=S/'reports/NEW108_REWARD_BLEND_GATE_AND_LEG_TARGET_SOURCE_CPU_ACTUAL.json'
assert not out.exists()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
try:
    spec=importlib.util.spec_from_file_location('reward108_source_audit',src/'mod4_fudan_contact_phase_reward_candidate_v2.py')
    mod=importlib.util.module_from_spec(spec);sys.modules[spec.name]=mod;spec.loader.exec_module(mod)
    ref=src/'OWN_FUDAN_STEP_TERMINAL_GOAL_CANDIDATE_V2.json'
    pars=json.loads(ref.read_bytes())['metadata']['bound_own_step_reward'];p=mod.BoundOwnStepReward(**pars)
    rows=[]
    for root_x in (.056,.20,.30):
        for vx_value in (0.,.25,.5):
            for vz_value in (0.,.15):
                vx=torch.tensor([vx_value],requires_grad=True);vz=torch.tensor([vz_value],requires_grad=True)
                L=torch.tensor([[.346,.346]],requires_grad=True)
                low=torch.tensor([[[root_x-.08,-.1,0.],[root_x-.08,.1,0.]]])
                high=torch.tensor([[[root_x+.08,-.1,.16],[root_x+.08,.1,.16]]])
                modes=mod.contact_and_step_modes(low,high,torch.full((1,2),100.),torch.tensor([root_x]),vz,p)
                z=torch.zeros(1);z2=torch.zeros(1,2);z3=torch.zeros(1,3);z6=torch.zeros(1,6)
                m=dict(flight=modes['flight'],takeoff=modes['takeoff'],virtual_leg_length=L,virtual_leg_angle=z2,
                    world_vertical_velocity=vz,body_vertical_velocity=vz,body_forward_velocity=vx,body_yaw_velocity=z,
                    command_forward_velocity=modes['command_forward_velocity'],command_yaw_velocity=z,
                    root_height=torch.full((1,),p.standing_body_height_m),relative_base_height=torch.full((1,),p.standing_body_height_m),
                    action=z6,previous_action=z6,actuated_torque=z6,projected_gravity=torch.tensor([[0.,0.,-1.]]),
                    body_angular_velocity=z3,actuated_leg_dq=torch.zeros(1,4),actuated_soft_limit_violation=z,
                    root_planar_velocity=torch.stack((vx,z),-1))
                r=mod.combined_reward(m,p,modes)
                dvx,dvz,dL=torch.autograd.grad(r['total'].sum(),(vx,vz,L))
                assert all(torch.isfinite(x).all() for x in (dvx,dvz,dL))
                rows.append(dict(synthetic_root_x_m=root_x,synthetic_forward_velocity=vx_value,synthetic_vertical_velocity=vz_value,
                    synthetic_leg_length_m=.346,jump_weight=float(modes['jump'].item()),recovery_weight=float(modes['recovery'].item()),
                    takeoff_gate=float(modes['takeoff'].item()),reward_per_control=float(r['total'].item()),
                    derivative_wrt_forward_velocity=float(dvx.item()),derivative_wrt_vertical_velocity=float(dvz.item()),
                    derivative_wrt_each_leg_length=dL.tolist()[0],
                    weighted_takeoff_extension_per_control=float(r['jump_terms']['takeoff_extend'].item())))
    derived=json.loads((S/'reports/NEW108_DERIVED_CONTROL_CURVES_FOR_PLOT_ONLY.json').read_bytes())['rows']
    geometry=dict(observed_new108_virtual_leg_length_min2=[min(x['virtual_leg_length2'][i] for x in derived) for i in range(2)],
                  observed_new108_virtual_leg_length_max2=[max(x['virtual_leg_length2'][i] for x in derived) for i in range(2)],
                  selected_control_legs={str(k):derived[k-1]['virtual_leg_length2'] for k in (200,400,1000,1900)})
    report=dict(passed_source_formulas_finite=True,epoch=time.time(),purpose='Analytical source-only gate and velocity/leg derivatives after actual108; no intervention or physics feasibility proof',
        source_SHA=sha(src/'mod4_fudan_contact_phase_reward_candidate_v2.py'),reference_SHA=sha(ref),parameters=pars,synthetic_rows=rows,
        actual_geometry_from_already_derived_text_only=geometry,
        findings=[
            'Grounded zero-vz takeoff gate approximately0.0474259 suppresses extension term until upward velocity is already present; this is a design candidate, not a disconnected gradient or unique cause.',
            'Source extension target0.31m is shorter than late standing observed virtual legs about0.346m in this case. At synthetic0.346m the extension-term preference is toward shorter legs. It might act as compression and does not prove mechanical impossibility or a wrong target by itself.',
            'Per-component clipping causes a flat region in the main recovery velocity-tracking component near command, while enhanced tracking still supplies a gradient. Total reward derivative is not universally zero.',
            'Near-edge smooth blend changes with root position/contact. These synthetic supported states are not measured reachable trajectories and zero torques/action are algebraic controls only.',
            'No new candidate reward, source deployment, learningGO, optimizer/norm update or policy/WM forward was executed by this audit.'],
        saved_model_reads=0,new_raw_decodes=0,remote_calls=0,source_or_physics_modified=False)
except BaseException:
    report=dict(passed_source_formulas_finite=False,error=traceback.format_exc(),epoch=time.time())
    with out.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    raise
with out.open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
print(json.dumps(dict(passed=True,rows=len(rows),ground_zero_vz_takeoff_gate=rows[0]['takeoff_gate'],leg_derivative_at_far_standing=rows[0]['derivative_wrt_each_leg_length'],observed_geometry=geometry)))

