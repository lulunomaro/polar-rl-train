# COMMANDER-AUTHORED CORE FILES LOCKED — EXECUTION BRIEF FOR `gpt-6.1-sol` (`max`)

Per explicit user instruction (`"奖励函数啥的比较重要的你写吧，你负责完然后交给sol去执行"`), Commander personally wrote, unit-tested, and staged onto `host72` all 8 core model, sensor, reward, PPO, and remote-runner files:

- `unified_policies.py` (`StairNav4DExpert` with `0.0` donor drift & exact `1e-6` bilateral equivariance + `UnifiedJumpActor` seeded from `R10ActorCritic` `4c35c0e1` + correlated symmetric Gaussian exploration + `AsymmetricValue`)
- `terrain_sensor_4d.py` (exact shared PyTorch/NumPy `extract_profile_torch` `2 cm` 98-sample ray extractor: `17°` ramps give `0` false stair detections, `step_20` & `RMUL 2027 3v3` give millimeter-exact `[d1, h1, d2, h2]`)
- `nav4d_isaac_env.py` (84% `200 mm` single/oblique/RMUL-3v3/RMUC-5v5 terrain mix + exact `RM27_SURVEY.npz` bilinear GPU heightfield + exact cumulative `z_step_base + h1` guide-wheel & wheel-lift rewards + self-regulated approach velocity + anti-backflip/roll/regression terminations + exact `E0 <-> E_stair_nav4d` handoff)
- `jump_unified_gpu.py` (`R10` Warp plant, `70%` flat + `30%` `200 mm` solid platform, `[0.24, 0.42] m` stances, `[0.0, 2.8] m/s` speeds, `/12.` smoothed `W`-release/turn perturbations, tall-stance crouch-to-`vz` launch shaping, true airborne `arc[:, 2]` clearance, level pitch/roll & ballistic flight conservation)
- `train_generalized_ppo.py`, `train_nav4d_stair.py`, `train_jump_unified.py`, `remote_nav4d.py`

Their SHA256 hashes are recorded in `COMMANDER_LOCKED_CORE_SHA256.json`, the bundle `inputs_v2.tar.gz` is ALREADY staged on `host72`, and **`stair_probe_r1` is ALREADY running on `host72 GPU 0`**!

## STRICT RULES FOR YOUR EXECUTION
1. **DO NOT MODIFY REWARD FORMULAS, MODEL ARCHITECTURES, OR PPO LOSS LOGIC** in the locked core files! Only if `stair_probe_r1` or `jump_probe_r2` encounters a genuine remote IsaacSim/Warp API compatibility traceback in `ERROR.txt` / `.log`, make the minimal 1–3 line API fix without altering any reward term, re-stage (`remote_nav4d.py stage`), and re-run probe.
2. **NO EXTERNAL STATE-MACHINE BAND-AIDS IN RUNTIME (`nav4d_runtime.py`)**:
   - **Stair routing (`nav4d_runtime.py`)** MUST match `Nav4DIsaacEnv.update_nav_features()` 100%:
     - Compute `g_step, ceiling, _ = terrain_sensor.sample(x, y, yaw)` (or fallback contact synthesis ONLY if `C/V` is manually pressed on an unmapped custom scene without an `.npz` elevation map).
     - `step_ahead = (g_step[1] > 0.06) and (g_step[0] <= 1.00)`
     - `fwd_intent = cmd_vx > 0.12`
     - Maintain `stair_hold_ticks`: set to `32` whenever `step_ahead and fwd_intent`, else `max(0, stair_hold_ticks - 1)`, reset to `0` if `cmd_vx < -0.05`.
     - When `stair_hold_ticks > 0`: feed `cat([obs35, hist420, g_step4])` (`459D`) into `StairNav4DExpert`, **WITHOUT** modifying/clamping `cmd_vx`, `cmd_wz`, or `target_h`! (Only lower `target_h = min(target_h, 0.22)` when `ceiling < 0.36` inside low-clearance dog-hole tunnels on `SymmetricE0`).
   - **Jump routing (`nav4d_runtime.py`)**:
     - Single unified `UnifiedJumpActor` (`455D` -> `6D`) executed with `JumpPlant._compute_motor_torque` (`PPO_TO_NATIVE` order, exact `R10` motor law!) for **ALL** jumps (`0.0 ~ 2.8 m/s`, `0.24 ~ 0.42 m`, no speed-threshold model splitting, no external pre-crouch ticks, no `cmd_vx` latching!).
     - Hold `obs[30] = 1.0` while `Space/J` is physically held (with a minimum pulse of `12` ticks on tap so quick taps register cleanly), and keep `UnifiedJumpActor` active while `recent_key` or `mode >= log(3.0)` until landed & stable (`10` ticks) or `120`-tick timeout, then return cleanly to `SymmetricE0`.

## YOUR STEP-BY-STEP EXECUTION PIPELINE NOW
1. **Monitor `stair_probe_r1` -> Launch `stair_train_r1` (`Priority #1: 200mm 3v3 & Single/Double Stairs`)**:
   - Poll `remote_nav4d.py status --job stair_probe_r1` and `remote_nav4d.py collect --job stair_probe_r1` until `evidence/stair_probe_r1/PROBE.json` (`passed: true`) and `SAFE_CLOSED.json` arrive and GPU 0 returns to idle.
   - Immediately launch `stair_train_r1`:
     `python -B remote_nav4d.py train --job stair_train_r1 --probe stair_probe_r1 --script train_nav4d_stair.py --seconds 1350`
2. **While `stair_train_r1` Trains on `host72 GPU 0` (~22 min), Build Local Runtime, Evaluators & External 3D Playground**:
   - `nav4d_runtime.py`: Clean CPU 400 Hz simulation sharing `SymmetricE0`, `StairNav4DExpert`, `UnifiedJumpActor`, `ElevationMap` + `WaypointFollower` (`lidar_nav_planner.py`), and `TerrainSensor4D`.
   - `eval_stair_nav4d.py` & `eval_jump_all_regimes.py` & `eval_nav4d_full_acceptance.py`:
     - `flat60` (`60/60`), high-speed `0.8~3.0 m/s` cruise (`0%` false stair triggers), `17°` Serial_Leg ramp (`0%` false stair triggers);
     - **`RMUL 2027 3v3` (`rmul2027_3v3_stiff_v1.mjb`)**: test climbing ALL main `200 mm` Central Highland stair approaches (`x = ±3.5, y = ±1.0`) across multiple speeds (`0.6, 1.0, 1.5, 2.0 m/s`) & angles + `250 mm` side stairs + full multi-waypoint Auto-Nav highland patrol!
     - **`step_20` (`200 mm` single stair)**: 5 starts + speeds `0.6~2.0 m/s` + `±25°` `oblique_20` + `curb_11`!
     - **`RMUC 2027 5v5` (`rmuc2027_stiff_v1.mjb`)**: West & East Central Highland double stairs + Auto-Nav highland assault!
     - **56-case Raw Human Jump Matrix**: `h ∈ {0.28, 0.35, 0.39, 0.42}` × `C/assist ∈ {0, 1}` × `v ∈ {0.0, 0.6, 0.8, 1.2, 1.6, 2.2, 2.8}` × `{keep_W, release_W}`!
   - `play_lidar_nav_wasd.py` + `Run_MOD4v3_LiDAR_Nav_3v3_5v5_WASD.bat`:
     - **External Native MuJoCo 3D Viewer (`mj.viewer.launch_passive`, `x=582, y=25, 1310×960`, `show_left_ui=False, show_right_ui=False`)** with `key_callback` routing `Space` (`32`) to robot jump (NEVER viewer pause!) and live 3D green/cyan A* path & step markers via `viewer.user_scn`!
     - **Dual-Window Keyboard Polling**: `GetAsyncKeyState` active whenever `GetWindowThreadProcessId(GetForegroundWindow()) == os.getpid()` (clicking/dragging the 3D MuJoCo window NEVER disables `WASD / Space`!).
     - **Left Dark HUD Console (`560×880+18+25`)** with clickable **2D Top-Down LiDAR Elevation/Nav Mini-Map** (left-click anywhere to dispatch A* Auto-Nav across stairs/highlands, preset mission buttons, `WASD` manual override, `g_step = [d1, h1, d2, h2]` live readout, and `1 · RMUL2027 官方 3v3 全赛场` + `2 · RMUC2027 官方 5v5 全赛场` + `3 · 综合试炼场` at top of dropdown!).
3. **Collect & Screen `stair_train_r1` -> Then Run `jump_probe_r2` & `jump_train_r2` (`1050 s`) on `host72 GPU 0`**:
   - Screen all `stair_train_r1` checkpoints (`model_004m..model_final.pt`) in 400 Hz CPU MuJoCo and pick the empirical best checkpoint preserving `200 mm` single stair `100%` and maximizing `RMUL 3v3` + `RMUC 5v5` stair pass rates!
   - Run `jump_probe_r2` (`--script train_jump_unified.py`) -> verify `PROBE.json` + `SAFE_CLOSED.json` -> run `jump_train_r2` (`--seconds 1050`), screen all jump checkpoints on the 56-case raw jump matrix, wire both best checkpoints into `CANDIDATE_NAV4D.json`, run `--smoke`, `--ui-smoke`, render 1x verification videos (`media/`), write `FINAL_NAV4D_REPORT.md` & `ACCEPTANCE_SUMMARY.json`, and verify `audit_assets.py --verify` (`exit 0`)!
