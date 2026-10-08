"""Actual paired candidate and next block review; no runtime or budget authority."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
scope=read(R/'D4_TRUE_WORLD_SCOPE_REVIEW.json');actual=read(D.parent/'MOD4_D4_FULL_CONTRACT_20261008/reports/D4_BLOCKS_ACTUAL_VERIFIED.json')
assert scope['decision']['candidate_all_three_complete'] and len(scope['pairs'])==3
for pair in scope['pairs']:
    assert all(pair[k] for k in ('root_exact','q_exact','initial_parameters_exact','runtime_exact','sensor_recipe_exact','feedback_recipe_exact','physical_action_recipe_exact','initial_action_assignments_exact','feedback_final_age_assignment_exact'))
assert all(scope['candidate28633'][k]['facts']['v4']['pass_'] and scope['baseline27575'][k]['facts']['v4']['pass_'] for k in ('flat','spin','world'))
world=scope['candidate28633']['world']['facts'];failed=[row for row in world['world_target']['rows'] if not row['pass_']]
assert len(failed)==1 and failed[0]['env_id']==8 and failed[0]['command_yaw_rad_s']==-2
assert abs(failed[0]['cross_m_s'])<=.05 and abs(failed[0]['observed_yaw_rad_s']+2)<=.2 and failed[0]['along_m_s']>.55
assert failed[0]['along_m_s']-.55<.001
one,two=actual['complete_blocks']['1'],actual['complete_blocks']['2'];h=two['health']
assert one['checkpoint']['sha256']==scope['candidate28633']['world']['result']['checkpoint']['sha256']
assert two['actual_updates']==1058 and two['actual_environment_steps']==507840000
assert h['ordinary_episode_reset_events']==h['closure_episode_reset_events']==1 and h['integrity_task_reset_events']==h['unknown_task_reset_events']==0
assert h['stop_reason'] is None and not h['nonfinite_observed'] and not h['legacy_single_peak_2mm_pass']
assert h['actual_physics_callbacks']==h['expected_physics_callbacks']==h['control_steps']*4==101568
assert len(two['unique_completed_segment'])==1
segment=two['unique_completed_segment'][0];charge=segment['ended_epoch']-segment['started_epoch']
current=actual['current'];assert current['block']==3 and current['init_sha256']==two['checkpoint']['sha256']
assert current['startup']['action_queue_targets_timestamps_both_RNG_restored_exact'] and not current['startup']['explicitly_new_D4_queue']
compact=lambda x:{k:v for k,v in x.items() if k!='world_target'}
review=dict(epoch=time.time(),actual_receipt_epoch=actual['epoch'],scope=scope['scope'],
    baseline27575={k:dict(facts=compact(v['facts']),action_audit=v['action_audit'],result=v['result']) for k,v in scope['baseline27575'].items()},
    candidate28633={k:dict(facts=compact(v['facts']),action_audit=v['action_audit'],result=v['result']) for k,v in scope['candidate28633'].items()},
    original_world_target_pass=False,original_world_target_count=[world['passed'],world['count']],
    original_world_target_failure_rows=failed,one_boundary_along_excess_m_s=failed[0]['along_m_s']-.55,
    pairs=scope['pairs'],old_D3_only_world_preserved_and_not_D4_evidence=True,
    source_and_raw_index=dict(full_derived_scope_review=dict(path=str(R/'D4_TRUE_WORLD_SCOPE_REVIEW.json'),sha256=sha(R/'D4_TRUE_WORLD_SCOPE_REVIEW.json')),returned_JSON_index=scope['returned_JSON_files'],all_raw_flags_cycles_retained=True),
    block1=one,block2=two,block2_already_uniquely_charged_seconds=charge,
    current_block3=dict(parent=actual['actual_owner'],guardian=actual['actual_guardian'],trainer=actual['actual_child'],run=current['run'],active_log=actual['phase']['active_log'],deadline_epoch=actual['phase']['deadline_epoch'],own_checkpoint=current['checkpoint'],startup=current['startup'],snapshot_count=current['snapshot_count'],live_health=current['live_health'],live_health_is_not_final=True),
    actual_tail_adjusted_remaining_seconds=actual['actual_tail_adjusted_remaining_seconds'],budget_snapshot=actual['budget'],
    decision=dict(complete_firstseed_white3_true_D4_behavior_scope_accepted=True,systemic_direction_or_major_retention_failure_observed=False,
        finite_boundary_and_positive_straight_error_retained_for_optimization=True,ordinary_closure_reset_did_not_stop_all_training=True,
        continue_actual_bounded_block3_and_prepare_D5=True,no_new_mechanical_graduation_threshold=True,
        dualseed_allprofile_or_complete_DR_graduation=False,current_block3_behavior_reviewed=False),
    production243_worker_canonical_unchanged=True,no_new_PPO_or_training_signal_or_budget_mutation=True)
(R/'D4_MODEL28633_COMPLETE_MATCHED_REVIEW.json').write_text(json.dumps(review,indent=2),encoding='utf8')
report=f'''# True D4 first candidate compared; second block saved and third block continues

Model28633 and behavior-reviewed27575 were paired on3060 at seed20261002/white_v3/D1–D4/2.5ms32-4. Flat80,spin88,world88 each ran1500 control steps/15s with exact initialroot/30q/parameters/recipes/action assignments and immutable source identity. Originalflat/spin evidence was reused; only correctedActionDelayMod4Env world was used. Each kind matched its own immutable runtime archive. OriginalD3-only world cases remain diagnostic history.

The candidate keeps both pure±4π8/8. World original facts are63/64 versus64/64; the only miss is env8/yaw−2 with along.550547179m/s, exceeding the original.55 edge by{review['one_boundary_along_excess_m_s']:.9f}m/s. Cross−.008127873m/s and yaw−1.992184997rad/s remain within original facts. Worst absolute net cross improves.042694507→.034355543m/s. Candidate±1.5 errors are.058227018/ .013997670m/s versus.039438218/ .019099578; the positive error is retained for optimization. Full circles/window/prefix and all original false flags remain. This is one seed/profile, not allDR graduation or across-GPU dynamic bitexact. The residual supports continued bounded learning and preparation, without a new percentage threshold.

Block2 model29690 is full CPU88 finite, ownPID1243218/243source/24snapshots,1058 updates/25392control/507840000 environment policy steps/101568 exact callbacks. One closure episode env5539/control23132 reset just that environment; peak2.319866559mm and legacy_single_peak_2mm_pass=false remain. There was no integrity/unknown/nonfinite/mimic fault or globalSTOP. The original parent uniquely charged{charge:.9f}s including load/save/exit; this review performs no settlement.

Actualblock3 PID1273629/start61325294 resumed model29690, including bothCUDA actionRNG/queue/targets/timestamps and completeD3 sensor-feedback/optimizer/global-named streams. It then began a new physical episode and clearedstale/rebasedqueue; noPhysX exactresume claim. Its own29775 CPU88/243source/24snapshot save is verified, not a behavior verdict. Deadline{actual['phase']['deadline_epoch']} (about21:14 Beijing). The original controller continues independently of3060. Current budget snapshot{actual['actual_tail_adjusted_remaining_seconds']/3600:.3f}h remaining is time-bound, not future remaining.

No production source, worker, task threshold, model, PPO setting, canonical budget or launch authority changed. D5 preparation continues independently; newscope still requires actual contracts and a unique safe save/exit/two-lock/active boundary.
'''
(R/'D4_MODEL28633_COMPLETE_MATCHED_REPORT.md').write_text(report,encoding='utf8')
print(json.dumps(dict(complete_D4_candidate=True,boundary_failure=failed[0]['env_id'],block2_charge=charge,block3_own_source_verified=True)))
