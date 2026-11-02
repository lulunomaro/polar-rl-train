"""Check the CAD input-difference projection on the TRAINING action path (2026-09-12).

Commands three raw leg actions (inside the window, far past the stop, and the shallow side) and
prints what the action term actually writes as joint-position targets, plus the resulting
(crank - hip) difference.  There is no physics stepping here: this checks the projection itself.

    .venv-isaaclab\\Scripts\\python.exe isaac/mod4/probe_coupling_clamp.py --headless
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser()
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
launcher = AppLauncher(args)
app = launcher.app

import torch  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mod4_task  # noqa: E402
from mod4_env import Mod4Env  # noqa: E402


def main() -> None:
    cfg = mod4_task.Mod4EnvCfg()
    cfg.scene.num_envs = 3
    env = Mod4Env(cfg=cfg)
    env.reset()
    term = env.action_manager.get_term("legs")
    idx = {n: i for i, n in enumerate(mod4_task.ACTION_ORDER)}
    scale = mod4_task.LEG_ACTION_SCALE
    print("[clamp] contract training window: %s" % (mod4_task.CONTRACT.get("training_window"),),
          flush=True)
    print("[clamp] term.diff_min=%.4f term.diff_max=%.4f" % (term.diff_min, term.diff_max),
          flush=True)
    cases = [("inside", 0.30, -1.00), ("past_stop", 0.30, -1.60), ("shallow", 0.30, 0.60)]
    for label, hip, crank in cases:
        # The "legs" action term owns 4 slots in LEG_ORDER:
        # [left_crank, left_hip, right_crank, right_hip].
        raw = torch.zeros((3, 4), device=env.device)
        raw[:, 0] = crank / scale
        raw[:, 1] = hip / scale
        raw[:, 2] = crank / scale
        raw[:, 3] = hip / scale
        # The action term owns a 0..ACTION_DELAY_MAX control-step delay line, so push the same
        # command several times before sampling the targets (otherwise envs show stale actions
        # from the previous case, which looks like a broken clamp).
        for _ in range(mod4_task.ACTION_DELAY_MAX + 2):
            term.process_actions(raw)
        pa = term.processed_actions
        for e in range(3):
            lc, lh = float(pa[e, 0]), float(pa[e, 1])
            rc, rh = float(pa[e, 2]), float(pa[e, 3])
            print("[clamp] %-10s env %d  target hip %+.3f crank %+.3f -> diff %+.4f  "
                  "(requested %+.4f)" % (label, e, lh, lc, lc - lh, crank - hip), flush=True)
    env.close()


if __name__ == "__main__":
    main()
    app.close()
