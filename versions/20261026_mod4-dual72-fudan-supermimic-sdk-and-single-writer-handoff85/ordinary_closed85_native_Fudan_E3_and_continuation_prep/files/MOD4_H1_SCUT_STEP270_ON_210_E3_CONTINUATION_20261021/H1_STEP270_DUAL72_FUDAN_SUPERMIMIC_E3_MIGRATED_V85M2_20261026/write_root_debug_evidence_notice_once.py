from pathlib import Path
import json,time
N=Path(__file__).resolve().parent;T=N.parent;J=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026';R=N/'reports'
p=R/'ROOT_ACTUAL_SAVED_WM_AND_PHASE_DEBUG_NOTICE_ACTUAL.json'
assert not p.exists()
data=json.loads((J/'root_Fudan_SuperMimic_actual_WM_sensitivity_20261026/ACTUAL_SAVED_NATIVE85_WM_SENSITIVITY_AND_PHASE_CPU.json').read_bytes())
obj=json.loads((J/'root_Fudan_SuperMimic_objective_source_CPU_20261026/ACTUAL_SOURCE_TASK_DISTANCE_ALIAS_AND_HEIGHT_GRADIENT_CPU.json').read_bytes())
snapshot=data['actual_final_snapshot']
v=dict(epoch=time.time(),new_user_debug_request_justified_single_new_purpose_local_WM_CPU_load=True,
 old_qualification_review_not_repeated=True,no_model_hash_raw_GPU_policy_forward_physics_remote_or_budget_change=True,
 actual_model_response=dict(nonzero_action_Jacobian=True,task_reward_gradient_nonzero_at_probes=True,not_real_dynamics_gradient_accuracy=True,reference='root_Fudan_SuperMimic_actual_WM_sensitivity_20261026/ACTUAL_SAVED_NATIVE85_WM_SENSITIVITY_AND_PHASE_CPU.json'),
 final_retained_snapshot=snapshot,
 key_scope='age/request snapshot is not whole-window age or reset statistics; WM probes are latest cached previous action with heading-neutral invariant reconstruction and no worldXY; no real next-state groundtruth',
 source_scheduling=dict(warmup=48,collect_each_iteration=24,world_only_iters=10,first_policy_collection_total=312,replay_capacity_controls=64,
 first_policy_no_reset_replay_frames=[248,311],original_jump_request_age_half_open=[100,180],conditional_missing_first_jump_in_no_reset_replay=True,
 source_evidence='learner605-606,636-640,653-656; bridge227; replay.add/_row; actual first policy312 controls'),
 root_counterexample_summary=obj['proved'],
 future_plan='First reproduce exact replay/phase scheduling with the existing helper. Use preserved native weights/optimizers and resumed iteration to avoid restarting10 world-only iterations; candidate first Pi after48+24=72 controls if admitted. Retain or balance jump-phase replay and log actual phase exposure. Task-relative geometry observability and dynamic-context consistency need separate typed source work, not a blanket current-contract relaxation. No new run or success claim here.',
 no86_GO=True,
 original_reader_issues_appended=[
 'Asked for an already-produced child gradient report at its folder root; actual file was under gradient_attempt_1793017866161662300. No reread/re-execution was done; later final handoff read.',
 'Queried nonexistent old h1_step270_phase_v1.py name; corrected using rg --files to h1_takeoff_progress_phase_v2.py. This was a local source reader error only.',
 'An early listing of the new helper phase directory returned exit1 while that supplement was not yet frozen; no inference of failure or missing training.'
 ],
 web_sources=[dict(url='https://github.com/Motphys/Uni-SuperMimic',kind='primary upstream README checked; learned differentiable WM and goal-conditioned motion tracking, not a promise of success on a new robot')])
p.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
new='''LATEST_ACTUAL_ROOT_CPU_SAVED_WM_PHASE_DIAGNOSED_20261026. Overrides older new-purpose-WM-diagnostic pending statements below, not old saved reports. Human debug request justified one NEW local CPU load of already-qualified85 nativeFINAL, not replay of oldreviewer and not forGit. No modelhash/raw/PTtransfer/actorforward/GPU/physics/remote/budget change. SavedWM action sensitivity and task-reward gradient are nonzero at63 heading-neutral cached-history probes; finite-difference dZ/action agrees~4e-8 median. This proves mathematical responsiveness, not real physics gradient accuracy. Do not claim zero-WM-actionJac or brokenautograd.
Actual85 FINAL retainedage median633;19722/20000(age>=180)=98.61percent,51in100..179,227<100;cachedZmedian.2341/Rzzmedian.9362. Single final snapshot, not wholewindowages/resets. Root source proved fresh training warmup48+11iterations*24=312controls before firstPi;64stepreplay no-reset f248..311 has already discardedjump age100..179. ActualfirstPi312matches. One helper is independently reproducing ring scheduling in a separate frozen supplement, no nestedagent. This is a concrete phase/replay scheduling defect for no-reset trajectories, not proof every env or the unique cause. Prefer correct native continuation preserving680WM/58Pi and globaliteration68 so no repeat10world-onlywarmup; source-only candidate wouldfirstPi72afterfresh48+24, then instrument/balance actualjumpphase coverage. Do not change originalage/reward/softtermination/success merelyto forceevents. Other confirmed missingdistance/dynamicxi modeling gaps need new typedcontract/CPUproof beforeanydeployment; no hotpatch/no86GO yet.
Exact rootactualnotice reports/ROOT_ACTUAL_SAVED_WM_AND_PHASE_DEBUG_NOTICE_ACTUAL.json. New WMdiagnostic entry is CONSUMED, no model reread to add desired stats. The child originalwrongquaternioninput hypothesis is REFUTED by actualSDKxyzw and preserved, neverapplythatfix. Old child pending-JVP plan is historical. All new debugreports/readerrors/singleCPUloadintent and source must ordinaryarchive with alreadyconsumed85trial, no newtag. Currentphase helper/source reports if stillactive must be explicitlypending until frozen, then ordinary capture.
'''
old=(R/'CURRENT_CLOSED85_ZERO_EVENTS_ROOTCAUSE_MONITOR_SOURCE_ACTUAL.txt').read_text('utf8')
(R/'CURRENT_CLOSED85_ACTUAL_WM_PHASE_SCHEDULING_MONITOR_SOURCE_ACTUAL.txt').write_text(new+'\n'+old,'utf8')
print(json.dumps({'notice':str(p),'new_purpose_diagnostic_complete':True,'training_started':False}))
