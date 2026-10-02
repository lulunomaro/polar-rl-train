"""Run the isolated MOD4 flat-ground SCUT-style contract probe or short PPO stage."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
from pathlib import Path

STAGE = Path(__file__).resolve().parent
OLD = Path("/home/egde/rl_candidates/MOD4_takeover_20260914/repair_zero_success_20260916/grounded_run_20260925/flat_walk_run_8h_20260926")
PARENT = OLD / "run/mixed_gas_dr/logs/2026-09-26_07-01-30_flat_mixed_gas_dr_20260926/model_385.pt"
ISAAC_PYTHON = "/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python"


def training_env():
    manifest = json.loads((PARENT.parent / "run_manifest.json").read_text())
    env = {k: v for k, v in os.environ.items() if not k.startswith("RM_")}
    env.update({k: str(v) for k, v in manifest["env"].items()
                if k.startswith("RM_") and v is not None})
    env.update({
        "RM_MOD4_USD": str(STAGE / "asset/robot_wheel_convex24.usd"),
        "RM_MOD4_MAP": "fudan_plane", "RM_MOD4_TERRAIN": "flat",
        "RM_WORKSPACE_ROOT": "/home/egde/rl_candidates/MOD4_takeover_20260914/env_scaling_20260915/source",
        "RM_DR_OFF": "1", "RM_GAS_FORCE_DR": "1", "RM_GAS_FORCE_DR_ONLY": "1",
        "RM_GAS_FORCE_FRAME": "reference", "RM_GAS_FORCE_NOMINAL_N": "500",
        "RM_GAS_FORCE_MIN_N": "500", "RM_GAS_FORCE_MAX_N": "500",
        "RM_HEIGHT_MIN": "0.24", "RM_HEIGHT_MAX": "0.24",
        "RM_CMD_VX_MIN": "0.05", "RM_CMD_VX_MAX": "0.55",
        "RM_CMD_WZ_MIN": "0", "RM_CMD_WZ_MAX": "0",
        "RM_ROUTE_KINDS": "", "RM_ROUTE_WEIGHTS": "",
        "RM_LEG_KP": "250", "RM_LEG_KD": "10",
        "RM_LEG_ACTION_SCALE": "0.5", "RM_CRANK_ACTION_SCALE": "0.75",
        "RM_CLAMP_LEG_TARGETS": "1", "RM_DIFF_MIN": "-0.95",
        "RM_SOLVER_POS": "16", "RM_SOLVER_VEL": "4",
        # The latest MOD4 checkpoint has a five-frame latent encoder.  Preserve its
        # observation interface; only reopen exploration std for the new stage.
        "RM_SEQ_ENCODER": "1", "RM_INIT_STD": "0.3",
        "RM_ENTROPY_COEF": "0.005",
        "RM_PPO_VALUE_LOSS_COEF": "4.0", "RM_PPO_SCHEDULE": "adaptive",
        "RM_W_FLAT_ORIENT": "-4.0", "RM_W_ANG_VEL_XY": "-0.05",
        "RM_W_TRACK_LIN": "1.0", "RM_W_RUN_VEL_ERROR": "-1.0",
        "RM_W_RUN_HEIGHT_DEFICIT": "-8.0", "RM_W_WHEEL_CONTACT": "2.0",
        "RM_W_GUIDE_CONTACT": "-1.0",
        "RM_W_GUIDE_LOAD": "-2.0", "RM_W_LEG_TARGET_PROJECTION": "-4.0",
        "RM_W_ACTION_L2_LEG": "-0.2",
        "RM_W_ACTION_RATE": "-0.05", "RM_W_ACTION_ACC": "-0.02",
        "RM_W_STAND_QUIET": "1.0", "RM_W_STAND_MOTION": "-1.0",
        "OMNI_KIT_ACCEPT_EULA": "YES", "PYTHONUNBUFFERED": "1", "CUDA_VISIBLE_DEVICES": "0",
    })
    return env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["mapping", "dryrun", "train"])
    parser.add_argument("--iterations", type=int, default=20)
    parser.add_argument("--envs", type=int, default=512)
    parser.add_argument("--warmstart", action="store_true")
    parser.add_argument("--resume-exact", action="store_true",
                        help="resume model, optimizer, iteration, and exploration std unchanged")
    parser.add_argument("--checkpoint", default="")
    parser.add_argument("--tag", default="")
    parser.add_argument("--plain-mlp", action="store_true",
                        help="train a fresh 35-D SCUT-style MLP instead of the legacy history encoder")
    parser.add_argument("--vx-min", default="")
    parser.add_argument("--vx-max", default="")
    args = parser.parse_args()
    if args.resume_exact and not args.warmstart:
        raise ValueError("--resume-exact requires --warmstart and --checkpoint")
    env = training_env()
    if args.resume_exact:
        env["RM_PARTIAL_WARMSTART"] = "0"
        env["RM_KEEP_STD"] = "1"
    if args.plain_mlp:
        if args.warmstart:
            raise ValueError("plain MLP requires a fresh run; legacy checkpoint has an encoder")
        env["RM_SEQ_ENCODER"] = "0"
    if args.vx_min:
        env["RM_CMD_VX_MIN"] = args.vx_min
    if args.vx_max:
        env["RM_CMD_VX_MAX"] = args.vx_max
    source_checkpoint = Path(args.checkpoint) if args.checkpoint else PARENT
    run_dir = STAGE / "run" / (args.tag or args.mode)
    if (run_dir / "report.json").exists():
        raise FileExistsError(f"run already has a report: {run_dir}")
    run_dir.mkdir(parents=True, exist_ok=True)
    if args.mode == "mapping":
        cmd = [ISAAC_PYTHON, str(STAGE / "source/mod4/probe_scut_mapping.py"),
               "--headless", "--steps", "50", "--report", str(run_dir / "report.json")]
    else:
        cmd = [ISAAC_PYTHON, str(STAGE / "source/mod4/train_mod4_ppo.py"),
               "--headless", "--num_envs", str(args.envs),
               "--seed", "20260926", "--steps_per_env", "48",
               "--report", str(run_dir / "report.json")]
        if args.mode == "dryrun":
            cmd += ["--dry_run", "100"]
        else:
            cmd += ["--additional_iterations", str(args.iterations),
                    "--save_interval", "5", "--learning_rate", "0.0001",
                    "--run_name", "scut_flat_mod4", "--log_root", str(run_dir / "logs")]
            if args.warmstart:
                cmd += ["--init_checkpoint", str(source_checkpoint)]
    metadata = {"mode": args.mode, "command": cmd,
                "source_checkpoint": str(source_checkpoint) if args.warmstart else None,
                "env": {k: v for k, v in env.items() if k.startswith("RM_")}}
    (run_dir / "launch.json").write_text(json.dumps(metadata, indent=2) + "\n")
    with (run_dir / "console.log").open("w") as log:
        p = subprocess.run(cmd, env=env, cwd=STAGE, stdout=log,
                           stderr=subprocess.STDOUT)
    report_ok = (run_dir / "report.json").is_file()
    print(f"{args.mode}: exit={p.returncode} report={report_ok} "
          f"log={run_dir / 'console.log'}", flush=True)
    # Some Isaac Kit failures finish with process exit 0 despite a Python traceback.
    raise SystemExit(p.returncode if p.returncode else (0 if report_ok else 3))


if __name__ == "__main__":
    main()
