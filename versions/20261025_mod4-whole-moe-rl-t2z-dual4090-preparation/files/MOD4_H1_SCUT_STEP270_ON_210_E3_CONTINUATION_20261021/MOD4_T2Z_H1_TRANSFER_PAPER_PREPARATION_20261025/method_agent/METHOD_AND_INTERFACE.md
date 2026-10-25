# Proposed H1 visual transfer and its action interface

Protocol ID: `H1_VISUAL_T2Z_TRANSFER_PROTOCOL_V1_20261025`. This is a prospective method, not a result or new production gate. Existing H1 work completes first. H1 still requires both wheels to truly cross the 270mm vertical step and make actual top-surface contact with stable recovery for 0.5s.

The fixed T2-z source trains an action-conditioned visual world model and per-environment latent by alternating updates; at test time shared weights are frozen and only a new latent is fitted from observed interactions. We retain this distinction. Its manipulation action representation cannot be transferred by loading the existing H1 PPO checkpoint or by zero-padding a six-dimensional wheel/leg command to fourteen dimensions. The new visual task requires native H1 RGB/action data and H1-specific fine-tuning. [Paper](https://arxiv.org/html/2610.22364v1), [task configuration](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/configs/ours/sim_pushbox_friction.yaml).

## 1. Primary research pipeline

1. Freeze the chosen completed H1 policy/checkpoint and collection protocol. Define environment configurations, capture native simulator RGB and actual target application logs in a separate, authorized collection stage. No source/PD/reward changes are needed for the predictive-model comparison.
2. Split by physical configuration before extracting clips. Train/validation/test group membership is immutable. Learn action normalization only from the train split. Keep a privileged configuration sidecar for grouping and evaluation, never for the latent optimizer.
3. Initialize the visual backbone from the documented pretrained resources; initialize the new H1 action module. Train the standard visual world model and the T2-z variant under the same H1 interface, data and comparison budget. Alternate shared visual/action/context weights with train-environment latents in the T2-z variant.
4. For an unseen held-out physical group, initialize a new 32D latent with a prespecified seed and initialization rule. Freeze **all** shared weights, including the new H1 action module, normalizers, VAE and context projectors. Optimize only the new latent on K=1 or K=2 observed, completed support episodes. A support episode contains actual interaction observations, not generated frames.
5. Lock the latent and run disjoint query episodes/candidate predictions. The model gets initial RGB and causally available planned actions; the isolated scorer gets native query RGB, contact and state ground truth after prediction. No query target, success/reward or numeric physical label affects adaptation, hyperparameters, early stopping or latent initialization.
6. The first claim is predictive transfer. Closed-loop action selection requires a later explicitly bounded execution study with a common candidate set and actual contact outcome. Offline visual fit alone cannot establish H1 skill improvement, PPO efficiency, 100Hz control, safety or sim-to-real transfer.

## 2. New action representation

Source order is read from the preserved local `mod4_task.py`: `left_crank`, `left_hip`, `right_crank`, `right_hip`, `left_wheel_spin`, `right_wheel_spin`. The first four are **actual applied leg position targets in radians**; the last two are **actual applied wheel velocity targets in radians/second**. Raw sampled PPO action, clip6 action, scaled/default-offset requested target, delayed queue target, actual articulation target and measured actuator torque are different quantities. The input here is the articulation target actually applied immediately before integration; other stages belong in the audit sidecar.

Time is represented by integer physics ticks, dt=2.5ms. Frames use native 20fps boundary capture, so each future RGB interval contains exactly twenty physics ticks. H1 control=100Hz/decimation4 gives five issue opportunities per RGB interval. E3 control=50Hz/decimation8 gives alternating boundary relationships, not an integer number of controls per frame. A target can change within a control interval because the selected delayed queue applies on physics ticks. Thus the converter preserves the full piecewise sequence and also packs twenty ordered applied targets per interval. It does not average, select the last target, repeat a sampled action, or infer timing from array index alone.

For frames at ticks t0,t1,...,t40, action item j>0 contains the target applied on each physics interval `[t(j-1)+k,t(j-1)+k+1)`, k=0..19. Item0 is an explicit zero/mask0 initial-observation anchor. Native observations at t(j) are consequences of intervals ending at that boundary; pre-reset values must never be confused with post-reset frames. V1 rejects resets inside a clip and does not pad missing frames. Nonzero camera exposure/rolling-shutter latency needs a separately versioned capture contract, not guessed alignment.

## 3. Actual Wan action encoder connection

The supplied `H1TemporalActionEncoder` consumes a **new tensor** `[B,T,20,7]`: six train-normalized target channels plus a validity mask. It adds fixed relative start/end timing inside the frame, flattens all twenty ordered physics rows, and uses a learned MLP to create one frame embedding. A second learned branch creates the context embedding. Four frame embeddings feed a learned modulation branch. `encode_ti2v2` returns:

| Output | Shape | Meaning |
|---|---|---|
| context | `[B,T,D]` | per-video-frame action context |
| modulation | `[B,(T+3)/4,D]` for T=4k+1 | causal VAE latent action conditioning |

The three initial anchor prefixes reproduce the fixed upstream grouping convention. A future latent covers four video intervals = 80 physics ticks = 0.2s = twenty H1 control periods, with all targets represented. The width D is read from `old.action_mlp1[0].out_features` at integration; the synthetic test uses D=32 solely to exercise shapes. The architecture is our proposed H1 transfer layer, not upstream code or a proven trained interface. [Upstream encoder](https://github.com/T2-z-latent-optimization/T2-z/blob/c72f051f5cffcb1f372a32bc488df273556d39b9/wan_video_action/models/wan_video_action_encoder.py).

All temporal/context/modulation action weights are newly initialized. Do not load the upstream fourteen-channel action weights into this module. Load the documented backbone/context weights through a reviewed key allowlist, explicitly report every skipped/new/unexpected key, then install this module before optimizer construction. An H1 checkpoint must save a versioned adapter/config/train-stat hash and load with strict matching. A manipulation checkpoint's missing action keys are expected only during the declared task-transfer initialization; missing keys must not be silently accepted in a resumed H1 run.

The standard visual baseline uses the identical new action module and initialization seed, so improvements cannot be attributed to an interface available only to T2-z. Compare parameter counts including latent tables and new projectors. At test-time the new action module is frozen, even though gradients pass through it to z.

## 4. Deliberate integration gaps

The current converter is a proposed interchange format. It is not accepted directly by upstream `LoadCobotAction`, which assumes manipulation action files and normalization. The engineering integration must: replace that special operator with a native H1 loader; collate the packed tensor without flattening to14D; pass it unchanged to adaln `encode_ti2v2`; install the new module; check latent/video temporal alignment on the actual Wan pipeline; filter checkpoint initialization keys; freeze the correct modules during z adaptation; and place evaluator truth outside the model process's mount. None of those GPU/Wan integration checks has run here. The helper `replace_action_encoder` only wires the module at the object level.

CPU tests demonstrate shape consistency, ordered-action sensitivity, gradients through the new action layer and rejection of missing/anchor actions. They do not establish full-pipeline compatibility, 24GB fit, visual accuracy, training convergence or useful z identification. The 20fps/41-frame starting geometry is a proposed controlled transfer choice; it may miss fast impacts. Contact metrics therefore retain native physics timing. Changing fps/clip length later is a preregistered ablation with a versioned adapter, not a hidden rescue of failed primary results.

## 5. Causal action availability and scope

For offline response prediction, actual applied targets can condition the trajectory if that telemetry is available to the intended user. This estimates dynamics *conditional on executed actions*. It does not by itself solve unobserved action delay. For candidate selection the future applied-target readback does not yet exist. Primary candidate studies must hold the action pipeline fixed and known so future issue targets map deterministically to applied targets; use only that known schedule. If delay is itself hidden, create a separately labeled **command-conditioned** model that receives issue-time commands and predicts the delay's consequences. Never feed a query's future application receipt to a selector and call the result deployable adaptation.

Similarly, simulator privileged root/q/contact truth is a scoring signal in the visual study, not the visual adaptation input. A state-driven variant, contact-supervised visual variant, camera-only physical inference, and a camera+proprioception variant are distinct experiments. Sim-to-real currently means a motivation only. No real H1 hardware data, camera calibration transfer or hardware execution has been validated.

## 6. Separate lightweight state-inspired comparator

Name it `H1_STATE_LATENT_INSPIRED`, not visual T2-z replication. Use ≤1M-parameter state transition models with pooled/no-z, alternating32D-z, and a budget-matched history encoder; optional known-parameter oracle is an offline upper bound. Train/test are independently blocked by the same physical groups and source episodes. States, executed targets and actual contact may be used only under that explicitly state-based modality. One-step/100ms/500ms state and contact timing error are its outcomes. It can test whether the environment is identifiable at all and whether visual scale is justified. It is not evidence that the Wan model is trained or that visual T2-z can run at100Hz. No state model was trained here.
