# URGENT COMMANDER DIRECTIVE (USER COURSE CORRECTION — READ IMMEDIATELY!)

Great work on `build_rmul2027_3v3.py` (`rmul2027_3v3_stiff_v1.mjb` loads in `0.15s` with `130` boxes + `484` convex prisms, accurately capturing both `200 mm` and `250 mm` stairs plus `400 mm` highlands!).

Before you write ANY jump or stair control code, the user issued a **CRITICAL ARCHITECTURAL COURSE CORRECTION** that supersedes any earlier suggestion of external pre-crouch ticks, fake `vx_cmd` latching, speed-clamping bridges, or dual-jump-model stitching:

> **"之前gpt就有一个错误不去修复策略去加强训练策略而是在硬整面对某一种情况专门写一个应对的状态来应对，要从策略去找问题修复让策略具有泛化性和鲁棒性"**

Re-read the updated `EXTERNAL_NAV_MASTER_PLAN.md` in full right now! You MUST strictly follow these rules:

1. **ZERO Special-Case External State Hacks / Command Spoofing**:
   - **NO** external `6~12` tick pre-crouch state before jump!
   - **NO** stitching `79e27807` + `jump380_r10` by `vx < 1.25` threshold!
   - **NO** faking/latching `obs[0]` (`vx_cmd`) behind the operator's back when `W` is released mid-jump!
   - **NO** external `cmd_vx` clamping (`[0.80, 1.05] m/s`) or forced `E0` height override in the stair bridge!
   - The external layer's ONLY jobs are:
     (a) Dual-window keyboard input (`GetWindowThreadProcessId(fg) == os.getpid()` + `launch_passive` `key_callback` so `Space` triggers jump instead of viewer pause);
     (b) Theta*/A* global path planning `(x, y) -> (vx_cmd, wz_cmd)` when Auto-Nav is active;
     (c) Objective `50 Hz` extraction of `g_step = [d1, h1, d2, h2]` from the `2 cm` 2.5D LiDAR elevation map, routing cleanly between `SymmetricE0` (flat/ramps/rough), **`E_stair_nav4d`** (when an upcoming step riser is within `d1 <= 1.10 m` with forward intent until climbed), and **`E_jump_unified`** (when `Space / J` is pressed until landed & stabilized).

2. **Strengthen BOTH Neural RL Policies Directly on `host72 GPU 0` (`GPU-16828f91-2b45-b646-8dc0-9481138e2842`)**:
   - **GPU RL Training #1 — `E_jump_unified` (`obs_35 + hist_420 -> 6D`)**:
     Diagnose why donor jump failed at `h >= 0.35 m` (`0.0 cm`) and on `W`-release (`-87.9°` flip), then train **ONE single unified RL jump policy** on `host72 GPU 0` (`600`-step `0`-update `PROBE.json` + `SAFE_CLOSED.json` precheck first!) across:
     - Initial stance heights uniformly sampled in **`[0.24, 0.42] m`** (including tall-stance observation histories so the neural policy ITSELF learns to rapidly load & jump from `0.39~0.42 m` with zero external pre-crouch!);
     - Continuous initial forward speeds **`[0.0, 2.8] m/s`** + flat & `160~380 mm` platforms/steps;
     - Variable key tap/hold **`[5, 45]` ticks** AND **in-flight operator command perturbations** (dropping `cmd_vx -> 0` mid-air to simulate releasing `W`, reversing, `cmd_wz ∈ [-1.2, 1.2]` steering) + level-body air-pitch reward (`|pitch| <= 10°`, heavy penalty `> 15°`) + Full-DR!
     - Validate raw, unpatched `E_jump_unified` on the **56-case** human matrix (`evidence/JUMP_56_AUDIT.json`).
   - **GPU RL Training #2 — `E_stair_nav4d` (`obs_35 + hist_420 + g_step_4 = 459D -> 6D`)**:
     Train `E_stair_nav4d` on `host72 GPU 0` (`600`-step `0`-update `PROBE.json` + `SAFE_CLOSED.json` precheck first!) with Asymmetric Critic (`1.6m × 0.8m` height scan) across:
     - Raw unscripted `cmd_vx ∈ [0.45, 2.30] m/s`, `h_init ∈ [0.25, 0.42] m`, oblique `yaw ∈ [-30°, +30°]`;
     - `200 mm` single stairs (**`100%` non-regression gate!**), `RMUL 2027 3v3` `200 mm` & `250 mm` stairs + `200+200 mm` highlands, and `RMUC 2027 5v5` West/East double stairs (both `90°` crisp and `84°` hfield risers), with `±4 cm` `g_step` noise + Full-DR + high-stance guide-wheel clearance & anti-backflip rewards (`|pitch| > 24°` penalty, `-25` flip/regression termination)!
     - Screen all checkpoints in **400 Hz CPU MuJoCo** on `step_20`, `RMUL 2027 3v3`, and `RMUC 2027 5v5` (`rmuc2027_stiff_v1.mjb`).

Proceed now: finish the pure-numpy `RMUL2027_3V3_GEOMETRY_AUDIT.json` (fixing the missing `rtree` import in `build_rmul2027_3v3.py`), build the clean 2.5D LiDAR elevation maps & A* planner, then execute GPU RL Training #1 (`E_jump_unified`) and GPU RL Training #2 (`E_stair_nav4d`) on `host72 GPU 0`, followed by the external MuJoCo 3D playground & full acceptance!
