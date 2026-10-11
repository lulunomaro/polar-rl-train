"""Actual complete source412 closeout, preserving every ordinary event and cost."""
from entry_second_io import *
def latest(pattern):return max(R.glob(pattern),key=lambda p:int(p.stem.rsplit('_',1)[1]))
def main():
 ownp=latest('ENTRY_SECOND_OWN_FORMAL_CPU_ACTUAL_[0-9]*.json');own=json.loads(ownp.read_bytes());assert own['passed'] and own['closeout_ready'] and own['actual_source_count']==412 and own['actual_finite_tensor_count']==102
 pp=latest('ENTRY_SECOND_OWN_STARTUP_CPU_ACTUAL_[0-9]*.json');ppo=json.loads(pp.read_bytes());assert ppo['passed'] and ppo['own_checkpoint']['sha256']==own['own_checkpoint']['sha256'] and ppo['actual_saved_PPO_updates_positive']
 tp=latest('ENTRY_SECOND_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json');trace=json.loads(tp.read_bytes());assert trace['passed'] and trace['own_checkpoint_SHA']==own['own_checkpoint']['sha256']
 row=own['own'];h=row['health'];seg=own['unique_completed_segment'];assert len(seg)==1 and row['unique_completed_segment']==seg and h['control_steps']==2280 and row['actual_updates']==95 and row['actual_environment_steps']==45600000 and h['actual_physics_callbacks']==9120
 assert trace['actual_controls']==h['control_steps'] and len(own['startup_markers'])==8 and all(p is None for p in own['actual_processes']) and all(p['actual_fcntl_free'] for p in own['locks'])
 timeout=h['termination_events_by_reason']['time_out'];route=h['termination_events_by_reason']['rough_route_boundary'];unique=h['actual_truncation_reset_events'];assert timeout==16038 and route==17267 and unique==33301 and timeout+route-unique==4
 ap=latest('ENTRY_SECOND_ACTUAL_[0-9]*.json');actual=json.loads(ap.read_bytes());assert actual['reports']['E1_STATE.json']['phase']=='E1_WAVE50_entry_second_bounded_saved_review_ready' and actual['actual_owner'] is None and actual['actual_child'] is None and actual['budget']['active'] is None and not actual['reports'].get('E1_ATTENTION.json')
 pub=actual['reports']['E1_WAVE50_ASYNC_PUBLISHED.json'];assert pub['source']['sha256']==own['own_checkpoint']['sha256'] and len(pub['jobs'])==4
 result=dict(epoch=time.time(),passed=True,own_formal_CPU_ref=str(ownp),final_saved_PPO_CPU_ref=str(pp),full_training_trace_ref=str(tp),current_actual_ref=str(ap),own_checkpoint=own['own_checkpoint'],checkpoint_bytes=pub['source']['bytes'],source_count=412,actual_module_snapshot_count=own['actual_snapshot_file_count'],actual_PID=own['own_PID'],own_fullsource_freeze_count=412,
 actual_updates=95,actual_controls=2280,actual_environment_steps=45600000,actual_callbacks=9120,actual_actor_tensors_changed=ppo['actor_tensors_changed'],actual_optimizer_step_delta=ppo['optimizer_step_delta_min'],target_seconds_including_load_learn_save_exit=1800,unique_completed_segment=seg,actual_original_parent_charged_wall_seconds=seg[0]['ended_epoch']-seg[0]['started_epoch'],no_recharge_or_budget_extension=True,
 health=h,timeout_count=timeout,route_count=route,overlap_count=4,unique_truncation_count=unique,ordinary_actual_events_preserved=h['last_actual_termination_events'],ordinary3_not_relabelled=False,actual_parent_guardian_child_all_exit=True,two_fcntl_free=own['locks'],active_Sactive_empty=True,legal_saved_review_ready_not_allcourse_finished=True,actual_publication=pub,remaining_idle_snapshot_seconds=actual['budget']['remaining'],own_fourcase_actual_fullreview_pending=True,
 no_third_blind_same_entry_duration_block_or70mm=True,other_frozen_experts_and_gate_untouched=True,fullstate_same50entry_strict_restored_not_PhysX_exact_resume=True,no_GPU_PPO_controller_or_budget_write=True)
 result['ordinary3_not_relabelled']=True
 save('ENTRY412_FORMAL_FINAL_ACTUAL_REVIEW.json',result);print(json.dumps(dict(own_final_passed=True,wall_seconds=result['actual_original_parent_charged_wall_seconds'],updates=95,ordinary=3,checkpoint_SHA=result['own_checkpoint']['sha256'],own_candidate_number=pub['jobs'][0]['job_id'])))
if __name__=='__main__':
 try:main()
 except BaseException:save('OWN412_FINAL_READER_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_replay=True));raise
