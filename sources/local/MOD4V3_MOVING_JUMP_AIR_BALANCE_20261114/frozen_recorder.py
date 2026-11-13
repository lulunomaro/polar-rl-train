"""Frozen, fully instrumented first-episode replays of the approved R3 player."""
from pathlib import Path
import argparse
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

T = Path(__file__).resolve().parent
R = T.parents[2]
D = R / 'deliveries/MOD4V3_BEST_MANUAL_STAIRS_20261112'
TEACHER = T.parent / 'MOD4V3_STAIRS_SPECIALIST_TEACHER_40M_20261113'
MODELS = {
    'teacher': (TEACHER / 'weights/selected_stair_teacher.pt', '715c40b6bd18c51d050d0bae38c0d04008f3841cc4a40ddca980a9cd52623ff5'),
    'parent': (TEACHER / 'frozen_parent/best_parent_full_ppo.pt', 'db6e9ccf5c6d4d05a68633fd82861d903c4c52fcc1a6dd89132e55e2a4bf1283'),
}
STARTS = [(-3.9, 0., 0.), (-3.75, -.12, -.03), (-3.6, .12, .03), (-3.99, .06, -.04), (-3.8, -.06, .04)]


def setup(out, model):
    torch.set_num_threads(1)
    spec = importlib.util.spec_from_file_location('low_speed_frozen_showcase', D / 'viewer/showcase.py')
    show = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(show)
    show.B = out / 'scene_assets'
    (show.B / 'tiles').mkdir(parents=True, exist_ok=True)
    show.CKPT, show.EXPECTED = MODELS[model]
    assert hashlib.sha256(show.CKPT.read_bytes()).hexdigest() == show.EXPECTED
    with np.load(D / 'viewer/tiles/r03_c00.npz') as source:
        vertices = source['vertices'].copy()
        vertices[:, 2] *= .2 / float(np.unique(vertices[:, 2])[1])
        np.savez_compressed(show.B / 'tiles/r03_c00.npz', vertices=vertices, faces=source['faces'])
    sys.path.insert(0, str(T / 'reference'))
    from replay_training_guards import replay_step
    show.Replay.step = replay_step(show.Simulation, show.SafetyStop, duration_steps=10, event_dir=out / 'reset_events')
    return show


def geom_points(model, gid):
    typ = int(model.geom_type[gid])
    if typ == int(mujoco.mjtGeom.mjGEOM_MESH):
        mid = int(model.geom_dataid[gid])
        a, n = int(model.mesh_vertadr[mid]), int(model.mesh_vertnum[mid])
        return model.mesh_vert[a:a+n].copy()
    center, half = model.geom_aabb[gid, :3], model.geom_aabb[gid, 3:]
    return np.asarray([[x, y, z] for x in [-1, 1] for y in [-1, 1] for z in [-1, 1]]) * half + center


class Recorder:
    def __init__(self, sim):
        self.sim = sim
        self.e, self.m, self.d = sim.env, sim.env.m, sim.env.d
        self.wheels = [self.m.body(x).id for x in ('left_wheel_link', 'right_wheel_link')]
        self.guides = sorted({int(self.m.geom_bodyid[i]) for i in range(self.m.ngeom) if self.m.geom(i).name.startswith('guide_wheel_')})
        self.robot = [i for i in range(1, self.m.nbody) if float(self.m.body_mass[i]) > 0]
        self.chassis_geoms = [(i, geom_points(self.m, i)) for i in range(self.m.ngeom) if self.m.geom_bodyid[i] == self.e.base_id and self.m.geom_contype[i] != 0]
        self.front_joints = [self.m.joint(x).id for x in ('left_front1_joint', 'right_front1_joint')]
        self.data = {}
        self.landings, self.wall_first = {}, {}
        self.snapshots = []
        self.max_closure = 0.
        self.local_force = np.zeros(6)
        self.last_wall = np.zeros((2, 2))

    def add(self, key, value):
        self.data.setdefault(key, []).append(np.asarray(value).copy())

    def sample(self):
        m, d, e = self.m, self.d, self.e
        forces = np.zeros((m.nbody, 3))
        tread = np.zeros((2, 2))
        wall = np.zeros((2, 2))
        for ci in range(d.ncon):
            contact = d.contact[ci]
            g1, g2 = int(contact.geom1), int(contact.geom2)
            b1, b2 = int(m.geom_bodyid[g1]), int(m.geom_bodyid[g2])
            if (b1 == 0) == (b2 == 0):
                continue
            terrain, robot, sign = (g1, b2, 1.) if b1 == 0 else (g2, b1, -1.)
            mujoco.mj_contactForce(m, d, ci, self.local_force)
            frame = np.asarray(contact.frame).reshape(3, 3)
            force = sign * frame.T @ self.local_force[:3]
            normal = sign * frame[0]
            forces[robot] += force
            name = m.geom(terrain).name
            if name in ('step_1', 'step_2'):
                level = int(name[-1])
                if robot in self.wheels:
                    wi = self.wheels.index(robot)
                    if normal[2] > .7 and self.local_force[0] > 5:
                        tread[level-1, wi] += max(0., force[2])
                    if abs(normal[0]) > .7:
                        wall[level-1, wi] += max(0., self.local_force[0])
                if (robot in self.wheels or robot in self.guides) and abs(normal[0]) > .7 and self.local_force[0] > 5 and level not in self.wall_first:
                    self.wall_first[level] = len(self.data.get('time', []))
        for level in (1, 2):
            if (tread[level-1] > 5).all() and level not in self.landings:
                self.landings[level] = len(self.data.get('time', []))
        points = np.concatenate([p @ d.geom_xmat[g].reshape(3, 3).T + d.geom_xpos[g] for g, p in self.chassis_geoms])
        chassis_min, chassis_max = points.min(axis=0), points.max(axis=0)
        wheel = d.xpos[self.wheels].copy()
        hip = d.xanchor[self.front_joints].copy()
        length = np.linalg.norm(wheel - hip, axis=1)
        body_length = np.linalg.norm(wheel - d.xpos[e.base_id], axis=1)
        cl = max(float(np.linalg.norm(d.site_xpos[u] - d.site_xpos[v])) for u, v in self.sim.pairs)
        self.max_closure = max(self.max_closure, cl)
        self.sim.closure = cl
        rotation = d.xmat[e.base_id].reshape(3, 3)
        pitch = math.degrees(math.asin(float(np.clip(-rotation[2, 0], -1, 1))))
        roll = math.degrees(math.atan2(float(rotation[2, 1]), float(rotation[2, 2])))
        yaw = math.degrees(math.atan2(float(rotation[1, 0]), float(rotation[0, 0])))
        for key, value in {
            'time': d.time - e.dt, 'root': d.xpos[e.base_id], 'com': d.subtree_com[e.base_id],
            'qpos_after': d.qpos, 'qvel_after': d.qvel, 'wheel': wheel,
            'hip_to_wheel': length, 'root_to_wheel': body_length,
            'wheel_upper_clearance': wheel[:, 2, None] - .0625 - np.array([.2, .4]),
            'wheel_edge_dx': wheel[:, 0, None] - np.array([-2.9, -1.4]),
            'chassis_min': chassis_min, 'chassis_max': chassis_max,
            'com_edge_dx': d.subtree_com[e.base_id, 0] - np.array([-2.9, -1.4]),
            'pose_deg': [pitch, roll, yaw], 'vx_body': e.vx,
            'torque_env_order': d.ctrl[e.act_ids], 'body_contact_force': forces,
            'wheel_tread_fz': tread, 'wheel_wall_normal': wall,
            'closure': cl, 'command': [self.sim.cmd_vx, self.sim.cmd_wz, self.sim.height],
        }.items():
            self.add(key, value)
        self.last_wall = wall
        return cl

    def snapshot(self):
        spec = mujoco.mjtState.mjSTATE_INTEGRATION
        state = np.empty(mujoco.mj_stateSize(self.m, spec))
        mujoco.mj_getState(self.m, self.d, state, spec)
        s = self.sim
        self.snapshots.append({
            'state': state, 'time': float(self.d.time), 'a_prev': s.a_prev.numpy().copy(),
            'env_a_prev': self.e.a_prev.numpy().copy(),
            'base_xmat': self.d.xmat[self.e.base_id].copy(),
            'commands': [s.cmd_vx, s.cmd_vy, s.cmd_wz, s.height],
            'guard': [getattr(s, '_repair_contact_steps', 0), getattr(s, '_replay_tilt_steps', 0), getattr(s, '_repair_stair_stage', 0)],
        })

    def save(self, path):
        arrays = {k: np.asarray(v) for k, v in self.data.items()}
        for key in ('state', 'time', 'a_prev', 'env_a_prev', 'base_xmat', 'commands', 'guard'):
            arrays['snapshot_' + key] = np.asarray([x[key] for x in self.snapshots])
        arrays['body_names'] = np.asarray([self.m.body(i).name for i in range(self.m.nbody)])
        arrays['actuated_joint_names'] = np.asarray([self.e.spec.joint_names[j] for j in self.e.spec.act_idx])
        arrays['wheel_body_ids'] = np.asarray(self.wheels)
        arrays['guide_body_ids'] = np.asarray(self.guides)
        arrays['base_body_id'] = np.asarray(self.e.base_id)
        np.savez_compressed(path, **arrays)
        return arrays


def run_case(show, out, model, speed, seed, seconds, angle=None, intervention=None, restore=None):
    name = f'{model}_v{speed:.1f}_s{seed}' + (f'_yaw{angle:+g}' if angle is not None else '')
    if intervention:
        name += '_' + intervention
    dest = out / name
    dest.mkdir(exist_ok=False)
    sim = show.Replay(level=3, direction='up', show=False)
    sim.args.vx = speed
    x, y, yaw = STARTS[seed]
    if angle is not None:
        yaw = math.radians(angle)
        y = (seed - 2) * .04 + (x + 1.1) * math.tan(yaw)
    e, m, d = sim.env, sim.env.m, sim.env.d
    d.qpos[:3] = [x, y, sim.ground(x, y) + e.bank_z]
    d.qpos[3:7] = [math.cos(yaw/2), 0., 0., math.sin(yaw/2)]
    d.qvel[:] = 0.
    mujoco.mj_forward(m, d)
    sim.reset_count, sim.reason = 1, ''
    recorder = Recorder(sim)

    def physics(env, action):
        action = action.clamp(-env.action_clip, env.action_clip)
        for j in range(env.decim):
            torque = env._torque(action).detach().numpy().reshape(-1)
            if j % 4 == 0:
                d.ctrl[env.act_ids[:4]] = torque[:4]
            d.ctrl[env.act_ids[4:]] = torque[4:]
            mujoco.mj_step(m, d)
            closure = recorder.sample()
            if not np.isfinite(d.qpos).all() or not np.isfinite(d.qvel).all():
                raise show.SafetyStop('nonfinite')
            if closure > .002:
                raise show.SafetyStop('closure>2mm')
        env.a_prev = action.detach()
        return env.state()

    e.step = types.MethodType(physics, e)
    if restore is not None:
        state = np.load(restore['path'])
        index = restore['index']
        integration = state['snapshot_state'][index].copy()
        mujoco.mj_setState(m, d, integration, mujoco.mjtState.mjSTATE_INTEGRATION)
        mujoco.mj_forward(m, d)
        mujoco.mj_setState(m, d, integration, mujoco.mjtState.mjSTATE_INTEGRATION)
        if 'snapshot_base_xmat' in state:
            d.xmat[e.base_id] = state['snapshot_base_xmat'][index]
        else:
            last = int(np.abs(state['time'] - (d.time - e.dt)).argmin())
            rotation = np.empty(9)
            mujoco.mju_quat2Mat(rotation, state['qpos_after'][last-1, 3:7])
            d.xmat[e.base_id] = rotation
        sim.a_prev = torch.tensor(state['snapshot_a_prev'][index])
        e.a_prev = torch.tensor(state['snapshot_env_a_prev'][index])
        sim.cmd_vx, sim.cmd_vy, sim.cmd_wz, sim.height = map(float, state['snapshot_commands'][index])
        sim._repair_contact_steps, sim._replay_tilt_steps, sim._repair_stair_stage = map(int, state['snapshot_guard'][index])
        sim._replay_last_time = float(d.time)
        start_time = float(d.time)
    else:
        start_time = 0.
    if intervention and intervention.startswith('retract'):
        pulse_parameters = list(map(float, intervention[7:].split('_')))
        target_delta, pulse_duration = pulse_parameters[:2]
        mean_offset = pulse_parameters[2] if len(pulse_parameters) > 2 else 0.
        frozen_actor = sim.actor
        default = sim.default_active
        class RetractionPulse(torch.nn.Module):
            def forward(self, obs):
                raw = frozen_actor(obs)
                elapsed = float(d.time) - start_time
                if 0. <= elapsed < pulse_duration:
                    alpha = min(1., elapsed / .08)
                    delta = 1.75 + (target_delta - 1.75) * alpha
                    result = raw.clone()
                    for front, rear in ((0, 1), (2, 3)):
                        mean = .5 * (default[front] + .5 * raw[:, front] + default[rear] + .5 * raw[:, rear]) + mean_offset * alpha
                        result[:, front] = 2. * (mean + delta / 2. - default[front])
                        result[:, rear] = 2. * (mean - delta / 2. - default[rear])
                    return result
                return raw
        sim.actor = RetractionPulse()
    hold, success = 0., False
    wall_start = time.time()
    try:
        for k in range(int(math.ceil(seconds / .02))):
            now = float(d.time)
            sim.set_height(.28 + .14 * min(now / 2., 1.))
            if intervention and now >= start_time:
                elapsed = now - start_time
                if intervention.startswith('height'):
                    target = float(intervention[6:])
                    sim.set_height(max(target, .42 - .7 * elapsed) if elapsed < .32 else min(.42, target + .35 * (elapsed - .32)))
            sim.step({'w'} if now >= 3. else set())
            if sim.reset_count != 1:
                break
            recorder.snapshot()
            wheel = d.xpos[recorder.wheels]
            on_top = bool((np.abs(wheel[:, 0]) < 1.4).all() and (np.abs(wheel[:, 1]) < 1.4).all() and (wheel[:, 2] > .3925).all())
            goal = 2 in recorder.landings and on_top
            hold = hold + .02 if goal else 0.
            success = hold >= .3
            if success:
                break
        arrays = recorder.save(dest / 'trajectory.npz')
        def event(level, source):
            idx = source.get(level)
            if idx is None:
                return None
            return {key: np.asarray(arrays[key][idx]).tolist() for key in ('time', 'root', 'com', 'wheel', 'hip_to_wheel', 'chassis_min', 'chassis_max', 'pose_deg', 'vx_body', 'wheel_wall_normal', 'body_contact_force')}
        land = {str(level): event(level, recorder.landings) for level in (1, 2)}
        first, second = recorder.landings.get(1), recorder.landings.get(2)
        row = dict(id=name, model=model, sha256=show.EXPECTED, speed_command=speed, seed=seed, initial=[x, y, yaw],
                   success=success, first_landed=first is not None, second_landed=second is not None,
                   first_to_second_s=float(arrays['time'][second]-arrays['time'][first]) if first is not None and second is not None else None,
                   first_riser=event(1, recorder.wall_first), second_riser=event(2, recorder.wall_first), landings=land,
                   reason=sim.reason or ('completed' if success else 'timeout'), simulated_s=float(arrays['time'][-1]),
                   wall_s=time.time()-wall_start, max_closure_m=recorder.max_closure, optimizer_updates=0,
                   intervention=intervention, restore=restore,
                   physics_s=.0025, legs_hz=100, wheels_hz=400, policy_hz=50,
                   geometry_time_note='Transforms and contact forces are from mj_step start; qpos_after/qvel_after are end-of-step. No mj_forward was inserted in the dynamics loop.')
        (dest / 'RESULT.json').write_text(json.dumps(row, indent=2) + '\n', encoding='utf8')
        print(json.dumps({k: row[k] for k in ('id', 'success', 'first_landed', 'second_landed', 'reason', 'simulated_s', 'wall_s')}), flush=True)
        return row
    finally:
        sim.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=list(MODELS), required=True)
    parser.add_argument('--out', required=True)
    parser.add_argument('--speeds', type=float, nargs='+', default=[.2, .4, .6, .8, 1., 1.8, 2.2])
    parser.add_argument('--seeds', type=int, nargs='+', default=list(range(5)))
    parser.add_argument('--seconds', type=float, default=24.)
    parser.add_argument('--angle', type=float)
    parser.add_argument('--restore')
    parser.add_argument('--snapshot', type=int)
    parser.add_argument('--intervention')
    parser.add_argument('--checkpoint')
    args = parser.parse_args()
    if args.checkpoint:
        path = Path(args.checkpoint).resolve()
        MODELS[args.model] = (path, hashlib.sha256(path.read_bytes()).hexdigest())
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    show = setup(out, args.model)
    rows = []
    for speed in args.speeds:
        for seed in args.seeds:
            restore = dict(path=str(Path(args.restore).resolve()), index=args.snapshot) if args.restore else None
            rows.append(run_case(show, out, args.model, speed, seed, args.seconds, args.angle, args.intervention, restore))
            (out / f'PROGRESS_{args.model}.json').write_text(json.dumps(dict(completed=len(rows), rows=rows), indent=2) + '\n')


if __name__ == '__main__':
    main()
