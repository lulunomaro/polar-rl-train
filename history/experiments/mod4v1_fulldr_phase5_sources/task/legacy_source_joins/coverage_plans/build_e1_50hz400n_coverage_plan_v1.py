"""Metadata/source coverage plan ONLY. Never imports runtime, mutates recipe or PT."""
from pathlib import Path
import hashlib,json
C=Path(r'C:\Users\lulu\Desktop\claude\mjcf');T=Path(r'F:\RMPOLAR-RL\mod4v1_experts_fulldr_rm70_20261101');B=Path(__file__).resolve().parent;L=T/'legacy_source_joins'
refs=[]
def tx(p):
 p=Path(p);assert p.suffix in ('.json','.py','.md');assert not p.name.startswith('TRAINING_BUDGET');r=p.read_bytes();ref=dict(path=str(p),bytes=len(r),SHA=hashlib.sha256(r).hexdigest());refs.append(ref);return r.decode('utf-8-sig'),ref
def load(p):
 s,r=tx(p);return json.loads(s),r
c,cr=load(L/'E1_CURB20_SOURCE_JOIN_v1.json');s,sr=load(L/'E1_SLOPE5_SOURCE_JOIN_v1.json');v,vr=load(L/'LEGACY_FROZEN_VARIANT_ROWS_v1.json')
h=C/'MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021/MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027'
_,typedref=tx(h/'NORMAL_H1_PPO86B_400N50_NEW86_SOURCE_PREPARATION_V1/prepare_normal_H1_86B_original20K_typed40050_CPU_UNUSED_once_v1.py')
_,feedbackref=tx(h/'NORMAL_H1_NEW86_PROJECT_WHOLECPU_NATIVE24_ADMISSION_SOURCE_V1/input_overlays/job0/runtime/isaac/mod4/feedback_delay_runtime.py')
snapshot,ssref=load(C/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011/reports/SNAPSHOT_OWN_FORMAL_CPU_1791686991841256500.json')
_,slhelper=tx(C/'MOD4_THREE_EXPERTS_AND_CURB878_EVAL_20261016/train_payload/job1/runtime/isaac/mod4/slope5_full_checkpoint.py');assert slhelper['SHA']==snapshot['manifest']['source_map']['isaac/mod4/slope5_full_checkpoint.py']
curbsupp,curbsuppref=load(L/'CURB141_EXACT_RUNTIME_PACKAGE_SUPPLEMENT_v1.json')
rows=[]
for row in v['rows']:
 if not row['alias'].startswith(('CURB','SLOPE')):continue
 rows.append(dict(alias=row['alias'],source_SHA=row['source_SHA'],selection_evidence=row['selection_evidence'],source_package=row['package_path'],original_policy_hz=100,target_policy_hz=50,original_and_target_feedback_hz=100,original_physics_dt_s=.0025,target_physics_dt_s=.0025,original_gas_k_N_m=3500,target_gas_k_N_m=2000,original_nominal_N_each=700,target_nominal_N_each=400,source_LR=row['saved_LR'],source_Adam_step=row['Adam_step'],state_helpers=row['complete_helpers'],coverage='PLAN_ONLY_NOT_DERIVED_NOT_TYPED_NOT_TARGET_ADMITTED',review_only_not_promoted=row['alias'].startswith('CURB133'),variant_selection='preserve separately; parent actual chosen variant, not maximumiter/rank'))
plan=dict(kind='E1_CURB_SLOPE_50HZ400N_SOURCE_COVERAGE_PLAN_ONLY_V1',permission='SOURCE_PLAN_ONLY_AFTER_H1_SOURCE_FINAL',H1_final_index_SHA='405308b41d79d6d044371d45f987db4ab5a68977bc8a642d8dbe55aa843a5153',variant_rows=rows,
 ordered_layers=[
 dict(layer='A.original_metadata_selection',action='Keep each explicitly frozen checkpoint separate; source current actualremote path/LR/iter UNKNOWN where not in saved receipts; no latest/rank replacement',runtime_changes=False),
 dict(layer='B.future_original20k_to400N50_typed_metadata',action='Not executed. Future separately permitted whole-source CPU read must validate keys/values. Candidate exact four recipe leaf changes below only, inverse all-source proof; no actor/critic/STD17Adam/globalnamed/privateRNG/terrain/retention/history/timestamp tensor changes',reference=typedref),
 dict(layer='C.future_exact_E1_runtime50Hz400N_source_fork',action='Preserve each E1 terrain/direction/independent-scope loader; install50Hz integerclock,100Hz fourphysics sampling hook,20ms actionqueue,gas400 nominal identity. Do not reuse H1 publicjump phase/Step270 env or generic flat as E1 task',reference=feedbackref),
 dict(layer='D.separate_new2c_bae_asset_binding',action='New enhanced asset firstimport/.01m+.01rad/newnominal guard is independent of3500→2000/100→50 migration; restorewhole typed state then ONE originalreset',new_asset=dict(USD_SHA='2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3',contract_SHA='bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'),status='PENDING_NOT_ADMITTED'),
 dict(layer='E.future_actual_sdk_and_independent_scope',action='Original parent permissions/uniqueexistingwriter/resources only; no SDK/Task/GO now. Original geometry scope/reward/hardware and actualtime durations retained in next fresh once; historical consumed native/eval not replayed',new_gate=False)
 ],
 future_candidate_four_recipe_leaves=[
 dict(path='physical_action_delay_state.control_us',old=10000,new=20000),
 dict(path='physical_action_delay_recipe.control_period_us',old=10000,new=20000),
 dict(path='spring_pressure_recipe.nominal_stiffness_N_m',old=3500,new=2000),
 dict(path='spring_pressure_recipe.actual_stiffness_bounds_N_m',old=[3150,3850],new=[1800,2200])
 ],
 explicitly_unchanged=['feedback_delay_recipe.control_period_us=10000 and requested_delay_us=[0,10000] remain100Hz; NEVER change to20ms','physical action delay0/2500/5000us; physics2.5ms/TGS32/4','D5factor/episode/twoCUDA RNG, D6gasdamping3/factors/privateRNG, D7COMdelta/PD factors/privateRNG','Actor35/cleancritic38/actions6/learnedSTD6/17Adam and exact saved LR/iter; no STD reset or model lift','All20k E1terrain/entry/direction/retainedcommand/independent-scope state and privateRNG; no slicing/reconstruction','Queue history targets/timestamps untouched in typedsource; original restore then ONE reset is still authoritative','True original CURB20/150mm and SLOPE5degree/2m geometry, reward parameters and physical SI action scales'],
 runtime_coverage_matrix=[
 dict(component='Clock/PPO discount',planned_source='Original exact E1entry runner_config+physics_clock',review='Keep24 rollout controls; wallphysical rollout .24→.48s; gamma.99→.9801 and lam.95→.9025 per same referenced40050 fork, coefficients/rewarddt handled by originalSDK rates',status='SOURCE_REVIEW_PENDING_NOT_PATCHED'),
 dict(component='Feedback100Hz',planned_source='feedback_delay_runtime.DelaySensorMod4Env._install_feedback_100hz_sampling',review='Sample every4 physicalticks at2.5ms while each50Hzcontrol has8ticks; sourcefeedbackhistory/RNG restored exactly; callback2samples/control',status='REFERENCE_SOURCE_BOUND_NOT_APPLIED'),
 dict(component='CURB141 fullstate',planned_source=curbsupp['local_package_root'],review='curb20_direction_full_checkpoint→entryfullcheckpoint→D7stack; preserveassignment/entrymapSHA/direction state/resetidentity and one sourceepisode+1',status='EXACT424_PACKAGE_JOINED_PLAN_ONLY'),
 dict(component='CURBshared878',planned_source=c['runtime_packages']['shared878']['local_root'],review='distributed_rank_contract is historical onePPO three rank; preserve rank-specific fullstate, not count as separate actors; choose exact parent variant',status='NOT_E1_SLOPE_SUBSTITUTE'),
 dict(component='Independent CURB113/SLOPE50',planned_source=c['runtime_packages']['independent113']['local_root'],review='Keepindependent_expert_scope_state/task_contract and bind_after_restore ordering; do not substitute old141/24b acceptance for neweractor qualification',status='COMPLETE_TRAIN_PACKAGE_REFERENCED_PLAN_ONLY'),
 dict(component='SLOPE24b fullstate',planned_source=slhelper,review='SamehelperSHA as old404source_map confirmed; snapshot_reviewed_payload is overlay notcomplete; exact remainder dependency map needed before any sourcefinal',status='PATH_MISS_PRESERVED_CORRECT_HELPER_IDENTIFIED'),
 dict(component='timeunits/health',planned_source='retention_command_state,retained_flat_command_math,retention_learning_env,E1terrain/direction runtime,clock_training_health,evaldriver',review='Audit hardcoded100Hz/control counters; preservephase_elapsed seconds and physicalroute15s (1500oldcontrols→750newcontrols only for equal15s contract), keeporiginal callbacks/5ms contactbins; healthreport expected=steps*cfg.decimation',status='NO_COUNTER_OR_DURATION_PATCH_EXECUTED'),
 dict(component='newnominal',planned_source='Newasset constructor+genericguard only',review='No known oldPT absolute m/I overwrite bug; protectconstructor and sourcefullrestore→ONE reset, no setparams/inertiaframe guess/FP64 gate',status='PENDING_SEPARATE_ASSET_LAYER')
 ],
 unresolved=['No current human-selected exactCURB/SLOPE variant implicitly chosen','Exact saved LR/storediter/currentremote PT paths UNKNOWN remainexplicit; never fill by math/global latest','Futuretyped model provenance not created; fourleaf candidates require originalsource values/schema then complete inverse proof under separate permission','Remaining exact temporalhardcodes/physics feedback install diff require pervariant source derivation; no universalH1/flat template','No newTargetReady/GPU/fullDR/skill or graduation claim'],
 input_text_SHA=refs,reader_failure='E1_PLAN_READER_R01.json',PT_operations=0,recipe_changes_executed=0,source_runtime_files_changed=0,SSH_SDK_GPU_budget_GO_operations=0,archive='Pendingparent append-only archive; no childcommit/push')
with (B/'CURB_SLOPE_50HZ400N_SOURCE_COVERAGE_PLAN_v1.json').open('x',encoding='utf-8') as f:json.dump(plan,f,ensure_ascii=False,indent=2)
print(json.dumps(dict(status='PLAN_ONLY_NO_RECIPE_OR_SOURCE_PATCH',variant_rows=len(rows),sourceSHA_count=len(refs),path=str(B/'CURB_SLOPE_50HZ400N_SOURCE_COVERAGE_PLAN_v1.json')),indent=2))
