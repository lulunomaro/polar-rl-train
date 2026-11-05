# E3 Fudan-sequence PPO native worker V1

Status: new worker source and task/owner interface only. A source syntax check is
not SDK construction, GPU training, a native zero-PT test, or an E3 skill result.
No old worker/once entry is reused. No SM eight-expert work is resumed.

## Files and launch interface

- `worker_fudan_sequence_ppo_native_v1.py`: stdlib-only on import; execute only from
  the original parent's admitted new E3 task, with `--job-root JOB_ROOT`.
- The parent stages its new task runtime, owner, source manifest and GO. This
  worker neither creates GO nor opens/updates canonical time/accounting state.
- Worker kind: `MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1`.
- The worker creates `JOB_ROOT/production` exactly once; an existing directory is
  an error, not a resume/replay request.

## Installed dependencies

Use the existing E3 constructor and its complete shared library/assets, not just
an incomplete E3-only source directory. Search paths, in order:

```
JOB_ROOT/worker_sources
JOB_ROOT/lib
JOB_ROOT/runtime/isaac/mod4
JOB_ROOT/runtime
JOB_ROOT/producer/lib
JOB_ROOT
```

The install manifest must include these exact basenames:

```
worker_fudan_sequence_ppo_native_v1.py
fudan_seq_ppo.py
e3_fudan_task_runtime_v1.py
app_close_semantics_v6.py
resume_runtime_contracts_v3.py
pose_cache_runtime_adapter_v4.py
train_mod4v1_e3.py
fudan_task_pose.json
```

`app_close_semantics_v6.py` supplies the pinned original SimulationApp binding and
bounded pose-event recorder only. Its SM-specific FINAL/count/close validator is
not used. `resume_runtime_contracts_v3.py` is its required import dependency.
The parent must include all the other constructor/shared-library imports in its
existing source closure. No SM learner, bridge, world model or vendor is imported
by this new worker.

## TASK / GO / admission / manifest

TASK fields (explicit old-key aliases are supported, not heuristic matching):

| Field | Meaning |
|---|---|
| `kind`, `role` | exact worker kind; role `E3` |
| `run` or `run_id` | same run in TASK, GO and admission |
| `gpu_uuid` or `GPU_UUID` | exact actual CUDA_VISIBLE_DEVICES UUID |
| `owner_parent_pid` | actual `os.getppid()` |
| `root_admission_sha256` or `root_admission_SHA` | admission bytes SHA |
| `install_manifest_sha256` or `manifest_SHA` | installed manifest bytes SHA |
| `inherited_lock_fds` | four inherited FDs; may instead come from admission |
| `num_envs`, `steps_per_env`, `max_iterations` | 4096, 48, 300 |
| `seed` | new branch seed |
| `teacher` or `teacher_path` | exact 1cd mother path below |
| `teacher_sha256` or `teacher_SHA`, `teacher_bytes`, `teacher_iter` | exact pins below |
| `asset_sha256` or `asset_SHA`, `contract_sha256` or `contract_SHA` | exact new-plant pins below |
| `runtime_entry` | optional; default `runtime/isaac/mod4/train_mod4v1_e3.py` |
| `original_run_manifest` | optional; default `original_run_manifest.json` |
| `asset_usd` | optional; default `runtime/assets/robot.usd` |

GO includes the same kind/role/run/GPU and `canonical_binding`, plus:

```
task_sha256 (or task_SHA)
root_admission_sha256 (or root_admission_SHA)
install_manifest_sha256 (or manifest_SHA)
learning_started_epoch
save_deadline_epoch (or save_deadline) = learning_started_epoch + 3600
nominal_end_epoch (or nominal_end) = learning_started_epoch + 3900
max_parent_seconds = 3900
shutdown_headroom_seconds = 300
```

Admission includes role/run/GPU, `canonical_binding`, the four FDs, and true
`actual_original_authority_EX_private_GPU_EX_finite_SH` /
`original_canonical_owner_admitted`. If parent PID fields are included they must
match the actual parent. The worker does not call flock or release inherited FDs.
It joins each child's FD inode to the same-number parent FD and reads its actual
`/proc/self/fdinfo` FLOCK mode. The four ordered lock basenames are:

```
native_floor_supervisor.lock            EX / WRITE
autonomy_controller.lock                EX / WRITE
three_expert_v2_GPU_UUID.lock            EX / WRITE
finite_environment_validation.lock      SH / READ
```

Replace `GPU_UUID` in the third name with the complete real UUID string.

Manifest JSON uses `files: [{path, sha256, bytes}]`; exact old aliases
`{relative, SHA, bytes}` also work. All files must resolve within JOB_ROOT.
Do not list mother/model PT/PTH/CKPT/ONNX/DATA files: the manifest validator never
reads model bytes. Stage the pose JSON and original manifest/asset/contract
source bindings as ordinary non-model inputs.

## Immutable mother and new branch

```
source: /home/lc01/Zonglin Li/zonglin2/tasks/MOD4_E3_PPO50_GAS400_2610v97/e3/adaptation/final_valid_update87.pt
bytes: 14715029
SHA256: 1cd99995d6b88d373df4c8fe869bb16321db561c7d23b00722de22ddba7c84b8
source iter: 43090
asset SHA256: 2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3
contract SHA256: bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755
```

Exactly one mother physical read/hash/CPU decode, retained whole in memory. Only
complete `mlp.0/2/4/6.{weight,bias}` actor/critic maps are passed to warm_start.
Known old exploration keys are recorded and ignored; unknown normalizer/model
keys fail. No old optimizer, iteration or 20k-environment DR slice is restored.
The new encoder and two Adam states/counts are new; latent input columns are zero
on actor/critic warm start. Initialization is forked off original DR RNG streams.
New policy sampling/minibatch RNG is already owned by the core generator.

## Native constructor and collection timing

```
non-main runpy(train_mod4v1_e3.py)  # starts original App, imports E3 class
import new task runtime
install_before_build()           # patch the already-imported class/module
build_env()                      # original fresh 4096-env constructor only
bind_after_build(env, JOB_ROOT)
install per-instance pose-cache adapter + fresh-nominal guard
one explicit env.reset()
use returned raw35 / privileged38
```

Never call the old main, runner, PPO, restore helper or PT read-rewrite save
contracts. The existing 2.5ms/TGS32/4 plant, 20ms action clock, 100Hz feedback,
10mm closure reset, .01rad mimic reset, physical action clip6 and all D0-D7
randomization/queues are asserted unchanged.

History is five actual noisy raw35 samples old-to-new. A reset/done row repeats
the same already-returned sample five times; there is no new sensor/noise draw.
Rollouts store unclipped Gaussian actions/log probabilities while the original
environment receives their clip[-6,6]. Body velocity target is physical m/s,
scaled x3 exactly once inside the existing core. Rewards are unadjusted; core
preserves the upstream pre-step-value timeout bootstrap and done-cut GAE.

Stage1 is the parent's new **local engineering low-rise curriculum**, not an
institution-official get-up task and not independent acceptance evidence:
original falls 0..11, normal12, low-rise13..25; native xyzw root quaternion;
low rootz .1781; .25 commanded height; 8s request and .23m / signed gravity /
speed / omega / .5s / two-wheel last-substep force1N / chassis<1N criterion.
Original falls keep their original request/predicate. The task summary is only
a training description. Whole-leg-same-end video target is explicitly false.

## Saving and deadlines

Maximum 300 new iterations, T48/N4096. Save every 25 completed new updates and
at deadline/parent stop. A 60s or 1.5x-last-update guard prevents starting the
next update too close to the save deadline; the parent retains its hard end /
actual-wait authority. Honor both STOP_AFTER_SAVE.json and STOP_AFTER_SAVE.
A partial collected rollout is stored rather than silently dropped or called
a learner update.

Each unique new save is fsynced/renamed, then hashed in one read of that OWN new
file. `FDN_LATEST_COMPLETE_SAVE.json` records its bytes/SHA and true counters.
No new save is reopened with torch.load. Required state: model, both Adam,
learner sampling/minibatch generator, Python/NumPy/Torch CPU/all-CUDA RNG,
actual root/joints, episode tensors, original noisy observations/history,
recovery/task phase, private command RNG/cache, every D0-D7 component state,
D0 baselines/current actuator scales, COM/PD/spring/gas adapter caches,
physical delay queue, sensor/feedback delay caches, contact accumulator/history
and physics/feedback counters. Missing required fields or nonfinite state makes
the save fail; no full=True fallback exists. Opaque SDK/warp handles and
historical diagnostic event lists are not checkpoint state. This typed fullstate
is explicitly **not** bitwise PhysX continuation.

`FDN_NATIVE_UPDATE.json` is overwritten after each actual two-phase update.
It gives new learner and actual native/control/physics/feedback counters,
pre-reset termination/height/credit summaries, and the parent task description.
No training counter is an independent skill pass rate.

## Exact FINAL and actual-wait semantics

`production/FDN_FINAL.json` contains:

- `kind/run/role/worker_pid/parent_pid/resource_binding`;
- `final`, `complete_save`, `latest_complete_save`, `save_count`, `stop_reason`;
- `counters`: updates / policy_optimizer_steps / encoder_optimizer_steps /
  transitions_seen (new branch only);
- `native_counters`: actual_native_policy_steps / actual_native_transitions /
  physical_callbacks / feedback_callbacks / termination_computations /
  termination_counts / pre_reset_credit_events / pre_reset_height_*;
- `error`, `close_errors`, `source_checkpoint`, `task_summary`;
- `parent_actual_wait_still_required=True`, `skill_improvement_claim=False`,
  `native_PhysX_bitwise_exact_resume=False`.

`production/FDN_APP_FAST_CLOSE_INTENT.json` contains:

- original pinned bound close receipt, final_path and final_sha256;
- latest_complete_save, actual_native_policy_steps, learner_counters;
- env_close_returned, worker_final_qualified, error_before_close, close_errors;
- parent_must_wait_rc0_and_validate_FDN_final=True.

Order: finalize complete state -> bounded event flush -> original env.close ->
pin original App method -> durable intent -> immediate ORIGINAL zero-argument
app.close(). No SDK call occurs between intent and original App.close. Source
pin is the existing V6 SimulationApp source48933B / SHA
6af5372bb0cdda6e665a30cd285ff724b3e5bd012dbdd4df458e0726173fc903.
No setting/monkeypatch of fast_shutdown, no private close shortcut.

Parent success requires **actual wait rc0**, matching final SHA in intent,
`final=True`, `complete_save=True`, error None, close_errors empty,
actual_native_policy_steps>0, both real Adam step counts>0, and a matching own
save receipt/file stat. Any FDN_NATIVE_ERROR / FDN_SAVE_ERROR /
FDN_FINAL_METADATA_ERROR / FDN_APP_CLOSE_ERROR is a failure. Final and latest
save counters/native counters must match. An intent alone is not a result.
SystemExit raised by close is preserved as an error. Direct original fast
shutdown may have no normal Python return; only actual parent wait can qualify
it. Normal return adds FDN_APP_CLOSE_RETURNED.json but never replaces wait.
