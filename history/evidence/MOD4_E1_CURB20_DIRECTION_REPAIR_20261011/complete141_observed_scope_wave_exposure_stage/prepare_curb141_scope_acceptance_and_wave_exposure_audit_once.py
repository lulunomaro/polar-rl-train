"""Complete observed CURB20 scope decision; inspect saved Wave evidence without replay."""
from direction_io import *
import traceback

def main():
    reviewpath=sorted(R.glob('CURB141_SCHEMA_REVIEW_[0-9]*.json'))[-1]
    review=json.loads(reviewpath.read_bytes());assert review['review_complete'] and not review['pending']
    ownpath=sorted(R.glob('EXPOSURE_MATCHED_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json'))[-1];own=json.loads(ownpath.read_bytes())
    tracepath=sorted(R.glob('EXPOSURE424_COMPLETE_TRAINING_TRACE_ACTUAL_[0-9]*.json'))[-1];trace=json.loads(tracepath.read_bytes())
    assert own['passed'] and own['closeout_ready'] and trace['passed']
    g=review['terrain']['groups'];assert all(g[k]['complete_envs']==g[k]['contact_confirmed_complete_envs']==27 for k in ('ascending','descending'))
    c=review['own'];seg=c['unique_completed_segment'];assert len(seg)==1
    final=dict(epoch=time.time(),passed=True,own_final_CPU_report=str(ownpath),root=own['root'],checkpoint=own['own_checkpoint'],
        actual_source_count=424,actual_snapshot_file_count=own['actual_snapshot_file_count'],actual_finite_tensor_count=104,
        formal_target_seconds=900,actual_load_learn_save_exit_seconds=seg[0]['ended_epoch']-seg[0]['started_epoch'],
        actual_updates=own['actual_updates'],actual_control_steps=own['health']['control_steps'],actual_environment_steps=own['actual_environment_steps'],
        health=own['health'],same_geometry_entry_direction_all9_CPU_CUDA_restore_verified=True,
        actual_parent_guardian_child_exited_two_OS_locks_free_active_Sactive_empty=True,unique_original_parent_segment=seg,
        observed_scope_requires_behavior_decision_not_whole_course_finished=True,no_budget_transaction_or_PPO_replay=True)
    save('EXPOSURE_MATCHED_FORMAL_FINAL_ACTUAL_REVIEW.json',final)
    decision=dict(epoch=time.time(),trial_id='CURB141-COMPLETE-OBSERVED20MM-SCOPE-ACCEPTANCE-01',actual_complete_review=str(reviewpath),review_SHA=H(reviewpath.read_bytes()),
        own_fullsave_CPU_PID_unique_closeout=str(ownpath),complete_training_exposure=str(tracepath),checkpoint=own['own_checkpoint'],
        accepted_observed_CURB20_mirrored_scope=True,accepted_scope=dict(height_m=.020,vertical_riser=True,strip_width_m=.150,tile_m=9,approach_m=.4,after_two_wheel_support_m=.200,seed=20260928,num_envs=80,controls=1500,seconds=15,ascending=27,descending=27,standing=26,standing_not_required_to_cross=True),
        ascending_source132=26,ascending_source140=23,ascending_candidate141=27,descending_source140_and_candidate141=27,
        contact_confirmed_complete_equals_position_complete=True,freeze_this_checkpoint_for_accepted_scope_no_more_CURB20_PPO=True,
        negative4pi_source140=3,negative4pi_candidate141=0,positive4pi=8,world_source140=64,world_candidate141=60,
        world_candidate_max_cross_m_s=review['summary']['retention']['world']['candidate']['max_abs_cross'],
        old_skill_diagnostics_do_not_replace_E0_or_CURB_acceptance=True,E0_frozen_gate_untrained=True,
        not_whole_CURB_RM002_STAIRS_E1_MoE_or_permanent_anti_forgetting_graduation=True,
        no_training_causal_ablation_claim=True,final_sensor_bias_observation_difference_disclosed=review['terrain']['sensor_receipt_selected140'],
        next_expert='E1_WAVE',next_axis='review old complete131 failures and full saved training exposure, then independent005 bounded repair from reviewed129 source3c97',
        no_automatic_third_CURB_block_or_higher_curb_geometry=True,no_old_false_raw_cost_prefix_relabel=True,no_new_budget_seconds=0)
    save('CURB141_COMPLETE_OBSERVED_SCOPE_DECISION.json',decision)
    n,w=io.connect_both()
    try:
        code=r'''from pathlib import Path
import json,hashlib,numpy as np,torch,time
torch.set_num_threads(1)
D=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010');j=lambda p:json.loads(p.read_bytes());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=j(D/'reports/e1_wave_G3_isolated_observation_PASSED.json');run=Path(b['run']);ck=Path(b['checkpoint']['path'])
assert h(ck)=='2b4f5a575d3a4d97013b331e215c503ab86e528a63a92d719a3366a684b52284' and b['actual_updates']==6 and b['health']['control_steps']==144
assert b['health']['actual_physics_callbacks']==b['health']['expected_physics_callbacks']==576
a=j(run/'RETENTION_COMMAND_ACTUAL.json');indices=[];total=0;counts={};speed=0.;yaw=0.;distance=None
for name in a['trace_files']:
 p=run/name
 with np.load(p) as z:
  x=z['rows'];assert x.shape[1:]==(20000,16) and np.isfinite(x).all();total+=len(x)
  if distance is None:distance=np.zeros(20000)
  distance+=abs(x[:,:,7]).sum(0)*.01
  for family in range(5):
   mask=x[:,:,10]==family;values=x[:,:,7][mask];counts[str(family)]=counts.get(str(family),0)+int(mask.sum())
   if family==4:speed=max(speed,float(abs(values).max()));yaw=max(yaw,float(abs(x[:,:,9][mask]).max()))
 indices.append(dict(path=str(p),bytes=p.stat().st_size,sha256=h(p),large_original_index_only=True,original_retained=True))
assert total==a['actual_controls']==144 and speed<=.300001 and yaw<=1e-6
assert not torch.cuda.is_initialized()
print(json.dumps(dict(epoch=time.time(),passed=True,old_own_checkpoint_SHA=h(ck),old_formal_run=str(run),saved_full_trace_indices=indices,
 complete_trace_controls=total,simulated_control_seconds_per_environment=1.44,maximum_gentle_nominal_distance_bound_m=.432,
 actual_family_control_histogram=counts,actual_wave_family_max_abs_command_m_s=speed,actual_wave_family_max_abs_yaw=yaw,
 all_environment_command_integral_range_m=[float(distance.min()),float(distance.max())],
 short_training_exposure_is_hypothesis_not_fullroute_contact_or_causal_proof=True,old131_incomplete_results_unchanged=True,
 no_RNG_draw_restore_GPU_PPO_queue_or_budget_write=True)))
'''
        exposure=run(n,code);save('WAVE366_COMPLETE_SAVED_EXPOSURE_CPU_ACTUAL.json',exposure)
    finally:io.cleanup(n,w)
    note='''# Next independent Wave35 exposure repair

Complete CURB141 observed20mm mirrored up/down each27/27 with original1N support, full6000 callbacks/contact-COM-hardware audits, health and validprefixes is accepted and own4247b7003 checkpoint frozen for this exact scope. Negative4pi diagnostic0/8 and world60/64 remain originalfalse; E0 is frozen and gate untrained, so this is not MoE or RM graduation. No third CURB20 block or highercurb automatic training.

Actively prepare the next independent Wave35 repair under004/005. Read WAVE366_COMPLETE_SAVED_EXPOSURE_CPU_ACTUAL and old complete131/selected129 matching evidence. Original sixupdates144controls only1.44s/env is a testable exposure issue, not proof that longer training alone fixes it. Source must remain fullyreviewed1293c97 rather than oldunqualifiedWave2b4 or CURB7b7003. Preserve35mm geometry, alltenwaves/200mm rear support, existing command profile/standing/terrainfamilies/reward/LR/DR/hardware/clock; if an entry or command axis needs change, establish that separate actualcontract rather than combinechanges.

Use a new isolated root/controller/sourcefreeze and explicit0051188000s7extensions admission, oldactualfullsave/PASSED/exits/twofcntl-locks/uniqueclosed ledger boundary. Reuse exact same-scope CPU/SDK/native/PPO/fresh/clock proofs only after SHA and scope identity verification; no oldonce/main or physical evaluation replay, no hotpatch/kill/dual20k/budgetclear/addition. Newsource completeactorcriticstdoptimizer/D0D7/globalnamed/privateCPUCUDA/terraincommand restored, actualCUDAroundtrip/savedsourceepisode+1/independentstorageoutput verified before bounded learning. An admitted new900s exposure observation can be used when duration is the sole approved change; otherwise newaxis missingcontracts must pass first. Ownfullsave/CPU/PID/PASSED/uniqueclosed segment and newunused fourcase actualcomplete fullraw review against129/131 required before furtherPPO/50mm. Do not use CURB skills as Wave graduation.

All saved source/reports/errors/unchangedfalse/raw/cost/workorders/sync/monitor/Gitreceipts must enterGit. Largeweights/rawNPZ/USD/ZIP only actualpath-size-SHA, credentials excluded. Single hourlyACTIVE heartbeat quietpending; E0/SLOPE/CURBacceptedweights/player untouched; no extra monitor or5minSSH/ping. No indefinitehold or queue-only work.
'''
    p=R/'NEXT_WAVE35_EXPOSURE_REPAIR_WORK_ORDER.md';assert not p.exists();p.write_text(note,encoding='utf8')
    print(json.dumps(dict(CURB20_observed_scope_accepted=True,old_Wave_exposure=exposure,next_expert='E1_WAVE')))

if __name__=='__main__':
    try:main()
    except BaseException:
        save('CURB141_WAVE_NEXT_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),old_results_unchanged=True,no_GPU_or_PPO_replay=True))
        raise
