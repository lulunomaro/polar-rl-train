# MOD4v3 SCUT V30 flat alignment snapshot (2026-11-08)

This directory is the source snapshot used for the MOD4v3 / SCUT V30 flat
training run on the 210 host (`10.24.5.27:4090`). It is an evidence snapshot,
not a standalone Isaac Lab installation.

## Included files

- `scut_flat_env.py`: 35D actor / 78D critic / 6D action flat environment,
  PhysX TGS 32/4, 2.5 ms physics step, 50 Hz policy.
- `scut_flat_rewards.py`: SCUT flat reward overlay.
- `scut_mild_dr.py`: `white_v3` mild domain randomization.
- `scut_flat_train.py`: PPO runner, complete actor/critic/std/Adam/RNG
  checkpoint handling, periodic saves, and progress receipts.
- `sampling.py`, `model.py`, `flat_terrain.py`: package support used by the run.
- `launch_scut_flat_v28.py`, `launch_scut_flat_v30.py`: launch helpers.
- `watch_and_launch_2h.py`, `launch_watch_2h.py`: watchdog helpers.
- `evidence/`: small JSON receipts copied from the actual run. Checkpoints,
  logs, USD assets, and rollouts are intentionally not committed.

## External dependencies

The source imports the pinned `mod4v1_scut` package, `semantics.py`,
`kinematics.py`, and the Isaac Lab / Isaac Sim runtime. Those are not copied
here because they are supplied by the target environment and its pinned
dependency package. The run plan in `evidence/PLAN_LOCAL.json` records the
actual 210 paths and seed 66.

## Important boundary

This snapshot records the V30 flat alignment and the current training state.
It does not claim the independent 200 mm skill acceptance test, real-robot
deployment, or a final flat-policy graduation. See
`../../../docs/SCUT_V30_FLAT_V3_ALIGNMENT_20261108.md`.


The 2-hour window completed normally; final and safe-close receipts are in vidence/2H_FINAL.json, vidence/2H_SAFE_CLOSED.json, and vidence/2H_FINAL_PERIODIC_FULL.json.
