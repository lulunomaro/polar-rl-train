"""Offline check of the CAD-skin tunnel terms (no simulator).

Guards the classic failure the audit keeps finding: a reward/termination that is registered,
logged and never fires.  Three synthetic roots: the drivable crouch inside the delivered hole,
a too-tall robot inside the hole, and a robot outside the hole.

    .venv-isaaclab\\Scripts\\python.exe isaac/mod4/probe_cad_clearance_math.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import torch

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import skills_isaac as skills  # noqa: E402


class _Robot:
    class data:                                       # noqa: N801 - mimic Isaac Lab's object
        root_pos_w = torch.zeros(4, 3)


class _Scene:
    """Minimal stand-in for InteractiveScene: scene['robot'] and scene.env_origins."""

    def __init__(self, robot, origins):
        self._robot, self._origins = robot, origins

    def __getitem__(self, key):
        return self._robot

    @property
    def env_origins(self):
        return self._origins


class _Env:
    def __init__(self, robot, origins):
        self.scene = _Scene(robot, origins)
        self.num_envs = int(origins.shape[0])
        self.device = origins.device


def main() -> None:
    robot = _Robot()
    env = _Env(robot, torch.zeros(4, 3))
    # local coordinates (env origin z = 0): [inside at the drivable crouch, inside too tall,
    # outside the hole]
    robot.data.root_pos_w = torch.tensor([
        [0.93, -5.95, -0.155806 + 0.178],      # drivable crouch -> 2.27 mm CAD clearance
        [0.93, -5.95, -0.155806 + 0.230],      # too tall -> CAD skin inside the roof
        [2.50, -5.95, -0.155806 + 0.178],      # past the hole -> term must not fire
        [0.93, -5.95, -0.155806 + 0.60],       # driving ON TOP of the tunnel (road) -> no fire
    ])
    rew = skills.tunnel_clearance_cad(env)
    hit = skills.tunnel_roof_hit_cad(env)
    ceil_z = skills.HOLE_CEILING_Z
    off = skills.CAD_TOP_ABOVE_ROOT_M
    for i, (name, z) in enumerate((("drivable crouch", -0.155806 + 0.178),
                                   ("too tall", -0.155806 + 0.230),
                                   ("outside", -0.155806 + 0.178),
                                   ("above the tunnel", -0.155806 + 0.60))):
        clearance = ceil_z - (z + off)
        print("[cad] %-16s root_z %+.4f  CAD top %+.4f  ceiling %+.4f  clearance %+.4f m "
              "-> reward %+.3f  roof_hit %s"
              % (name, z, z + off, ceil_z, clearance, float(rew[i]), bool(hit[i])))
    ok = (abs(float(rew[0]) - 0.002274 / 0.006) < 5e-3 and not bool(hit[0])
          and float(rew[1]) < -0.5 and bool(hit[1])
          and abs(float(rew[2])) < 1e-9 and not bool(hit[2])
          and abs(float(rew[3])) < 1e-9 and not bool(hit[3]))
    print("[cad] clearance %s" % ("PASS" if ok else "FAIL"))

    # --- staged height command (SCUT parity): approach -> pre-crouch -> inside -> recover -----
    n = 4
    robot2, env2 = _Robot(), None
    kinds = ["run"] * 13 + ["tunnel_cross", "tunnel_cross"]
    robot2.data.root_pos_w = torch.tensor([
        [2.40, -5.95, 0.02],        # past the exit: back to the normal drive height
        [0.45, -5.95, 0.02],        # 0.31 m before the mouth: pre-crouch (lead is 1.0 m)
        [0.93, -5.95, 0.02],        # inside the roofed span
        [1.60, -5.95, 0.02],        # 0.50 m past the exit: recover
    ])
    env2 = _Env(robot2, torch.zeros(n, 3))
    env2._mod4_height_cmd = torch.full((n, 1), 0.24)
    env2._mod4_route_ids = torch.tensor([13, 13, 13, 13])
    env2._mod4_route_kinds = kinds
    skills.update_tunnel_state(env2)
    got = [round(float(v), 4) for v in env2._mod4_height_cmd[:, 0]]
    want = [0.24, 0.178, 0.178, 0.30]
    print("[cad] staged height command %s (want %s)" % (got, want))
    stage_ok = all(abs(a - b) < 1e-6 for a, b in zip(got, want))
    print("[cad] stages %s" % ("PASS" if stage_ok else "FAIL"))
    return 0 if (ok and stage_ok) else 1


if __name__ == "__main__":
    sys.exit(main())
