# SPDX-License-Identifier: MIT
"""Headless comparison of actual WASD inference at 50 Hz and contact evidence at 400 Hz."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET

os.environ.setdefault('MUJOCO_GL', 'disable')

import mujoco as mj
import numpy as np

from play_repaired import HERE, AutonomousMapSimulation, RepairedSimulation, load_candidate, load_manifest, load_parent, map_for, maps

RADIUS = .0625
CONTROL_DT = .02
SUPPORT_S = .40


@dataclass(frozen=True)
class Case:
    name: str
    target: float = .28
    yaw: float = 0.
    offset: float = 0.
    speed: float = .9
    duration: float = 7.5
    mode: str = 'climb'
    map_height: int = 20
    raise_while_moving: bool = False
    double: bool = False
    cancel_delay_s: float = .04
    restart_delay_s: float | None = None
    raise_at_s: float = .10
    jump_distance_m: float = .66
    drive_at_s: float = .40
    proving_lane: int | None = None


def cases(quick):
    single = [Case(f'h{round(h * 100):02}', target=h) for h in (.28, .36, .4, .42)]
    single += [Case('rise_h42', target=.42, raise_while_moving=True)]
    if not quick:
        single += [Case('h32', target=.32), Case('h38', target=.38),
                   Case('rise_h36', target=.36, raise_while_moving=True),
                   Case('rise_h40', target=.40, raise_while_moving=True)]
        single += [Case(f'h{h:02}', target=h/100) for h in (30, 34, 37, 39, 41)]
        single += [Case(f'h{round(h * 100):02}_offset{offset:+03}', target=h, offset=offset/1000)
                   for h in (.28, .32, .42) for offset in (-60, -30, 30, 60)]
        single += [Case(f'h{round(h * 100):02}_yaw{yaw:+03}', target=h, yaw=yaw)
                   for h in (.28, .42) for yaw in (-20, -10, 10, 20)]
        single += [Case(f'double_h{round(h * 100):02}', target=h, duration=12., double=True) for h in (.28, .42)]
        single += [Case('jump_idle_long', mode='jump_idle', duration=5.)]
        single += [Case(f'jump_{kind}_h{round(h * 100):02}', target=h, mode=f'jump_{kind}', duration=5.)
                   for kind in ('idle', 'moving') for h in (.36, .40, .42)]
    return single + [
        Case('stop_at_step', target=.42, mode='stop', duration=5.),
        Case('reverse_at_step', target=.42, mode='reverse', duration=5.),
        Case('turn_at_step', target=.42, mode='turn', duration=5.),
        Case('turn_while_w_at_step', target=.42, mode='turn_w', duration=5.),
        Case('wall_h28', map_height=50, duration=4., mode='wall'),
        Case('wall_h32', target=.32, map_height=50, duration=4.5, mode='wall'),
        Case('wall_h42', target=.42, map_height=50, duration=4., mode='wall'),
        Case('flat_rise', target=.42, raise_while_moving=True, mode='flat', duration=3.),
        Case('jump_idle', mode='jump_idle', duration=3.),
        Case('jump_moving', mode='jump_moving', duration=3.4),
        Case('jump_step20', mode='jump_step', duration=4.),
    ]


def takeover_cases():
    profiles = ((.28, -7, .11, .86), (.32, 5, .14, .91), (.34, 0, .21, .89), (.36, 0, .04, .9),
                (.39, -8, .07, .82), (.40, 8, .15, .90), (.42, 0, .30, .9))
    return [Case(f'{mode}_h{round(100*h)}_yaw{yaw:+03}_d{round(delay*1000):03}', target=h, yaw=yaw,
                 speed=speed, mode=mode, duration=5., cancel_delay_s=delay)
            for h, yaw, delay, speed in profiles for mode in ('stop', 'reverse', 'turn_w')]


def restart_cases():
    cases = [Case(f'restart_{mode}_h{round(100 * h):02}', target=h, mode=mode, duration=9.,
                  cancel_delay_s=.08, restart_delay_s=.92)
             for h in (.28, .32, .36, .40, .42) for mode in ('stop', 'reverse')]
    cases += [Case(f'restart_wall_h{round(100 * h):02}', target=h, mode='stop', map_height=50, duration=7.,
                   cancel_delay_s=.08, restart_delay_s=.92) for h in (.28, .36, .42)]
    cases += [Case(f'restart_stop_h42_v47_x{offset:+03}', target=.42, speed=.47, mode='stop', offset=offset / 1000,
                   duration=10., cancel_delay_s=.08, restart_delay_s=.92) for offset in (-60, 0, 60)]
    return cases


def load_case(sim, case):
    if case.proving_lane is not None:
        meta = map_for(0)
        idx = case.proving_lane
        names = {0: ['lane0_step1_20cm', 'lane0_step2_40cm'], 3: ['lane_stair200']}[idx]
    else:
        scene = '20 + 20 cm 连续双阶' if case.double else f'{case.map_height} cm 单阶'
        meta = map_for(4, scene)
        idx = 1 if case.mode == 'jump_step' else 0
        names = ['step_1_20cm', 'step_2_40cm'] if case.double else [f'matrix_step_{case.map_height}cm']
    pose = meta['spawns'][idx]
    pose['yaw_deg'] = case.yaw
    pose['x'] += case.offset
    if case.mode in ('flat', 'jump_idle', 'jump_moving'):
        scene_xml = Path(meta['xml_path'])
        tree = ET.parse(scene_xml)
        world = tree.find('worldbody')
        world.remove(world.find(f"geom[@name='{names[0]}']"))
        path = scene_xml.with_name('scene_wasd_eval_flat.xml')
        tree.write(path, encoding='utf-8', xml_declaration=True)
        meta['xml_path'] = str(path)
        names = []
    sim.load_map(meta, idx)
    sim.target_h = .28 if case.raise_while_moving else case.target
    sim.max_vx = case.speed
    return names


class ContactTrace:
    def __init__(self, sim, names):
        self.sim = sim
        self.tire = {int(gid): side for side, gid in enumerate(sim.tire_gids)}
        self.top = {}
        for i, name in enumerate(names):
            geom = sim.m.geom(name)
            edge = float(geom.pos[0] - geom.size[0])
            top = float(geom.pos[2] + geom.size[2])
            self.top[geom.id] = (i, edge, top)
        self.force_buffer = np.zeros(6)
        self.rows = []
        self.hits = [None] * len(self.top)
        self.peak_hit_n = np.zeros(len(self.top))
        self.first_other_floor = None

    def add(self, m, d):
        sim = self.sim
        support = np.zeros((len(self.top), 2))
        wheel = np.zeros(2)
        for index in range(d.ncon):
            c = d.contact[index]
            a, b = map(int, c.geom)
            platform, other = (a, b) if a in self.top else (b, a)
            is_step = platform in self.top
            if not is_step and other not in self.tire and platform not in self.tire:
                continue
            mj.mj_contactForce(m, d, index, self.force_buffer)
            normal = abs(float(self.force_buffer[0]))
            if is_step:
                i, edge, top = self.top[platform]
                is_top = abs(c.frame[2]) > .72 and c.pos[0] > edge + .004 and abs(c.pos[2] - top) < .014
                if is_top and other in self.tire:
                    support[i, self.tire[other]] += normal
                elif c.pos[0] < edge + .045:
                    self.peak_hit_n[i] = max(self.peak_hit_n[i], normal)
                    if normal > 5. and self.hits[i] is None:
                        self.hits[i] = {'t': float(d.time), 'normal_n': normal, 'body_z': float(d.qpos[2]),
                                        'geom': m.geom(other).name, 'body': m.body(m.geom_bodyid[other]).name}
            for tire_id in self.tire.keys() & {a, b}:
                wheel[self.tire[tire_id]] += normal
        rotation = d.xmat[sim.env.base_id].reshape(3, 3)
        pitch = np.rad2deg(np.arcsin(np.clip(-rotation[2, 0], -1., 1.)))
        yaw = np.rad2deg(np.arctan2(rotation[1, 0], rotation[0, 0]))
        tires = d.geom_xpos[sim.tire_gids]
        self.rows.append([float(d.time), *d.qpos[:3], *d.qvel[:3], pitch, yaw,
                          float(tires[:, 2].min() - RADIUS), float(tires[:, 0].min()),
                          *wheel, *support.ravel()])


def longest_streak(t, mask, dt):
    start = np.flatnonzero(np.diff(np.r_[False, mask, False].astype(int)) > 0)
    end = np.flatnonzero(np.diff(np.r_[False, mask, False].astype(int)) < 0)
    length = end - start
    first = np.flatnonzero(length * dt >= SUPPORT_S - 1e-9)
    return round(float(length.max(initial=0) * dt), 5), (float(t[start[first[0]]]) if len(first) else None)


def run_case(sim, case, out, video=False, before_step=None):
    names = load_case(sim, case)
    trace = ContactTrace(sim, names)
    trace.add(sim.m, sim.d)
    normal_step = mj.mj_step

    def instrumented_step(m, d):
        normal_step(m, d)
        trace.add(m, d)

    tick_rows = []
    observations = []
    replay_states = []
    request = cancel = restart = None
    resets = 0
    mj.mj_step = instrumented_step
    try:
        for k in range(round(case.duration / CONTROL_DT)):
            now = k * CONTROL_DT
            keys = {'w'} if now >= case.drive_at_s and case.mode != 'jump_idle' else set()
            if (case.raise_while_moving and now >= case.raise_at_s
                    and sim.target_h + 1e-8 < case.target):
                keys.add('e')
            if (case.mode in ('stop', 'reverse', 'turn', 'turn_w') and trace.hits[0]
                    and now >= trace.hits[0]['t'] + case.cancel_delay_s):
                if cancel is None:
                    cancel = now
                if case.restart_delay_s is None or now < cancel + case.restart_delay_s - 1e-9:
                    keys = {'s'} if case.mode == 'reverse' else {'a'} if case.mode == 'turn' else {'w', 'a'} if case.mode == 'turn_w' else set()
                elif restart is None:
                    restart = now
            if (case.mode == 'jump_idle' and k == 50 or case.mode == 'jump_moving' and k == 64
                    or case.mode == 'jump_step' and request is None and now >= case.drive_at_s + .04 - 1.e-9 and
                    list(trace.top.values())[0][1] - np.mean(sim.d.geom_xpos[sim.tire_gids, 0]) <= case.jump_distance_m):
                if sim.request_jump():
                    request = now
            if before_step is not None:
                before_step(sim, trace, now, keys)
            last_time = float(sim.d.time)
            sim.step(keys)
            if sim.d.time < last_time:
                resets += 1
                break
            observations.append(sim.last_obs.copy())
            if video and k % 2 == 0:
                replay_states.append(sim.d.qpos.copy())
            raw = sim.route.get('g_prob', sim.route['e1'] * .95 + .05 if sim.route['e1'] else 0.)
            tick_rows.append([now, sim.cmd_vx, sim.cmd_wz, sim.target_h, raw, sim.route['e1'], sim.route['e2'],
                              *sim.prev_a.tolist(), float('w' in keys), float('s' in keys), float('a' in keys),
                              sim.route.get('virtual_velocity', np.nan), sim.route.get('virtual_height', np.nan)])
    finally:
        mj.mj_step = normal_step
    a = np.array(trace.rows)
    u = np.array(tick_rows)
    dt = float(sim.m.opt.timestep)
    t = a[:, 0]
    if out is not None:
        np.savez_compressed(out / (case.name + '.npz'), physical=a, control=u, obs=np.array(observations),
                            physical_columns=['t', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'pitch_deg', 'yaw_deg',
                                              'min_rim_z', 'min_wheel_x', 'fl_n', 'fr_n'] +
                                             [f'support_{name}_{side}_n' for name in names for side in ('L', 'R')],
                            control_columns=['t', 'cmd_vx', 'cmd_wz', 'height_cmd', 'gate_raw', 'gate_e1', 'gate_e2',
                                             'a0', 'a1', 'a2', 'a3', 'a4', 'a5', 'w', 's', 'a', 'virtual_v', 'virtual_h'])
    geometry = []
    for i, name in enumerate(names):
        _, edge, top = list(trace.top.values())[i]
        # Record each physical contact, then require both tires to carry load in every
        # 20 ms control window. Using 5 N at every 2.5 ms solver sample would reject
        # ordinary rolling as the tire's discrete contact patches alternate.
        n_sub = round(CONTROL_DT / dt)
        b = a[1:1 + (len(a) - 1) // n_sub * n_sub].reshape(-1, n_sub, a.shape[-1])
        tick_end = b[:, -1]
        mean_normal = b[:, :, 13 + i * 2:15 + i * 2].mean(1)
        top_pose = (tick_end[:, 10] > edge + .004) & (tick_end[:, 1] > edge + .02)
        supported = (mean_normal >= 5.).all(1) & top_pose
        streak, held_at = longest_streak(tick_end[:, 0], supported, CONTROL_DT)
        first_top = float(tick_end[supported, 0][0]) if supported.any() else None
        hit = trace.hits[i]
        during = np.zeros(len(a), dtype=bool) if hit is None else t >= hit['t'] - dt * .1
        if held_at is not None:
            during &= t <= held_at + SUPPORT_S
        if cancel is not None and restart is None:
            during &= t <= cancel
        x = a[during, 1]
        gate_before_end = u[:, 0] < (held_at + SUPPORT_S if held_at is not None else np.inf)
        gate_on_hit = u[(u[:, 0] >= hit['t'] - CONTROL_DT) & gate_before_end, 5] if hit is not None else []
        recovery = None if held_at is None else float(a[np.argmin(np.abs(t - held_at - SUPPORT_S)), 3] - top)
        slip = bool(held_at is not None and np.any((t > held_at + SUPPORT_S) & (a[:, 10] < edge - .02)))
        geometry.append({'name': name, 'hit': hit, 'peak_face_force_n': float(trace.peak_hit_n[i]),
                         'both_top_s': streak, 'first_dual_support_s': first_top, 'first_held_from_s': held_at, 'slid_back': slip,
                         'first_activation_s': float(u[u[:, 5] >= .5, 0][0]) if (u[:, 5] >= .5).any() else None,
                         'e1_precontact_peak': float(u[u[:, 0] < hit['t'], 5].max(initial=0)) if hit else float(u[:, 5].max()),
                         'top_height_after_hold_m': recovery, 'peak_e1_after_hit': float(np.max(gate_on_hit, initial=0)),
                         'backtrack_m': float((np.maximum.accumulate(x) - x).max()) if len(x) else None,
                         'min_vx_m_s': float(a[during, 4].min()) if len(x) else None})
    summary = {'name': case.name, 'mode': case.mode, 'height_cmd_m': case.target, 'yaw_deg': case.yaw,
               'fell': bool(np.min(a[:, 3]) < .13 or np.max(np.abs(a[:, 7])) > 44.),
               'peak_vx_m_s': float(np.abs(a[:, 4]).max()), 'peak_pitch_deg': float(np.abs(a[:, 7]).max()),
               'final_dx_m': float(a[-1, 1] - a[0, 1]), 'final_body_z_m': float(a[-1, 3]),
               'final_pitch_deg': float(a[-1, 7]), 'resets': resets,
               'raw_gate_peak': float(u[:, 4].max()), 'e1_peak': float(u[:, 5].max()),
               'seconds_e1_gt_50pct': round(float((u[:, 5] > .5).sum()) * CONTROL_DT, 4), 'steps': geometry}
    if case.mode == 'wall' and trace.hits[0]:
        wall_late = u[u[:, 0] >= trace.hits[0]['t'] + 1.]
        summary['wall_gate_after_one_second'] = float(wall_late[:, 5].max(initial=0))
    if cancel is not None:
        window_end = restart if restart is not None else np.inf
        b = a[(t >= cancel) & (t <= window_end)]
        override_u = u[(u[:, 0] >= cancel - .001) & (u[:, 0] < window_end)]
        first_cmd = override_u[0, 1:3]
        summary['override'] = {'t': cancel, 'first_cmd_vx': float(first_cmd[0]), 'first_cmd_wz': float(first_cmd[1]),
                               'forward_overshoot_m': float(b[:, 1].max() - b[0, 1]),
                               'max_abs_dx': float(np.abs(b[:, 1] - b[0, 1]).max()), 'peak_e1': float(override_u[:, 5].max()),
                               'final_dx': float(b[-1, 1] - b[0, 1]), 'min_vx': float(b[:, 4].min()),
                               'yaw_change_deg': float((b[-1, 8] - b[0, 8] + 180) % 360 - 180),
                               'vx_last_200ms': float(b[-min(80, len(b)):, 4].mean()),
                               'peak_pitch_deg': float(np.abs(b[:, 7]).max()),
                               'minimum_body_height_m': float(b[:, 3].min())}
    if restart is not None:
        resumed = u[u[:, 0] >= restart - 1e-9]
        body = a[t >= restart - dt * .1]
        first_active = resumed[resumed[:, 5] >= .5, 0]
        top_s = geometry[0]['first_held_from_s']
        dx = body[:, 1] - body[0, 1]
        summary['restart'] = {
            't': restart,
            'body_height_at_restart_m': float(body[0, 3]),
            'first_e1_delay_s': float(first_active[0] - restart) if len(first_active) else None,
            'first_dual_hold_delay_s': top_s - restart if top_s is not None and top_s >= restart else None,
            'peak_e1': float(resumed[:, 5].max()),
            'peak_e1_after_one_s': float(resumed[resumed[:, 0] >= restart + 1., 5].max(initial=0)),
            'backtrack_m': float((np.maximum.accumulate(dx) - dx).max()),
            'final_dx_m': float(dx[-1]),
        }
    if request is not None:
        b = a[t >= request - dt * .1]
        under_load = (b[:, 11:13] > 2.).any(1)
        floor_z = sim.jump_launch_gz
        flight_mask = (~under_load) & (b[:, 9] > floor_z + .018)
        takeoff = np.flatnonzero(flight_mask)
        land = np.array([], dtype=int)
        if len(takeoff):
            land = np.flatnonzero((np.arange(len(b)) > takeoff[0]) & under_load)
        flight = b[takeoff[0]:(land[0] if len(land) else len(b))] if len(takeoff) else b[:0]
        after = b[land[0]:] if len(land) else b[:0]
        dx = b[:, 1] - b[0, 1]
        active = u[u[:, 6] > .5, 0]
        major_flights = []
        if len(active):
            in_window = (b[:, 0] >= active[0] - dt * .1) & (b[:, 0] <= active[-1] + CONTROL_DT + dt * .1)
            edges = np.flatnonzero(np.diff(np.r_[False, flight_mask & in_window, False]))
            for start, end in zip(edges[::2], edges[1::2], strict=True):
                if (end - start) * dt < .12:
                    continue
                samples = b[start:end]
                major_flights.append({'takeoff_s': float(samples[0, 0] - request), 'duration_s': (end-start)*dt,
                                      'clearance_m': float(samples[:, 9].max() - floor_z),
                                      'takeoff_vx_m_s': float(samples[0, 4]),
                                      'peak_pitch_deg': float(np.abs(samples[:, 7]).max())})
        main_flight = max(major_flights, key=lambda row: row['clearance_m'], default=None)
        summary['jump'] = {'requested_at_s': request, 'main_flight': main_flight,
                           'e2_first_at_s': float(active[0]) if len(active) else None,
                           'e2_last_at_s': float(active[-1]) if len(active) else None,
                           'major_flights': len(major_flights), 'first_air_s': float(flight[0, 0] - request) if len(flight) else None,
                           'first_landing_s': float(after[0, 0] - request) if len(after) else None,
                           'clearance_m': float(flight[:, 9].max() - floor_z) if len(flight) else 0.,
                           'air_peak_pitch_deg': float(np.abs(flight[:, 7]).max()) if len(flight) else None,
                           'landing_peak_pitch_deg': float(np.abs(after[:, 7]).max()) if len(after) else None,
                           'max_backtrack_m': float((np.maximum.accumulate(dx) - dx).max()),
                           'min_dx_m': float(dx.min()), 'end_dx_m': float(dx[-1]),
                           'recovery_vx_m_s': float(np.mean(b[-min(80, len(b)):, 4])),
                           'command_vx_at_end_m_s': float(u[-1, 1]),
                           'peak_post_land_retreat_m': float((np.maximum.accumulate(after[:, 1]) - after[:, 1]).max())
                               if len(after) else None}
    if video:
        render_rollout(sim.m, replay_states, out / (case.name + '_1X.mp4'))
    return summary


def render_rollout(model, states, path):
    import imageio.v2 as imageio

    d = mj.MjData(model)
    camera = mj.MjvCamera()
    camera.azimuth = 81.
    camera.elevation = -16.
    camera.distance = 2.45
    with mj.Renderer(model, height=480, width=720) as renderer:
        with imageio.get_writer(path, fps=25, codec='libx264', quality=7) as writer:
            for state in states:
                d.qpos[:] = state
                mj.mj_forward(model, d)
                camera.lookat[:] = [d.qpos[0] + .35, d.qpos[1], max(.30, d.qpos[2])]
                renderer.update_scene(d, camera=camera)
                writer.append_data(renderer.render())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    source = parser.add_mutually_exclusive_group()
    source.add_argument('--parent', action='store_true', help='Run the deployed Gemini WASD path.')
    source.add_argument('--candidate', type=Path, help='Load the exact interactive player manifest.')
    parser.add_argument('--quick', action='store_true')
    parser.add_argument('--video', action='store_true')
    parser.add_argument('--cases', nargs='+')
    parser.add_argument('--speed-sweep', action='store_true', help='Add the 0.47 m/s approach cases.')
    parser.add_argument('--takeover-sweep', action='store_true', help='Add varied operator takeover cases.')
    parser.add_argument('--restart-sweep', action='store_true', help='Add stop and reverse followed by renewed forward intent.')
    for role in ('stair', 'router', 'jump'):
        parser.add_argument('--' + role, type=Path)
    parser.add_argument('--keep-fast-moving-jump', action='store_true')
    parser.add_argument('--stair-height-bank', type=Path)
    parser.add_argument('--high-router', type=Path)
    parser.add_argument('--jump-stance-prep', action='store_true')
    parser.add_argument('--jump-min-forward', type=float, default=0.0)
    parser.add_argument('--gate-floor', type=float, default=.05)
    parser.add_argument('--gate-release', type=float, default=1.0)
    args = parser.parse_args()
    maps.CACHE_DIR = HERE / 'runtime_cache' / f'wasd_eval_{args.out.name}_{os.getpid()}'
    if args.parent:
        policy, sha = load_parent()
        hashes = {'package': sha}
        sim = AutonomousMapSimulation(policy, sha, show_viewer=False)
    elif args.candidate:
        policy, hashes, args.jump_stance_prep = load_manifest(args.candidate)
        args.gate_floor = policy.stair_gate_floor
        args.gate_release = policy.stair_release_per_tick
        args.jump_min_forward = policy.jump_min_forward
        sim = RepairedSimulation(policy, hashes['package'], show_viewer=False, jump_stance_prep=args.jump_stance_prep)
    else:
        policy, hashes = load_candidate(args.stair, args.router, args.jump, keep_fast_moving_jump=args.keep_fast_moving_jump,
                                        stair_height_bank=args.stair_height_bank, high_router_path=args.high_router)
        policy.jump_min_forward = args.jump_min_forward
        policy.stair_gate_floor = args.gate_floor
        policy.stair_release_per_tick = args.gate_release
        sim = RepairedSimulation(policy, hashes['package'], show_viewer=False, jump_stance_prep=args.jump_stance_prep)
    results = []
    planned = cases(args.quick)
    if args.speed_sweep:
        planned += [Case(f'low_speed_h{int(100*h)}_offset{offset:+03}', target=h, offset=offset/1000, speed=.47,
                         duration=10.) for h in (.28, .42) for offset in (-60, -30, 0, 30, 60)]
    if args.takeover_sweep:
        planned += takeover_cases()
    if args.restart_sweep:
        planned += restart_cases()
    relevant = [c for c in planned if args.cases is None or c.name in args.cases]
    if args.cases is not None and set(args.cases) != {c.name for c in relevant}:
        raise ValueError(f'Unknown cases: {sorted(set(args.cases) - {c.name for c in relevant})}')
    args.out.mkdir(parents=True, exist_ok=False)
    for case in relevant:
        result = run_case(sim, case, args.out, video=args.video)
        results.append(result)
        print(json.dumps(result, ensure_ascii=False, allow_nan=False), flush=True)
        (args.out / 'WASD.json').write_text(json.dumps({'sha256': hashes, 'runtime_sha256': getattr(policy, 'runtime_sha', None),
                                  'gate_floor': args.gate_floor, 'gate_release_per_tick': args.gate_release,
                                  'jump_stance_prep': args.jump_stance_prep,
                                  'jump_min_forward': args.jump_min_forward,
                                  'handoff_gains': None if args.parent or policy.handoff_gains is None else policy.handoff_gains.ravel().tolist(),
                                  'handoff_duration': None if args.parent else policy.handoff_duration,
                                  'immediate_stair_stop': False if args.parent else policy.immediate_stair_stop,
                                  'results': results}, ensure_ascii=False,
            allow_nan=False, indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
