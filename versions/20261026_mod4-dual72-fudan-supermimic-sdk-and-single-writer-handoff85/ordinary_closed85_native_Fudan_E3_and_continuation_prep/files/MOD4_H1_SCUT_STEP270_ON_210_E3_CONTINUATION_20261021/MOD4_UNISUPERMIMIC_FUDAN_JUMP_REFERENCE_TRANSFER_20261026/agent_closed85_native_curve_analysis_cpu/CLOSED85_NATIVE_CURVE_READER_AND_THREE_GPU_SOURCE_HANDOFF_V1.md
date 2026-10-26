# Offline native curve reader and next three-GPU source handoff

This directory is a local source/CPU preparation. It does not collect a remote run, qualify a checkpoint, create a ledger, copy a model, or admit a new GO. The actual V85M2 closing curves were not supplied to this helper. `actual85_pending/NATIVE_CURVE_TEXT_ANALYSIS.json` therefore retains pending curves, null summary, unknown source, and no FINAL. The separate production work-order receipt records the already observed first native Pi update; that observation is not a completed-window result.

## Read the later actual text

Use Python 3.14 with only its standard library:

```powershell
& 'C:/Users/lulu/AppData/Local/Programs/Python/Python314/python.exe' -B '<this-directory>/native_curve_text_reader_v1.py' --collector-json '<actual-local-closing-collector-receipt.json>' --out-dir '<fresh-local-analysis-directory>'
```

The collector schema is the existing V85M2 `all_texts` array with `relative`, `local_path`, `bytes`, `SHA`. The reader verifies each selected local text against those producer pins. It resolves these exact suffixes under logical slot `e2/`:

| Meaning | Relative suffix |
| --- | --- |
| Native H1 original GO | `/job0/GO_PRODUCTION.json` |
| Iteration-sampled curve | `/job0/production/ACTUAL_H1_CONVERGENCE_CURVE.jsonl` |
| Completed-control index | `/job0/production/control_prefix_raw/CONTROL_VALID_PREFIX_INDEX_ACTUAL.json` |
| Original lifetime counters | `/job0/production/control_prefix_raw/CONTROL_LIFETIME_GOAL_EVENTS_ACTUAL.json` |
| Native terminal manifest | `/job0/production/FINAL.json` |

Explicit `--curve-jsonl`, `--go-json`, `--prefix-json`, `--lifetime-json`, `--final-json`, and optional `--generic-metrics-json` are also available. Supplying the same input through both modes is rejected. Inputs must be bounded UTF-8 JSON/JSONL text. Checkpoint/NPZ paths inside metadata are never opened. The owner segment is retained from **`authority72.original_segment`**, with its original field structure uninterpreted; the reader never relies on reviewer stdout or an obsolete source210 key. Current closing review is root's V3 one-load reviewer, independently of this reader.

## What the analysis means

Each curve point retains original GO wall seconds, learner iteration, actual WM/Pi update counters, completed physical control rows, and environment transitions. A control row means a returned complete `vec.step`; partial physics callbacks are excluded. For 20,000 environments the two transition counts must equal completed controls × 20,000. Prefix index chunk counts must sum to its controls. The final counter snapshot must cover those same completed controls before full coverage is reported. This is a text evidence consistency check, not an added training or physics gate; it does not replay raw state or independently re-execute the goal machine.

`completed_control_goal_events_v1` counts original takeoff, landing, and recovery counter positive deltas with reset accounting from the previous completed row's `done`. Cross counts are rising edges of both original leading-edge flags. They are not complete-footprint contact or skill success. The reader checks the exact schema, original coverage flags, invalid/negative/write-error diagnostics, integer counts, and cumulative monotonicity. Initial snapshots are retained and are not added to lifetime deltas. It does not assume H1 counters apply to normal E2 or E3.

Curve writes happen in `before_action` once per learner iteration. The first positive curve count is therefore bounded by `(last valid zero curve observation, first valid positive curve observation]`. Its exact event time is unknown. If the first valid observation is already positive, the lower endpoint remains null. Final lifetime counts are separate from the last curve observation; a terminal event missing from the iteration curve is not assigned a fabricated curve time. An absent counter is unknown, never zero. Malformed lines, including an interrupted last line, remain in the report with their original text; valid earlier rows retain their limited scope.

Loss meanings come directly from the pinned current learner source:

- `wm_last`: WM prediction loss divided by its rollout window; masked final-step prediction error.
- `policy_last`: negative imagination objective; imagined critic MSE; normalized imagined reward; policy gradient norm; mean imagined survival.

These outputs are separate from physical task events and from uninterpreted generic velocity metrics. `Metrics/velocity/success_rate = 1` is not H1 step270 graduation. The existing native imagination reward is not physical V8 RewardManager reward. The reader does not claim frozen-policy skill, a causal PPO comparison, or same-dynamics validity for foreign Fudan transitions. Null `FINAL`, checkpoint SHA, source, and latest-save metadata stay null/unknown; presence of `FINAL.json` alone is not model qualification. Manifest write time is not the original accounting terminal.

## Next three slots, preparation only

The machine plan is `NEXT_THREE_GPU_SOURCE_ONLY_PLAN_V1.json`. It preserves the current pair until actual original closure, complete save, owner/children all out, locks released, canonical settlement, and independent source/fullstate qualification. No next owner or GO is implemented here.

| Future slot | Machine/resource | Allowed source type |
| --- | --- | --- |
| Normal H1 PPO | Restored original single210, actual GPU identity pending next readback | Qualified complete83B production H1, update130 / Adam829700, SHA `8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6` |
| Native Fudan H1 | 72 GPU `GPU-16828f91-2b45-b646-8dc0-9481138e2842` | Future qualified complete85M2 native WM/Pi/Critic/optimizers; actual final artifact and qualification pending. Logical key `e2` is native H1, not normal E2. |
| Normal E3 recovery PPO | 72 GPU `GPU-c27eecbd-6838-7290-1cd2-37e34522213d` | Future latest qualified completed E3; pending. Existing fallback complete83B E3 update83 / Adam860800, SHA `68d95156fc5dd294e43b21ad39691da8f1df1c5b85667db3001335796521ea49`. |

The source210 original NTFS mount was recorded rw with 716,942,045,184 free bytes; this is a historical saved receipt, not a fresh admission probe. Its old canonical was actually tombstoned after preserving exact old bytes. It must remain retired. The single authority remains 72 generation `MOD4_SINGLE_WRITER72_20261026` at `/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json`. A future source210 worker must use the reviewed forwarded control to that authority; it must never recreate an old210 canonical. All process/GPU/private-lock and full physical-save protections remain required.

Finite mode and the existing strict minimum 86,412.86069250107 seconds remain unchanged. Three original 3,900-second caps total 11,700; original 3,600 save block and 300 headroom remain. Admission must use the then-current authority balance after the present pair is settled. No current balance is inferred from the first-observer snapshot. Actual GO-to-actual-terminal time is charged once in full, including an actual overcap duration with `duration_bound_passed=false`; no truncation, refund, history reconstruction, or new budget is authorized by this plan.

Normal and native H1 keep 100Hz ×4 physics callbacks; E3 keeps 50Hz ×8; physics remains 2.5ms/TGS32/4. Proper source and target SDK qualification must match each actual scope. Existing same-source native/160k-query evidence is reused; 2mm remains a per-environment reset rule. Frozen E0/W35 and every other source stay retained. The frozen E2 source/CPU candidate is not part of this next GO. This plan implements no new reference, command, reward, policy, or success change.

## CPU proof and preserved errors

The first synthetic attempt was 10/11. It correctly exposed an incorrect drafted GO basename (`ACTUAL_GO.json` instead of actual `job0/GO_PRODUCTION.json`). Its source snapshots, fixture inputs, and failed report are preserved. A separate PowerShell attempt used unsupported `New-Item -LiteralPath`; source snapshots were then saved before the source correction using the original unchanged source. Both local helper errors are recorded in the manifest and are not training failures.

The corrected attempt is 11/11, covering real producer fields, text pins, interval censoring, null/unknown states, partial/invalid counter coverage, interrupted tail, monotonicity, prefix coverage, separate losses/generic metrics, and refusal to open model suffixes. Corrected CLI runs separately prove synthetic valid input and empty actual85 input remaining pending. No policy, RNG, optimizer, plant, GPU, model, raw NPZ, remote transport, or Git action was performed.

All files, the failed attempt, corrected source snapshots, lineage pins, and reports are indexed for root's later ordinary85 supplement. Git status remains **pending root archive**, not recorded by this helper. New actual collector inputs should be analyzed into a fresh directory without changing this frozen source or its preserved attempts.
