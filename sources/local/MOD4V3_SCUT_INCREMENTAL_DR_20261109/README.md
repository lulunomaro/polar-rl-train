# MOD4v3 SCUT Incremental DR (2026-11-09)

This snapshot records the partial-DR base and incremental joint-friction, spring-damping, external-wrench, and observation-noise stages.

## Stage order

| Stage | Checkpoint | 2.0 err | 2.2 err | Height | Backward err | Yaw 14.14 err | Jitter vx | Drop |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| partial-full-DR base | `base_partial_75m` | 0.011 | 0.042 | 0.274 | 0.117 | 0.060 | 0.843 | 2/3 |
| partial-full-DR base | `base_partial_101m` | 0.009 | 0.029 | 0.276 | 0.188 | 0.026 | 0.879 | 1/3 |
| joint friction 50% | `stage1_joint_friction_final` | 0.126 | 0.122 | 0.277 | 0.184 | 0.007 | 0.869 | 2/3 |
| joint friction 50% + spring damping 25% | `stage2_spring_damping_cont20m_final` | 0.042 | 0.012 | 0.276 | 0.123 | 0.020 | 0.820 | 2/3 |
| joint friction 50% + spring damping 25% | `stage2_spring_damping_cont30m_final` | 0.172 | 0.203 | 0.275 | 0.157 | 0.013 | 0.854 | 2/3 |
| + external force/torque 25% | `stage3_external_dr_20m_final` | 0.012 | 0.071 | 0.278 | 0.247 | 0.012 | 0.827 | 2/3 |
| + external force/torque 25% | `stage3_external_dr_cont10m_r2_final` | 0.082 | 0.052 | 0.281 | 0.178 | 0.040 | 0.855 | 2/3 |
| + observation noise 25% (20m) | `stage4_obs_noise_20m_final` | 0.018 | 0.008 | 0.279 | 0.092 | 0.048 | 0.808 | 2/3 |
| + observation noise 25% (40m, frozen) | `stage4_obs_noise_40m_final` | 0.053 | 0.030 | 0.280 | 0.149 | 0.212 | 0.839 | 2/3 |

The single-environment yaw column is intentionally retained; the multi-environment result is the acceptance evidence for high-speed yaw.

## Frozen Stage 4 candidate

`stage4_obs_noise_40m_final` is frozen as a Stage 4 engineering candidate.

```text
local:  D:\claude2\fangzhen\runs3060\mod4v3_play_20261107\ckpt_flat_obs_noise_stage4_40m_final.pt
SHA256: 74D65E189CB496F0298D08D966329DA902147F440B01C78209FDA1A9C1136CA8
remote: /mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/scut_rough_v0_22cap_1h_20261109_r2/flat_obs_noise_stage4_cont20m_20261110_r1/model_final.pt
```

Multi-environment fixed-command check, 10 initial environments:

```text
2.0 m/s:       10/10
2.2 m/s:       10/10
backward 1.5:  10/10
height 0.20:   10/10
height 0.40:   10/10
jitter:        10/10
yaw 14.14:     10/10 at ±2% (mean 0.82%, worst 1.59%)
yaw 14.14:      5/10 at strict 0.10 rad/s absolute
```

The explicit Stage 4 acceptance rule is **yaw 14.14 relative error ≤2% with no termination**. The strict absolute 0.10 rad/s result remains in the evidence and is not hidden.

`stage4_obs_noise_20m_final` remains the conservative yaw/drop backup. `stage2_spring_damping_cont20m_final` remains the best nominal all-round checkpoint.

## Parallel-environment check

The target 4096-env evaluation, 501 steps, 10-second snapshot:

```text
40m final: final_stable_count 935 / 4096; episodes 3; numerical 0; fall 0; catastrophic closure 0
20m final: final_stable_count 916 / 4096; episodes 3; numerical 0; fall 0; catastrophic closure 0
```

`final_stable_count` is an instantaneous snapshot at step 501, not a full-episode pass rate.

## Evidence

- `STAGE4_OBS_NOISE_40M_20261110.md` — freeze report and acceptance decision.
- `evidence/EVAL_FLAT_OBS_NOISE_STAGE4_40M_FINAL.json` — single-environment replay.
- `evidence/EVAL_FLAT_OBS_NOISE_STAGE4_40M_MULTIENV.json` — 10 fixed-command environments.
- `evidence/EVAL_FLAT_OBS_NOISE_STAGE4_40M_4096ENV.json` — 4096 parallel environments.
- `evidence/FLAT_OBS_NOISE_STAGE4_40M_STARTUP.json` / `FINAL.json` — training receipts.
- `eval_flatv2_multienv.py` — fixed-command multi-environment evaluator.

## Not yet added

Observation delay, action delay, and full SCUT mass/COM/material ranges remain off. This is an incremental warm-start curriculum, not a strict SCUT full-DR-from-scratch claim.

## Weights and Git

Frozen Stage 4 binary:

```text
weights/stage4_obs_noise_40m_final.pt
SHA256: 74D65E189CB496F0298D08D966329DA902147F440B01C78209FDA1A9C1136CA8
```


The frozen Stage 4 `.pt` is committed at `weights/stage4_obs_noise_40m_final.pt` by explicit user request. Other `.pt` binaries remain indexed by SHA/path and are not committed unless separately frozen. `MODEL_INDEX.json` records frozen/selected model SHA256, local path, remote path, and eval summary; comparison-only checkpoints are marked separately.
