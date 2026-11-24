# URGENT COMMANDER INTERVENTION: REWARD AUDIT BUGS CAUGHT + USER PRIORITY SHIFT (`200mm` 3v3 STAIR IS #1 RIGID PRIORITY!)

Commander stopped `jump_train_r1` cleanly (`GPU 0` verified back at `13 MiB / 0%`) after live telemetry + code audit confirmed **two critical user warnings** and **deadly reward/mapping bugs** in both `jump_unified_gpu.py` and `nav4d_isaac_env.py`:

1. **Why `jump_train_r1` flatlined at `62 / 16,477` (`0.37%` liftoff!)**:
   - **Channel/Plant Mismatch**: You loaded `MOD4V3_RL_FORWARD_LEAP_STEP_JUMP_20261118/weights/model_rl_forward_leap_best.pt` (`79e27807`) into `Jump380Gpu` (`jump380_r6_gpu.py`), OR mixed `79e27807` (trained on `Mod4v3Mujoco._torque` with `c874` `loco_base` and `obs_mean/obs_scale` buffers!) with `SymmetricE0` + `Jump380Gpu` unwrapped motor law + `380 mm` solid walls! Even worse: `train_generalized_ppo.py` anchored ALL states (`0.008 * (mean - teacher)^2`) to that `0.37%` failing teacher, AND `info[:, 6]` measured raw tire world-Z instead of true airborne clearance `arc[:, 2]`, with zero roll/symmetry penalties and zero tall-stance crouch-to-`vz` launch gradient!
   - **HARD GATE FOR JUMP PROBE**: In `probe` (`0` updates), nominal `h = 0.28 m` episodes MUST already show high liftoff (`> 50%`) — if a warm-started donor gets `0.37%` in `probe`, **STOP AND FIX THE PLANT/OBSERVATION/MOTOR MAPPING MISMATCH** (for example, warm-start `Jump380Gpu` from `jump380_r10` `MOD4V3_MOVING_JUMP_360MM_GPU_RL_20261121/evidence/jump380_r10/ppo/model_009m.pt` which was ACTUALLY trained on `Jump380Gpu`, OR train `79e27807` in IsaacLab `Nav4DIsaacEnv` where `Mod4v3` motor physics matches `79e27807` 100%!) before launching PPO!
   - **User Priority Update**:
     > **"380mm台阶不是刚需，稳定上200mm的3v3台阶目前是刚需，当然两者都要解决"**
     Drop `360/380 mm` walls from `E_jump_unified` training! Train `E_jump_unified` on **`70%` flat ground + `30%` `160 ~ 220 mm` steps/platforms** across `h_init ∈ [0.24, 0.42] m`, `v ∈ [0.0, 2.8] m/s`, `key_hold ∈ [5, 45]` ticks, and mid-air `W`-release / turn perturbations!

2. **FIVE LETHAL REWARD & ARCHITECTURE BUGS CAUGHT IN YOUR `nav4d_isaac_env.py` & `unified_policies.py` (FIX ALL 5 BEFORE RUNNING STAIR PROBE + TRAIN FIRST!)**:
   **Run `E_stair_nav4d` on `host72 GPU 0` FIRST (Priority #1), then `E_jump_unified` SECOND!**

   - **BUG S1 (FATAL DOUBLE-STAIR WORLD-Z BUG in `nav4d_isaac_env.py` lines 174, 184–186)**:
     You wrote:
     `target = self.features()[:, 1]` (which is the **step height delta** `0.20 m` on step 2, NOT world Z `0.40 m`!)
     and then compared **world-Z** `guide_low` (`~0.40..0.64 m` when standing on the `0.20 m` first tread!) against `target + 0.035 = 0.235 m`, and **world-Z** `feet` (`>= 0.20 m` on tread 1) against `target - 0.03 = 0.17 m`!!
     On the second step of every double stair (`RMUC 5v5` & `RMUL 3v3`), that bug **actively rewards collapsing flat onto the 1st tread (`0.235 m` world Z) and gives `lift = 1.0` for free without lifting the wheels at all**!
     **MANDATORY FIX**:
     Compute current base tread elevation `z_floor = torch.where(passed & self.nav_double, self.nav_h1, torch.zeros_like(self.nav_h1))` and absolute upcoming step top `z_top_target = z_floor + target` (`0.20 m` on step 1, `0.40 m` on step 2!).
     - Guide-wheel clearance reward (`0.15 < d1 <= 0.95` & `target > 0.05`): target `guide_low` at `z_top_target + 0.038` (`exp(-((guide_low - (z_top_target + 0.038)) / 0.045)^2)`);
     - Main-wheel tuck/lift reward (`-0.14 <= d1 <= 0.22` & `target > 0.05`): `lift = ((feet.amin(1) - z_floor) / target.clamp_min(0.10)).clamp(0., 1.05)`!

   - **BUG S2 (MISSING ROLL / SIDE-FALL TERMINATION, SMOOTHNESS & SPEED SELF-REGULATION REWARDS)**:
     - In `nav4d_isaac_env.py` line 190, `nav_failed` ONLY checked `pitch > 42° | regression`! A robot rolled `90°` sideways (`|projected_gravity_b[:, 1]| > sin(32°)` or `projected_gravity_b[:, 2] > -0.55`) NEVER terminated and farmed rewards! Add roll `> 32°`, inverted `g_z > -0.55`, and lateral run-off `|pos[:, 1]| > 1.35 m` to `nav_failed`!
     - Add **Action Smoothness & Attitude Stability**: penalize `dt * 0.15 * (actions - prev_actions).square().mean(1)` (stored per control step so legs never 50Hz-chatter!), `dt * 2.5 * roll^2`, `dt * 0.05 * (ang_vel_xy^2)`, and undesired chassis/belly terrain contact force!
     - **Speed Self-Regulation Reward Inside `before` (`0.15 < d1 <= 0.95` & `target > 0.05`)**: When `command[:, 0]` is high (e.g. `1.6 ~ 2.3 m/s`), `9.0 * progress` previously rewarded launching ballistically at `2.3 m/s` into the `200 mm` riser! Instead, cap `progress` step delta cleanly and inside `before` add `+1.2 * exp(-((vx_b - 0.90) / 0.35)^2) - 1.0 * (vx_b - 1.25).clamp_min(0.)^2` so **the neural policy ITSELF learns from `g_step` to decelerate smoothly from `2.3 m/s -> ~0.90 m/s` while raising its chassis to `~0.40 m` before guide-wheel capture**!
     - Also handle `regression` on BOTH step 1 AND step 2: once both wheels clear step 1 (`crossed_1`), dropping below `nav_h1 - 0.08` fails; once both wheels clear step 2 (`crossed_2`), dropping below `nav_h1 + nav_h2 - 0.08` fails!

   - **BUG S3 (`profile(course)` STARVED `200 mm` OBLIQUE & `200 mm` RMUL 3v3 STAIRS!)**:
     In `nav4d_isaac_env.py` line 17, you set `course == 4` (`oblique_20`) to `0.255 m` and `course == 7` to `0.25 m`!
     Remember: in `RMUL2027_3V3_BUILD.json`, the 4 main Central Highland stairs (`faces 592, 594, 642, 643`) are **`0.200 m` (`200 mm`)**, and `oblique_20` is **`0.200 m`**!
     Fix `profile(course)` so **`>= 80%` of envs are `0.200 m` single & double stairs** (`200 mm` straight single, `200 mm` `±25°` oblique single, `200 mm` RMUL 3v3 single & `200+200 mm` double highland with `1.0~2.0 m` treads, `200 mm` RMUC 5v5 West/East crisp & `84°` bevel double stairs), plus `10%` `110 mm` curbs and `10%` `250 mm` steps!

   - **BUG S4 (`StairNav4DExpert` CORRUPTED RAW `obs[:35]` IN `unified_policies.py`!)**:
     Never add `terrain_projection(g_step)` into `obs[:35]` (`obs[7:10]` is unit gravity and `obs[28:35]` is mode one-hot!).
     Instead, feed unmodified `obs[:35]` and `hist[35:455]` into `self.trunk`, and add a normalized nonlinear residual branch into `self.trunk.head`:
     `g_norm = stack([(d1 - 0.4)/0.5, h1/0.20, (d2 - 0.8)/0.5, h2/0.20, (h1 > 0.05).float(), (h2 > 0.05).float()], -1)`
     `terrain_delta = self.terrain_head(cat([obs_latent_or_obs, g_norm], -1))` (with final layer of `terrain_head` zero-initialized so `0`-update output equals the donor to `0.0` error!).
     And in `train_generalized_ppo.py`, do **NOT** anchor `actor` to the frozen blind `teacher` when `d1 > 0.25` (where `teacher` stays low instead of raising stance for the guide wheel!) — either set `anchor = 0` after iteration 20 or mask `anchor` strictly to `|d1| <= 0.20 & command <= 1.2` with decaying weight!

   - **BUG S5 (JUMP REWARD & PLANT ALIGNMENT FOR JOB #2 AFTER STAIR FINISHES)**:
     When you run `E_jump_unified` right after `E_stair_nav4d`:
     1) Ensure 100% identical motor torque law & channel ordering between donor checkpoint, GPU training env, and CPU MuJoCo player (verify in `probe` that `0`-update nominal `h=0.28` episodes achieve high liftoff BEFORE starting PPO!);
     2) Mask `teacher` anchor strictly to nominal `(height <= 0.30) & (perturb_kind == 0)` so tall-stance (`0.35~0.42 m`) and `W`-release (`perturb_kind > 0`) states are FREE to learn crouch-loading & level-pitch flight (`logstd` init around `-2.1` on leg channels so tall stances explore leg flexion!);
     3) Add pre-takeoff crouch-then-upward-`vz` shaping for tall starts (`height > 0.31 m`), reward **true all-geom airborne clearance `arc[:, 2]`** (never raw `info[:, 6]`!), and penalize **both pitch (`> 10°`) and roll (`> 8°`), angular rates, bilateral leg asymmetry (when `turn == 0`), four-bar closure, and mid-air wheel braking**!

## Immediate Action Order Now:
1. Fix `nav4d_isaac_env.py`, `unified_policies.py`, and `train_generalized_ppo.py` (`train_nav4d_stair.py`), run `stair_probe_r1` (`600` steps, `0` updates) on `host72 GPU 0`, verify `PROBE.json` + `SAFE_CLOSED.json`, and launch **`stair_train_r1`** (`1200~1400 s` on `host72 GPU 0`).
2. While `stair_train_r1` runs on `host72 GPU 0`, fix `jump_unified_gpu.py` (plant/channel alignment + no `380 mm` walls + fixed rewards) and build the External Native MuJoCo 3D Playground (`play_lidar_nav_wasd.py` with dual-window `GetAsyncKeyState` focus + `launch_passive` `key_callback` + 2D LiDAR Nav mini-map + `RMUL 2027 3v3` & `RMUC 2027 5v5`).
3. Screen `stair_train_r1` checkpoints in 400 Hz CPU MuJoCo on `RMUL 2027 3v3` `200 mm` stairs, `step_20` (`0°` & `±25°`), and `RMUC 2027 5v5` double stairs; then run `jump_probe_r2` + `jump_train_r2` on `host72 GPU 0`, screen on the 56-case human jump matrix, and run full final acceptance!
