"""Actual newbackend zero-PPO readback, original tolerances and full inputs."""
from pathlib import Path
import os, time, json
import numpy as np
import torch
from temporary_state_binding import H, same, DONOR_SHA, GEOMETRY_SHA, PARTITION_SHA, ASSIGNMENT_SHA

def cpu(v):
    return v.detach().cpu().clone() if torch.is_tensor(v) else v.torch.detach().cpu().clone() if hasattr(v, 'torch') else v

def save_raw(O, name, value):
    p = O / name
    assert not p.exists()
    torch.save(value, p)
    with p.open('r+b') as f:
        f.flush()
        os.fsync(f.fileno())
    return dict(path=str(p), bytes=p.stat().st_size, sha256=H(p))

def birth_inputs(env, O, write, source, placement):
    from wave50_entry_current_state_v2 import current_state, identity
    from nominal_parameter_audit import parameter_audit
    from wave50_route_runtime import state_dict as route_state
    from wave50_lifetime_runtime import state_dict as lifetime_state
    import mod4_task as task
    r = env.scene['robot']
    state = current_state(env)
    term = env.command_manager.get_term('twist')
    term._write_dynamic(torch.arange(env.num_envs, device=env.device))
    assert state['geometry_triangles_sha256'] == GEOMETRY_SHA and state['ordered_partition_triangles_sha256'] == PARTITION_SHA and (state['triangles'] == 10306304) and (state['entry_assignment_sha256'] == ASSIGNMENT_SHA)
    assert float(state['G4_height_peak_to_trough_m']) == 0.05
    q = cpu(r.data.joint_pos)
    root = cpu(r.data.root_state_w)
    spawn = cpu(env._rough_spawn_xy)
    assert torch.equal(q, cpu(env._rough_probe_expected_q)) and torch.equal(root[:, :2], spawn) and torch.equal(root[:, 7:], torch.zeros_like(root[:, 7:]))
    if env.num_envs == 20000:
        for field in ('entry_map_sha256', 'entry_origin_sha256', 'entry_assignment_sha256', 'entry_math_sha256', 'entry_runtime_sha256'):
            assert state[field] == source['E1_terrain_state'][field], field
        assert same(state['spawn_xy'], source['E1_terrain_state']['spawn_xy']) and same(state['reset_expected_q'], source['E1_terrain_state']['reset_expected_q'])
    assert env._mild_dr.profile == 'white_v3' and env._sensor_mild.receipt()['profile'] == 'noise_bias_mild_v1'
    assert env.cfg.scene.replicate_physics and env.cfg.scene.filter_collisions and ('cuda' in str(env.device))
    paths = list(env.scene.env_prim_paths)
    assert len(paths) == env.num_envs and len(set(paths)) == env.num_envs
    assert int(r.root_view.count) == env.num_envs
    write('CAPACITY_COLLISION_FILTER_REQUEST_ACTUAL.json', dict(epoch=time.time(), pid=os.getpid(), num_envs=env.num_envs, unique_env_prim_paths=paths, replicate_physics=True, GPU_enable_env_ids_request=True, articulation_view_count=int(r.root_view.count), duplicate_parent_worldXY_disclosed=True, not_independent_interaction_causal_ablation=True))
    parameters = parameter_audit(env)
    raw = save_raw(O, 'BIRTH_PHYSICAL_INPUTS_ACTUAL.pt', dict(root_state=root, root_quaternion_convention='xyzw', joint_pos=q, joint_names=list(r.joint_names), spawn_xy=spawn, actual_scene_origins=cpu(env.scene.env_origins), parameters=parameters, entry=env._wave50_entry_map_receipt, terrain=state, direction=term.state_dict_direction(), route=route_state(env, refresh=True), lifetime=lifetime_state(env, refresh=True), actual_assignments=env.scene.terrain.retention_assignment))
    from pxr import Usd, UsdPhysics, PhysxSchema
    solvers = []
    loops = 0
    for i in range(env.num_envs):
        for prim in Usd.PrimRange(env.sim.stage.GetPrimAtPath('/World/envs/env_' + str(i) + '/Robot')):
            if prim.HasAPI(PhysxSchema.PhysxArticulationAPI):
                api = PhysxSchema.PhysxArticulationAPI(prim)
                solvers.append((api.GetSolverPositionIterationCountAttr().Get(), api.GetSolverVelocityIterationCountAttr().Get()))
            if prim.IsA(UsdPhysics.Joint):
                j = UsdPhysics.Joint(prim)
                if j.GetExcludeFromArticulationAttr().Get() and j.GetJointEnabledAttr().Get():
                    loops += 1
    assert len(solvers) == env.num_envs and all((x == (32, 4) for x in solvers)) and (loops == 6 * env.num_envs)
    assert env.cfg.sim.physx.solver_type == 1 and env.cfg.terminations.closure.params['threshold'] == 0.002
    if placement:
        assert placement['actual_G4_cell_count'] == 10 and placement['two_front_support_sides'] and placement['complete_footprint_all_flat_hits'] and (placement['actual_footprint_max_height_range_m'] <= 1e-06)
    receipt = dict(epoch=time.time(), pid=os.getpid(), passed=True, num_envs=env.num_envs, actual_zero_control_birth_before_probe=True, geometry_identity=identity(state), full_inputs=raw, all_actual_root_xy_30q_and_zero_velocity_exact=True, actual_selected_origin_entry_assignment_exact=env.num_envs == 20000, actual_solver32_4_all_articulations=len(solvers), actual_enabled_closed_loops=loops, TGS_solver_type=env.cfg.sim.physx.solver_type, original_closure_threshold_m=0.002, placement=placement, DR_profiles={'D0': 'white_v3', 'D2': 'noise_bias_mild_v1'}, full_actor_optimizer_DR_RNG_restore_not_claimed_by_fresh_native=True)
    write('ZERO_CONTROL_BIRTH_CONTRACT_ACTUAL.json', receipt)
    return receipt

def end_contract(env, O, write, source, controls, ground_error, height_error, initial_birth):
    from nominal_parameter_audit import parameter_audit
    from wave50_route_runtime import audit as route_audit
    from wave50_lifetime_runtime import audit as lifetime_audit
    assert ground_error <= 1e-06 and height_error <= 1e-06
    sensor = env._sensor_mild.receipt()
    old = source['sensor_recipe']
    mutable = {'noise_draw_counts', 'max_abs_actual_bias_rad', 'bias_finite'}
    assert {k: v for k, v in sensor.items() if k not in mutable} == {k: v for k, v in old.items() if k not in mutable}
    assert sensor['bias_finite'] and sensor['max_abs_actual_bias_rad'] <= 0.0075
    recipes = {'sensor_recipe': sensor, 'feedback_delay_recipe': env.feedback_delay_recipe(), 'physical_action_delay_recipe': env.action_delay_recipe(), 'spring_pressure_recipe': env.spring_pressure_recipe(), 'gas_damping_recipe': env.gas_damping_recipe(), 'chassis_PD_recipe': env.chassis_pd_recipe()}
    for k, v in recipes.items():
        if k != 'sensor_recipe':
            assert v == source[k], k
    audits = dict(mild=env._mild_dr.audit(), sensor_manager=env.sensor_sdk_audit(), action=env._physics_action_delay.audit(), spring=env._spring_pressure.audit(), gas=env._gas_damping.audit(), chassis_PD=env.chassis_pd_audit(), command_retention=env.command_manager.get_term('twist').audit_retention(), episode_direction=env.command_manager.get_term('twist').audit_direction(), route=route_audit(env), lifetime=lifetime_audit(env))
    assert all((v == controls * 4 for v in env._physics_action_delay.calls.values())) and audits['action']['application_formula_max_error'] <= 1e-06
    assert env._physics_action_delay.queue.validate_state(env._physics_action_delay.state_dict())
    raw = save_raw(O, 'FINAL_PHYSICAL_READBACK_AND_D0D7_AUDITS_ACTUAL.pt', dict(parameters=parameter_audit(env), audits=audits, recipes=recipes, root=cpu(env.scene['robot'].data.root_state_w), q=cpu(env.scene['robot'].data.joint_pos)))
    env.write_retention_trace(O / 'probe_retention_trace')
    assert len(env._retention_trace) == controls
    receipt = dict(epoch=time.time(), pid=os.getpid(), passed=True, actual_controls=controls, actual_callbacks=controls * 4, actual_ground_query_error_m=ground_error, actual_height_reward_formula_error=height_error, original_tolerances_m=1e-06, all_static_D0D7_recipes_exact_to_complete_source=True, sensor_dynamic_bias_noise_counts_separate=True, full_final_physical_and_audit_inputs=raw, initial_birth_contract_ref=str(O / 'ZERO_CONTROL_BIRTH_CONTRACT_ACTUAL.json'), all_current_command_prefix_beforephysics_trace_saved=True, fullroute_or_fullresume_or_PPO_not_claimed=True)
    write('PROBE_D0D7_GEOMETRY_COMMAND_CONTRACT_ACTUAL.json', receipt)
    return receipt
