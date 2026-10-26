# E2 native SuperMimic: concrete source / CPU candidate

The E2GoalMdp, declared command-reference book, readonly source adapter, native transition bridge and complete bridge/book tensor roundtrip are implemented. Final fixtures pass15/15. No source environment, policy/model, optimizer, plant, GPU, network, Git, lock or budget writer ran. This is not a new Task/GO or expert graduation. Existing E0/W35 and all qualified experts remain retained; H1/Fudan and mixed84 files were not edited.

## Sources and lineage

Integration modules are `e2_native_supermimic_candidate_v1.py` and `e2_source_readonly_adapter_v1.py`. Tests are `test_e2_native_source_cpu_v1.py`; schema is `e2_reference_schema_v1.json`.

Current qualified complete83B E2 lineage supplied by root:90 updates /17 Adam857460, SHA `72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f`. No weight file was opened or hashed. Payload `job0/TASK.json` describes its historical85-update input, not that later complete90-update output; these are recorded separately. Original source files and their exact SHA/bytes are indexed in the lineage receipt.

The original training entry installs `e2_directional_spin_runtime_v1` as `directional_spin_runtime` for kind `E2_WORLD_MOVING_SIGNED4`; source comments predating deployment are not treated as live execution status. The command term is `command_manager.get_term('twist')`. Actual fields are `command`/`vel_command_b`, standing/heading/pure/moving/transition flags, `world_direction`, `signed_yaw`, `phase_elapsed`, `time_left`, `progress_goal`, `body_limit` and `manual_evaluation_mode`. The private `_mode_rng` remains untouched. Original `E2_moving4_command_state` and D0–D7 private checkpoint state remain owned by the original complete-save writer.

## Command and reference semantics

The effective source twist is BODY `[vx,vy,wz]`. For world-moving samples, `vx=2*V*cos(actual_heading-world_direction)`, `vy=0`, `V=.5`, and signed yaw is±4 rad/s. The instantaneous world velocity has twice-yaw ripple; only its complete-turn mean isV along the world direction. A constant world `[V*cos(alpha),V*sin(alpha)]` velocity/straight path would contradict the source command.

The implemented reference uses the analytic ideal nonholonomic path including that ripple, signed yaw, and the exact source12 s start/hold/brake/stop/reverse/hold/brake/stop profile. It is explicitly a **declared command-following kinematic hypothesis**, not a measured demonstration or a physically feasible expert trajectory. Pure spin retains zero translation; standing/straight and manual literal command modes are explicit. Planned q30/dq30 are unobserved, remain zero in goals, and have no pose imitation term.

Each observed command interval registers an immutable plan. Native scalar `f=planID*1024+control_offset` preserves the existing native `goal(frames)` / `frames+1` interfaces without reading H1 public-request ages or counters. Actual heading-dependent body command changes and deterministic transition profile updates do not fabricate new random command intervals. A plan changes only after actual public command-state/resampling/reset evidence. Unknown future private RNG draws are never predicted: `valid_imagination_start` excludes a rollout that reaches the observed resampling timer. Old plans are retained for replay; they are never overwritten.

The source `_update_command` writes the transition yaw and then advances `phase_elapsed` by the actual20 ms control clock. The planned transition anchor uses `max(phase_elapsed-.02,0)` and preserves the exact actual command readback at offset0. Actual SDK timing/source callback readback remains a future runtime check, not a claimed executed probe.

## Exact dimensions and action provenance

| Component | Values |
|---|---|
| Own state |73: local XYZ, wxyz, world v/omega, q30/dq30 |
| Mean contact history |18:3 fixed5 ms bins×2 wheels×3 vector force |
| Applied torque |30 |
| Public command/context |16: body twist3, five flags, direction cos/sin2, signed yaw, phase time, progress goal, body limit, height command, manual flag |
| Delay context |28: leg history12+lag/age2, wheel history6+lag/age2, previous processed targets6 |
| Resampling timer |1 |
| Native context |93 |
| Native observation |175 = invariant73+previous action6+context93+heading-frame relative plan error3 |
| Candidate native history |10;1750 values before goal conditioning |
| Native goal |73 per requested frame |
| Critic base / with one goal |170 =73+93+3+1;243 with goal73 |

The old PPO actor175/critic98 are retained baselines. The native175 count is a dimensional coincidence: its feature meaning and history10 differ, and no old175 weights can be treated as compatible native policy weights.

The original source's `_own_flat_frame['executed6']` is `ActionManager.action`: actual ingress after the existing vector wrapper clip6, **before** delayed target processing, PD and motor saturation. It is not measured motor action/torque. Native transition `a` is explicitly that plant-interface ingress. Pre-action action-delay queues, lag/age, and previous processed SI targets are carried separately in context; applied torque30 remains separate. The bridge forwards the requested native action object unchanged to the original vector wrapper and never adds its own clip, delay, PD, command update or force.

Raw root13 is the current measured xyzw convention; packing only subtracts own environment origins and reorders xyzw to wxyz. Velocities and q/dq are unchanged. Source `E2H1FlatEnv` already exposes a termination-manager pre-reset `_own_flat_frame`; this adapter reads it and does not install hooks or enable capture. Terminal `s1` is that actual pre-reset state, not the source's post-reset current state. Real physical reward/done are passed unchanged. Only actual own transitions enter native WM replay.

## Native imagination objective and original physics

The source physical SCUT velocity/yaw/height/rolling and stateful phase-compensated cycle-cross rewards are unchanged. `E2GoalMdp.reward` is a separate, declared native imagination surrogate: signed BODY forward/pitch-corrected velocity and signed BODY yaw tracking, own height task, low-weight deviation from the correct periodic planned path, upright factor and action/joint-speed regularization. It does not claim reproduction of every original physical reward term or a measured imitation demonstration. CPU tests show a valid instantaneous world ripple is not penalized as secular drift and wrong signed yaw is penalized.

Physics remains2.5 ms,50 Hz×8, original TGS32/4, original commands/PD/delay/DR/reset/success. Existing float32/native160k-query evidence and2 mm per-environment closed-chain reset remain. No new global FP64/bitwise/triangle numerical gate is added. `Metrics/success_rate` / renamed velocity-tracking success remains a command metric, not proof of complete turns, world progress, drift, stop/reversal, physical support or full E2 graduation.

## Verification and preserved failure

First attempt:11 passes /1 failure. The code/test manifest labeled critic-base169, while the real constructed tensor was170 (`73+93+3+1`). Its report and exact source snapshot remain unchanged. The correction states170; no channel padding or physical change was made. Final attempt passes15/15.

Fixtures cover source-AST body/transition function parity, signed complete-turn world progress and cross ripple, zero-yaw limit, clock/resampling boundary, exact93/175/170/73 shapes, root provenance, gradients using tensor math only, original action/reward/terminal forwarding, source field mapping without RNG reads or writes, immutable replay plan retention/capacity refusal, source transition changes without fake resampling, and complete software bridge/book tensor roundtrip. Tensor roundtrip explicitly does not claim exact PhysX resume. Every invocation preserves its source bytes and separate report.

## Remaining actual admission

The source-only checklist requires: actual source-qualified checkpoint lineage and full original private-state save ownership; current actual30 SDK joint names; exact actual delay queue/lag/age/processed-target layouts; actual pre-reset capture callback timing and ingress semantics; public transition clock validation; own50 Hz/2.5 ms×8 readback; bounded plan-book capacity/lifetime and replay retention; live plan synchronization if native learner and sampler devices differ; complete native WM/Pi/Critic/optimizers/history/replay plus reference-book/bridge save and failed-partial handling; owner-approved new experiment/GO and original budget boundary. No such runtime action was executed here.

The default book is bounded and refuses capacity exhaustion rather than overwriting replay plans. A future long original-writer experiment must admit capacity covering its interval or a proven replay-safe retention implementation. Source CPU fixtures are not a runtime performance/memory certificate. A fresh physical episode on restore must follow the owner's original complete-source/new-episode protocol; loading software bridge tensors does not restore a plant.

Dynamic feasibility, original-policy/native comparisons, actual displacement/signed complete cycles/cross drift/support/stops/reversals and frozen skill evaluation remain pending. Root requested this handoff and freeze; this helper will not automatically expand another skill.
