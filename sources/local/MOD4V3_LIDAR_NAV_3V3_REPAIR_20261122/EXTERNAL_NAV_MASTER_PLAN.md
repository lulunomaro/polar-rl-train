# MOD4v3 External LiDAR Nav + Pure-RL Generalized Jump & Stair Policies Master Plan (NO Special-Case State Hacks!)

## 0. CRITICAL ARCHITECTURAL MANDATE FROM COMMANDER & USER (NON-NEGOTIABLE!)
**STRICT BAN ON CASE-BY-CASE EXTERNAL STATE HACKS / COMMAND SPOOFING**:
- Previously, GPT made the mistake of writing brittle external workarounds (`if height > 0.31: run 8 ticks of E0 pre-crouch`, `if vx < 1.25: stitch model A else overwrite obs[0] with latched vx_cmd and run model B`, `if approaching stair: externally clamp user vx_cmd to [0.80, 1.05]`, or fitting 10 fragile detector thresholds to specific test seeds) instead of **fixing the root training distribution & rewards so the RL neural policies themselves generalize and stay robust**!
- **YOU ARE STRICTLY FORBIDDEN FROM**:
  1. Adding an external pre-crouch state before jump (`E_jump_unified` MUST receive raw `obs` directly at ANY initial height `0.24 ~ 0.42 m` and learn inside its own neural weights to compress & explode!).
  2. Stitching two separate jump models (`79e27807` + `jump380_r10`) by speed threshold OR overwriting/faking `obs[0:3]` (`cmd_vx`, `cmd_wz`) during flight when the human releases `W` or steers `A/D`! Instead, you MUST train **ONE single unified RL jump policy `E_jump_unified`** on `host72 GPU 0` whose training rollouts explicitly randomize initial stance height `[0.24, 0.42] m`, initial speed `[0.0, 2.8] m/s`, AND mid-jump operator command drops (`cmd_vx -> 0` on release `W`, `cmd_wz` steering, variable `Space` hold duration) + Full-DR so **the RL policy itself** stays level (`|pitch| <= 12°`) and never flips!
  3. Having the external navigation bridge hijack/clamp the human operator's `cmd_vx`, `cmd_wz`, or `target_h` when approaching stairs! In `WASD` mode, operator commands go straight through; in Auto-Nav mode, the global A*/Theta* planner outputs standard `(vx_cmd, wz_cmd)`. The external bridge's ONLY job for stairs is computing the clean objective 4D local terrain vector `g_step = [d1, h1, d2, h2]` from the 2.5D LiDAR map and routing to `E_stair_nav4d` when a positive step is within `d1 <= 1.10 m` (with forward intent) until climbed. **`E_stair_nav4d` ITSELF** must learn on `host72 GPU 0` across wide `cmd_vx ∈ [0.4, 2.4] m/s`, `h_init ∈ [0.25, 0.42] m`, and `yaw ∈ [-30°, +30°]` to self-raise its body so the front `guide_wheel` clears `200~250 mm`, self-regulate climb momentum, tuck main wheels without `-64.8°` backflip, and climb single & continuous double stairs!

---

## 1. Scope, Safety & Hardware Rules
- **Dedicated Workspace**: `d:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_LIDAR_NAV_3V3_REPAIR_20261122`.
- **Protected Assets (`6,586` files)**: Read-only (`audit_assets.py --verify` must exit `0`). Never modify donor directories or `MOD4v3_HW300N60_R3` `400Hz` physics / `100Hz` leg PD / `400Hz` wheel / `[-6,6]` motor contract.
- **Remote GPU**: **ONLY `host72 GPU 0`** (`UUID = GPU-16828f91-2b45-b646-8dc0-9481138e2842`), `/home/lc01/Zonglin Li/zonglin2/run-python.sh`, mandatory `600`-step `0`-update `PROBE.json` + `SAFE_CLOSED.json` precheck before each GPU training job, wall-clock guard + clean GPU release after each job.

---

## 2. Phase-by-Phase Execution Plan

### Phase 1 — `RMUL2027_3V3_V1.0.0.stp` Stiff Arena & 2.5D LiDAR Elevation Maps (Keep & Finish Verification)
- Your `build_rmul2027_3v3.py` already produced `maps/wasd/rmul2027_3v3_stiff_v1.mjb` (`0.15 s` load, `130` boxes + `484` convex prisms, `det = +1`, discovering both `200 mm` and `250 mm` stairs plus `400 mm` tiers!).
- Finish the pure-numpy / triangle-raster `2 cm` height verification (`evidence/RMUL2027_3V3_GEOMETRY_AUDIT.json`, no `rtree` dependency needed) and also ensure `maps/wasd/rmuc2027_stiff_v1.mjb` (`solref="0.0012 1" friction="0.9 0.005 0.0001"`) is built/staged.
- Generate exact `2 cm` 2.5D elevation `.npz` maps + Theta*/A* global path planners (`lidar_nav_planner.py`) + objective 50 Hz `g_step = [d1, h1, d2, h2]` local terrain extractor (`terrain_sensor_4d.py`) for `RMUL 2027 3v3`, `RMUC 2027 5v5`, `suite_proving`, `step_20`, `oblique_20`, `oblique_20_negative`, `curb_11`, `rm27_west_400`, `rm27_east_400`.

### Phase 2 — GPU RL Training #1 on `host72 GPU 0`: Single Unified All-Regime Jump Policy `E_jump_unified`
- **Architecture**: Single neural policy `obs(35) + history(420) -> 6D` (warm-started from `jump380_r10` `4c35c0e1` or `79e27807`, keeping frozen `E0` base if residual, with Asymmetric Critic).
- **Training Distribution (`2048` envs on `host72 GPU 0`) — Fix the Root Distribution!**:
  1. **Initial stance height**: uniformly sample `h_init ∈ [0.24, 0.42] m` before jump trigger (including `0.39 m` / `0.42 m` tall stance histories!), so the policy ITSELF learns to rapidly flex/load its legs from tall stance and explode upward (`rim >= 28~48 cm`, ZERO `0.0 cm` dead-locks)!
  2. **Continuous speed range**: sample initial forward speed continuously across **`[0.0, 2.8] m/s`** (`25%` stationary `[0.0, 0.25] m/s`, `35%` low/mid `[0.25, 1.35] m/s`, `40%` high-speed `[1.35, 2.85] m/s`), on both flat ground and `160 ~ 380 mm` platforms/steps!
  3. **Realistic Human Key Perturbations in Flight (Crucial!)**:
     - Randomize `obs[30]` (`jump` key hold duration) across **`[5, 45]` ticks** (`0.10 s` quick tap up to `0.90 s` hold)!
     - With `50%` probability right after jump trigger or liftoff, **drop `obs[0]` (`cmd_vx`) to `0.0`** (human releasing `W`!), or perturb `obs[0]` & `obs[2]` (`cmd_wz ∈ [-1.2, 1.2]`), while rewarding **physical ballistic momentum conservation in flight + level chassis (`|pitch| <= 10°`, heavy penalty for `|pitch| > 15°` or mid-air wheel braking impulse) + compliant skyhook landing before tracking the post-landing `cmd_vx`**!
  4. **Full Physics/Sensor DR** (`0% -> 50% -> 100%` progressive DR).
- **Raw Unpatched Verification (`eval_jump_all_regimes.py`)**:
  - Test `E_jump_unified` directly with **raw human commands** (NO external pre-crouch ticks, NO `vx_cmd` latching, single checkpoint!) across all **56** cases (`h ∈ {0.28, 0.35, 0.39, 0.42}` × `v ∈ {0.0, 0.6, 0.8, 1.2, 1.6, 2.2, 2.8}` × `{tap_Space_5ticks, hold_Space_25ticks}` × `{keep_W, release_W}`): target **`>= 54/56` (`96%+`, ideally `56/56`) liftoff (`rim >= 22 cm`) and `0/56` flips**!

### Phase 3 — GPU RL Training #2 on `host72 GPU 0`: Generalized High-Clearance `E_stair_nav4d`
- **Architecture**: `StairNav4DExpert` (`obs_35 + hist_420 + g_step_4 = 459D -> 6D`), warm-started from `fsm_r10c` (`3a95e86e`) / `softmoe_r9` with zero-init on the 4D terrain columns + Asymmetric Critic (`base_lin_vel` + `1.6m × 0.8m` height scan + contact forces, `12` iter Critic warmup).
- **Training Distribution (`2048` envs on `host72 GPU 0`) — True Speed/Angle/Height/Geometry Generalization!**:
  1. Activate from `d1 <= 1.10 m` with **raw unscripted operator inputs**: `cmd_vx ∈ [0.45, 2.30] m/s`, initial stance `h_init ∈ [0.25, 0.42] m`, entry angle `yaw ∈ [-30°, +30°]`, plus mid-climb speed changes!
  2. **Terrains**:
     - `35%` single stairs (`200 mm` core + `110..255 mm`, covering both standard `200 mm` and `RMUL 2027 3v3`'s `250 mm` steps!);
     - `35%` `RMUC 2027 (5v5)` West (`1.0m` tread) & East (`1.5m` tread) continuous double stairs (both `90°` vertical and `82°~86°` hfield-sloped risers);
     - `30%` `RMUL 2027 (3v3)` single & double highland step profiles.
  3. **Physics-Grounded Rewards (Policy Learns the Mechanics!)**:
     - When `0.15 m < d1 <= 0.90 m`: reward raising chassis/front `guide_wheel` clearance above `h1 + 0.035 m` (`h ≈ 0.40 m`) and self-regulating approach speed so impact doesn't bounce/flip;
     - When `-0.12 m <= d1 <= 0.20 m` (guide wheel over tread): reward rapid main-wheel elevation clearing `h1` + forward progress + **strict anti-backflip pitch penalty (`|pitch| > 24°` quadratic penalty, `|pitch| > 42°` or step regression -> `-25` termination)**;
     - Inject `±4 cm` distance noise, `±2 cm` height noise, `0~2` tick delay on `g_step_4`, and progressive Full-DR!
- **400 Hz CPU MuJoCo Checkpoint Screening**:
  - Screen checkpoints on `step_20` (5 starts + `±25°` oblique + `0.6~2.0 m/s` speeds — **MUST preserve `200 mm` single stair `100%`!**), `RMUL 2027 3v3` (`200 mm` & `250 mm` stairs), and `RMUC 2027 5v5` (`rmuc2027_stiff_v1.mjb` West & East double stairs).

### Phase 4 — External Native MuJoCo 3D Playground & Full Acceptance (`play_lidar_nav_wasd.py` + `Run_MOD4v3_LiDAR_Nav_3v3_5v5_WASD.bat`)
- **UI**: External Native MuJoCo 3D Viewer (`mj.viewer.launch_passive`, `x=582, y=25, 1310×960`, `show_left_ui=False, show_right_ui=False`, `key_callback` routing `Space` to jump instead of viewer pause, 3D path/step markers in `viewer.user_scn`) + Left Dark HUD Console (`560×880+18+25`) with clickable **2D Top-Down LiDAR Nav Mini-Map** (click anywhere for Theta*/A* Auto-Nav across stairs/highlands, or drive raw `WASD` + `Space` with dual-window keyboard focus `GetWindowThreadProcessId(fg) == os.getpid()`!).
- Run `eval_nav4d_full_acceptance.py`, `--smoke`, `--ui-smoke`, render 1x videos, write `FINAL_NAV4D_REPORT.md` & `ACCEPTANCE_SUMMARY.json`, and verify `audit_assets.py --verify` (`exit 0`).
