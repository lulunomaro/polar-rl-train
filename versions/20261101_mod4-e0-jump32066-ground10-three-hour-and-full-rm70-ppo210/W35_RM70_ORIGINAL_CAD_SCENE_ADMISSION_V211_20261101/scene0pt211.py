"""One future root-owned scene-only purpose: eight original arenas, ZERO PT.

This script is supplied unused. Root must separately bind the typed task, actual
binary installation receipts, source/GPU/private/shared/control lease. It does
not issue GO, contact SSH or write the canonical account.
"""
from pathlib import Path
import argparse, json, os, hashlib, time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job-root', type=Path, required=True)
    args = parser.parse_args(); root = args.job_root.resolve()
    task = json.loads((root / 'SCENE0PT208_TASK.json').read_text())
    assert task['kind'] == 'NEW208_ORIGINAL_CAD_SCENE_ZERO_PT'
    assert task['num_envs'] == 8 and task['max_physics_steps'] == 8
    assert task['max_wall_seconds'] == 180 and task['model_opens'] == 0
    assert task['raw_JSONL_opens'] == 0 and task['neural_optimizer_updates'] == 0
    assert task['root_actual_exclusive_control_and_GPU_admission'] is True
    assert os.environ.get('CUDA_VISIBLE_DEVICES') == task['GPU_UUID']
    assert hashlib.sha256(Path(__file__).read_bytes()).hexdigest() == task['worker_SHA']
    output = root / 'scene0pt208'; output.mkdir(exist_ok=False)
    storage = root / 'kit_isolation'; storage.mkdir(exist_ok=False)
    for name in ('data', 'DerivedDataCache'):
        (storage / name).mkdir()
    (storage / 'data/user.config.json').write_text('{}')
    os.environ['MOD4_NEW208_JOB_ROOT'] = str(root)
    os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT'] = str(storage)
    started = time.time()
    from launcher208 import IsolatedAppLauncher208 as AppLauncher
    launcher = AppLauncher(headless=True, device='cuda:0')
    try:
        import torch
        import isaaclab.sim as sim_utils
        from field208 import make_terrain_cfg, SharedQuery208
        from course_math208 import ROUTE_X, ROUTE_Y
        from types import SimpleNamespace
        receipt = json.loads((root / 'RM70_BINARY_INSTALL_ACTUAL.json').read_text())
        cfg = make_terrain_cfg(root / 'original_field', receipt, 8, output / 'layout')
        from isaaclab_physx.physics import PhysxCfg
        sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(dt=.0025, device='cuda:0', physics=PhysxCfg(solver_type=1, enable_external_forces_every_iteration=True)))
        terrain = cfg.class_type(cfg)
        sim.reset()
        env = SimpleNamespace(device='cuda:0', scene=SimpleNamespace(
            terrain=terrain, env_origins=terrain.env_origins))
        query = SharedQuery208(env)
        points = terrain.env_origins[:, None].repeat(1, 2, 1)
        points[:, :, 0] += torch.tensor(ROUTE_X, device='cuda:0')
        points[:, :, 1] += ROUTE_Y; points[:, :, 2] += 2.
        facts = query.cast(points, 4.)
        assert bool(facts['hit'].all()) and bool(torch.isfinite(facts['normal']).all())
        assert bool((facts['normal'][..., 2] > 0).all())
        for _ in range(8):
            if time.time() - started > 180:
                raise TimeoutError('Finite scene0PT208 purpose exceeded 180s')
            sim.step()
        report = dict(kind=task['kind'], passed_scene_and_route_ground_query=True,
            arenas=8, physics_steps=8, model_opens=0, actor_calls=0, optimizer_updates=0,
            actual_endpoint_heights=facts['height'].cpu().tolist(),
            actual_endpoint_normals=facts['normal'].cpu().tolist(),
            source_slope_preserved=True, no_new_160k_or_precision_audit=True,
            robot_contact_fullreset_native24_training_admission=False,
            complete_RM70_skill=False, original_geometry_not_synthesized=True)
        (output / 'SCENE0PT208_ACTUAL.json').write_text(json.dumps(report, indent=2))
    finally:
        launcher.app.close()


if __name__ == '__main__':
    main()
