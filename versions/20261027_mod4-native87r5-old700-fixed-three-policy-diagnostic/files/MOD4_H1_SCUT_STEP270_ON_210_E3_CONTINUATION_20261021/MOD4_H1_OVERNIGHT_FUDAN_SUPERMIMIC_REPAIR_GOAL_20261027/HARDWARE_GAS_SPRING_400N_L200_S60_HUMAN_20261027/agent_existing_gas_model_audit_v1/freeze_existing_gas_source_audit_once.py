"""Source/text-only final errata+human facts+freeze; no assets or model access."""
from pathlib import Path
import ast,datetime,hashlib,json
HERE=Path(__file__).resolve().parent
def read(name):return json.loads((HERE/name).read_bytes())
def put(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=read('EXISTING_R5_GAS_UNITS_EYE_MAPPING_AND_FORCE_AUDIT_ACTUAL.json');v=r['per_side']['left'];assert r['passed'] is True
facts=dict(source='parent relaying new explicit human hardware selection; no image/API/model query by helper',force_per_spring_nominal_N=400.,extended_hole_centres_m=.2,illustrated_stroke_m=.06,inferred_compressed_hole_centres_m=.14,compressed_length_is_derived_not_independent_measurement=True,
 diameter_variant_unknown=['D18/d8','D21/22/d10'],force_measurement_position_unknown=True,force_stroke_friction_hysteresis_damping_temperature_unknown=True,
 forbidden_visual_tool='No Luna/OpenRouter; no image tool called in this audit',
 actual_R5_parent_summary=dict(formal_native_bytes_each=256224393,h1_takeoff_count=3755,recovery_slot_takeoff_count=748,both_cross_count=0,landing_count=0,recovery_count=0,closed_balance_snapshot=569553.363275528,source='parent actual reports; not independently queried or model-read here',old_state_not_modified=True))
put('HUMAN_NEW_HARDWARE_AND_PARENT_R5_FACTS_ACTUAL.json',facts)
q200=v['human140_to200_required_q_m'][1];q140=v['human140_to200_required_q_m'][0];qref=v['old_target_joint_q_m'];k400=400/(qref-q200)
minimal=dict(deployed=False,hardware_curve_calibrated=False,old_runtime_or_Task_changed=False,
 nominal400_anchor_m=.2,anchor_is_explicit_approximation_convention_not_given_F1_measurement=True,
 one_anchor_does_not_identify_slope_and_virtual_target='q_ref=q_at200+400/k; any chosen positive k gives the same single400N anchor',
 preserve_old_virtual_target_option=dict(q_ref_m=qref,derived_k_N_per_m=k400,approximate_k_N_per_m=2000.,force_at140_N=k400*(qref-q140),force_at200_N=400.,assumption='Retain old virtual rest geometry only as an engineering convention; this predicts520N at140mm, not measured.'),
 preserve_old_engineering_slope_option=dict(k_N_per_m=3500.,q_ref_m=q200+400/3500.,force_at140_N=610.,force_at200_N=400.,assumption='Retain unmeasured old3500N/m slope; predicts610N at140mm, not measured.'),
 constant_nominal_option=dict(axial_force_N=400.,force_stroke='constant quasistatic surrogate only; does not invent progressivity or seal/damping law',joint_effort='400*dL/dq N by virtual work'),
 conservative_geometric_candidate=dict(q_limits_m=v['overlap_of_existing_joint_limits_and_human_stroke_q_m'],eye_limits_m=v['overlap_eye_length_m'],travel_m=v['overlap_eye_length_m'][1]-v['overlap_eye_length_m'][0],
  reason='Intersection of existing source limits and human-inferred140..200: do not blindly expand existing CAD lower bound; cap old extension above200 only in a NEW explicitly approved plant.',
  does_not_prove_dynamic_reachability_contact_or_stop_force=True),
 existing_adapter_couplings=['spring_pressure_index_runtime.SpringPressureSDK.nominal hardcodes3500 and verifies actual initial buffers','mod4_task reads contract stiffness/target/damping','NominalSpringReadback and original saved-source guards pin nominal3500/3','D5/static31/DR expected-value and whole-save source must be updated together in a new exact namespace if any nominal changes'],
 no_dropin_patch_or_bypass_provided=True,
 old_config_frozen_diagnostic_can_continue_honestly_without_hardware_alignment_claim=True)
put('MINIMAL_400N_ANCHOR_FAMILY_AND_STROKE_INTERSECTION_NOT_ADMITTED.json',minimal)
put('READER_ERRORS_AND_NUMERIC_FIELD_ERRATUM_ACTUAL.json',dict(
 errors=[dict(kind='FileNotFound source reader',path='polar-rl-train/sources/remote/incoming/rm2025_mod4/reports/reference_manifest.json',original_error='Get-Content: path not found',handling='No data inferred. Current R5 authored pin/slide/closure JSON suffices; missing historical path not retried.'),dict(kind='historical different parameter rows',read_path='polar-rl-train/sources/remote/incoming/rm2025_fixed/model_parameters.json',observed='500N/2500N/m old starting-point rows',handling='Retained as deprecated history. Current R5 nominal comes from its exact contract3500N/m; rm2025_mod4 provenance calls it700N candidate.')],
 numeric_errata=[dict(original_report='EXISTING_R5_GAS_UNITS_EYE_MAPPING_AND_FORCE_AUDIT_ACTUAL.json',original_field='source_limit_below_human_extended_cap_q_m',correction='Name is reversed: positive0.014563894754...m means original UPPER limit exceeds the200mm human extension length; numeric value is correct. Original report/code preserved, not overwritten.'),dict(original_field='source_limit_above_human_compressed_floor_q_m',interpretation='Positive0.012655875391...m means existing lower bound is152.656mm, above inferred140mm floor. Do not expand it without actual geometric evidence.')],
 source_search_only_note='rg also returned gas lines from rm2025_mod4/robot_hifi.xml as plain source text. No XML was compiled/loaded/hash-calculated; no USD/mesh/PT/raw was opened.',
 no_source_CPU_errors_or_runtime_failures=True,no_old_frozen_file_modified=True))
text=f'''# Existing R5 gas spring versus new human400N/L200/S60 evidence

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

`L(q)≈{v['neutral_hole_center_length_m']:.15f}+q` metres; positive q extends.

| Quantity | q (m) | hole-centre length (mm) |
|---|---:|---:|
| Existing lower limit | {v['old_limits_q_m'][0]:.12f} | {v['old_limits_eye_length_m'][0]*1000:.6f} |
| Existing neutral | 0 | {v['neutral_hole_center_length_m']*1000:.6f} |
| Existing upper limit | {v['old_limits_q_m'][1]:.12f} | {v['old_limits_eye_length_m'][1]*1000:.6f} |
| Human inferred compressed | {q140:.12f} | 140 |
| Human extended | {q200:.12f} | 200 |

Existing source travel is{v['old_coordinate_travel_m']*1000:.6f}mm, not60mm.
It permits extension14.563895mm beyond200, while its lower bound is12.655875mm
above140. This proves the existing source limits are not literally140..200.
It does not prove that a particular R5 episode visited either endpoint.

The target0.220639m corresponds to a **virtual zero-force eye length≈400mm**.
A target outside joint limits is legitimate for a preloaded linear spring;
mistaking it for a220.6mm physical eye distance would be an error.

## Existing law is not the newly supplied400N nominal

At200mm, nominal static elastic effort is{v['original_force_at_human_extended200_N']:.6f}N;
at q0 it is{v['original_nominal_quasistatic_force_at_q0_N']:.6f}N. Within the old
joint limits it is{v['original_nominal_quasistatic_force_range_over_original_limits_N'][0]:.6f}..
{v['original_nominal_quasistatic_force_range_over_original_limits_N'][1]:.6f}N;
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

* Keep existing virtual target: k={k400:.9f}N/m (approximately2000), giving400N
  at200 and520N at140; the slope/1.30 ratio remain an engineering assumption.
* Keep3500N/m as an engineering sensitivity slope: qref={q200+400/3500:.12f}m,
  giving400N at200 and610N at140; the1.525 ratio is **not measured**.

400N must never be entered as400N/m. Neither linear choice is uniquely justified
by the label. No friction, damping, compression curve or diameter is filled in
from a generic table. The existing3Ns/m can only be described as retained
engineering damping if a future source explicitly chooses it, not calibrated.

A bounded geometric proposal is the intersection of old source limits and the
human-inferred stroke: q=[{v['overlap_of_existing_joint_limits_and_human_stroke_q_m'][0]:.12f},
{v['overlap_of_existing_joint_limits_and_human_stroke_q_m'][1]:.12f}], i.e.
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
'''
(HERE/'HANDOFF.md').write_text(text,encoding='utf8')
for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
rows=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='FROZEN_SHA_INDEX_ACTUAL.json']
put('FROZEN_SHA_INDEX_ACTUAL.json',dict(frozen_at=datetime.datetime.now().astimezone().isoformat(),source_only=True,checks=14,files_excluding_index=rows,not_deployed=True,hardware_curve_not_identified=True,original_R5_immutable=True,all_errors_and_errata_retained=True,Git='PENDING root ordinary supplemental archive'))
print(json.dumps(dict(frozen=True,checks=14,files=len(rows),index_SHA=H(HERE/'FROZEN_SHA_INDEX_ACTUAL.json'),HANDOFF_SHA=H(HERE/'HANDOFF.md'),module_SHA=H(HERE/'gas_eye_length_and_nominal_force_candidate_v1.py'),minimal_k2000=k400),indent=2))
