# Whole-MoE transfer method and prospective paper protocol v1

ID: `MOD4_WHOLE_MOE_RL_T2Z_PROTOCOL_V1_20261025`. Status: prospective design, not a public preregistration, result or compute authorization. Human correction expands the objective from H1-only to the complete MoE/mixed-RL system. Here mixed RL refers to the existing expert RL + routing/task-override stack; no unverified new RL algorithm is assumed. Current main PPO inputs, PD, rewards, physical settings, optimizer state and budget remain unchanged.

## Method boundary

T2-z's prior-art core is a visual predictive model with per-environment latent, alternating shared-model/latent optimization and frozen-model support-only test adaptation. We transfer that principle to the full wheel-legged skill stack and its mixed policy clocks. A new policy-conditioned command/route interface is an explicit extension, not an exact reproduction of the upstream14D manipulation action interface. [Fixed primary paper](https://arxiv.org/html/2610.22364v1), [fixed source commit](https://github.com/T2-z-latent-optimization/T2-z/commit/c72f051f5cffcb1f372a32bc488df273556d39b9).

There is one environment z for one stable physical configuration, shared across E0/W35/H1/E2/E3 support/query tasks. Expert identity, task command, route proposal and policy-cohort identity are known controller conditions; they are not hidden physical labels and must not be conflated with environment group ID. A reset may retain the same physical group only if the actual physical receipt is unchanged. A physical resampling/change invalidates oldz. A different policy checkpoint is a controller/domain change and requires explicit registry/version treatment, not a silent new friction group.

Primary visual world model predicts native future RGB conditioned on initial RGB, z, a prespecified command/route candidate and the frozen expert-pool version. The expert policies execute their original observation interfaces; they are not fed z. The predictive model learns the consequences of the frozen closed-loop expert under the known command/route plan. Training and query episodes must actually execute the same precommitted high-level plan. Future expert actions, actual gate decisions and future application receipts are targets/audit information, not candidate inputs.

The implemented `command_route` features contain four declared issued command channels and five route-choice indicators, at backend physics resolution. They describe a plan available at the initial decision boundary. The plan must be committed before the first observation; recorded future gate decisions cannot be relabeled a plan. Individual expert inference remains50/100Hz and actual actions are held/applied through the original mechanics. A candidate route can constrain a macro/expert schedule while each selected expert remains closed-loop on its own original observations. This is a proposed policy-conditioned world model; useful prediction is not yet established.

An `applied_diagnostic` model receives the actual target6, selected expert onehot and recorded routing weights. It can diagnose response prediction conditional on executed control. It is retrospectively action-conditioned and **cannot** drive candidate selection using future closed-loop action/gate receipts. The executable bridge rejects this mode with `for_planning=true`. Hidden-delay experiments use only the command-conditioned branch; future apply timing is privileged even if a simulator log exposes it.

## Research branches and baseline preservation

| ID | Behavior | Research-input status |
|---|---|---|
| `MOE_ORIGINAL` | frozen actual original E0/W35 gate plus existing H1/E2/E3 task routing | original expert/gate inputs unchanged; mandatory baseline |
| `MOE_FIXED_EXPERT` | same expert pool, fixed expert in its matching task | original inputs; reveals routing-induced degradation |
| `WM_STANDARD_ROUTE` | pooled visual predictor of precommitted command/route candidates | same new task adapter/backbone asT2-z, noz |
| `WM_T2Z_ROUTE` | same predictor + environment latent, support-only adaptation | z conditions world model only; expert inputs unchanged |
| `ROUTE_SELECTOR_STANDARD/T2Z` | choose from identical precommitted candidate library using respective model | new external router/selector research branch, not the original gate |
| `NEW_GATE_PLUS_Z` | a separately trained gate reads z plus declared observations | **new gate input and training method**; optional future phase, never a hotpatch or original-baseline claim |
| `STATE_LATENT_INSPIRED` | small state dynamics/latent comparator | separate modality; not original visualT2-z reproduction |

The initial transferable claim is world-model prediction across the complete expert/task stack. Candidate selection is a later separately authorized execution study. Newgate+z is conditional on useful prediction and requires its own architecture/training/checkpoint/budget protocol. Do not jump from latent visualization to expert/gate policy improvement. Do not add z to current PPO observations or restart expert training under this preparation.

## Existing evidence that must remain negative/unqualified

Actual player manifest: gate148, H1/E3pair47, E2cohort52; no new five-way learned gate and no skill qualification. Source67 H1/E3 are more recent training provenance and not that player registry. Existing4090 small-curb V3 records nine matched cases at requested .65/.8/1.0 velocities; its three automatic cases select W35 for500controls and have zero expert switches. This is recorded routing occupancy, not proof of routing health or skill graduation. Zero jitter can coexist with collapse onto one expert. The older matched/series reports are retained too. No large NPZ was reopened or evaluation rerun here.

## Questions and hypotheses

1. Does one physical environment latent improve disjoint-query predictive error across **all five task families and transition suites**, compared with matched pooled/history-conditioned models?
2. Can support collected under one safe skill identify factors useful for another skill in the same physical environment? Prespecify within-skill versus cross-skill support/query, e.g. E0/W35support and H1/E2/E3query; never select support based on query outcome.
3. Does z improve true macro/task outcomes and worst-domain performance when used for candidate routing, without increasing failures, action discontinuities, pathological occupancy or expert-task degradation relative to original and fixed-expert baselines?
4. Is the accuracy/latency/memory tradeoff useful on actual target hardware? No4090 fit, real-time control or PPO/physics acceleration is assumed.

## Held-out design

Choose a single primary training backend: PhysX,2.5ms/TGS32/4, separate future isolated collection. This is a proposed experiment domain, not a claim all existing experts were trained with that same backend profile or a modification of current runs. The player MuJoCo0.5ms is a separate domain; do not concatenate it into the same training batch/group or reuse fixed20tick weights. A later backend-transfer experiment uses a separately trained/declared adapter or clock-domain model and independent outcomes.

Split by actual physical configuration **before** clipping, normalization, augmentation and hyperparameter search. Use train/validation/test groups with all source episodes and overlapping windows confined to one split/role. Held-out supports and queries are different source episodes under the same fixed physical configuration; one latent can be evaluated across skill labels. Fix K={1,2}, support task/order, query task count, controller-pool SHA, camera profile and initialization/action-library seeds before test access. No numeric friction/mass/PD/delay label, nearest-parameter lookup, test query future, success/contact/reward or task-result feedback updates testz.

Primary proposal: three paired training seeds; at least12held-out physical configurations each containing the five task families plus explicit transitions, with two prespecified support episodes and independent queries. Exact train/val counts, episode lengths and collection/GPU budgets remain pending actual data/resource approval and a pre-test power/precision review. These are design targets, not collected samples or permission. A small pilot can validate interface/observability but cannot silently replace the confirmatory dataset. Any domain/cohort/factor coverage gap is reported as a gap.

Separate tests: held-out in-range factor values, held-out factor combinations, outside-range conditions, cross-task support transfer, camera changes, backend changes and controller-cohort changes. Report them separately. H1/E3source67 replacingpair47 is a new policy-cohort test, not a mere filename refresh. Current expert qualifications are not inferred from their inclusion in the pool.

## Baselines, ablations and matching

Mandatory predictive comparators: Standard/no-z, alternating32D-z T2-z, same trained checkpoint with0adaptation steps, and matched history encoder; optional support-only LoRA with measured equal time envelope. Standard/T2-z get the same newly initialized action adapter/backbone init, train data exposure, spatial/temporal geometry and validation-search allowance. Trainable/new/total parameter counts include latent tables and encoder branches. All shared weights including task/action/context projectors freeze at test; only newz updates.

Ablations: K1/2; steps0/5/10/40; zdim8/32/64; same-env versus shuffled-env support; within-skill versus cross-skill support; shared physicalz versus explicitly skill-specificz; ordered physics targets/plans versus lossy last/mean baselines; gate-history-only versus physicalz; expert-ID/clock features; newgate+z only as a separately named branch. Privileged known-parameter oracle and future-applied diagnostic are upper bounds/diagnostics, never deployable baselines. Test-only hidden-label or future-action leakage invalidates that attempt.

Candidate execution comparators: original frozen MoE, fixed E0/W35/H1/E2/E3 per appropriate task, common random/common-library selector, StandardWMselector andT2-zWMselector. Use identical candidate schedules, command envelopes, task distribution, initial states, execution budgets and actual evaluator. Log candidate ranking before execution. No model score is counted as physical success. Preserve failures/timeouts and common denominators; unfinished tasks do not vanish from a macro average.

## Metrics for the whole system

Predictive physical endpoint uses frozen independently validated observers/readouts on query predictions: per-task state/trajectory error at0.1/0.5/1.0s, contact/event timing proxies where valid, and full native image metrics. Predefine task-wise normalization on validation; primary aggregate is equal-weight macro mean across five tasks **plus a separately reported transition suite**, never pooled frames dominated by easyE0. Also report worst task × physical-domain score and missing/observer-failure rates. If no valid physical observer exists, physical accuracy is not evaluable; pixel quality alone is insufficient.

Execution outcomes: original task-specific success/termination, speed/yaw tracking, tilt/fall/reset rates; W35 original terrain outcome; H1 actual both-wheel270mm crossing plus actual top-surface contact/footprint and0.5s stable recovery; E2original signed spin/motion criteria; E3original recovery criteria. Exact old evaluators remain frozen and indexed; this proposal does not invent new qualification thresholds. Every task's count/status is visible, including unqualified experts and unrun tests.

Routing outcomes: selected-expert occupancy, coverage/collapse, switches/sec, dwell-time distribution, alternating switch bursts/chatter, missed necessary transitions, switch timing relative to actual events, actual target6 discontinuity, torque/saturation envelopes,50/100Hz inference/hold violations, and recovery after transitions. Low switch count is not automatically stability; high occupancy of W35 is not success. Compare mixed-mode performance to the identical fixed expert on the same task to quantify routing-associated degradation. If expert weights remain frozen, this is functional degradation under routing/context, not parameter forgetting.

Actual contact comes from the native backend's independently logged partner/surface/footprint evaluator. Generated video has no actual collision partner. Peak COM/wheel height or visual contact can be descriptive but cannot certify H1 or the whole MoE. A contact-supervised head/observer is an additional trained component with its own split/labels; report that supervision. The MuJoCo GUI, whose physics/contact domain differs from PhysX, cannot stand in for PhysX ground truth or real hardware.

## Statistics, resources and publication scope

The independent unit is physical configuration, with task and episode nested inside; frames/windows/vector slots are not independent replicates. Average within group/task first; report paired effects, seed-specific results and95% group-cluster bootstrap CIs with10,000resamples and a frozen seed, plus hierarchical seed/group sensitivity. Use the same paired seeds/data ordering/candidates; expose all per-group/task results and failed/missing cases. One primary macro prediction endpoint is confirmatory; secondary/ablation/transition endpoints are labeled exploratory or receive a preregistered multiplicity family. No acceptance or significance promise.

Match both data/update exposure and actual GPU-hour/latency envelopes; report backward/microbatch counts, trainable params, all failed attempts, per-device peak VRAM, CPU/RAM/I/O, offload/sharding and precision. Split cold-load/video decode/VAE/z-backward/query denoise/write timings from warm-resident latency. Two24GB cards do not automatically pool memory. The prior H1-only2GPU-hour proposal is **not** an approved whole-MoE budget. Upstream H200 timings do not predict4090 costs or current PPO throughput. No training has run in this package.

Potential contribution is the whole-stack causal interface, shared physical latent across expert/task/clock domains, and measured routing/robustness outcomes. The upstream latent optimization principle remains prior art. Broader related-work/novelty review is pending before a manuscript claims novelty. Simulator held-out results support simulation claims only; real-world transfer requires independent hardware data, clock synchronization, actual contact instrumentation, baselines and authorization. Paper acceptance, whole-MoE graduation and real-time deployment are not promised.
