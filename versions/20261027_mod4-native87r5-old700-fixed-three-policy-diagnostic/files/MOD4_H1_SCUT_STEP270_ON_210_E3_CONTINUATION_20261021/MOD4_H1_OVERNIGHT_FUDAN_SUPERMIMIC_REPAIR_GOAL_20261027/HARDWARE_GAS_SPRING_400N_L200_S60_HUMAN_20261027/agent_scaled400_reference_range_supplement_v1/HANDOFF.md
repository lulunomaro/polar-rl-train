# Supplement: scale old elastic curve to400N and check exact9223 reference

This is an isolated source-only supplement to the already frozen gas audit.
No old file/runtime/Task/reference was edited; no images/Luna/OpenRouter, actor,
SDK, nativequery, model/raw/PT/NPZ/USD/mesh or physical rollout was used. The
source JSON was read and hashed because it is the pinned planned reference,
not a saved trajectory or model. Six new CPU source/math checks passed.

The simplest declared approximation is **k2000N/m, old target0.22063944109m
unchanged**. It scales the original elastic law by400/700 at every coordinate.
It gives400.00000168N at200mm and520.00000168N at140mm (the tiny offset is from
the already-recorded authored-frame representation). The exact anchor fit is
1999.99999158N/m, so ordinary nominal2000 is appropriate; no new physical
precision gate follows.400N is a force, not a stiffness.

This retains the old **relative elastic progression assumption**, not a measured
new gas curve. The1.3 compression ratio at140mm follows that chosen line and is
not supplied by the hardware label. Viscous damping3Ns/m is not part of the
400/700 scaling and remains the previous unmeasured engineering value, likewise
seal friction, hysteresis/temperature and diameter are unknown. There is no
need to introduce a new constant-force backend for this minimal candidate;
the original implicit actuator could express the new k only under a coherent
new contract/admission, because D5 and readback source hardcode3500.

Exact reference358885bytes SHA9223a53e7bf85a0dc3505cc46c0eb33d04fc35a9bf85e7ffe0e4fbd03e1e46c3
contains301 frames0..300. Name-bound gas position columns are39(left) and42(right)
in packed73; they are active in the position mask for all301 frames.

| Side | qmin..qmax (m) | implied eye range (mm) | margin to200 at maximum |
|---|---:|---:|---:|
| Left | 0 .. .016799940619 | 179.360560 .. 196.160500 | 3.839500mm |
| Right | -.002649272300 .. .016887820269 | 176.711287 .. 196.248380 | 3.751620mm |

Both maxima are at age122. There are **zero** source samples above200mm or
below140mm, and zero samples outside the existing gas coordinate limits.
Therefore the proposed claim that this reference already needs retargeting
because its gas-eye targets exceed200 is **excluded by this source check**.
There is no gas-range-only reason to redo its IK. This is not a dynamic,
tracking, actual joint/closure/contact or full hardware qualification. A real
policy can overshoot a source goal, so the margin is not a safety guarantee.

Over this existing source table, k2000 predicts elastic efforts407.679..441.279N
(left),407.503..446.577N(right). These are model predictions, not forces measured
from R5 or purchased hardware.

The proposed model-limit intersection remains152.655875..200mm,47.344125mm
usable travel. Do not blindly expand the old lower CAD limit to140 merely
because the gas spring alone nominally has60mm stroke. Do not label the whole
60mm as assembly-proven. A changed base stiffness/limit is a new plant source;
the old R5 hardware alignment and same-plant continuation are not established.
Old-config frozen diagnostics remain valid within their honest declared scope.

`SCALED400_ELASTIC_CURVE_AND_9223_REFERENCE_GAS_RANGE_ACTUAL.json` retains full
named min/max/ages/masks and candidate assumptions. The CSV contains all602
source gas samples, not raw physical evidence. Source inputs and this directory
are fully indexed. All prior error/field-name errata remain in the first frozen
audit. No errors arose in these six checks. Git supplement is PENDING root.
