# Autonomous Stair Jump Final Result

Task outcome: **FAILED**. The finite optimizer run and final evaluation completed, but the final model achieved 0/256 stable target stair landings. No completed checkpoint had a target crossing or successful landing. The existing manual player is not promoted to a failed stair policy.

## Final Independent Evaluation

| Group | Height(cm) | Cases | Takeoff | Crossed in air | Both wheels top | Stable success |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fullDR | 16.5 | 104 | 104 | 0 | 0 | 0 |
| fullDR | 22.0 | 101 | 101 | 0 | 0 | 0 |
| nominal | 16.5 | 26 | 26 | 0 | 0 | 0 |
| nominal | 22.0 | 25 | 25 | 0 | 0 | 0 |

Nominal median wheel-lower-rim peak above the approach ground: 5.16cm. This measures the lower of the two wheel rims during qualified flight, not chassis/root height. Nominal median sensed target-edge distance at episode end: 0.505m. The outcome is consistent with small hops before the edge, not successful stair traversal.

There are 21 completed checkpoint evaluations and 1 failed/missing evaluation. Every completed evaluation used the same specified 256 cases(seed10066); do not pool checkpoints into an independent success-rate estimate. The 30-minute evaluation failed `Terrain height observation mismatch` and has no accepted RESULT. Its original ERROR and source are retained and it was not replayed.

## Timing And State

- Original window start: 2026-11-14T22:36:38.623455+08:00.
- Valid repaired segment start: 2026-11-14T22:46:58.990453+08:00.
- Original deadline: 2026-11-15T00:36:38.623455+08:00.
- Final checkpoint saved: 2026-11-15T00:36:45.917915+08:00; runtime closed: 2026-11-15T00:36:49.332866+08:00.
- Final evaluation finished: 2026-11-15T00:39:31.344807+08:00.
- Valid segment wall time: 6586.927s, updates: 618, environment steps: 30375936.
- The final rollout and complete save finished 7.294s after the absolute deadline. No automatic new training window was started. Failed initial runtime and repair/admission consumed the same original 7200s window.
- Final checkpoint SHA256: `fc4ad9131d922763fa3d9670106ffe9d3ac7e43d712f40c0b9630f2b57a92674`; the downloaded checkpoint hash matches both training and independent evaluation.
- All rejected R1 source, reports and checkpoints are retained. R2 had no PhysX console error; closure resets: 1, mimic resets: 0, numerical resets: 0. These are per-environment events.

## Confirmed Reward Defect

`Outcome.update` clears `qualified` at contact and can emit `takeoff=start` again after the next qualifying flight, even though `took_off` is already true for the episode. `_get_rewards` grants 2.0 for every such event. This permits repeated small-hop rewards in one episode. Large raw takeoff event counts are therefore not independent successful jumps. The source defect and observed pre-edge hops are documented; no causal reward-ablation experiment is claimed.

Even the 4cm warmup only accumulated 19 crossing events and 17 first dual-wheel top contacts, with zero 0.5s stable successes. Other training heights had no crossings. Time-based difficulty promotion continued despite that lack of mastery. This run did not learn the requested skill.

The next version needs an episode-bounded or removed takeoff bonus, useful forward clearance/edge-progress signals and a curriculum tied to actual task mastery. Those changes are not applied to this frozen run, and this report does not launch a new budget. Original plant, motors, timing, DR contracts, one-tile player and one-shot Space interface remain as archived at launch.

Full per-case evaluations, failed evaluation, raw logs and artifact hashes accompany `evidence/FINAL_SUMMARY.json` and `evidence/ARTIFACTS_FINAL.json`. Training and evaluation are complete; both GPUs were free at the final read-only status check.
