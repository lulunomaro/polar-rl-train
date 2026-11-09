# MOD4v3 SCUT Incremental DR (2026-11-09)
This snapshot records the partial-DR base, stage-1 joint-friction run, and stage-2 spring-damping continuations.

## Stage order

| Stage | Checkpoint | 2.0 err | 2.2 err | Height | Backward err | Yaw 14.14 err | Jitter vx | Drop |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| partial-full-DR base | `base_partial_75m` | 0.011 | 0.042 | 0.274 | 0.117 | 0.060 | 0.843 | 2/3 |
| partial-full-DR base | `base_partial_101m` | 0.009 | 0.029 | 0.276 | 0.188 | 0.026 | 0.879 | 1/3 |
| joint friction 50% | `stage1_joint_friction_25m` | 0.176 | 0.229 | 0.277 | 0.234 | 0.030 | 0.843 | 2/3 |
| joint friction 50% | `stage1_joint_friction_final` | 0.126 | 0.122 | 0.277 | 0.184 | 0.007 | 0.869 | 2/3 |
| joint friction 50% + spring damping 25% | `stage2_spring_damping_25m` | 0.149 | 0.171 | 0.274 | 0.200 | 0.065 | 0.835 | 2/3 |
| joint friction 50% + spring damping 25% | `stage2_spring_damping_cont10m_final` | 0.054 | 0.048 | 0.277 | 0.191 | 0.496 | 0.807 | 2/3 |
| joint friction 50% + spring damping 25% | `stage2_spring_damping_cont20m_final` | 0.042 | 0.012 | 0.276 | 0.123 | 0.020 | 0.820 | 2/3 |
| joint friction 50% + spring damping 25% | `stage2_spring_damping_cont30m_final` | 0.172 | 0.203 | 0.275 | 0.157 | 0.013 | 0.854 | 2/3 |

## Current best

`stage2_spring_damping_cont20m_final` remains the best speed-tracking candidate. `cont30m_final` improves jitter and yaw but regresses 2.0/2.2 tracking, so it is retained as evidence, not promoted.

## Weights and Git

Per repository policy, `.pt` binaries are not committed. `MODEL_INDEX.json` records every model SHA256, local path, remote path, and eval summary. Actual local weights remain under `runs3060/mod4v3_play_20261107/`; remote originals remain on the 4090 data disk.

## Not yet added

Observation noise/delay, action delay, external force/torque, and full SCUT mass/COM/material ranges remain off. This is an incremental warm-start curriculum, not a strict SCUT full-DR-from-scratch claim.
