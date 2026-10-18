"""Check the existing exported bundle and exercise the actual MuJoCo bridge."""
import json
from pathlib import Path
import time
import traceback
import numpy as np
import torch
import onnxruntime as ort
from export_latest_moe import ROOT, STAGE, SOURCES, ManualMoE, sha
from launcher import validate_model, validate_policy
from sim_runtime import Mod4Sim
from drive_wasd import CONTROL_KEYS, MUJOCO_DIRECT_RESERVED_KEYS


def main():
    torch.set_num_threads(2)
    path = ROOT / 'policies/imported/mod4_latest_moe_20261018.onnx'
    meta = json.loads(path.with_suffix('.json').read_text(encoding='utf-8'))
    assert sha(path) == meta['onnx_sha256']
    # This verifies an existing export; it never re-exports a graph or touches a GPU.
    checkpoints = {}
    for role, (source, digest) in SOURCES.items():
        assert sha(source) == digest
        checkpoints[role] = torch.load(source, map_location='cpu', weights_only=False)
    reference = ManualMoE(checkpoints).eval()
    session = ort.InferenceSession(str(path), providers=['CPUExecutionProvider'])
    scenes, observations = [], []
    for kind in ('normal_walk', 'jump_request', 'jump_from_pause', 'recover', 'spin_left', 'spin_right'):
        sim = Mod4Sim(ROOT/'model/rm_training_arena_headless.xml', path)
        assert not sim.command.auto_mode and sim.cfg.yaw_assist_gain == 0
        initial_z = float(sim.base_position[2])
        peak_z = initial_z
        if kind == 'normal_walk':
            sim.command.vx = .3
        elif kind == 'recover':
            sim.select_manual_mode(3)
        elif kind.startswith('spin'):
            sim.select_manual_mode(6)
            sim.command.wz = 4 if kind.endswith('left') else -4
        elif kind == 'jump_from_pause':
            sim.request_jump()
        request_modes = []
        n = 300 if kind.startswith('jump') else 100
        for tick in range(n):
            if kind == 'jump_request' and tick == 100:
                sim.request_jump()
            observations.append(sim.observation_frame())
            request_modes.append(int(np.argmax(observations[-1][28:35])))
            action = sim.step_control()
            assert action.shape == (6,) and np.isfinite(action).all() and np.max(np.abs(action)) <= 6
            peak_z = max(peak_z, float(sim.base_position[2]))
        if kind.startswith('jump'):
            assert request_modes.count(4) == 80 and sim.command.mode == 0 and sim._jump_ticks == 0
        scenes.append(dict(scenario=kind, controls=n, initial_z=initial_z, peak_z=peak_z,
            jump_public_mode4_controls=request_modes.count(4), health=sim.health(),
            simulation_interface_ran=True, skill_qualified=False))
    x = np.stack(observations).astype(np.float32)
    with torch.no_grad():
        expected = reference(torch.from_numpy(x)).numpy()
    actual = session.run(None, {'observation': x})[0]
    error = float(np.max(np.abs(expected-actual)))
    assert np.isfinite(actual).all() and error <= 1e-4, error
    keys = {k for values in CONTROL_KEYS.values() for k in values}
    assert not keys.intersection(MUJOCO_DIRECT_RESERVED_KEYS)
    for n in (1, 2, 7):
        assert session.run(None, {'observation': x[:n]})[0].shape == (n, 6)
    # Reconstruct the report after the exporter had already completed its parity
    # test and metadata, then hit a duplicate keyword in report construction.
    export_report = dict(status='PASS', onnx_path=str(path), bytes=path.stat().st_size, **meta)
    export_report_path = STAGE/'reports/LOCAL_LATEST_MOE_EXPORT_ACTUAL.json'
    if not export_report_path.exists():
        export_report_path.write_text(json.dumps(export_report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    report = dict(epoch=time.time(), status='PASS', purpose='Local player interface, not training or skill qualification',
        source_and_graph_hashes_exact=True, existing_export_reused=True,
        original_export_report_construction_error_retained=True,
        launcher=validate_policy(path), model=validate_model(),
        trajectory_rows=len(x), trajectory_parity_max_abs_error=error, parity_bound=1e-4,
        viewer_key_conflicts=0, scenarios=scenes, no_remote_training_changes=True)
    (STAGE/f'reports/LOCAL_LATEST_MOE_MUJOCO_RUNTIME_ACTUAL_{time.time_ns()}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('status','trajectory_rows','trajectory_parity_max_abs_error','viewer_key_conflicts')}, ensure_ascii=False))
    print(json.dumps(scenes, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except BaseException:
        (STAGE/f'reports/LOCAL_MOE_RUNTIME_ORIGINAL_ERROR_{time.time_ns()}.txt').write_text(traceback.format_exc(), encoding='utf-8')
        raise
