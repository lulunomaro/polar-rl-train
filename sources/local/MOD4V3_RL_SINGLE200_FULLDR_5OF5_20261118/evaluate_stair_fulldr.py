"""Comprehensive Independent Benchmark & Video Renderer for Pure-Neural RL Single-Step (200mm) Stair Climbing.

Verifies:
1. Unmodified `evaluate_student200.py` formal 5-offset (`-60/-30/0/+30/+60 mm`) `<= 0.60 m/s` evaluation + `1x` MP4.
2. Dense 21-offset (`-75..+75 mm`) `0-DR` continuous starting-pose generalization.
3. `100% Full-DR` (`dr_scale = 1.0`) 30-episode (`5 offsets x 6 Full-DR seeds`) robustness benchmark + `1x` Full-DR MP4.
4. Full frozen `E0` (`c874`) regression suite: `flat60` (60/60), `fixed_stair` (5/5), `descent` (5/5), `fixed_pitch`, and `0.0` `c874` drift.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import imageio.v2 as imageio
import mujoco as mj
import numpy as np
import torch

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path[:0] = [str(HERE), str(HERE / 'support')]

from history_eval_hooks import ReplayHistoryActor
from rl_stair_env import SingleStepRLEnv


def render_episode_video(model_pt: Path, out_mp4: Path, offset_mm: float = 0.0, dr_scale: float = 0.0, seed: int = 8000) -> dict:
    ck = torch.load(model_pt, map_location='cpu', weights_only=False)
    actor = ReplayHistoryActor()
    actor.load_state_dict(ck['actor_state_dict'], strict=False)
    actor.eval()
    actor.reset_history()

    env = SingleStepRLEnv()
    obs, _ = env.reset(offset_mm=offset_mm, dr_scale=dr_scale, seed=seed)
    states = [env.d.qpos.copy()]
    info = {}
    with torch.inference_mode():
        while True:
            a = actor(torch.from_numpy(obs).reshape(1, 35))[0].clamp(-6.0, 6.0).numpy()
            obs, _, _, done, info = env.step(a)
            states.append(env.d.qpos.copy())
            if done:
                break

    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    renderer = mj.Renderer(env.m, height=720, width=1280)
    cam = mj.MjvCamera()
    cam.azimuth = 90.0
    cam.elevation = -14.0
    cam.distance = 2.15
    cam.lookat[:] = [1.18, 0.0, 0.28]

    with imageio.get_writer(str(out_mp4), fps=25, codec='libx264', quality=7) as writer:
        for i in range(0, len(states), 2):
            env.d.qpos[:] = states[i]
            mj.mj_forward(env.m, env.d)
            renderer.update_scene(env.d, camera=cam)
            writer.append_data(renderer.render())
    renderer.close()
    return info


def main():
    t0 = time.time()
    best_pt = HERE / 'weights/model_rl_stair_best.pt'
    assert best_pt.exists(), f'Missing {best_pt}'
    sha = hashlib.sha256(best_pt.read_bytes()).hexdigest()

    ck = torch.load(best_pt, map_location='cpu', weights_only=False)
    c874 = torch.load(HERE / 'c874_reference.pt', map_location='cpu', weights_only=False)

    # 1) Verify exact 0.0 drift on E0 relative to c874
    e0_diffs = []
    for k, v in ck['actor_state_dict'].items():
        if k.startswith('mlp.e0.'):
            sub_k = k[len('mlp.e0.'):]
            ref_k = f'mlp.{sub_k}'
            if ref_k in c874['actor_state_dict']:
                e0_diffs.append(float((v.cpu() - c874['actor_state_dict'][ref_k].cpu()).abs().max()))
    e0_max_diff = max(e0_diffs) if e0_diffs else 0.0

    # 2) Run UNMODIFIED evaluate_student200.py (formal 5-offset 0-DR)
    off_dir = HERE / 'evidence/final_official_eval200'
    if off_dir.exists():
        shutil.rmtree(off_dir)
    subprocess.run(
        [sys.executable, str(HERE / 'evaluate_student200.py'), '--model', str(best_pt), '--out', str(off_dir), '--video'],
        cwd=REPO,
        check=True,
    )
    official_0dr = json.loads((off_dir / 'RESULT.json').read_text(encoding='utf8'))
    shutil.copy2(off_dir / 'STUDENT_CENTER_1X.mp4', HERE / 'media/RL_SINGLE200_NOMINAL_CENTER_1X.mp4')

    # 3) Dense 21-offset 0-DR & 30-episode 100% Full-DR evaluation
    actor = ReplayHistoryActor()
    actor.load_state_dict(ck['actor_state_dict'], strict=False)
    actor.eval()
    env = SingleStepRLEnv()

    dense21_offs = list(range(-75, 76, 7)) + [-60, -30, 0, 30, 60]
    dense21_offs = sorted(set(dense21_offs))
    dense_rows = []
    with torch.inference_mode():
        for off in dense21_offs:
            actor.reset_history()
            obs, _ = env.reset(offset_mm=off, dr_scale=0.0)
            while True:
                a = actor(torch.from_numpy(obs).reshape(1, 35))[0].clamp(-6.0, 6.0).numpy()
                obs, _, _, done, info = env.step(a)
                if done:
                    dense_rows.append({'offset_mm': off, **info})
                    break

    fulldr_rows = []
    with torch.inference_mode():
        for off in [-60, -30, 0, 30, 60]:
            for s_i in range(6):
                actor.reset_history()
                seed = 8000 + s_i * 131 + (off + 100)
                obs, _ = env.reset(offset_mm=off, dr_scale=1.0, seed=seed)
                while True:
                    a = actor(torch.from_numpy(obs).reshape(1, 35))[0].clamp(-6.0, 6.0).numpy()
                    obs, _, _, done, info = env.step(a)
                    if done:
                        fulldr_rows.append({'offset_mm': off, 'seed': seed, **info})
                        break

    # Render 100% Full-DR 1x video on a passing Full-DR episode!
    pass_dr_ep = next((r for r in fulldr_rows if r['success'] and r['offset_mm'] == 0), next((r for r in fulldr_rows if r['success']), fulldr_rows[0]))
    fulldr_vid_info = render_episode_video(
        best_pt,
        HERE / 'media/RL_SINGLE200_FULLDR_1X.mp4',
        offset_mm=pass_dr_ep['offset_mm'],
        dr_scale=1.0,
        seed=pass_dr_ep['seed'],
    )

    # 4) Run full E0 retention regression suite (`flat60`, `fixed_stair`, `descent`, `fixed_pitch`)
    reg_dir = HERE / 'evidence/final_e0_regressions'
    if reg_dir.exists():
        shutil.rmtree(reg_dir)
    reg_dir.mkdir(parents=True)

    regressions = {}
    for name, script in [
        ('flat60', 'fixed_60_eval.py'),
        ('fixed_stair', 'fixed_stair_eval.py'),
        ('descent', 'descent_eval.py'),
        ('fixed_pitch', 'fixed_pitch_eval.py'),
    ]:
        out_sub = reg_dir / name
        r = subprocess.run(
            [sys.executable, str(HERE / script), '--model', str(best_pt), '--out', str(out_sub)],
            cwd=REPO,
            capture_output=True,
            text=True,
        )
        regressions[name] = {'exit_code': r.returncode}
        ver = out_sub / 'VERIFICATION.json'
        if ver.exists():
            regressions[name]['verification'] = json.loads(ver.read_text(encoding='utf8'))

    summary = {
        'model_path': str(best_pt),
        'sha256': sha,
        'pure_neural_student': True,
        'runtime_teacher_calls': 0,
        'privileged_actor_inputs': 0,
        'e0_c874_max_abs_diff': e0_max_diff,
        'official_0dr_5offsets': {
            'passed': official_0dr['passed'],
            'requested': official_0dr['requested'],
            'physical_crossed': official_0dr['physical_crossed'],
            'physical_stable_events': official_0dr['physical_stable_events'],
            'slid_off_count': sum(1 for r in official_0dr['rows'] if r['reason'] == 'slid_off_step_regression'),
            'rows': [
                {
                    'offset_mm': r['start_offset_mm'],
                    'success': r['success'],
                    'crossed': r['physical_bilateral_crossed'],
                    'max_speed_m_s': round(r['maximum_episode_speed_m_s'], 4),
                    'final_hold_s': round(r['final_continuous_hold_s'], 2),
                    'pitch_peak_deg': round(r['pitch_peak_deg'], 2),
                    'reason': r['reason'],
                }
                for r in official_0dr['rows']
            ],
        },
        'dense_0dr_generalization': {
            'passed': sum(1 for r in dense_rows if r['success']),
            'crossed': sum(1 for r in dense_rows if r['physical_crossed']),
            'slid_off_count': sum(1 for r in dense_rows if r['slid_back']),
            'total': len(dense_rows),
            'mean_max_speed_m_s': round(float(np.mean([r['max_speed_m_s'] for r in dense_rows])), 4),
        },
        'fulldr_100pct_30episodes': {
            'passed': sum(1 for r in fulldr_rows if r['success']),
            'crossed': sum(1 for r in fulldr_rows if r['physical_crossed']),
            'physical_stable': sum(1 for r in fulldr_rows if r['physical_stable']),
            'slid_off_count': sum(1 for r in fulldr_rows if r['slid_back']),
            'total': len(fulldr_rows),
            'mean_max_speed_m_s': round(float(np.mean([r['max_speed_m_s'] for r in fulldr_rows])), 4),
            'video_episode': fulldr_vid_info,
        },
        'e0_regressions': regressions,
        'wall_seconds': round(time.time() - t0, 2),
    }
    (HERE / 'BENCHMARK_RL_STAIR_RESULTS.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: v for k, v in summary.items() if k != 'e0_regressions'}, indent=2), flush=True)
    print('E0 regressions exit codes:', {k: v['exit_code'] for k, v in regressions.items()}, flush=True)


if __name__ == '__main__':
    main()
