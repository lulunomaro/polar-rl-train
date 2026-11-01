271 is SOURCE_ONLY with one new synthetic CPU purpose. It is not a real camera,
native Pi/WM update, actual future-safe Pi runtime qualification, full
SuperMimic conversion or skill result.263/255/259/268 and their old once/index
files remain unchanged. No model,267raw/NPZ/componentPT, asset, SDK, GPU, remote,
budget/GO or Git is read or executed by this package. ROOT owns future admission
and ordinary Git append of every new report.

observed_support_context271.py provides Producer271, CurrentDepthPacket271,
make_anchor(packet,static31_raw=...,geometry=...) and
anchor.context40(predicted_native_state,producer=...,imagination_step=0..32,
geometry=...). Actual mode is default. Synthetic packets are accepted only in
explicit synthetic_CPU_test mode. The geometry argument is the pinned native
geometry returned by255 load_native_kernels; no separate SE3 integrator is added.
The builder has no future-depth/map argument, hidden measurement getter, sensor
call or future packet sequence interface.

A current packet must contain found/RAW263feature9, measured visible_floor_z_m,
sensor and control times on the same relative simulation clock, the same sensor-time actual pose, explicit
heading-to-WORLD transform, actual environment origins, packet ID and actual
own-plant producer/run/generation/admissionSHA/sensor/environment/episode identity.
Pose is native env-origin-local position with wxyz, not unconverted SDK xyzw.
The source263 heading frame is gravity-level, yaw from actual root, origin
WORLD(root.x,root.y,0). T_world_heading must match that actual pose plus env
origins. visible_floor_z is expressed in that same heading frame. No floor0,
map floor, pose, producer, environment origin or missing measured value is filled
in. Actual entry requires0<=control_time-sensor_time<=.20s and matching feature
age and pose time. Missing/not-found/future/stale/foreign/invalid fields reject.

263's feature0 is x0 of a supported visible top-surface candidate, a3% point-cloud
quantile; feature5 is x1-x0 using97%/3% visible x quantiles; lateral is(y0+y1)/2,
width y1-y0; yaw atan2(lateral,x0). These do not certify the true physical front
edge or full terrain/landing footprint. The anchor creates a fixed belief of the
measured rectangle [x0,x0+depth] x [lateral-width/2,lateral+width/2] at
visible_floor_z+step_height and transforms its four corners into WORLD once.
All measurements/static31 are detached clones, so later camera buffers cannot
update the anchor. No unobserved continuation, holes, surface map or dynamic
terrain behavior is inferred. This is an observed-range lower-bound belief,
conditional on the detector's rectangle/static-terrain interpretation.

At each imagined50Hz step, only predicted native224 position/rotation is used to
transform that same WORLD four-corner belief into predicted gravity-level heading.
Feature0/width/depth are its signed near-x and x/y projection spans; lateral is
the projected y-range midpoint and yaw atan2(lateral,near). Negative near-x after
passing or turning is retained. After yaw, projected AABB extents include locations
outside the original rotated polygon: do NOT treat its interior as a newly
observed/supportable rectangle or use these spans to certify landing area. Four
WORLD corners and transformed corners are returned so the caller retains the
actual fixed observed range. Feature0 is the projected observed-belief near
boundary, never a certified real front edge. An exactly undefined near/lateral
bearing returns neutral yaw0 with an explicit target_bearing_defined=False mask;
it is not a directional observation.

Height remains the observed floor-relative step height; predicted rootZ does not
turn it into root clearance. Confidence is the original observation confidence,
not predicted occlusion/visibility confidence. valid=1 means the fixed observed
belief exists, not that a new camera would see it. Age is original measured depth
age + step*.02 and may reach .64+initial_age (up to .84 at H32). It is BELIEF AGE
under a static-terrain assumption, not a future camera timestamp or stale current
depth admitted as fresh. All metadata explicitly identifies this boundary.

The output is RAW static31 concatenated with RAW belief9. Both static31 and the
observed anchor remain fixed within the original run/generation/source/sensor/
environment/episode scope; a reset/new generation requires a new current packet
and static snapshot. Pass context40_raw through the existing255
normalize_context40 exactly once.271 never calls a normalizer internally.
Predicted native tuples must be explicit physical73/aux151; legacy127 cannot be
relabeled224. The projection is differentiable in predicted XY/yaw away from its
normal piecewise min/max boundaries. RootZ, terrain confidence, visibility,
sensor noise and future measurements are not claimed differentiable predictions.

267 compatibility is limited and explicit. Its source depth_now currently returns
image,K,T,features,found,sensor_time, and the saved NPZ contains feature9 plus K/T
depth clocks; it does not retain target['visible_floor_z_m']. That detector value
was available in the current target263 result but discarded by that return. The
old NPZ is not enough to make this anchor. ROOT must authorize a NEW collector /
NEW current-packet purpose that retains that measured floor and sensor-time pose,
T_world_heading, actual env origins and source identity. No old raw re-read or
map-floor0 substitution is authorized here. Its existing T_heading_optical is
NOT T_world_heading and must not be relabeled. Derive/save the latter from the
same actual root heading/frame convention, then validate the matching times.

This module replaces only the missing SOURCE context-builder side of268's
PENDING boundary. It does not modify or bypass268.policy_imagination()'s explicit
PENDING refusal. Actual collection/association, sensor-time pose correctness,
actual replay start selection/reset masks, belief use inside the real H32 Pi
caller, known command evolution, literal259 memory and complete Pi/Critic/WM
optimizer/save/state admission still require ROOT's separate source and actual
purpose. Recorded future depth9 from supervised255 replay remains forbidden as
Pi imagined future truth.10mm closure/.01 mimic/400N50D0-D7 and Fudan19/16 are
unchanged; this pure context module reads or changes none of those runtime knobs.

FROZEN271_NEW_STATIC_SUPPORT_CONTEXT_SYNTHETIC_CPU_PURPOSE.json fixes one new
two-env synthetic packet/pose fixture, no NN construction/optimizer/real controls,
five groups and23 refusals. The original255/263/268/270 fixtures are not replayed.
Its returned pass/false and consumed marker are preserved; do not rerun the once.
