"""WASD playback for the separately evaluated flat and rough E0."""
from argparse import ArgumentParser
import hashlib
import json
import os
from pathlib import Path
import tempfile

from eval_drive import BASELINES, FAMILIES, REPO, install_diagnostic_physics, load_showcase, mujoco, torch
from play_e0_candidate import manifest_drive


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--terrain', choices=FAMILIES, default='flat')
    parser.add_argument('--speed', type=float, default=.5)
    parser.add_argument('--height', type=float, default=.28)
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    if not 0. <= args.speed <= 2.2 or not .20 <= args.height <= .42:
        parser.error('Speed must be 0–2.2 m/s and stance must be 0.20–0.42 m')
    if not args.smoke and os.environ.get('MUJOCO_GL') == 'disable':
        del os.environ['MUJOCO_GL']
    torch.set_num_threads(1)
    config = json.loads(args.manifest.read_text(encoding='utf-8'))
    checkpoint = REPO / BASELINES['c874'][0]
    if hashlib.sha256(checkpoint.read_bytes()).hexdigest() != config['e0_base_sha256']:
        raise ValueError('Base E0 does not match its pinned SHA256')
    cache = Path(os.environ['LOCALAPPDATA'])/'MOD4v3_Repair_Archive/e0_flat_rough_20261120/wasd'
    cache.mkdir(parents=True, exist_ok=True)
    family, level = FAMILIES[args.terrain]
    with tempfile.TemporaryDirectory(prefix='e0_', dir=cache) as folder:
        show = load_showcase(Path(folder), checkpoint)
        class CenteredDrive(show.Replay):
            def reset_standing(self):
                super().reset_standing()
                self.env.d.qpos[:3] = [0., 0., self.ground(0., 0.) + self.env.bank_z]
                mujoco.mj_forward(self.env.m, self.env.d)
                self.z = float(self.env.z) - self.ground(0., 0.)

        sim = CenteredDrive(level=level, family=family, show=not args.smoke)
        install_diagnostic_physics(sim)
        sim.actor = manifest_drive(sim.actor, args.manifest, config)
        sim.args.vx = args.speed
        sim.set_height(args.height)
        try:
            if args.smoke:
                for _ in range(50):
                    sim.step(set())
                for _ in range(50):
                    sim.step({'w'})
                print(json.dumps(dict(terrain=args.terrain, vx=float(sim.env.vx),
                                      resets=sim.reset_count-1, closure_m=sim.closure_peak_m)))
                return
            import tkinter as tk
            from play_ppo_flatv1_control import ControlApp

            root = tk.Tk()
            panel = ControlApp(root, sim)
            label = '平地' if args.terrain == 'flat' else 'L9 rough'
            root.title(f'MOD4v3 E0 | {label} | {config["e0_sha256"][:8]}')
            slider = tk.Scale(root, from_=0., to=2.2, resolution=.05, orient='horizontal',
                              label='速度设定 m/s', takefocus=False,
                              command=lambda value: setattr(sim.args, 'vx', float(value)))
            slider.set(args.speed)
            slider.pack(fill='x', padx=15, pady=(0, 8))
            root.geometry('520x735+30+70')
            root.after(200, panel._focus_control)
            root.mainloop()
        finally:
            sim.close()


if __name__ == '__main__':
    main()
