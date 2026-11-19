# SPDX-License-Identifier: MIT
"""Training-only search for one-contact, forward-only MOD4v3 stair demonstrations.

The search uses the WASD plant and frozen E0 as a low-level controller. Terrain,
contact and the intervention clock are available only to this data collector.
Saved observations are the actual policy inputs and contain none of that data.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import asdict, dataclass
import json
import math
import os
from pathlib import Path

os.environ.setdefault('MUJOCO_GL', 'disable')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import mujoco as mj
import numpy as np
import torch

from play_repaired import HERE, AutonomousMapSimulation, load_parent, maps
from verify_wasd import Case, load_case


@dataclass(frozen=True)
class Parameters:
    push_speed: float
    top_height: float
    tuck_speed: float
    tuck_height: float
    delay: float
    body_advance: float
    rear_bias: float
    tuck_limit: float
    contact_front: float = 0.0
    contact_rear: float = 0.0
    contact_wheel: float = 0.0
    contact_settle: float = 0.0


class DemoPolicy:
    def __init__(self, e0):
        self.e0 = e0
        self.override = None
        self.data = []
        self.student = None
        self.student_mix = 0.

    def reset_history(self):
        self.override = None
        self.data.clear()

    @torch.inference_mode()
    def act(self, obs):
        expert = self.override
        target = obs.copy()
        if expert is not None:
            target[0], target[3] = expert[0], 5.0 * expert[1]
        action = self.e0(torch.from_numpy(target)[None])[0].numpy()
        if expert is not None:
            action[[1, 3]] += expert[2]
            if len(expert) > 3:
                action[[0, 2]] += expert[3]
                action[[1, 3]] += expert[4]
                action[4:6] += expert[5]
        teacher_action = np.clip(action, -6., 6.)
        applied = teacher_action
        if expert is not None and self.student_mix > 0.:
            observed = [frame[0] for frame in self.data[-39:]] + [obs]
            history = np.stack([observed[0]] * (40 - len(observed)) + observed)
            student = self.student.compute_all_heads(torch.from_numpy(obs)[None], torch.from_numpy(history).reshape(1, -1))
            learned = student['a_stair'][0].clamp(-6., 6.).numpy()
            applied = (1. - self.student_mix) * teacher_action + self.student_mix * learned
        self.data.append((obs.copy(), applied.copy(), float(expert is not None), target[:4].copy(), teacher_action.copy()))
        return applied, {'e0': float(expert is None), 'e1': float(expert is not None), 'e2': 0.}


class CaseSearch:
    def __init__(self, height, speed, offset, yaw, rise=False):
        # Use different caches for parallel workers, so no other writer can race the XML load.
        maps.CACHE_DIR = HERE / 'runtime_cache' / f'seed_{os.getpid()}'
        parent, sha = load_parent()
        self.ctrl = DemoPolicy(parent.stair.e0)
        self.sim = AutonomousMapSimulation(self.ctrl, sha, show_viewer=False)
        names = load_case(self.sim, Case('seed', target=height, speed=speed, yaw=yaw, offset=offset, raise_while_moving=rise))
        self.step_id = self.sim.m.geom(names[0]).id
        self.edge = float(self.sim.m.geom_pos[self.step_id, 0] - self.sim.m.geom_size[self.step_id, 0])
        self.tires = {int(g): i for i, g in enumerate(self.sim.tire_gids)}
        self.force = np.zeros(6)
        self.height, self.speed = height, speed
        self.start_yaw = yaw
        self.rise = rise
        self.approach_until_touch()

    def contact_forces(self):
        data = self.sim.d
        top = np.zeros(2, dtype=np.float64)
        hit = False
        for i in range(data.ncon):
            contact = data.contact[i]
            a, b = map(int, contact.geom)
            if self.step_id not in (a, b):
                continue
            other = b if a == self.step_id else a
            mj.mj_contactForce(self.sim.m, data, i, self.force)
            if abs(self.force[0]) < 3.:
                continue
            face = contact.pos[0] < self.edge + .035
            surface = contact.pos[0] > self.edge + .004 and abs(contact.pos[2] - .20) < .014 and abs(contact.frame[2]) > .72
            if surface and other in self.tires:
                top[self.tires[other]] += abs(self.force[0])
            if face and not surface:
                hit = True
        return hit, top

    def contacts(self):
        hit, top = self.contact_forces()
        return hit, top >= 5.

    def approach_until_touch(self):
        sim = self.sim
        detected = False
        orig = mj.mj_step

        def detect(model, data):
            nonlocal detected
            orig(model, data)
            detected = detected or self.contact_forces()[0]

        mj.mj_step = detect
        try:
            for k in range(300):
                keys = {'w'} if k >= 20 else set()
                if self.rise and k >= 5 and sim.target_h + 1e-8 < self.height:
                    keys.add('e')
                sim.step(keys)
                if detected:
                    break
            else:
                raise RuntimeError('E0 did not contact the step')
        finally:
            mj.mj_step = orig
        self.state_spec = mj.mjtState.mjSTATE_INTEGRATION
        self.state = np.empty(mj.mj_stateSize(sim.m, self.state_spec))
        mj.mj_getState(sim.m, sim.d, self.state, self.state_spec)
        self.prefix = self.ctrl.data.copy()
        self.k0 = sim.steps
        self.prev = sim.prev_a.copy()
        self.cmd = sim.cmd_vx, sim.cmd_wz

    def trial(self, parameters, keep=False):
        normal_step = mj.mj_step
        load_accum = np.zeros(2)

        def measured_step(model, data):
            normal_step(model, data)
            load_accum[:] += self.contact_forces()[1]

        mj.mj_step = measured_step
        try:
            return self._trial(parameters, load_accum, keep)
        finally:
            mj.mj_step = normal_step

    def _trial(self, parameters, load_accum, keep):
        param = parameters
        sim, controller = self.sim, self.ctrl
        data = sim.d
        mj.mj_setState(sim.m, data, self.state, self.state_spec)
        mj.mj_forward(sim.m, data)
        sim.steps, sim.prev_a = self.k0, self.prev.copy()
        sim.cmd_vx, sim.cmd_wz = self.cmd
        controller.data = self.prefix.copy() if keep or controller.student_mix > 0. else []
        controller.override = None
        max_x, backtrack = float(data.qpos[0]), 0.
        max_x_wheel, max_rim, peak_pitch = -1., 0., 0.
        phase, tuck_at, top_at = 'push', None, None
        held = first_held = 0
        changed = False
        lost = False
        tail = []
        for i in range(160):
            time = i * .02
            rim = sim.d.geom_xpos[sim.tire_gids]
            x = float(data.qpos[0])
            traversed = rim[:, 0].min() > self.edge + .018 and rim[:, 2].min() > .248
            if phase == 'push' and (time >= param.delay and x > self.edge + param.body_advance):
                phase, tuck_at = 'tuck', time
            if phase == 'tuck' and traversed:
                phase, top_at = 'recovery', time
                changed = True
            if phase == 'push':
                ramp = max(0., 1. - time / param.contact_settle) if param.contact_settle > 0. else 0.
                controller.override = (param.push_speed, param.top_height, 0., param.contact_front * ramp,
                                       param.contact_rear * ramp, param.contact_wheel * ramp)
            elif phase == 'tuck':
                controller.override = (param.tuck_speed, param.tuck_height, param.rear_bias)
                if time - tuck_at > param.tuck_limit:
                    break
            elif phase == 'recovery':
                weight = min(1., (time - top_at) / .28)
                h = (1. - weight) * max(.205, param.tuck_height) + weight * self.height
                controller.override = (max(.35, min(.95, self.speed)), h, 0.) if weight < 1. else None
            load_accum.fill(0)
            sim.step({'w'})
            top = load_accum / sim.env.decim >= 5.
            p = math.degrees(math.asin(np.clip(-data.xmat[sim.env.base_id, 6], -1, 1)))
            rim = sim.d.geom_xpos[sim.tire_gids]
            min_wheel_x = float(rim[:, 0].min())
            x = float(data.qpos[0])
            if not first_held:
                max_x = max(max_x, x)
                backtrack = max(backtrack, max_x - x)
            peak_pitch = max(peak_pitch, abs(p))
            max_x_wheel = max(max_x_wheel, min_wheel_x - self.edge)
            max_rim = max(max_rim, float(rim[:, 2].min()) - .0625)
            stable = bool(top.all() and min_wheel_x > self.edge + .018 and abs(p) < 25.)
            held = held + 1 if stable else 0
            if held >= 20 and not first_held:
                first_held = i + 1
            if first_held and min_wheel_x < self.edge - .01:
                lost = True
                break
            if keep:
                tail.append([time, x, data.qpos[2], data.qvel[0], p, float(top[0]), float(top[1])])
            if abs(p) > 57. or data.qpos[2] < .13:
                lost = True
                break
            if first_held and i - first_held > 17:
                break
        score = min(max_rim, .22) * 12. + min(max_x_wheel, .16) * 10. + min(20, held) * .09
        score -= backtrack * 25. + max(0., peak_pitch - 18.) * .06
        score -= float(lost) * 4. + (first_held * .012 if first_held else 1.)
        success = bool(first_held and changed and not lost and backtrack <= .075 and peak_pitch <= 32.)
        result = dict(score=score, qualified=success, hold_frame=first_held or None, lost=lost, backtrack_m=backtrack,
                      max_rim_m=max_rim, max_wheel_cross_m=max_x_wheel, pitch_peak_deg=peak_pitch,
                      parameters=asdict(param), plant_contact_time_s=self.k0 * .02)
        if keep:
            obs, actions, gate, latent_cmd, teacher_act = zip(*controller.data, strict=True)
            return result, dict(obs=np.array(obs), act=np.array(actions), gate=np.array(gate),
                                latent_cmd=np.array(latent_cmd), teacher_act=np.array(teacher_act), tail=np.array(tail))
        return result


LOW = np.array([.24, .366, .32, .195, .00, -.06, -.60, .28])
HIGH = np.array([1.65, .420, 1.86, .275, .52, .125, 1.35, .95])


def search(item):
    height, speed, offset, yaw, count, out = item
    searcher = CaseSearch(height, speed, offset, yaw)
    rng = np.random.default_rng(int(round(height*10000 + speed*10000)) + round(offset*1000) + round(yaw*12))
    initial = [Parameters(.71, .405, .32, .251, .0, -.06, .396, .906)]
    initial += [Parameters(p, .415, v, .205, t, x, 0., .85) for p in (.50, 1.15) for v in (.70, 1.55)
               for t, x in ((.02, -.035), (.08, .02), (.20, .075))]
    pool = [(np.array(list(asdict(p).values())[:8]), searcher.trial(p)) for p in initial]
    for _ in range(max(0, count - len(initial))):
        if rng.random() < .37:
            candidate = rng.uniform(LOW, HIGH)
        else:
            top = sorted(pool, key=lambda pair: pair[1]['score'], reverse=True)[:6]
            center = top[int(rng.integers(len(top)))][0]
            candidate = np.clip(center + .25 * (HIGH - LOW) * rng.normal(size=len(LOW)), LOW, HIGH)
        pool.append((candidate, searcher.trial(Parameters(*candidate))))
    qualified = [entry for entry in pool if entry[1]['qualified']]
    chosen = sorted(qualified or pool, key=lambda pair: pair[1]['score'], reverse=True)[0]
    result, episode = searcher.trial(Parameters(*chosen[0]), keep=True)
    info = dict(height_cmd=height, speed=speed, offset_m=offset, yaw_deg=yaw, tried=len(pool),
                qualified_count=len(qualified), **result)
    key = f'h{round(height*100):02}_v{round(speed*100):02}_x{round(offset*1000):+04}_y{round(yaw):+03}'
    out = Path(out)
    np.savez_compressed(out / f'{key}.npz', **episode)
    (out/f'{key}.json').write_text(json.dumps(info | {'trials':[r for _, r in pool]}, indent=2) + '\n', encoding='utf8')
    return info


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--trials', type=int, default=72)
    parser.add_argument('--heights', type=float, nargs='+', default=[.28, .36, .40, .42])
    parser.add_argument('--speeds', type=float, nargs='+', default=[.47, .90])
    parser.add_argument('--spread', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    poses = [(0., 0.)] if not args.spread else [(-.06, 0.), (-.03, 8.), (.03, -8.), (.06, 0.)]
    tasks = [(h, v, x, y, args.trials, args.out.resolve()) for h in args.heights for v in args.speeds for x, y in poses]
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        results = []
        for result in pool.map(search, tasks):
            results.append(result)
            print(json.dumps(result), flush=True)
            (args.out/'SEARCH.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf8')


if __name__ == '__main__':
    main()
