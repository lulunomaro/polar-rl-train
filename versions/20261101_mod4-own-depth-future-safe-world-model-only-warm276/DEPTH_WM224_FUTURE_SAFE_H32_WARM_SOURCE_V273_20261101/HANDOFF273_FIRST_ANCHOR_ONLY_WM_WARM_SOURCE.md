273 is an independent SOURCE/synthetic-CPU WM-warm interface. It does not launch
SDK/SSH/GPU, read any checkpoint/raw/NPZ/USD, install a caller, create GO or write
an account. Original255/268/271V2 remain unchanged. Actual current-packet/teacher
qualification, resources, solewriter authority and real execution are ROOT-owned.
No actual WM or Pi update is claimed from the synthetic fixture.

FutureSafeWarmWM273 inherits268's native224/aux151 model, SE3 step/targets/error,
original64-row physical replay, dedicated sampling RNG, H32 autoregression,
time-sum/batch loss, done mask, error floors, Adam and gradient clip1. Its update
does NOT read or gather future xi/depth. Every selected start stores one admitted
current271V2 support anchor. At step i=0..31, context40 is fixed RAW current
static31 + RAW9 projected from that start's WORLD observed corners and predicted
native pose; existing255.normalize_context40 scales it exactly once. True future
physical s1 and teacher actions remain measured supervision labels, not future
depth inputs. A rollout is not a policy imagined rollout or a future camera.

Required imports on sys.path are this directory, pinned268 source, selected271V2
source, pinned255 source and the native source directory listed in
SOURCE273_PINNED_BINDINGS_AND_ABI.json. No module changes those dependencies.

ROOT interface:

1. Build FrozenTeacherContract273(checkpoint_SHA,whole_fullstate_receipt_SHA,
   actor35_critic38_STD6_full17Adam_verified=True) from ROOT's actual qualified
   fullstate evidence. This is a required metadata contract, not an alternative
   to actual tensor/optimizer verification. The class has no teacher parameter
   or optimizer references and cannot perform a Pi/Critic/STD/17Adam update.
   ROOT must keep actor35/critic38/STD/full17Adam exactly frozen, collect under
   inference/no_grad, verify before/after fingerprints and preserve original
   source/iteration/LR provenance in the actual caller.
2. Construct FutureSafeWarmWM273(native_source, actual_tensor.device,
   teacher_contract=...,binding=actual MeasurementBinding268,seed=...,
   envs=N,batch=...,hidden=...,synthetic_CPU_test=False). It creates only the NEW
   WM and one NEW WM Adam; default2048env/1024batch/512x3/LR1e-4/H32 match268.
   Root's admitted actual N may be64; no padding or implicit environment
   truncation is allowed. It does not coldstart or load a teacher itself.
3. Each completed50Hz transition is a dict with original replay fields:
   s/s1 float32[N,224],a/a_prev float32[N,6],xi float32[N,40],r float32[N],
   f long[N],ep_step int32[N],done bool[N]. s1 and its measured224 labels are
   original pre-reset endpoints; done is the original terminated/truncated union.
   xi records current raw static31+current raw camera feature9 for provenance;
   future xi is not used in forward. Supply the complete CURRENT
   CurrentDepthPacket271 from the s/start time as actual_anchor, including
   feature9/found/measured floor/sensor+control+pose times/native13 pose/
   actual env origins/T_world_heading/actual Producer271/packet ID. T_heading_optical
   is not T_world_heading. No floor0 or geometry-map fill is provided.271V2 uses
   gravity heading at WORLD(root.x,root.y,0), native wxyz position relative to
   actual env origins. Times share the actual relative simulation clock.
4. Call add(transition,actual_anchor=packet,physics_end_tick=end,
   physics_us=2500,feedback_samples=2,producer=...). Producer kind is
   ACTUAL_OWN_MOD4_FULLSTATE_DEPTH_PRODUCER, plant own_MOD4_live_USD, state_schema
   OWN_MOD4_PHYSICAL73_AUX151_MEASURED224_V268, measured_fields exactly
   ['own_L0_theta4','contact_forces_BODY31x3'], binding_witness_SHA equal to the
   admitted binding, and run_id/generation/source_admission_SHA matching packet.
   It must name s_physics_end_tick=end-8/s1_physics_end_tick=end, with successive
   end ticks separated by8. Ingress checks shapes, finite physical labels,
   source scope and clock before norm/replay mutation. Same ordered real env IDs
   must persist; per-env episode IDs remain actual. New run/generation requires
   a new replay, not reusing old anchor state.
5. Collect continuously. When ready_for_update() is true, update() performs
   one WM-only update and returns counts/loss/finite gradient norm. No supported
   H32 start means false readiness and sample/update refusal, never fake READY.
   Scheduling, finite save cadence and authority/caps remain in the ROOT caller.

found=False is normal measurement absence: keep its current feature valid0 and
visible_floor_z_m=NaN (explicit UNKNOWN), never fill0/hold old floor. Other actual
pose/time/transform/source columns are still required. Found support with missing
floor rejects. Future depth rejects. A found but stale age>.20 is retained as
raw physical/current-packet provenance but has no eligible anchor. For genuine
found+fresh rows, ingress selects the real env subset, preserves its actual IDs
and calls271.make_anchor once for that subset.271's uniqueness constraint is not
bypassed or supplied invented env IDs. Unsupported WORLD corners/derived fields
remain NaN/valid_anchor=False and never enter the network or target normalizers.

AnchorReplay273 is aligned to the same original64 slots and stores feature9,
floor, sensor/control/pose time, sensor native13 pose, T_world_heading, actual
env origins, raw static31, found/valid mask, start tick, admitted WORLD corners,
derived floor/height/confidence/age and true producer/packet/env/episode scope.
All physical transitions remain available, including unsupported-camera rows.
Sampling is uniform WITH replacement among real valid(start,env) pairs that have
H32 subsequent physical transitions. This is the necessary supported-start
conditioning of the original random minibatch. A later missing camera does not
erase the first fixed belief or substitute a later observation; original done
mask zeros losses after the first episode end. Root must maintain original reset
and episode labels rather than splicing episodes into a false nonterminal span.

Gathered batch.anchor includes the immutable copied start data plus one true
scope_records entry per draw. The same real env can occur multiple times or at
different start times; its real IDs are retained. A vectorized projection kernel
with the271 formulas handles this heterogeneous batch. It does not call271 for
each sampled item at each imagined step and invent no replacement unique IDs.
The actual raw packet/identity remains in replay for traceability.

Norms update only from each ingress row's supported current-anchor inputs and
measured current transition targets. No in_norm/out_norm updates occur inside
rollout_loss/update forward. These learned historical population statistics are
distinct from access to a particular rollout's future camera sequence. The new
fixture perturbs later stored depth/packet fields with norms held fixed and
checks the forward contexts, predictions and loss are exactly unchanged. It also
checks the first anchor affects context, preventing a vacuous constant-output
test. Synthetic nonzero final WM weights in that fixture are test-only; production
native WM initialization remains unchanged.

All271 limitations carry through: static terrain/observed-range belief only,
feature0 is projected visible near-boundary, not certified physical front edge;
AABB projection interior/full footprint is not certified. Belief age can reach
.64+initial age and is not future camera freshness/visibility. Step height is
floor-relative, confidence is held, undefined bearing is neutral with no new
directional claim. No GT terrain or future depth is accessed.

checkpoint() includes WM weights/norms/one Adam/private RNG/counters, source and
teacher contracts, measured224 schema and explicit future-safe-WM-warm schema.
It checks its complete in-memory tree finite. Replay/raw anchor storage is NOT
saved: resume starts both replays fresh while preserving WM state/counters.
Teacher/Pi updates stay0, complete_three_optimizer_conversion=False, and
actual_Pi_runtime_qualified=False.268's policy_imagination PENDING remains in
effect. No full Pi/Critic/three-optimizer conversion or stable skill is implied.
Effective10mm closure/.01 mimic/400N50D0-D7/Fudan19+16 are untouched and remain
ROOT's actual runtime readback responsibility.

The new purpose freezes3synthetic envs/33rows/99pairs/one synthetic WM update,
four source integration groups/four refusals. No268/271 old fixture is replayed;
no actual dataset/model is used. False/errors, if any, remain with their consumed
marker, and all reports await ROOT's ordinary append.
