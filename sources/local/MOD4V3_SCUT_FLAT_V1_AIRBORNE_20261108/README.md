# MOD4v3 SCUT Flat-v1 airborne snapshot (2026-11-08)

This is the Flat-v1 overlay for the MOD4v3 PPO task:

- flat V30 reward/action/observation base;
- SCUT airborne state machine enabled;
- 30% airborne resets;
- pre-contact wheel directional-speed rewards;
- landing contact-force / downward-velocity / recovery terms;
- 7-D ctrl-mode observation (`normal/stair/slope/recover/jump/height_target/state_time`);
- warm start from the V30 flat final checkpoint.

## Run

- host: `egde@10.24.5.27:4090`
- job: `scut_flat_v1_airborne_3h_20261108_r1`
- 4096 env, seed 66
- 50 Hz policy, 2.5 ms physics, TGS 32/4
- duration: 10800 s (3 h)
- source: `scut_flat_v30_v28warm_2h_20261108_r1/model_final.pt`

## Important boundary

The checkpoint from the 3-hour run is not committed here. `evidence/` contains
only the startup, restore, and first progress receipts. The launch is recorded
for reproducibility; this snapshot does not claim a completed Flat-v1 acceptance.

## Closure-policy correction

SCUT V14 source has no closed-chain 2 mm termination threshold. The Flat-v1
subclass now keeps `max_closure_m` only as a diagnostic and sets
`enforce_closure_reset=False`; closure is not added to `terminated`. The resumed
run `scut_flat_v1_airborne_3h_20261108_r2` starts from `model_periodic.pt` of the
first run for the remaining 7900 seconds.
