"""NEW MuJoCo closed loop driven by resident C estimator/P25, not Python control.
MATH_TAU and GUARDED_TAU cohorts remain distinct. Sim driver still has inversePD,
processed-target D4, randomized PD/gain and signed-DC bounds. Logical clocks are
not host/ARM real-time proof. Python V4/P25 are SHADOW diagnostics only.
"""
from pathlib import Path
import argparse
import copy
import hashlib
import json
import math
import sys
import time
import traceback
import numpy as np
import mujoco
from physics_bridge import ROOT, OLD, MODEL_FILE, MODEL_SHA, FullDR, geometry, load_gain
from physics_bridge_v4_grade import BufferedImuPlant
from sensor_core_v4 import StateEstimator
from ground_controller_v4 import GroundController

HOST = ROOT / 'SPR_AUDIT/HOST_CLOSED_LOOP_IO_V1'
sys.path.insert(0, str(HOST))
from p25_stdio import P25Local, DEFAULT, from_v4_packet


def dump(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)


def execute(config, output):
    assert (HOST / 'INDEX.json').is_file(), 'wait for resident adapter seal'
    output = output.resolve()
    assert output.is_relative_to(ROOT)
    output.mkdir(parents=True, exist_ok=False)
    dump(output / 'config.json', config)
    rows = []
    source_files = [Path(__file__), ROOT / 'physics_bridge.py', ROOT / 'physics_bridge_v3.py',
                    ROOT / 'physics_bridge_v4_grade.py', ROOT / 'sensor_core_v4.py',
                    ROOT / 'ground_controller_v4.py', ROOT / 'nominal_gain_v1.json',
                    ROOT / 'MODEL_AUDIT' / MODEL_FILE, OLD / 'dr_components.py',
                    HOST / 'p25_stdio.py', HOST / 'PROTOCOL_SCHEMA.json',
                    HOST / 'DEFAULT_INIT_P25.json', HOST / 'INDEX.json',
                    HOST / 'p25_host_adapter.exe']
    sources = []
    for path in source_files:
        data = path.read_bytes()
        sources.append(dict(path=str(path), bytes=len(data), SHA=hashlib.sha256(data).hexdigest()))
    dump(output / 'SOURCE_MANIFEST.json', dict(kind='NEW_C_P25_PHYSICAL_LOOP', files=sources,
         robot_model_SHA=MODEL_SHA, engine=mujoco.__version__, hardware_binding=False))
    plant = None
    client = None
    trace_hash = hashlib.sha256()
    trace_bytes = 0
    started = time.perf_counter()
    trace = (output / 'trace.jsonl').open('xb')
    try:
        gain = load_gain(ROOT / 'nominal_gain_v1.json')
        plant = BufferedImuPlant(False)
        dr = FullDR(int(config['seed']), nominal=bool(config.get('nominal', False)))
        dr_receipt = plant.attach_dr(dr)
        plant.reset(gain['symmetric'], 0.)
        shadow_chart = geometry()
        shadow_chart.radius = float(config.get('kinematic_radius_m', .0625))
        shadow_estimator = StateEstimator(shadow_chart, plant.imu_offset, upright_prior=True,
                                         accel_reference='wheel_midpoint', innovation_limit=1.)
        shadow_controller = GroundController(gain, dict(position_weight=25., position_leash=1.,
             yaw_kp=.8, yaw_ki=.5, yaw_integral_limit=15., yaw_rate_ff=.052))
        init = copy.deepcopy(DEFAULT)
        init['OFFSET'] = plant.imu_offset.tolist()
        init['RADIUS'] = float(config.get('kinematic_radius_m', .0625))
        client = P25Local(timeout_s=3., stderr_path=output / 'resident_stderr.log')
        ack = client.initialize(init)
        dump(output / 'INIT_ACK.json', ack)
        quality_history = {}
        duration = float(config.get('duration_s', 12.))
        count = round(duration / .01)
        selected_field = config['torque_domain']
        assert selected_field in ('MATH_TAU', 'GUARDED_TAU')
        complete = False
        stop = 'complete'
        for index in range(count):
            now = float(plant.d.time)
            now_us = int(round(now * 1e6))
            samples = int(plant.imu_window_count)
            if samples:
                aperture = int(round(samples * plant.dt * 1e6))
                quality = dict(sequence=index + 1, window_begin_us=now_us - aperture,
                    mean_weight_sum_us=aperture, expected_count=samples, valid_count=samples,
                    dropped_count=0, mean_mode=1, mean_valid=True, mean_weights_valid=True)
            else:
                quality = dict(sequence=index + 1, window_begin_us=now_us,
                    mean_weight_sum_us=0, expected_count=1, valid_count=1, dropped_count=0,
                    mean_mode=0, mean_valid=True, mean_weights_valid=False)
            quality_history[now_us] = quality
            packet = plant.sensor_packet()
            sampled_us = int(round(packet.time_s * 1e6))
            assert sampled_us in quality_history, 'known D3 queue source epoch required'
            # Repeated startup source epoch reuses ORIGINAL instant/count/sequence metadata.
            wire_packet = from_v4_packet(packet, **quality_history[sampled_us])
            forward = float(config.get('forward_m_s', 0.)) if now >= 1. else 0.
            if config.get('brake_at_s') is not None and now >= config['brake_at_s']:
                forward = 0.
            command = dict(issued_us=now_us, expires_us=now_us + 10000, sequence=index + 1,
                           flags=1, enable=1, forward_m_s=forward, yaw_rad_s=0.)
            dq = packet.joint_vel4
            spins = packet.wheel_vel2
            drive = dict(sampled_us=sampled_us, flags=1,
                         velocity_row6=[dq[0], dq[1], spins[0], dq[2], dq[3], spins[1]])
            rpc_start = time.perf_counter_ns()
            reply = client.step(wire_packet, command, drive, now_us)
            rpc_ms = (time.perf_counter_ns() - rpc_start) * 1e-6
            assert reply['valid'] and reply['ENQUEUE_DELTA'] == 1 and reply['DISABLE_DELTA'] == 0
            estimate_py = shadow_estimator.update(packet)
            tau_py = shadow_controller.command(estimate_py, forward, 0.)
            tau = np.asarray(reply[selected_field], float)
            grade_before = plant.grade()
            plant.apply_torque_request(tau, packet)
            grade = plant.grade()
            row = dict(time=float(plant.d.time), estimate_time=now, request=[forward, 0.],
                selected_tau_domain=selected_field, raw_requested_tau=tau.tolist(),
                actual_tau=plant.d.ctrl.tolist(), c_reply=reply, rpc_wall_ms=rpc_ms,
                packet=wire_packet, command=command, drive=drive,
                estimated14=reply['STATE14'], estimated_roll=reply['ROLL'],
                shaped=[reply['SHAPER_V'], reply['SHAPER_W']],
                python_shadow_state14=estimate_py.state14.tolist(), python_shadow_tau=tau_py.tolist(),
                state14_C_minus_Py=(np.asarray(reply['STATE14']) - estimate_py.state14).tolist(),
                math_tau_C_minus_Py=(np.asarray(reply['MATH_TAU']) - tau_py).tolist(),
                pre_minus_guarded_tau=(np.asarray(reply['MATH_TAU']) - reply['GUARDED_TAU']).tolist(),
                physics_wheel_mean_force_N2=(plant.last_control_wheel_impulse / .01).tolist(),
                physics_nonwheel_contact_ticks=plant.last_control_nonwheel_ticks,
                ground_truth_before=grade_before, ground_truth=grade)
            encoded = (json.dumps(row, separators=(',', ':'), allow_nan=False) + '\n').encode('utf-8')
            trace.write(encoded)
            trace_hash.update(encoded)
            trace_bytes += len(encoded)
            rows.append(row)
            if not grade['finite'] or grade['closure'] > .01 or grade['mimic'] > .01 or grade['upright_cos'] < .45:
                stop = 'health'
                break
        else:
            complete = True
        trace.close()
        client.close()
        tail = [r for r in rows if r['time'] >= max(1., duration - 2.)] or rows
        truth_v = np.array([r['ground_truth']['body_velocity'][0] for r in tail])
        truth_w = np.array([(r['ground_truth']['gyro_true'][1] * math.sin(r['ground_truth']['roll_true']) +
                   r['ground_truth']['gyro_true'][2] * math.cos(r['ground_truth']['roll_true'])) /
                   max(math.cos(r['ground_truth']['pitch_true']), .15) for r in tail])
        refs = np.array([r['shaped'] for r in tail])
        vrms = float(np.sqrt(np.mean((truth_v - refs[:, 0])**2)))
        wrms = float(np.sqrt(np.mean((truth_w - refs[:, 1])**2)))
        pose = all(abs(r['ground_truth']['roll_true']) < math.radians(10) and
                   abs(r['ground_truth']['pitch_true']) < math.radians(10) for r in tail)
        support = np.mean([r['physics_wheel_mean_force_N2'] for r in tail], axis=0)
        nonwheel = sum(r['physics_nonwheel_contact_ticks'] for r in rows)
        passed = bool(complete and pose and vrms < .15 and wrms < .1 and nonwheel == 0 and
                      np.min(support) > .2 * plant.mass * 9.81)
        result = dict(kind='C_P25_CLOSEDLOOP_HOST_SIM_ONLY_NOT_BSP_ARM_RELEASE', config=config,
            complete=complete, stop_reason=stop, proposed_gate_passed=passed,
            kinematic_radius_m=init['RADIUS'], collision_circumradius_m=.06369999796152115,
            radius_scope='publichardware_nominalspecnotmeasuredrollingcalibration; collisiongeometryunchanged',
            torque_domain=selected_field,
            C_final_dispatch_selected_for_actuation=selected_field == 'GUARDED_TAU',
            MATH_cohort_scope='C estimator/LQR prefix fidelity through original already-bounded sim driver; not claiming final C guarded enqueue actuation',
            actual_feedback='sensor_packets_only',
            python_control_is_shadow_only=True, truth_used_for_control=False,
            controls=len(rows), physics_callbacks=plant.tick_phys, duration_actual_s=float(plant.d.time),
            model_SHA=MODEL_SHA, DR=dr_receipt, queue_receipt=dr.queue_receipt(),
            tail_velocity_mean_m_s=float(truth_v.mean()), tail_v_tracking_RMSE=vrms,
            tail_w_tracking_RMSE=wrms, tail_mean_force_N2=support.tolist(),
            physics_nonwheel_contact_ticks=nonwheel,
            max_closure=max(r['ground_truth']['closure'] for r in rows),
            max_mimic=max(r['ground_truth']['mimic'] for r in rows),
            max_math_tau_C_minus_Py_Nm=float(np.max(np.abs([r['math_tau_C_minus_Py'] for r in rows]))),
            max_state14_C_minus_Py=float(np.max(np.abs([r['state14_C_minus_Py'] for r in rows]))),
            max_pre_minus_guarded_tau_Nm=float(np.max(np.abs([r['pre_minus_guarded_tau'] for r in rows]))),
            rpc_wall_ms_max=max(r['rpc_wall_ms'] for r in rows),
            rpc_wall_ms_p99=float(np.quantile([r['rpc_wall_ms'] for r in rows], .99)),
            clocks='logical simulation microseconds, NOT measured host/ARM deadline',
            host_RPC_timing_is_only_observed=True, hardware_binding=False, BSP=False, ARM_runtime=False,
            root_assist_forces=0, root_state_writes_after_initialization=0,
            window_metadata='derived from actual simulator 20x0.5ms collector source per acquisition epoch; D3 metadata follows returned epoch; not real CAN sampling proof',
            resident_exit=client.process.returncode, wall_s=time.perf_counter() - started,
            trace_artifact=dict(path=str(output / 'trace.jsonl'), bytes=trace_bytes,
                                SHA=trace_hash.hexdigest(), producer_streamed_once=True))
        dump(output / 'result.json', result)
        print(json.dumps({k: v for k, v in result.items() if k not in ('DR', 'queue_receipt')}, indent=2))
        return result
    except BaseException:
        trace.close()
        dump(output / 'ERROR.json', dict(error=traceback.format_exc(), controls=len(rows),
             physics_callbacks=None if plant is None else plant.tick_phys,
             trace_prefix=dict(path=str(output / 'trace.jsonl'), bytes=trace_bytes,
                               SHA=trace_hash.hexdigest()), no_silent_restart=True))
        raise
    finally:
        if client is not None:
            client.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    execute(json.loads(args.config.read_bytes()), args.out)
