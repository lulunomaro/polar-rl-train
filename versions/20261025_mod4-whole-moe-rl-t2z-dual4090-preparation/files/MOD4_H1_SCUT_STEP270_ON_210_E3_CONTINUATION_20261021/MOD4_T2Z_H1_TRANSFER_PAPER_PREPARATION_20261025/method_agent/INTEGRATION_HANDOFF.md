# Root / engineering handoff

Scope here is complete local **method and synthetic-interface preparation**, not a running T2-z system. Root owns serial host72 deployment, shared-host coordination and unified Git. This agent made no SSH/remotehost calls, installation, model/data download, physical rollout, policy inference, model training, production edit, budget mutation, kill, Git commit or subdelegation. Native RGB collection and Wan integration have not occurred.

## Minimal concrete next stage after current H1 finishes

1. Root confirms actual completed H1 policy/checkpoint SHA, full save, process/resource release and next-stage authority. Source67 H1 Adam790000 and E3 Adam837200 hashes below are historical context, not automatic future starting points. Do not hotpatch the running H1.
2. Put the package under an isolated host72 namespace, retaining original local reports/failed source. Do not launch imports that initialize Wan/CUDA during deployment. The CPU test command can be rerun there only as a new uniquely identified receipt; never relabel this Windows CPU receipt a72 result.
3. Engineer implements an authorized native RGB + actual per-physics applied-target collector and receipt exporter. No collector is present in this method-only package. First validate a tiny genuinely recorded clip against actual timestamps, reset masks and target readbacks. If data is missing, fail `DATASET_MISSING`, retain the rejection and stop the modeling stage without touching current training.
4. Freeze actual group/source-episode split, train-only action stats and capture camera geometry. Run manifest conversion with `--require-real`, then separately audit file existence/bytes/SHA/decode/native provenance and contact truth; structural conversion alone keeps `training_ready=false`.
5. Export model views and evaluator truths to separate processes/namespaces. Replace upstream `LoadCobotAction` and feed the `[B,T,20,7]` tensor; reject old14D arm action files. Replace the complete old action encoder with the new module under adaln mode; conditioning D comes from the actual old object. All visual comparators receive the same replacement. Save skipped/new initialization keys and architecture/stat hashes.
6. Under the separately approved model-download/hardware/computation stage, test actual Wan forward/loss alignment on native H1 data, then a backward through z with shared modules frozen; verify shared state hashes unchanged and z changed. Measure4090 memory and timing. This is not performed by the current tiny CPU tests. If fit fails, retain the failed attempt/config and return a new reviewable design rather than unbounded retries.
7. Only after those readiness checks and explicit actual budget/context approval, execute the preregistered offline visual comparisons. Real candidate executions and sim-to-real remain later distinct stages. No H1 PPO input/reward/PD edit is required for predictive modeling.

## Shape and key integration checklist

The upstream action special operator produces manipulation-shaped action tensors. Simply naming `action_dim=6` does not fix its4actions-per-latent assumption. The new loader must preserve `[batch,4k+1,20,7]`, including a no-action first frame and twenty applied targets for every following frame. Use exactly the same window offsets for RGB and action. Native frame countT=41 yields context `[B,41,D]`, modulation `[B,11,D]`; the first modulation entry is anchor-only, each remaining entry covers4future frames. Inspect actual pipeline consumers of these tensors and check the VAE's temporal dimension; do not assume CPU shape matching proves spatial/DiT integration.

`replace_action_encoder` is an object-level helper only. Check the actual pipeline attribute name, optimizer trainable-module selection, model device/dtype and acceleration wrapping before using it. Inspect every old/new state_dict key, distinguishing pretrained initialization from strict resume. Training must include new action layers in both Standard and T2-z. During test z fitting, include no action/backbone/context-projector parameters in the optimizer; disable mutable train-mode buffers/dropout consistently; reset optimizer state per group; do not allow optimizer momentum to carry between groups. A frozen model still permits gradients to z through its computations.

The converter's `model` object is an allowlist, but its combined output includes evaluator truth. The engineering loader must consume `record["model"]` only, with actual model tensors assembled from pixels and actions. Avoid passing whole dicts to generic prompt/metadata encoders. Query future target URIs are exported only to the evaluator. Physical group labels route context handles only and never become a feature; numeric physical truth cannot initialize testz.

The fixed upstream `t2z/metadata.py` has task-specific friction grouping and marks selected rows as train. Do not feed a combined H1 split file through it and assume the original split labels survive. Replace that task-specific grouping with a mapping from opaque H1 train-group IDs to contiguous train latent-table indices; retain a separate private mapping receipt. Validation/test group handles create new latents and never alias train indices. True friction/mass values are not a convenient substitute for a model feature or test initializer. Verify every resulting train row's source episode against the frozen split after the actual upstream preprocessing stage.

## Preserved contextual sources

- fixed upstream: `c72f051f5cffcb1f372a32bc488df273556d39b9` and paper `arXiv:2610.22364v1`.
- root-supplied source67 H1: Adam790000, SHA256 `d1dd187177a1878f007b05da26e39c5ee101e937d2d86f0948dde1ffd37f062e`.
- root-supplied E3: Adam837200, SHA256 `0487231c1feec62c9c60063b7f7227ebc7e859ef881a31879a719b0ef03196f7`.
- prior feasibility: sibling `MOD4_T2Z_FUTURE_TRAINING_FEASIBILITY_20261025/reports/SOURCES_AND_COMPATIBILITY_ACTUAL.json` and `ROOT_OFFLINE_TRAINING_AND_ONLINE_REAL_INTERACTION_CLARIFICATION_ACTUAL.md`.
- H1 diagnostics: sibling `H1_STEP270_CLOSED67_SAVED_REPLAY_AFTER_V5_20261025/reports/LATEST67_STEP_TIMING_AND_REWARD_ALIGNMENT_DESCRIPTIVE_ACTUAL.json`; only a selected0.48s saved excerpt, not new rollout or final evaluation.
- action semantics: sibling `H1_STEP270_REWARD_AIRBORNE_FEASIBLE_V5_RESOURCE_V67_20261025/payloads/h1/job0/runtime/isaac/mod4/mod4_task.py` lines114–116 and ActionsCfg; `action_delay_sdk_adapter.py` shows actual target readback before integration. Code was read, not executed.

## Archive inventory and errors

Run/source evidence and every saved report under this directory must be included in root's unique annotated stage trial archive using `record_experiment.py`; verify remote main/tag/peeled through root. Do not claim this directory is already in Git. Keep the failed CPU test's original JSON/log and `FAILED_20261025T054253_test_adapter_cpu.py` snapshot alongside the repaired passing result. Reader errors and the unusable WindowsApps Python alias are preserved in `ACTUAL_PREPARATION_AND_ERRORS.json`; they are preparation errors, not H1 training failures.

The first test used bitwise equality on a reordered float32 mean; it failed despite identical multisets because reduction order changes rounding. The follow-up uses1e-6 mean-comparison tolerance and retains the order-sensitive embedding check. This is solely a synthetic numerical test correction, not a physical tolerance change. No1µm/FP64 requirement was added to production.

No publication, speed, resource fit, H1 success or simulated/real transfer result is claimed. `result_template.json` intentionally contains null measurements. Treat unresolved actual-native-data, image integrity, operational split/mount security, Wan integration, hardware fit and trained model results as pending, not as completed just because source/protocol preparation is complete.
