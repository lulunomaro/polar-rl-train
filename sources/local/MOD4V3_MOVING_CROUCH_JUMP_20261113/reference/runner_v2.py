"""Bounded forward crouch/push/tuck/land probes of the frozen approved R3."""
from pathlib import Path
import argparse
import ast
import hashlib
import importlib.util
import json
import math
import sys
import time
import types

import mujoco
import numpy as np
import torch

import frozen_recorder as ref

T = Path(__file__).resolve().parent
PHASES = ['approach', 'crouch', 'push', 'flight_extend', 'flight_tuck',
          'landing_extend', 'recover', 'done']
BOUNDS = (.17265192458887935, 1.7508937980913823)
BASE = dict(crouch=.9, compress_s=.24, push_s=.32, tuck=.45,
            extend_air_s=.02, tuck_s=.10, land_delta=1.35,
            blend_s=.30, height=.36, mean_offset=0.)


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf8')


def headless_controller(delivery):
    """Keep Simulation source unchanged while omitting unused GUI-only imports."""
    core = delivery / 'runtime/core'
    sys.path.insert(0, str(core))
    path = core / 'play_ppo_flatv1_control.py'
    tree = ast.parse(path.read_text(encoding='utf8'))
    tree.body = [n for n in tree.body if not (
        isinstance(n, ast.Import) and any(x.name == 'tkinter' for x in n.names)
        or isinstance(n, ast.ImportFrom) and n.module == 'pynput')]
    module = types.ModuleType('play_ppo_flatv1_control')
    module.__file__ = str(path)
    sys.modules[module.__name__] = module
    exec(compile(tree, str(path), 'exec'), module.__dict__)


def setup(out, model, terrain, delivery):
    headless_controller(delivery)
    ref.D = delivery
    ref.MODELS = {k: (T/'weights'/('frozen_'+k+'.pt'), v[1]) for k, v in ref.MODELS.items()}
    show = ref.setup(out, model)
    if terrain == 'flat':
        path = show.B/'tiles/r03_c00.npz'
        with np.load(path) as a:
            v, f = a['vertices'].copy(), a['faces'].copy()
        v[:, 2] = 0.
        np.savez_compressed(path, vertices=v, faces=f)
    return show


def segments(mask):
    padded = np.r_[False, np.asarray(mask, dtype=bool), False].astype(int)
    return list(zip(np.flatnonzero(np.diff(padded) == 1),
                    np.flatnonzero(np.diff(padded) == -1)))


def rolling_stable_window(data, start, terrain_level=None):
    """A moving wheel may have sub-step contact gaps; report a 0.5s window."""
    t = data['time']
    force = data['body_contact_force']
    support = force[:, data['wheel_body_ids'], 2]
    good = (t >= start) & (np.abs(data['pose_deg'][:, :2]) < 15.).all(1)
    if terrain_level is not None:
        edge, top, half = (-2.9, .2, 2.88) if terrain_level == 1 else (-1.4, .4, 1.38)
        wheel = data['wheel']
        good &= (wheel[:, :, 0] > edge+.02).all(1)
        good &= (np.abs(wheel[:, :, 1]) < half).all(1)
        good &= (np.abs(wheel[:, :, 2]-top-.0625) < .04).all(1)
        support = data['wheel_tread_fz'][:, terrain_level-1]
    forbidden = np.r_[data['guide_body_ids'], int(data['base_body_id'])]
    good &= np.linalg.norm(force[:, forbidden], axis=2).max(1) < 1.
    absent = np.linalg.norm(force, axis=2).sum(1) < 1.
    for lo, hi in segments(good):
        for begin in range(lo, hi-199, 4):
            end = begin+200
            duty = (support[begin:end] > 5.).mean(0)
            if duty.min() < .8:
                continue
            max_gap = max([b-a for a, b in segments(absent[begin:end])] or [0])*.0025
            if max_gap >= .02 or np.ptp(data['root'][begin:end, 2]) > .03:
                continue
            if np.abs(data['qvel_after'][begin:end, 2]).max() > .30:
                continue
            return dict(start=float(t[begin]), duration_s=.5,
                        per_wheel_support_duty=duty.tolist(), max_unsupported_gap_s=max_gap,
                        root_height_span_m=float(np.ptp(data['root'][begin:end, 2])),
                        max_abs_root_vz_m_s=float(np.abs(data['qvel_after'][begin:end, 2]).max()))
    return None


class Maneuver:
    def __init__(self, sim, recorder, config, terrain, baseline):
        self.sim, self.rec, self.cfg = sim, recorder, config
        self.terrain, self.baseline = terrain, baseline
        self.actor = sim.actor
        self.phase, self.entered = 'approach', 0.
        self.events = []
        self.target = np.full(2, np.nan)
        self.start_delta = None
        self.last_delta = None
        self.recover_delta = None
        self.launch = None
        self.landed_at = None

    def change(self, phase, now):
        self.phase, self.entered = phase, now
        d = self.sim.env.d
        self.events.append(dict(phase=phase, time=now, root=d.qpos[:3].tolist(),
                                vx=float(self.sim.env.vx), vz=float(d.qvel[2])))

    def unsupported(self):
        if not self.rec.data.get('body_contact_force'):
            return False
        return float(np.linalg.norm(self.rec.data['body_contact_force'][-1], axis=1).sum()) < 1.

    def __call__(self, obs):
        raw = self.actor(obs)
        s, cfg = self.sim, self.cfg
        d, now = s.env.d, float(s.env.d.time)
        default = s.default_active
        raw_delta = np.array([float(default[f]+.5*raw[0, f]-default[r]-.5*raw[0, r])
                              for f, r in ((0, 1), (2, 3))])
        raw_delta = raw_delta.clip(*BOUNDS)
        if self.baseline:
            self.target = raw_delta
            return raw
        if self.phase == 'approach':
            wheel = d.xpos[self.rec.wheels]
            if self.terrain == 'flat':
                ready = now >= 3.6
            else:
                distance = float(-2.9-wheel[:, 0].max())
                lead = cfg.get('lead_m', .30)
                ready = now >= 3.2 and distance <= lead
            if ready and s.env.vx > .10:
                self.start_delta = raw_delta.copy()
                self.change('crouch', now)
        elapsed = now-self.entered
        if self.phase == 'crouch' and elapsed >= cfg['compress_s']:
            self.change('push', now)
        elif self.phase == 'push':
            if elapsed >= .04 and self.unsupported() and d.qvel[2] > .10:
                self.launch = now
                self.change('flight_extend', now)
            elif elapsed >= cfg['push_s']:
                self.recover_delta = self.last_delta.copy()
                self.change('recover', now)
        elif self.phase == 'flight_extend' and elapsed >= cfg['extend_air_s']:
            self.change('flight_tuck', now)
        elif self.phase == 'flight_tuck':
            if elapsed >= cfg['tuck_s'] and (d.qvel[2] <= -.05 or elapsed >= .24):
                self.change('landing_extend', now)
        elif self.phase == 'landing_extend':
            if not self.unsupported() and elapsed > .02:
                self.landed_at = now
                self.recover_delta = self.last_delta.copy()
                self.change('recover', now)
            elif elapsed > .8:
                self.recover_delta = self.last_delta.copy()
                self.change('recover', now)
        elif self.phase == 'recover' and elapsed >= cfg['blend_s']:
            self.change('done', now)

        elapsed = now-self.entered
        phase = self.phase
        if phase in ('approach', 'done'):
            self.target = raw_delta
            return raw
        if phase == 'crouch':
            alpha = min(1., elapsed/cfg['compress_s'])
            delta = self.start_delta+(cfg['crouch']-self.start_delta)*alpha
        elif phase in ('push', 'flight_extend'):
            delta = np.full(2, BOUNDS[1])
        elif phase == 'flight_tuck':
            alpha = min(1., elapsed/.06)
            delta = np.full(2, BOUNDS[1]+(cfg['tuck']-BOUNDS[1])*alpha)
        elif phase == 'landing_extend':
            alpha = min(1., elapsed/.08)
            delta = np.full(2, cfg['tuck']+(cfg['land_delta']-cfg['tuck'])*alpha)
        else:
            alpha = min(1., elapsed/cfg['blend_s'])
            delta = self.recover_delta+(raw_delta-self.recover_delta)*alpha
        delta = np.asarray(delta).clip(*BOUNDS)
        result = raw.clone()
        for i, (front, rear) in enumerate(((0, 1), (2, 3))):
            mean = .5*(default[front]+.5*raw[:, front]+default[rear]+.5*raw[:, rear])
            mean = mean + cfg.get('mean_offset', 0.)
            result[:, front] = 2*(mean+delta[i]/2-default[front])
            result[:, rear] = 2*(mean-delta[i]/2-default[rear])
        self.last_delta = self.target = delta
        return result


def summarize(data, config, events, terrain, reason, case_id):
    t = data['time']
    phase = data['phase']
    wheel = data['wheel']
    force = data['body_contact_force']
    unsupported = np.linalg.norm(force, axis=2).sum(1) < 1.
    com_vz = np.gradient(data['com'][:, 2], .0025)
    air = []
    for lo, hi in segments(unsupported & (phase >= PHASES.index('push'))):
        if (hi-lo)*.0025 < .02:
            continue
        before = max(0, lo-20)
        upward = float(com_vz[before:min(hi, lo+8)].max())
        if upward <= .10:
            continue
        air.append(dict(start=float(t[lo]), end=float(t[hi-1]+.0025),
                        duration_s=(hi-lo)*.0025, upward_com_vz_m_s=upward,
                        peak_paired_rim_z_m=float((wheel[lo:hi, :, 2].min(1)-.0625).max()),
                        com_rise_m=float(data['com'][lo:hi, 2].max()-data['com'][lo, 2]),
                        root_rise_m=float(data['root'][lo:hi, 2].max()-data['root'][lo, 2]),
                        dx_m=float(data['com'][hi-1, 0]-data['com'][lo, 0]),
                        index_start=int(lo), index_end=int(hi)))
    primary = max(air, key=lambda x: x['duration_s']) if air else None
    stable = False
    stable_time = None
    if primary:
        end = primary['index_end']
        support = (force[:, data['wheel_body_ids'], 2] > 5.).all(1)
        upright = (np.abs(data['pose_deg'][:, :2]) < 15.).all(1)
        valid = support & upright & (t >= t[min(end, len(t)-1)])
        for lo, hi in segments(valid):
            if (hi-lo)*.0025 >= .5:
                stable, stable_time = True, float(t[lo])
                break
    start = next((e['time'] for e in events if e['phase'] == 'crouch'), None)
    push = next((e['time'] for e in events if e['phase'] == 'push'), None)
    actmask = t >= (start or 3.6)
    from_push = t >= (push or 3.6)
    wi, gi, bi = data['wheel_body_ids'], data['guide_body_ids'], int(data['base_body_id'])
    contacts = {}
    for name, ids in [('wheels', wi), ('guides', gi), ('chassis', [bi])]:
        f = force[:, ids]
        contacts[name] = dict(peak_norm_N=float(np.linalg.norm(f, axis=2).sum(1)[actmask].max(initial=0)),
                              vertical_impulse_Ns=float(f[actmask, :, 2].sum()*.0025))
    strict_stable = stable
    rolling_window = rolling_stable_window(data, primary['end']) if primary else None
    stable = rolling_window is not None
    stable_time = rolling_window['start'] if rolling_window else None
    first = False
    second = False
    strict_stairs = []
    for level, edge, top in [(1, -2.9, .2), (2, -1.4, .4)]:
        valid = ((data['wheel_tread_fz'][:, level-1] > 5.).all(1)
                 & (wheel[:, :, 0] > edge+.02).all(1)
                 & (np.abs(wheel[:, :, 1]) < (2.88 if level == 1 else 1.38)).all(1)
                 & (np.abs(wheel[:, :, 2]-(top+.0625)) < .04).all(1)
                 & (np.abs(data['pose_deg'][:, :2]) < 20.).all(1))
        strict_stairs.append(any((hi-lo)*.0025 >= .5 for lo, hi in segments(valid)) if terrain == 'stairs' else False)
        landed = rolling_stable_window(data, 0., level) is not None if terrain == 'stairs' else False
        if level == 1:
            first = landed
        else:
            second = landed
    return dict(id=case_id, config=config, terrain=terrain, reason=reason or 'time_limit',
                events=events, action_started=start is not None,
                genuine_airborne=primary is not None, air_intervals=air,
                primary_air=primary, stable_landing=stable, stable_landing_time=stable_time,
                strict_contiguous_support_landing=strict_stable,
                rolling_landing_window=rolling_window, strict_contiguous_stair_support=strict_stairs,
                first_step_stable=first, second_step_stable=second,
                phase_sequence_completed=all(any(e['phase']==p for e in events)
                    for p in ('crouch', 'push', 'flight_extend', 'flight_tuck', 'landing_extend', 'recover')),
                max_paired_rim_z_after_push_m=float((wheel[from_push, :, 2].min(1)-.0625).max(initial=-1)),
                peak_abs_pitch_roll_deg=np.abs(data['pose_deg'][actmask, :2]).max(0).tolist(),
                closure_max_m=float(data['closure'].max()), contacts=contacts,
                root_final=data['root'][-1].tolist(), seconds=float(t[-1]+.0025),
                physics_dt_s=.0025, policy_hz=50, legs_hz=100, wheels_hz=400,
                closure_reset_m=.01, optimizer_updates=0,
                timing_note='Geometry/contact at physics-step start; qpos_after/qvel_after at end. No mj_forward inside dynamics.')


def run_case(show, out, model, terrain, speed, seed, config, case_id, seconds=8., baseline=False):
    dest = out/case_id
    dest.mkdir(exist_ok=False)
    sim = show.Replay(level=3, direction='up', show=False)
    sim.args.vx = speed
    e, m, d = sim.env, sim.env.m, sim.env.d
    yaw = [0., -.025, .025, -.04, .04][seed]
    x = (-2.5 if terrain == 'flat' else -3.9) + [0., .04, -.04, .02, -.02][seed]
    y = [0., -.06, .06, .03, -.03][seed]
    d.qpos[:3] = [x, y, e.bank_z]
    d.qpos[3:7] = [math.cos(yaw/2), 0., 0., math.sin(yaw/2)]
    d.qvel[:] = 0.
    mujoco.mj_forward(m, d)
    sim.reset_count, sim.reason = 1, ''
    recorder = ref.Recorder(sim)
    controller = Maneuver(sim, recorder, config, terrain, baseline)
    sim.actor = controller
    leg_qadr = [[m.joint(n).qposadr[0] for n in names] for names in
                [('left_front1_joint', 'left_rear1_joint'),
                 ('right_front1_joint', 'right_rear1_joint')]]

    def physics(env, action):
        action = action.clamp(-env.action_clip, env.action_clip)
        for j in range(env.decim):
            torque = env._torque(action).detach().numpy().reshape(-1)
            if j % 4 == 0:
                d.ctrl[env.act_ids[:4]] = torque[:4]
            d.ctrl[env.act_ids[4:]] = torque[4:]
            mujoco.mj_step(m, d)
            closure = recorder.sample()
            recorder.add('phase', PHASES.index(controller.phase))
            recorder.add('target_delta', controller.target)
            recorder.add('leg_delta_actual', [d.qpos[f]-d.qpos[r] for f, r in leg_qadr])
            if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():
                raise show.SafetyStop('nonfinite')
            if closure > .01:
                raise show.SafetyStop('closure>10mm')
        env.a_prev = action.detach()
        return env.state()

    e.step = types.MethodType(physics, e)
    wall = time.time()
    try:
        for _ in range(int(math.ceil(seconds/.02))):
            now = float(d.time)
            sim.set_height(.28+(config['height']-.28)*min(now/2., 1.))
            sim.step({'w'} if now >= 2. else set())
            if sim.reset_count != 1:
                break
        data = recorder.save(dest/'trajectory.npz')
        result = summarize(data, config, controller.events, terrain, sim.reason, case_id)
        result.update(model=model, checkpoint_sha256=show.EXPECTED, speed_command=speed,
                      seed=seed, initial=[x, y, yaw], baseline=baseline, wall_s=time.time()-wall)
        result['runner_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        write_json(dest/'RESULT.json', result)
        print(json.dumps({k: result[k] for k in ['id', 'genuine_airborne', 'stable_landing',
                         'phase_sequence_completed', 'max_paired_rim_z_after_push_m',
                         'first_step_stable', 'reason', 'wall_s']}), flush=True)
        return result
    finally:
        sim.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out', required=True)
    p.add_argument('--delivery', default=str(T/'delivery'))
    p.add_argument('--model', choices=['teacher', 'parent'], default='teacher')
    p.add_argument('--terrain', choices=['flat', 'stairs'], default='flat')
    p.add_argument('--configs', type=Path)
    p.add_argument('--speeds', type=float, nargs='+', default=[.6])
    p.add_argument('--seeds', type=int, nargs='+', default=[0])
    p.add_argument('--seconds', type=float, default=8.)
    a = p.parse_args()
    out = Path(a.out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    show = setup(out, a.model, a.terrain, Path(a.delivery).resolve())
    configs = json.loads(a.configs.read_text(encoding='utf8')) if a.configs else [
        dict(id='baseline', baseline=True),
        *[dict(id=f'c{int(c*100):03d}_t{int(dt*1000)}', crouch=c, compress_s=dt)
          for c in (.65, .9, 1.1) for dt in (.16, .30)]]
    rows = []
    for config in configs:
        cfg = {**BASE, **config}
        for speed in a.speeds:
            for seed in a.seeds:
                name = f'{a.model}_{a.terrain}_{cfg["id"]}_v{speed:g}_s{seed}'
                rows.append(run_case(show, out, a.model, a.terrain, speed, seed, cfg, name,
                                     a.seconds, cfg.get('baseline', False)))
                write_json(out/'PROGRESS.json', rows)
    write_json(out/'COMPLETE.json', dict(completed=len(rows), rows=rows))


if __name__ == '__main__':
    main()
