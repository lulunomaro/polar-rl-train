"""Freeze only the new text candidate and source/API status; no USD/model I/O."""
from pathlib import Path
import ast,datetime,hashlib,json
HERE=Path(__file__).resolve().parent;T=HERE.parents[2];W=T.parent;N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,v):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2,ensure_ascii=False,allow_nan=False)
cpu=json.loads((HERE/'SOURCE_CPU_SEMANTIC_DIFF_AND_ADMISSION_FIXTURE_ACTUAL.json').read_bytes());assert cpu['passed'] and cpu['checks']==28
sources=[N/'saved_actual_SDK_source/actual_physx_articulation_data_for_R5_tensor_view.py.txt',N/'saved_actual_SDK_source/actual_base_articulation_data_for_R5_tensor_view.py.txt',W/'polar-rl-train/sources/remote/incoming/rm2025_fixed/tools/export_usd.py',W/'polar-rl-train/sources/remote/incoming/mod4_fixed_20260912/chassis_mod4/isaac/audit_import.py',W/'polar-rl-train/sources/remote/incoming/mod4_rolling_20260913/tools/build_rolling_rollers_usd.py']
put('ACTUAL_SDK_SOURCE_AND_REQUIRED_INTERFACES_ACTUAL.json',dict(
 actual_source_inputs=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sources],
 proved_existing_readonly_interfaces=['robot.data.joint_pos_limits: actual PhysX ProxyArray(N,30,2), [lower,upper]','actual PhysX data initialization uses _root_view.get_dof_limits()','old runtime root_view.get_dof_stiffnesses/get_dof_dampings/get_dof_max_forces/get_dof_armatures','old runtime set_joint_position_target via existing step preload event (unchanged)'],
 proved_existing_stiffness_write='original write_joint_stiffness_to_sim_index remains inside original D5 adapter; only its nominal input changes',
 proved_asset_authoring_interfaces=['UsdPhysics.PrismaticJoint.Define(stage,path)','Prismatic.CreateUpperLimitAttr(float)','UsdPhysics.DriveAPI.Apply(prim,linear)','DriveAPI.CreateStiffnessAttr(float)','Usd.Stage.Open(privatecopy,Usd.Stage.LoadAll) and GetRootLayer().Export(newpath) already used by old asset tools'],
 no_proved_cfg_hardlimit_setter=True,no_new_PhysX_hardlimit_setter_implemented=True,
 required_new_asset_only_changes=['/Robot/joints/left_gas_slide.drive:linear:physics:stiffness3500->2000','/Robot/joints/right_gas_slide.drive:linear:physics:stiffness3500->2000','left_gas_slide.physics:upperLimit.0352033350025->.020639440248416612','right_gas_slide.physics:upperLimit.0352033350025->.020639440248416612'],
 actual_target_future_required=['new USD composition and4property allowlist; old base binary/dependencies unchanged according to original pinned manifest','original complete authored joint/body/mimic/closure/geometry import checks using new4leaf contract','actual30order/4096/D0-D7/TGS32/4/2.5ms100Hz/actiondelay/clip6 and exact original success','new k2000*episodefactor agrees actual buffer/implicit model/PhysX','actual hard limits backend+buffer, not merely soft_joint_pos_limit_factor','preload reset0 is truthfully pending; observe unchanged original step event activate oldqref beforefirstnewPi','whole each-own qualified R5 native WM/Pi/Critic/allnorm/threeopt/counter source load and new method changed-plant output contract','root sole72 fresh resources and metadata/current canonical closing; no sourceCPU fixture may satisfy these'],
 actual_target_SDK_scene_or_USD_admitted=False,actual_hardware_force_curve_calibrated=False,no_remote_query_requested_for_this_candidate=True))
put('READER_ERROR_RETAINED_ACTUAL.json',dict(kind='local PowerShell source metadata reader parser error',original_command_fragment='foreach (...) { [PSCustomObject]... } | ConvertTo-Json',original_error='ParserError at line2: empty pipe element / 不允许使用空管道元素（tool output contained mojibake）',effect='No query ran because whole command failed parsing; no runtime/asset/model or remote action.',correction='New local read wrapped foreach in @(...). All5selected SOURCE_FREEZE entries were then proven to match current originals.',original_error_not_reclassified_as_training_or_SDK_failure=True))
text='''# Nominal400 target source candidate — frozen, NOT admitted/deployed

This is source-only preparation for a **700N→400N nominal changed plant**, not
an88 payload/controller/Task/GO or an actual SDK admission.28 new CPU source/
semantic/API-metadata checks passed. No real model/PT/raw/NPZ, original USD/mesh
binary read/stat/hash/copy, actor, physical rollout/nativequery, SDK App/GPU,
remote, account or Git action occurred. No old fixtures were rerun. All old
frozen files/R5 sources/actual reports remain unchanged.

## Concrete text overlay

`gas400_source_patcher_v1.prepare(B,new_dest)` rejects unknown old source SHAs,
unexpected token counts/paths or an existing/source-contained destination.
The generated `isolated_text_overlay_NOT_A_PAYLOAD` has exactly7 replacements:

* `job0/assets/import_contract.json` and runtime `isaac/mod4/import_contract.json`:
  exactly4 scalar edits in each: two stiffness3500→2000N/m and two upper slide
  limits.0352033350025→.020639440248416612m. Scalar-offset edits preserve all
  other JSON bytes, including lower limit, targets, damping, joint/body/geometry.
* `spring_pressure_index_runtime.py`: two nominal3500→2000 constants and its
  module description. `spring_pressure_audit_runtime.py` and
  `spring_nominal_sdk_readback.py`: only their nominal3500 assertions→2000.
* `spring_pressure_training_env.py`: recipe nominal3500→2000 and expected D5
  [3150,3850]→[1800,2200]. Factor/RNG/reset/SDK application flow stays identical.
* `job0/runtime/reports/SOURCE_FREEZE.json`: only the5selected current source
  rows above are rebound (four Python+runtime contract). All selected old pins
  matched actual source; every other legacy row/byte remains untouched.

These are7 source replacements, not a full runnable training package. The old
`mod4_task.py` needs no code edit: it already reads gas k/target from the adjacent
asset contract. `skills_isaac` preload, D5 component/RNG, D6, action queue,
original V8/command/success and complete save-function code are not patched.
AST comparison proves7 numeric constants plus1module-doc string differ in the
four Python files; imports/classes/loops/reset/save logic are unchanged.
Old/new SHA rows are in `CANDIDATE_SOURCE_CHANGESET_NOT_ADMITTED.json`.

## Asset authoring, with no guessed hard-limit cfg/PhysX setter

No currently obtained actual source proves a hard joint-limit cfg setter.
`soft_joint_pos_limit_factor` is insufficient. Two explicit future options:

1. Prefer the tiny `NOMINAL400_GAS_ONLY_OVERLAY_NOT_ADMITTED.usda` source layer.
   It sublayers `source_700N/robot.usd` and gives only four physical attribute
   opinions: the two linear stiffnesses and two upper limits. Old binary and
   its relative dependencies must remain byteexact under that private base
   directory according to their existing producer/manifest pins. This layer
   has not been parsed/composed by an actual USD/SDK here.
2. `gas400_private_asset_authoring_unused_v1.author_private_copy(...)` is an
   unexecuted alternative. It accepts only distinct private source/output
   under a new-owned root, opens the private copy, and uses original exporter
   APIs Prismatic.Define/CreateUpperLimitAttr and Drive.Apply/CreateStiffnessAttr
   to change the same4attributes, then Export(newpath). It never Save()s/opens
   the original asset. A re-exported copy is only a proposed semantic-preserving
   asset; actual composition/inventory checks remain root's future admission.

**Materialization detail:** current `mod4_task.py` takes the parent directory of
RM_MOD4_USD and always constructs `.../robot.usd`. Thus root must place the new
layer/private derived asset at **newassets/robot.usd**, with the changed contract
beside it. Passing only the long candidate.usda filename would still load the
old robot.usd in that directory. Do not overwrite an old asset or copy only a
root layer while breaking its relative mesh/material dependencies.

All other joint/closure/mimic/body/collision properties and old geometry source
bytes must retain their original pins. A new actual target stage/parameter
review is required; the pure-layer textual allowlist is not that review.

## Parameters and scope

The virtual q target is retained (.22063944109012937/.2206394410901294m).
k2000 is400/700 times old3500, yielding nominal400N at eye200mm and520N at140mm.
This preserves an **engineering elastic progression**, not a measured curve.
Damping3Ns/m remains unmeasured engineering damping; D5±10% and D6±10% retain
their original algorithms. No diameter, force/stroke/friction/hysteresis or
temperature curve is invented.400N is a force, not400N/m.

Keep original q lower-.0267046843609, cap upper.020639440248416612. This is the
existing CAD/source-range intersection: eye152.655875..200mm,47.344125mm travel.
It does not claim the assembly uses all physical60mm or expand its lower bound.
Reference9223... remains byteexact; the previous source check already proved
its maximum196.2484mm, so no gas-range-only retarget is required or performed.
Actual tracking/impact/force/closed-chain health is not established by that fact.

## Actual SDK admission hook (future only)

`gas400_sdk_admission_candidate_v1.check_actual_new_gas(env,
expected_joint_names=...,tensor=<existing readonly view adapter>,
require_active_preload=...)` validates actual gas order, nominal2000, D5/D6
episode values in memory/implicit model/PhysX, original force cap/armature,
hard limits backend+buffer, original target and target velocity, clock/TGS32/4.
Its getter names are already in original runtime and saved actual PhysX data
source. Missing Tensor/.torch backend objects reject; it never substitutes a
cast or guesses a limit setter. A static type/getter query, if still needed,
belongs to a root-only future missing-only purpose, not this candidate.

Original reset can have neutral target0 until the existing step preload event.
The hook reports that honestly; `require_active_preload=True` must be satisfied
by a real subsequent pre-Pi readback during the new adaptation stage. An initial
parameters-pass is not a fake active-preload/full production-ready flag.
Actual SDK/readback/resource/whole-model source admission remains PENDING.

## Typed native transfer, not same-physics continuation

`gas400_migration_contract_v1.declare_transfer` requires each slot's own formally
qualified R5 native127/obs86/static31/aux54 source and saved global counters.
It declares preservation of WM/Pi/Critic, all norms, three optimizer states and
global counters, with fresh physical episode/replay/history and no old700N DR
restore. Root must supply positive adaptation-control/world-update counts
explicitly before launching; no arbitrary new count default is imposed here.
The synthetic64/10 fixture is **only a metadata example**, not an approved
training schedule. No native-source/PPO20Adam conflation is permitted.

`validate_new_publication` refuses old positivePi, insufficient actual new
controls/WM updates, missing active preload, or a new Pi without matching actual
new preupdate SHA/bytes/before-control binding. It requires globalPi>sourcePi
and WM delta≥declared readaptation. Its metadata expects native_iteration
(the internal checkpoint publication field); root may explicitly map the
external receipt's `updates` to it after exact equality checks.

This module is a source interface, **not integrated training warmup**. Root's
new entry must implement world-only adaptation using new-window deltas, not
oldglobal iteration>wm_only. It must preserve cumulative source counts while
recording zero newPi during warmup. The static31 spring feature divides k by
its nominal base; factor1 can look identical before/after while the real law
changes, which is why WM readaptation cannot be skipped.

Old native output contract `original_physics_and_success_unchanged=True` and
`fresh4096_policy_only_bootstrap=True` must NOT be reused as new-method claims.
Root must give the changed-plant native output its separate typed migration
contract/source/producer pins while retaining original fullsave function bodies
and all D0-D7 groups. The7overlay files alone must never be fed through the old
same-physics ready branch or considered an88 admission.

Root retains sole72 canonical/current resource/fee authority.569553.363275528
is the latest closed snapshot supplied by parent, not a helper account read.
No lock/account/controller/budget/deadline/Task/GO is created or changed here.
The one local PowerShell reader parser error is retained separately. Git
ordinary supplement remains PENDING root. Stop/freeze after this handoff.
'''
(HERE/'HANDOFF.md').write_text(text,encoding='utf8')
for p in HERE.rglob('*.py'):ast.parse(p.read_bytes())
rows=[]
for p in sorted(HERE.rglob('*')):
 if p.is_file() and p.name!='FROZEN_SHA_INDEX_ACTUAL.json':
  assert p.suffix in ('.json','.py','.md','.usda')
  rows.append(dict(relative=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
put('FROZEN_SHA_INDEX_ACTUAL.json',dict(frozen_at=datetime.datetime.now().astimezone().isoformat(),source_only=True,checks=28,files_excluding_index=rows,no_payload_or_Task_GO_created=True,no_original_USD_model_raw_SDK_GPU_or_remote_access=True,old_R5_frozen_bytes_unchanged=True,actual_SDK_USD_and_transfer_warmup_pending=True,Git='PENDING root ordinary supplemental archive'))
print(json.dumps(dict(frozen=True,files=len(rows),checks=28,index_SHA=H(HERE/'FROZEN_SHA_INDEX_ACTUAL.json'),handoff_SHA=H(HERE/'HANDOFF.md')),indent=2))
