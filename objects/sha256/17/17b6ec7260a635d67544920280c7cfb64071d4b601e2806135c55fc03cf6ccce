# -*- coding: utf-8 -*-
"""GPU scaling probe: what does one more environment actually cost?

  python scripts/gpu_scale.py --envs 4096 [--njmax 320] [--nconmax 48] [--steps 300]

Builds the closed-chain task, prints the profile in force, then runs random-action
policy steps and reports policy-steps/s, physics-steps/s and memory.  Nothing trains.
"""
import argparse
import sys
import time

ap = argparse.ArgumentParser()
ap.add_argument("--envs", type=int, default=2048)
ap.add_argument("--njmax", type=int, default=None)
ap.add_argument("--nconmax", type=int, default=None)
ap.add_argument("--steps", type=int, default=300)
ap.add_argument("--task", default="RMVehicle-CC-Skills-v0")
ap.add_argument("--iterations", type=int, default=None)
ap.add_argument("--ls-iterations", type=int, default=None)
ap.add_argument("--tolerance", type=float, default=None)
ap.add_argument("--solver", default=None)
ap.add_argument("--dt", type=float, default=None)
a = ap.parse_args()

sys.path.insert(0, r"D:/claude2/fangzhen/train/rmvehicle/src")
import torch
from mjlab.envs import ManagerBasedRlEnv
from mjlab.tasks.registry import load_env_cfg

torch.cuda.init()
free0, total0 = torch.cuda.mem_get_info()
print("cuda before : free=%.2f/%.2f GiB" % (free0 / 2**30, total0 / 2**30))

cfg = load_env_cfg(a.task)
cfg.scene.num_envs = a.envs
if a.njmax is not None:
  cfg.sim.njmax = a.njmax
if a.nconmax is not None:
  cfg.sim.nconmax = a.nconmax
if a.iterations is not None:
  cfg.sim.mujoco.iterations = a.iterations
if a.ls_iterations is not None:
  cfg.sim.mujoco.ls_iterations = a.ls_iterations
if a.tolerance is not None:
  cfg.sim.mujoco.tolerance = a.tolerance
if a.solver is not None:
  cfg.sim.mujoco.solver = a.solver
if a.dt is not None:
  cfg.sim.mujoco.timestep = a.dt
env = ManagerBasedRlEnv(cfg=cfg, device="cuda:0")

m = env.sim.mj_model
print("model  : nq=%d nv=%d nu=%d neq=%d ngeom=%d mj-timestep=%g"
      % (m.nq, m.nv, m.nu, m.neq, m.ngeom, m.opt.timestep))
print("sim    : nconmax=%s njmax=%s decimation=%s dt=%g"
      % (env.cfg.sim.nconmax, env.cfg.sim.njmax, env.cfg.decimation, env.cfg.sim.mujoco.timestep))
try:
  ents = dict(env.cfg.scene.entities) if not isinstance(env.cfg.scene.entities, dict) else env.cfg.scene.entities
  arts = ents["robot"].articulation.actuators
  for name, ac in arts.items():
    print("  actuator %-12s %-24s effort=%s sat=%s vmax=%s kp=%s kd=%s" %
          (name, type(ac).__name__, getattr(ac, "effort_limit", None),
           getattr(ac, "saturation_effort", None), getattr(ac, "velocity_limit", None),
           getattr(ac, "stiffness", None), getattr(ac, "damping", None)))
except Exception as e:
  print("actuator introspection failed:", type(e).__name__, e)

obs, _ = env.reset()
o = obs["actor"] if isinstance(obs, dict) else obs
print("obs    :", tuple(o.shape))
nenv = env.unwrapped.num_envs
DIM = 6


def kick(scale):
  act = torch.empty(nenv, DIM, device="cuda:0").uniform_(-scale, scale)
  return env.step(act)


for _ in range(25):
  kick(0.05)
torch.cuda.synchronize()
peak_setup = torch.cuda.max_memory_allocated() / 2**30
t0 = time.perf_counter()
for _ in range(a.steps):
  kick(0.3)
torch.cuda.synchronize()
dt = time.perf_counter() - t0
import subprocess
try:
    sm = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'],
                        capture_output=True, text=True, timeout=20).stdout.strip().splitlines()[0]
    print('VRAM  : GPU memory.used = %s MiB (nothing else on the card)' % sm)
except Exception as e:
    print('nvidia-smi probe failed:', e)
free1, _ = torch.cuda.mem_get_info()
ps = a.steps / dt
print("RESULT : envs=%-5d policy-steps/s=%8.1f physics-steps/s=%9.1f torch-peak=%.2f GiB cuda-free=%.2f GiB"
      % (a.envs, ps, ps * env.cfg.decimation, peak_setup, free1 / 2**30))
print("         %.1f ms/policy-step  %.1f us/env-step  %.2f MiB/env(torch peak)"
      % (1000 * dt / a.steps, 1e6 * dt / (a.steps * nenv), peak_setup * 1024 / nenv))
try:
  print("contacts: max per world = %d (nconmax=%s)" % (int(env.sim.data.ncon.max().item()), env.cfg.sim.nconmax))
except Exception as e:
  print("contacts probe failed:", type(e).__name__, e)
