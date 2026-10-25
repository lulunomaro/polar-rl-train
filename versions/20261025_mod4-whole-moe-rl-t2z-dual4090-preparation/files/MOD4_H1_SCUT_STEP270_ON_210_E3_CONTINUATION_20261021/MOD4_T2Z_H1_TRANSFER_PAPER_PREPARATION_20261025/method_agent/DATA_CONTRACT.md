# Native H1 RGB/action/data split contract v1

Schema ID: `mod4.h1.t2z.raw.v1`. Proposed action module: `h1_temporal_action_adapter.py`. `contract_v1.py` validates this contract and produces an intermediate diagnostic bundle. **No real native H1 RGB dataset has been supplied or certified.** The provided fixture's `synthetic://` URIs and zero hashes cannot be used for training. `--require-real` rejects it. A real empty manifest rejects with `DATASET_MISSING`; absent/misclassified native frames reject rather than being replaced by generated imagery.

## Required collection and provenance

| Layer | Required fields / rule |
|---|---|
| dataset | schema, immutable dataset_id, explicit synthetic boolean, license/access provenance, collector source/config SHA, collection UTC, source host/path index |
| source checkpoints | SHA256 of policy and its producing source/config; root-supplied source67 H1 Adam790000 / `d1dd187177a1878f007b05da26e39c5ee101e937d2d86f0948dde1ffd37f062e` is provenance only, not the future completed H1 automatically |
| episode identity | global `source_episode_uuid`, fragment `episode_id`, simulator_run_id; vector env slot and reset_generation retained in audit; never assume permanent env slot implies fixed physics |
| physical grouping | opaque physical_group_id from actual configuration receipt; all trajectories sharing actual fixed parameters belong to the same group; grouping identity remains private to the splitter |
| physical receipt | private sidecar with robot/asset/contact mesh SHA, friction/material, mass/inertia/load, actuator/PD/limit/delay law, terrain geometry, solver settings, dt, randomization receipt and change times; unknown values marked unknown, not defaulted |
| dynamics clocks | integer sim_tick at physics boundary, physics_dt_ns=2,500,000; H1 decimation4, E3 decimation8; monotonic global simulation clock, wall-clock capture time and actual control issue index separately |
| frame | native RGB URI, byte count, SHA256, RGB dimensions/color space, camera_calibration_sha256, sim_tick, sim_time_ns, available_at_tick, exposure/render/encoding provenance |
| applied action | start_tick/end_tick half-open interval; target6 in declared order/units; issued_control_step; actual articulation-target readback provenance; exact interval coverage |
| auxiliary action audit | sampled raw6, actual clip6, requested processed target, actual queue issue/due/apply timing, actual articulation target, saturation flags and measured torques if available; keep each stage named; never invent missing stages |
| scoring truth | source recorded both-wheel crossing/top-surface partner/contact/footprint and recovery/reset/termination fields at actual physics/control timestamps; root/q/qd, geometry-derived height/edge metrics separately labeled |
| immutable origin | file path, bytes and SHA for every retained native file; no copying large raw/PT/video solely for Git; archive small metadata and content index; original artifacts remain at source |

H1 action order is `[left_crank,left_hip,right_crank,right_hip,left_wheel_spin,right_wheel_spin]`; units `[rad,rad,rad,rad,rad/s,rad/s]`. The contract accepts the **already processed and actually applied** target. It neither recomputes actuator processing nor changes CAD projection, PD, saturation or delay. Existing action code shows that application can occur at physics ticks; the actual collector must read at that same integration boundary and preserve reset ordering.

The small schema validator checks required fields, temporal coverage, native origin labels, numerical finiteness and split isolation. It does **not** currently decode image files or independently attest a collector's native origin claim, byte counts, contact truth or SHA correctness. An image file-content verification utility and actual collector receipt are required before training. Therefore the converter always declares `training_ready=false`, including for a structurally valid real manifest. Calling `--require-real` is a rejection check, not training authorization or a readiness certificate.

## Time alignment and conversion

Capture at exact20fps boundary ticks and choose T=4k+1 native frames (primary proposed T=41). The converter rejects missing frames, duplicate/nonmonotonic timestamps, camera changes, absent actions, target gaps/overlaps, nonfinite actions and resets in the clip. Do not interpolate contact, fill frames with generated video, concatenate across resets or treat post-reset zeros as natural recovery.

`pack_episode` outputs both exact ragged source interval references and a dense `[T,20,7]` tensor. Every future frame has twenty targets plus mask1. First-frame action rows are zeros with mask0 because that image is the decision anchor. The ordered positions encode timing; relative time boundaries are added by the new action module. A target held across a frame boundary appears in the relevant physics ticks of both adjacent intervals. This is lossless at the selected2.5ms application resolution, including E3's2.5 control periods per video interval.

For an existing log sampled only once every10ms, actual within-control queue changes are unknown. V1 must refuse to certify exact targets. A separate explicitly approximate command-held converter could be studied later, but must carry a different schema and must never be relabeled actual-application data. Existing source67 reports and retained selected NPZ names alone do not certify native RGB or per-tick applied-target coverage.

## Stable physical environment grouping

Use a canonical private configuration receipt after actual randomization/application, not merely requested seeds or nominal config. All physical/actuator/geometry factors held constant for the identification experiment define a group. A reset can stay in the same group if those factors are demonstrably unchanged; a resampling event gets a new group even on the same vector slot. A configuration change during a trajectory requires segmentation and a new latent lifecycle. An episode with uncertain change timing is excluded with its original data retained.

No group label or numeric factor value enters model tensors. The splitter may use those labels for stratification, group blocking and later plots; only the grouping relation is needed by the training latent table. At test time a fresh context handle maps support and query to the same opaque environment. It cannot look up the training latent nearest in numeric friction/mass space. All train latent tables are inaccessible to test initialization unless a separately preregistered initialization ablation declares an allowed pooled statistic.

## Split plan and leakage protections

Split physical groups before clipping, normalization, augmentation, data inspection by the model and hyperparameter search. Assign every source episode to exactly one partition. Train=fit; validation/test=support or query. Same-group support/query use disjoint source_episode_uuid values and disjoint native captures. Clips from one source episode stay in one role. Adjacent overlapping windows or reset fragments from the same source episode never become independent support/query. If recollections share the same underlying randomized configuration, they remain in the same physical group even with different seeds.

The validator rejects physical groups across train/validation/test, reused support/query source episodes, duplicated capture identity across roles, incomplete group support/query assignments and unassigned episodes. It does not infer physical equality from pixels or audit falsely assigned group labels; actual configuration receipts are required. Byte-identical RGB backgrounds are not automatically duplicated trajectories, so capture identity is checked rather than globally rejecting equal image hashes.

Validation is the only place to select learning rates, latent initialization, adaptation step count, thresholds and early stopping. Test K=1 uses the first prespecified support episode, K=2 the first two; all methods receive identical support/query ordering. Test queries are sealed until code/config/source and val-selected hyperparameters are frozen. The test latent optimizer receives support RGB+actions only. It cannot see query future frames, contact/success/reward, privileged state, numeric physical settings or test summary feedback. Query initial RGB is the only query observation at prediction time. Training normalization statistics use train actions only and are frozen for every split and method.

## Process-level data separation

The converter's combined bundle is for audit. It contains a `model` allowlist and a separate `evaluation` object; it must never be passed wholesale to a model. Engineering must export fit/support model views to training/adaptation namespace, query model views to prediction namespace and query truths/contact/state/config sidecars to an evaluator namespace with no adaptation-process access. A string URI is resolved to an image by the loader and never tokenized as text; numeric factor names in storage paths cannot become prompt features. Routing IDs, sample hashes and split labels are bookkeeping only, never embedded.

The synthetic counterfactual test changes query truth and future target URIs while proving the returned query model view is unchanged. This checks our view builder, not operating-system access control. A real training go/no-go audit must inspect the export/mounts and actual loader to ensure no later stage reintroduces forbidden fields. The main paper includes a deliberate leak-detection canary test, not a claim that schema alone guarantees privacy.

## Actual contact scoring and missingness

Success is evaluated using the original approved H1 physical criterion and its frozen production evaluator: both wheels actually clear the vertical edge, make top-surface contact/footprints, and satisfy the existing0.5s stable recovery rule. Preserve exact surface/mesh partner identity, wheel identity, contact timestamps and all reset/termination reasons. Net force, COM/robot peak height, signed edge clearance, visual contact impression or generated pixels cannot replace this truth. At20fps the0.5s interval spans ten frame intervals, but scoring uses the native recorded truth, not ten guessed image labels.

If only geometry reconstruction exists, label it `KINEMATIC_RECONSTRUCTION_NOT_CONTACT_TRUTH`. If contact partner/success/recovery timestamps are missing, contact accuracy and H1 success are **not evaluable**; report NA with reason. Unknown termination is not a success. Every exclusion, mismatch and reader/schema error is retained and indexed. A malformed reader is corrected against retained data rather than rerunning an old once or producing extra training.

## Real-world and delay caveat

Applied-target telemetry is usable only if available to the intended downstream system. For hidden action delay experiments, future application receipts are privileged information: command-conditioned candidates use only issued command/time schedules. A model given actual future apply timing is an offline conditional predictor and must be labeled accordingly. Real hardware would additionally need camera/actuator clock synchronization, latency receipts and independent top-contact instrumentation; none has been validated here. The visual study cannot claim sim-to-real solely because it holds out simulator parameters.
