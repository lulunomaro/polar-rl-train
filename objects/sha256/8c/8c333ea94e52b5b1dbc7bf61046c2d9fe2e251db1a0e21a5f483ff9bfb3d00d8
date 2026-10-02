# Interactive playback integration checks

Validated locally on Windows on 2026-10-01. Private assets and generated results
remain outside Git; this repository contains source and synthetic protocol tests.

| Check | Result |
|---|---|
| Protocol/display tests | 6 passed: stale/foreign/malformed commands, pause/reset/quit, Windows replacement locks, session lock, runtime validation, body pose contract |
| Tk driver interactions | Forward, reverse, release to stop, pause/resume, key-repeat debounce, reset, graceful stop request passed |
| PowerShell launcher | Parser check passed |
| Existing authorized ONNX/MJCF adapter | 150 headless control steps, no fault; final closure residual 0.00095 mm |
| New native Isaac bridge | 120 control steps / 1.2 simulated seconds; no fault; maximum closure 0.05785 mm, mimic 0.00098 rad |
| Source USD display export | 31 bodies, 277 visual meshes, 1,038,138 triangles |
| Native pose → MuJoCo display | Exact body-set agreement; position error 0 m for the tested packet |

The native test used the existing authorized MOD4 compatibility bundle with Isaac
Sim 5.1 / Isaac Lab 2.3.2, CPU physics, deterministic actor inference and the
bundle's detailed USD. The display has `nq=nv=0`; its result tests rendering and
pose mapping, not MuJoCo dynamics. The original delivery's longer driving tests
are separate from this short integration check.

These checks establish launcher/control integration. They do not certify a policy
for arbitrary terrain, a different robot description, another Isaac API, or real
hardware. The ONNX adapter still needs controller and MJCF matching for each
new policy; the example JSON intentionally documents the original adapter.

Re-run source tests:

```powershell
python -m unittest discover -s tests -v
```
