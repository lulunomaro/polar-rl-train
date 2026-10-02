"""Terrain-wise acceptance evaluator (audit P0-6 / P1).

Two modes:
  * arena  (RM_MOD4_MAP=rmuc2026): bucket by the delivered package's ROUTE KIND, using its own
           progress/success bookkeeping.  RM_ROUTE_KINDS selects the stage's routes.
  * field  (default): bucket by the legacy env_id % N task ids.

    $env:RM_MOD4_TERRAIN="field"; $env:RM_MOD4_MAP="rmuc2026"
    python isaac\\mod4\\eval_terrain_mod4.py --headless --checkpoint <ckpt> --num_envs 64 \
        --steps 1500 --report docs\\terrain_<tag>.json
"""
from __future__ import annotations
import argparse, json, os, sys
from pathlib import Path
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--num_envs", type=int, default=64)
parser.add_argument("--steps", type=int, default=1500)
parser.add_argument("--report", default="")
parser.add_argument("--manifest", default="",
                    help="run_manifest.json of the training run; default: next to the checkpoint")
parser.add_argument("--seed", type=int, default=20260912,
                    help="fixed seed for the nominal evaluation (goal 2026-09-12 §5)")
parser.add_argument("--domain_rand", action="store_true",
                    help="evaluate with the checkpoint manifest's DR contract instead of nominal physics")
parser.add_argument("--training_route_scope", action="store_true",
                    help="retain the manifest's shortened training goals/spawn lead for diagnosis")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

# 2026-09-12: the per-kind buckets carry COUNTS, but the acceptance bars are RATES
# ("underpass_seen >= 0.80", "air_after_launch >= 0.60"), so the report publishes both.
# These keys are the ones patch_eval_clearance.py normalises.
#
# BUG FIX: the first version of migration/linux/patch_eval_clearance.py inserted the
# `for _k in RATE_KEYS` loop below but never inserted this tuple, so EVERY evaluation raised
# `NameError: name 'RATE_KEYS' is not defined` at the very END of its 2200-step rollout (i.e.
# after ~8-10 min of GPU time) and wrote NO report.  `eval_phase()` in run_special_phases_v3.sh
# invokes the evaluator with `|| true`, so the failure was silent: the chain printed
# VERSION_CHECK=PASS and then FileNotFoundError from read_phase_eval.py.  Measured on the
# terrain phase 2026-09-12 22:18-22:37: the full eval and the ramp_up focus eval both died here.
RATE_KEYS = ("underpass_seen", "air_after_launch", "launched", "landed", "entered", "attempted")


def _find_manifest(path_hint: str, checkpoint: str):
    """(manifest dict, path) of the run that produced this checkpoint (audit item 9)."""
    cands = ([Path(path_hint)] if path_hint else [])
    ck = Path(checkpoint)
    cands += [ck.parent / "run_manifest.json", ck.parent.parent / "run_manifest.json"]
    for cand in cands:
        try:
            if cand.is_file():
                return json.loads(cand.read_text(encoding="utf8")), str(cand)
        except Exception:
            continue
    return {}, ""


# The task switches have to be in os.environ BEFORE mod4_task is imported below: MAP_MODE,
# DR_OFF and the delay/effort constants are all read at import time.  CLI wins over manifest.
MANIFEST, MANIFEST_PATH = _find_manifest(args.manifest, args.checkpoint)
APPLIED = {}
for _key, _val in (MANIFEST.get("env") or {}).items():
    if _key.startswith("RM_") and _key not in os.environ:
        os.environ[_key] = str(_val)
        APPLIED[_key] = str(_val)

# Episode-accounted acceptance.  Nominal is the default; --domain_rand keeps the
# manifest's randomized plant and delays for paired robustness measurement.
os.environ["RM_EPISODE_AUDIT"] = "1"
os.environ["RM_DR_OFF"] = "0" if args.domain_rand else "1"
os.environ["RM_ROUTE_CURRICULUM"] = "0"
os.environ["RM_JUMP_SCRIPT_PROB"] = "0"
if not args.training_route_scope:
    os.environ["RM_TUNNEL_GOAL_X"] = "0"
    os.environ["RM_TUNNEL_SPAWN_LEAD_M"] = "0"
    os.environ["RM_TUNNEL_SPAWN_DIST"] = "0"
    os.environ["RM_ROUGH_SPEED_MAX"] = "0"
os.environ["RM_ROUTE_WEIGHTS"] = ""
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from repair_contracts import REQUIRED_TRAINING_ENV  # noqa: E402
_missing_contract = [k for k in REQUIRED_TRAINING_ENV if k not in (MANIFEST.get("env") or {})]
if _missing_contract:
    raise ValueError("checkpoint manifest lacks explicit contract keys: " + ", ".join(_missing_contract))

launcher = AppLauncher(args); app = launcher.app

import torch  # noqa: E402
from importlib import metadata  # noqa: E402
from isaaclab_rl.rsl_rl import (RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg,
                                   RslRlMLPModelCfg, RslRlPpoAlgorithmCfg,
                                RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg)  # noqa: E402
from rsl_rl.runners import OnPolicyRunner  # noqa: E402
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402
from route_isaac import bucket_by_route  # noqa: E402
import skills_isaac as skills  # noqa: E402  (delivered roof geometry, deliverable 4)


def route_config(buckets) -> dict:
    """What this evaluation actually ran (audit item 9): labels, map, DR switch, filter."""
    return {
        "manifest": MANIFEST_PATH,
        "applied_from_manifest": APPLIED,
        "rm_mod4_map": os.environ.get("RM_MOD4_MAP", ""),
        "rm_mod4_terrain": os.environ.get("RM_MOD4_TERRAIN", ""),
        "rm_dr_off": os.environ.get("RM_DR_OFF", ""),
        "rm_route_kinds": os.environ.get("RM_ROUTE_KINDS", ""),
        "route_kinds_from_manifest": (MANIFEST.get("routes") or {}).get("requested_kinds"),
        "envs_per_kind": {k: v["envs"] for k, v in (buckets or {}).items()},
    }

TASK_NAMES = {0: "normal", 1: "stair", 2: "slope", 3: "tunnel", 4: "jump", 5: "gyro", 6: "island", 7: "undulation"}


def _actor_class_from_manifest() -> str:
    """The trainer picks `mod4_sequence_model:LatentEncoderModel` when RM_SEQ_ENCODER=1.

    The evaluator must pick the same, otherwise the state_dict cannot load (audit 49).
    """
    keys = {}
    for src in ((MANIFEST or {}).get("env") or {}, os.environ):
        for k, v in src.items():
            keys[k] = v
    return ("mod4_sequence_model:LatentEncoderModel"
            if str(keys.get("RM_SEQ_ENCODER", "0")).strip() == "1" else "MLPModel")


_ACTOR_CLASS = _actor_class_from_manifest()


def build_runner(vec, ckpt, manifest_path=""):
    from repair_contracts import assert_checkpoint_semantics
    assert_checkpoint_semantics(ckpt, manifest_path)
    rcfg = RslRlOnPolicyRunnerCfg(
        seed=0, device="cuda:0", num_steps_per_env=24, max_iterations=1, save_interval=1,
        experiment_name="terrain", run_name="eval", clip_actions=6.0, check_for_nan=True,
        obs_groups={"actor": ["policy"], "critic": ["critic"]},
        # v2 fix (2026-09-13, audit 49): build the actor with the SAME class the trainer used.
        # The old `RslRlPpoActorCriticCfg(actor_hidden_dims=...)` form always yields a plain
        # MLPModel, so a v2 encoder checkpoint (mlp.0 = [256, 38] + encoder.*) could not load
        # into it (the 175-D history obs sized the MLP at [256, 175]) and EVERY phase eval failed.
        actor=RslRlMLPModelCfg(
            class_name=_ACTOR_CLASS,
            hidden_dims=[256, 128, 64], activation="elu", obs_normalization=False,
            distribution_cfg=RslRlMLPModelCfg.GaussianDistributionCfg(
                init_std=0.3, std_type="scalar")),
        critic=RslRlMLPModelCfg(
            class_name="MLPModel",
            hidden_dims=[256, 128, 64], activation="elu", obs_normalization=False),
        algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=1.0, use_clipped_value_loss=True,
                                       clip_param=0.2, entropy_coef=0.005, num_learning_epochs=5,
                                       num_mini_batches=4, learning_rate=1e-4, schedule="fixed",
                                       gamma=0.99, lam=0.95, desired_kl=0.01, max_grad_norm=1.0))
    rcfg = handle_deprecated_rsl_rl_cfg(rcfg, metadata.version("rsl-rl-lib"))
    runner = OnPolicyRunner(vec, rcfg.to_dict(), log_dir=None, device=rcfg.device)
    runner.load(ckpt)
    return runner.get_inference_policy(device=vec.unwrapped.device)


def main() -> None:
    import hashlib
    from repair_contracts import EpisodeLedger, POLICY_TERMS
    if not args.report:
        raise ValueError("--report is required; use a new evidence path")
    dest = Path(args.report)
    if dest.exists():
        raise FileExistsError("refusing to overwrite an acceptance report: " + str(dest))
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    cfg.seed = args.seed
    if not mod4_task.attach_rmuc2026_terrain(cfg):
        raise ValueError("episode evaluator requires the delivered rmuc2026 arena")
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed_all(args.seed)
    env = Mod4Env(cfg=cfg)
    try:
        vec = RslRlVecEnvWrapper(env, clip_actions=6.0)
        policy = build_runner(vec, args.checkpoint, args.manifest)
        env.reset(seed=args.seed)
        obs = vec.get_observations()
        rc = env._mod4_routes
        ledger = EpisodeLedger(env.num_envs, [r["kind"] for r in rc.routes])
        # Deterministic-policy smoothness audit.  Accumulate on the GPU and synchronize only
        # once after the rollout so this measurement does not perturb the control loop.
        prev_actions = None
        prev_delta = None
        prev_valid = torch.zeros(env.num_envs, dtype=torch.bool, device=env.device)
        prev_delta_valid = torch.zeros_like(prev_valid)
        delta_sq = torch.zeros((), device=env.device)
        accel_sq = torch.zeros((), device=env.device)
        delta_max = torch.zeros((), device=env.device)
        accel_max = torch.zeros((), device=env.device)
        delta_n = 0
        accel_n = 0
        for _ in range(args.steps):
            with torch.inference_mode():
                actions = policy(obs)
            if not bool(torch.isfinite(actions).all()):
                raise RuntimeError("nonfinite evaluation action")
            if prev_actions is not None:
                da = actions - prev_actions
                valid = prev_valid.unsqueeze(1)
                delta_sq += torch.sum(torch.where(valid, da * da, torch.zeros_like(da)))
                delta_max = torch.maximum(
                    delta_max, torch.where(valid, da.abs(), torch.zeros_like(da)).max())
                delta_n += int(prev_valid.sum().item()) * actions.shape[1]
                if prev_delta is not None:
                    dda = da - prev_delta
                    accel_valid = (prev_valid & prev_delta_valid).unsqueeze(1)
                    accel_sq += torch.sum(torch.where(
                        accel_valid, dda * dda, torch.zeros_like(dda)))
                    accel_max = torch.maximum(
                        accel_max,
                        torch.where(accel_valid, dda.abs(), torch.zeros_like(dda)).max())
                    accel_n += int((prev_valid & prev_delta_valid).sum().item()) * actions.shape[1]
                prev_delta = da.detach()
            prev_actions = actions.detach()
            obs, rewards, dones, extras = vec.step(actions)
            # A reset changes observation/command discontinuously.  Exclude that boundary from
            # policy smoothness rather than charging it as actuator chatter.
            prev_delta_valid = prev_valid & (~dones.bool())
            prev_valid = ~dones.bool()
            if not bool(torch.isfinite(rewards).all()):
                raise RuntimeError("nonfinite evaluation reward")
            terminal = extras.get("repair_terminal_episodes")
            if terminal is None:
                raise RuntimeError("pre-reset episode snapshot hook is missing")
            if len(terminal) != int(dones.bool().sum()):
                raise RuntimeError("wrapper lost or duplicated a terminal episode")
            ledger.consume(terminal)
        digest = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
        # Runtime tensors establish what is actually active, not regex guesses of defaults.
        protocol = {
            "schema": "mod4_dr_protocol_v1" if args.domain_rand else "mod4_nominal_protocol_v1",
            "num_envs": env.num_envs, "step_dt": env.step_dt,
            "max_episode_length": env.max_episode_length,
            "requested_route_kinds": os.environ.get("RM_ROUTE_KINDS", ""),
            "usd_sha256": digest(mod4_task.USD_PATH),
            "route_table": rc.routes,
            "runtime_goals": rc.goals.detach().cpu().tolist(),
            "runtime_starts": rc.starts.detach().cpu().tolist(),
            "runtime_speeds": rc.speeds.detach().cpu().tolist(),
            "task_sha256": digest(HERE/"mod4_task.py"),
            "repair_sources": {p.name:digest(p) for p in sorted(HERE.glob('repair_*.py'))},
            "controller_sha256": digest(HERE/"mod4_env.py"),
            "reward_sha256": digest(HERE/"skills_isaac.py"),
            "route_adapter_sha256": digest(HERE/"route_isaac.py"),
            "sequence_sha256": digest(HERE/"mod4_sequence_model.py"),
            "observations": {k:[str(v) for v in vals] for k, vals in
                             env.observation_manager.active_terms.items()},
            "rm_env": {k:v for k,v in sorted(os.environ.items()) if k.startswith("RM_")
                and k not in {"RM_ACCEPT_TAG", "RM_INIT_STD", "RM_RETENTION_MIN"}},
        }
        encoded = json.dumps(protocol, sort_keys=True, separators=(",", ":")).encode()
        report = {
            "schema": "mod4_episode_eval_v2", "status": "ROLLOUT_COMPLETE",
            "domain_randomization": bool(args.domain_rand),
            "training_route_scope": bool(args.training_route_scope),
            "seed": args.seed, "steps_completed": args.steps,
            "checkpoint": str(Path(args.checkpoint).resolve()),
            "checkpoint_sha256": digest(args.checkpoint),
            "protocol": protocol, "protocol_sha256": hashlib.sha256(encoded).hexdigest(),
            "route_kinds": ledger.buckets(), "episodes": ledger.records,
            "censored_active_episodes": int((env.episode_length_buf > 0).sum()),
            "physical_clearance_verified": False,
            "clearance_note": "Root plus a constant is not a full articulated CAD envelope."
                " This report does not certify physical dog-hole clearance.",
            "closure_max_m": float(getattr(env, "_mod4_max_closure", float("nan"))),
            "mimic_max_rad": float(getattr(env, "_mod4_max_mimic", float("nan"))),
            "closure_post_grace_max_m": float(
                getattr(env, "_mod4_max_closure_post_grace", float("nan"))),
            "mimic_post_grace_max_rad": float(
                getattr(env, "_mod4_max_mimic_post_grace", float("nan"))),
            "action_smoothness": {
                "policy_dt_s": float(env.step_dt),
                "delta_scalar_samples": int(delta_n),
                "delta_sum_sq": float(delta_sq),
                "delta_rms_per_step": float(torch.sqrt(delta_sq / max(1, delta_n))),
                "delta_max_abs": float(delta_max),
                "second_difference_scalar_samples": int(accel_n),
                "second_difference_sum_sq": float(accel_sq),
                "second_difference_rms_per_step": float(torch.sqrt(accel_sq / max(1, accel_n))),
                "second_difference_max_abs": float(accel_max),
            },
        }
        dest.parent.mkdir(parents=True, exist_ok=True)
        # No NaN or partial report may masquerade as a pass.
        payload = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
        with dest.open("x", encoding="utf8") as f:
            f.write(payload + "\n")
        print("[episode-eval] wrote", str(dest), "completed episodes:", len(ledger.records), flush=True)
    finally:
        env.close()


if __name__ == "__main__":
    import traceback
    try:
        main()
    except BaseException:
        # Kit can terminate the interpreter while app.close() unwinds and hide the
        # original exception.  Persist it before closing so a failed acceptance run
        # can never look like a clean rollout with a missing report.
        crash = Path(args.report).with_suffix(".crash.txt") if args.report else \
            HERE / "eval_episodes_crash.txt"
        crash.parent.mkdir(parents=True, exist_ok=True)
        crash.write_text(traceback.format_exc(), encoding="utf8")
        print(traceback.format_exc(), flush=True)
        raise
    finally:
        app.close()
