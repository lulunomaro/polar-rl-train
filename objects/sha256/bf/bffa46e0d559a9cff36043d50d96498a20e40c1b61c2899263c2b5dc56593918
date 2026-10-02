# MOD4 1536-env skill recovery checklist

Source checkpoint: `model_2775.pt` (`741e0cdd242e53cea5d187f405b98e2f3931f4d9cd12a3cbc2832b342cb25c9f`).

## Defects fixed before training

- [x] RMUC2026 tunnel rewards use the measured mirrored arena tunnel at `y=+/-5.95 m`, not the procedural-map tunnel at `y=+3.55 m`.
- [x] `jump_in_place` no longer requires the `fly_jump` launch-platform latch before it can receive air reward.
- [x] Flight and landing rewards are confined to their intended route kinds; jump routes are exempt from the unwanted-airborne penalty.
- [x] The gyro curriculum magnitude is written to `RouteCommands.spin_speed`; the former 2..4 rad/s sampler can no longer silently override the displayed curriculum.
- [x] Action second-difference penalty is disabled only during a real jump transient, matching the existing action-rate exemption.
- [x] Action penalty weights and PPO entropy are explicit environment knobs and are recorded in `run_manifest.json`.
- [x] Tunnel low pose uses 0.02 guide-roller friction plus a private USD with 1.2 mm tyre-radius load compensation so the drive tyres retain traction. The radius is baked before PhysX creates tensor views; the source USD remains unchanged.

## Training plan (all phases use 1536 environments)

1. `s1_signal_bootstrap`: nominal plant, short tunnel goal, low jump target, failing-route oversampling.
2. `s2_mild_dr`: narrow domain randomization, longer tunnel, higher jump and gyro targets.
3. `s2b_specialist_recovery`: keep mild DR and isolate dog-hole, legal fly-ramp launch, and real in-place jump after repairing their counters/rewards.
4. `s3_full_dr`: full deployment randomization, full dog-hole route, all terrain skills retained.
5. `s4_smooth_consolidate`: lower policy entropy and stronger action-rate/action-acceleration penalties with full DR.

## Runtime gates

- [ ] Python compile and static contract tests pass on the target Isaac environment.
- [ ] A patched 128-env smoke run completes without traceback, nonfinite values, 64K material errors, closure error, or mimic error.
- [ ] The formal 1536-env process acquires the single-GPU lock and reaches PPO iterations.
- [ ] Each phase produces a checkpoint and immutable source snapshot.
- [ ] Final ONNX export succeeds.
- [ ] Four-seed nominal and four-seed DR episode evaluation covers every route kind.
- [ ] Report action smoothness, route completion, tunnel underpass, launch/air/landing, closure, and mimic safety separately; no aggregate score may hide a failed route.
- [ ] Write `COMPLETE` only when nominal and DR summaries pass their per-route hard gates; otherwise write `NEEDS_TRAINING` and retain the checkpoint.

## Acceptance intent

The run is a recovery run, not proof that every skill has passed. A skill is accepted only from deterministic post-training rollouts. The training process must not label a route successful from reward magnitude alone.
