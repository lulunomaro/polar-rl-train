# Moving Jump Repair: New Two-Hour PPO Run

The user authorized repair followed by another two hours of moving-jump learning on Host72. This is a new task with a fresh7200-second continuous owner window; repair and admission are outside that window. Host210 and the existing viewer were not touched.

## Evidence And Repair

Previous R3best nominal fixed cases:51takeoffs,51air-balance passes,0measured retractions,0complete successes. Minimum nominal airborne leg difference median1.055rad, range1.018-1.133rad; required<0.9rad. Flight teacher-fit MSE was substantially above other phases. Native PPO already clips actor and critic separately, so critic gradient magnitude is not a demonstrated direct actor-clipping cause.

The old airborne reward switched to extension as soon as vz<0, and the teacher/cue switched at vz<-0.10, irrespective of measured retraction. The repair requires measured tuck before landing preparation in reward, observed command and training labels. Thresholds and success rules are unchanged. Online guidance now averages each present phase and weights flight4; equal-phase demonstrations also weight flight4. Only learned actor actions drive the training plant.

The40ms teacher probe achieved nominal51/51retractions but only37/51complete passes because14cases exceeded10degree air pitch. Its raw failures and source are retained. The final teacher restores the original80ms ramp. Final native teacher complete nominal: 48/51. Successful dataset metadata: {"seed": 20066, "teacher_sha256": "03884d680c0fcb4c5216f8aeaa42c319473ea1cbc7261df089f42c1136b07edd", "successful_episodes": 154, "requested": 256, "samples": 46200, "phase_counts": [16810, 2559, 1386, 2246, 23199], "native_success_only": true, "optimizer_created": false, "teacher_execution": true, "note": "Training demonstration collector; this is not a learned-policy evaluation"}. These are teacher collection results, not learned-policy successes.

Native runtime admission passed original assets, motor limits and physical timing. No-update guidance loss=0.219019, finite gradient norm=1.855410; no optimizer was created or stepped for that check. Physical runtime admission restored PPO state but took zero updates.

## Frozen Parents And Runtime

- Root five-minute parent SHA: `03884d680c0fcb4c5216f8aeaa42c319473ea1cbc7261df089f42c1136b07edd`.
- Best prior learned child used for full PPO continuation: `eb8a6d42b17332100935201530a82688e9bad273af2ef5a8c28d49aa0e29f104`, iteration26590.
- Remote workspace: `/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V3_FORWARD_JUMP_REPAIR_2H_20261114_R1`.
- Physical GPU0: one2048-environment optimizer owner; GPU1: fixed independent evaluation without an optimizer.
- Actor35, critic78, actions6; full actor/critic/STD/17Adam states and RNG restored, fresh physical episodes.
-2.5ms/TGS32/4; leg100Hz/wheel400Hz/policy50Hz;10mm closure and0.01rad mimic single-episode resets; motor envelopes and assets unchanged.
- Phase-command input semantics are versioned and require a matching deployment input producer. This is a simulation trial, not production promotion.

## Actual Learning Start

Start: 2026-11-14T11:52:19.165226+08:00. Target end: 2026-11-14T13:52:19.165226+08:00. First measured PPO update iteration: 26591. Changes verified: `{'actor': True, 'critic': True, 'STD': True, 'Adam': True}`. Full first-update checkpoint: `99b85652349c5975991483367beecac446c868032eb08e1de02e5a611c2d7cd1`.

Training and evaluation are in progress. No success or completion claim is made by this launch record. Final selection will use standalone deterministic actor evaluation on51nominal/205fullDR fixed cases, retain later terminations as failures, and preserve every intermediate checkpoint and failed attempt.
