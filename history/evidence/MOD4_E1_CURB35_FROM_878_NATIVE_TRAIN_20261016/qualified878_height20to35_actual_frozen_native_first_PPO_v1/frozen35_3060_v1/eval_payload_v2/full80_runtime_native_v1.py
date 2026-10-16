"""New native backend port, original80 placement/commands/termination/physical loop retained."""
from pathlib import Path
import json,time,hashlib,numpy as np,torch,warp as wp
import mod4_task as task
from curb35_geometry import configure_curb as configure_intro
from e1_reset_evidence_training_env import E1ResetEvidenceLearningEnv
from e1_terrain_training_health import declared_truncation_terms,ORDINARY_TERMS,INTEGRITY_TERMS,TRUNCATION_TERMS
from e1_full_pose_reset import query
from s5_single_frozen35_v1 import build_route_pair
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from factor_runtime_3060_reference17b_v1 import cpu,js,tensor,params,actual_substep_hardware_and_COM

def assignments(e):
    return dict(action={k: dict(delay_us=js(g['lag_steps'] * 2500), episode=js(g['episode'])) for k, g in e._physics_action_delay.queue.groups.items()}, spring=dict(factor=js(e._spring_pressure.component.factor), episode=js(e._spring_pressure.component.episode)), gas=dict(factor=js(e._gas_damping.component.factor), episode=js(e._gas_damping.component.episode)), COM=dict(delta_m=js(e._chassis_com.component.delta_m), episode=js(e._chassis_com.component.episode)), PD=dict(factors={k: js(v) for k, v in e._explicit_pd.component.factor.items()}, episode=js(e._explicit_pd.component.episode)), feedback_delay=js(e._feedback_delay_mild.lag_steps) if hasattr(e._feedback_delay_mild, 'lag_steps') else e.feedback_delay_recipe())

@torch.inference_mode()
def run_full80(args,O,L,save):
    assert args.steps in (120,1500) and args.num_envs == 80 and (args.seed == 20260928) and (args.dr_profile == 'white_v3')
    torch.manual_seed(args.seed)
    cfg = task.Mod4EnvCfg()
    cfg.seed = args.seed
    cfg.scene.num_envs = args.num_envs
    cfg.sim.device=args.device
    for k,v in dict(gpu_max_rigid_contact_count=2**20,gpu_max_rigid_patch_count=2**16,gpu_found_lost_pairs_capacity=2**18,gpu_found_lost_aggregate_pairs_capacity=2**22,gpu_total_aggregate_pairs_capacity=2**20).items():setattr(cfg.sim.physics,k,v)
    recipe = configure_intro(cfg)
    gen = cfg.scene.terrain.terrain_generator
    assert gen.curriculum and gen.num_rows == gen.num_cols == 40
    keys = list(gen.sub_terrains)
    weights = np.array([gen.sub_terrains[k].proportion for k in keys])
    weights /= weights.sum()
    family = np.array([int(np.min(np.where(i / 40 + 0.001 < np.cumsum(weights))[0])) for i in range(40)])
    cols = np.flatnonzero(family == keys.index('random_uniform_for_rm'))
    assert len(cols) == 6
    size = np.asarray(gen.size, dtype=float)
    assert np.array_equal(size, [9.0, 9.0])
    ids = np.arange(80)
    tile_rows = ids // 2
    tile_cols = cols[ids % 2]
    centers = np.stack(((tile_rows + 0.5) * size[0] - 20 * size[0], (tile_cols + 0.5) * size[1] - 20 * size[1]), axis=-1)
    support = 0.4
    def whole_route_boundary(env):
        xy = env.scene['robot'].data.root_pos_w[:, :2] - env._g1_whole_route_centers
        return (xy[:, 0].abs() > 3.5) | (xy[:, 1].abs() > 3.0)
    cfg.terminations.rough_route_boundary.func = whole_route_boundary
    assert cfg.terminations.rough_route_boundary.time_out is True
    e = E1ResetEvidenceLearningEnv(cfg=cfg)
    r = e.scene['robot']
    e._g1_whole_route_centers = torch.as_tensor(centers, device=e.device, dtype=e.scene.env_origins.dtype)
    ray = query(e)
    xy = np.repeat(centers[:,None,:],2,axis=1)
    xy[:,0,0]-=1.;xy[:,1,0]+=1.
    ceiling=float(ray.geometry.vertices[:,2].max())+2.
    preliminary=ray.cast(torch.as_tensor(np.concatenate((xy,np.full((80,2,1),ceiling)),axis=-1),device=e.device,dtype=torch.float32),10.)
    preliminary_height=cpu(preliminary['height'])
    assert preliminary['hit'].all() and (preliminary['normal'][...,2]>.99).all()
    orientation=np.where(preliminary_height[:,1]>preliminary_height[:,0],1.,-1.)
    assert np.sum(orientation==1)==40 and np.sum(orientation==-1)==40
    assert np.max(abs(np.ptp(preliminary_height,axis=1)-.035))<=1e-6
    assert np.max(abs(np.min(preliminary_height,axis=1)))<=1e-6
    starts=centers.copy()
    starts[:,0]+=orientation*np.where(ids%3==1,.075+support,-.075-support)
    assert len(np.unique(np.stack((tile_rows,tile_cols),axis=-1),axis=0))==80
    e.scene.env_origins[:,:2]=torch.as_tensor(starts,device=e.device,dtype=e.scene.env_origins.dtype)
    e.reset()
    root_xy=tensor(r.data.root_pos_w)[:,:2]
    assert isinstance(root_xy,torch.Tensor) and root_xy.dtype==torch.float32
    assert torch.allclose(root_xy,torch.as_tensor(starts,device=e.device,dtype=root_xy.dtype),atol=1e-6,rtol=0)
    samples=np.linspace(-.475,.475,35)
    xy=np.repeat(centers[:,None,:],35,axis=1)
    xy[:,:,0]+=orientation[:,None]*samples
    sample=ray.cast(torch.as_tensor(np.concatenate((xy,np.full((80,35,1),ceiling)),axis=-1),device=e.device,dtype=root_xy.dtype),10.)
    assert sample['hit'].all() and (sample['normal'][...,2]>.99).all()
    sampled=cpu(sample['height']);expected=np.where(samples<-.075,0.,.035)
    assert np.max(abs(sampled-expected[None,:]))<=1e-6
    wheel_ids=[r.body_names.index(n) for n in ('left_wheel','right_wheel')]
    initial_wheel=cpu(r.data.body_link_pos_w)[:,wheel_ids,:]
    initial_u=(initial_wheel[:,:,0]-centers[:,None,0])*orientation[:,None]
    assert (initial_u[ids%3!=1]<-.075).all() and (initial_u[ids%3==1]>.075).all()
    route_scope=dict(tile_rows=tile_rows.tolist(),tile_cols=tile_cols.tolist(),family='derived35mm_vertical_curb_strip150',tile_centers=centers.tolist(),requested_starts=starts.tolist(),size_m=size.tolist(),flat_support_margin_m=support,orientation=orientation.tolist(),riser_canonical_x_m=-.075,strip_end_canonical_x_m=.075,height_m=.035,strip_width_m=.150,required_after_support_m=.200,actual_sampled_canonical_x_m=samples.tolist(),actual_sampled_ground=sampled.tolist(),actual_sampled_normals=js(sample['normal']),actual_authored_ground_query_passed=True,initial_wheel_link_positions=initial_wheel.tolist(),initial_two_wheels_on_requested_side=True,vertical_riser_unsmoothed=True,not_actual_RM002_height=True,not_stair_flight=True,termination_change='evaluation-only declared truncation at abs x from tile center3.5m or abs y3m',production_boundary_unchanged=True,not_training_or_RM70mm=True)
    actual_world_ray_origins=cpu(torch.as_tensor(np.concatenate((xy,np.full((80,35,1),ceiling)),axis=-1),device=e.device,dtype=root_xy.dtype))
    from curb_worldmesh_query_contract_v1 import expected_ground
    expected_actual_ground,world_mesh_receipts,query_world_triangles=expected_ground(ray.geometry.vertices,ray.geometry.faces,centers,actual_world_ray_origins)
    actual_query_height_error=float(np.max(abs(sampled-expected_actual_ground)))
    assert actual_query_height_error<=1e-6
    query_evidence_path=Path(args.output).with_name(Path(args.output).name+'.worldmesh_query.npz')
    assert not query_evidence_path.exists()
    np.savez_compressed(query_evidence_path,actual_world_ray_origins=actual_world_ray_origins,actual_canonical_ray_x=(actual_world_ray_origins[:,:,0].astype(np.float64)-centers[:,None,0])*orientation[:,None],actual_sampled_ground=sampled,expected_actual_ground=expected_actual_ground,ideal_profile_ground=np.broadcast_to(expected[None,:],sampled.shape),world_triangles=query_world_triangles)
    assert all((r['mirrored']==bool(o<0)) for r,o in zip(world_mesh_receipts,orientation))
    route_scope.update(actual_world_ray_origins=actual_world_ray_origins.tolist(),actual_query_height_error_m=actual_query_height_error,actual_query_ground_tolerance_m=1e-6,expected_actual_sampled_ground=expected_actual_ground.tolist(),world_mesh_receipts=world_mesh_receipts,query_worldmesh_evidence=dict(path=str(query_evidence_path),bytes=query_evidence_path.stat().st_size,sha256=hashlib.sha256(query_evidence_path.read_bytes()).hexdigest()))
    assert e.physics_dt == 0.0025 and e.step_dt == 0.01 and (r.data.joint_pos.shape == (80, 30))
    assert torch.equal(tensor(r.data.joint_pos), e._rough_probe_expected_q)
    initial = dict(root=js(r.data.root_state_w), q=js(r.data.joint_pos), parameters=e.chassis_pd_audit(), assignments=assignments(e), reset=e._rough_probe_reset_receipt, actual_all_physical_parameters=params(e))
    decl = declared_truncation_terms(e.termination_manager)
    names = tuple(e.termination_manager.active_terms)
    cmd = e.command_manager.get_term('twist')
    cmd.set_manual_evaluation_mode()
    groups = torch.arange(80, device=e.device) % 3
    targets = torch.tensor([0.3, -0.3, 0.0], device=e.device)[groups] * torch.as_tensor(orientation,device=e.device,dtype=torch.float32)
    vec, policy, observer = build_route_pair(RslRlVecEnvWrapper(e, clip_actions=6.0), args.checkpoint, e.device,O,save)
    source=torch.load(args.checkpoint,map_location='cpu',weights_only=False)
    assert source['E1_terrain_state']['num_envs']==20000
    assert source['E1_terrain_state']['CURB_height_m']==.020 and source['E1_terrain_state']['CURB_strip_width_m']==.150
    assert source['E1_terrain_state']['geometry_triangles_sha256']!=ray.geometry.receipt()['triangles_sha256']
    save('CURB20_SOURCE_TO_35_NEW_GEOMETRY_ACTUAL.json',dict(source_height_m=.020,actual_new_height_m=.035,source_only_actor_loaded=True,new_geometry_not_claimed_saved_source_same_scope=True,source_mesh_SHA=source['E1_terrain_state']['geometry_triangles_sha256'],actual_mesh=ray.geometry.receipt(),actual_partition=e.scene.terrain.exact_partition_receipt))
    pair_source=json.loads((O/'S5_SINGLE_POLICY_SOURCE_ACTUAL.json').read_bytes())
    assert pair_source['all9_actor_std_GPU_source_exact'] and pair_source['optimizer_updates']==0
    save('INITIAL_ACTUAL.json',initial)
    save('FROZEN_POLICY_SOURCE_ACTUAL.json',dict(source_SHA=observer.checkpoint_sha256,source_saved_envs=20000,fixture_envs=80,actual_anchor_actor_nine_GPU_tensors_source_exact=True,all9_single_actor_std_exact=True,only_actor_loaded=True,no_gate_or_second_expert_forward=True,no_training_DR_projection=True,no_PPO=True))
    initial_pre_wrapper=initial
    initial=dict(root=js(r.data.root_state_w),q=js(r.data.joint_pos),parameters=e.chassis_pd_audit(),assignments=assignments(e),reset=e._rough_probe_reset_receipt,actual_all_physical_parameters=params(e))
    save('FIRST_PHYSICS_INITIAL_ACTUAL.json',dict(phase='after RSL wrapper reset and policy construction, before first physical control',values=initial,legacy_pre_wrapper_values=initial_pre_wrapper,readonly_no_setters_or_RNG=True))
    cap = e._integrated_contact
    start_tick = cap.tick
    calls0 = dict(e._physics_action_delay.calls)
    rows = {k: [] for k in ('before_root', 'root', 'q', 'command', 'action', 'ground', 'normal', 'closure', 'mimic', 'episode', 'terminated', 'truncated', 'reasons', 'impulse', 'history', 'wheel_force', 'COM_link_pos', 'COM_link_vel', 'applied_torque', 'joint_vel', 'policy_obs', 'processed_action', 'guarded_leg_targets')}
    rawforces = []
    hardware_rows=[]
    episode = np.zeros(80, dtype=np.int64)
    capture = cap.capture
    integral_error = 0.0

    def measured_capture(dt):
        capture(dt)
        raw = cap.sensor.contact_view.get_net_contact_forces(dt=cap.dt).view(wp.vec3)
        rawforces.append(cpu(wp.to_torch(raw).reshape(80, 2, 3)))
        hardware_rows.append(actual_substep_hardware_and_COM(e))
    cap.capture = measured_capture
    original = e.termination_manager.compute
    phase = {}
    e._s4_before_reset_route_phase=phase

    def before_reset(*a, **k):
        result = original(*a, **k)
        tm = e.termination_manager
        phase.update(terminated=cpu(tm.terminated), truncated=cpu(tm.time_outs), reasons=np.stack([cpu(tm.get_term(n)) for n in names], axis=-1), impulse=cpu(cap.impulse), history=cpu(cap.history), wheel_force=cpu(e.scene.sensors['wheel_contact'].data.net_forces_w), COM_link_pos=cpu(r.data.body_link_pos_w), COM_link_vel=cpu(r.data.body_link_vel_w), applied_torque=cpu(r.data.applied_torque), joint_vel=cpu(r.data.joint_vel), processed_action=cpu(e.action_manager.action), guarded_leg_targets=cpu(e.action_manager.get_term('legs').processed_actions))
        return result
    e.termination_manager.compute = before_reset
    coverage = True
    ground_error = 0.0
    height_error = 0.0
    start = time.time()
    for step in range(args.steps):
        cmd.time_left[:] = 1000000000.0
        cmd.is_standing_env[:] = groups == 2
        if hasattr(cmd, 'is_heading_env'):
            cmd.is_heading_env[:] = False
        cmd.is_pure_spin[:] = False
        cmd.is_moving_spin[:] = False
        cmd.is_transition_spin[:] = False
        cmd.command[:] = 0.0
        cmd.command[:, 0] = targets
        task.height_cmd(e)[:] = 0.25
        before = cpu(r.data.root_state_w)
        requested = cpu(cmd.command)
        obs=vec.get_observations()
        action = policy(obs)
        _, reward, done, _ = vec.step(action)
        frame = e._e1_pre_reset_frame
        ordinary = phase['reasons'][:, [names.index(n) for n in names if n in ORDINARY_TERMS]].any(-1)
        integrity = phase['reasons'][:, [names.index(n) for n in names if n in INTEGRITY_TERMS]].any(-1)
        unknown = phase['reasons'][:, [names.index(n) for n in names if n not in ORDINARY_TERMS | INTEGRITY_TERMS | TRUNCATION_TERMS]].any(-1) if any((n not in ORDINARY_TERMS | INTEGRITY_TERMS | TRUNCATION_TERMS for n in names)) else np.zeros(80, dtype=bool)
        trunc = phase['reasons'][:, [names.index(n) for n in TRUNCATION_TERMS]].any(-1)
        coverage = coverage and np.array_equal(phase['terminated'], ordinary | integrity | unknown) and np.array_equal(phase['truncated'], trunc)
        assert coverage and (not integrity.any()) and (not unknown.any()), 'Actual terrain reason coverage/integrity'
        assert e._rough_reward_query_tick == e._rough_termination_query_tick == int(e._sim_step_counter)
        ground_error = max(ground_error, frame['independent_ground_error'])
        height_error = max(height_error, e._e1_height_formula_error)
        assert ground_error <= 1e-06 and height_error <= 1e-06
        values = dict(before_root=before, root=cpu(frame['root']), q=cpu(frame['q']), command=requested, action=cpu(action), ground=cpu(frame['ground']), normal=cpu(frame['normal']), closure=cpu(frame['closure']), mimic=cpu(frame['mimic']), episode=episode.copy(), policy_obs=cpu(obs['policy']), **phase)
        assert all((np.isfinite(x).all() for x in values.values())) and bool(torch.isfinite(reward).all())
        assert np.max(values['mimic']) <= 0.01
        assert len(rawforces) == (step + 1) * 4
        independent = np.maximum(np.stack(rawforces[-4:])[..., 2], 0).sum(0) * 0.0025
        integral_error = max(integral_error, float(np.max(abs(independent - phase['impulse']))) / 0.01)
        assert integral_error <= 0.1, 'Original mean-load 0.1N data contract'
        for k, v in values.items():
            rows[k].append(v)
        episode += phase['terminated'] | phase['truncated']
    data = {k: np.stack(v) for k, v in rows.items()}
    data['physical_wheel_force_N'] = np.stack(rawforces)
    data['group_ids'] = cpu(groups)
    data['targets_m_s'] = cpu(targets)
    assert len(hardware_rows)==args.steps*4
    for k in hardware_rows[0]['arrays']:data['physical_hardware_'+k]=np.stack([r['arrays'][k] for r in hardware_rows])
    data['physical_mass_weighted_COM_world']=np.stack([r['mass_weighted_COM_world'] for r in hardware_rows])
    save('SUBSTEP_HARDWARE_COM_ACTUAL.json',dict(callbacks=len(hardware_rows),motor_torque_speed_bounds_exact=True,COM_frame_max_error_m=max(r['COM_frame_error_m'] for r in hardware_rows),original_COM_formula_tolerance_m=1e-5,no_parameter_setters=True,hardware_calibrated=False))
    output = Path(args.output)
    npz = output.with_name('route_raw.npz')
    np.savez_compressed(npz, **data)
    summaries = []
    q = data['before_root'][:, :, 3:7]
    heading = np.arctan2(2 * (q[:, :, 3] * q[:, :, 2] + q[:, :, 0] * q[:, :, 1]), 1 - 2 * (q[:, :, 1] ** 2 + q[:, :, 2] ** 2))
    delta = data['root'][:, :, :2] - data['before_root'][:, :, :2]
    along = delta[:, :, 0] * np.cos(heading) + delta[:, :, 1] * np.sin(heading)
    cross = -delta[:, :, 0] * np.sin(heading) + delta[:, :, 1] * np.cos(heading)
    route_i = names.index('rough_route_boundary')
    failstep = np.where(data['terminated'], np.arange(args.steps)[:, None], args.steps).min(0)
    for i, label in enumerate(('forward', 'reverse', 'stand')):
        ids = data['group_ids'] == i
        valid = np.arange(args.steps)[:, None] < failstep[None, :]
        mask = valid[:, ids]
        speed = along[:, ids] / 0.01
        target = data['targets_m_s'][ids][None,:]
        per = np.where(mask, speed, 0).sum(0) / mask.sum(0).clip(1)
        summaries.append(dict(group=label, command_vx_m_s=target[0].tolist(), env_ids=np.flatnonzero(ids).tolist(), valid_prefix_control_per_env=mask.sum(0).tolist(), first_non_timeout_failure_control=failstep[ids].tolist(), mean_valid_prefix_along_m_s=float(per.mean()), per_env_valid_prefix_along_m_s=per.tolist(), valid_prefix_abs_tracking_error_m_s=float(np.abs(speed - target)[mask].mean()) if mask.any() else None, total_signed_along_m=float(along[:, ids].sum()), total_abs_cross_m=float(abs(cross[:, ids]).sum()), route_boundary_truncations=int(data['reasons'][:, ids, route_i].sum()), ordinary_termination_events=int(data['terminated'][:, ids].sum()), observed_wheel_ground_range_m=[float(data['ground'][:, ids].min()), float(data['ground'][:, ids].max())]))
    audit = e._physics_action_delay.audit()
    actualcallbacks = cap.tick - start_tick
    assert actualcallbacks == args.steps*4 and all((v - calls0[k] == args.steps*4 for k, v in e._physics_action_delay.calls.items())) and (audit['application_formula_max_error'] == 0)
    sensor = e.sensor_sdk_audit()
    assert sensor['actor35'] and sensor['critic38_clean'] and (sensor['formula_max_error'] <= 2e-06)
    pd = e.chassis_pd_audit()
    assert pd['parameter_auditor']['actual_parameters_pass']
    result = dict(protocol='new_CURB35_frozen_source878_original_mirrored_approach040_worldmesh_v1', not_user_paused93_94=True, new_learning=False, optimizer_updates=0, checkpoint_sha256=observer.checkpoint_sha256, seed=args.seed, profile=args.dr_profile, steps=args.steps, num_envs=80, seconds=args.steps*.01, collection_elapsed_s=time.time() - start, initial=initial, final=dict(parameters=pd, assignments=assignments(e)), geometry_recipe=recipe, geometry=e.scene.terrain.exact_partition_receipt, route_scope=route_scope, body_names=list(r.body_names), full_route_raw=dict(name=npz.name, bytes=npz.stat().st_size, sha256=hashlib.sha256(npz.read_bytes()).hexdigest(), shapes={k: list(v.shape) for k, v in data.items()}), raw_contains_every_control_pre_reset_root30q_commands_actions_ground_normal_reason_contact_and_each_physical_wheel_force=True, progress_semantics='sum pre-reset minus same-step before root projected on actual before heading; no teleport progress; full and first-ordinary-failure prefix separately', groups=summaries, reason_names=names, declared_time_outs=decl, termination_counts={n: int(data['reasons'][..., i].sum()) for i, n in enumerate(names)}, actual_union_ordinary=int(data['terminated'].sum()), actual_union_truncation=int(data['truncated'].sum()), reason_coverage_exact=coverage, nonfinite=False, max_closure_m=float(data['closure'].max()), legacy_single_peak_2mm_pass=bool(data['closure'].max() <= 0.002), max_mimic_rad=float(data['mimic'].max()), independent_ground_max_error_m=ground_error, height_reward_formula_max_error=height_error, independent_control_mean_load_max_error_N=integral_error, actual_physical_callbacks=actualcallbacks, actual_action_callbacks={k: v - calls0[k] for k, v in e._physics_action_delay.calls.items()}, physical_action_audit=audit, sensor_recipe=e._sensor_mild.receipt(), sensor_manager=sensor, feedback_recipe=e.feedback_delay_recipe(), action_recipe=e.action_delay_recipe(), spring_recipe=e.spring_pressure_recipe(), gas_recipe=e.gas_damping_recipe(), chassis_PD_recipe=e.chassis_pd_recipe(), frozen_actor=observer.audit(), contact_metadata=e._contact_capture_metadata, terrain_grade_not_declared=True, RM_annotation_id='MOD4-RM-TERRAIN-SPIN-AND-ENTRY-LIP-ANNOTATION-001')
    output.write_text(json.dumps(result, indent=2))
    print(json.dumps(dict(route_groups=summaries, source=result['checkpoint_sha256'], raw_SHA=result['full_route_raw']['sha256'])), flush=True)
    save('COMPLETE_ACTUAL.json',dict(passed_data_contract=True,case_id=args.case_id,protocol=result['protocol'],checkpoint_sha256=observer.checkpoint_sha256,num_envs=80,steps=args.steps,callbacks=actualcallbacks,ordinary=result['actual_union_ordinary'],truncation=result['actual_union_truncation'],ground_error_m=ground_error,query=result['route_scope']['query_worldmesh_evidence'],raw=dict(path=str(npz),bytes=npz.stat().st_size,sha256=hashlib.sha256(npz.read_bytes()).hexdigest()),original_report=dict(path=str(output),sha256=hashlib.sha256(output.read_bytes()).hexdigest()),native120_not_full15s=args.steps==120,no_PPO=True,qualification_claimed=False))
    e.close()
