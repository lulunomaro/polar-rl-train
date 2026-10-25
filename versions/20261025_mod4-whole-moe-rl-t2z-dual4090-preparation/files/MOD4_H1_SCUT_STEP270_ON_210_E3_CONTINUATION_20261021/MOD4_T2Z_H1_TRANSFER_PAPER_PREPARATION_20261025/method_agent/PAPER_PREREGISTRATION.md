# Prospective research protocol: H1 visual environment-latent transfer

Protocol status: **DESIGN_PREPARATION_NOT_REGISTERED_NOT_RUN**. Version1 dated2026-10-25. Preregistration here means freezing a prospective local protocol before test access, not a public registration, accepted paper or authorized compute allocation. The engineering/dataset manifest and exact budget must be reviewed and frozen by root before the actual stage. Amendments append a new version with reason; failed primary results remain failed.

## Research question and intended contribution

Does support-only optimization of an unsupervised environment latent improve an H1 action-conditioned video predictor's response to unseen physical conditions, especially the timing/location relationship of takeoff, edge clearance and landing, over matched no-latent or history-conditioned predictors?

This applies the T2-z optimization principle to wheel-legged step contact dynamics using an explicit physics-resolution action adapter. The upstream visual objective and adaptation concept are prior art, not our novelty. The proposed new contributions would be the H1 task/interface, the causally correct issued-versus-applied action analysis, configuration-held-out benchmark and evidence about limits in fast contact dynamics. This is an investigation, not a claim that those contributions are already demonstrated. Related-work/novelty review beyond the fixed upstream source is still required before a manuscript claims novelty. [Primary method paper](https://arxiv.org/html/2610.22364v1).

The current source67 timing/crank-saturation problem is not known to be caused by hidden physics. Current H1 does not yet satisfy its270mm graduation criterion. The experiment therefore does not promise to fix today's failure; it begins after the existing H1 completion and actual collection/modeling authorization. An unsuccessful adaptation result is scientifically informative if the interface, support identifiability and controls are sound.

## Hypotheses

- H1-prediction: on unseen physical groups, fixed32D-z adaptation using K=1 support episode reduces query wheel/edge trajectory error relative to the matched standard visual model. K=2 is a prespecified secondary endpoint.
- H2-specificity: true same-group support is more useful than support from a different held-out group and than an unadapted z. Query-error reduction is not merely support overfitting.
- H3-contact: if a separately authorized candidate-execution study occurs, action selection using adapted predictions improves actual both-wheel270mm top-contact/recovery success under the same candidate library and execution budget. This hypothesis cannot be tested by generated video alone.
- H4-efficiency: latent adaptation provides a better measured error/latency/memory tradeoff than a matched history encoder or weight adaptation; no100Hz or4090 advantage is assumed.

## Dataset and held-out factors

Primary simulation factor family: wheel/step-ground friction and inertial load variation within a separately frozen safe collection envelope. Geometry stays the true270mm step and the approved H1 mechanics/solver remain unchanged. Factors are recorded for grouping/scoring but not supplied to the unsupervised method. Do not change physics to create a paper result without the separately approved collection plan. PD, action limits, action processing and nominal pipeline timing are fixed in this primary study.

Proposed confirmatory design, subject to actual data availability and explicit collection budget: 12train,6validation,12test **physical configurations**, six independent source episodes per group. Each held-out group has two support and four query episodes. TestK=1 uses support#1, K=2 uses#1+#2, and all four queries are disjoint from both. Source episode duration, action library and sampling schedule are frozen after a separate pilot that does not touch confirmatory test groups. T=41/20fps clips can be extracted from longer source episodes; every overlapping clip stays in the source episode's role. These180source episodes are a proposed design target, not collected data, a sample-size guarantee or a current rollout authorization. A smaller4/2/4-group pilot is descriptive only and cannot silently replace the confirmatory design.

Use a deterministic opaque group list generated before collection with its SHA and explicit train/val/test assignment. The group list must distinguish (a) held-out values within the training factor range, (b) held-out combinations of observed marginal factors, and (c) outside-range extrapolation. Primary endpoint uses(a); (b)/(c) are separately labeled tests with their own frozen lists and uncertainty. Sample/train/val/test configuration equality is verified from actual receipts, not just seeds. No frame-level random split.

Secondary factor studies—unknown delay, contact material, camera/background, step height or damaged actuator—are distinct protocols. In particular hidden-delay study uses command-conditioned input or explicitly labels actual-future-application input as privileged. E3 is not mixed into the primary H1 training/test set; transferring across100Hz and50Hz is a separately labeled clock/domain ablation. Simulated randomization is not real hardware transfer.

## Mandatory visual comparisons

| Method ID | Shared model and interface | Test adaptation/input |
|---|---|---|
| `VIS_STANDARD_H1` | same initialized visual backbone + same new H1 action adapter; pooled H1 training | none; initial RGB and query action only |
| `VIS_T2Z_H1` | same backbone/action adapter +32D environment branch; alternating world-model/z training | freeze every shared weight, support-only z updates |
| `VIS_T2Z_H1_S0` | exact trained T2-z checkpoint | fresh z, zero adaptation steps; same query input |
| `VIS_HISTORY_H1` | same backbone/action interface, support RGB/action encoder conditioning | amortized support context; no query targets |

Report total/trainable parameters and pretraining sources separately. The standard and T2-z variants use paired seeds, identical train episodes, train augmentation, per-method data exposure and independent validation selection allowances. Count latent-table parameters, projectors and history encoders. A trainable branch may make exact parameter equality impossible; report both matched-backbone and a parameter-matched sensitivity control. Never compare a pretrained visual model to a newly initialized small state MLP as if modality/scale were matched.

Useful extended baselines after feasibility: (1) `VIS_LORA_TTA_H1`, same H1 visual model with support-only adaptation of a declared low-rank subset, matched update/time envelope; (2) `VIS_NUMERIC_ORACLE_H1`, true factor labels given at train/test as a privileged upper bound, clearly separated from unsupervised/deployable methods. An oracle is not an allowed test-z initializer or input. The history encoder must be trained for the same support distribution and use the same K; it cannot see more episodes/actions than the optimized latent.

## Separate state comparison

`STATE_POOLED`, `STATE_LATENT32` and `STATE_HISTORY` use the same small state model family, ≤1M parameters, the same state/action/contact fields and the same group/source-episode splits. They predict1step/100ms/500ms state/contact outcomes. If state performs well and visual fails, that may indicate visual observability/model/interface limits, not proof that T2-z's principle fails. If all state and visual adaptation variants fail despite correct interfaces, support identifiability or hidden-factor relevance is a plausible explanation requiring explicit diagnostic evidence. No state method is called an original visual T2-z reproduction.

## Ablations and negative controls

Prespecified: K={1,2}; z adaptationS={0,5,10,40}; zdim={8,32,64}; same-group versus shuffled-group support; alternating training versus a joint-update variant; full ordered20tick action versus last-target/mean-target ablations; native20fps versus a separately versioned higher-fps observer if feasible. The proposed primary setting remains32D/K1/S40/native20fps/full action. Hyperparameters other than these chosen on validation are logged, not swept on test. Last/mean-target ablations are deliberately approximate comparisons, never relabeled actual lossless data.

Run ablations in a frozen priority order under the approved finite budget. If budget is exhausted, unrun cells remain `NOT_RUN_BUDGET` rather than using a cheaper method's saved compute to extend only T2-z. A shuffled-support control uses held-out support only and cannot borrow another query trajectory or test outcome. Reset z per physical group, per method/seed, and per independent query evaluation session; no cross-group latent/optimizer state carryover.

## Outcomes and valid physical claims

Primary predictive endpoint: mean query wheel/step-edge trajectory location error, normalized by fixed image width, at0.1s/0.5s/1.0s, aggregated equally over held-out groups. A frozen wheel/edge observer must first be validated on native validation RGB with independently retained geometry labels and prespecified error/missingness bounds. The primary scalar is the arithmetic mean of the three normalized horizon errors; publish all horizons. If that observer cannot be validated, the physical endpoint is `NOT_EVALUABLE_OBSERVER`; pixel metrics alone cannot be relabeled the primary physical result.

Secondary: PSNR/SSIM and, only if the required frozen feature model is available under approved downloads, perceptual distance; whole-image and fixed robot/edge ROI results; support loss versus disjoint-query error; takeoff/apex/landing timing proxies; uncertainty/calibration; nonfinite predictions and missing-object/observer-failure rates. Missing observer detections must not be dropped selectively. Publish an intention-to-predict count, conditional error on valid detections, detection failure rate and a prespecified bounded failure-penalty sensitivity analysis. Freeze those bounds on validation before test access.

Generated RGB has no actual collision partner or PhysX contact. A visual contact proxy requires a separately validated frozen observer; compare proxy predictions against native logged contact and report false positives/misses and timing error with the proxy qualification. A contact-supervised auxiliary head is a different method/ablation because it adds privileged training labels. Never call a generated wheel-on-top image physical success. The authorized candidate-execution outcome, if run, is the **actual** existing both-wheel crossing + actual top-surface contact/footprint +0.5s stable recovery event. Use the frozen original evaluator and all failures/reset reasons; peak height is descriptive only.

## Statistical unit and uncertainty

Use three paired training seeds. A physical configuration is the independent primary unit; average query episodes and clips within a group before comparing methods. Repeated windows, video frames, seeds or vector-env slots do not inflate the group sample count. Report per-group and per-seed raw outcomes with a long-form table. Report paired mean/median differences and95% configuration-cluster bootstrap CIs with10,000 resamples and a frozen bootstrap seed. Also show seed-specific effects and a hierarchical seed/group sensitivity interval; three training seeds alone do not estimate all optimization uncertainty.

For H1 actual-success comparisons, pair configurations, initial-state/action-library seeds and candidate budgets where feasible; report successes/total, paired difference with group-cluster CI, and all exclusions. Do not treat generated candidates as successful trials or create independent denominators from multiple frames of one landing. PrimaryH1-prediction is the only confirmatory hypothesis. Secondary tests/ablations are labeled exploratory or receive an explicit multiplicity correction family chosen before test unsealing. No significance claim from overlapping/selected examples. No posthoc power claim; revise sample sizes only before test access with an appended protocol version.

## Compute/data matching and measurement

Use paired backbone initializations and the same H1 action adapter, precision, spatial resolution, T=41 clip geometry, data exposure/augmentation and common validation search allowance. Count model-update microbatches, latent-update microbatches, backward passes, trainable parameters, total GPU-hours, peak reserved/allocated VRAM, CPU/RAM/disk/I/O, checkpointing/offload/sharding configuration and failed attempts. Match offline GPU-hour caps **and** report optimizer/data exposure; unequal work per step makes step counts alone misleading. A secondary equal-update analysis may be reported separately.

At test time fixK and number/length of query candidates. Report adaptation-only and per-query latency separately, including p50/p95 over groups; also report cold-load, video decode, VAE encode/decode, z-backward, denoising and disk write components. Main end-to-end includes everything required for the intended deployment; warm resident measurements are additional. Match a finite wall-time/VRAM envelope across adaptation baselines and retain timeout/OOM failures in the denominator. No rescaling of the upstream H200 timing to a4090 estimate. Two24GB cards are not an automatic48GB memory pool; actual memory must be measured at the approved host72 stage.

The paper's common offline2H200×24h reference is unrelated to the current PPO budget; its reported18.09s includes adaptation and five queries, not adaptation alone. These are source clarifications, not this study's measurements. No hardware speed, PPO sample efficiency or physics throughput claim is permitted without a separate matching actual measurement.

## Candidate execution and sim-to-real scope

No candidate rollout runs under this preparation. Before H3, freeze candidate library, commands/durations/targets, common action limits, selection rule, scores, support collection procedure, episode horizon, reset/stop rules and execution budget. All candidates must be available to all selectors; model-predicted reward/success cannot be judged against a goal unavailable to comparators. Retain open-loop random/common-library and standard-model selectors. A model-ranked success is not counted until that candidate is actually executed and satisfies true contact recovery. Model errors cannot lower existing mechanics/termination/closure handling or production safety rules.

Simulation evidence supports simulated held-out dynamics claims only. Real-world claims require independently authorized hardware experiments, synchronized native camera/control telemetry, calibrated geometry/contact truth, a hardware baseline and explicit transfer accounting. Until then write “potential sim-to-real relevance,” not “sim-to-real demonstrated.” Publication venue fit and acceptance cannot be promised; a future manuscript must report negative/no-go results and the exact scope actually measured.
