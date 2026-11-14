# Forward Jump Repair And New Two-Hour PPO Result

New continuous learning window: 2026-11-14 11:52:19 CST to 2026-11-14 13:52:24 CST; actual owner duration 7205.178s. Preparation, physical admission and teacher collection happened before this window. PPO updates: 735; native environment steps: 36,126,720. Exactly one optimizer owner on Host72GPU0; GPU1evaluations created no optimizer. Full saves were made every five minutes and at final completion.

Independent evaluation startup failures and separate retries: eval_model_070m -> eval_model_070m_retry1. The original70minute evaluator segmented during engine initialization before creating an environment or evaluating any cases. Its process exit and absent GPU context were verified, its raw log and failure marker retained, and a new attempt evaluated the same immutable checkpoint. The local observer was repaired and restarted; the native training owner was never restarted or paused.

Selected child: `model_085m.pt`, iteration 27116, SHA256 `c4d0328472e8642c497f113e37fb8940d92435cd8d96f547b8f1f4aa15cc1dfe`. The complete result requires the full forward-crouch-push-air-tuck-land-stable sequence and excludes any later termination.

| Fixed evaluation | Nominal | Full DR |
| --- | ---: | ---: |
| Measured takeoff | 51/51 | 205/205 |
| Measured tuck | 51/51 | 205/205 |
| Airborne balance | 51/51 | 173/205 |
| Complete and survived | **51/51** | **172/205** |

Total accepted complete cases: **223/256**. The selected child has no later failures among its successful cases.

The final chronological checkpoint is retained separately. Its accepted result is nominal **51/51**, full DR **78/205**. The full DR raw completed-event count was 117, but 39 of those cases later terminated and were excluded. The intermediate console counters must not be read as final accepted successes. Every checkpoint's raw, later-failure and survived counts are in the CSV and JSON.

## Repair And Evidence

The predecessor best learned child had nominal0/51tucks and0/51complete passes, despite51/51takeoff and airborne balance passes. Measured minimum airborne leg difference median1.055rad exceeded the unchanged<0.9radcriterion. Flight action fitting error was much higher than other phases. We confirmed conflicting timing: reward started rewarding landing extension at vz<0, while teacher/cue switched at vz<-0.10regardless of measured tuck. The repaired reward, observed landing-preparation command and training-only labels all require actual measured tuck first. The original80ms teacher tuck ramp was retained. Online loss uses phase-balanced means and flight weight4; equal-phase demo loss uses the same flight weight. The two-hour plant is driven solely by learned actor output; there is no scripted motor overlay.

The first40ms teacher probe was rejected as the final teacher:51/51nominal tucks but37/51complete passes,14pitch failures. Its successful and failed cases, source snapshot and dataset remain recorded. The80ms follow-up dataset and all failed attempted episodes are stored separately. Teacher successes are not counted as learned-policy performance. No standalone BC warmup or unbudgeted optimizer update occurred. Native PPO already clips actor and critic separately; no unproven critic-clipping defect was claimed.

## Provenance And Contract

Continuation parent SHA `eb8a6d42b17332100935201530a82688e9bad273af2ef5a8c28d49aa0e29f104`; root five-minute parent SHA `03884d680c0fcb4c5216f8aeaa42c319473ea1cbc7261df089f42c1136b07edd`. Complete actor, critic, STD, 17 Adam states and RNG were restored from the prior best learned child. Actor 35 / critic 78 / action 6 retained; fresh physical episodes. The native MOD4V3 HW300N60R3 asset, motor envelopes, 2.5ms / TGS32/4, leg 100Hz / wheel 400Hz / policy 50Hz were retained. Closure 10mm and mimic 0.01rad are per-environment episode resets. Admission and the zero-update finite-gradient check are in evidence.

Acceptance thresholds remain: measured tuck<0.9rad; air>=0.16s; wheel rim peak>=0.12m; all-air pitch<=10deg/roll<=5deg; stable forward landing>=0.5s with>=80%support,|vz|<0.3m/s,vx>0.1m/s,roll/pitch<15deg,no forbidden contact. No threshold was lowered.

Selection uses the lower nominal/full DR success rate first, then total successes, nominal successes and recency. All fixed-checkpoint evaluations and individual failures are retained. These fixed cases are selection evidence, not a claim of generalization across all seeds. Phase command semantics are versioned and need a matching deployment input producer. No production or hardware promotion was performed. Host210 and the existing viewer were not touched.

## Files

`checkpoint_results.csv`, `results_summary.json`, `training_curve.png`, selected complete PPO checkpoint and recorded-native-state video/frame board are in the delivery directory. Full PT bodies are retained in Git as specifically requested for this session; large trajectory and media originals are indexed by path,size,SHA. Launch and final Git receipts are verified separately by the archive tool.
