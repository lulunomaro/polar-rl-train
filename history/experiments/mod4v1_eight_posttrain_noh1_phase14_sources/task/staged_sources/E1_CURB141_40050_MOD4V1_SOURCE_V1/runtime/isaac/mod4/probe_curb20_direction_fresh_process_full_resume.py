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
# 2026-09-29 PPO 对齐华南虎 agents/rsl_rl_ppo_cfg.py：std 1.0 / [512,256,128] /
# value_loss 2.0 / adaptive LR(KL 0.01)。全部可由 RM_* 覆盖，默认值与旧行为一致。
RM_HIDDEN_DIMS = [int(x) for x in os.environ.get("RM_HIDDEN_DIMS", "256,128,64").split(",")]
RM_VALUE_LOSS_COEF = float(os.environ.get("RM_VALUE_LOSS_COEF", "1.0"))
RM_SCHEDULE = os.environ.get("RM_SCHEDULE", "fixed")
RM_ENTROPY_COEF = float(os.environ.get("RM_ENTROPY_COEF", "0.005"))
RM_DESIRED_KL = float(os.environ.get("RM_DESIRED_KL", "0.01"))
launcher = AppLauncher(args)
app = launcher.app

import json  # noqa: E402
from importlib import metadata  # noqa: E402

import torch  # noqa: E402
from isaaclab.envs import ManagerBasedRLEnv  # noqa: E402
from isaaclab_rl.rsl_rl import (  # noqa: E402
    RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg,
    RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg)
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

from retention_learning_env import RetentionLearningEnv as Mod4Env
from curb20_direction_runtime import configure_retention as configure_intro  # noqa: E402
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


def build_env() -> ManagerBasedRLEnv:
    cfg = Mod4EnvCfg()
    cfg.scene.num_envs = args.num_envs
    if mod4_task.attach_rmuc2026_terrain(cfg):
        print("[mod4-isaac] RM_MOD4_MAP=rmuc2026: arena_%d terrain attached" % args.num_envs,
              flush=True)
    cfg.seed = args.seed
    configure_intro(cfg)
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
        policy=RslRlPpoActorCriticCfg(
            init_noise_std=RM_INIT_STD, actor_hidden_dims=RM_HIDDEN_DIMS,
            critic_hidden_dims=RM_HIDDEN_DIMS, activation="elu"),
        algorithm=RslRlPpoAlgorithmCfg(
            value_loss_coef=RM_VALUE_LOSS_COEF, use_clipped_value_loss=True, clip_param=0.2,
            entropy_coef=RM_ENTROPY_COEF, num_learning_epochs=5, num_mini_batches=4,
            learning_rate=args.learning_rate, schedule=RM_SCHEDULE, gamma=0.99,
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
    import hashlib
    assert args.num_envs==20000 and args.max_iterations==0 and not args.dry_run
    assert os.environ.get('RM_KEEP_STD')=='1' and os.environ.get('RM_CURB_FRESH_RESUME_ONLY')=='1'
    source=Path(args.init_checkpoint);expected=json.loads(Path(REPO/'reports/FRESH_PROCESS_BIG_CORE_VERIFIED.json').read_text())
    assert str(source)==expected['checkpoint']['path'] and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']
    env=build_env();assert int(env._sim_step_counter)==0
    log_dir=Path(args.log_root);assert not log_dir.exists();log_dir.mkdir()
    cfg=runner_config();vec=RslRlVecEnvWrapper(env,clip_actions=cfg.clip_actions)
    cfg=handle_deprecated_rsl_rl_cfg(cfg,metadata.version('rsl-rl-lib'))
    runner=OnPolicyRunner(vec,cfg.to_dict(),log_dir=str(log_dir),device=cfg.device);runner.load(str(source))
    from curb20_direction_full_checkpoint import resume_e1_new_episode,install_e1_save_contract
    proof=resume_e1_new_episode(runner,env,str(source),str(log_dir))
    assert proof['predecessor_command_state_restored_exact'] and not proof['explicitly_new_command_scope']
    terrain=json.loads((log_dir/'E1_TERRAIN_RESUME_STARTUP_VERIFIED.json').read_text())
    assert terrain['terrain_state_restored_exact'] and not terrain['explicit_G3_to_CURB_geometry_transition']
    assert terrain['entry_reset_state_restored_exact'] and not terrain['explicit_new_entry_reset_scope']
    assert int(env._sim_step_counter)==0
    install_e1_save_contract(runner,env) # no optional save on an uninitialized logger
    direction=json.loads((log_dir/'E1_CURB_DIRECTION_RESUME_STARTUP_VERIFIED.json').read_text())
    assert direction['passed'] and direction['predecessor_direction_state_restored_exact'] and not direction['explicit_new_episode_direction_scope']
    assert int(env._sim_step_counter)==0 and hashlib.sha256(source.read_bytes()).hexdigest()==expected['checkpoint']['sha256']
    v=dict(epoch=time.time(),pid=os.getpid(),passed=True,num_envs=env.num_envs,source_checkpoint=expected['checkpoint'],source_fullstate_exact=True,
        actual_same_CURB_terrain_command_private_CPUCUDA_disk_roundtrip_exact=True,all_D0_D7_actor_critic_std_optimizer_global_named_actual_restored=True,
        saved_source_episode_plus_one_verified=True,actual_control_steps=0,actual_additional_PPO_updates=0,
        original_zero_step_startup_guard_unchanged=True,own_complete_new_episode_save=None,optional_uninitialized_logger_save_not_called=True,
        proof=proof,terrain=terrain,not_PhysX_exact_resume=True,discarded_checkpoint_not_formal_learning_source=True)
    (log_dir/'FRESH_PROCESS_SAME_CURB_FULL_RESUME_PASSED.json').write_text(json.dumps(v,indent=2));env.close()
if __name__=='__main__':
    import traceback
    try:main()
    except BaseException:
        Path(REPO/'reports/FRESH_PROCESS_PROBE_ERROR.txt').write_text(traceback.format_exc());print(traceback.format_exc(),flush=True);raise
    finally:app.close()
