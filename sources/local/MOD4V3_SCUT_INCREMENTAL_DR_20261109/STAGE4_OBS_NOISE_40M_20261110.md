# Stage 4 Observation Noise — 40 Minute Freeze

Date: 2026-11-10  
Status: **frozen engineering candidate**  
Model: `stage4_obs_noise_40m_final`

## Identity

```text
local:
D:\claude2\fangzhen\runs3060\mod4v3_play_20261107\ckpt_flat_obs_noise_stage4_40m_final.pt

SHA256:
74D65E189CB496F0298D08D966329DA902147F440B01C78209FDA1A9C1136CA8

remote:
/mnt/mod4_linux_durable_20261013/mod4v3_scut_target_native_20261107/scut_rough_v0_22cap_1h_20261109_r2/flat_obs_noise_stage4_cont20m_20261110_r1/model_final.pt

git:
weights/stage4_obs_noise_40m_final.pt
```

## Recipe

Stage 4 adds only observation noise on top of Stage 3:

```text
joint friction 50%
+ spring damping 25%
+ external force/torque 25%
+ observation noise 25%
```

Observation noise ranges:

```text
height:             ±0.0025 m
orientation:        ±0.0625 rad
base angular vel:   ±0.0125
joint position:     ±0.00625
joint velocity:     ±0.125
last action:        ±0.25
```

Not enabled:

```text
observation delay
action delay
full SCUT mass/COM/material ranges
```

Reward, 35-D observation contract, 6-D action contract, action order, and 2 kHz physics are unchanged.

## Training

The requested 40 minutes was run as two 20-minute segments because the first segment reached the `iteration 20000` cap:

```text
segment 1: flat_obs_noise_stage4_40m_20261110_r1
segment 2: flat_obs_noise_stage4_cont20m_20261110_r1
total:     2400 s
```

Final training receipt:

```text
iteration:              20285
episodes:               24633
numerical:              7
fall:                   34
timeout:                24560
max_closure:            0.94 mm (diagnostic)
closure_catastrophic:   0
joint_vel_max:          86.4
env_steps_s:            ~23.3k
```

No training crash. The 2 mm closure value is diagnostic only for this Flat-v2-derived profile; only `>1 m` catastrophic closure resets an environment, and that count is zero.

## Single-environment replay

| Case | Result |
|---|---:|
| 2.0 m/s error | 0.0527 |
| 2.2 m/s error | 0.0300 |
| backward 1.5 error | 0.1488 |
| height 0.20 | 0.2041 |
| height 0.40 | 0.4037 |
| yaw 14.14 actual | 13.9256 |
| yaw 14.14 error | 0.2115 |
| jitter vx | 0.8387 |
| jitter wz | 1.2147 |
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
| yaw 14.14, ±2% | **10/10** |
| yaw 14.14, absolute 0.10 rad/s | 5/10 |
| 1 m drop recovery | 6/10 |

Yaw 14.14 statistics:

```text
mean absolute error: 0.1164 rad/s = 0.82%
worst absolute error: 0.2252 rad/s = 1.59%
```

## Acceptance decision

This checkpoint is frozen under the explicit engineering tolerance:

```text
yaw 14.14: relative error <= 2%
and no termination / fall / numerical failure
```

Under that rule, the 40-minute model passes. The stricter `0.10 rad/s` absolute rule is retained as evidence, not silently removed; it would reject the model at 5/10.

The 20-minute Stage 4 checkpoint remains the conservative yaw/drop backup. The 40-minute model is not a claim of full SCUT DR or deployment readiness.

## Parallel 4096-environment smoke test

```text
requested:           4096
steps:               501
final_stable_count:  935 / 4096
episodes:            3
numerical:           0
fall:                0
closure catastrophic: 0
```

`final_stable_count` is an instantaneous snapshot at step 501, not a full-episode pass rate. The 20-minute checkpoint produced `916 / 4096` on the same smoke test.

## Evidence files

```text
evidence/FLAT_OBS_NOISE_STAGE4_40M_STARTUP.json
evidence/FLAT_OBS_NOISE_STAGE4_40M_FINAL.json
evidence/FLAT_OBS_NOISE_STAGE4_40M_SAFE_CLOSED.json
evidence/EVAL_FLAT_OBS_NOISE_STAGE4_40M_FINAL.json
evidence/EVAL_FLAT_OBS_NOISE_STAGE4_40M_MULTIENV.json
evidence/EVAL_FLAT_OBS_NOISE_STAGE4_40M_4096ENV.json
evidence/EVAL_FLAT_OBS_NOISE_STAGE4_20M_MULTIENV.json
evidence/EVAL_FLAT_OBS_NOISE_STAGE4_20M_4096ENV.json
```

The frozen `.pt` is committed by explicit user request. Other experiment weights remain outside Git unless separately frozen.
