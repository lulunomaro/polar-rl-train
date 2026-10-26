# Native full-attempt replay boundary and unused driver

Saved86B training prefixes cannot guarantee a complete attempt. The trace writes
24-control blocks; retention keeps the first complete block and latest two,
plus incomplete/current-failure protection. Normal closing therefore preserves
the initial0.24s and a late contiguous segment of at most0.48s, with a missing
middle. The index's old paths/SHA cannot reconstruct pruned raw. Failure
protection does not recover files already pruned. These are control-rate records,
not complete400Hz physical callback recordings.

The existing83B saved-only renderer explicitly renders48 controls using saved
root/q and USD kinematics. It neither evaluates the FINAL policy nor reintegrates
physics. Concatenating first24+last48 or repeating/interpolating them cannot be
called a full attempt. No saved raw or old replay was opened in this task.

The user's requested current mature native behavior consequently needs a new,
independent frozen-policy attempt, using the latest **formal CPU-qualified native
FINAL after86B closure**. It must be labelled a fresh test, not exact replay of
the training trajectory. PPO83B/H1 and Fudan demonstration footage are not native
SuperMimic policy outputs and cannot supply its actions or stand in for success.

## Source candidate delivered, not yet an admitted executable

`native_frozen_single_attempt_driver_candidate_v1.py` supplies:

- `make_frozen_native_policy(checkpoint, Policy, device)`: strict-loads only the
  saved native Pi and RunningNorm buffers, with the actual128/history10/goal73/
  6-action architecture. It constructs no SuperMimicLearner, WM, replay or
  optimizer; the caller supplies the qualified checkpoint object.
- `run_frozen_single_attempt(...)`: accepts an independently built fresh N1
  original SDK vec env, exact PartialFudan MDP, original H1Bridge.current/pack
  state reader and original geometry helper. It records one episode until the
  first original done/success or10s cap. The cap is explicitly censored, not
  complete success. No retry or best-case environment selection exists.

The driver is source/AST-reviewed only. It was not imported/executed. It does not
load files, construct an SDK scene, infer an actor or access a GPU in this task.
No actual small-N runtime admission is claimed. Source/AST findings and all
source hashes are in `reports/FULL_NATIVE_REPLAY_SOURCE_FEASIBILITY_AST_ACTUAL.json`.

## Minimal root entry wiring

Use an independent process/new output root after86B safely closes and its native
source is qualified. Reuse the original `build_env` factory, not training
`main`, `runner.learn`, `SuperMimicLearner.collect` or a20k bootstrap restore.
The existing configuration script may be loaded under a non-main run name solely
to obtain its SDK startup and build_env namespace; never call its training main.

The inspected build_env sets `cfg.scene.num_envs=args.num_envs`; it has no20k
assertion. The production worker and native `bridge.run` do hard-require20k,
so neither is a valid single-env launcher. A new entry must set fresh num_envs1,
the declared seed and original profiles, and replace the factory's environment
and cfg hooks exactly as the native worker does for H1Step270Env, aside from N1.
Keep2.5ms/TGS32/4, decimation4/100Hz, delay queue10000us, clip6, authored270mm
geometry, original command schedule and all hardware/closure/mimic/reset/success
conditions. Use original RslRlVecEnvWrapper(clip_actions=6), without a PPO runner
or PPO actor. Its native driver receives the same four-value step API.

The actual single-env factory/SDK/profile/reset must be checked before any actor
call. Native weights are batch independent, but that does not prove the complete
SDK accepts N1. If an inherited component has a hard N requirement, stop and
report the exact incompatibility. Do not reshape/tile20k D0-D7 tensors into N1.
Fresh profile initialization and one original reset are required; this is not
full-state or bitwise resumption of the training episode. Do not reset twice if
the original wrapper already resets. Record environment seed and fresh profile
readback in the root's source_identity/admission receipt.

One concrete source caveat: the inherited optional observer builds witness IDs
including1,2,3, which are invalid for N1 if its old `h1_capture` path is enabled.
The candidate never enables that path. It uses its own selected read-only hooks
and asserts h1_capture=false. Other small-N runtime compatibility remains pending.

Construct the reference/MDP exactly as native source: original H1GoalMdp with
original current-state pack (including the already-correct quaternion reorder),
the original reference artifact and PartialReferenceImitationMdp wrapper/config.
Verify actual ordered30 joint names equal the learned source order and verify
the canonical runtime objective hash against the formal native producer. A
fresh-N1 height/mapping/config mismatch is an incompatibility to report, not
something to normalize away silently. Do not call H1Bridge.before_action, step
or run: those require the training trace/save lifecycle. Only its exact current/
pack helpers are used as a raw sensor reader.

## Frozen policy and complete recording

Never use collect to fill history: actual collect calls pi.obs_norm.update,
pi.goal_norm.update and WM normalizer updates. The candidate copies only its pure
fresh/history-padding logic, computes exact obs/goal and uses saved native Pi
normalizers in eval/inference mode. It snapshots Pi state before and compares
all parameters/normalizers literally afterward. Original episode age controls
the request; it is not advanced manually. Previous action comes from the actual
pre-reset executed6, not a guessed raw network output.

The root must choose and report one action mode:

- `deterministic_native_mean`: no training collection exploration noise;
- `fixed_seed_original_collection_noise`: frozen Pi plus original0.1 Gaussian
  collection noise using a declared private seed.

Neither is called the original stochastic training path. Original native clamp20
and SDK clip6 remain. Do not add externally forced actions or trajectories.

Do not install H1ControlPrefixTrace: it saves preupdate checkpoints and enables
training reward flags. The candidate's read-only scene.update and termination
hooks save actual31-body poses/contact at each physical callback, and root13,
q30, raw/executed6, public age/request, done and original goal/event/callback
ticks for every completed control. Termination captures the final physical
state **before selected reset**, then disables capture before reset readbacks.
The first actual failure remains visible rather than showing a reset teleport
as movement. These hooks do not change original reset or termination decisions.

Outputs are complete sequential JSONL telemetry plus status, with original
success and stable callback ticks, no pruning. They can support the existing
renderer/camera pipeline using the actual whole sequence and timestamps. The
current48-frame renderer is not a drop-in consumer of this new schema; root
must make the narrow data/frame-count adaptation or record the original SDK
camera. No new player, fake trajectory or Fudan-video substitute is delivered.

SDK launch/admission, model load, actor execution, GPU/resource/budget transport,
actual video/render and final user delivery are pending root work. There were
no failed source checks in this task; no runtime success is inferred from AST.
All old frozen directories remain unchanged. This directory is frozen after its
complete file index is created and awaits root's ordinary source supplement.
