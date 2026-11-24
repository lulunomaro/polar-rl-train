"""COMMANDER-AUTHORED & LOCKED Entry Script for Priority #1: E_stair_nav4d (DO NOT MODIFY!)."""
from __future__ import annotations

from argparse import ArgumentParser
import json
import os
from pathlib import Path
import random
import sys
import time
import traceback


def put(path: Path, obj: dict):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".partial")
    tmp.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    tmp.replace(path)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("job", type=Path)
    parser.add_argument("--seconds", type=int, default=0)
    parser.add_argument("--probe", type=Path, default=None)
    parser.add_argument("--lr", type=float, default=5.0e-5)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    job = args.job.resolve()
    job.mkdir(parents=True, exist_ok=True)
    app = None
    env = None
    scene_closed = False
    err_txt = None

    try:
        dep = root / "dependencies"
        plant = root / "plant"
        sources = json.loads((dep / "SOURCE_PATHS.relative.json").read_text(encoding="utf-8"))
        put(job / "source_paths.json", {k: str(dep / v) for k, v in sources.items()})

        storage = job / "kit_isolation"
        (storage / "data").mkdir(parents=True, exist_ok=True)
        (storage / "DerivedDataCache").mkdir(parents=True, exist_ok=True)
        (storage / "data/user.config.json").write_text("{}", encoding="utf-8")

        os.environ.update(
            MOD4V1_E0_JOB_ROOT=str(job),
            MOD4V1_E0_KIT_STORAGE_ROOT=str(storage),
            MOD4_SCUT_SOURCE_PATHS=str(job / "source_paths.json"),
            OMNI_KIT_ACCEPT_EULA="YES",
            ISAACSIM_ACCEPT_EULA="Y",
            WARP_CACHE_PATH=str(root / "cache/warp"),
            JOINT_FRICTION_SCALE="1",
            SPRING_DAMPING_FRACTION="1",
            EXTERNAL_DR_FRACTION="1",
            OBS_NOISE_FRACTION="1",
            PHYSICAL_DELAY_QUANTUM_MS="5",
            PHYSICAL_ACTION_DELAY_MIN_MS="5",
            PHYSICAL_ACTION_DELAY_MAX_MS="10",
            PHYSICAL_SENSOR_DELAY_MIN_MS="5",
            PHYSICAL_SENSOR_DELAY_MAX_MS="15",
            PYTHONDONTWRITEBYTECODE="1",
        )
        sys.path[:0] = [str(root), str(dep / "launcher"), str(dep / "package"), str(plant), str(root / "support")]

        from launcher_mod4v1_e0 import IsolatedAppLauncher208

        app = IsolatedAppLauncher208(dict(headless=True, device="cuda:0", enable_cameras=False)).app

        import numpy as np
        import torch
        from fsm_geometry import physx_tire_geometry
        from manual_fsm_model import SymmetricE0
        from mod4v3_ppo_v1.model import metadata, reset_bank
        from mod4v3_ppo_v1.scut_flat_env import configuration
        from nav4d_isaac_env import Nav4DIsaacEnv, TrainingAdapter, install_course
        from train_generalized_ppo import run_ppo
        from unified_policies import AsymmetricValue, StairNav4DExpert

        seed = 20261122
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        install_course()
        meta = metadata(plant)
        bank = reset_bank(plant, dep / "reset_bank.json")
        cfg_env = configuration(meta, bank, 2048, seed, terrain_selection="rough_scut_v1")
        env = Nav4DIsaacEnv(cfg_env, meta, bank, physx_tire_geometry(plant), initial_dr=0.0)
        env.render_enabled = False
        env.scene["contacts"].cfg.update_period = 0.0

        orig_update = env.scene.update

        def hooked_update(dt):
            orig_update(dt)
            env.sample_physics(dt)

        env.scene.update = hooked_update
        env.reset()

        e0 = (
            SymmetricE0()
            .load_e0(
                torch.load(root / "weights/e0.pt", map_location=env.device, weights_only=False),
                torch.load(root / "weights/e0_base.pt", map_location=env.device, weights_only=False),
            )
            .to(env.device)
            .eval()
        )
        if (root / "E0_CALIBRATION.json").is_file():
            e0.load_calibration(json.loads((root / "E0_CALIBRATION.json").read_text(encoding="utf-8")))

        adapter = TrainingAdapter(env, e0)
        donor_payload = torch.load(root / "weights/stair_donor.pt", map_location="cpu", weights_only=False)
        actor = StairNav4DExpert(donor_payload)
        critic_dim = 459 + adapter.extra().shape[1]
        critic = AsymmetricValue(critic_dim)

        run_ppo(
            adapter,
            actor,
            critic,
            job,
            seconds=args.seconds,
            kind="stair",
            probe_dir=args.probe,
            donor_meta={"donor_format": donor_payload.get("format")},
            lr_actor=args.lr,
            lr_critic=2.5e-4,
            rollout_len=28,
        )
    except BaseException:
        err_txt = traceback.format_exc()
        (job / "ERROR.txt").write_text(err_txt, encoding="utf-8")
        raise
    finally:
        try:
            if env is not None:
                env.close()
                scene_closed = True
        except Exception:
            pass
        put(
            job / "SAFE_CLOSED.json",
            dict(epoch=time.time(), scene_closed=scene_closed, worker_finished=True, error=err_txt),
        )
        if app is not None:
            try:
                app.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()
