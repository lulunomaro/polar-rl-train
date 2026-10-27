"""Final source-only objective qualification/index; does not reopen NPZ/raw."""
from pathlib import Path
import ast,datetime,hashlib,json
HERE=Path(__file__).resolve().parent;T=HERE.parents[1];R2=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027'
def read(name):return json.loads((HERE/name).read_bytes())
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
base=read('SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_ACTUAL.json');phase=read('PHASE_COHERENT_V2_FINAL_SOURCE_CPU_INCREMENT_ACTUAL.json');assert base['passed'] and phase['passed']
final=dict(base);final['source_CPU_checks']=45;final['old_vs_new_final_phase_coherent']=phase['old_vs_new_same_real_derived_states'];final['phase_velocity_coherent']=True
for name in final['runtime_modules']:final['runtime_modules'][name]=dict(bytes=(HERE/name).stat().st_size,SHA=H(HERE/name))
final['source_reports']['PHASE_COHERENT_V2_FINAL_SOURCE_CPU_INCREMENT_ACTUAL.json']=dict(bytes=(HERE/'PHASE_COHERENT_V2_FINAL_SOURCE_CPU_INCREMENT_ACTUAL.json').stat().st_size,SHA=H(HERE/'PHASE_COHERENT_V2_FINAL_SOURCE_CPU_INCREMENT_ACTUAL.json'))
final['previous_source_qualification_preserved']='SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_ACTUAL.json'
final['objective_contract']['stability']='wheel-center/root velocities track the same reference during145..185 braking and naturally target0 after reference stop; no physical stable threshold/clock changed'
final['runtime_builder']='own_step_differentiable_objective_v2.build_own_step_mdp(contract_document,geometry_document,reference_document,actual_joint_names,actual_encoder_joint_names,device=...,order_scope=...)'
final['contact_order_actual_sdk_pending']='contact18 latest forces expected left_wheel/right_wheel in worldXYZ; root actual sensor/name order/readback must bind this before use; not a platform face classifier'
put('SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_FINAL_ACTUAL.json',final)
text='''# Selected own-step differentiable objective — SOURCE+CPU frozen, NOT GO

45 bounded source/math/metadata checks passed across the preserved stages
(20FK/V1 checks+14selected bounded aggregation+2metadata constructor checks+
9phase-coherence checks). Only the explicitly allowed NEW R2 derived-only NPZ,
DERIVED_GEOMETRY JSONs, R5 source contract,9223 reference and Python source were
read. No old raw/PT/old rollout, actor/WM forward, optimizer step, SDK App/GPU,
remote, task/payload/GO/budget/Git action occurred. Derived NPZ was revisited
only for new aggregation and phase-correction purposes, never raw replay.

## Final runtime API and copy list

Copy these3 exact Python files, with the SHAs in the final qualification JSON:

* `own_step_differentiable_geometry_v1.py` — `OwnStepWheelGeometry` deterministic
  Torch FK/support buffers, no trainable parameters.
* `own_step_differentiable_objective_v1.py` — shared Huber task-cost implementation.
  **Do not instantiate its V1 reward class**; negative V1 reward was rejected.
* `own_step_differentiable_objective_v2.py` — selected `OwnStepDifferentiableMdpV2`
  plus the explicit `build_own_step_mdp` constructor.

One extra small geometry JSON is required:
`H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027/DERIVED_GEOMETRY_20260928.json`,
34263B SHA461f6b44e6014c72a755a0db5136fa8d45bd5b53b6318ee4b38221a4c597bc4d.
Recommended payload-relative name:
`source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json`. It contains actual31body
names and two own wheel collider48-point meshes among the34source shapes.
The29/30 JSONs have literal-equal body_names/shapes/geometry (checked), so one
copy suffices. Its old source_asset path is provenance only and never opened.

Use the NEW400N `job0/assets/import_contract.json`, original9223 reference and
actual30joint/encoder order already bound by root's SDK path. The4gas k/limit
changes leave every consumed parent/child/type/T0/T1 geometry field identical;
old700/new400 JSONs construct literal-equal FK buffers (checked). No separate
old700 dynamic contract or raw data is a runtime dependency.

Construction:

    mdp = build_own_step_mdp(new400_contract, recorded_geometry, ref9223,
        actual30names, actual_encoder_names, device=env.device,
        order_scope='actual_SDK_readback')

Equivalent: construct original ConvertedMOD4Reference+bind_named_order, then
OwnStepWheelGeometry and OwnStepDifferentiableMdpV2. Caller must perform the
actual SDK readback; the scope string alone is no qualification. `.to()` keeps
the V2 class. Original `converted_MOD4_jump_mdp_v4.py` remains the provider/base
dependency, not the selected native reward. State127/static31/obs86/history10/
goal1460/critic features/max_step_reward.06 are unchanged; no virtual joints,
new input, normalizer or optimizer parameters are introduced.

## Geometry and actual-derived alignment

FK uses every actual q in named order and the pinned exporter X hinge/slide
axes, local frames T0/T1. It does not impose an ideal drive==hip mimic identity,
run IK, read USD, or ask a simulator for new poses. Two wheel meshes transformed
from their own rigid body give exact recorded-shape support minima/maxima and
complete rectangular-platform footprint extents. Rigid velocity recursion uses
root v/omega and original qd to compute wheel-center velocities.

Each of1500 packed127 control-start states is compared with recorded31body
poses at **frame4*(control-1)**, including frame0 for first control. Origins are
zero with zero drift in all3cases. Maximum body position difference across the
cases is4.63e-7m; maximum wheel support difference vs recorded bodypose geometry
is4.32e-7m; bodypose supports agree with original callback caches within4.47e-8m
on499valid cache rows per case (initial cache is absent). Rotation matrix
differences are also fully reported. This is float32 arithmetic, not a new
FP64/1µm/physical graduation gate. It validates this source-to-recorded geometry
map, not collision cooking/contact or dynamic predictions of imagined states.

## Selected objective and weight choices

Let rho(x)=.5*x² for|x|<=1, else|x|-.5 (Huber). The weighted task cost uses:

| Cost | Scale | Weight |
|---|---|---:|
| Both wheel bottoms vs same9223own targets | .10m |2|
| Both wheel rears vs same reference rear positions | .15m |2|
| Lateral wheel-center errors | .08m |.5|
| Low wheel crossing front edge: positive front deficit×height deficit | .05m/.10m |4|
| After-contact bottom support vs270mm | .04m |1|
| Full footprint violations of edge.35/depth.8/width1.2 | .10m |1|
| Soft force deficit below original1N |1N|.15|
| Wheel-center/root v and omega vs same reference |.15m/s,.5rad/s|.3|

Support/contact/footprint/stability blend from reference first_touch145 to
support165.145..185 horizontal braking still tracks **its reference velocities**,
not an incorrectly early zero-speed target. After reference stop185 those
velocities naturally become0. Original physical request100..179/.8command,
clock/reset, V8 reward and hard success thresholds are not modified.

The early-wall5mm term is a soft planning penalty margin only, never a new
runtime collision/success tolerance. The mesh support/full footprint test has
the same geometric meaning as the original wheel-bound callback, but it is not
used to declare actual contact or replace original physical truth.

Old six tracking terms provide only a bounded **style deficit penalty** with
weight.05; they cannot contribute5easy positive points that hide task failure.
The original action-rate cost stays a positive cost with local near-goal
coefficient.01 in reward units. The selected whole aggregation is:

    reward = .06 / (1 + weighted_task_Huber_cost
                        + .05*style_deficit + action_rate_cost/6)

It is monotone, positive and bounded for finite evaluated cost, with polynomial
gradient decay rather than an exponential tail/product. V1 `1-HuberCost` gave
negative returns and was rejected because original survival weighting could
encourage ending imagination to avoid future penalties. V1 source and passed
math reports remain unchanged as history; their CPU pass is not deployment.
This V2 positivity removes that specific negative-future-return incentive; it
does not prove the world model, value adaptation or learned policy cannot fail.

## Same failed real states and counterfactual evidence

| Seed | Old request tracking/6 | New request task score | Old post200 | New post200 |
|---|---:|---:|---:|---:|
|20260928|.81387|.21481|.83403|.05164|
|20260929|.81733|.24249|.83443|.05232|
|20260930|.81457|.20490|.83349|.05198|

These task scores are shaped analytic values, **not probabilities or success
rates**. Same reference geometric goal atage200 scores≈.99977 when supplied
an explicitly synthetic soft1N support value; this is not a real landing.
Representative failed ground score≈.05176; raising root alone27cm while still
short of edge scores≈.11555; low-wheel early crossing scores≈.02415. A feature-
level COM rise with wheels held on ground changes no task-geometry cost; it is
an analytic loophole counterexample, not a claimed closed-chain physical pose.

Failed-state reward gradients point forward/up (≈.002545/.007233). Early low
wall-cross gradients point back/up (≈-.007091/.005174). Float32 central finite
differences agree (reported relative errors≈4.3e-5/2.5e-6 for x/z, and hip check
also passes). Missing soft force has positive force gradient and moving at the
post-stop goal has a decelerating velocity gradient. Atage170 reference brake
velocity has zero velocity-cost, while forcing a premature stop costs1.16667.
No actor or WM forward, optimizer or actual physics is involved in these tests.

## Interface differences and remaining limits

obs/critic_features/goal/relative_features/normalize_context/add_noise/
soft_termination/valid_imagination_start are the **same inherited original
function objects** (checked); future10 goals are literal-equal. Only reward/
objective_terms/contract_manifest/to are overridden, and constructor adds the
readonly geometry buffers. Real bridge and imagination must call this same new
head. The native objective metadata now says reward_changed; original physical
V8/hard success remain separate. Bind the final qualification+all3fileSHAs and
the actual objective contract SHA in publisher/reviewer/source Task metadata;
do not label a changed native reward as original-objective exact continuation.

Latest contact18 world-Z force is a **soft support proxy**. Caller must bind
actual left_wheel/right_wheel sensor/history order before use. It cannot identify
the platform face, and all recorded cases are failures, so no positive real
landing calibration is available. Original actual callback platform_contact,
fullfootprint, nonwheel_clean and stable-ticks success remain the only truth.
WM auxiliary-force prediction fidelity, fullbody collision/imagined closed-loop
validity, new400 dynamics, value adaptation, GPU performance/memory and actual
training gain remain pending. No speed/convergence/skill claim follows.

The phase correction, metadata-label correction and rejected negative-V1 concern
are all saved as explicit errata/rejection reports with previous source bytes.
No source CPU execution failed. The final independent source qualification is
`SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_FINAL_ACTUAL.json`; earlier
qualification JSONs are preserved stages, not current module-pin authority.
No deployment/GO is authorized here. All files await root ordinary Git supplement.
Stop after this freeze; root owns actual SDK/worker/resources/ledger/integration.
'''
(HERE/'HANDOFF.md').write_text(text,encoding='utf8')
for p in HERE.glob('*.py'):ast.parse(p.read_bytes())
rows=[dict(relative=p.name,bytes=p.stat().st_size,SHA=H(p)) for p in sorted(HERE.iterdir()) if p.is_file() and p.name!='FROZEN_SHA_INDEX_ACTUAL.json']
put('FROZEN_SHA_INDEX_ACTUAL.json',dict(frozen_at=datetime.datetime.now().astimezone().isoformat(),source_only=True,source_CPU_checks=45,files_excluding_index=rows,only_allowed_new_derived_data_used=True,no_old_raw_PT_USD_model_actor_WM_GPU_SDK_or_remote=True,actual_runtime_new400_and_training_not_admitted=True,all_rejections_errata_and_source_bytes_preserved=True,Git='PENDING root ordinary supplemental archive'))
print(json.dumps(dict(frozen=True,files=len(rows),qualification_SHA=H(HERE/'SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_FINAL_ACTUAL.json'),index_SHA=H(HERE/'FROZEN_SHA_INDEX_ACTUAL.json'),handoff_SHA=H(HERE/'HANDOFF.md'),runtime_modules=final['runtime_modules']),indent=2))
