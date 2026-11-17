# End-to-End RL High-Jump Expert Distillation & PPO Plan (`MOD4v3 / c874`)

## 1. Executive Purpose

The `HighJumpController` in [high_jump_controller.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/high_jump_controller.py) already executes **standing high jumps, moving high jumps (`-0.5` to `+1.2+ m/s`), hold-charge jumps, and continuous 3x moving multi-jumps** directly on the unmodified `MOD4v3 / HW300N60_R3` plant (`MJCF SHA256 = 77904c00...`) layered over the adopted low-pitch base policy `c874` (`SHA256 = c874a1af...`).

Crucially, **every single action emitted by `HighJumpController` passes through the 100% unmodified `Mod4v3Mujoco._torque` actuator law**:
- **Action space**: `6-D` (`[LF, LR, RF, RR, LW, RW]`), strictly clipped to `[-6.0, 6.0]`.
- **PD & Servo rates**: `dt = 0.0025 s` (`400 Hz` physics), `100 Hz` leg PD (`Kp = 60, Kd = 2` with `_continuous_leg_target` bounds `[0.17265, 1.75089] rad`), `400 Hz` wheel velocity servo (`Kv = 0.6`), `50 Hz` policy (`decimation = 8`).
- **Motor & Spring Physics**: Exact DC torque-speed envelope (`40 / 53.333 / 16.755` for legs; `5.7759 / 28.185 / 55.3557` for wheels) and `2000 N/m` closed-loop 4-bar gas springs.

Because there is **zero actuator bypass**, the recorded 50 Hz demonstration dataset [high_jump_demos_c874.npz](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/trajectories/high_jump_demos_c874.npz) contains exact `(obs_35, act_6)` pairs that are **1-to-1 realizable by a pure neural network actor in Isaac Lab** once the remote RTX 4090 finishes its active stair job.

---

## 2. Recorded Demonstration Dataset (`high_jump_demos_c874.npz`)

Generated automatically by [benchmark_and_render.py](file:///d:/claude2/fangzhen/_mod4v2_src_20261106/sources/local/MOD4V3_HIGH_MOVING_JUMP_20261118/benchmark_and_render.py) across **30 nominal 400 Hz episodes (40 full jumps)** covering:
- Standing High Jump (`v_cmd = 0.0 m/s`, 5 perturbed seeds)
- Forward Moving High Jumps (`v_cmd = +0.4, +0.8, +1.2 m/s`, 5 seeds each)
- Reverse Moving High Jump (`v_cmd = -0.5 m/s`, 5 seeds)
- Continuous 3x Moving Multi-Jump (`v_cmd = +0.8 m/s`, 5 seeds)

| Array Key | Shape | Dtype | Description |
| :--- | :--- | :--- | :--- |
| `obs` | `(N, 35)` | `float32` | Standard `c874` 35-D actor observation at 50 Hz |
| `act` | `(N, 6)` | `float32` | Executed `[-6, 6]` 6-D PPO action (`[LF, LR, RF, RR, LW, RW]`) |
| `phase` | `(N,)` | `int32` | Phase label (`0=DRIVE, 1=CROUCH, 2=PUSH, 4=FLIGHT_TUCK, 5=LANDING_EXTEND, 6=SKYHOOK_ABSORB`) |
| `root_pos` | `(N, 3)` | `float32` | World base position `(x, y, z)` (m) |
| `root_quat` | `(N, 4)` | `float32` | World base quaternion `(w, x, y, z)` |
| `qvel` | `(N, 6)` | `float32` | Root linear + body angular velocity |
| `rim_clearance_m` | `(N,)` | `float32` | Bilateral minimum wheel-rim ground clearance (m) |
| `v_cmd` | `(N,)` | `float32` | Commanded forward/reverse velocity (m/s) |

---

## 3. Two Supported Pure-Neural Execution Architectures

### Option A (Recommended for Zero Regression Risk): MoE Route-2 Jump Expert (`E_jump`) + Frozen `E0 = c874`
Following the project's verified MoE Route-2 isolation contract:
1. **`E0` (`c874a1af`) is 100% frozen** (`requires_grad = False`, zero optimizer state, `Δθ_E0 == 0` verified at every checkpoint), guaranteeing **zero regression** on `flat60 (60/60)`, rough/flat emergency braking (`13.56° / 13.37°`), and stairs.
2. **`E_jump` (`ActorMLP` + short 8-frame proprioceptive history or single `jump_latch` scalar in `obs[29]`)** eliminates any hand-crafted phase state machine at deployment:
   - When the user presses `Space`, `obs[29] = 1.0` latches on until bilateral wheel landing + `0.25 s` stabilization resets `obs[29] = 0.0` (returning seamlessly to `E0`).
   - Inside that single latch window, `E_jump` autonomously infers crouch compression, grounded liftoff timing, apex leg tuck, Raibert pre-touchdown foot placement, and skyhook landing damping purely from proprioceptive observations (`joint_pos`, `joint_vel`, `gravity_b`, `root_ang_vel_b`, `a_prev`)!

### Option B: Unified Single-MLP 35-D Policy via `ctrl_mode_obs` (`obs[28:35]`)
If a single `ActorMLP(35 -> 256 -> 128 -> 64 -> 6)` checkpoint is desired:
- `c874` already reserves `obs[28:35]` (`ctrl_mode_obs`, 7 dims) where normal driving sets `obs[28:35] = [1, 0, 0, 0, 0, 0, 0]`.
- Set `obs[29] = 1.0` (`jump_trigger`) and `obs[34] = ramp_clock` (`0 -> 1` over `1.2 s`), warm-starting from `c874` weights with a persistent on-policy anchor `L_keep = 8.0 * ||π(s_drive) - π_c874(s_drive)||^2` on `50%` driving environments so `c874` locomotion remains intact.

---

## 4. Three-Stage Training Curriculum on Remote RTX 4090 (`2048` Envs, `40 min` Budget)

### Stage 0: Warm-Start Behavioral Cloning Pre-Alignment (`2 min` / `300` Adam steps, `0` Physics Rollout Cost)
- Stratify `high_jump_demos_c874.npz` across four balanced buckets so short high-power phases are never drowned out by cruise frames:
  - `25%` `CROUCH` (`phase == 1`)
  - `25%` `PUSH` (`phase == 2`)
  - `30%` `FLIGHT_TUCK + LANDING_EXTEND` (`phase in {4, 5}`)
  - `20%` `SKYHOOK_ABSORB` (`phase == 6`)
- Minimize `MSE(π_jump(obs), act_demo)` to `< 0.015` before enabling PPO gradients, ensuring initial rollouts already jump `> 32 cm` with `0` guide/chassis impacts!

### Stage 1: `0-DR` Nominal PPO + Stratified Success Replay (`0 -> 15 min`)
- **Environments**: `2048` parallel `HW300N60_R3` environments (`v_cmd ~ Uniform[-0.6, +1.4] m/s`, `wz_cmd ~ Uniform[-0.6, +0.6] rad/s`, single & 3x multi-jump triggers).
- **Jump Reward Shaping** (active only while `jump_latch == 1`):
  - **Crouch Preload**: `+0.4 * exp(-((z_root - 0.190) / 0.025)^2)` during the first `0.45 s` with bilateral wheel contact `> 20 N` and `guide/chassis < 1 N`.
  - **Peak Bilateral Wheel-Rim Clearance**: `+12.0 * max(0, rim_peak_episode - 0.24)` + dense airborne clearance `+1.5 * dt * clamp(rim_z / 0.35, 0, 1.2)` when `q_delta < 0.45` near apex (explicitly rewards true leg tuck + high COM rise).
  - **Airborne Attitude Flatness**: `+0.8 * dt * exp(-(pitch / 0.10)^2 - (roll / 0.06)^2) - 0.08 * dt * (ω_x^2 + ω_y^2)`.
  - **Touchdown Skyhook Smoothness & Velocity Retention**: `-2.0 * dt * sin(pitch)^2` during `1.0 s` post-landing + `+1.0 * dt * exp(-(v_x - v_cmd)^2 / 0.25)` + `-5.0` penalty for any `guide_wheel` or `chassis` contact `> 1 N`.
- **Stratified Replay Regularizer**: Keep `lambda_bc = 0.5` on verified `>= 33 cm`, `< 8°` airborne pitch, `0 N` guide-contact trajectories so PPO never forgets the deep-crouch preload or collapses into a shallow hop.

### Stage 2: Progressive Full-SCUT Domain Randomization Graduation (`15 -> 40 min`)
- Promote `10% -> 25% -> 50% -> 100%` of envs to full SCUT DR (payload mass, COM shift, friction `[0.5, 1.25]`, motor strength `±10%`, PD delay, uneven rough tiles) once nominal success rate (`rim_peak >= 32 cm`, `air_pitch <= 10°`, `air_roll <= 5°`, `0 N` forbidden contact, `0.5 s` stable recovery) exceeds `80%` over a 256-episode window.

---

## 5. Pre-Launch Safety Checklist (For Next Authorized Remote Window)

1. Confirm remote GPU (`egde`) has **zero active training owners** (`nvidia-smi` clean after `01:56`).
2. Run a mandatory **600-step `0-PPO` precheck** verifying:
   - `Δθ_E0 == 0.0` (exact bitwise match to `c874a1af`),
   - `closure_error < 2.0 mm` across all 2048 envs,
   - Warm-started `E_jump` achieves `> 70%` clean `> 30 cm` jumps before step 1 of PPO.
3. Archive checkpoints every `5 min` and run both the **6-condition Moving Jump Benchmark** and the **frozen `E0` full regression** (`flat60`, stairs, oblique, emergency stop) before any candidate adoption.
