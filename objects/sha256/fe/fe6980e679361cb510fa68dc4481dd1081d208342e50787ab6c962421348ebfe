"""MuJoCo physics + ONNX, driven exclusively by the separate operator window."""
from __future__ import annotations

import argparse
from dataclasses import fields
import json
from pathlib import Path
import time

import mujoco
import numpy as np

from drive_wasd import SPAWNS
from launcher import validate_model, validate_policy
from playback_ipc import CommandReader, atomic_json, slew
from sim_runtime import Mod4Sim, RuntimeConfig


def load_runtime(path, yaw_assist=0.):
    config = {} if path is None else json.loads(Path(path).read_text(encoding='utf-8'))
    allowed = {field.name for field in fields(RuntimeConfig)}
    if not isinstance(config, dict) or set(config) - allowed:
        raise ValueError('runtime JSON must contain only RuntimeConfig fields')
    if any(isinstance(v, bool) or not np.isfinite(float(v)) for v in config.values()):
        raise ValueError('runtime JSON contains a non-finite parameter')
    config = {key: float(value) for key, value in config.items()}
    config['yaw_assist_gain'] = yaw_assist  # always an explicit UI/CLI choice
    result = RuntimeConfig(**config)
    positive = ('policy_hz', 'leg_no_load', 'wheel_no_load', 'leg_effort', 'wheel_effort',
                'leg_stall', 'wheel_stall', 'crank_scale', 'hip_scale', 'wheel_scale')
    if any(getattr(result, key) <= 0 for key in positive) or result.diff_min >= result.diff_max:
        raise ValueError('invalid runtime scale, speed, effort or stop range')
    if min(result.leg_kp, result.leg_kd, result.wheel_kd, result.yaw_assist_gain) < 0:
        raise ValueError('negative controller gain')
    return result


def wheel_loads(sim):
    """Instantaneous world-Z net contact force, not a contact-duty ratio."""
    ids = [sim.model.jnt_bodyid[sim._joint(n)] for n in ('left_wheel_spin', 'right_wheel_spin')]
    loads = [0., 0.]
    for contact_id in range(sim.data.ncon):
        contact = sim.data.contact[contact_id]
        force = np.zeros(6)
        mujoco.mj_contactForce(sim.model, sim.data, contact_id, force)
        world = contact.frame.reshape(3, 3).T @ force[:3]
        for index, body_id in enumerate(ids):
            if sim.model.geom_bodyid[contact.geom1] == body_id:
                loads[index] -= float(world[2])
            if sim.model.geom_bodyid[contact.geom2] == body_id:
                loads[index] += float(world[2])
    return loads


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--policy', type=Path, required=True)
    parser.add_argument('--model', type=Path, required=True)
    parser.add_argument('--command-file', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--session-id', required=True)
    parser.add_argument('--runtime-config', type=Path)
    parser.add_argument('--yaw-assist', type=float, default=0.)
    parser.add_argument('--spawn', choices=[f'f{i}' for i in range(1, 9)], default='f1')
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--steps', type=int, default=0, help='optional bounded headless check')
    args = parser.parse_args()
    validate_policy(args.policy)
    validate_model(args.model)
    sim = Mod4Sim(args.model, args.policy, load_runtime(args.runtime_config, args.yaw_assist))
    _, x, y, yaw, ground = SPAWNS[int(args.spawn[1:]) - 1]
    sim.reset(x, y, yaw, ground)
    reader = CommandReader(args.command_file, args.session_id)
    viewer = None
    if not args.headless:
        from mujoco import viewer as mj_viewer
        # No vehicle key_callback: Viewer shortcuts cannot also drive the vehicle.
        viewer = mj_viewer.launch_passive(sim.model, sim.data, show_left_ui=False, show_right_ui=False)
        viewer.cam.type = mujoco.mjtCamera.mjCAMERA_TRACKING
        viewer.cam.trackbodyid = sim.chassis_id
        viewer.cam.distance, viewer.cam.azimuth, viewer.cam.elevation = 2.2, 145, -22
    reset_id, current, fault, steps = 0, 0., None, 0
    last, previous_delta = np.zeros(6), np.zeros(6)
    begin = next_tick = time.perf_counter()
    dt = 1. / sim.cfg.policy_hz
    try:
        while (viewer is None or viewer.is_running()) and (args.steps <= 0 or steps < args.steps):
            command = reader.read()
            if command['quit']:
                break
            if command['reset_id'] != reset_id:
                reset_id = command['reset_id']
                sim.reset(x, y, yaw, ground)
                current, fault = 0., None
                last[:] = previous_delta[:] = 0.
            delta, d2 = np.zeros(6), np.zeros(6)
            if not command['paused'] and not fault:
                current = slew(current, command['vx'], dt)
                sim.command.vx, sim.command.wz = current, command['wz']
                sim.command.height, sim.command.auto_mode, sim.command.mode = command['height'], False, 0
                try:
                    sim.step_control()
                    delta = sim.last_action - last
                    d2 = delta - previous_delta
                    last, previous_delta = sim.last_action.copy(), delta.copy()
                    if sim.closure_error() > .002:
                        fault = '闭链残差超过 2 mm'
                    elif sim.mimic_error() > .01:
                        fault = '耦合残差超过 0.01 rad'
                except FloatingPointError as error:
                    fault = str(error)
                steps += 1
            velocity = np.zeros(6)
            mujoco.mj_objectVelocity(sim.model, sim.data, mujoco.mjtObj.mjOBJ_BODY, sim.chassis_id, velocity, 1)
            health = sim.health()
            loads = wheel_loads(sim)
            packet = dict(session_id=args.session_id, updated_epoch=time.time(), engine='MuJoCo physics + ONNX',
                          policy=args.policy.name, sim_time_s=float(sim.data.time), command_vx=current,
                          target_vx=command['vx'], actual_vx=float(velocity[3]),
                          height_m=float(sim.base_position[2] - ground),
                          height_reference='root Z minus initial spawn ground (terrain height is not sampled)',
                          tilt_deg=float(np.degrees(np.arccos(np.clip(health['upright_cos'], -1, 1)))),
                          closure_mm=health['closure_error_m'] * 1000, mimic_rad=health['mimic_error_rad'],
                          delta=float(np.sqrt(np.mean(delta ** 2))), d2=float(np.sqrt(np.mean(d2 ** 2))),
                          left_wheel_load_n=loads[0], right_wheel_load_n=loads[1], fault=fault,
                          paused=command['paused'], stale_command=command['stale'],
                          yaw_assist_gain=sim.cfg.yaw_assist_gain,
                          realtime_ratio=steps * dt / max(.001, time.perf_counter() - begin))
            # Preserve the failure state even when it contains NaNs; JSON must stay valid.
            packet = {key: (None if isinstance(value, float) and not np.isfinite(value) else value)
                      for key, value in packet.items()}
            atomic_json(args.output, packet)
            if args.headless and fault:
                raise RuntimeError(fault)
            if viewer:
                viewer.sync()
            next_tick += dt
            time.sleep(max(0., next_tick - time.perf_counter()))
            if time.perf_counter() - next_tick > 1.:
                next_tick = time.perf_counter()
    finally:
        if viewer:
            viewer.close()


if __name__ == '__main__':
    main()
