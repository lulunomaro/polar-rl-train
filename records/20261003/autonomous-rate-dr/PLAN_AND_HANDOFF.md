# MOD4 remote autonomous rate and DR controller

User 2026-10-03 authorized independent automatic rate/DR progression while the local PC is off. This controller runs detached on the existing 4090 host; Codex desktop heartbeats are not its execution engine.

Production root remains `/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002`. New entry `isaac/mod4/supervise_autonomy.py`; preparation `/home/egde/rl_candidates/MOD4_AUTONOMY_SLEEP_20261003`. Read `reports/AUTONOMY_HANDOVER.json`, `AUTONOMY_STATE.json`, actual `/proc` identities and `status.json`. Dispatch does not prove completed handover or production.

Only the original canonical ledger is authorized: `/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json`, 180000 effective PPO seconds. Both prior 20-hour extensions are already applied. No new budget, ledger copy, reset or repeated handover is permitted. PPO scene loading, preflights and save/exit time count; isolated frozen evaluations do not.

## Automatic decisions

- Retain current 6rad/s learning and all existing thresholds. Two distinct complete policies must pass the current-cap skill plus flat regression; then identical candidate two-seed nominal/active-DR initial-root/q pairs must pass before advancement.
- Rate ladder remains 3, 4, 6, 8, 10, 4pi rad/s. 4pi is a goal, not a measured result. New rate gets 3s frozen physical smoke, 20k1.2s actual physical/material readback and 128env two PPO rounds. Discard preflight weights and preserve original optimizer/std/critic/actor/iteration.
- Hold yaw fixed when changing DR. At a mature 6rad/s, prefer white_v2 before 8; at mature 8 with white_v2, prefer white_v3. Frozen nominal/current/wider two-seed flat/spin pairs and actual parameter audits must pass first. Then 20k physical readback, 128env two PPO rounds, 20k four PPO rounds with throughput protection, and 45min trial. Final two-seed nominal/wider flat/spin checks must pass to accept.
- white_v1 retains mass/inertia and six motor factors 0.95–1.05, wheel friction 0.8–1.0. white_v2 uses 0.925–1.075 and friction 0.75–1.0. white_v3 uses 0.9–1.1 and friction 0.7–1.0. Every profile keeps about 20% clean nominal environments, independent RNG and 33 material buckets. Motor gains are followed by the ORIGINAL hardware torque-speed clipping for all three profiles. PD, COM, spring, noise, delay, hardware limits, reward and PPO coefficients remain unchanged. These are uncalibrated engineering stress ranges, not real-world certification.
- Rejecting wider DR restores its pre-trial full policy and previous profile, preserves failed weights/results, and prevents repeated overnight attempts of that rejected profile. Real flat/physics regression restores the last paired mature complete policy. Three unsuccessful new-rate skill blocks return to the actually certified cap rather than spending all remaining time on that failed rate; a separate wider-DR trial of the mature policy is allowed.
- Latest-cap ordinary BODY arc skill is rechecked with two seeds and nominal/active DR when mature. Existing successful generalization does not automatically add another PPO course. This is not world-frame FPS motion or spin-directed translation. The latter's 0.15→0.3→0.5m/s SDK/PPO adaptation and Rough/airborne/full closed-chain reset remain separate incomplete work; this controller does not mix them in blindly.

## Preserved evidence and safety

All original group booleans, failed environments and old contact-window shadow stay in the reports. Add a separate severe single-environment guard; group averages cannot hide severe tilt/unloading or death. +/-2m/s flat extrapolation remains diagnostic. Mean world XY speed is not net displacement; mesh support-point slip is a proxy, not PhysX manifold slip. 5ms integrated contact passing is neither continuous support nor learning progress. Original contact-window gate is project-defined.

The new whitelist module passes CPU reset/RNG/array bit equivalence against white_v1, broader actual-parameter tests and motor post-gain saturation tests. Target-side CPU tests precede dispatch. Wider GPU/PPO/45min acceptance is deliberately deferred until the remote gates qualify; do not describe stronger DR as already active.

Retired parent identity is checked before suspension; trainer-specific `latest_complete.json` selects the control directory. A stop request saves complete state; only after CPU validation does the handover settle the still-unaccounted tail exactly once, retire the old supervisor and acquire the SAME canonical lock. Tail exit detection has at most one second polling uncertainty, disclosed in the receipt. The standalone guardian restores the original parent if migration fails before receipt and enforces a stop-file at canonical budget exhaustion. Each trainer also has its own bounded deadline (at most two hours), independent of the supervisor process and this PC.

The first dispatch exited before pausing the parent because a just-started trainer did not yet have a complete receipt. Original production continued. Retry1 waits for the actual PID-bound receipt. Keep the initial error log; do not rerun either deployment script or the one-shot takeover after receipt exists.

## Recovery and final stop

Use `--resume` only with a completed handover, no trainer/probe and a fully reconciled canonical active segment. An interrupted `AUTONOMY_STATE.active_training` requires review, not blind clearing. Bind recovery to its exact trainer/run/save receipt; never use the global highest iteration, which may belong to a rejected DR preflight or trial. Sudden reboot needs last health/log/checkpoint/shutdown evidence and a separate explicit reconciliation record, preserving charged time and both extension IDs. No automatic reboot launch is installed.

At budget exhaustion, complete-save stop precedes final flat, current-DR spin and nominal spin. `AUTONOMY_FINISHED.json` and actual final outputs define achieved ability and failures. Desktop mod4-10 remains a two-hour quiet monitor; it should delete itself once final results are reviewed. The Ubuntu TUI continues following the same root/status/active log with five-second local file refresh only.
