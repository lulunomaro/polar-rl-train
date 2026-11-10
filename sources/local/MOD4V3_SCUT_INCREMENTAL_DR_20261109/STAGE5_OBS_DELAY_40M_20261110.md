# Stage 5 Observation Delay — 40 Minute Freeze

Date: 2026-11-10  
Status: **frozen engineering candidate**  
Model: `stage5_obs_delay_40m_final`

## Identity

```text
parent:
stage4_obs_noise_40m_final

local:
D:\claude2\fangzhen\runs3060\mod4v3_play_20261107\ckpt_flat_obs_delay_stage5_40m_final.pt

SHA256:
884CD07B3942DF9C8484B905994E302906C84151F6F9C5D079A417EC98158F24

git:
weights/stage5_obs_delay_40m_final.pt

remote:
/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/scut_rough_v0_22cap_1h_20261109_r2/flat_obs_delay_stage5_40m_20261110_r1/model_final.pt
```

## Recipe

Stage 5 adds only a one-control-step observation delay on top of Stage 4:

```text
joint friction 50%
+ spring damping 25%
+ external force/torque 25%
+ observation noise 25%
+ observation delay 1 step (20 ms)
```

The delayed signal is the 35-D policy observation only. The critic observation, reward, action order, action clip, and 6-D action interface are unchanged.

## Training

```text
num_envs:             4096
duration:             2400 s
checkpoint interval:  300 s
periodic checkpoints: 005m, 010m, 015m, 020m, 025m, 030m, 035m
final iteration:      20838
episodes:             53445
numerical:            26
fall:                 46
max_closure:          1.13 mm (diagnostic)
catastrophic closure: 0
joint_vel_max:        85.0
mean_reward:          0.0778
```

No training crash. The 2 mm closure value is diagnostic only; only `>1 m` catastrophic closure resets an environment, and that count is zero.

## Single-environment replay

| Case | Result |
|---|---:|
| 2.0 m/s error | 0.0265 |
| 2.2 m/s error | 0.0626 |
| backward 1.5 error | 0.1541 |
| height 0.20 | 0.2050 |
| height 0.40 | 0.4034 |
| yaw 14.14 actual | 14.0101 |
| yaw 14.14 error | 0.1271 |
| jitter vx | 0.8450 |
| jitter wz | 1.2215 |
| common falls | 0 |
| 1 m drop | 2/3 |

## Multi-environment fixed-command replay

Ten initial environments per case:

| Case | Pass count |
|---|---:|
| 2.0 m/s, error <0.15 | 10/10 |
| 2.2 m/s, error <0.15 | 10/10 |
| backward 1.5, error <0.20 | 10/10 |
| height 0.20, error <0.02 | 10/10 |
| height 0.40, error <0.02 | 10/10 |
| jitter vx/wz | 10/10 |
| yaw 14.14, ±1% | **10/10** |
| yaw 14.14, ±2% | **10/10** |
| 1 m drop recovery | 7/10 |

Yaw 14.14 statistics:

```text
mean absolute error: 0.0816 rad/s = 0.58%
worst absolute error: 0.1362 rad/s = 0.96%
```

## 4096-environment smoke

```text
requested:           4096
steps:               501
final_stable_count:  782 / 4096
episodes:            4
numerical:           0
fall:                0
closure catastrophic: 0
```

This is an instantaneous snapshot at step 501, not a full-episode pass rate. It is retained as smoke evidence only; future routine checks use 10 environments, with 64 at most unless explicitly requested.

## Acceptance decision

Stage 5 is frozen under the same explicit high-speed yaw engineering tolerance as Stage 4:

```text
yaw 14.14 relative error <= 2%
and no termination / fall / numerical failure
```

It also passes the stricter ±1% multi-environment check at 10/10.

## Next stage

Stage 6 will add **action delay 1 control step (20 ms)** from this frozen Stage 5 model. This is the high-risk stage; start with a 40-minute run and 5-minute checkpoints, and stop if joint velocity or numerical resets become catastrophic.

## Evidence files

```text
evidence/FLAT_OBS_DELAY_STAGE5_STARTUP.json
evidence/FLAT_OBS_DELAY_STAGE5_FINAL.json
evidence/FLAT_OBS_DELAY_STAGE5_SAFE_CLOSED.json
evidence/FLAT_OBS_DELAY_STAGE5_PERIODIC_005M.json
evidence/FLAT_OBS_DELAY_STAGE5_PERIODIC_010M.json
evidence/FLAT_OBS_DELAY_STAGE5_PERIODIC_015M.json
evidence/FLAT_OBS_DELAY_STAGE5_PERIODIC_020M.json
evidence/FLAT_OBS_DELAY_STAGE5_PERIODIC_025M.json
evidence/FLAT_OBS_DELAY_STAGE5_PERIODIC_030M.json
evidence/FLAT_OBS_DELAY_STAGE5_PERIODIC_035M.json
evidence/FLAT_OBS_DELAY_STAGE5_PERIODIC_FULL.json
evidence/EVAL_FLAT_OBS_DELAY_STAGE5_40M_FINAL.json
evidence/EVAL_FLAT_OBS_DELAY_STAGE5_40M_MULTIENV.json
evidence/EVAL_FLAT_OBS_DELAY_STAGE5_40M_4096ENV.json
```
