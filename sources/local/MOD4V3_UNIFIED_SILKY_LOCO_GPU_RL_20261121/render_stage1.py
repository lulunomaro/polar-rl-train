"""Render paired MuJoCo rollouts at the original 50 policy frames per second."""
from argparse import ArgumentParser
import json
import math
from pathlib import Path
from tempfile import TemporaryDirectory

import imageio.v2 as imageio
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import mujoco as mj
import numpy as np
from PIL import Image, ImageDraw
import torch

from eval_silky_rm27 import DOUBLE, EXPERTS, HERE, LEVELS, Replay, cases, high_speed_cases, put, sha256
from silky_geometry import SUPPORT_FORCE_N

FPS = 50
WIDTH, HEIGHT = 448, 288
COLORS = ('#176FA6', '#328654', '#C35A20', '#833993')


def select_cases(rows, high_speed=False):
    selected = []
    for course in ('flat', 'rough_L9', 'curb_11', 'step_20', 'oblique_20',
                   'rm27_west', 'rm27_east', 'rm27_west_400', 'rm27_east_400'):
        choices = [row for row in rows if row['course'] == course]
        target = 2.8 if high_speed else (.60 if course in DOUBLE else 1.)
        example = min(choices, key=lambda row: (abs(row['speed']-target), abs(row['height']-.42),
                                                abs(row['yaw_deg']), row['id']))
        selected.append(example)
    return selected


def select_high_speed_cases(rows):
    defined = [case for case in high_speed_cases() if case['id'] in rows]
    selected = select_cases(defined, high_speed=True)
    reached = [case for case in defined if case['speed'] == 2.8 and rows[case['id']]['reached_command_for_400ms']]
    if reached:
        fastest = max(reached, key=lambda case: rows[case['id']]['best_400ms_mean_forward_com_m_s'])
        if fastest not in selected:
            selected.append(fastest)
    return selected


def plot_routing(output, panels):
    rows = math.ceil(len(panels)/3)
    fig, axes = plt.subplots(rows, 3, figsize=(13, 3*rows), layout='constrained', sharey=True)
    for (row, raw), ax in zip(panels, axes.flat):
        for i, (title, color) in enumerate(zip(EXPERTS, COLORS, strict=True)):
            ax.plot(raw[:, 0], raw[:, -4+i], color=color, lw=1.45, label=title)
        ax.axvline(row['settle_s'], color='#888888', lw=.8, ls='--')
        for column, color in ((15, '#A22525'), (16, '#572A6B')):
            entry = np.flatnonzero(raw[:, column])
            if len(entry):
                ax.axvline(raw[entry[0], 0], color=color, lw=1, ls=':')
        if row['course'] in LEVELS:
            start = 23 if row['course'] in DOUBLE else 21
            loaded = np.flatnonzero(((raw[:, start:start+2] >= SUPPORT_FORCE_N).all(1)) & (raw[:, 1] >= .55))
            if len(loaded):
                ax.axvline(raw[loaded[0], 0], color='#057960', lw=.9, ls='-.')
        ax.set(title=f"{row['course']}   |   {row['height']:.2f} m   |   {row['speed']:+.2f} m/s",
               xlabel='Simulated time [s]', ylabel='Router weight', ylim=(0, 1.02))
        ax.grid(alpha=.20)
    for ax in axes.flat[len(panels):]:
        ax.set_visible(False)
    axes.flat[0].legend(loc='upper right', fontsize=8, ncol=2)
    fig.suptitle('Unified Soft MoE on held-out starts\nGray = command onset   Red = first riser contact   '
                 'Violet = second riser contact   Green = first final-level load')
    fig.savefig(output, dpi=165)
    plt.close(fig)


def render_case(name, case, cache):
    replay = Replay(name, case['course'], cache, case.get('edge_sign', 1))
    frames = []
    sim = replay.sim
    option = mj.MjvOption()
    if sim.scene_meta.get('hide_group5'):
        option.geomgroup[5] = 0
    camera = mj.MjvCamera()
    camera.distance = 2.3
    camera.elevation = -19.
    direction = DOUBLE.get(case['course'], (0., 0., 1))[-1]
    camera.azimuth = 135. if direction > 0 else -45.
    run = Path(name).parent.parent.name
    tag = 'R61' if name == 'R61' else 'Unified Soft MoE'
    if run.startswith('softmoe_'):
        tag = f"Soft MoE {run.removeprefix('softmoe_').upper()}"

    with mj.Renderer(sim.m, height=HEIGHT, width=WIDTH) as renderer:
        def capture(player, judge, failure):
            camera.lookat[:] = player.d.qpos[:3] + np.array([.36*direction, 0., .06])
            renderer.update_scene(player.d, camera=camera, scene_option=option)
            image = Image.fromarray(renderer.render())
            draw = ImageDraw.Draw(image)
            last = judge.trace[-1]
            draw.rectangle((0, 0, WIDTH, 35), fill='#14202E')
            draw.text((10, 6), f"{tag}   |   {case['course']}   |   {last[0]:.2f} s", fill='white')
            draw.text((10, 19), f"CoM {last[2]:+.2f} m/s   |   command {case['speed']:+.2f} m/s"
                      + ('   |   FALL' if failure else ''), fill='white')
            if np.isfinite(judge.weights).all():
                x = 10
                for value, color in zip(judge.weights, COLORS, strict=True):
                    w = int(value*(WIDTH-20))
                    draw.rectangle((x, HEIGHT-13, x+w, HEIGHT-6), fill=color)
                    x += w
            frames.append(np.array(image))
        row, _ = replay.run(case, frames=capture)
    return np.array(frames), row


def render_pair(path, checkpoint, entries, reference):
    metadata = []
    with TemporaryDirectory(prefix='stage1_maps_', dir=path.parent) as folder:
        cache = Path(folder)
        with imageio.get_writer(path, fps=FPS, codec='libx264', macro_block_size=8) as out:
            for case in entries:
                base, row_b = render_case(reference, case, cache)
                candidate, row_c = render_case(checkpoint, case, cache)
                count = max(len(base), len(candidate))
                for i in range(count):
                    # Blank a terminated panel so that a failure is not replayed
                    # in slow motion while the other policy continues.
                    sides = []
                    for series, row in ((base, row_b), (candidate, row_c)):
                        if i < len(series):
                            sides.append(series[i])
                        else:
                            blank = Image.new('RGB', (WIDTH, HEIGHT), '#14202E')
                            ImageDraw.Draw(blank).text((14, 18), f"Run ended at {row['simulated_s']:.2f} s", fill='white')
                            sides.append(np.array(blank))
                    out.append_data(np.concatenate(sides, axis=1))
                metadata.append(dict(case=case['id'], course=case['course'], command_m_s=case['speed'], footage_frames=count,
                                     reference_frames=len(base), candidate_frames=len(candidate),
                                     reference_passed=row_b['passed'], candidate_passed=row_c['passed']))
                print(case['id'], 'frames', count, flush=True)
    with imageio.get_reader(path) as reader:
        assert reader.count_frames() == sum(entry['footage_frames'] for entry in metadata)
        assert reader.get_meta_data()['fps'] == FPS
    return dict(path=path.relative_to(HERE).as_posix(), sha256=sha256(path), fps=FPS,
                frame_simulation_seconds=1/FPS, frame_count=sum(entry['footage_frames'] for entry in metadata),
                cases=metadata)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('checkpoint', type=Path)
    parser.add_argument('--eval', type=Path, required=True)
    parser.add_argument('--high-speed-eval', type=Path)
    parser.add_argument('--reference', default='R61')
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    torch.set_num_threads(1)
    data = json.loads(args.eval.read_text(encoding='utf-8'))
    name = next(iter(data['policies']))
    rows = {row['id']: row for row in data['policies'][name]['rows']}
    checkpoint_sha = sha256(args.checkpoint)
    assert checkpoint_sha == data['policies'][name]['sha256']
    entries = select_cases([case for case in cases() if case['id'] in rows])
    with np.load(args.eval.with_suffix('.npz')) as traces:
        panels = [(case, traces[f'{Path(name).stem}_{case["id"]}']) for case in entries]
    if args.high_speed_eval is not None:
        high = json.loads(args.high_speed_eval.read_text(encoding='utf-8'))
        high_name, high_policy = next(iter(high['policies'].items()))
        assert high['suite'] == 'HIGH_SPEED_2P8MS' and high_policy['sha256'] == checkpoint_sha
        rows.update({row['id']: row for row in high_policy['rows']})
        high_entries = select_high_speed_cases(rows)
        assert all(case['speed'] == 2.8 for case in high_entries)
        entries.extend(high_entries)
        with np.load(args.high_speed_eval.with_suffix('.npz')) as traces:
            panels.extend((case, traces[f'{Path(high_name).stem}_{case["id"]}']) for case in high_entries)
    for case in entries:
        assert all(rows[case['id']][key] == value for key, value in case.items())
    output = args.output_dir.resolve() if args.output_dir else HERE
    output.mkdir(parents=True, exist_ok=True)
    router_plot = output/'ROUTER_WEIGHTS.png'
    plot_routing(router_plot, panels)
    result = render_pair(output/'STAGE1_1X_COMPARISON.mp4', str(args.checkpoint), entries, args.reference)
    for entry, case in zip(result['cases'], entries, strict=True):
        row = rows[case['id']]
        assert entry['candidate_passed'] == row['passed'], case['id']
        # A fall can terminate mid-control-frame. The final video frame shows that sample.
        assert entry['candidate_frames'] == math.ceil(row['simulated_s']*FPS-1.e-9), case['id']
    result.update(reference=args.reference, checkpoint_sha256=checkpoint_sha, heldout_sha256=sha256(args.eval),
                  router_plot_sha256=sha256(router_plot))
    if args.high_speed_eval is not None:
        result['high_speed_sha256'] = sha256(args.high_speed_eval)
        reached = [rows[case['id']] for case in high_entries if rows[case['id']]['reached_command_for_400ms']]
        if reached:
            fastest = max(reached, key=lambda row: row['best_400ms_mean_forward_com_m_s'])
            result['measured_2p8ms_clip'] = fastest['id']
    put((output if args.output_dir else HERE/'evidence')/'VIDEO.json', result)


if __name__ == '__main__':
    main()
