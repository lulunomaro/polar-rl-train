"""Sensor-only control engine for the RM/FPS player; GUI truth is display only.
The robot/PD/DC path is reused unchanged. Explicit operator reset is not standup.
"""
from pathlib import Path
import sys
import json
import math
import numpy as np
import mujoco

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import physics_bridge as bridge
from physics_bridge_v3 import BufferedImuPlant
from sensor_core_jump_v1 import StateEstimator, quat_mul, quat_from_rpy
from FLAT_STABILITY_FIX_V1.controller_v2 import GroundController
from RM_FPS_PLAYER_V1 import terrain
from RM_FPS_PLAYER_V1.jump import JumpAction


class Engine:
    def __init__(self, scene='rm_all', difficulty=.5, seed=9001, full_dr=False, controller_mode='coord_soft'):
        if controller_mode not in ('coord_soft', 'c2_fps'):
            raise ValueError('Unknown controller mode: '+str(controller_mode))
        self.controller_mode = controller_mode
        self.gain = bridge.load_gain(ROOT / 'nominal_gain_v1.json')
        self.pack = json.loads((ROOT / 'NORMAL_P25_HOLDOUT_V1/CONTROLLER_PACK.json').read_bytes())
        self.scene_name, self.difficulty, self.seed = scene, float(difficulty), int(seed)
        model, self.meta = terrain.build_model(scene, self.difficulty, self.seed)
        # Constructor-local factory injection; no source patch and no other physics
        # thread uses this process. The existing actuator/sensor methods are retained.
        original = bridge.model_factory
        try:
            bridge.model_factory = lambda *args, **kwargs: model
            self.plant = BufferedImuPlant(False, (.03, 0., .04))
        finally:
            bridge.model_factory = original
        self.full_dr = bool(full_dr)
        self.zone = 0
        self.reset(0)

    def reset(self, zone=None):
        if zone is not None:
            self.zone = int(zone)
        zones = self.meta['zones']
        self.zone = max(0, min(self.zone, len(zones)-1))
        spawn = zones[self.zone]['spawn']
        p = self.plant
        self.dr_meta = p.attach_dr(bridge.FullDR(self.seed, nominal=not self.full_dr))
        p.reset(self.gain['symmetric'], float(spawn[0]))
        p.d.qpos[1] = float(spawn[1])
        p.d.qpos[2] += float(spawn[2]) if len(spawn) > 2 else 0.
        self.spawn_yaw = float(zones[self.zone].get('yaw', 0.))
        p.d.qpos[3:7] = quat_mul(quat_from_rpy(0., 0., self.spawn_yaw), p.d.qpos[3:7])
        p.d.time = 0.
        p.tick_phys = 0
        p.previous_torque = None
        p.last_packet = None
        mujoco.mj_forward(p.m, p.d)
        p.initial = p.d.qpos.copy()
        geom = bridge.geometry()
        self.estimator = StateEstimator(geom, p.imu_offset, accel_correction=1.5,
            wheel_std=.065, accel_reference='wheel_midpoint', innovation_limit=1., upright_prior=True)
        if self.controller_mode == 'c2_fps':
            # C2 = C1 leg following + the existing FPS heading loop.
            # Player.controls already closes heading at3/s; do not cascade it twice.
            from RM_ROBUSTNESS_V1.controller_roll_follow_v1 import GroundController as RollFollow
            self.controller = RollFollow(self.gain, self.pack['controller'], variant='coord_soft', geometry=geom)
        else:
            self.controller = GroundController(self.gain, self.pack['controller'], variant='coord_soft')
        self.controller.K = np.asarray(self.pack['K_6x14'], float)
        self.jump = JumpAction(self.gain, geom, self.controller)
        self.estimate = None
        self.packet = None
        self.last_tau = np.zeros(6)
        self.controls = 0
        self.fault = ''
        self.paused = False
        self.target = (0., 0.)
        self.phase = 'BALANCE'
        self.jump_message = ''

    def request_jump(self):
        if self.estimate is None or self.paused:
            self.jump_message = '先运行并站稳，再跳跃'
            return False
        result = bool(self.jump.request(float(self.plant.d.time), self.estimate, self.packet))
        self.jump_message = '试验跳跃已触发' if result else str(getattr(self.jump, 'fault_reason', '') or '先松键刹稳：速度≤0.2m/s，俯仰/横滚≤8.6°，动作完成后再跳')
        return result

    def tick(self, forward=0., yaw_rate=0.):
        if self.paused:
            return
        p = self.plant
        try:
            now = float(p.d.time)
            self.jump.prepare(self.estimator, now)
            packet = p.sensor_packet()
            e = self.estimator.update(packet)
            was_active = bool(self.jump.active)
            v, w = (0., 0.) if was_active else (float(forward), float(yaw_rate))
            tau = self.controller.command(e, v, w)
            jumping = self.jump.command(e, packet, now, tau)
            if self.jump.fault_reason:
                self.fault = 'JUMP INHIBIT: '+str(self.jump.fault_reason)
                self.paused = True
                self.phase = 'INHIBIT'
                self.packet, self.estimate = packet, e
                self.last_tau = np.zeros(6)
                print(self.fault, flush=True)
                return
            if jumping is not None:
                tau = np.asarray(jumping, float)
            if was_active and not self.jump.active:
                # Re-acquire controller references only; never reset the estimator.
                self.controller.ref[:2] = e.state14[:2]
                self.controller.park_error = 0.
                self.controller.previous = np.asarray(tau).copy()
            self.packet, self.estimate = packet, e
            self.last_tau = np.asarray(tau, float).copy()
            self.target = (v, w)
            p.apply_torque_request(self.last_tau, packet)
            self.controls += 1
            self.phase = str(self.jump.phase) if self.jump.active else 'BALANCE'
            if not np.isfinite(p.d.qpos).all() or abs(float(e.state14[2])) > 1.3 or abs(float(e.roll)) > 1.0:
                self.fault = '姿态越界 / FALL：按 R 复位'
                self.phase = 'FALL_PAUSED'
                self.paused = True
        except (ValueError, FloatingPointError) as exc:
            self.fault = str(exc)
            self.paused = True
            print('CONTROL_FAULT: '+str(exc), flush=True)

    def estimated_yaw(self):
        return float(self.estimate.state14[1]) if self.estimate is not None else 0.
