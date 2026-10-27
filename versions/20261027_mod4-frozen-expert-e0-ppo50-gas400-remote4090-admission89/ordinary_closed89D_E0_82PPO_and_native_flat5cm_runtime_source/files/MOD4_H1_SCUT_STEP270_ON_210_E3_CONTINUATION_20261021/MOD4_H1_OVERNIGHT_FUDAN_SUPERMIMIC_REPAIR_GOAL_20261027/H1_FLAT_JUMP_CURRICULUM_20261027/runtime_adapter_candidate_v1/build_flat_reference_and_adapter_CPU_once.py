"""One source-purpose derived-neutral export and analytic CPU check; no policy."""
from pathlib import Path
import hashlib, json, os, sys, time, traceback
HERE = Path(__file__).resolve().parent
COURSE = HERE.parent
L = COURSE.parent
T = L.parent
N = T/'MOD4_E0_PPO50_GAS400_REMOTE4090_RESOURCE_V89D_20261027'
S = T/'H1_NATIVE88C_GAS400_FROZEN_SINGLE_DIAGNOSTIC_SOURCE210_R3_20261027'
SOURCE = T/'H1_STEP270_OWN_STEP_GAS400_NATIVE_RESOURCE_V88C_20261027/payloads/h1/source'

def put(name, value):
    with (HERE/name).open('x', encoding='utf8') as f:
        json.dump(value, f, indent=2, allow_nan=False)

def H(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    put('FLAT_ADAPTER_SOURCE_CPU_STARTED_ACTUAL.json', dict(epoch=time.time(),
        purpose='Own flat task primitive from recorded neutral shape; analytic FK/phase gradients only',
        no_PT_actor_WM_forward_SDK_GPU_physics_remote_or_account=True,
        existing_derived_NPZ_only_new_reference_purpose=True))
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    import numpy as np
    import torch
    torch.set_num_threads(2)
    sys.path[:0] = [str(HERE), str(COURSE), str(SOURCE), str(SOURCE/'sm_deps')]
    from native_flat_jump_adapter_v1 import OwnFlatJumpReference, OwnFlatJumpMdp, encode_frame, decode_frame
    from supermimic_wheel_leg_v3.geometry import unflatten_state
    from native_wheel_leg_bridge_v4 import NativeWheelLegBridge
    from native_flat_jump_bridge_v1 import FlatWheelLegBridge
    admission = json.loads((S/'actual210/seed_20260928/ACTUAL_FRESH_N1_SDK_BEFORE_FORWARD_ADMISSION.json').read_bytes())
    old_doc = json.loads((SOURCE/'MOD4_OWN_CONVERTED_BALLISTIC_STEP_REFERENCE_FINAL87_NOT_ADMITTED.json').read_bytes())
    with np.load(S/'NEW88C_SINGLE_RECORDED_DERIVED_SMALL.npz', allow_pickle=False) as z:
        neutral = z['packed127'][0].tolist()
        xi = z['xi31'][0].tolist()
    doc = dict(schema='mod4.own_flat_jump_reference.v1', joint_names=admission['actual_order'],
        neutral_packed73=neutral[:73], metadata=dict(height_m=.05, control_dt_s=.01,
        initial_standing_s=2., deterministic_env_stagger_s=[0.,2.49], repeat_s=2.5,
        actuator_leg_joint_names=old_doc['metadata']['actuator_leg_joint_names'],
        joint_position_range_scale30=old_doc['metadata']['joint_position_range_scale30'],
        foreign_transitions_for_world_model=False, physical270_success_unchanged=True,
        source_is_measured_successful_Fudan_joint_motion=False,
        joint_trajectory_unmeasured_and_masked=True,
        neutral_source='already derived actual88C recorded first state, shape witness only',
        task_goal_not_forced_action_or_state=True,
        Fudan_video_scope='phase-order inspiration only, not a measured3D limb path',
        wheel_lowest_point_actual_acceptance_m=.05, actual_floor_stability_s=.5))
    put('OWN_FLAT5CM_TASK_REFERENCE_SOURCE.json', doc)
    put('NEUTRAL127_XI31_SOURCE_CPU_FIXTURE.json', dict(neutral127=neutral, xi31=xi,
         not_a_WM_transition_dataset=True, not_a_successful_demonstration=True))
    geometry = json.loads((SOURCE/'OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json').read_bytes())
    contract = json.loads((SOURCE.parent/'job0/assets/import_contract.json').read_bytes())
    provider = OwnFlatJumpReference(doc).bind_named_order(admission['actual_order'], scope='source_CPU_fixture')
    mdp = OwnFlatJumpMdp(provider, contract, geometry)
    state = unflatten_state(torch.tensor([neutral], dtype=torch.float32))
    context = torch.tensor([xi], dtype=torch.float32)
    zero = torch.zeros(1, 6)
    frames = encode_frame(torch.tensor([210]), torch.tensor([0]))
    age, delay = decode_frame(frames)
    assert age.tolist()==[210] and delay.tolist()==[0]
    assert provider.future_goal(frames, 10).shape==(1,1460)
    assert mdp.obs(state,zero,context,frames).shape==(1,86)
    critic = mdp.critic_features(state,frames,mdp.normalize_context(context))
    assert critic.shape[-1] == 165
    value,mask = provider.query(frames)
    assert mask[...,:13].eq(1).all() and mask[...,13:].eq(0).all()
    measured = mdp.wheel_geometry(state)
    # At the ballistic apex, raising BOTH wheels from the real neutral posture
    # has the correct local task gradient. No learned WM/actor is evaluated.
    base = state[0].detach().clone().requires_grad_(True)
    active = (base,*state[1:])
    terms = mdp.objective_terms(active,frames,zero,zero)
    gradient, = torch.autograd.grad(terms['total'].sum(), base)
    assert torch.isfinite(gradient).all() and gradient[0,2]>0
    raised = (state[0]+state[0].new_tensor([0.,0.,.05]),*state[1:])
    elevated = mdp.objective_terms(raised,frames,zero,zero)
    assert elevated['total'].item()>terms['total'].item()
    assert mdp.valid_imagination_start(encode_frame(torch.tensor([450]),torch.tensor([249])),32).all()
    assert not mdp.valid_imagination_start(encode_frame(torch.tensor([470]),torch.tensor([249])),32).any()
    assert provider.target(encode_frame(torch.tensor([210]),torch.tensor([249])))['active'].item() is False
    # Demonstrate that next-step aux is used, not frozen contact context.
    aux_air = state[6].clone();aux_air[...,:6]=0
    aux_ground = aux_air.clone();aux_ground[...,2]=100;aux_ground[...,5]=100
    flight_air = mdp.objective_terms((*state[:6],aux_air),frames,zero,zero)['support_cost']
    flight_ground = mdp.objective_terms((*state[:6],aux_ground),frames,zero,zero)['support_cost']
    assert flight_ground.item()>flight_air.item()
    # Exact parent step action forwarding remains inherited. A stub proves the
    # subclass changes only its private frame in the identical returned object.
    from types import SimpleNamespace
    from supermimic_wheel_leg_v3.contract import SUPERMIMIC_STATE_KEY
    original = NativeWheelLegBridge.step
    seen=[];actions=object();returned=SimpleNamespace(info={SUPERMIMIC_STATE_KEY:{'f':torch.tensor([12])}})
    try:
        NativeWheelLegBridge.step=lambda this,a: (seen.append(a),returned)[1]
        bridge=object.__new__(FlatWheelLegBridge);bridge.flat_env_ids=torch.tensor([249])
        got=bridge.step(actions)
        assert got is returned and seen==[actions]
        assert got.info[SUPERMIMIC_STATE_KEY]['f'].item()==249*1024+12
    finally: NativeWheelLegBridge.step=original
    assert not torch.cuda.is_initialized()
    put('FLAT5CM_NATIVE_ADAPTER_SOURCE_CPU_ACTUAL.json', dict(passed=True, source_only=True,
        neutral_lowest_wheel_m=measured['low'][...,2].tolist(),
        current_neutral_request_score=terms['total'].item(), raised5cm_score=elevated['total'].item(),
        gradient_reward_d_neutral_root_z=gradient[0,2].item(),
        goal_shape=[1,1460], actor_obs_shape=[1,86], critic_features_shape=list(critic.shape),
        source_mapping_scope=provider.order_scope, private_encoded_frame_phase_and_terminal_horizon=True,
        actual_public_phase_unchanged=True, actual_parent_action_identity_return_preserved=True,
        dynamic_aux54_is_WM_predicted_and_used_in_each_reward=True,
        legacy_missing_distance_or_frozen_dynamic_context_claim_not_applicable_to_current127=True,
        actual_plant_command0_source_integration_pending=True,
        physical_success=False, installed_SDK_or_native_GPU_updates=False,
        no_PT_actor_WM_forward_SDK_GPU_physics_remote_or_account=True,
        new_reference_SHA=H(HERE/'OWN_FLAT5CM_TASK_REFERENCE_SOURCE.json'),
        source_contract=mdp.contract_manifest()))
    print(json.dumps(dict(passed=True, source_only=True, neutral_wheel_bottom=measured['low'][...,2].tolist())))

if __name__=='__main__':
    try: main()
    except BaseException:
        put('FLAT_ADAPTER_SOURCE_CPU_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(traceback=traceback.format_exc()))
        raise
