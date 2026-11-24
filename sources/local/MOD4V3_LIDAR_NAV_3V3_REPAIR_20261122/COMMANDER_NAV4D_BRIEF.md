# COMMANDER DISPATCH BRIEF FOR `gpt-6.1-sol` (`max`)

You are executing inside the dedicated workspace:
`d:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_LIDAR_NAV_3V3_REPAIR_20261122`

First, read `EXTERNAL_NAV_MASTER_PLAN.md` in this directory in full. It is your binding engineering specification.

## 1. Strict Boundaries & Environment
- **Python**: Always use `d:\claude2\fangzhen\.venv\Scripts\python.exe` locally (`OCP`, `cadquery`, `trimesh`, `vtk`, `mujoco`, `torch`, `paramiko` are all pre-installed).
- **Read-Only Protection**:
  - Do NOT edit any file outside `d:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_LIDAR_NAV_3V3_REPAIR_20261122`.
  - Treat `MOD4V3_MANUAL_FSM_STAIR_UNIFIED_20261122`, `MOD4V3_RL_FORWARD_LEAP_STEP_JUMP_20261118`, `MOD4V3_RL_SINGLE200_FULLDR_5OF5_20261118`, `MOD4V3_MOVING_JUMP_360MM_GPU_RL_20261121`, `MOD4V3_E0_FLAT_ROUGH_REPAIR_20261120`, and `MOD4V3_UNIFIED_SILKY_LOCO_GPU_RL_20261121` strictly as **read-only donors**.
  - Verify `d:\claude2\fangzhen\_mod4v2_src_20261106\sources\local\MOD4V3_MANUAL_FSM_STAIR_UNIFIED_20261122\audit_assets.py --verify` passes (`exit 0`) both before GPU training and at final sign-off.
  - Never alter the `MOD4v3_HW300N60_R3` physical plant contract (`dt=0.0025s` 400Hz physics, 100Hz leg PD every 4 substeps, 400Hz wheel servo, 50Hz policy, `[-6,6]` motor clip, `2000 N/m` gas spring, unmodified wheel/guide-wheel geometry, inertias, gains, and effort limits).
- **Remote GPU Discipline (`host72 GPU 0` ONLY)**:
  - Host: `host72` (via `remote_e0.connect('host72')`, see `MOD4V3_MANUAL_FSM_STAIR_UNIFIED_20261122\remote_manual_fsm.py`).
  - GPU 0 UUID: `GPU-16828f91-2b45-b646-8dc0-9481138e2842` ONLY. Never touch GPU 1 or `edge4090`.
  - Remote task root: `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_LIDAR_NAV_3V3_REPAIR_20261122`.
  - Remote Python: `/home/lc01/Zonglin Li/zonglin2/run-python.sh`.
  - **Mandatory Precheck**: Run a `600`-step, `2048`-env, `0`-optimizer-update `probe` job first (`PROBE.json` + `SAFE_CLOSED.json` + GPU memory released) before launching any PPO training job (`budget <= 1500 s` per training round with hard wall-clock guard and `SAFE_CLOSED.json`).

## 2. Mandatory Execution Sequence (Do NOT Skip Steps!)

### Phase 1 — Official `RMUL2027_3V3_V1.0.0.stp` Arena + 2.5D LiDAR Elevation Maps (`build_rmul2027_3v3.py`)
1. Input CAD is already staged at `assets/cad/RMUL2027_3V3_V1.0.0.stp` (`1,989,786` bytes, SHA256 `7d47c1b6a6a0253a732e46cb122bb84410b11d5134bcb5658104299db4a48ca4`).
2. Apply the exact right-handed rigid transform (`det = +1`):
   `x_mj = 0.001 * x_cad`, `y_mj = 0.001 * z_cad`, `z_mj = -0.001 * y_cad`.
   Verify: footprint `12.60 m × 8.60 m`, main floor at `z_mj = 0.000 m`, first highland/step tier at `z_mj = +0.200 m`, second highland/perimeter wall at `z_mj = +0.400 m`.
3. **CRITICAL MUJOCO RULE**: MuJoCo `<geom type="mesh">` computes the CONVEX HULL! NEVER use the whole non-convex arena mesh as a single collision geom. Instead:
   - Export clean visual OBJ/STL meshes (`contype="0" conaffinity="0"`) grouped by elevation/feature with clear readable colors so stairs, highlands, ramps, and walls look sharp in the 3D viewer.
   - Build exact non-overlapping analytic `box` and convex-wedge/convex-part collision geoms with `solref="0.0012 1" friction="0.9 0.005 0.0001" contype="1" conaffinity="3"`.
   - Compile fast binary `maps/wasd/rmul2027_3v3_stiff_v1.mjb` (`< 0.4 s` load) AND ensure `RMUC 2027 5v5` also uses `solref="0.0012 1" friction="0.9 0.005 0.0001"` (`maps/wasd/rmuc2027_stiff_v1.mjb`).
   - Audit `mj_ray` vertical height vs exact `trimesh`/CAD vertical raycast on a `2 cm` grid across `RMUL 2027 3v3` and write `evidence/RMUL2027_3V3_GEOMETRY_AUDIT.json` (median error `< 1 mm`, 99th-percentile on playable surfaces `< 3 mm`, plus list all stair risers, ramp slopes, and highland spawn points!).

### Phase 2 — Fix ALL Jump Bugs ("雷霆的跳不起来" & "边跑边跳翻车") (`jump_stabilizer.py` + `eval_jump_all_regimes.py`)
1. Inspect how `MOD4V3_RL_FORWARD_LEAP_STEP_JUMP_20261118` loads and runs `weights/model_rl_forward_leap_best.pt` (`79e27807`, level-chassis `<= 8.70°` max air pitch forward leap + `16/20/24 cm` step jump) and how `MOD4V3_MOVING_JUMP_360MM_GPU_RL_20261121` runs `jump380_r10` (`4c35c0e1`).
2. Fix **both** failure modes completely:
   - **Tall-Stance / C-ON `0.0 cm` Dead-Lock Fix**: Whenever jump is requested while `rel_z > 0.312 m` or `effective_h > 0.31 m` (e.g. `h = 0.35, 0.39, 0.42 m` or `C` ON), automatically run a crisp `0.28 m` pre-crouch preparation phase (`6~12` ticks on `SymmetricE0` with `h_cmd = 0.28 m` while maintaining forward momentum) until the legs enter the `<= 0.312 m` launch posture and history aligns, then immediately fire the jump expert!
   - **Release-`W` Mid-Air Braking Flip Fix**: Gate jump expert strictly on **true physical forward velocity `vx_real`** (NEVER commanded `obs[0]`!):
     - `vx_real < 1.25 m/s`: route to level-chassis `79e27807` (`E_leap`, air pitch `<= 10°`) with latched forward command during leap;
     - `vx_real >= 1.25 m/s`: route to `jump380_r10` (`4c35c0e1`) with **Takeoff Momentum Latch** (`vx_cmd = clip(vx_takeoff, 1.35, 2.80)`, `wz_cmd = 0.0`, `h_cmd = 0.28~0.30 m` locked from takeoff through flight and first `10` landing-stabilization ticks before smoothly blending back to live operator `cmd_vx`).
3. Run `eval_jump_all_regimes.py` across ALL **56** human combinations:
   `init_h ∈ {0.28, 0.35, 0.39, 0.42}` × `C ∈ {False, True}` × `v ∈ {0.0, 0.6, 0.8, 1.2, 1.6, 2.2, 2.8}` × `{keep_W, release_W_on_Space}` on flat/arena road -> MUST achieve **`56 / 56` liftoff (`rim >= 22 cm`) and `0 / 56` flips**! Save `evidence/JUMP_56_AUDIT.json`.

### Phase 3 — External LiDAR 2.5D Navigation + 50 Hz Terrain-Aware Bridge (`lidar_nav_planner.py` + `terrain_nav_bridge.py`)
1. Generate `2 cm` 2.5D elevation & semantic traversability maps (`.npz`) for `RMUL 2027 3v3`, `RMUC 2027 5v5`, `suite_proving`, `step_20`, `oblique_20`, `oblique_20_negative`, `curb_11`, `rm27_west_400`, `rm27_east_400`.
   - Automatically detect **climbable stair risers (`0.08 m <= dh <= 0.23 m`)** vs **impassable sheer walls (`dh >= 0.26 m`)** vs **ramps** vs **low-clearance tunnels (`ceiling < 0.36 m`)**.
   - Implement Theta* / smoothed A* global path planning + stair-corridor normal alignment waypoints (so when planning from arena floor to a `+0.20 m` or `+0.40 m` highland, the path approaches the climbable stair corridor straight along its outward normal, NEVER trying to climb a `400 mm` sheer wall!).
2. Implement the **50 Hz Terrain-Aware Locomotion Bridge** (`terrain_nav_bridge.py`) shared by BOTH Auto-Nav AND Human `WASD` (when Terrain Assist is enabled, default ON):
   - Sample horizontal yaw-aligned lookahead profile `s ∈ [-0.25, +1.40] m` on the 2.5D elevation map (completely pitch-invariant!) and extract `g_step = [d1, h1, d2, h2]`.
   - **Flat / Ramp (`no positive riser within 1.05 m`)**: lock 100% pure `SymmetricE0` (`0` premature squat; auto-crouch `0.22 m` in tunnels).
   - **Stair Pre-Align (`0.34 m < d1 <= 1.05 m` with forward intent toward stair)**: stay on `SymmetricE0`, **automatically raise `h_cmd -> 0.400 m`** (guaranteeing `guide_wheel_04` sits `> 0.22 m` above ground to clear `200 mm`!), smoothly regulate `cmd_vx` into `[0.80, 1.05] m/s`, and gently assist `cmd_wz` toward the local stair normal (`|yaw_err| < 45°`).
   - **Active Climb (`d1 <= 0.34 m` until rear wheels clear the last riser by `>= 0.22 m` and body pitch settles `< 8°`)**: route to `E_stair_nav4d(obs_35, hist_420, g_step_4)`. Include contact-triggered fallback synthesis of `g_step_4` when `C/V` is used on unmapped custom scenes.

### Phase 4 — Train `E_stair_nav4d` on `host72 GPU 0` (`nav4d_isaac_env.py` + `train_nav4d_stair.py` + `remote_nav4d.py`)
1. Build `StairNav4DExpert` (`459D -> 6D`), warm-starting the `455D` trunk from the best validated stair donor (`MOD4V3_MANUAL_FSM_STAIR_UNIFIED_20261122/weights/E_stair_stage2_gate_final_fsm_r10c_model_015m.pt` and/or `a1acd1a8` / `softmoe_r9`) with zero-initialized weights on the `4D` `g_step` projection so `0`-update behavior matches the donor cleanly.
2. Use an **Asymmetric Critic** receiving `base_lin_vel` + local `1.6m × 0.8m` terrain height-scan (`Sirina` `rc_mjlab` style) + `12` iterations of Critic-only warm-up before Actor updates.
3. Train across `2048` envs mixing:
   - `35%` `200 mm` single stairs (`110..220 mm`, `0°` & `±25°` oblique) — **MUST preserve `100%` `200 mm` single-stair pass rate**;
   - `35%` `RMUC 2027 (5v5)` West (`1.0m` tread) & East (`1.5m` tread) double stairs (including both `90°` crisp and `84°` hfield-bevelled risers);
   - `30%` `RMUL 2027 (3v3)` Central Highland single & double stairs matching `RMUL2027_3V3_V1.0.0.stp`.
4. Enforce **High-Stance Guide-Wheel Capture + Anti-Backflip Rewards**:
   - Approach at `h ≈ 0.40 m` before `d1 = 0.08 m`, rapid main-wheel tuck as `d1` crosses `[0.22, -0.10] m` while front guide wheel rides the tread, steady forward progress across both risers, smooth deck settle;
   - Strong penalty for nose-up pitch `|pitch| > 24°`, immediate `-25` termination on backflip (`|pitch| > 42°`) or step regression (dropping back down a climbed step);
   - Inject `±3 cm` distance jitter, `±1.5 cm` height jitter, and `0~2` tick delay into `g_step_4` + progressive DR (`0% -> 25% -> 50% -> 100%`).
5. Run `600`-step `0`-update `probe` first -> verify `PROBE.json` + `SAFE_CLOSED.json` -> launch guarded PPO (`<= 1400 s`), saving checkpoints every 5 minutes, and evaluate every checkpoint in **400 Hz CPU MuJoCo** across `step_20`, `RMUL 2027 3v3`, and `RMUC 2027 5v5` (`rmuc2027_stiff_v1.mjb`) to select the true best checkpoint (`CANDIDATE.json`).

### Phase 5 — External Native MuJoCo 3D Nav Playground & Full Acceptance (`play_lidar_nav_wasd.py` + `Run_MOD4v3_LiDAR_Nav_3v3_5v5_WASD.bat`)
1. **NON-NEGOTIABLE UI REQUIREMENT**: Use **ONLY** the External Native MuJoCo 3D OpenGL Viewer (`mj.viewer.launch_passive`, positioned at `x=582, y=25, 1310×960`, `show_left_ui=False, show_right_ui=False`, with `key_callback` routing `Space` to robot jump instead of viewer pause, and drawing live 3D green/cyan A* path waypoints & step markers via `viewer.user_scn`!) paired with the Left Dark HUD Console (`560×880+18+25`). **NEVER** use an embedded `ImageTk` rendered-frame viewer!
2. **Dual-Window Keyboard Polling Fix**: `GetAsyncKeyState` MUST remain active whenever `GetWindowThreadProcessId(GetForegroundWindow()) == os.getpid()` (so clicking/rotating the external 3D MuJoCo window NEVER breaks `WASD / Space / C`!). Also gently clean up any stale orphan `play_manual_fsm_wasd.py` processes on startup only if requested via `--close-stale` (do not kill unrelated python processes).
3. Include an interactive **2D Top-Down Elevation & LiDAR Nav Canvas** inside the Left HUD Console:
   - Shows robot pose `(x, y, yaw)`, elevation heatmap, planned A* path, and upcoming `g_step = [d1, h1, d2, h2]` readout;
   - Left-click anywhere on the 2D mini-map (or click preset mission buttons like `"自动冲占中央高地"`, `"全图巡航跑图"`) to launch automatic LiDAR Navigation; pressing `WASD` seamlessly overrides/drives manually with `50 Hz` Terrain Assist (`T` toggles Terrain Assist ON/OFF).
   - Put **`1 · RMUL2027 官方 3v3 全赛场 (秒开·含高地自动导航)`**, **`2 · RMUC2027 官方 5v5 全赛场 (MJB秒载·东西高地导航)`**, and **`3 · 综合试炼场 · 五车道`** right at the top of `PLAYER_SUITES`!
4. Run full acceptance (`eval_nav4d_full_acceptance.py`), `--smoke`, `--ui-smoke`, render 1x verification videos (`media/`), write `FINAL_NAV4D_REPORT.md` & `ACCEPTANCE_SUMMARY.json`, and verify `audit_assets.py --verify` (`exit 0`).
