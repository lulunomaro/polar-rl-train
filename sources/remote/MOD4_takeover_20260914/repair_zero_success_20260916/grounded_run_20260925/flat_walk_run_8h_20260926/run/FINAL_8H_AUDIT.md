**Correction 2026-09-26:** Its tilt/contact means included samples after an environment had already reset. Completion counts remain valid. Use `eval_nominal_first_episode_v2.json` and `eval_gasdr_first_episode_v2.json` for first-episode metrics.

# MOD4 flat walk/run eight-hour audit

Training ran from 2026-09-26 01:11:21 +0800 to the eight-hour deadline; status `TIME_BUDGET_COMPLETE`. The saved final checkpoint is `/home/egde/rl_candidates/MOD4_takeover_20260914/repair_zero_success_20260916/grounded_run_20260925/flat_walk_run_8h_20260926/run/mixed_gas_dr/logs/2026-09-26_07-01-30_flat_mixed_gas_dr_20260926/model_385.pt` (SHA256 `0ceba3209b9905408c347509f23ed04a5f960d9223743ee2a49bdc6912516256`). All three phase checkpoints remain intact.

| 15-second deterministic test, same seed 202609268 | Survived | Passed all bars | Tilt RMS | Velocity error RMS | Both wheels in contact | Action delta/d2 RMS | Max closure/mimic residual |
|---|---:|---:|---:|---:|---:|---:|---:|
| 500 N nominal | 21/64 | 0/64 | 17.66° | 0.680 m/s | 71.7% | 0.028/0.042 | 0.214 mm / 0.0017 rad |
| Gas force only, 300–700 N full-stroke envelope | 19/64 | 0/64 | 17.69° | 0.662 m/s | 72.1% | 0.027/0.040 | 0.192 mm / 0.0018 rad |

Acceptance bars: tilt <=8°, speed error <=0.75 m/s, angular XY <=1.5 rad/s, both-wheel contact >=90%, action delta <=0.18, d2 <=0.25, and survive 15 s. **Result: zero qualified episodes in both tests.** Nominal mean forward speed was 0.217 m/s; gas-only DR mean was 0.208 m/s. The final model is smoother and more upright than the start, but it is not a stable walk/run policy.

**Critical contract defect:** During the eight-hour run, `RM_DR_OFF=1` made `sample_gas_reference_force()` assign 500 N unconditionally. Thus the phase named `mixed_gas_dr` did **not** train over 300–700 N. The initial DR evaluation repeated the nominal result exactly and exposed this. After training, I added `RM_GAS_FORCE_DR_ONLY=1` in this isolated stage, with a passing unit test, and reran a true gas-only evaluation. It sampled reference forces 423.2–606.5 N; full-stroke elastic-force envelope is 300–700 N. The checkpoint is unchanged.

The binding failures are pitch (-17.2° nominal) and intermittent driven-wheel contact (71.7% nominal), not action smoothness. Inspect the height/pose target, load distribution between drive and guide wheels, and why the controller settles tail-down before another training budget. Retain the final and old checkpoints; no claim of verified running or gas robustness.

Raw paired results: `eval_final_nominal_15s.json`, `eval_final_gasdr_only_15s.json`.
