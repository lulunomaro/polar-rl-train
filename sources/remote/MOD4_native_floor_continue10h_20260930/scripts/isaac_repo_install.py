"""Install the SCUT wheeled-legged_RL packages into the Isaac Lab venv and list its tasks.

Usage:  python scripts/isaac_repo_install.py [--list|--train]
The NVIDIA kit asks for EULA acceptance on first use, so stdin is fed "Yes".
"""
import argparse, os, subprocess, sys
LAB = r"D:/claude2/fangzhen/third_party/IsaacLab-3.0.0-beta2.patch1"
REPO = r"D:/claude2/fangzhen/refs/wheeled-legged_RL-main"
PY = r"D:/claude2/fangzhen/.venv-isaaclab/Scripts/python.exe"
UV = r"C:/Users/lulunomaro/.local/bin/uv.exe"
ap = argparse.ArgumentParser()
ap.add_argument("--mode", default="install", choices=["install", "list", "train"])
ap.add_argument("--task", default="Robotics-Wheelbipe-V14-Flat-v0")
ap.add_argument("--num-envs", type=int, default=64)
ap.add_argument("--iters", type=int, default=20)
a = ap.parse_args()
env = dict(os.environ, TMP=r"D:\tmp", TEMP=r"D:\tmp", TMPDIR=r"D:\tmp",
           PYTHONIOENCODING="utf-8", PYTHONUTF8="1", PYTHONCOERCECLOCALE="0", PYTHONUNBUFFERED="1",
           UV_CACHE_DIR=r"D:\uvcache", PIP_CACHE_DIR=r"D:\pipcache")
YES = open(r"D:\tmp\yes.txt", "rb")


def run(cmd, cwd=None, shell=False):
    print("+", " ".join(cmd) if isinstance(cmd, list) else cmd, flush=True)
    r = subprocess.run(cmd, cwd=cwd, env=env, stdin=open(r"D:\tmp\yes.txt", "rb"),
                       capture_output=True, text=True, shell=shell)
    out = (r.stdout or "") + (r.stderr or "")
    tail = [l for l in out.splitlines() if l.strip()][-40:]
    print("\n".join(tail), flush=True)
    print("rc =", r.returncode, flush=True)
    return r.returncode, out


if a.mode == "install":
    for pkg in ("agent_world", "agent_tasks", "agent_rl"):
        run([UV, "pip", "install", "--python", PY, "-e", os.path.join(REPO, "source", pkg)])
else:
    cwd = REPO
    if a.mode == "list":
        run([PY, os.path.join(REPO, "scripts", "list_envs.py")], cwd=cwd)
    else:
        run([PY, os.path.join(REPO, "scripts", "rsl_rl", "train.py"), "--task", a.task,
             "--num_envs", str(a.num_envs), "--headless", "--max_iterations", str(a.iters)],
            cwd=cwd)
