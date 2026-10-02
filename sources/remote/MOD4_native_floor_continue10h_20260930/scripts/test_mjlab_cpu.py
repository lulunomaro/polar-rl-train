"""Can the closed-chain mjlab env be built without touching the GPU?

The production GPU is usually busy training.  ONNX export only needs the observation
layout, joint names and one probe observation, so a CPU build is enough - if mjlab
supports it.  This script answers that question without allocating any CUDA memory.
"""
from __future__ import annotations

import os

os.environ["CUDA_VISIBLE_DEVICES"] = ""

import torch  # noqa: E402

print("torch", torch.__version__, "cuda_available", torch.cuda.is_available())

from mjlab.envs import ManagerBasedRlEnv  # noqa: E402
from mjlab.tasks.registry import load_env_cfg  # noqa: E402

cfg = load_env_cfg("RM2025-Later-CC-Flat-v0", play=True)
cfg.scene.num_envs = 1
env = ManagerBasedRlEnv(cfg=cfg, device="cpu")
obs, _ = env.reset()
print("CPU ENV OK")
print("obs groups:", {k: tuple(v.shape) for k, v in obs.items()})
print("action_dim:", env.action_manager.total_action_dim)
robot = env.scene["robot"]
print("joint_names:", list(robot.joint_names))
env.close()
