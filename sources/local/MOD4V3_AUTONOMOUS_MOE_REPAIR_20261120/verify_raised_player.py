# SPDX-License-Identifier: MIT
# Drive the real StepPlayer poll/tick and Tcl callbacks with a virtual clock.
# Only the viewer and hardware keyboard state are replaced.
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import sys
import time
import tkinter as tk
from types import SimpleNamespace

os.environ['MUJOCO_GL'] = 'disable'
import mujoco as mj
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, required=True)
parser.add_argument('--r61', action='store_true', help='Replay the archived R61 player and candidate.')
parser.add_argument('--proving-ground', action='store_true')
parser.add_argument('--only', nargs='+')
parser.add_argument('--manifest', type=Path)
parser.add_argument('--offsets', type=float, nargs='+')
args = parser.parse_args()
if args.r61:
    import play_repaired_r61 as repair
else:
    import play_repaired as repair
import play_autonomous_all_maps as play
from verify_wasd import ContactTrace, longest_streak

args.out.mkdir(parents=True, exist_ok=True)
clock = 1.
app = None
results = []

class Viewer:
    def __init__(self):
        self.cam = SimpleNamespace(lookat=np.zeros(3), azimuth=0.)

    def lock(self):
        return contextlib.nullcontext()

    def is_running(self):
        return True

    def sync(self):
        pass

    def close(self):
        pass


class TestApp(play.AutonomousPlayer):
    def __init__(self, root, sim):
        global app
        super().__init__(root, sim)
        self.keys = set()
        self.user32 = SimpleNamespace(GetAsyncKeyState=self.get_keystate)
        sim.viewer = Viewer()
        app = self

    def get_keystate(self, code):
        return 0x8000 if any(play.VK_MAP[key] == code for key in self.keys) else 0

    def is_console_foreground(self):
        return True

    def focus_console(self):
        pass

    def refresh_hud(self, pressed):
        # Keep the real HUD bindings while avoiding the shared player's status file.
        self.last_status_dump = clock
        super().refresh_hud(pressed)


class Root(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()

    def after(self, ms, func=None, *values):
        return None  # The test calls exactly the same tick with a controlled clock.

    def mainloop(self):
        try:
            if args.proving_ground:
                profiles = [('ground20', 'reset', 3, 0., 5), ('ground20_g4', 'slider', 3, 0., 4),
                            ('double20x2', 'reset', 0, 0., 5)]
            else:
                profiles = [
                    ('center_slide', 'slider', 0, 0., 5), ('center_reset', 'reset', 0, 0., 5),
                    ('center_e_hold', 'e', 0, 0., 5), ('center_e_then_w', 'e', 0, 0., 4),
                    ('center_reset_g4', 'reset', 0, 0., 4), ('near_spawn', 'reset', 1, 0., 5),
                    ('close_g4', 'slider', 0, .82, 4), ('early_w', 'slider', 0, 0., 5),
                ]
            if args.offsets is not None:
                profiles += [(f'near_{offset:.3f}', 'slider', 0, offset, 4) for offset in args.offsets]
            for profile in profiles:
                if args.only is not None and profile[0] not in args.only:
                    continue
                results.append(run(*profile))
                print(results[-1]['name'], results[-1]['before_w'], results[-1]['both_top_s'], flush=True)
        finally:
            self.destroy()


def tick(keys=()):
    global clock
    clock += .005
    app.keys = set(keys)
    app.tick()


def ticks(seconds, keys=()):
    for _ in range(round(seconds / .005)):
        tick(keys)


def state():
    sim = app.sim
    return {'sim_s': float(sim.d.time), 'x': float(sim.d.qpos[0]), 'z': float(sim.d.qpos[2]),
            'vx': float(sim.d.qvel[0]), 'target_h': sim.target_h,
            'cmd_vx': sim.cmd_vx, 'waiting': app.waiting_for_input, 'e1': sim.route['e1']}


def run(name, path, spawn, offset, gear):
    sim = app.sim
    point = sim.scene_meta['spawns'][spawn]
    app.spawn_var.set(f'{spawn + 1}. {point["name"]}')
    point['x'] += offset
    try:
        # Starting with focus on the console, set the height exactly as the GUI does.
        app.on_height_slider('0.420' if path == 'reset' else '0.280')
        app.on_spawn_selected()
        app.action_reset()
        tick((str(gear),))
        tick()
        first = state()
        if path == 'slider':
            app.h_slider_var.set(.42)
            app.on_height_slider('0.420')
        elif path == 'e':
            ticks(4. if name.endswith('_hold') else 1.23, {'e'})
        appearance = state()
        ticks(.25 if name == 'early_w' else 4.)
        ready = state()
        if name != 'early_w':
            ticks(14.)
        before = state()
        if args.proving_ground:
            names = ['lane0_step1_20cm', 'lane0_step2_40cm'] if spawn == 0 else ['lane_stair200']
        else:
            names = ['matrix_step_20cm']
        trace = ContactTrace(sim, names)
        trace.add(sim.m, sim.d)
        physics_step = mj.mj_step

        def sampled_step(m, d):
            physics_step(m, d)
            trace.add(m, d)

        mj.mj_step = sampled_step
        sim.control_rows = []
        try:
            ticks(.02, {'w'})
            after_w = state()
            ticks(10.5 if len(names) == 2 else 6., {'w'})
            tick()
            ticks(.02)
            after_release = state()
        finally:
            mj.mj_step = physics_step
        ctrl = sim.control_rows
        sim.control_rows = None
        a = np.array(trace.rows)
        support_s = []
        backtrack_m = []
        for i, (_, edge, _) in enumerate(trace.top.values()):
            windows = a[1:].reshape(-1, 8, a.shape[-1])
            end = windows[:, -1]
            support = ((windows[:, :, 13 + i * 2:15 + i * 2].mean(1) >= 5.).all(1)
                       & (end[:, 10] > edge + .004) & (end[:, 1] > edge + .02))
            length, confirmed_at = longest_streak(end[:, 0], support, .02)
            support_s.append(length)
            hit = trace.hits[i]
            if hit is not None and confirmed_at is not None:
                x = a[(a[:, 0] >= hit['t']) & (a[:, 0] <= confirmed_at + .40), 1]
                backtrack_m.append(float((np.maximum.accumulate(x) - x).max(initial=0)))
            else:
                backtrack_m.append(None)
        np.savez_compressed(args.out / (name + '.npz'), physical=a, control=np.array([x[0] for x in ctrl]),
                            obs=np.array([x[1] for x in ctrl]), action=np.array([x[2] for x in ctrl]))
        return dict(name=name, gear=gear, first=first, after_height_input=appearance, ready=ready, before_w=before,
                    after_w=after_w, after_release=after_release, both_top_s=support_s, backtrack_m=backtrack_m,
                    peak_horizontal_speed_m_s=float(np.linalg.norm(a[:, 4:6], axis=1).max()),
                    peak_abs_pitch_deg=float(np.abs(a[:, 7]).max()),
                    fell=bool(a[:, 3].min() < .13 or np.abs(a[:, 7]).max() > 44.), hits=trace.hits)
    finally:
        point['x'] -= offset


class TestSimulation(repair.RepairedSimulation):
    control_rows = None

    def step(self, pressed):
        super().step(pressed)
        if self.control_rows is not None:
            z = self.unified.raised_slow_handoff_time
            control = (
                self.d.time, self.d.qpos[0], self.d.qvel[0], self.route['e1'],
                self.route.get('g_prob', 0.), -1. if z is None else z,
                self.route.get('virtual_velocity', 0.), self.route.get('virtual_height', 0.),
            )
            self.control_rows.append((control, self.last_obs.copy(), self.prev_a.copy()))

    def __init__(self, policy, sha, *, show_viewer=True, jump_stance_prep=False):
        super().__init__(policy, sha, show_viewer=False, jump_stance_prep=jump_stance_prep)


# main() and StepPlayer are unmodified. The Win32 keyboard adapter feeds the
# same virtual keys the parent window handles, without touching user windows.
play.AutonomousPlayer = TestApp
repair.RepairedSimulation = TestSimulation
tk.Tk = Root
time.perf_counter = lambda: clock
default_manifest = 'CANDIDATE_R61_RAISED_READY.json' if args.r61 else 'CANDIDATE.json'
sys.argv = [repair.__file__, '--candidate', str(args.manifest or repair.HERE / default_manifest)]
if args.proving_ground:
    sys.argv += ['--proving-ground']
repair.main()
(args.out / 'RESULTS.json').write_text(json.dumps(dict(player_source_sha=hashlib.sha256(Path(repair.__file__).read_bytes()).hexdigest(),
    proving_ground=args.proving_ground, rows=results), indent=2, allow_nan=False) + '\n', encoding='utf8')
