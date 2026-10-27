# Existing R5 gas spring versus new human400N/L200/S60 evidence

Frozen source-only audit.14 CPU source/math checks passed; no SDK/model/actor,
physics/nativequery/GPU/remote, USD/mesh/raw/PT read/stat/hash/copy, original
runtime/Task edit, force write, Git, image tool, Luna or OpenRouter call.

The user's new selection is400N **per spring**, extended hole-centre distance
200mm, illustrated stroke60mm, hence inferred compressed distance140mm. Diameter
D18/d8 versus D21/22/d10 and force/stroke/friction/damping curves remain unknown.
140mm is derived from the two dimensions, not a separate end-stop measurement.

## What3500 and0.2206 actually mean

Exact R5 `job0/assets/import_contract.json` has two gas slide joints: stiffness
3500 **N/m**, damping3 **N·s/m**, joint target0.220639441090129m. The runtime uses
an implicit force drive,2000N cap, armature0.002 and a step event that writes
the **joint position target**, not the physical eye distance. D5 changes each
spring stiffness by an independent episode factor0.9..1.1; D6 independently
changes damping by0.9..1.1. They are engineering variation, not hardware curves.

The source readback explicitly distinguishes the SDK approximate generalized
effort from a separately measured PhysX/hardware gas force:
`estimatedF=k*(q_target-q)+c*(qd_target-qd)+ff`, clipped±2000N.
The authored velocity target is0. Preload writes the position target only.
This audit evaluates the zero-velocity elastic term; it does not claim measured
drive/constraint force. `applied_torque` is a generic SDK effort name; slide
effort units are N, not N·m.

## Eye-centre coordinate mapping from already-recorded frames

The upper eye is `gas_pin`'s child-side anchor in gas_inner coordinates; the
lower eye is `gas_closure`'s barrel-side anchor. Source exporter pins slide X.
The analytic rigid composition is
`L(q)=||T0*Tx(q)*inverse(T1)*gas_end - gas_pin_child_anchor||=||d+u*q||`.
It does not depend on the common gas_pin rotation or require an IK/physics run.
The shin-side point coincides only when the original closed-loop constraint is
satisfied; no new closure validity is claimed here. Left/right give the same
mapping. The tiny recorded-frame transverse residual is source arithmetic, not
an extra physical health tolerance.

`L(q)≈0.179360559751583+q` metres; positive q extends.

| Quantity | q (m) | hole-centre length (mm) |
|---|---:|---:|
| Existing lower limit | -0.026704684361 | 152.655875 |
| Existing neutral | 0 | 179.360560 |
| Existing upper limit | 0.035203335003 | 214.563895 |
| Human inferred compressed | -0.039360559752 | 140 |
| Human extended | 0.020639440248 | 200 |

Existing source travel is61.908019mm, not60mm.
It permits extension14.563895mm beyond200, while its lower bound is12.655875mm
above140. This proves the existing source limits are not literally140..200.
It does not prove that a particular R5 episode visited either endpoint.

The target0.220639m corresponds to a **virtual zero-force eye length≈400mm**.
A target outside joint limits is legitimate for a preloaded linear spring;
mistaking it for a220.6mm physical eye distance would be an error.

## Existing law is not the newly supplied400N nominal

At200mm, nominal static elastic effort is700.000003N;
at q0 it is772.238044N. Within the old
joint limits it is649.026371..
865.704439N;
including D5 the elastic envelope is584.123734..952.274883N.400N is outside that
zero-velocity envelope, so a hidden coordinate offset cannot make this old law
a400N law within its source limits. The matching MOD4 author provenance already
says **700N candidate per side, not verified hardware**. The separately read
deprecated rm2025_fixed500N/2500 rows are history, not active R5 nominal values.

This is a source-law/nominal mismatch, not a measured real-spring curve.400N's
catalogue measurement position is not supplied. Do not identify gas effort with
vertical chassis lift or declare this the sole cause of the zero landing result.

## Immediately meaningful nominal approximations — isolated, NOT deployed

A constant400N axial quasistatic surrogate has correct units and no invented
compression ratio. The accompanying pure module maps that to generalized
joint effort `400*dL/dq`; it installs no actuator and makes no dynamic-law claim.

Alternatively, explicitly choose **400N at200mm** as an approximation convention.
One force point leaves the family `qref=q200+400/k` unidentified:

* Keep existing virtual target: k=1999.999991583N/m (approximately2000), giving400N
  at200 and520N at140; the slope/1.30 ratio remain an engineering assumption.
* Keep3500N/m as an engineering sensitivity slope: qref=0.134925154534m,
  giving400N at200 and610N at140; the1.525 ratio is **not measured**.

400N must never be entered as400N/m. Neither linear choice is uniquely justified
by the label. No friction, damping, compression curve or diameter is filled in
from a generic table. The existing3Ns/m can only be described as retained
engineering damping if a future source explicitly chooses it, not calibrated.

A bounded geometric proposal is the intersection of old source limits and the
human-inferred stroke: q=[-0.026704684361,
0.020639440248], i.e.
152.655875..200mm. It does not expand the CAD lower bound to140. Its dynamic
reachability, stop forces, own contact and real hardware dimensions remain
unverified. This is a new-plant proposal, never an old runtime patch.

If root chooses such a new approximation, it must update the contract, D5
hardcoded3500 nominal/readback, expected DR/static31/source checks together
under a new namespace and fresh actual admission. Old native weights may be a
declared transfer source, but cannot be relabeled hardware-aligned or exact
same-plant continuation. The declared old-config frozen diagnostic can proceed
with honest scope; this audit introduces no extra physical tolerances/gates.

All source inputs and whole-directory SHAs are indexed. The missing historical
reference_manifest reader error and the reversed field-name erratum are retained
in `READER_ERRORS_AND_NUMERIC_FIELD_ERRATUM_ACTUAL.json`; original result/code
bytes remain unchanged. R5 actual findings/costs supplied by parent are copied
as attributed text only, never rewritten. Git ordinary supplement is PENDING
root; no helper Git operation occurred.
