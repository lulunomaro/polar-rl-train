"""Optimize a closed-loop demonstration on the pinned plant for offline warm starting."""
from __future__ import annotations

from argparse import ArgumentParser
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from scipy.optimize import differential_evolution
import torch

from eval_moving_jump_360mm import MeasuredPlant, Trial, measure
from jump360_scene import CLOSURE_LIMIT, HERE, HOLD_TICKS, cruise_actor, json_save, mujoco

BOUNDS = [
    (-.15, .52), (1.5, 6.5), (.0, .20), (-.10, .11),   # crouch target, rate, settle, lean/speed
    (-.28, .07), (-.10, .14), (.08, .24), (.0, .036),   # push lean, lean/speed, time, delay after liftoff
    (-.23, .07), (.0, .30), (.13, .27), (1.05, 1.75),  # tuck lean, desired pitch, duration, landing delta
    (-.22, .06), (.0, .12),                             # landing lean, wheel launch assistance
    (-.65, 1.5), (-.14, .14), (-.12, .12),              # crouch ramp curve and two push corrections
    (1.72, 2.85), (-.38, .32),                         # extension and tuck targets
]
INITIAL = [.30, 2.7, .13, .03, -.22, .11, .18, .010, -.145, .075, .20, 1.55, -.09, .04, 0., 0., 0., 1.98, .12]
WORKER = None
DRIVE = None
SAMPLES = {}
E0 = HERE.parent / "MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120/weights/e0_c874_004m.pt"
CONFIG = (1.20, .32, False, None)


def initialize(speed=1.20, height=.32, smooth_landing=False, e0=False, target_clearance=None):
    global WORKER, DRIVE, CONFIG
    torch.set_num_threads(1)
    WORKER = MeasuredPlant()
    DRIVE = cruise_actor(E0 if e0 else None)
    CONFIG = speed, height, smooth_landing, target_clearance


class Teacher:
    def __init__(self, variables, plant):
        self.variables = variables
        self.plant = plant
        self.default = plant.default_active
        self.mode = 0
        self.phase_start = 0.
        self.no_contact = 0
        self.contact = 0
        self.delta_start = np.zeros(2)
        self.push_vx = 0.
        self.preland_altitude = 0.
        self.touch_z = 0.
        self.ramp_time = 0.

    def inspect(self, f):
        self.no_contact = self.no_contact + 1 if f.total_force < 1. else 0
        self.contact = self.contact + 1 if min(f.wheel_up_force) > 1. else 0

    @torch.inference_mode()
    def action(self, observation):
        sim = self.plant
        args = self.variables
        now = sim.d.time
        key = observation[30] > .5
        obs = observation.copy()
        obs[30] = 0.
        action = DRIVE(torch.from_numpy(obs)).numpy()
        if not key or self.mode == 6:
            return action.clip(-6., 6.)
        actual = sim.d.qpos[sim.active_qadr[:4]].reshape(2, 2)
        offset = self.default[:4].reshape(2, 2)
        q = offset + .5*action[:4].reshape(2, 2)
        pitch = float(np.arcsin(np.clip(-sim.d.xmat[sim.base_id][6], -1, 1)))
        wy = sim.d.qvel[4]
        vx = sim.body_vx
        vx_cmd = sim.cmd_vx
        z, vz = sim.d.qpos[2], sim.d.qvel[2]
        if self.mode == 0:
            self.mode, self.phase_start = 1, now
            self.delta_start = np.diff(actual[:, ::-1], axis=1)[:, 0]
            self.ramp_time = max(.08, float(np.max(self.delta_start-args[0])) / args[1])
        duration = now-self.phase_start
        if self.mode == 1 and duration >= self.ramp_time+args[2]:
            self.mode, self.phase_start, duration = 2, now, 0.
            self.push_vx = vx
        if self.mode == 2 and ((self.no_contact*.0025 > args[7] and vz > .4 and duration >= .08)
                               or duration >= args[6]):
            self.mode, self.phase_start, duration = 3, now, 0.
        if self.mode == 3 and duration >= args[10] and vz < .3:
            self.mode, self.phase_start, duration = 4, now, 0.
        if self.mode == 4 and self.contact >= 3 and duration >= .02:
            self.mode, self.phase_start, duration = 5, now, 0.
            self.touch_z = z
        if self.mode == 5 and duration >= .32:
            self.mode = 6
            return action.clip(-6., 6.)

        mean = q.mean(axis=1)
        raw_delta = q[:, 0]-q[:, 1]
        if self.mode == 1:
            decay = min(duration / self.ramp_time, 1.)
            decay = 1.-(1.-decay)**(1.+args[14])
            delta = self.delta_start + decay*(args[0]-self.delta_start)
            mean = mean + args[3]*vx
        elif self.mode == 2:
            delta = np.full(2, args[17])
            mean = mean + args[4] + args[5]*self.push_vx + .20*pitch+.025*wy
            mean += args[15]*(1.-2.*min(duration/args[6],1.)) + args[16]*vz
            action[4:] += args[13]*10.
        elif self.mode in (3, 4):
            ref = args[9] if self.mode == 3 else 0.
            pe = pitch-ref
            qd = sim.d.qvel[sim.active_dadr[4:]]
            action[4:] = (qd + .5*(10.*pe+1.1*wy)/.6)/10.
            balance = np.clip(2.3*pe+.18*wy, -.42, .42)
            if self.mode == 3:
                delta = np.full(2, args[18])
                mean = mean + args[8] + balance
            else:
                delta = np.full(2, args[18]+(args[11]-args[18])*min(duration/.07, 1.))
                current = (actual[:, 0]-actual[:, 1]).mean()
                base = np.interp(current, [.17, .35, .66, .95, 1.33, 1.75], [.48, .467, .380, .317, .265, .232])
                mean = mean*.32 + .68*(base+args[12]-.18*(vx-vx_cmd)) + balance
        else:
            delta = raw_delta+.36*max(0., -vz)+max(0., self.touch_z-.14-z)*9.
        q[:, 0] = mean+.5*delta
        q[:, 1] = mean-.5*delta
        action[:4] = (2.*(q-offset)).reshape(4)
        return action.clip(-6., 6.)


def prefill(speed, height, seed, dr):
    key = speed, height, seed, dr
    env = WORKER
    if dr == 0. and key in SAMPLES:
        integration, previous, past = SAMPLES[key]
        mujoco.mj_setState(env.m, env.d, integration, mujoco.mjtState.mjSTATE_INTEGRATION)
        env.a_prev = previous.copy()
        mujoco.mj_forward(env.m, env.d)
        env.tilt_fault = False
        return past
    rng = np.random.default_rng(seed)
    env.setup(height, dr, (0., float(rng.uniform(-.008,.008)), float(rng.uniform(-.006,.006))))
    command = 0.
    past_obs = []
    with torch.inference_mode():
        for tick in range(138):
            command += ((speed if tick >= 30 else 0.)-command)/12.
            obs = env.command(command, height, False)
            past_obs.append(obs)
            env.advance(DRIVE(torch.from_numpy(obs)).numpy())
    past = np.stack(past_obs[-12:])
    if dr == 0.:
        spec = mujoco.mjtState.mjSTATE_INTEGRATION
        integration = np.empty(mujoco.mj_stateSize(env.m, spec))
        mujoco.mj_getState(env.m, env.d, integration, spec)
        SAMPLES[key] = (integration, env.a_prev.copy(), past)
    return past


def trial(variables, speed, height, seed=51, dr=0., build=False):
    env = WORKER
    if env.wall_scene != "flat" or env.dr_scale != dr:
        env.setup(height, dr)
    history = prefill(speed, height, seed, dr).copy()
    press = env.frame()
    expert = Teacher(variables, env)
    frames, observations, histories, actions = [], [], [], []

    def inspect(frame):
        frames.append(frame)
        expert.inspect(frame)

    for step in range(112 if build else 86):
        obs = env.command(speed, height, step < HOLD_TICKS)
        action = expert.action(obs)
        history[:-1] = history[1:]
        history[-1] = obs
        if build:
            observations.append(obs.copy())
            histories.append(history.flatten().copy())
            actions.append(action.copy())
        env.advance(action, inspect)
        if env.tilt_fault:
            break
    result = measure(frames, Trial(seed, speed, height, dr), press, float("inf"), env.tilt_fault)
    return result, (observations, histories, actions)


def loss(variables):
    speed, height, smooth_landing, target = CONFIG
    result, _ = trial(variables, speed, height)
    peak = result["flight_peak_all_m"]
    objective = -peak if target is None else abs(peak-target)
    return (objective + .10*(result["fall"]) + .045*(not result["landed_running"])
            + .004*max(0., result["flight_pitch_deg"]-10.)
            + .30*max(0., .50*speed-result["min_charge_vx_m_s"])
            + .012*(result["charge_scrape_n"] > 1e-4) + .00012*min(120., result["charge_scrape_n"])
            + 5.*max(0., result["max_closure_m"]-CLOSURE_LIMIT)
            + .009*float(smooth_landing)*(result["landing_scrape_n"]>1.e-5))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--generations", type=int, default=22)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--speed", type=float, default=1.2)
    parser.add_argument("--height", type=float, default=.32)
    parser.add_argument("--seed-config", type=Path)
    parser.add_argument("--smooth-landing", action="store_true")
    parser.add_argument("--e0", action="store_true")
    parser.add_argument("--target-clearance", type=float)
    args = parser.parse_args()
    init_args = args.speed, args.height, args.smooth_landing, args.e0, args.target_clearance
    initialize(*init_args)
    initial = (json.loads((HERE/args.seed_config).read_text())["parameters"] if args.seed_config else INITIAL)
    initial = initial + INITIAL[len(initial):]
    nominal, _ = trial(initial, args.speed, args.height)
    print("initial", nominal, flush=True)
    def checkpoint(x, convergence):
        result, _ = trial(x, args.speed, args.height)
        json_save(args.out/"TEACHER_LATEST.json", dict(parameters=x.tolist(), cost=loss(x), metrics=result))
        print(f"cost={loss(x):.4f} peak={result['flight_peak_all_m']:.4f} "
              f"pitch={result['flight_pitch_deg']:.2f} charge={result['min_charge_vx_m_s']:.2f} "
              f"scrape={result['charge_scrape_n']:.2f} stable={result['landed_running']}", flush=True)
    with Pool(args.workers, initializer=initialize, initargs=init_args) as pool:
        rng = np.random.default_rng(771)
        lo, hi = np.asarray(BOUNDS).T
        population = np.clip(initial + rng.normal(0., .16, (32,len(INITIAL)))*(hi-lo), lo, hi)
        population[0] = initial
        best = differential_evolution(loss, BOUNDS, init=population, maxiter=args.generations,
                                      workers=pool.map, updating="deferred", polish=False, tol=.001,
                                      mutation=(.4,.82), recombination=.74, seed=101, callback=checkpoint)
    nominal, nominal_demo = trial(best.x, args.speed, args.height, seed=51, build=True)
    metrics, observations, history, actions = [nominal], [], [], []
    for speed in (.6, .8, 1., 1.2, 1.4, 1.6, 1.8, 2.):
        for height in (.22, .28, .32, .37, .42):
            for seed, dr in ((141, 0.), (171, .30)):
                record, demo = trial(best.x, speed, height, seed, dr, build=True)
                metrics.append(record)
                if (not record["fall"] and record["flight_peak_all_m"] >= .34 and record["forward_running"]
                        and record["charge_scrape_n"] < 1. and record["flight_pitch_deg"] < 16.
                        and record["landed_running"] and record["max_closure_m"] < CLOSURE_LIMIT):
                    observations.extend(demo[0])
                    history.extend(demo[1])
                    actions.extend(demo[2])
    if observations:
        if nominal["qualified"]:
            for _ in range(4):
                observations.extend(nominal_demo[0])
                history.extend(nominal_demo[1])
                actions.extend(nominal_demo[2])
        np.savez_compressed(args.out/"teacher.npz", obs=np.asarray(observations), hist=np.asarray(history),
                            act=np.asarray(actions))
    json_save(args.out/"TEACHER.json", dict(cost=float(best.fun), geom_min="2 tires, 8 guides, 8 base boxes",
                                          parameters=best.x.tolist(), samples=len(observations), nominal=nominal,
                                          trials=metrics))
    print("teacher finished", len(observations), "samples", flush=True)


if __name__ == "__main__":
    main()
