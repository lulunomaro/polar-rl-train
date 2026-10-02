"""Export a MOD4 rsl-rl checkpoint with its exact observation/control contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from importlib import metadata
from pathlib import Path

from isaaclab.app import AppLauncher

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

parser = argparse.ArgumentParser()
parser.add_argument("--checkpoint", required=True)
parser.add_argument("--manifest", required=True)
parser.add_argument("--out", required=True)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()

manifest = json.loads(Path(args.manifest).read_text(encoding="utf8"))
for key, value in (manifest.get("env") or {}).items():
    if key.startswith("RM_"):
        os.environ[key] = str(value)
from repair_contracts import require_explicit_training_env
require_explicit_training_env(os.environ)

launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402
from isaaclab_rl.rsl_rl import (  # noqa: E402
    RslRlMLPModelCfg, RslRlOnPolicyRunnerCfg, RslRlPpoAlgorithmCfg,
    RslRlVecEnvWrapper, handle_deprecated_rsl_rl_cfg)
from rsl_rl.runners import OnPolicyRunner  # noqa: E402
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = 1
    cfg.seed = 20260914
    if not mod4_task.attach_rmuc2026_terrain(cfg):
        raise ValueError("export requires the same RMUC2026 task contract as training")
    env = Mod4Env(cfg=cfg)
    try:
        vec = RslRlVecEnvWrapper(env, clip_actions=6.0)
        actor_class = ("mod4_sequence_model:LatentEncoderModel"
                       if os.environ["RM_SEQ_ENCODER"] == "1" else "MLPModel")
        rcfg = RslRlOnPolicyRunnerCfg(
            seed=0, device="cuda:0", num_steps_per_env=24, max_iterations=1,
            save_interval=1, experiment_name="export", run_name="export",
            clip_actions=6.0, check_for_nan=True,
            obs_groups={"actor": ["policy"], "critic": ["critic"]},
            actor=RslRlMLPModelCfg(
                class_name=actor_class, hidden_dims=[256, 128, 64], activation="elu",
                obs_normalization=False,
                distribution_cfg=RslRlMLPModelCfg.GaussianDistributionCfg(
                    init_std=0.3, std_type="scalar")),
            critic=RslRlMLPModelCfg(class_name="MLPModel", hidden_dims=[256, 128, 64],
                                    activation="elu", obs_normalization=False),
            algorithm=RslRlPpoAlgorithmCfg(
                value_loss_coef=1.0, use_clipped_value_loss=True, clip_param=0.2,
                entropy_coef=0.005, num_learning_epochs=5, num_mini_batches=4,
                learning_rate=1e-4, schedule="fixed", gamma=0.99, lam=0.95,
                desired_kl=0.01, max_grad_norm=1.0))
        rcfg = handle_deprecated_rsl_rl_cfg(rcfg, metadata.version("rsl-rl-lib"))
        runner = OnPolicyRunner(vec, rcfg.to_dict(), log_dir=None, device=rcfg.device)
        runner.load(args.checkpoint, strict=True)
        actor = runner.alg.actor
        exported = actor.as_onnx(False).cpu().eval()
        dummy = exported.get_dummy_inputs()
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        torch.onnx.export(
            exported, dummy, str(out), export_params=True, opset_version=18,
            dynamo=False, input_names=exported.input_names,
            output_names=exported.output_names, dynamic_axes={})
        with torch.inference_mode():
            expected = exported(*dummy).detach().cpu()
        import onnx
        onnx.checker.check_model(onnx.load(str(out)))
        verification = {"onnx_checker": True, "onnxruntime": False, "max_abs_error": None}
        try:
            import onnxruntime as ort
            got = ort.InferenceSession(str(out), providers=["CPUExecutionProvider"]).run(
                None, {exported.input_names[0]: dummy[0].numpy()})[0]
            err = float(torch.as_tensor(got).sub(expected).abs().max())
            verification = {"onnx_checker": True, "onnxruntime": True, "max_abs_error": err}
            if err > 1e-5:
                raise RuntimeError("ONNX numerical mismatch: %.9g" % err)
        except ImportError:
            pass
        meta = {
            "schema": "mod4_onnx_contract_v2",
            "checkpoint": str(Path(args.checkpoint).resolve()),
            "checkpoint_sha256": sha(args.checkpoint),
            "onnx_sha256": sha(out),
            "observation_semantics": manifest["observation_semantics"],
            "input_names": exported.input_names,
            "input_width": int(dummy[0].shape[-1]),
            "frame_width": 35,
            "history_length": int(os.environ["RM_SEQ_HISTORY"]),
            "action_order": mod4_task.ACTION_ORDER,
            "leg_action_scale": mod4_task.LEG_ACTION_SCALE,
            "crank_action_scale": mod4_task.CRANK_ACTION_SCALE,
            "wheel_action_scale": mod4_task.WHEEL_ACTION_SCALE,
            "policy_hz": mod4_task.POLICY_HZ,
            "controller": {"isaac_kp": mod4_task.LEG_KP, "kd": mod4_task.LEG_KD,
                           "isaac_ki": mod4_task.LEG_KI,
                           "mujoco_equivalent": {"kp": 320, "kd": 10, "ki": 90}},
            "robot_usd_sha256": sha(mod4_task.USD_PATH),
            "verification": verification,
        }
        out.with_suffix(".contract.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
        print(json.dumps(meta, ensure_ascii=False, indent=2), flush=True)
    finally:
        env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        app.close()
