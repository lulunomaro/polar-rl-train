from pathlib import Path
import json,os,time,math,numpy as np,torch
import mod4_task as task
from spin_commands import audit
from nominal_parameter_audit import parameter_audit
from contact_geometry import ControlGeometry
from actuator_clip_diagnostics import rating_clipped
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from retention_native_witness_v1 import tensor,create_observed_env,build_observed_frozen_policy,finalize_observer,SMALL_EVAL_CAPACITY

@torch.inference_mode()
def run_spin(args):
    torch.manual_seed(args.seed)
    cfg = task.Mod4EnvCfg()
    cfg.seed = args.seed
    cfg.scene.num_envs = args.num_envs
    cfg.sim.device = args.device
    for key, value in SMALL_EVAL_CAPACITY.items():
        setattr(cfg.sim.physics, key, value)
    cfg.scene.wheel_contact_scut.filter_prim_paths_expr = ['/World/ground/geometry/mesh']
    cfg.scene.wheel_contact_scut.max_contact_data_count_per_prim = 64
    env = create_observed_env(args, cfg=cfg)
    vec = RslRlVecEnvWrapper(env, clip_actions=6.0)
    robot = env.scene['robot']
    dev = env.device
    n = env.num_envs
    from frozen_history_policy import build_frozen_policy
    vec, policy, policy_observer = build_observed_frozen_policy(vec, args.checkpoint, dev)
    env.reset()
    initial_action_assignments = {k: {'delay_us': (g['lag_steps'] * 2500).cpu().tolist(), 'episode': g['episode'].cpu().tolist()} for k, g in env._physics_action_delay.queue.groups.items()}
    cmd = env.command_manager.get_term('twist')
    initial_command_audit = audit(env)
    initial_parameters = parameter_audit(env)
    spring_initial_assignments = dict(factor=env._spring_pressure.component.factor.cpu().tolist(), episode=env._spring_pressure.component.episode.cpu().tolist(), actual_stiffness_N_m=env._spring_pressure.component.actual_stiffness(env._spring_pressure.nominal).cpu().tolist())
    gas_initial_assignments = dict(factor=env._gas_damping.component.factor.cpu().tolist(), episode=env._gas_damping.component.episode.cpu().tolist(), actual_damping_Ns_m=env._gas_damping.component.actual_damping_Ns_per_m().cpu().tolist())
    chassis_pd_initial_assignments = dict(COM=dict(delta_m=env._chassis_com.component.delta_m.cpu().tolist(), episode=env._chassis_com.component.episode.cpu().tolist()), PD=dict(factors={k: v.cpu().tolist() for k, v in env._explicit_pd.component.factor.items()}, episode=env._explicit_pd.component.episode.cpu().tolist(), actual_coefficients={k: v.cpu().tolist() for k, v in env._explicit_pd.component.coefficients().items()}))
    if hasattr(cmd, 'set_manual_evaluation_mode'):
        cmd.set_manual_evaluation_mode()
    groups = [dict(vx=0.0, wz=0.0, profile='stand'), dict(vx=0.3, wz=0.0, profile='straight'), dict(vx=1.0, wz=0.0, profile='straight'), dict(vx=0.0, wz=1.0, profile='spin'), dict(vx=0.0, wz=-1.0, profile='spin'), dict(vx=0.0, wz=2.0, profile='spin'), dict(vx=0.0, wz=-2.0, profile='spin'), dict(vx=0.0, wz=args.max_rate, profile='spin'), dict(vx=0.0, wz=-args.max_rate, profile='spin'), dict(vx=0.0, wz=args.max_rate, profile='spin_ramp_stop_reverse'), dict(vx=0.0, wz=-args.max_rate, profile='spin_ramp_stop_reverse')]
    if n % len(groups):
        raise ValueError('Number of environments must be divisible by eleven')
    gids = torch.arange(n, device=dev) % len(groups)
    vx = torch.tensor([g['vx'] for g in groups], device=dev)[gids]
    yaw = torch.tensor([g['wz'] for g in groups], device=dev)[gids]
    ramp = gids >= 9
    alive = torch.ones(n, dtype=torch.bool, device=dev)
    counts = torch.zeros(n, device=dev)
    initial_q = tensor(robot.data.joint_pos).cpu().tolist()
    initial_root = tensor(robot.data.root_state_w).cpu().tolist()
    root0 = tensor(robot.data.root_pos_w)[:, :2].clone()
    posmax = counts.clone()
    peaktilt = counts.clone()
    gapmax = counts.clone()
    unloadmax = counts.clone()
    wheel_speed_peak = counts.clone()
    wheel_torque_peak = counts.clone()
    turns = counts.clone()
    absolute_turns = counts.clone()
    firstfail = torch.full((n,), args.steps, device=dev, dtype=torch.long)
    last = torch.zeros((n, 6), device=dev)
    last2 = last.clone()
    closed = 0.0
    mimic = 0.0
    nonfinite = False
    names = ['yaw_rate', 'yaw_error', 'speed_error', 'tilt', 'height_error', 'delta', 'd2', 'left_fz', 'right_fz', 'guide_force', 'base_force', 'wheel_rating_clip', 'leg_rating_clip', 'left_slip', 'right_slip', 'spin_translation_speed', 'left_slip_legacy_reference', 'right_slip_legacy_reference']
    sums = {k: counts.clone() for k in names}
    stopcount = counts.clone()
    stoperr = counts.clone()
    geom = ControlGeometry(env, task.USD_PATH)
    capture = env._integrated_contact
    contact = None
    if args.contact_readback:
        from substep_contact_readback import SubstepContactReadback
        contact = SubstepContactReadback(env, geom)
    shadows = {k: torch.zeros((n, 2), device=dev) for k in ('midplane_mean_speed', 'midplane_mean_rolling_abs', 'scut_vertical_bottom_mean_speed', 'midplane_loaded_mean_speed', 'midplane_load_samples', 'scut_history_masked_mean_speed', 'scut_history_samples')}
    wheel_ids, _ = robot.find_joints(task.WHEEL_ORDER, preserve_order=True)
    start = time.time()
    for step in range(args.steps):
        t = step * env.step_dt
        factor = 0.0 if t < 0.5 else min(1.0, (t - 0.5) / 1.0) if t < 5.0 else max(0.0, 1.0 - (t - 5.0) / 1.5) if t < 9.0 else -min(1.0, (t - 9.0) / 1.0) if t < 13.0 else -max(0.0, 1.0 - (t - 13.0) / 1.0)
        desired_yaw = torch.where(ramp, yaw * factor, yaw)
        cmd.time_left[:] = 1000000000.0
        cmd.is_standing_env[:] = False
        cmd.is_heading_env[:] = False
        cmd.command[:] = 0
        cmd.command[:, 0] = vx
        cmd.command[:, 2] = desired_yaw
        audit(env)
        task.height_cmd(env)[:] = 0.25
        if contact:
            contact.begin_control(alive & (step >= 50))
        action = policy(vec.get_observations())
        _, _, done, _ = vec.step(action)
        firstfail = torch.where(alive & done.bool(), torch.full_like(firstfail, step), firstfail)
        alive &= ~done.bool()
        if not torch.isfinite(tensor(robot.data.joint_pos)).all() or not torch.isfinite(action).all():
            nonfinite = True
            break
        valid = env.episode_length_buf >= 10
        if valid.any():
            closed = max(closed, float(torch.stack(list(task.closure_errors(env).values()))[:, valid].max()))
            mimic = max(mimic, float(torch.stack(list(task.mimic_errors(env).values()))[:, valid].max()))
        mask = alive & (step >= 50)
        counts += mask
        tilt = torch.acos((-tensor(robot.data.projected_gravity_b)[:, 2]).clamp(-1, 1)) * 180 / torch.pi
        rate = tensor(robot.data.root_ang_vel_w)[:, 2]
        turns += torch.where(alive, rate * env.step_dt / (2 * torch.pi), 0.0)
        absolute_turns += torch.where(alive, rate.abs() * env.step_dt / (2 * torch.pi), 0.0)
        gap, slip = geom.read()
        if step == 50:
            capture.off_max.zero_()
        gapmax = torch.maximum(gapmax, torch.where(mask, gap.max(1).values, 0.0))
        unloadmax = torch.maximum(unloadmax, torch.where(mask, capture.off_max.float() * env.physics_dt, 0.0))
        posmax = torch.maximum(posmax, torch.where(mask, (tensor(robot.data.root_pos_w)[:, :2] - root0).norm(dim=1), 0.0))
        peaktilt = torch.maximum(peaktilt, torch.where(mask, tilt, 0.0))
        wheel_speed_peak = torch.maximum(wheel_speed_peak, torch.where(mask, tensor(robot.data.joint_vel)[:, wheel_ids].abs().max(1).values, 0.0))
        wheel_torque_peak = torch.maximum(wheel_torque_peak, torch.where(mask, robot.actuators['wheels'].applied_effort.abs().max(1).values, 0.0))
        fz = capture.impulse / env.step_dt
        rolling = env._spin_rolling_consistency
        values_shadow = rolling.last
        mid = values_shadow['point_velocity'][..., :2].norm(dim=-1)
        vertical = torch.zeros((n, 2, 3), device=dev)
        vertical[..., 2] = -rolling.radius.squeeze(-1)
        scutvel = (tensor(robot.data.body_link_lin_vel_w)[:, geom.ids] + torch.cross(tensor(robot.data.body_ang_vel_w)[:, geom.ids], vertical, dim=-1))[..., :2].norm(dim=-1)
        history = tensor(env.scene.sensors['wheel_contact_scut'].data.net_forces_w_history).norm(dim=-1).max(dim=1).values > 1.0
        loaded = (fz >= 10.0) & mask[:, None]
        hist = history & mask[:, None]
        shadows['midplane_mean_speed'] += mid * mask[:, None]
        shadows['midplane_mean_rolling_abs'] += values_shadow['rolling_signed'].abs() * mask[:, None]
        shadows['scut_vertical_bottom_mean_speed'] += scutvel * mask[:, None]
        shadows['midplane_loaded_mean_speed'] += mid * loaded
        shadows['midplane_load_samples'] += loaded
        shadows['scut_history_masked_mean_speed'] += scutvel * hist
        shadows['scut_history_samples'] += hist
        values = dict(yaw_rate=rate, yaw_error=(rate - desired_yaw).abs(), speed_error=(tensor(robot.data.root_lin_vel_b)[:, 0] - vx).abs(), tilt=tilt, height_error=(task.root_height_above_ground(env) - 0.25).abs(), delta=(action - last).abs().mean(1), d2=(action - 2 * last + last2).abs().mean(1), left_fz=fz[:, 0], right_fz=fz[:, 1], guide_force=tensor(env.scene.sensors['guide_contact'].data.net_forces_w).norm(dim=-1).sum(1), base_force=tensor(env.scene.sensors['chassis_contact'].data.net_forces_w).norm(dim=-1).sum(1), wheel_rating_clip=rating_clipped(robot.actuators['wheels']).float().mean(1), leg_rating_clip=rating_clipped(robot.actuators['legs']).float().mean(1), left_slip=slip[:, 0], right_slip=slip[:, 1], spin_translation_speed=tensor(robot.data.root_lin_vel_w)[:, :2].norm(dim=1), left_slip_legacy_reference=geom.legacy_reference_slip[:, 0], right_slip_legacy_reference=geom.legacy_reference_slip[:, 1])
        for k, v in values.items():
            sums[k] += v * mask
        stopped = ramp & (t >= 8.0 and t < 9.0 or t >= 14.5)
        stopcount += mask & stopped
        stoperr += rate.abs() * (mask & stopped)
        last2 = last
        last = action.clone()
    per = {k: v / counts.clamp_min(1) for k, v in sums.items()}
    per.update(peak_wheel_speed_rad_s=wheel_speed_peak, peak_wheel_applied_torque_nm=wheel_torque_peak, peak_tilt=peaktilt, maximum_gap_m=gapmax, longest_both_low_s=unloadmax, net_signed_turns=turns, absolute_turns=absolute_turns, root_xy_excursion_m=posmax, stop_yaw_abs=stoperr / stopcount.clamp_min(1))
    physical = alive & (counts > 0) & (peaktilt <= 15) & (per['height_error'] <= 0.03) & (per['base_force'] <= 1) & (per['guide_force'] <= 1) & (per['wheel_rating_clip'] <= 0.2) & (per['leg_rating_clip'] <= 0.2)
    skill = physical & (per['yaw_error'] <= torch.maximum(torch.full_like(yaw, 0.2), yaw.abs() * 0.2)) & (per['speed_error'] <= torch.maximum(torch.full_like(vx, 0.12), vx.abs() * 0.25)) & (per['tilt'] <= 8) & (per['peak_tilt'] <= 12) & (per['left_slip'] <= 0.15) & (per['right_slip'] <= 0.15) & (per['delta'] <= 0.18) & (per['d2'] <= 0.25) & (per['maximum_gap_m'] <= 0.002) & (per['longest_both_low_s'] <= 0.01501) & (per['left_fz'] >= 10) & (per['right_fz'] >= 10) & ((yaw == 0) | (per['spin_translation_speed'] <= 0.12)) & (~ramp | (per['stop_yaw_abs'] <= 0.2))
    skill_legacy_reference = physical & (per['yaw_error'] <= torch.maximum(torch.full_like(yaw, 0.2), yaw.abs() * 0.2)) & (per['speed_error'] <= torch.maximum(torch.full_like(vx, 0.12), vx.abs() * 0.25)) & (per['tilt'] <= 8) & (per['peak_tilt'] <= 12) & (per['left_slip_legacy_reference'] <= 0.15) & (per['right_slip_legacy_reference'] <= 0.15) & (per['delta'] <= 0.18) & (per['d2'] <= 0.25) & (per['maximum_gap_m'] <= 0.002) & (per['longest_both_low_s'] <= 0.01501) & (per['left_fz'] >= 10) & (per['right_fz'] >= 10) & ((yaw == 0) | (per['spin_translation_speed'] <= 0.12)) & (~ramp | (per['stop_yaw_abs'] <= 0.2))
    rows = []
    for gid, g in enumerate(groups):
        ids = gids == gid
        row = dict(g, group_id=gid, environments=int(ids.sum()), survival_fraction=float(alive[ids].float().mean()), physical_smoke_fraction=float(physical[ids].float().mean()), spin_skill_fraction=float(skill[ids].float().mean()), spin_skill_fraction_legacy_reference=float(skill_legacy_reference[ids].float().mean()))
        row['means'] = {k: float(v[ids].mean()) for k, v in per.items()}
        row['worst'] = {k: float(per[k][ids].max()) for k in ['peak_wheel_speed_rad_s', 'peak_wheel_applied_torque_nm', 'peak_tilt', 'maximum_gap_m', 'longest_both_low_s', 'height_error', 'wheel_rating_clip', 'leg_rating_clip']}
        rows.append(row)
    result = dict(probe_version='spin_rate_v1_same_gates_control_rate_motor_peaks', probe_sha256=__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(), target_rate_rad_s=args.max_rate, mode='frozen_deterministic_spin_rate_probe', checkpoint=args.checkpoint, seed=args.seed, steps=args.steps, seconds=args.steps * env.step_dt, profile=args.dr_profile, groups=rows, nonfinite=nonfinite, max_closure_m=closed, max_mimic_rad=mimic, physical_smoke_pass=not nonfinite and closed <= 0.002 and (mimic <= 0.01) and all((r['physical_smoke_fraction'] >= 0.95 for r in rows)), spin_skill_pass=args.steps * env.step_dt >= 15 and (not nonfinite) and (closed <= 0.002) and (mimic <= 0.01) and all((r['spin_skill_fraction'] >= 0.8 for r in rows)), initial_command_audit=initial_command_audit, initial_parameter_audit=initial_parameters, reset_joint_pos_before_physics=initial_q, reset_root_before_physics=initial_root, final_parameter_audit=parameter_audit(env), observations={k: list(v.shape) for k, v in env.observation_manager.compute().items()}, per_environment={k: v.cpu().tolist() for k, v in per.items()}, alive=alive.cpu().tolist(), group_ids=gids.cpu().tolist(), first_failure_step=firstfail.cpu().tolist(), elapsed_s=time.time() - start, ppo_performed=False, scope='Physical smoke does not require an untrained policy to track yaw. Spin skill pass requires 15s. Gap/slip proxy and torque are control-step sampled; load/off duration use the actual reported physics timestep. Stage one has NO spin translation.')
    result.update(geometry_reference_version=geom.reference_version, spin_skill_pass_legacy_reference=args.steps * env.step_dt >= 15 and (not nonfinite) and (closed <= 0.002) and (mimic <= 0.01) and all((r['spin_skill_fraction_legacy_reference'] >= 0.8 for r in rows)), geometry_thresholds_changed=False)
    for key in ('midplane_mean_speed', 'midplane_mean_rolling_abs', 'scut_vertical_bottom_mean_speed'):
        shadows[key] /= counts[:, None].clamp_min(1)
    shadows['midplane_loaded_mean_speed'] /= shadows['midplane_load_samples'].clamp_min(1)
    shadows['scut_history_masked_mean_speed'] /= shadows['scut_history_samples'].clamp_min(1)
    result['calibration_control_shadow'] = {k: v.cpu().tolist() for k, v in shadows.items()}
    result['calibration_geometry'] = rolling.metadata
    result['calibration_scope'] = 'Read-only shadows; SCUT-style uses correct link reference and input-mesh radius. No old acceptance boolean changed.'
    if contact:
        result['substep_contact_readback'] = contact.result()
    result['frozen_architecture_audit'] = policy_observer.audit()
    result['sensor_recipe'] = env._sensor_mild.receipt()
    result['sensor_actual_manager_audit'] = env.sensor_sdk_audit()
    result['feedback_delay_recipe'] = env.feedback_delay_recipe()
    result['D3_closed_loop_actual_actor_input'] = True
    assert env._feedback_delay_mild.enabled and env.physics_dt == 0.0025
    result['physical_action_delay_recipe'] = env.action_delay_recipe()
    result['physical_action_delay_audit'] = env._physics_action_delay.audit()
    result['physical_action_final_episode_assignments'] = {k: {'delay_us': (g['lag_steps'] * 2500).cpu().tolist(), 'episode': g['episode'].cpu().tolist()} for k, g in env._physics_action_delay.queue.groups.items()}
    result['physical_action_initial_episode_assignments'] = initial_action_assignments
    result['D6_closed_loop_gas_damping_engineering_pressure'] = True
    result['D7_closed_loop_chassis_COM_explicit_PD_engineering_pressure'] = True
    result['chassis_PD_recipe'] = env.chassis_pd_recipe()
    result['chassis_PD_audit'] = env.chassis_pd_audit()
    result['chassis_PD_initial_episode_assignments'] = chassis_pd_initial_assignments
    result['chassis_PD_final_episode_assignments'] = dict(COM=dict(delta_m=env._chassis_com.component.delta_m.cpu().tolist(), episode=env._chassis_com.component.episode.cpu().tolist()), PD=dict(factors={k: v.cpu().tolist() for k, v in env._explicit_pd.component.factor.items()}, episode=env._explicit_pd.component.episode.cpu().tolist(), actual_coefficients={k: v.cpu().tolist() for k, v in env._explicit_pd.component.coefficients().items()}))
    result['gas_damping_recipe'] = env.gas_damping_recipe()
    result['gas_damping_audit'] = env._gas_damping.audit()
    result['gas_damping_initial_episode_assignments'] = gas_initial_assignments
    result['gas_damping_final_episode_assignments'] = dict(factor=env._gas_damping.component.factor.cpu().tolist(), episode=env._gas_damping.component.episode.cpu().tolist(), actual_damping_Ns_m=env._gas_damping.component.actual_damping_Ns_per_m().cpu().tolist())
    result['D5_closed_loop_stiffness_engineering_pressure'] = True
    result['spring_pressure_recipe'] = env.spring_pressure_recipe()
    result['spring_pressure_audit'] = env._spring_pressure.audit()
    result['spring_pressure_initial_episode_assignments'] = spring_initial_assignments
    result['spring_pressure_final_episode_assignments'] = dict(factor=env._spring_pressure.component.factor.cpu().tolist(), episode=env._spring_pressure.component.episode.cpu().tolist(), actual_stiffness_N_m=env._spring_pressure.component.actual_stiffness(env._spring_pressure.nominal).cpu().tolist())
    result['D4_closed_loop_actual_physical_target_delay'] = True
    result['inherited_feedback_recipe_action_delay0_is_D3_only'] = True
    assert all((v == args.steps * 4 for v in env._physics_action_delay.calls.values()))
    assert result['physical_action_delay_audit']['application_formula_max_error'] <= 1e-06
    Path(args.output).write_text(json.dumps(result, indent=2))
    print('SPIN_PROBE_RESULT', json.dumps({k: v for k, v in result.items() if k not in ['per_environment', 'groups', 'initial_parameter_audit', 'final_parameter_audit', 'reset_joint_pos_before_physics', 'reset_root_before_physics', 'alive', 'group_ids', 'first_failure_step']}), flush=True)
    finalize_observer(env, result)
    return result
