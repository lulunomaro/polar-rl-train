"""Frozen-checkpoint MuJoCo replays that distinguish delay units and action memory.

Evaluation only: weights, original playback, plant, reward and training sources
are read-only. The plant's original PD/envelopes and refresh cadence are reused.
Sensor history is sampled after each existing physics step. Action history uses
emission timestamps; its delayed target is read at each original PD refresh.
"""
from __future__ import annotations
import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(r'D:\claude2\fangzhen')
PLAY = ROOT / 'runs3060/mod4v3_play_20261107'
sys.path.insert(0, str(PLAY))
import mujoco
import numpy as np
import torch
import eval_flatv2_multienv as legacy
from eval_flatv2_final import args_for, actual_yaw_rate
from play_ppo_flatv1_control import Simulation


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class DelayReplay:
    """Use actual seconds, preserve 35 inputs, and expose action-memory choice."""
    def __init__(self, sim, action_ms, obs_ms, memory='sent', scope='sensors'):
        self.sim = sim
        self.action_s = action_ms / 1000.
        self.obs_s = obs_ms / 1000.
        self.memory = memory
        self.scope = scope
        self.actor = sim.actor
        self.original_reset = sim.reset_standing
        self.action_history = deque(maxlen=128)
        self.sensor_history = deque(maxlen=256)
        self.policy_history = deque(maxlen=128)
        self.last_applied = torch.zeros((1, 6))
        self.resets = 0
        self.count_resets = False
        self.applied_trace = []
        self.sent_trace = []
        sim.actor = self.policy
        sim.env.step = self.physics
        sim.reset_standing = self.reset
        self.clear()

    def clear(self):
        self.action_history.clear()
        self.sensor_history.clear()
        self.policy_history.clear()
        self.last_applied.zero_()
        self.applied_trace = []
        self.sent_trace = []
        self.sensor_history.append((float(self.sim.env.d.time), self.sensor()))

    def reset(self):
        if self.count_resets:
            self.resets += 1
        self.original_reset()
        self.clear()

    @staticmethod
    def lookup(history, at):
        for timestamp, value in reversed(history):
            if timestamp <= at + 1e-9:
                return value
        return history[0][1]

    def sensor(self):
        sim = self.sim
        env = sim.env
        d = env.d
        q = np.asarray(d.qpos[env.qadr_all])
        qd = np.asarray(d.qvel[env.dadr_all])
        indices = [env.spec.joint_names.index(n) for n in sim.active_names]
        pos = q[indices] - sim.default_active.detach().cpu().numpy()
        pos[4:] = 0.
        vel = qd[indices]
        rotation = np.asarray(d.xmat[env.base_id]).reshape(3, 3)
        gravity = rotation.T @ np.array([0., 0., -1.])
        return np.concatenate((np.asarray(d.qvel[3:6]) * .5, gravity,
                               pos, vel[:4] * .1, vel[4:] * .1)).astype(np.float32)

    def policy(self, observation):
        now = float(self.sim.env.d.time)
        current = observation.clone()
        if self.memory == 'applied':
            current[:, 22:28] = self.last_applied.to(current)
        if self.scope == 'all':
            self.policy_history.append((now, current.clone()))
            encoded = self.lookup(self.policy_history, now - self.obs_s).clone()
        else:
            encoded = current
            if self.obs_s > 0:
                delayed = self.lookup(self.sensor_history, now - self.obs_s)
                encoded[:, 4:22] = torch.as_tensor(delayed, device=current.device)
        return self.actor(encoded)

    def physics(self, action):
        env = self.sim.env
        action = action.clamp(-env.action_clip, env.action_clip)
        self.action_history.append((float(env.d.time), action.detach().clone()))
        self.sent_trace.append(action.detach().cpu().numpy().reshape(-1).tolist())
        applied = action
        for j in range(env.decim):
            applied = self.lookup(self.action_history, float(env.d.time) - self.action_s)
            if j % 4 == 0:
                env.d.ctrl[env.act_ids] = env._torque(applied).detach().cpu().numpy().reshape(-1)
            mujoco.mj_step(env.m, env.d)
            self.sensor_history.append((float(env.d.time), self.sensor()))
        env.a_prev = applied.detach().clone()
        # The environment order [LF,RF,LR,RR,LW,RW] is converted back to PPO.
        self.last_applied = applied[:, self.sim.ppo_to_env].detach().cpu().clone()
        self.applied_trace.append(applied.detach().cpu().numpy().reshape(-1).tolist())
        return env.state()


def run_case(sim, replay, seed, vx, steps, tail, height=.28, wz=0.):
    replay.count_resets = False
    legacy.reset_perturbed(sim, seed)
    replay.clear()
    replay.resets = 0
    replay.count_resets = True
    sim.args.vx = abs(float(vx))
    sim.args.wz = abs(float(wz))
    sim.height = float(height)
    keys = set()
    if vx != 0: keys.add('w' if vx > 0 else 's')
    if wz != 0: keys.add('a' if wz > 0 else 'd')
    values = []
    started = time.perf_counter()
    for k in range(steps):
        telemetry = sim.step(keys)
        values.append((float(telemetry['vx']), actual_yaw_rate(sim),
                       float(telemetry['z']), float(telemetry['cos_tilt'])))
        if replay.resets or not np.isfinite(values[-1]).all():
            break
    replay.count_resets = False
    samples = np.asarray(values[-tail:], dtype=float)
    return dict(seed=seed, cmd_vx=vx, cmd_wz=wz, cmd_height=height,
                completed_steps=len(values), requested_steps=steps,
                reset_count=replay.resets, vx_mean=float(samples[:,0].mean()),
                vx_abs_error=float(abs(samples[:,0].mean() - vx)),
                wz_mean=float(samples[:,1].mean()),
                wz_abs_error=float(abs(samples[:,1].mean() - wz)),
                height_mean=float(samples[:,2].mean()),
                height_abs_error=float(abs(samples[:,2].mean()-height)),
                min_cos_tilt=float(samples[:,3].min()),
                sent_action_abs_max=float(np.abs(replay.sent_trace).max()) if replay.sent_trace else None,
                applied_action_abs_max=float(np.abs(replay.applied_trace).max()) if replay.applied_trace else None,
                wall_seconds=time.perf_counter()-started)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    plan = json.loads(Path(args.plan).read_text(encoding='utf-8-sig'))
    out = Path(args.out)
    if out.exists(): raise FileExistsError(out)
    torch.set_num_threads(1)
    result = dict(format='STEP7_DELAY_DIAGNOSTIC_V1',
                  started_at=datetime.now(timezone.utc).isoformat(),
                  evaluation_only=True, plan=plan, replays=[])
    input_paths = [Path(__file__), PLAY/'play_mod4v3.py', PLAY/'play_ppo_flatv1_control.py',
                   PLAY/'eval_flatv2_multienv.py']
    input_paths += [Path(p) for p in plan['models'].values()]
    result['input_sha256'] = {str(p.resolve()): sha(p) for p in input_paths}
    for label, checkpoint in plan['models'].items():
        for mode in plan['modes']:
            sim = Simulation(args_for(checkpoint))
            replay = DelayReplay(sim, mode['action_ms'], mode['obs_ms'],
                                 mode.get('memory','sent'), mode.get('scope','sensors'))
            row = dict(model=label, mode=mode, physics_dt_s=sim.env.dt,
                       decimation=sim.env.decim, pd_refresh_s=sim.env.dt*4,
                       plant_sha256=sha(sim.args.xml), cases=[])
            try:
                for case in plan['cases']:
                    for seed in plan['seeds']:
                        record = run_case(sim, replay, seed,
                                          case.get('vx',0.),
                                          case.get('steps',300),
                                          case.get('tail',120),
                                          case.get('height',.28),
                                          case.get('wz',0.))
                        row['cases'].append(record)
                result['replays'].append(row)
            finally:
                sim.close()
            out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps(dict(model=label,mode=mode['name'],
                  rows=[dict(seed=c['seed'],cmd=c['cmd_vx'],wz=c['cmd_wz'],
                             actual=round(c['vx_mean'],4),
                             error=round(c['vx_abs_error'],4),
                             resets=c['reset_count']) for c in row['cases']]),ensure_ascii=False),flush=True)
    result['finished_at']=datetime.now(timezone.utc).isoformat()
    result['input_sha256_after']={str(p.resolve()):sha(p) for p in input_paths}
    result['inputs_unchanged']=result['input_sha256']==result['input_sha256_after']
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__': main()
