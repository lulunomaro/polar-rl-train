from slope_io import *
actual=json.loads(sorted(R.glob('SLOPE_SNAPSHOT_ACTUAL_[0-9]*.json'))[-1].read_bytes());r=actual['own_reports']
big=r['slope_snapshot_reviewed_discard20k_PASSED.json'];fresh=r['SLOPE_FRESH_PROCESS_SAME_SCOPE_PASSED.json'];gate=r['E1_COMPLETE_PPO_PREFLIGHT_PASSED.json']
assert big['actual_updates']==4 and big['actual_environment_steps']==1920000 and big['health']['actual_physics_callbacks']==384 and big['discarded_preflight']
assert fresh['passed'] and fresh['actual_control_steps']==fresh['actual_additional_PPO_updates']==0 and fresh['saved_source_episode_plus_one_verified'] and fresh['actual_same_SLOPE_terrain_command_private_CPUCUDA_disk_roundtrip_exact']
assert gate['SDK_native_small_exact_reused'] and gate['weights_discarded'] and gate['old402_failed_snapshot_literal_preserved']
seg=big['unique_completed_segment'];assert len(seg)==1
row=dict(epoch=time.time(),new_big_actual_full_PPO_PASSED=big,independent_fresh_same_SLOPE_zero_PPO_PASSED=fresh,originalSDK_native_small_exact_SHA_reused=True,preflight_checkpoint_not_formal_source=True,unique_big_seconds=seg[0]['ended_epoch']-seg[0]['started_epoch'],actual_phase=actual['phase'],formal_source_SHA=actual['own_reports']['E1_STATE.json']['source']['sha256'],formal_target_seconds=300,formal_actual_final_pending=True,no_new_GPU_or_budget_action_by_review=True)
assert row['formal_source_SHA']==SHA
save('SNAPSHOT_COMPLETE_PREFLIGHT_ACTUAL_REVIEW.json',row)
print(json.dumps(dict(big_seconds=row['unique_big_seconds'],fresh_zero_PPO_passed=True,formal_actual_phase=actual['phase'],formal_final_pending=True)))
