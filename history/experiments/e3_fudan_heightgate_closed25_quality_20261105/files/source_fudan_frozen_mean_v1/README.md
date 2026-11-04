# FrozenSequenceMean V1 — E3 pi-only evaluation adapter

Purpose: deterministic inference for independent N80 / 31-body MuJoCo evaluation
of the new local Fudan-sequence PPO branch. This is not institution-official
get-up code. Existing evaluation grade, DR, commands, resets and thresholds stay
with the evaluator; this adapter changes none of them.

## CPU-root ownership and exact schema

The caller selects a qualified new native-worker save and reads/hashes/decodes
its **whole root once to CPU**. Pass that already-decoded Mapping to this adapter.
The adapter has no checkpoint-file I/O and never invokes torch.load. Do not pass
the original 1cd mother as if it were a new sequence checkpoint.

Source contracts inspected:

- `../source_fudan_seq_ppo_v1/fudan_seq_ppo.py:439-447`: `state_dict()`.
- `../source_fudan_native_worker_v2/worker_fudan_sequence_ppo_native_v1.py:259-265`:
  original-mother receipt; v2 only fixed Mapping traversal after W1 PPO0.
- `../source_fudan_native_worker_v2/worker_fudan_sequence_ppo_native_v1.py:467-477`:
  native full-save root. No running source was changed or executed here.

The new root has `kind=MOD4V1_E3_FUDAN_SEQUENCE_PPO_NATIVE_V1`, version1,
`branch_kind=NEW_SEQUENCE_PPO_ACTOR_CRITIC_WARM_START`, `learner`,
`source_checkpoint`, `environment`, `native_counters`, `global_rng`, etc.
Weights come **only** from `cpu_root['learner']['model']`.
The source receipt uses exact keys `source_path/source_sha256/source_bytes/`
`source_iter`, `physical_byte_opens`, `SHA_calculations`, `CPU_decodes`,
`actor_critic_MLP_only`, `source_optimizer_and_DR_state_not_restored`,
`old_iteration_not_inherited`. It is not a `{path,sha256,iter}` receipt.

Strict selected keys, shapes:

| Prefix | Layer | weight | bias |
|---|---:|---|---|
| actor.mlp | 0 | 256 x 38 | 256 |
| actor.mlp | 2 | 128 x 256 | 128 |
| actor.mlp | 4 | 64 x 128 | 64 |
| actor.mlp | 6 | 6 x 64 | 6 |
| encoder.mlp | 0 | 128 x 175 | 128 |
| encoder.mlp | 2 | 64 x 128 | 64 |
| encoder.mlp | 4 | 3 x 64 | 3 |

Every row has exact `.weight` and `.bias` suffixes: 14 selected tensors.
They must be finite FP32 CPU tensors. No key-prefix guessing or partial load.
The complete saved training model must also contain the known eight
`critic.mlp.{0,2,4,6}.{weight,bias}` keys plus `log_std`, and no unknown keys.
Those critic/std values are **not** copied into the inference object or onto
GPU. The adapter never constructs a critic, Adam, SequencePPO training object,
privileged observation buffer or training-environment state.

Construction order is CPU actor/encoder modules -> strict load -> verify selected
weight digest -> freeze/eval -> transfer only these modules to the requested
device. There is no random-policy fallback or later model reconstruction. CPU
initialization runs inside fork_rng(devices=[]) and preserves global CPU RNG.

## Public API

```python
from frozen_sequence_mean import (
    FrozenSequenceMean, validate_checkpoint_provenance, extract_pi_state_dict,
)

# cpu_root was already decoded once by the caller; no file path is accepted here.
metadata = validate_checkpoint_provenance(cpu_root, expected_run=RUN_ID)
policy = FrozenSequenceMean(cpu_root, device='cuda:0', expected_run=RUN_ID)

observations, infos = env.reset()          # evaluator's unchanged reset contract
policy.initialize(observations['policy']) # actual already-noisy [N,35]
for _ in range(EVALUATOR_HORIZON):
    actions = policy.act()                # [N,6], deterministic mean, clip[-6,6]
    observations, rewards, terminated, truncated, infos = env.step(actions)
    policy.observe(observations['policy'], terminated | truncated)

policy.assert_immutable(deep=True)
receipt = policy.receipt()
```

Adapt the reset/step tuple unpacking to the existing native/MuJoCo evaluator,
not its physics, DR or grading. For a NumPy MuJoCo observation, convert its actual
raw35 values to a Torch [N,35] floating tensor before initialize/observe. No
normalizer, sensor redraw or body-velocity injection is performed. The evaluator
owns action conversion to its existing environment API.

Exact signatures:

```
validate_checkpoint_provenance(cpu_checkpoint: Mapping[str, Any], *,
    require_native_updates: bool = True, expected_run: str | None = None) -> dict[str, Any]
extract_pi_state_dict(cpu_learner_state: Mapping[str, Any]) -> dict[str, Tensor]
FrozenSequenceMean(cpu_checkpoint: Mapping[str, Any], *, device='cpu',
    require_native_updates=True, expected_run=None)
initialize(raw35: Tensor) -> None
act() -> Tensor
observe(returned_raw35: Tensor, done: Tensor) -> None
history_snapshot() -> Tensor
weights_snapshot() -> dict[str, Tensor]  # independent CPU copies, selected keys only
assert_immutable(*, deep: bool = False) -> None
receipt() -> dict[str, Any]
```

## History and immutable guards

- First actual raw35 repeats five times. History order is oldest -> newest.
- `act()` appends nothing; it computes encoder(flat175) -> latent3, then
  actor(concat(current raw35, latent3)) -> deterministic mean -> clip6.
- There is no true body-V / privileged-input argument. Actor input is 38 because
  raw35+learned latent3, **not** privileged38 or ground-truth linear velocity.
- `observe()` must follow exactly one `act()` and one environment step. It appends
  that returned actual noisy observation once. Only done rows replace all five
  frames with their own already-returned observation. done is boolean [N],
  including both termination and timeout.
- Repeated act/observe calls in the wrong phase raise; initialize is once only.
  Do not separately append/reset a second external history for this object.
- A fresh evaluator N is established by initialize. No N4096 training root,
  DR/RNG/queue/history is read/sliced/restored into N80 or N1 inference state.
- Inputs/outputs/public snapshots do not alias private history or weights.
  Every inference call checks parameter identity/version/frozen mode and exact
  private-history integrity. Deep checking also hashes weight values, catching
  `.data` edits that evade normal Torch version counters. Deep checks copy
  selected weight values to CPU; they are explicit boundary checks, not sensor
  evaluations. There is no promise against arbitrary hostile Python rewriting
  of private guard fields.
- The methods work inside an outer torch.inference_mode() while keeping owned
  history tensors ordinary/versioned. Parameter gradients remain None.

## Structural provenance is not independent acceptance

The optional standalone validator checks full-save/known-branch declarations,
immutable-mother receipt, typed environment/component key structure, original
T48/N4096 and 5x4 optimizer counter relations, and 8physics/2feedback/control
counter relations. Default construction requires positive completed updates in
both Adam groups and positive native controls. W1 PPO0 therefore fails default
admission. This source does not assume W2 produced an update.

`require_native_updates=False` exists only for explicit synthetic functionality
fixtures; its setting is retained in the receipt. It is not the normal
independent-evaluation admission setting.

The validator does not reopen/re-hash files, prove claims recorded in metadata,
traverse every full-state tensor, verify actual owner wait or certify DR/PhysX
continuation. The parent still binds the chosen new save's actual SHA, qualified
FINAL/intent and actual wait. `selected_weight_sha256` is a canonical digest of
14 selected FP32 key/shape/value arrays, not the checkpoint-file SHA.

After this CPU-only functionality check, independent native N80 and 31-body
MuJoCo evaluation still establish actual behavior. Neither mean equivalence nor
training credit counts are a skill-improvement or full-rear-leg-goal result.

## Single synthetic test

```
C:/Users/lulu/Desktop/claude/mjcf/.venv/Scripts/python.exe -B test_synthetic_n80_cpu.py
```

This new adapter-specific CPU test uses one N80/9-step synthetic trajectory,
mixed resets plus one all-reset frame, a same-weight core SequenceActorCritic
CPU reference constructed before strict load, and no SequencePPO/Adam object or
PPO update. OrderedDict roots/weights are used. It also probes duplicate-call,
missing-key, no-alias, frozen-parameter and history guards. Training-state
sentinels raise on any attempt to read/slice/restore DR/history/RNG values.
No real model file or SDK/GPU is used; the old core test is not rerun.
[CPU_RESULT.json](<CPU_RESULT.json>) preserves the sole run and blocks repetition.
History is controlled mutable runtime state, not a globally constant tensor:
act leaves it unchanged, observe updates it once, and only done rows receive
repeat-reset.

### Actual sole CPU result

PASS with Torch2.14.0+cpu, N80, nine steps. All nine same-weight core-reference
clipped-mean maximum absolute differences were exactly 0.0. Mixed done counts
were [27,20,16,14,80,10,9,8,8]; every expected history matched exactly. Each step
included 160 saturated action elements, so clip6 was exercised. The runtime
adapter contained 14 parameter tensors / 82,505 scalars. CPU global RNG was
preserved by construction; selected source weights stayed unchanged/unaliased.
Missing-key, repeated-act/observe, normal-version/deep-weight and exact-history
guards passed. A CPU core NETWORK (including its unused critic) supplied the
reference; neither adapter nor test constructed Adam or SequencePPO learner,
and PPO updates were zero. Real checkpoint/SDK/GPU/native/MuJoCo evaluation
were all absent. The fixture's native/Adam counts remained zero and the default
native-positive admission rejected it as intended. These results do not assert
W2 GO/update or independent N80 / 31-body MuJoCo skill success.
