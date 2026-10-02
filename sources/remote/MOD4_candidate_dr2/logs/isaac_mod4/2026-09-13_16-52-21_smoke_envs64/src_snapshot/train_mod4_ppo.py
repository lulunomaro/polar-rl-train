r"""PPO training entry point for the MOD4 Isaac Lab task (see mod4_task.py).

Examples (run from the repo root):

  # contract / engine smoke: 32 envs, 200 env steps, prints the live contract
  .venv-isaaclab\Scripts\python.exe isaac\mod4\train_mod4_ppo.py --num_envs 32 --dry_run 200

  # short training smoke: 64 envs, 10 iterations
  .venv-isaaclab\Scripts\python.exe isaac\mod4\train_mod4_ppo.py --num_envs 64 --max_iterations 10 --run_name smoke

  # real run on this box (RTX 3060 12 GB); scale to taste
  .venv-isaaclab\Scripts\python.exe isaac\mod4\train_mod4_ppo.py --num_envs 4096 --max_iterations 3000 --run_name mod4_isaac_v1
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

THIS = Path(__file__).resolve().parent
REPO = THIS.parents[1]
sys.path.insert(0, str(THIS))

parser = argparse.ArgumentParser(description="MOD4 Isaac Lab PPO")
parser.add_argument("--num_envs", type=int, default=256)
parser.add_argument("--max_iterations", type=int, default=100,
                    help="DEPRECATED alias for --additional_iterations (loading model_6450.pt with --max_iterations 8000 silently trained to 14450)")
parser.add_argument("--target_iteration", type=int, default=0,
                    help="train until this TOTAL iteration (warm start included)")
parser.add_argument("--additional_iterations", type=int, default=0,
                    help="iterations to run ON TOP of the checkpoint's iteration")
parser.add_argument("--run_name", type=str, default="mod4_isaac_v1")
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--save_interval", type=int, default=50)
parser.add_argument("--steps_per_env", type=int, default=24)
parser.add_argument("--learning_rate", type=float, default=1.0e-4)
parser.add_argument("--log_root", type=str, default=str(REPO / "logs" / "isaac_mod4"))
parser.add_argument("--report", type=str, default="")
parser.add_argument("--init_checkpoint", type=str, default="",
                    help="warm start: load these PPO weights before learning (e.g. a flat-terrain "
                         "locomotion policy, the mjlab-proven way to get skills on terrain)")
parser.add_argument("--dry_run", type=int, default=0,
                    help="run this many env steps with zero actions and exit")

from isaaclab.app import AppLauncher  # noqa: E402

AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

# The validated mjlab recipe (train/rmvehicle/src/rmvehicle/rl_cfg.py) uses init std 0.3 with the
# linear 'scalar' parameterisation; 1.0 (the rsl_rl default) is 3.3x larger and, on a balancing
# wheeled biped, means +-10 rad/s of wheel noise from step 0 -- the 2026-09-11 02:36 run held
# std ~1.0 for 100 iterations while episodes lasted 11-15 steps (the mjlab run of the same plant
# sits at std 0.05 / 23-89 steps).  Override with RM_INIT_STD.
RM_INIT_STD = float(os.environ.get("RM_INIT_STD", "0.3"))
launcher = AppLauncher(args)
app = launcher.app

import json  # noqa: E402
from importlib import metadata  # noqa: E402

import torch  # noqa: E402
from isaaclab.envs import ManagerBasedRLEnv  # noqa: E402
from isaaclab_rl.rsl_rl import (  # noqa: E402
    RslRlMLPModelCfg, RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg,
    RslRlPpoAlgorithmCfg, RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg)
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

from mod4_env import Mod4Env  # noqa: E402
import mod4_task  # noqa: E402
from mod4_task import Mod4EnvCfg, contract_report  # noqa: E402


def _isaaclab_version() -> str:
    try:
        return metadata.version("isaaclab")
    except Exception:
        return "n/a"


def _warm_start_with_reset_std(path: str, std: float) -> str:
    """Return a checkpoint whose exploration noise has been re-opened (else `path` unchanged).

    A warm start inherits the checkpoint's exploration std along with its weights: the stage1f
    lineage had decayed to 0.082 (measured in model_8300.pt, key `distribution.std_param`), and
    0.082 x 0.5 rad is +-0.04 rad of leg motion -- far too little to discover a new gait.  The
    measurement that proves it matters: the "run" stage stood still for 250 iterations while
    the route-progress reward paid 2.0/step for driving.  Setting the tensor inside the live
    runner was version-fragile (rsl_rl moved the attribute), so the ONE tensor is rewritten in
    a copy of the checkpoint instead: visible, auditable, API-independent.  RM_KEEP_STD=1 keeps
    the checkpoint's own value.
    """
    if os.environ.get("RM_KEEP_STD", "").strip() == "1":
        return path
    try:
        import math
        import tempfile
        ck = torch.load(path, map_location="cpu", weights_only=False)
        sd = ck.get("model_state_dict") or ck.get("actor_state_dict")
        keys = [k for k in (sd or {}) if k.endswith("std_param") or k.endswith("log_std_param")]
        if not keys:
            print("[mod4-isaac] std reset: no noise parameter in " + str(path), flush=True)
            return path
        old = sum(float(sd[k].mean()) for k in keys) / len(keys)
        for k in keys:
            sd[k] = (torch.full_like(sd[k], math.log(std)) if k.endswith("log_std_param")
                     else torch.full_like(sd[k], std))
        out = os.path.join(tempfile.gettempdir(), "warmstart_std%.3f.pt" % std)
        torch.save(ck, out)
        print("[mod4-isaac] exploration std %.4f -> %.3f (%s)"
              % (old, std, ", ".join(keys)), flush=True)
        return out
    except Exception as exc:
        print("[mod4-isaac] std reset failed (%r); using the checkpoint as-is" % (exc,),
              flush=True)
        return path


def _partial_warm_start(path: str, frame_dim: int, out_dim: int) -> str:
    """Allow exactly the known frame->frame+latent upgrade. Never hide load errors."""
    import tempfile
    if os.environ.get("RM_PARTIAL_WARMSTART", "1").strip() != "1":
        return path
    ck = torch.load(path, map_location="cpu", weights_only=False)
    sd = ck.get("actor_state_dict") or {}
    w = sd.get("mlp.0.weight")
    if w is None:
        raise ValueError("checkpoint has no actor first layer")
    if w.ndim != 2:
        raise ValueError("checkpoint actor first layer must be a matrix")
    if int(w.shape[1]) == int(out_dim):
        return path
    if int(w.shape[1]) != int(frame_dim) or out_dim <= frame_dim:
        raise ValueError("unsupported warm-start input layout")
    if any(k.startswith("encoder.") for k in sd):
        raise ValueError("encoder checkpoint cannot be treated as a plain-policy upgrade")
    sd["mlp.0.weight"] = torch.cat([w, w.new_zeros(w.shape[0], out_dim-frame_dim)], dim=1)
    ck.pop("optimizer_state_dict", None)
    fd, out = tempfile.mkstemp(prefix="mod4_partial_", suffix=".pt")
    os.close(fd)
    torch.save(ck, out)
    print("[repair] warm-start copy: " + out, flush=True)
    return out


def _load_partial(runner, path: str, actor_dim: int) -> None:
    """Only a COMPLETE new encoder may be absent; actor head and critic must match."""
    from repair_contracts import validate_warmstart
    checkpoint = torch.load(path, map_location="cpu", weights_only=False)
    partial = os.environ.get("RM_PARTIAL_WARMSTART", "1").strip() == "1"
    missing = validate_warmstart(runner.alg.actor.state_dict(),
                                runner.alg.critic.state_dict(), checkpoint, partial)
    if missing:
        print("[repair] deliberate encoder initialization: " + ", ".join(missing), flush=True)
    if partial:
        runner.load(path, load_cfg={"actor": True, "critic": True,
                    "optimizer": False, "iteration": False}, strict=not missing)
    else:
        runner.load(path, strict=True)


def build_env() -> ManagerBasedRLEnv:
    cfg = Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    if mod4_task.attach_rmuc2026_terrain(cfg):
        print("[mod4-isaac] RM_MOD4_MAP=rmuc2026: arena_%d terrain attached" % args.num_envs,
              flush=True)
    cfg.seed = args.seed
    # Mod4Env = ManagerBasedRLEnv + the per-step event mode (gas-spring preload, air state,
    # SCUT push and actuator noise) that stock Isaac Lab never applies; see mod4_env.py.
    env = Mod4Env(cfg=cfg)
    # Aim the Kit viewport at the first environment: the robot on the centre lane, stairs and
    # ramps ahead, tunnel lane to its left.  Without this the window opens on empty space
    # because the default camera looks nowhere near the field.
    try:
        env.sim.set_camera_view([3.0, -3.4, 1.6], [0.9, 0.25, 0.32])
    except Exception as exc:  # viewer-only nicety; never fatal for training
        print("[mod4-isaac] camera view not set: %s" % exc, flush=True)
    return env


# v2 item 1: actor history + latent encoder (see isaac/mod4/mod4_sequence_model.py).
# RM_SEQ_ENCODER=1 turns it on; the actor model then consumes history*35 inputs and
# feeds [newest frame | latent] to its MLP.  The critic always stays a plain MLP over
# the privileged observation set.
SEQ_ENCODER = os.environ.get("RM_SEQ_ENCODER", "0").strip() == "1"
SEQ_HISTORY = int(os.environ.get("RM_SEQ_HISTORY", "5")) if SEQ_ENCODER else 0
SEQ_LATENT = int(os.environ.get("RM_SEQ_LATENT", "3"))
SEQ_ENCODER_HIDDEN = [int(v) for v in
                      os.environ.get("RM_SEQ_ENCODER_HIDDEN", "128,64").split(",")]
SEQ_ACTOR_CLASS = ("mod4_sequence_model:LatentEncoderModel" if SEQ_ENCODER
                   else "MLPModel")


def runner_config() -> RslRlOnPolicyRunnerCfg:
    return RslRlOnPolicyRunnerCfg(
        seed=args.seed,
        device=args.device,
        num_steps_per_env=args.steps_per_env,
        max_iterations=args.max_iterations,
        obs_groups={"actor": ["policy"], "critic": ["critic"]},   # silences the rsl_rl 5.x
                                                               # "obs_groups has no actor key" warning
        save_interval=args.save_interval,
        experiment_name="mod4_isaac",
        run_name=args.run_name,
        clip_actions=6.0,
        check_for_nan=True,
        # v2 item 1: separate actor/critic model configs.  RslRlPpoActorCriticCfg is
        # deprecated for rsl-rl >= 4.0.0 (isaaclab_rl/rsl_rl/rl_cfg.py:356-360) and
        # rsl_rl 4.x resolves the two model classes independently
        # (rsl_rl/algorithms/ppo.py:477-497), which is what lets the actor carry the
        # encoder while the critic stays a plain MLP over the privileged set.
        actor=RslRlMLPModelCfg(
            class_name=SEQ_ACTOR_CLASS,
            hidden_dims=[256, 128, 64], activation="elu",
            obs_normalization=False,
            distribution_cfg=RslRlMLPModelCfg.GaussianDistributionCfg(
                init_std=RM_INIT_STD, std_type="scalar"),
            # v2 fix (2026-09-13): the custom dimensions are NOT cfg fields -- passing them here
            # raised "TypeError: RslRlMLPModelCfg.__init__() got an unexpected keyword argument
            # 'frame_dim'".  LatentEncoderModel reads RM_SEQ_LATENT / RM_SEQ_ENCODER_HIDDEN itself.
            ),
        critic=RslRlMLPModelCfg(
            class_name="MLPModel",
            hidden_dims=[256, 128, 64], activation="elu",
            obs_normalization=False),
        algorithm=RslRlPpoAlgorithmCfg(
            value_loss_coef=1.0, use_clipped_value_loss=True, clip_param=0.2,
            entropy_coef=0.005, num_learning_epochs=5, num_mini_batches=4,
            learning_rate=args.learning_rate, schedule="fixed", gamma=0.99,
            lam=0.95, desired_kl=0.01, max_grad_norm=1.0),
    )


def describe(env: ManagerBasedRLEnv, extra: dict) -> dict:
    info = dict(contract_report())
    info.update(extra)
    info["action_dim"] = env.action_manager.total_action_dim
    info["policy_obs_dim"] = int(sum(env.observation_manager.group_obs_dim["policy"]))
    info["critic_obs_dim"] = int(sum(env.observation_manager.group_obs_dim["critic"]))
    info["policy_obs_terms"] = list(env.observation_manager.active_terms["policy"])
    info["policy_obs_dims"] = [list(map(int, d))
                              for d in env.observation_manager.group_obs_term_dim["policy"]]
    terms = getattr(env.action_manager, "_terms", {})
    info["action_terms"] = {name: {"joints": list(getattr(term, "_joint_names", [])),
                                   "dim": int(term.action_dim)}
                            for name, term in terms.items()}
    info["num_envs"] = env.num_envs
    info["device"] = str(env.device)
    return info


def dry_run(env: ManagerBasedRLEnv, steps: int) -> dict:
    """Zero-action rollout: proves the env steps, counts terminations, tracks closures."""
    env.reset()
    zeros = torch.zeros(env.num_envs, env.action_manager.total_action_dim,
                        device=env.device)
    reward_sum = 0.0
    terminations = {}
    start = time.perf_counter()
    for _ in range(steps):
        _, reward, terminated, truncated, extras = env.step(zeros)
        reward_sum += float(reward.mean().item())
        for key, value in extras.get("log", {}).items():
            if "Episode_Termination" in key:
                terminations[key] = float(value)
    wall = time.perf_counter() - start
    return {
        "steps": steps,
        "wall_s": wall,
        "policy_steps_per_s": steps / max(wall, 1e-9),
        "physics_steps_per_s": steps * env.num_envs * env.cfg.decimation / max(wall, 1e-9),
        "mean_reward": reward_sum / max(1, steps),
        "mean_episode_len_steps": float(env.episode_length_buf.float().mean().item()),
        "max_episode_len_steps": float(env.episode_length_buf.max().item()),
        "terminations": terminations,
        "max_closure_error_m": float(getattr(env, "_mod4_max_closure", float("nan"))),
    }


def main() -> None:
    env = build_env()
    info = describe(env, {"mode": "dry_run" if args.dry_run else "train"})
    print("[mod4-isaac] " + json.dumps(info, indent=2), flush=True)
    if args.dry_run:
        result = dry_run(env, args.dry_run)
        print("[mod4-isaac] dry run: " + json.dumps(result, indent=2), flush=True)
        info["dry_run"] = result
        if args.report:
            Path(args.report).write_text(json.dumps(info, indent=2), encoding="utf8")
        env.close()
        return
    log_dir = os.path.join(args.log_root,
                           datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + args.run_name)
    os.makedirs(log_dir, exist_ok=True)
    cfg = runner_config()
    vec_env = RslRlVecEnvWrapper(env, clip_actions=cfg.clip_actions)
    # rsl-rl >= 4 wants explicit actor/critic model configs; Isaac Lab derives them from
    # the legacy `policy` block through this helper (same call as scripts/rsl_rl/train.py).
    cfg = handle_deprecated_rsl_rl_cfg(cfg, metadata.version("rsl-rl-lib"))
    runner = OnPolicyRunner(vec_env, cfg.to_dict(), log_dir=log_dir, device=cfg.device)
    if args.init_checkpoint:
        warm = _warm_start_with_reset_std(args.init_checkpoint, RM_INIT_STD)
        # v2 item 1: the encoder changes the actor input (35 -> history*35) and adds
        # `encoder.*` parameters, so a strict load refuses every existing checkpoint.
        # This pads the first layer with zeros and skips the (now mismatched)
        # optimizer state; see _partial_warm_start.
        from repair_contracts import assert_checkpoint_semantics
        assert_checkpoint_semantics(args.init_checkpoint)
        warm = _partial_warm_start(warm, 35, 35 + SEQ_LATENT if SEQ_ENCODER else 35)
        _load_partial(runner, warm, 35)
        print("[mod4-isaac] warm start from " + args.init_checkpoint
              + ("" if warm == args.init_checkpoint else " (std reset copy: %s)" % warm),
              flush=True)
    # audit P3: every run records what it actually trained on -- config, asset hash, warm-start
    # hash and software versions -- so "warmstart_base11.pt" style names can never drift from
    # their real provenance again.
    def _sha256(path):
        import hashlib
        try:
            h = hashlib.sha256()
            with open(path, "rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception as exc:
            return "unavailable: %r" % (exc,)

    def _route_manifest():
        """The route table this run actually trains on (audit item 9).

        RM_ROUTE_KINDS is a *filter*: the ids the adapter publishes, the observation mode bits
        and the evaluator's per-route buckets all mean different things with and without it, so
        the resolved list -- not just the raw string -- belongs in the manifest.
        """
        kinds = [k.strip() for k in os.environ.get("RM_ROUTE_KINDS", "").split(",") if k.strip()]
        path = mod4_task.RMUC2026_ISAAC.parent / "data" / "routes.json"
        info = {"requested_kinds": kinds or "all", "routes_json": str(path)}
        try:
            routes = json.loads(path.read_text(encoding="utf8"))
            keep = [i for i, r in enumerate(routes) if not kinds or r["kind"] in kinds]
            info["total"] = len(routes)
            info["allowed"] = [{"index": i, "kind": routes[i]["kind"], "id": routes[i]["id"]}
                               for i in keep]
            info["filtered_out"] = len(routes) - len(keep)
        except Exception as exc:
            info["error"] = repr(exc)
        return info

    def _effective_knobs():
        """Every RM_* knob the sources read, with the value the code resolves for it."""
        out = {}
        here = Path(__file__).resolve().parent
        # NOT `os.environ.get(` only.  Measured 2026-09-13: 112 RM_* names appear in the sources but
        # only 80 go through os.environ.get directly -- the other 32 (INCLUDING the v2 knobs
        # RM_ACTION_DELAY_MS_*, RM_CURR_*, RM_EFFORT_*, RM_OBS_DELAY_*) are read through helpers such
        # as `_f("RM_X", default)`, which that pattern cannot see.  Verifying with the SAME pattern
        # the code uses proves only self-consistency, never completeness -- the earlier "100 %" was
        # measured that way and was wrong.  So match ANY quoted RM_ literal on the line.
        for path in sorted(here.glob("*.py")):
            try:
                text = path.read_text(encoding="utf8")
            except Exception:
                continue
            for line in text.splitlines():
                for quote in ('"', "'"):
                    needle = quote + "RM_"
                    pos = line.find(needle)
                    while pos >= 0:
                        rest = line[pos + 1:]
                        end = rest.find(quote, 1)
                        if end > 0:
                            knob = rest[:end]
                            default = ""
                            tail = rest[end + 1:]
                            if "," in tail:
                                default = tail.split(",", 1)[1].split(")", 1)[0].strip()
                                for ch in ('"', "'"):
                                    default = default.strip(ch)
                            out[knob] = os.environ.get(knob, default)
                        pos = line.find(needle, pos + 1)
        return dict(sorted(out.items()))

    manifest = {
        "observation_semantics": "mod4_term_major_latest_gather_v1" if SEQ_ENCODER else "mod4_plain_frame35_v1",
        "effective_values_verified": False,
        "effective_note": "legacy regex source hints; runtime_contract below records selected resolved values",
        "runtime_contract": {"sequence_encoder": SEQ_ENCODER, "history_length": SEQ_HISTORY,
            "latent_width": SEQ_LATENT, "step_dt": env.step_dt,
            "repair_sources": {p.name: _sha256(p) for p in Path(__file__).parent.glob("repair_*.py")}},
        "run_name": args.run_name,
        "num_envs": args.num_envs,
        "terrain": os.environ.get("RM_MOD4_TERRAIN", "flat"),
        "skill_tasks": os.environ.get("RM_SKILL_TASKS", "all"),
        # audit item 9 (2026-09-11): the TASK is switched by environment variables -- the map,
        # the route filter (which decides what the ids, the mode bits and the evaluator's
        # labels mean), the DR switch and the jump curriculum window.  None of that was
        # recorded, so two runs with identical CLI arguments could train different tasks.
        "env": {k: os.environ[k] for k in sorted(os.environ) if k.startswith("RM_")},
        # v2: the EFFECTIVE configuration -- every RM_* knob the sources read, with the value
        # the code resolves (env when set, else the source default).  Derived from the source, so
        # it cannot drift.  See docs/MOD4_V2_REDESIGN_AUDIT_20260912.md section 12.
        "effective": _effective_knobs(),
        "routes": _route_manifest(),
        "code_sha256_12": {
            name: (_sha256(Path(__file__).resolve().parent / name)[:12])
            for name in ("mod4_task.py", "skills_isaac.py", "route_isaac.py",
                         "train_mod4_ppo.py", "probe_jump_reward.py")
        },
        "max_iterations_arg": args.max_iterations,
        "target_iteration_arg": args.target_iteration,
        "additional_iterations_arg": args.additional_iterations,
        "start_iteration": int(getattr(runner, "current_learning_iteration", 0) or 0),
        "init_checkpoint": args.init_checkpoint,
        "init_checkpoint_sha256": _sha256(args.init_checkpoint) if args.init_checkpoint else "",
        "robot_usd": str(mod4_task.MOD4_ISAAC / "robot.usd"),
        "robot_usd_sha256": _sha256(mod4_task.MOD4_ISAAC / "robot.usd"),
        "import_contract_sha256": _sha256(mod4_task.MOD4_ISAAC / "import_contract.json"),
        "versions": {"torch": torch.__version__,
                     "rsl_rl": metadata.version("rsl-rl-lib"),
                     "isaaclab": metadata.version("isaaclab") if _isaaclab_version() else "n/a"},
    }
    # --- version freeze (goal 2026-09-12 §1) ------------------------------------------------
    # Both earlier training processes were launched at 07:25 and the task sources were edited at
    # 08:27, so their checkpoints were later evaluated against a DIFFERENT code revision.  Copy
    # the exact bytes this run loads into the run directory and record full hashes, so the
    # evaluator can prove "same version" instead of assuming it.
    import shutil
    snapshot_dir = Path(log_dir) / "src_snapshot"
    snapshot_dir.mkdir(exist_ok=True)
    snapshot = {}
    for name in ("mod4_task.py", "skills_isaac.py", "route_isaac.py", "train_mod4_ppo.py"):
        src = Path(__file__).resolve().parent / name
        if src.is_file():
            shutil.copy2(src, snapshot_dir / name)
            snapshot[name] = _sha256(src)
    for name in ("robot.usd", "import_contract.json", "robot_cfg.py"):
        src = Path(mod4_task.MOD4_ISAAC) / name
        if src.is_file():
            shutil.copy2(src, snapshot_dir / name)
            snapshot[name] = _sha256(src)
    manifest["src_sha256"] = snapshot
    Path(log_dir, "run_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf8")
    print("[mod4-isaac] manifest: " + json.dumps(manifest, indent=2)[:1200], flush=True)
    print("[mod4-isaac] log_dir=" + log_dir, flush=True)
    # audit item 7: resolve the target ONCE, after the checkpoint's iteration is known.
    start_iter = int(getattr(runner, "current_learning_iteration", 0) or 0)
    if args.target_iteration:
        n_iter = max(0, args.target_iteration - start_iter)
    elif args.additional_iterations:
        n_iter = args.additional_iterations
    else:
        n_iter = args.max_iterations
    print("[mod4-isaac] start_iteration=%d  will_run=%d  target=%d"
          % (start_iter, n_iter, start_iter + n_iter), flush=True)
    runner.learn(num_learning_iterations=n_iter, init_at_random_ep_len=True)
    info["log_dir"] = log_dir
    info["max_closure_error_m"] = float(getattr(env, "_mod4_max_closure", float("nan")))
    if args.report:
        Path(args.report).write_text(json.dumps(info, indent=2), encoding="utf8")
    env.close()


if __name__ == "__main__":
    # Kit tears the interpreter down inside app.close(), which can swallow a traceback;
    # write it to disk first so a failed launch is diagnosable instead of silent.
    import traceback

    try:
        main()
    except BaseException:
        crash = REPO / "isaac" / "mod4" / "train_crash.txt"
        crash.write_text(traceback.format_exc(), encoding="utf8")
        print(traceback.format_exc(), flush=True)
        raise
    finally:
        app.close()
