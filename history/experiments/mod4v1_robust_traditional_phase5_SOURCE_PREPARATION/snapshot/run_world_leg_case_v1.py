"""FinitefreshMOD4v1case: fullMuJoCo, sensorcontrollerseparatedfromtruthgrading.
Eachunusedoutputname is onepurpose; snapshots/errors/failedtraces are retained.
"""
from pathlib import Path
import json, sys, time, math, argparse, hashlib, traceback
import numpy as np, mujoco
from physics_bridge import RobustPlant, FullDR, geometry, load_gain, MODEL_SHA, MODEL_FILE, ROOT, MODEL_WHEEL_RADIUS, OLD
from ROUGH_WORLD_LEG_V1.controller import WorldLegController as GroundController
from streamed_trace_rows_v1 import StreamedRows
from sensor_core_v4 import StateEstimator, Estimate, wrap
from physics_bridge_rm_grade_v1 import BufferedImuPlant as RobustPlant

def dump(p, v):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(v, f, indent=2, allow_nan=False)
from rm_grid_terrain_v1 import configure

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_bytes())
    out = args.out.resolve()
    assert out.is_relative_to(ROOT)
    out.mkdir(parents=True, exist_ok=False)
    dump(out / 'config.json', cfg)
    started = time.perf_counter()
    rows = StreamedRows(out / 'trace.jsonl')
    p = None
    complete = False
    try:
        sources = []
        for f in [Path(__file__), ROOT / 'ROUGH_WORLD_LEG_V1/controller.py', ROOT / 'streamed_trace_rows_v1.py', ROOT / 'physics_bridge.py', ROOT / 'sensor_core_v4.py', ROOT / 'ground_controller_v4.py', ROOT / 'physics_bridge_v3.py', ROOT / 'rm_grid_terrain_v1.py', ROOT / 'physics_bridge_rm_grid_v1.py', ROOT / 'physics_bridge_rm_buffer_v1.py', ROOT / 'physics_bridge_rm_grade_v1.py', ROOT / 'MODEL_AUDIT/mesh_support_helper_v1/mesh_support.py', ROOT / 'nominal_gain_v1.json', ROOT / cfg['gain_file'], ROOT / 'MODEL_AUDIT' / MODEL_FILE, OLD / 'full_lqr.py', OLD / 'control_core.py', OLD / 'kinematics.py', OLD / 'dr_components.py']:
            raw = f.read_bytes()
            sources.append(dict(path=str(f), bytes=len(raw), SHA=hashlib.sha256(raw).hexdigest()))
        dump(out / 'SOURCE_MANIFEST.json', dict(kind='NEW_FRESHCASE_FULLMODEL_NO_PPO', model_SHA=MODEL_SHA, files=sources, engine=mujoco.__version__, python=sys.version, scope='diagnostic/screening, nohardwarequalification'))
        g = load_gain(ROOT / cfg['gain_file'])
        configure(int(cfg.get('terrain_seed', 9001)), float(cfg.get('terrain_difficulty', 1.0)))
        p = RobustPlant(False, tuple(cfg.get('imu_offset_m', [0.03, 0, 0.04])))
        dr = FullDR(int(cfg['seed']), nominal=bool(cfg.get('nominal', False)))
        drreceipt = p.attach_dr(dr)
        p.reset(g['symmetric'], float(cfg.get('start_x_m', 0.8)))
        estimator = StateEstimator(geometry(), p.imu_offset, accel_correction=float(cfg.get('accel_correction', 1.5)), wheel_std=float(cfg.get('wheel_std', 0.065)), accel_reference=cfg.get('accel_reference', 'wheel_midpoint'), innovation_limit=float(cfg.get('accel_innovation_limit', 1.0)), upright_prior=bool(cfg.get('upright_arming_prior', True)))
        controller = GroundController(g, cfg.get('controller', {}))
        truth_mode = False
        truth_yaw = 0.0
        truth_distance = 0.0
        last_yaw = 0.0
        truth_x0 = float(p.d.qpos[0])
        duration = float(cfg.get('duration_s', 6.0))
        N = round(duration / 0.01)
        mode = cfg.get('mode', 'stand')
        stop = 'complete'
        commands = []
        maxclosure = 0.0
        maxmimic = 0.0
        maxroll = 0.0
        maxpitch = 0.0
        nonwheel_controls = 0
        for k in range(N):
            t = float(p.d.time)
            chain_start = time.perf_counter_ns()
            packet = p.sensor_packet()
            estimate = estimator.update(packet)
            active = t >= float(cfg.get('command_at_s', 1.0))
            forward = float(cfg.get('forward_m_s', 2.0)) if active and mode in ('forward', 'combined') else 0.0
            yaw_rate = float(cfg.get('yaw_rad_s', 4 * math.pi)) if active and mode in ('spin', 'yaw_step', 'combined') else 0.0
            if cfg.get('brake_at_s') is not None and t >= cfg['brake_at_s']:
                forward = 0.0
                yaw_rate = 0.0
            tau = controller.command(estimate, forward, yaw_rate)
            chain_ms = (time.perf_counter_ns() - chain_start) * 1e-06
            grade_before = p.grade()
            p.apply_torque_request(tau, packet, mechanical_power_limit=cfg.get('mechanical_power_limit_W'))
            grade = p.grade()
            maxclosure = max(maxclosure, float(grade['closure']))
            maxmimic = max(maxmimic, float(grade['mimic']))
            maxroll = max(maxroll, abs(float(grade['roll_true'])))
            maxpitch = max(maxpitch, abs(float(grade['pitch_true'])))
            wheelF = np.zeros(2)
            nonwheel = 0
            ground = p.m.geom('ground').id
            for ci, ct in enumerate(p.d.contact):
                a, b = (int(ct.geom1), int(ct.geom2))
                if ground not in (a, b):
                    continue
                force = np.zeros(6)
                mujoco.mj_contactForce(p.m, p.d, ci, force)
                if force[0] <= 1:
                    continue
                other = b if a == ground else a
                if other in p.tires:
                    wheelF[p.tires.index(other)] += force[0]
                else:
                    nonwheel += 1
            nonwheel_controls += bool(nonwheel)
            row = dict(world_leg_reference=dict(controller.world_log), time=float(p.d.time), estimate_time=t, chain_compute_ms=chain_ms, ground_truth_before=grade_before, physics_wheel_mean_force_N2=(p.last_control_wheel_impulse / 0.01).tolist(), physics_nonwheel_contact_ticks=p.last_control_nonwheel_ticks, request=[forward, yaw_rate], shaped=[float(controller.ref[7]), float(controller.ref[8])], estimated14=estimate.state14.tolist(), estimated_roll=float(estimate.roll), sensor_age_s=estimate.sensor_age_s, sensor_timestamp_s=packet.time_s, raw_gyro=packet.gyro_body.tolist(), raw_accel=packet.accel_proper_body.tolist(), encoder4=packet.joint_pos4.tolist(), encoder_rate4=packet.joint_vel4.tolist(), wheel_rate2=packet.wheel_vel2.tolist(), raw_requested_tau=tau.tolist(), actual_tau=p.d.ctrl.tolist(), ground_truth=grade, wheel_support_N2=wheelF.tolist(), nonwheel_ground_contact=nonwheel, velocity_variance=estimate.velocity_variance, slip_innovation=estimate.slip_innovation, contact_proxy=estimate.contact_confidence)
            rows.append(row)
            if not grade['finite'] or grade['closure'] > 0.01 or grade['mimic'] > 0.01 or (grade['upright_cos'] < 0.45):
                stop = 'health'
                break
        else:
            complete = True
        elapsed = float(p.d.time)
        assert p.tick_phys == len(rows) * 20 and abs(elapsed - len(rows) * 0.01) < 1e-07
        tail = [r for r in rows if r['time'] >= max(1.0, duration - 2.0)]
        score_rows = tail or rows
        v = np.array([r['ground_truth']['body_velocity'][0] for r in score_rows])
        w = np.array([(r['ground_truth']['gyro_true'][1] * math.sin(r['ground_truth']['roll_true']) + r['ground_truth']['gyro_true'][2] * math.cos(r['ground_truth']['roll_true'])) / max(math.cos(r['ground_truth']['pitch_true']), 0.15) for r in score_rows])
        pitch = np.array([r['ground_truth']['pitch_true'] for r in score_rows])
        roll = np.array([r['ground_truth']['roll_true'] for r in score_rows])
        ref = np.array([r['shaped'] for r in score_rows])
        ev = np.array([r['estimated14'][7] - r['ground_truth_before']['body_velocity'][0] for r in score_rows])
        ep = np.array([r['estimated14'][2] - r['ground_truth_before']['pitch_true'] for r in score_rows])
        heading = np.unwrap([r['ground_truth']['yaw_true'] for r in rows])
        actual_yaw_turns = float((heading[-1] - heading[0]) / (2 * math.pi))
        position_start = np.asarray(rows[0]['ground_truth']['xyz'])
        position_end = np.asarray(rows[-1]['ground_truth']['xyz'])
        drift = float(np.linalg.norm(position_end[:2] - position_start[:2]))
        vrmse = float(np.sqrt(np.mean((v - ref[:, 0]) ** 2)))
        wrmse = float(np.sqrt(np.mean((w - ref[:, 1]) ** 2)))
        upright_tail = bool(np.all(abs(roll) < math.radians(10)) and np.all(abs(pitch) < math.radians(10)))
        proposed_gate = bool(complete and upright_tail and (vrmse < 0.15) and (wrmse < 0.1 * max(1.0, float(abs(ref[:, 1]).max()))) and (maxclosure <= 0.01) and (maxmimic <= 0.01))
        if mode == 'spin':
            proposed_gate = proposed_gate and drift < 0.3
        support_mean = np.mean([r['physics_wheel_mean_force_N2'] for r in score_rows], axis=0)
        physics_nonwheel = sum((r['physics_nonwheel_contact_ticks'] for r in rows))
        supported_impulse = bool(np.all(support_mean > 0.2 * p.mass * 9.81))
        proposed_gate = bool(proposed_gate and supported_impulse and (physics_nonwheel == 0))
        result = dict(kind='R40_NEW_WORLD_LEG_REFERENCE_SENSOR_ONLY_COUNTERFACTUAL', upright_arming_prior=bool(cfg.get('upright_arming_prior', True)), initial_orientation_scope='Supporteduprightcasearmingprior; NOTarbitraryunknownattitudequalification', sensor_frontend='2kHzIMUandencoderrateboxcar_to100Hz_thenD1noise_D3delay; explicitnewfrontend', highrate_IMU_samples=p.total_highrate_IMU_samples, attitude_accel_reference=cfg.get('accel_reference', 'wheel_midpoint'), initial_mesh_support=p.initial_mesh_support, tail_physics_mean_wheel_force_N2=support_mean.tolist(), physics_nonwheel_contact_ticks=physics_nonwheel, impulse_support_gate=supported_impulse, whole_sensor_control_chain_ms_max=max((r['chain_compute_ms'] for r in rows)), whole_sensor_control_chain_ms_p99=float(np.quantile([r['chain_compute_ms'] for r in rows], 0.99)), config=cfg, model_SHA=MODEL_SHA, nominal=dr.nominal, DR=drreceipt, queue_receipt=dr.queue_receipt(), source_root_state_writes_after_initialization=0, root_assist_forces=0, full_D0_D7_on_control_path=not dr.nominal and (not truth_mode), legacy_gravity3_channel_is_raw_minus_accel_over_g_not_truth_gravity=True, actual_feedback=cfg.get('feedback', 'sensors'), truth_used_for_control=truth_mode, terrain='SCUT_tiny_step_exact_box_family_not_full_RM_arena', mode=mode, physics_callbacks=p.tick_phys, controls=len(rows), duration_actual_s=elapsed, control_dt_s=0.01, physics_dt_s=0.0005, stop_reason=stop, complete=complete, tail_sample_count=len(score_rows), tail_velocity_mean_m_s=float(v.mean()), tail_yawrate_mean_rad_s=float(w.mean()), tail_v_tracking_RMSE=vrmse, tail_w_tracking_RMSE=wrmse, tail_pitch_RMS=float(np.sqrt(np.mean(pitch * pitch))), tail_roll_RMS=float(np.sqrt(np.mean(roll * roll))), estimator_velocity_RMSE=float(np.sqrt(np.mean(ev * ev))), estimator_pitch_RMSE=float(np.sqrt(np.mean(ep * ep))), actual_yaw_turns=actual_yaw_turns, xy_displacement_m=drift, max_pitch_abs=maxpitch, max_roll_abs=maxroll, max_closure=maxclosure, max_mimic=maxmimic, nonwheel_ground_contact_control_samples=int(nonwheel_controls), peak_positive_mechanical_power_W=p.max_mechanical_power, power_scope='Mechanicalonly; copper/bus/thermalparametersunbound; notelectricalqualification', max_actual_tau6=p.max_applied_tau.tolist(), max_controller_compute_ms=controller.max_solve_ms, command_envelope_clips=controller.envelope_clips, proposed_engineering_gate_not_user_ratified=True, proposed_gate_passed=proposed_gate, real_robot_or_board_claim=False, world_truth_control_bypasses=truth_mode, imu_offset_scope='Explicitvirtualtestextrinsic; notconfirmedphysicalmount', collision_radius_m=MODEL_WHEEL_RADIUS, nominal_hardware_radius_spec_m=0.0625, actuation_mapping='OriginalinversePDprocessedtargets/DR; finalDMCANbindingnotyetconfirmed', wall_s=time.perf_counter() - started)
        result['yaw_score_frame'] = 'EulerheadingratefrombodygyroandtrueRPY, notbodygyro_zalone'
        result['cohort'] = cfg.get('cohort', 'train')
        trace_hash = hashlib.sha256()
        trace_bytes = 0
        trace_hash = rows.sha
        trace_bytes = rows.bytes
        result['scene'] = p.scene_metadata
        result['rough_progress_m'] = float(p.d.qpos[0] - float(cfg.get('start_x_m', 0.8)))
        result['rough_max_y_m'] = float(max((abs(rr['ground_truth']['xyz'][1]) for rr in rows)))
        result['rough_case_pass'] = bool(result['proposed_gate_passed'] and result['rough_progress_m'] >= 6.5 and (result['rough_max_y_m'] <= 0.3) and (float(p.d.qpos[0]) < 8.8))
        result['trace_artifact'] = {'path': str(out / 'trace.jsonl'), 'bytes': trace_bytes, 'SHA': trace_hash.hexdigest(), 'producer_streamed_once': True}
        dump(out / 'result.json', result)
        print(json.dumps({k: v for k, v in result.items() if k not in ('DR', 'queue_receipt')}, indent=2))
        print('RESULT', out / 'result.json')
    except BaseException:
        dump(out / 'ERROR.json', dict(error=traceback.format_exc(), controls=len(rows), physics_callbacks=p.tick_phys if p is not None else None, trace_prefix=dict(path=str(rows.path), bytes=rows.bytes, SHA=rows.sha.hexdigest()), original_error_preserved=True, no_samepurpose_retry=True))
        raise
if __name__ == '__main__':
    main()
