268 is an independent source/synthetic-CPU package. It has not consumed a real
checkpoint, measured trajectory, depth artifact, asset or SDK. It has not trained
an actual WM or Pi, or qualified a skill. Its CPU fixture did not assume267 had
completed. The subsequent saved267 metadata join is described below.255 and259 are
unchanged. All new files/reports await ROOT's ordinary Git append.

The selected state is224 = physical73 + aux151. The first127 values retain the
original native physical73/aux54 layout. The new97 are L0_left/right in metres,
theta0_left/right in radians, then31 BODY-frame contact-force xyz vectors divided
by fixed400N. The force scale is a numerical label scale, not force injection or
an actuator force limit. The original history18 is not replaced or rescaled.
SCHEMA268_MEASURED224_AUX151.json records every slice and unit. No new effort6 is
added: packed91:121 already holds applied_torque30; the original reward-order six
are selected by the admitted actual motor IDs.

MeasurementBinding268 takes ordered30 joint names, ordered31 body names, the six
actual motor IDs in original reward order, and an actual binding witness SHA.
The required motor names are left_crank,left_hip,left_wheel_spin,right_crank,
right_hip,right_wheel_spin. Numeric IDs here are deliberately not guessed. The
fixture's IDs and witness are explicitly synthetic and rejected in actual mode.
ROOT must obtain the actual binding from its admitted robot metadata. Applied
efforts are SDK applied_torque, not independently measured hardware torque.

pack_measured224(base127, L0=..., theta0=..., contact_forces_world=..., layout=...,
binding=..., measurement=...) requires all three actual measurements. L0/theta
must use own_virtual_legs v2: authored hip anchor to main-wheel body origin,
sagittal L0 and atan2(-v_b.z,v_b.x)-pi/2 including the original branch convention.
Actual WORLD net_forces_w must already be reordered into robot.body_names. The
function stores R^T F/400 from that same endpoint. Missing/legacy/wrong-frame,
wrong-order, nonfinite or partial measurements reject; no zero padding or held
force label is supplied. The metadata names the original physics endpoint tick.
For each add, s tick=end_tick-8 and s1 tick=end_tick are required, with original
2500us physics/eight callbacks/two100Hz samples per50Hz control. Actual callers
must capture terminal s1 and these new measurements BEFORE reset, using the same
endpoint as physical73/aux54. Do not combine a pre-reset physical state with
post-reset forces/legs, carry a position difference across reset, or call a
declared producer label proof of actual measurement.

MeasuredDepthTeacherWM50(source,device,binding=...,seed=...) inherits255's sample
and update functions, original replay class, H32 autoregressive supervised loss,
time-sum/batch reduction, masking, running norms, finite checks and gradient
clip1. Native step/targets/state_error and SE3 integration are unedited. Only
auxiliary_dim changes54->151 and packed state127->224. Input/output dimensions
are273/223; context40 remains static31+depth9, action6, replay64, default2048
envs/batch1024/hidden512x3/LR1e-4. Old127 WM checkpoints are not shape-compatible
exact resumes. This package initializes a NEW224 WM; it does not load/copy old
weights or reset/modify an original PPO optimizer.

Important context boundary: inherited255 update consumes recorded xi at each
H32 time. Its later depth9 is permitted as WM supervised replay context ONLY.
It is future actual camera truth for a policy imagined rollout. The protocol and
checkpoint explicitly set policy_imagination_context_ready=False and
policy_imagination() raises PENDING. A first-real-depth+first-measured-pose anchor,
observed support-plane belief and predicted-pose context transforms remain
PENDING; this package does not claim that runtime, full Pi BPTT or future-depth
handling is complete. No later actual depth may be used as a hidden Pi fallback.

predicted_literal_frame(previous_state,state,commands,environment_origins=...,
layout=...,binding=...) builds the nine-field259 frame. Native root position is
env-origin-local in WORLD axes and native quaternion wxyz. The original bridge
explicitly converted actual SDK xyzw->wxyz. The new frame adds known actual env
origins back and converts predicted R to the original SDK xyzw convention.
BODY linear velocity is R_current^T*(p_current-p_previous)/.02, not a substitute
root velocity channel. BODY angular velocity is R^T*w_world; projected gravity
is R^T*(0,0,-1). Original root WORLD velocities remain in root_states. Known
original command4 is provided by the caller. Predicted L0/theta come from the
new aux; original six efforts from aux18:48; contact BODY suffix*400 is rotated
back into WORLD for the unchanged literal19 methods. No future/live PhysX or
depth getters are called. Original action reordering, air/contact/action memory,
16weights/clip2.5 and reset semantics remain in259/the original SDK adapter;
they are not rewritten here.

Dependencies and exact SHAs are pinned in SOURCE268_PINNED_REFERENCE_BINDINGS.json:
255 native_depth_world_model50_v255.py d2554ca2fe96c56a1aaaab22c4da76482ab5ee5da07887b8b238294d3d016f6b;
259 literal_imagination259.py ad84314f64b21308651b1a1c759e23742bd25efa78e145d50c999a60b249c44a;
native augmented model ba89385cdd80c365923a31c90ffca1457d9a116d195035c2051a6c8f573a9408;
geometry f908362f1b70c4e125890e1d277e62212df6875870893982fa91cddd3f7988e3;
original bridge4de4cda8be9b18d4b32da26cf2f4a8de660ecc8f9471a040a4b8723ff6574433
establishes env-origin subtraction and SDK xyzw conversion at pack(); the
original jump194_sdk.py8058eb0d4cbfc8c8582f4b9580004978a3fd49ed5c5afbac9aad578ba1426bc5
establishes measured motor naming/order, WORLD contact frame, BODY position
difference velocity and own virtual-leg consumption. Those are historical
source references, not claims that their old guard config is current. This
module's10mm closure/.01rad mimic/400N50D0-D7 protocol is declarative; effective
current runtime guards still require ROOT's actual before-constructor/native
readback. It supplies no SDK launch, GO, budget writer or training caller.

ROOT integration is SOURCE_READY only: put this directory, the pinned255
directory, and the pinned native source directory on the import path. Bind actual
metadata, build the explicit224 measured endpoints and matching producer metadata,
then use MeasuredDepthTeacherWM50.add.259's literal adapter may consume the
predicted frame only once an actual future-safe policy-context caller exists.
Target authority/resources, actual body/motor binding, actual depth timestamps,
complete pre-reset capture, one necessary source-Pi read purpose, effective
guards/native startup and any real new WM/Pi execution remain ROOT-owned and
EXPLICIT_PENDING. This source package requests no remote execution by itself.

The single NEW268 synthetic CPU purpose completed once:5 groups/15 rejections,
2 synthetic envs/32controls/64pairs/one supervised synthetic WM optimizer update.
Native loss127.39803314208984 and preclip gradient L2384.52557373046875 are synthetic
interface numbers. Global Torch RNG was unchanged, CUDA uninitialized; models,
raw/assets, SDK/GPU/SSH, checkpoint writes and Git calls were0. Old255/259 fixtures
were not replayed. The purpose, consumed marker and returned report are retained
under reports. Do not rerun this once; future actual integration needs its own
frozen purpose and actual admission.

After that CPU purpose, ROOT reported267's actual frozen2135 actor collector
complete. The saved JSON at
OWN_MOD4_FULLSTATE_DEPTH_COLLECTOR_V267_20261101/reports/ROOT267_NEW240_MEAN_REGRESSION_PARENT_OR_ORIGINAL_ERROR_RETURNED_ACTUAL.json
is a separate ROOT execution fact, not a268 run. It records N1/64controls,
512physics/128feedback,65camera reads,64valid depth inputs,0terminated/truncated,
one source-model byte read/decode, frozen actor,0optimizer/GO/account writes,
original waitRC0 and actual release. That collector's source
source/measured224_schema267.py has the same224 slices: base127, L0[127:129],
theta[129:131], BODY31x3/400[131:224]. The saved-JSON/AST metadata join and their
SHAs are in reports/SOURCE268_ACTUAL267_SAVED_METADATA_ABI_JOIN.json. Neither its
612372B NPZ nor1848341B component PT was opened, copied, downloaded or decoded by
this child.64 transitions from one N1 trajectory are not a population, a real WM
update or successful skill/training.224 also does not claim complete sensor,
queue, noise, spring, delay or DR Markov memory;267 stores component/static memory
separately. Actual measured-pair supervision and use of that separate memory
remain a new ROOT purpose. The actual numeric binding witness and the
future-safe Pi depth-context builder are still required before real integration.
