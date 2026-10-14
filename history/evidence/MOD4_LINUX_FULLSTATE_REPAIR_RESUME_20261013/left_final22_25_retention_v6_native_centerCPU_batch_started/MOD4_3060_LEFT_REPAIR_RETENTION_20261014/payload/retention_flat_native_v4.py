from pathlib import Path
import json,os,time,math,numpy as np,torch
import mod4_task as task
from spin_commands import audit
from nominal_parameter_audit import parameter_audit
from contact_geometry import ControlGeometry
from actuator_clip_diagnostics import rating_clipped
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from retention_native_witness_v4 import tensor,create_observed_env,build_observed_frozen_policy,finalize_observer,SMALL_EVAL_CAPACITY

@torch.inference_mode()
def run_flat(args):
    torch.manual_seed(args.seed)
    cfg = task.Mod4EnvCfg()
    cfg.seed = args.seed
    cfg.scene.num_envs = args.num_envs
    cfg.sim.device = args.device
    cfg.sim.enable_scene_query_support = True
    for key, value in SMALL_EVAL_CAPACITY.items():
        setattr(cfg.sim.physics, key, value)
    from isaaclab.sensors import ContactSensorCfg
    cfg.scene.wheel_contact_legacy_capture = ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/links/(left|right)_wheel', update_period=0.005, history_length=3, track_air_time=False, debug_vis=False)
    env = create_observed_env(args, cfg=cfg)
    vec = RslRlVecEnvWrapper(env, clip_actions=6.0)
    robot = env.scene['robot']
    dev = env.device
    n = env.num_envs
    if not args.reset_smoke:
        from frozen_history_policy import build_frozen_policy
        vec, policy, policy_observer = build_observed_frozen_policy(vec, args.checkpoint, dev)
    env.reset()
    initial_action_assignments = {k: {'delay_us': (g['lag_steps'] * 2500).cpu().tolist(), 'episode': g['episode'].cpu().tolist()} for k, g in env._physics_action_delay.queue.groups.items()}
    spring_initial_assignments = dict(factor=env._spring_pressure.component.factor.cpu().tolist(), episode=env._spring_pressure.component.episode.cpu().tolist(), actual_stiffness_N_m=env._spring_pressure.component.actual_stiffness(env._spring_pressure.nominal).cpu().tolist())
    gas_initial_assignments = dict(factor=env._gas_damping.component.factor.cpu().tolist(), episode=env._gas_damping.component.episode.cpu().tolist(), actual_damping_Ns_m=env._gas_damping.component.actual_damping_Ns_per_m().cpu().tolist())
    chassis_pd_initial_assignments = dict(COM=dict(delta_m=env._chassis_com.component.delta_m.cpu().tolist(), episode=env._chassis_com.component.episode.cpu().tolist()), PD=dict(factors={k: v.cpu().tolist() for k, v in env._explicit_pd.component.factor.items()}, episode=env._explicit_pd.component.episode.cpu().tolist(), actual_coefficients={k: v.cpu().tolist() for k, v in env._explicit_pd.component.coefficients().items()}))
    mild_initial_parameters = env._mild_dr.audit() if hasattr(env, '_mild_dr') else None
    mild_initial_q = env._rescue_reset_q.detach().cpu().tolist()
    mild_initial_root = tensor(robot.data.root_state_w).detach().cpu().tolist()
    initial_capture = getattr(env, '_integrated_contact', None)
    if initial_capture is not None:
        assert all((int(torch.count_nonzero(x)) == 0 for x in [initial_capture.history, initial_capture.sums, initial_capture.impulse, initial_capture.off_run, initial_capture.off_max])), 'stale contact buffers after reset'
    legids, _ = robot.find_joints(task.LEG_ORDER, preserve_order=True)
    command = env.command_manager.get_term('twist')
    if hasattr(command, 'set_manual_evaluation_mode'):
        command.set_manual_evaluation_mode()
    levels = [0.0, 0.3, 0.6, 1.0, -args.speed_limit, args.speed_limit]
    if args.ramp_suite:
        levels += [-1.5, 1.5, -2.0, 2.0]
    if n % len(levels):
        raise ValueError('num_envs must be divisible by number of groups')
    group_ids = torch.arange(n, device=dev) % len(levels)
    peak_targets = torch.tensor(levels, device=dev)[group_ids]
    ramp_groups = group_ids >= 6 if args.ramp_suite else torch.zeros(n, dtype=torch.bool, device=dev)
    targets = peak_targets.clone()
    wheelids, _ = robot.find_joints(task.WHEEL_ORDER, preserve_order=True)
    motorids = legids + wheelids
    from contact_geometry import ControlGeometry
    from actuator_clip_diagnostics import rating_clipped
    geometry = ControlGeometry(env, task.USD_PATH)
    gap_max = torch.full((n, 2), -1000000000.0, device=dev)
    unload_max = torch.zeros(n, device=dev)
    max_tilt = torch.zeros(n, device=dev)
    sat_run = torch.zeros(n, device=dev)
    sat_longest = sat_run.clone()
    rated_run = sat_run.clone()
    rated_longest = sat_run.clone()
    steady_counts = torch.zeros(n, device=dev)
    steady_error = steady_counts.clone()
    stop_counts = torch.zeros(n, device=dev)
    stop_error = stop_counts.clone()
    alive = torch.ones(n, dtype=torch.bool, device=dev)
    firstdone = torch.full((n,), args.steps, device=dev, dtype=torch.long)
    counts = torch.zeros(n, device=dev)
    sums = {k: torch.zeros(n, device=dev) for k in ['speed', 'vel_error', 'tilt', 'height', 'height_error', 'both_wheels', 'both_wheels_scut_history', 'both_wheels_history_5ms', 'both_wheels_binned_mean', 'height_credit_active', 'height_credit_legacy', 'left_wheel_contact', 'right_wheel_contact', 'left_wheel_fz', 'right_wheel_fz', 'guide_force', 'base_force', 'delta', 'd2', 'wheel_abs_speed', 'wheel_abs_torque', 'leg_abs_torque', 'wheel_effort_clip_fraction', 'leg_effort_clip_fraction', 'wheel_near_no_load', 'left_mean_fz_substep', 'right_mean_fz_substep', 'left_loaded_fraction_substep', 'right_loaded_fraction_substep', 'left_support_slip_control', 'right_support_slip_control', 'left_support_slip_legacy_reference', 'right_support_slip_legacy_reference', 'wheel_rating_clip_fraction', 'leg_rating_clip_fraction', 'wheel_rating_clip_fraction_unmapped_shadow', 'leg_rating_clip_fraction_unmapped_shadow']}
    last = torch.zeros((n, 6), device=dev)
    last2 = last.clone()
    maxclosure = 0.0
    maxmimic = 0.0
    nonfinite = False
    resets = 0
    reset_closures = []
    first_pose = {}
    start = time.time()
    for step in range(args.steps):
        if args.reset_smoke and step % 30 == 0:
            env.reset()
            alive[:] = True
        command.time_left[:] = 1000000000.0
        command.is_standing_env[:] = False
        if hasattr(command, 'is_heading_env'):
            command.is_heading_env[:] = False
        t = step * env.step_dt
        factor = 0.0 if t < 0.5 else min(1.0, (t - 0.5) / 2.0) if t < 5.0 else max(0.0, 1.0 - (t - 5.0) / 2.0) if t < 9.0 else -min(1.0, (t - 9.0) / 2.0) if t < 13.0 else -max(0.0, 1.0 - (t - 13.0))
        targets = torch.where(ramp_groups, peak_targets * factor, peak_targets)
        command.command[:] = 0
        command.command[:, 0] = targets if not args.reset_smoke else 0.0
        task.height_cmd(env)[:] = 0.25
        with torch.inference_mode():
            if args.reset_smoke:
                action = torch.zeros((n, 6), device=dev)
                action[:, :4] = env._rescue_reset_q[:, legids] / task.LEG_ACTION_SCALE
            else:
                action = policy(vec.get_observations())
            _, _, done, _ = vec.step(action)
        done = done.bool()
        firstdone = torch.where(alive & done, torch.full_like(firstdone, step), firstdone)
        alive &= ~done
        resets += int(done.sum())
        if not torch.isfinite(tensor(robot.data.joint_pos)).all() or not torch.isfinite(action).all():
            nonfinite = True
            break
        clo = torch.stack(list(task.closure_errors(env).values())).max(0).values
        mim = torch.stack(list(task.mimic_errors(env).values())).max(0).values
        if step == 0:
            reset_closures = clo.detach().cpu().tolist()
            first_pose = {'root_z_m': tensor(robot.data.root_pos_w)[:, 2].detach().cpu().tolist(), 'ground_z_m': getattr(env, '_mod4_ground_z', torch.zeros(n, device=dev)).detach().cpu().tolist(), 'reported_height_m': task.root_height_above_ground(env).detach().cpu().tolist()}
        valid = env.episode_length_buf >= 10
        if valid.any():
            maxclosure = max(maxclosure, float(clo[valid].max()))
            maxmimic = max(maxmimic, float(mim[valid].max()))
        mask = alive & (step >= 50)
        counts += mask
        forces = tensor(env.scene.sensors['wheel_contact'].data.net_forces_w)
        guide = tensor(env.scene.sensors['guide_contact'].data.net_forces_w)
        base = tensor(env.scene.sensors['chassis_contact'].data.net_forces_w)
        history_active = tensor(env.scene.sensors['wheel_contact_scut'].data.net_forces_w_history)
        history = tensor(env.scene.sensors['wheel_contact_legacy_capture'].data.net_forces_w_history)
        both_active = (history_active.norm(dim=-1).amax(dim=1) > 1.0).all(dim=1).float()
        both_legacy = (history.norm(dim=-1).amax(dim=1) > 1.0).all(dim=1).float()
        capture = getattr(env, '_integrated_contact', None)
        integrated_history = capture.history if capture is not None else history_active
        both_integrated = (integrated_history.norm(dim=-1).amax(dim=1) > 1.0).all(dim=1).float()
        height_soft = task.height_track(env, sigma=task.SCUT_H_SOFT_SIGMA)
        h = task.root_height_above_ground(env)
        values = {'speed': tensor(robot.data.root_lin_vel_b)[:, 0], 'vel_error': (tensor(robot.data.root_lin_vel_b)[:, 0] - targets).abs(), 'tilt': torch.acos((-tensor(robot.data.projected_gravity_b)[:, 2]).clamp(-1, 1)) * 180 / torch.pi, 'height': h, 'height_error': (h - 0.25).abs(), 'both_wheels': (forces.norm(dim=-1) > 1.0).all(1).float(), 'both_wheels_scut_history': both_legacy, 'both_wheels_history_5ms': both_active, 'both_wheels_binned_mean': both_integrated, 'height_credit_active': height_soft * both_integrated, 'height_credit_legacy': height_soft * both_legacy, 'left_wheel_contact': (forces[:, 0].norm(dim=-1) > 1.0).float(), 'right_wheel_contact': (forces[:, 1].norm(dim=-1) > 1.0).float(), 'left_wheel_fz': forces[:, 0, 2], 'right_wheel_fz': forces[:, 1, 2], 'guide_force': guide.norm(dim=-1).sum(1), 'base_force': base.norm(dim=-1).sum(1), 'delta': (action - last).abs().mean(1), 'd2': (action - 2 * last + last2).abs().mean(1)}
        gap, slip = geometry.read()
        gap_max = torch.maximum(gap_max, torch.where(mask[:, None], gap, torch.full_like(gap, -1000000000.0)))
        if capture is not None:
            if step == 50:
                capture.off_max.zero_()
            unload_max = torch.maximum(unload_max, torch.where(mask, capture.off_max.float() * env.physics_dt, 0.0))
            mean_fz = capture.impulse / env.step_dt
            loaded = capture.loaded.float() / int(round(env.step_dt / env.physics_dt))
        else:
            mean_fz = forces[:, :, 2]
            loaded = (forces.norm(dim=-1) > 1.0).float()
        values.update(left_mean_fz_substep=mean_fz[:, 0], right_mean_fz_substep=mean_fz[:, 1], left_loaded_fraction_substep=loaded[:, 0], right_loaded_fraction_substep=loaded[:, 1], left_support_slip_control=slip[:, 0], right_support_slip_control=slip[:, 1], left_support_slip_legacy_reference=geometry.legacy_reference_slip[:, 0], right_support_slip_legacy_reference=geometry.legacy_reference_slip[:, 1])
        applied = tensor(robot.data.applied_torque)
        computed = tensor(robot.data.computed_torque)
        wc = (computed[:, wheelids] - applied[:, wheelids]).abs() > 0.1
        lc = (computed[:, legids] - applied[:, legids]).abs() > 0.1
        unmapped_wc = (computed[:, wheelids] * robot.actuators['wheels'].episode_scale - applied[:, wheelids]).abs() > 0.1
        unmapped_lc = (computed[:, legids] * robot.actuators['legs'].episode_scale - applied[:, legids]).abs() > 0.1
        rated_wc = rating_clipped(robot.actuators['wheels'])
        rated_lc = rating_clipped(robot.actuators['legs'])
        values.update(wheel_rating_clip_fraction=rated_wc.float().mean(1), leg_rating_clip_fraction=rated_lc.float().mean(1), wheel_rating_clip_fraction_unmapped_shadow=unmapped_wc.float().mean(1), leg_rating_clip_fraction_unmapped_shadow=unmapped_lc.float().mean(1))
        values.update(wheel_abs_speed=tensor(robot.data.joint_vel)[:, wheelids].abs().amax(1), wheel_abs_torque=applied[:, wheelids].abs().amax(1), leg_abs_torque=applied[:, legids].abs().amax(1), wheel_effort_clip_fraction=wc.float().mean(1), leg_effort_clip_fraction=lc.float().mean(1), wheel_near_no_load=(tensor(robot.data.joint_vel)[:, wheelids].abs() > 0.95 * task.WHEEL_NO_LOAD).any(1).float())
        max_tilt = torch.maximum(max_tilt, torch.where(mask, values['tilt'], 0.0))
        sat_run = torch.where(mask & wc.any(1), sat_run + env.step_dt, 0.0)
        sat_longest = torch.maximum(sat_longest, sat_run)
        rated_run = torch.where(mask & rated_wc.any(1), rated_run + env.step_dt, 0.0)
        rated_longest = torch.maximum(rated_longest, rated_run)
        settled = ~ramp_groups | (t >= 3.5 and t < 5.0 or (t >= 12.0 and t < 13.0))
        stopped = ramp_groups & (t >= 8.0 and t < 9.0 or t >= 14.5)
        steady_counts += mask & settled
        steady_error += values['vel_error'] * (mask & settled)
        stop_counts += mask & stopped
        stop_error += values['speed'].abs() * (mask & stopped)
        for k, v in values.items():
            sums[k] += v * mask
        last2 = last
        last = action.clone()
    per = {k: v / counts.clamp_min(1) for k, v in sums.items()}
    targets = peak_targets
    per['steady_vel_error'] = steady_error / steady_counts.clamp_min(1)
    per['stop_abs_speed'] = stop_error / stop_counts.clamp_min(1)
    per['longest_both_low_force_s_substep'] = unload_max
    per['left_gap_max_control_m'] = gap_max[:, 0]
    per['right_gap_max_control_m'] = gap_max[:, 1]
    per['max_tilt'] = max_tilt
    per['longest_wheel_effort_clip_s'] = sat_longest
    per['longest_wheel_rating_clip_s'] = rated_longest
    common = alive & (counts > 0) & (per['vel_error'] <= torch.maximum(torch.full_like(targets, 0.12), targets.abs() * 0.25)) & (per['tilt'] <= 8) & (per['height_error'] <= 0.03) & (per['delta'] <= 0.18) & (per['d2'] <= 0.25)
    strict = common & (per['both_wheels_scut_history'] >= 0.9)
    strict_integrated = common & (per['both_wheels_binned_mean'] >= 0.9)
    strict_5ms = common & (per['both_wheels_history_5ms'] >= 0.9)
    strict_instant = common & (per['both_wheels'] >= 0.9)
    crit = {'alive': alive, 'sampled': counts > 0, 'vel': per['vel_error'] <= torch.maximum(torch.full_like(targets, 0.12), targets.abs() * 0.25), 'tilt': per['tilt'] <= 8, 'height': per['height_error'] <= 0.03, 'contact_window': per['both_wheels_scut_history'] >= 0.9, 'delta': per['delta'] <= 0.18, 'd2': per['d2'] <= 0.25}
    groups = []
    for group_index, target in enumerate(levels):
        ids = group_ids == group_index
        validrows = ids & (counts > 0)
        d = {'command_vx': target, 'environments': int(ids.sum()), 'survival_fraction': float(alive[ids].float().mean()), 'strict_pass': float(strict[ids].float().mean()), 'first_failure_step_mean': float(firstdone[ids].float().mean()), 'sampled_envs': int(validrows.sum())}
        d['profile'] = 'ramp_brake_reverse' if args.ramp_suite and group_index >= 6 else 'constant'
        d['fail_counts'] = {k: int((~m & (ids if k in ['alive', 'sampled'] else validrows)).sum()) for k, m in crit.items()}
        d['strict_pass_window'] = d['strict_pass']
        d['strict_pass_window_legacy_capture'] = d['strict_pass']
        d['strict_pass_integrated_mean'] = float(strict_integrated[ids].float().mean())
        d['strict_pass_window_5ms'] = float(strict_5ms[ids].float().mean())
        d['strict_pass_instant_legacy'] = float(strict_instant[ids].float().mean())
        if abs(args.steps * env.step_dt - 15.0) < 1e-06:
            d['survival_15s'] = d['survival_fraction']
        for k, v in per.items():
            d[k] = float(v[validrows].mean()) if validrows.any() else None
        groups.append(d)
    result = {'mode': 'reset_smoke' if args.reset_smoke else 'deterministic_policy', 'checkpoint': args.checkpoint, 'seed': args.seed, 'steps': args.steps, 'seconds': args.steps * env.step_dt, 'elapsed_s': time.time() - start, 'groups': groups, 'max_closure_after_grace_m': maxclosure, 'max_mimic_after_grace_rad': maxmimic, 'first_step_closure_max_m': max(reset_closures) if reset_closures else None, 'first_pose': first_pose, 'nonfinite': nonfinite, 'resets': resets, 'wheel_sensor_body_order': list(env.scene.sensors['wheel_contact'].body_names), 'gate_version': 'legacy_gate_preserved_with_integrated_and_endpoint_reporting_20260930', 'scut_contact_window': {'semantics': 'per-wheel peak over 3 samples >1N; not simultaneous continuous loading', 'configured_update_period_s': 0.005, 'actual_update_interval_s_prior_measured': 0.01, 'prior_evidence': 'contact_substep_diagnostic.json'}, 'metric_population': 'per-environment means after first 0.5 s, censored at FIRST termination; survival denominator includes all environments', 'physics_pass': not nonfinite and maxclosure < 0.002 and (maxmimic < 0.01)}
    result['per_environment'] = {k: v.detach().cpu().tolist() for k, v in per.items()}
    result['per_environment'].update(alive=alive.cpu().tolist(), group_ids=group_ids.cpu().tolist())
    result['strict_pass'] = result['physics_pass'] and all((g['strict_pass'] >= 0.8 for g in groups))
    result['speed_safety_pass'] = result['physics_pass'] and all((g['survival_fraction'] >= 0.95 and g['max_tilt'] is not None and (g['max_tilt'] <= 15) and (g['height_error'] <= 0.03) and (g['wheel_effort_clip_fraction'] <= 0.2) and (g['leg_effort_clip_fraction'] <= 0.2) and (g['longest_wheel_effort_clip_s'] <= 0.5) and (g['wheel_near_no_load'] <= 0.01) and (g['base_force'] <= 1.0) and (g['guide_force'] <= 1.0) for g in groups))
    result['speed_safety_pass_gain_compensated'] = result['physics_pass'] and all((g['survival_fraction'] >= 0.95 and g['max_tilt'] is not None and (g['max_tilt'] <= 15) and (g['height_error'] <= 0.03) and (g['wheel_rating_clip_fraction'] <= 0.2) and (g['leg_rating_clip_fraction'] <= 0.2) and (g['longest_wheel_rating_clip_s'] <= 0.5) and (g['wheel_near_no_load'] <= 0.01) and (g['base_force'] <= 1.0) and (g['guide_force'] <= 1.0) for g in groups))
    result['gain_compensated_clipping_semantics'] = 'actuator_local_order_v1: raw requested PD torque times episode and step gains minus final applied torque, all in the actuator joint order; includes pre/post gain hardware envelope clipping. 10ms snapshots, not substep peaks. Raw and unmapped gain shadow fields are retained.'
    result['rating_diagnostic_version'] = 'actuator_local_order_v1'
    result['actuator_joint_order'] = {k: list(robot.actuators[k].joint_names) for k in ('legs', 'wheels')}
    result['policy_joint_order'] = {'legs': task.LEG_ORDER, 'wheels': task.WHEEL_ORDER}
    result['speed_limit'] = args.speed_limit
    result['ramp_suite'] = args.ramp_suite
    result['effort_sampling'] = '10ms control-step snapshots, not substep peak audit; computed-minus-applied >0.1Nm counts clipping'
    result['contact_physical_metrics_semantics'] = {'force_and_low_load': 'captured every.5ms; longest both norm force<=1N; low force is not airborne', 'gap_and_slip': 'sampled each10ms control; input USD hull support excludes cooking/offset/compliance; lowest-vertex slip approximation, not contact manifold', 'group_values': 'means of per-environment summaries; individual arrays retained in per_environment, not worst cases', 'integration': 'mean force per5ms impulse bins is a reward adaptation; bin pass is not continuous contact or legacy graduation'}
    result['strict_pass_window'] = result['strict_pass']
    result['strict_pass_window_legacy_capture'] = result['strict_pass']
    result['strict_pass_integrated_mean'] = result['physics_pass'] and all((g['strict_pass_integrated_mean'] >= 0.8 for g in groups))
    result['strict_pass_window_5ms'] = result['physics_pass'] and all((g['strict_pass_window_5ms'] >= 0.8 for g in groups))
    result['contact_capture_metadata'] = getattr(env, '_contact_capture_metadata', {'enabled': False})
    result['graduation_gate_contact_source'] = 'legacy control-endpoint shadow; corrected 5ms stats do not automatically promote speed'
    result['height_credit_semantics'] = 'unweighted exp height * recent contact; weighted per control step = credit * 0.3 * 0.01'
    result['physical_contact_evidence'] = 'reports/contact_probe_7450_20260930/FINDINGS.md in source root; 2kHz unload/gap/slip retained there, not overwritten by window stats'
    result['strict_pass_instant_legacy'] = result['physics_pass'] and all((g['strict_pass_instant_legacy'] >= 0.8 for g in groups))
    result['mild_initial_parameters'] = mild_initial_parameters
    result['reset_joint_pos_before_physics'] = mild_initial_q
    result['reset_root_before_physics'] = mild_initial_root
    result['mild_final_parameters'] = env._mild_dr.audit() if hasattr(env, '_mild_dr') else None
    result.update(geometry_reference_version=geometry.reference_version, geometry_thresholds_changed=False)
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
    result['sensor_platform_sdk'] = dict(rows=getattr(env, '_platform_sensor_sdk', []), selected_reset=getattr(env, '_platform_sensor_reset', None), diagnostic_reset_only_for_10env=True)
    Path(args.output).write_text(json.dumps(result, indent=2))
    print('RESCUE_RESULT ' + json.dumps(result), flush=True)
    finalize_observer(env, result)
    return result
