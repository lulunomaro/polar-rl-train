"""Measured airborne pitch/roll feedback through the original six motor servos."""
from pathlib import Path
import argparse
import hashlib
import json
import math

import numpy as np
import torch

import base_jump as base

T = Path(__file__).resolve().parent


class AirBalance(base.Maneuver):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        m = self.sim.env.m
        self.wheel_dofs = [int(m.joint(n).dofadr[0])
                           for n in ('left_wheel_joint', 'right_wheel_joint')]
        self.balance_active = False
        self.pitch_torque_request = 0.
        self.roll_offset = 0.
        self.leg_pitch_offset = 0.
        self.last_air_leg_pitch = 0.
        self.air_exit_started = None
        self.wheel_target = np.zeros(2)

    def __call__(self, obs):
        result = super().__call__(obs)
        self.balance_active = False
        self.pitch_torque_request = 0.
        self.roll_offset = 0.
        self.leg_pitch_offset = 0.
        self.wheel_target = result[0, 4:].detach().numpy()*10.
        if not self.cfg.get('air_balance', False):
            return result
        if self.phase not in ('flight_extend', 'flight_tuck', 'landing_extend') or not self.unsupported():
            duration = self.cfg.get('leg_exit_s', 0.)
            if duration > 0. and self.last_air_leg_pitch != 0.:
                now = float(self.sim.env.d.time)
                if self.air_exit_started is None:
                    self.air_exit_started = now
                alpha = min(1., (now-self.air_exit_started)/duration)
                self.leg_pitch_offset = self.last_air_leg_pitch*(1.-alpha)
                result = result.clone()
                result[:, :4] += 2.*self.leg_pitch_offset
                if alpha >= 1.:
                    self.last_air_leg_pitch = 0.
            return result
        e = self.sim.env
        rotation = e.d.xmat[e.base_id].reshape(3, 3)
        pitch = math.asin(float(np.clip(-rotation[2, 0], -1., 1.)))
        roll = math.atan2(float(rotation[2, 1]), float(rotation[2, 2]))
        wx, wy = float(e.d.qvel[3]), float(e.d.qvel[4])
        body_pitch_torque = -self.cfg['pitch_kp']*pitch-self.cfg['pitch_kd']*wy
        motor_torque_each = -.5*body_pitch_torque
        qd = e.d.qvel[self.wheel_dofs]
        target = qd+motor_torque_each/.6
        result = result.clone()
        result[0, 4:] = torch.as_tensor(target/10., dtype=result.dtype, device=result.device)
        correction = self.cfg.get('roll_kp', 0.)*roll+self.cfg.get('roll_kd', 0.)*wx
        correction = float(np.clip(correction, -.15, .15))
        new_delta = np.clip(self.target+np.array([-correction, correction]), *base.BOUNDS)
        for i, (front, rear) in enumerate(((0, 1), (2, 3))):
            change = new_delta[i]-self.target[i]
            result[:, front] += change
            result[:, rear] -= change
        leg_pitch = self.cfg.get('leg_pitch_kp', 0.)*pitch+self.cfg.get('leg_pitch_kd', 0.)*wy
        leg_pitch = float(np.clip(leg_pitch, -.35, .35))
        result[:, :4] += 2.*leg_pitch
        self.target = new_delta
        self.balance_active = True
        self.pitch_torque_request = body_pitch_torque
        self.roll_offset = correction
        self.leg_pitch_offset = leg_pitch
        self.last_air_leg_pitch = leg_pitch
        self.air_exit_started = None
        self.wheel_target = np.clip(target, -60., 60.)
        return result


class AirRecorder(base.ref.Recorder):
    def sample(self):
        closure = super().sample()
        controller = self.sim.actor
        for key, value in dict(air_balance_active=controller.balance_active,
                               requested_body_pitch_torque_Nm=controller.pitch_torque_request,
                               roll_delta_offset=controller.roll_offset,
                               leg_pitch_offset=controller.leg_pitch_offset,
                               measured_wheel_velocity=self.d.qvel[controller.wheel_dofs],
                               wheel_velocity_target=controller.wheel_target).items():
            self.add(key, value)
        return closure


def air_metrics(data, row):
    if not row['primary_air']:
        return dict(air_peak_abs_pitch_deg=None, air_peak_abs_roll_deg=None,
                    air_rms_pitch_deg=None, within_pitch10_roll5=False)
    air = row['primary_air']
    lo, hi = air['index_start'], air['index_end']
    pose = data['pose_deg'][lo:hi, :2]
    gyro = data['qvel_after'][lo:hi, 3:6]
    return dict(air_peak_abs_pitch_deg=float(np.abs(pose[:, 0]).max()),
                air_peak_abs_roll_deg=float(np.abs(pose[:, 1]).max()),
                air_rms_pitch_deg=float(np.sqrt(np.mean(pose[:, 0]**2))),
                air_rms_roll_deg=float(np.sqrt(np.mean(pose[:, 1]**2))),
                air_peak_angular_speed_rad_s=np.abs(gyro).max(0).tolist(),
                pitch10_roll5_fraction=float(((np.abs(pose[:, 0])<=10.) & (np.abs(pose[:, 1])<=5.)).mean()),
                within_pitch10_roll5=bool((np.abs(pose[:, 0])<=10.).all() and (np.abs(pose[:, 1])<=5.).all()),
                peak_wheel_speed_rad_s=np.abs(data['measured_wheel_velocity']).max(0).tolist(),
                balance_active_samples=int(data['air_balance_active'][lo:hi].sum()))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--delivery', type=Path, default=T/'delivery')
    p.add_argument('--model', choices=['teacher', 'parent'], default='teacher')
    p.add_argument('--terrain', choices=['flat', 'stairs'], default='flat')
    p.add_argument('--configs', type=Path, required=True)
    p.add_argument('--speeds', type=float, nargs='+', default=[.6])
    p.add_argument('--seeds', type=int, nargs='+', default=[0])
    p.add_argument('--seconds', type=float, default=8.)
    a = p.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    base.Maneuver = AirBalance
    base.ref.Recorder = AirRecorder
    show = base.setup(out, a.model, a.terrain, a.delivery.resolve())
    configs = json.loads(a.configs.read_text(encoding='utf8'))
    rows = []
    for config in configs:
        cfg = {**base.BASE, 'crouch':.5, 'compress_s':.3, 'tuck':.2, **config}
        for speed in a.speeds:
            for seed in a.seeds:
                name = f'{a.model}_{a.terrain}_{cfg["id"]}_v{speed:g}_s{seed}'
                row = base.run_case(show, out, a.model, a.terrain, speed, seed, cfg, name, a.seconds)
                with np.load(out/name/'trajectory.npz') as data:
                    row.update(air_metrics(data, row))
                row['controller_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
                base.write_json(out/name/'RESULT.json', row)
                rows.append(row)
                base.write_json(out/'PROGRESS.json', rows)
                print('AIR_BALANCE '+json.dumps({k:row[k] for k in [
                    'id', 'air_peak_abs_pitch_deg', 'air_peak_abs_roll_deg', 'air_rms_pitch_deg',
                    'within_pitch10_roll5', 'stable_landing']}), flush=True)
    base.write_json(out/'COMPLETE.json', dict(completed=len(rows), rows=rows))


if __name__ == '__main__':
    main()
