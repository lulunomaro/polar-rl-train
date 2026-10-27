"""Final source/metadata freeze; no model/asset/raw/runtime operations."""
from pathlib import Path
import ast,datetime,hashlib,json,sys
HERE=Path(__file__).resolve().parent;L=HERE.parent;T=L.parent;N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027';B=N/'payloads_r5/h1';sys.path.insert(0,str(HERE))
from native88_gas400_migration_v1 import SOURCES
def H(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(name,value):
 with (HERE/name).open('x',encoding='utf8') as f:json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
cpu=json.loads((HERE/'SOURCE_CPU_NATIVE88_INTEGRATION_ACTUAL.json').read_bytes());assert cpu['passed'] and cpu['checks']==48
qualification=N/'reports/H1_NATIVE87R5_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json';q=json.loads(qualification.read_bytes());bound={}
for role,expected in SOURCES.items():
 row=q['models'][role];final=row['final']
 assert row['passed'] is True and final['SHA']==expected['SHA'] and all(final[k]==expected[k] for k in ('updates','world_updates','policy_updates'))
 assert row['native_fullstate_finite'] and row['frozen_bootstrap']['Adam']==832460
 bound[role]=dict(source=expected,formal_bytes=final['bytes'],formal_metadata=final,whole_CPU_model_passed=True,frozen_RSL_Adam=832460)
put('QUALIFIED_R5_FORMAL_SOURCE_METADATA_BINDING_ACTUAL.json',dict(source_only=True,qualification_report=dict(path=str(qualification),bytes=qualification.stat().st_size,SHA=H(qualification)),sources=bound,no_checkpoint_read_stat_hash_or_copy=True,new400N_target_not_admitted=True))
objective=T/'H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027/reports/ORIGINAL_NATIVE_OBJECTIVE_ON_NEW_RECORDED_MOTION_CPU_ACTUAL.json'
assert objective.is_file()
put('PARENT_NEW_FROZEN_DIAGNOSTIC_OBJECTIVE_EVIDENCE_AND_NO_GO_ACTUAL.json',dict(
 evidence=dict(path=str(objective),bytes=objective.stat().st_size,SHA=H(objective)),
 parent_actual_summary=dict(cases=3,one_fixed_seed_attempt_each=True,seconds_each=5,highest_wheel_bottom_mm=[9.3,13.3],closest_front_edge_remaining_mm=[237,257],only_timeout=True,takeoff=0,cross=0,landing=0,recovery=0,
  request_tracking_div6=[.8139,.8173,.8146],after_age200_position_term_range=[.0196,.0212],other_five_terms_near_one=True,standing_tracking_div6_approx=.834,
  old_native_objective_has_no_direct_actual_wheel_clearance_cross_landing_terms=True,physical_V8_reported_separately=True,
  evidence_scope='root actual new frozen motion plus original objective CPU on those states; helper only indexes the returned text report, does not read raw or recompute'),
 known_objective_alignment_gap=True,unique_causal_explanation_not_proven=True,
 swapping400N_alone_does_not_authorize_same_objective_training=True,independent_effective_own_step_objective_repair_and_admission_required_before_GO=True,
 source_CPU_restore_inheritance_not_skill_or_GO=True,actual_asset_SDK_and_resource_admission_pending=True))
def function_bytes(path,name):
 raw=path.read_bytes();tree=ast.parse(raw);n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name);return b''.join(raw.splitlines(keepends=True)[n.lineno-1:n.end_lineno])
preserved={name:function_bytes(B/'source/native_finalization_own_v3.py',name)==function_bytes(HERE/'native_finalization_own88_gas400.py',name) for name in ('run_native_lifecycle','error_record','emit_error','atomic_json','assert_finite')}
put('UNCHANGED_FINALIZATION_FUNCTION_BYTE_COMPARISON_ACTUAL.json',dict(byteexact=preserved,all_byteexact=all(preserved.values()),AST_exact_also_checked_in48_CPU=True,no_runtime_query=True))
assert all(preserved.values()),'unchanged critical function bytes must remain exact'
text='''# Native88 nominal400 typed native transfer bridge — SOURCE ONLY, frozen

48 new synthetic source/restore/window/publisher/reviewer checks passed. This
is not an installed/admitted source, payload/controller/Task/GO, training,
physical rollout, skill proof or new budget charge. No real PT/model/raw/NPZ,
old USD/mesh binary, actor/WM forward, optimizer step, SDK App/GPU or remote
operation occurred. Qualified source binding reads existing formal CPU JSON
only. Every source-generation error/partial file is preserved in this index.

## Selected source metadata and restoration

Each role is pinned to its **own formal R5** native fullstate:

| Role/seed | SourceSHA | Iteration | WM | Pi |
|---|---|---:|---:|---:|
| h1/27 | ae5ff91877bcfdda72b864a181fdbbbd0c78401cb34591ca507adda44a6632e9 |3317|33170|3253|
| recovery/29 |870e63b6ef41f870109fc1c3b6d9d67fe2f472ca8436145755db5d74a7b8e404|1409|14090|1345|

The existing wholeCPU report confirms these rows and is SHA-indexed in
`QUALIFIED_R5_FORMAL_SOURCE_METADATA_BINDING_ACTUAL.json`; no checkpoint was
opened. Full native WM/Pi/Critic, registered normalizers, all3 optimizer states,
global iteration/WM/Pi, walltime and sim_steps restore through the **byteexact**
previous `same_architecture_native_continuation_candidate_v1.py`. Optimizer
state is deep-copied. Native architecture remains physical73+aux54=127,
static31/obs86/history10/goal146x10/action6. Frozen RSL actor9/critic8/STD6/
17Adam832460 remains a separate literal source witness, not native optimizer
progress. There is no native PPO20Adam rule or old native86 restore.

Fresh4096 physical episode/DR/replay/history/episode counters remain fresh.
No source environment or DR/global RNG state is restored by that primitive;
newly initialized runtime streams remain unchanged and no extra random draws
were added. The original constructor RNG preservation and native collect/noise
algorithm remain. Saved norms restore literally at startup; subsequent original
collect normalization updates remain the original training semantics.

## Candidate files and exact integration

Use **`native_own_fudan88_gas400_training_v2.py`** as the final candidate entry
(`run` API remains runner,n,log_dir,B,J,out,task,go,src,phase). The earlier file
without `_v2` is a preserved generation draft with old metadata labels. The
entry verifies new native source kind/SHA/role/counters, fresh actual plant and
frozen RSL source, builds the original bridge/learner, restores all native
state **before publisher/train**, then attaches optional phase sampling.

`native_wheel_leg_bridge_v4.py` itself is byteexact; control/pack/quaternion/
pre-reset/dynamic54/static31/reward/action forwarding are untouched. The copied
gas SDK checker is the frozen source-only candidate: actual asset composition,
new2000 k/hard limits backend/readback/SDK getter representation remain pending.
This preparation opens no asset or real scene and cannot satisfy those flags.

`vendor_candidate/supermimic_wheel_leg_v3/learner.py` is the sole vendor edit:
`if iteration >= cfg.wm_only_iters` becomes
`if self.native88_migration.allow_policy_update(iteration)`. The entire train
AST apart from that predicate, collect/loss/sampler/WM/Pi/Critic/globalLR/
checkpoint functions are exact. Root must pin this file at the actual vendor
package path; the candidate directory is not an importable full vendor install.

`native88_gas400_migration_v1.py` binds sources and a separate new window:

* Fresh empty replay triggers the original64-control warmup on restored
  start_iteration>0. Global iteration is **not reset**.
* Policy updates remain disabled for new-window iteration0..63. At the first
  allowed update, at least64 complete fresh controls and640 **new** WM optimizer
  steps are required. Original10WM steps/iter and UTD.4 are unchanged.
* With the exact original schedule, the first allowed Pi is at new-window
  iteration64, after226 fresh controls and650 WM steps (64+current iteration's
  WM batch precede Pi). The requirements are minima, not a promise of runtime
  timing. Publication may wait for the next original trace/save boundary.
* Old restored positivePi does not qualify a prefix or FINAL. Source/window/
  global deltas must agree, the new firstPi must carry adaptation evidence,
  and preupdate SHA/bytes/before_control must match the actual trace source.

The only new physical observation is a **one-time readonly** wrapper around
the original `robot.write_data_to_sim`, calling the old callable unchanged.
Original Mod4Env.step applies step-mode gas preload before super.step/write.
This observes actual original qref activation before write, without a setter,
action change or per-control query. A reset boundary may already show target0
for selected environments; demanding qref from all post-reset rows beforePi
would incorrectly reject legitimate original resets. The saved prewrite proof
must exist before the new policy gate can open.

## Publisher, finalization and review

`native_finalization_own88_gas400.py` retains original physical fullsave chain,
atomic stage/verify/hash/publish and all exception handlers. Critical lifecycle/
error/save utility functions are **byteexact** (separate byte comparison JSON)
and their AST equality is also checked. Only the new typed NATIVE_CONTRACT and
in-stage source/window metadata and its verifier are added. The source/window
snapshot is in both checkpoint publication and `UniSuperMimic_changed_plant_migration`,
before verification/hash. No postpublication checkpoint edit is used.

The new contract explicitly sets `original_physics_and_success_unchanged=False`
and `fresh4096_policy_only_bootstrap=False`; it says nominal700→400 changed plant,
native full-model/normalizer/3opt restoration, fresh episode/replay/history,
original numerical clock/solver/geometry/physical V8/command/success retained,
and uncalibrated force curve. It pins parameter-source/actual-asset evidence;
source R5 input still uses its own old contract for strict restore validation.

`RequireNewWindowFinal` calls protected fullsave **first**, then refuses zero
newPi; original lifecycle classifies that error and cannot emit a passed FINAL
merely because inherited globalPi>0. Such a newly saved but unqualified file is
retained with the error and must not be promoted by rc0/filename alone.

`native88_typed_window_reviewer_v1.review_new_native88_decoded` receives an
already decoded new FINAL and exact original formal manifest. It checks strict
new contract/source/window/producer/global deltas/new2000 recipe/formal save
binding. It performs no file load and does **not replace** original whole-model
finite/schema/three-optimizer/frozen-RSL/DR/backend/twohost/source/resource/fee
qualification. Optional phase reader baseline is the restored source iteration,
not fresh0; sampling starts are not completedPi or physical successes.

## Required new Task/GO metadata interface — none written here

New source kind is `MOD4_H1_NATIVE88_GAS400_CHANGED_PLANT_NATIVE_SOURCE_CPU_V1`.
Task source_SHA/source_progress(updates/world_updates/policy_updates)/key/
native_seed bind the role above. source_Adamstep832460 is only the frozen RSL
witness. `source_native_contract` is the exact qualified R5 input contract;
expected source args come from pinned config_for/asdict (strict tuple/list).
Task/GO must match changed_plant700_to_nominal400, parameter-source contract SHA,
actual asset-composition report SHA and original3900/300/3600 boundaries.
The fresh native source/sourceguard/full inventory/worker/controller/owner and
actual sourceSDK/resource installation remain **root integration pending**;
no old same-physics ready branch may dispatch this candidate.

## New parent evidence: no blind400N-only GO

Root completed three fixed old700N R5 mean-policy N1 episodes: only timeout,
takeoff/cross/land/recovery0; highest wheel bottom9.3..13.3mm and closest wheel
front still237..257mm short of the edge. The original e574 objective on the new
recorded states gave request tracking/6≈.8139/.8173/.8146. Afterage200 while
standing on ground, position term≈.0196..0212 but the other5 terms≈1, yielding
tracking/6≈.834. Native reward has no direct actual wheel-clearance/cross/landing
term; physical V8 is separately recorded. This is a concrete objective-alignment
gap, not proof of a unique cause or that gas400 alone fixes anything.

Evidence: `H1_NATIVE87R5_OLD700_FROZEN_DIAGNOSTIC_R2_20261027/reports/ORIGINAL_NATIVE_OBJECTIVE_ON_NEW_RECORDED_MOTION_CPU_ACTUAL.json`;
its exact path/SHA is indexed in the new parent-evidence JSON here. Helper did
not reopen raw trajectories or recompute the actual-motion objective.

**No GO** until an independently effective own-step-objective repair/admission
is complete. The new admission function requires Task andGO both explicitly
bind `independent_own_step_objective_admission_passed=True` and identical
`own_step_objective_qualification_SHA`; absent/current evidence refuses. The
producer also records that SHA. This does not authorize altering objectives in
this source task:9223 reference, native reward, clip, RNG/action-delay and real
physical success are unchanged here. Asset/API/SDK and objective admission are
all still pending. CPU restore/inheritance success is not robot skill or GO.

## Error history and freeze

V1 generator failed on a receipt literal whose WM/Pi fields share a line;
V2 failed because a partial vendor directory already existed. Both original
errors and exact partial copies remain. V3 verified/reused byte-identical
partial files and completed. A separate metadata-label V4 generator rejected
an ambiguous source_SHA substring (also inside bootstrap_task_source_SHA);
V5 used the complete GPU-report anchor and produced final `_v2` entry. These
are local source-generation errors, not model/SDK/physics/training failures.
No old source/report/false was overwritten. All files are in the self-excluding
SHA index; Git ordinary supplement is PENDING root. Stop after this freeze.
'''
(HERE/'HANDOFF.md').write_text(text,encoding='utf8')
for p in HERE.rglob('*.py'):ast.parse(p.read_bytes())
rows=[]
for p in sorted(HERE.rglob('*')):
 if p.is_file() and p.name!='FROZEN_SHA_INDEX_ACTUAL.json':
  assert p.suffix in ('.json','.py','.md','.txt')
  rows.append(dict(relative=p.relative_to(HERE).as_posix(),bytes=p.stat().st_size,SHA=H(p)))
put('FROZEN_SHA_INDEX_ACTUAL.json',dict(frozen_at=datetime.datetime.now().astimezone().isoformat(),source_only=True,synthetic_CPU_checks=48,files_excluding_index=rows,qualified_source_metadata_bound=True,actual_asset_SDK_resources_objective_admission_pending=True,not_a_payload_Task_GO_or_skill=True,no_models_assets_raw_GPU_SDK_or_remote_access=True,errors_preserved=True,Git='PENDING root ordinary supplemental archive'))
print(json.dumps(dict(frozen=True,files=len(rows),index_SHA=H(HERE/'FROZEN_SHA_INDEX_ACTUAL.json'),handoff_SHA=H(HERE/'HANDOFF.md'),all_critical_finalize_functions_byteexact=all(preserved.values())),indent=2))
