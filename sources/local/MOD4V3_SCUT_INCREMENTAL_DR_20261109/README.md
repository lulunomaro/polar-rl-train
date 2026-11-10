# MOD4v3 SCUT Incremental DR (2026-11-09)

This snapshot records the partial-DR base and incremental joint-friction, spring-damping, external-wrench, observation-noise, and observation-delay stages.

## Stage order

| Stage | Checkpoint | 2.0 err | 2.2 err | Height | Backward err | Yaw 14.14 err | Jitter vx | Drop |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| partial-full-DR base | `base_partial_75m` | 0.011 | 0.042 | 0.274 | 0.117 | 0.060 | 0.843 | 2/3 |
| partial-full-DR base | `base_partial_101m` | 0.009 | 0.029 | 0.276 | 0.188 | 0.026 | 0.879 | 1/3 |
| joint friction 50% | `stage1_joint_friction_final` | 0.126 | 0.122 | 0.277 | 0.184 | 0.007 | 0.869 | 2/3 |
| joint friction 50% + spring damping 25% | `stage2_spring_damping_cont20m_final` | 0.042 | 0.012 | 0.276 | 0.123 | 0.020 | 0.820 | 2/3 |
| + external force/torque 25% | `stage3_external_dr_20m_final` | 0.012 | 0.071 | 0.278 | 0.247 | 0.012 | 0.827 | 2/3 |
| + external force/torque 25% | `stage3_external_dr_cont10m_r2_final` | 0.082 | 0.052 | 0.281 | 0.178 | 0.040 | 0.855 | 2/3 |
| + observation noise 25% (20m) | `stage4_obs_noise_20m_final` | 0.018 | 0.008 | 0.279 | 0.092 | 0.048 | 0.808 | 2/3 |
| + observation noise 25% (40m, frozen) | `stage4_obs_noise_40m_final` | 0.053 | 0.030 | 0.280 | 0.149 | 0.212 | 0.839 | 2/3 |
| + observation delay 1 step (40m, frozen) | `stage5_obs_delay_40m_final` | 0.027 | 0.063 | 0.278 | 0.154 | 0.127 | 0.845 | 2/3 |

The single-environment yaw column is retained for continuity; the multi-environment result is the acceptance evidence for high-speed yaw.

## Frozen Stage 5 candidate

`stage5_obs_delay_40m_final` is the current frozen engineering candidate.

```text
parent:  stage4_obs_noise_40m_final
local:   D:\claude2\fangzhen\runs3060\mod4v3_play_20261107\ckpt_flat_obs_delay_stage5_40m_final.pt
SHA256:  884CD07B3942DF9C8484B905994E302906C84151F6F9C5D079A417EC98158F24
git:     weights/stage5_obs_delay_40m_final.pt
remote:  /mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/scut_rough_v0_22cap_1h_20261109_r2/flat_obs_delay_stage5_40m_20261110_r1/model_final.pt
```

The 40-minute run saved checkpoints every 5 minutes: `005m` through `035m`, plus `model_final.pt`.

10-environment fixed-command acceptance:

```text
2.0 / 2.2 / backward / heights / jitter: 10/10
yaw 14.14: 10/10 at ±1%
yaw 14.14: 10/10 at ±2%
1m drop: 7/10
```

The 4096-env smoke result is `782 / 4096` instantaneous stable at step 501, with zero numerical/fall/catastrophic-closure resets. This is smoke evidence only; 4096 tests are not routine.

## Previous frozen Stage 4 candidate

`stage4_obs_noise_40m_final` remains the parent and the previous frozen engineering candidate:

```text
SHA256: 74D65E189CB496F0298D08D966329DA902147F440B01C78209FDA1A9C1136CA8
git:    weights/stage4_obs_noise_40m_final.pt
```

Its multi-environment yaw 14.14 result was 10/10 at ±2%; the strict 0.10 rad/s absolute result was 5/10. The explicit engineering tolerance remains ±2%.

## Evidence

- `STAGE4_OBS_NOISE_40M_20261110.md` — Stage 4 freeze report.
- `STAGE5_OBS_DELAY_40M_20261110.md` — Stage 5 freeze report.
- `evidence/EVAL_FLAT_OBS_DELAY_STAGE5_40M_FINAL.json` — single-environment replay.
- `evidence/EVAL_FLAT_OBS_DELAY_STAGE5_40M_MULTIENV.json` — 10 fixed-command environments.
- `evidence/EVAL_FLAT_OBS_DELAY_STAGE5_40M_4096ENV.json` — 4096 parallel smoke test.
- `evidence/FLAT_OBS_DELAY_STAGE5_STARTUP.json` / `FINAL.json` — training receipts.
- `evidence/FLAT_OBS_DELAY_STAGE5_PERIODIC_*.json` — 5-minute checkpoint receipts.

## Not yet added

Action delay and full SCUT mass/COM/material ranges remain off. The next incremental stage is action delay 1 control step; it must be treated as high-risk because prior probes showed joint-velocity spikes.

## Weights and Git

Frozen Stage 5 binary:

```text
weights/stage5_obs_delay_40m_final.pt
SHA256: 884CD07B3942DF9C8484B905994E302906C84151F6F9C5D079A417EC98158F24
```

Frozen Stage 4 parent:

```text
weights/stage4_obs_noise_40m_final.pt
SHA256: 74D65E189CB496F0298D08D966329DA902147F440B01C78209FDA1A9C1136CA8
```

Other `.pt` binaries remain indexed by SHA/path and are not committed unless separately frozen. `MODEL_INDEX.json` records frozen/selected model SHA256, local path, remote path, and eval summary.
