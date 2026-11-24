"""MOD4v3 WASD player for the trained UnifiedSoftMoEActor."""
import argparse
import json
from pathlib import Path
import tkinter as tk

import numpy as np
import torch

from eval_silky_rm27 import AA, HERE, RM, PolicyLoco, legacy, metadata
import play_autonomous_all_maps as ui

MAPS = (
    ('平地', 'flat'), ('L9 崎岖', 'rough_L9'), ('110 mm 坎', 'curb_11'), ('200 mm 单阶', 'step_20'),
    ('200 mm 正斜沿', 'oblique_20'), ('200 mm 反斜沿', 'oblique_20_negative'),
    ('RMUC2027 西入口', 'rm27_west'), ('RMUC2027 东入口', 'rm27_east'),
    ('A–A 西入口 400 / 360 mm', 'rm27_west_400'), ('A–A 东入口 400 / 360 mm', 'rm27_east_400'),
)
JUMP = legacy.jump
MAX_FORWARD_SPEED = 3.0


class PlayerPolicy:
    def __init__(self, checkpoint):
        self.loco = PolicyLoco(checkpoint)
        manifest = legacy.HERE/'CANDIDATE_R61_RAISED_READY.json'
        donor, _, _ = legacy.load_manifest(manifest)
        self.jump = donor.jump
        self.jump_sha = json.loads(manifest.read_text(encoding='utf-8'))['sha256']['jump']
        self.jump_history_frames = donor.jump_history_frames
        self.jump_frames = donor.jump_frames
        self.jump_history = legacy.stair.ProprioHistoryQueue40()
        self.reset_history()

    def reset_history(self):
        self.loco.reset_history()
        self.jump_history.clear()
        self.weights = [0.] * 4

    @torch.inference_mode()
    def act(self, obs):
        x = torch.from_numpy(obs).reshape(1, 35)
        history = self.jump_history.append(x)
        current = obs.copy()
        current[JUMP.JUMP_MODE_BIT_INDEX] = 0.
        action, routes = self.loco.act(current)
        self.weights = list(routes.values())
        jump = obs[JUMP.JUMP_MODE_BIT_INDEX] > .5
        if jump:
            frames = history.reshape(1, legacy.stair.HIST_LEN, 35)[:, -self.jump_history_frames:]
            action = self.jump(x, frames.flatten(1)).clamp(-6., 6.)[0].numpy()
        return action, {'e0': self.weights[0], 'e1': sum(self.weights[1:]), 'e2': float(jump)}


class PlayerSimulation(legacy.AutonomousMapSimulation):
    def request_jump(self):
        if not super().request_jump():
            return False
        self.jump_rem = self.unified.jump_frames
        return True


def player_metadata(course):
    meta = metadata(course, HERE/'maps'/'wasd')
    for spawn in meta['spawns']:
        spawn['name'] = '起点'
        if course in RM:
            x, y, sign = RM[course]
            spawn.update(x=x, y=y, yaw_deg=0. if sign == 1 else 180., name='高地入口')
        if course in AA:
            spawn['name'] = 'A–A 剖面入口'
    if course == 'step_20':
        for angle in (-25., 25.):
            meta['spawns'].append(dict(meta['spawns'][0], yaw_deg=angle, name=f'斜入 {angle:+.0f}°'))
    return meta


class Player(ui.AutonomousPlayer):
    def _build_ui(self):
        ui.SUITE_LABELS = tuple(label for label, _ in MAPS)
        super()._build_ui()
        widgets = self.root.winfo_children()
        while widgets:
            widget = widgets.pop()
            if isinstance(widget, tk.Scale) and str(widget.cget('variable')) == str(self.v_slider_var):
                widget.configure(to=MAX_FORWARD_SPEED)
                break
            widgets.extend(widget.winfo_children())
        self.root.title(f'MOD4v3 Unified Soft MoE · {self.sim.ckpt_sha[:8]}')
        self.max_wz = self.sim.max_wz = 1.8

    def on_suite_changed(self):
        self.apply_suite_selection()

    def apply_suite_selection(self, initial=False):
        _, course = MAPS[max(0, self.suite_cb.current())]
        config = player_metadata(course)
        self.sim.load_map(config)
        self.spawn_cb.configure(values=[s['name'] for s in config['spawns']])
        self.spawn_cb.current(0)
        self.hint_var.set('W/S 前后 · A/D 偏航 · Q/E 站高 · Space/J 跳跃')
        self.waiting_for_input = True
        self.event_msg = '地图已载入'
        if not initial:
            self.focus_console()

    def refresh_hud(self, pressed):
        data = self.sim.telemetry()
        g = self.sim.unified.weights
        state = '跳跃' if self.sim.route['e2'] else ('按 W 开始' if self.waiting_for_input else '驾驶')
        self.live_var.set(f'{state}   巡航 {g[0]:.0%}   崎岖 {g[1]:.0%}   上阶 {g[2]:.0%}   越顶 {g[3]:.0%}\n'
                          f"速度 {data['vx']:+.2f} / {data['cmd_vx']:+.2f} m/s   "
                          f"站高 {data['rel_z']:.3f} / {data['target_h']:.3f} m\n"
                          f"俯仰 {data['pitch_deg']:+.1f}°   闭链误差 {data['closure_mm']:.3f} mm")
        if pressed & {'q', 'e'}:
            self.h_slider_var.set(self.sim.target_h)
        self.status_var.set(self.event_msg)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', type=Path)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    if args.model is None:
        candidate = json.loads((HERE/'STAGE1_RESULT.json').read_text(encoding='utf-8'))['checkpoint']
        args.model = HERE/candidate['path']
    policy = PlayerPolicy(args.model)
    sim = PlayerSimulation(policy, policy.loco.sha, show_viewer=not args.smoke)
    try:
        if args.smoke:
            for _, course in MAPS:
                sim.load_map(player_metadata(course))
                for key, command, direction in (('w', 'cmd_vx', 1), ('s', 'cmd_vx', -1),
                                                 ('a', 'cmd_wz', 1), ('d', 'cmd_wz', -1)):
                    for _ in range(10):
                        sim.step({key})
                        assert not sim.route['e2']
                    assert direction * getattr(sim, command) > 0.
                    assert np.isfinite(policy.weights).all() and abs(sum(policy.weights)-1.) < 1.e-6
                if course == 'flat':
                    default_speed = sim.max_vx
                    sim.reset_at_spawn()
                    sim.max_vx = MAX_FORWARD_SPEED
                    for _ in range(45):
                        sim.step({'w'})
                    assert abs(sim.cmd_vx-MAX_FORWARD_SPEED) < .01
                    assert np.isclose(sim.last_obs[0], sim.cmd_vx) and not sim.route['e2']
                    print(f'W speed goal {MAX_FORWARD_SPEED:.2f} m/s reached in the actor command channel')
                    sim.max_vx = default_speed
                    sim.reset_at_spawn()
                assert sim.request_jump() and sim.jump_rem == policy.jump_frames
                sim.step(set())
                assert sim.route['e2'] == 1.
                print(course, sim.ckpt_sha[:8], 'WASD / explicit jump OK')
            return
        ui.ERROR_PATH = HERE/'evidence'/'WASD_ERROR.txt'
        root = tk.Tk()
        Player(root, sim)
        root.mainloop()
    finally:
        sim.close()


if __name__ == '__main__':
    main()
