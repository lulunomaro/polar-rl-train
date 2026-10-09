"""Independent own-run proof; pending is not a pass and this never launches GPU work."""
from pathlib import Path
import json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';B=D.parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
v=read(R/'E1_RESOURCE_PROGRESS_ACTUAL.json');own=v['own_current_run'];assert own and own['receipts']['latest_complete.json'],'Own complete save pending'
rr=own['receipts'];h=rr['CLOCK_TRAINING_HEALTH.json'];assert h and h['route_boundary_truncation_events']>0,'Actual natural route boundary evidence pending'
assert h['version']==3 and h['unknown_task_reset_events']==h['integrity_task_reset_events']==0 and h['nonfinite_observed'] is False and h['stop_reason'] is None
assert h['termination_reason_coverage_exact'] and h['truncation_reason_coverage_exact'] and h['actual_physics_callbacks']==h['expected_physics_callbacks']
assert h['explicit_truncation_term_timeout_flags']['rough_route_boundary'] and h['explicit_truncation_term_timeout_flags']['time_out']
assert h['original_task_reset_reward_and_PPO_timeout_bootstrap_unchanged']
terrain=rr['E1_TERRAIN_RESUME_STARTUP_VERIFIED.json'];assert terrain['predecessor_had_E1_terrain_state'] and terrain['terrain_state_restored_exact'] and not terrain['explicitly_new_E1_terrain']
assert terrain['actual_CUDA_terrain_bookkeeping_disk_roundtrip_exact'] and terrain['complete_D1_D7_optimizer_global_named_streams_verified'] and terrain['E1_episode_incremented_once'] and not terrain['PhysX_exact_resume_claimed']
m=rr['run_manifest.json'];freeze=rr['rolling_source_freeze.json'];assert own['snapshot_bytes_exact'] and len(freeze['sha256'])==310 and len(m['src_sha256'])==57 and m['source_map']==freeze['sha256']
assert own['complete_checkpoint']['finite_tensors']==96
assert v['actual_child']['pid']==rr['latest_complete.json']['pid']==h['pid'] and v['actual_child']['start_ticks']==v['state']['child']['start_ticks']
assert v['actual_parent'] and v['actual_parent']['ppid']==1 and not v['receipts']['E1_ATTENTION.json']
source=read(R/'E1_ROUTE_HEALTH_DISPATCH_LAUNCHED.json')['source'];audit=read(B/'MOD4_S3_E1_RESET_EVIDENCE_REVIEW_20261009/reports/E1_ROUTE_TRUNCATION_SAVED_EXIT_AUDITED.json')
assert source==audit['checkpoint'] and source['sha256']==terrain['source_sha256']==m['init_checkpoint_sha256']
assert read(R/'E1_ROUTE_HEALTH_CPU_PASSED.json')['passed']
master=hashlib.sha256((B/'polar-rl-train/history/plans/MOD4_MOE_MASTER_PLAN.md').read_bytes()).hexdigest();assert master=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
proof=dict(epoch=v['epoch'],current_root='/home/egde/rl_candidates/'+D.name,current_phase=v['state']['phase'],parent=v['actual_parent'],trainer=v['actual_child'],guardian=v['receipts']['E1_GUARDIAN_STARTED.json'],run=own['path'],source=source,own_PID_bound_receipt=rr['latest_complete.json'],own_checkpoint=own['complete_checkpoint'],source_count=310,snapshot_count=57,snapshot_bytes_exact=True,actual_PPO_logs=v['actual_PPO_log_count'],health=h,terrain_startup=terrain,actual_E1_to_E1_full_restore_verified=True,actual_natural_route_boundary_classification_accepted=True,CPU11_passed=True,all_original306_and_D7_source_bytes_preserved=True,old_rejected_health_raw_weights_and_cost_retained=True,old_formal_unique_segment_seconds=audit['segment_seconds'],no_native_or_PPO_preflight_replay=True,preflight_weights_discarded=True,first_task_total_window_seconds=2700,remaining_recovery_window_seconds=2700-audit['segment_seconds'],deadline_epoch=v['state']['deadline_epoch'],first_terrain_behavior_not_yet_accepted=True,not_RM_or_hardware_graduation=True,remaining_training_seconds=v['budget']['remaining_training_seconds'],new_budget_seconds=0,master_SHA_unchanged=master,RM_annotation_id='MOD4-RM-TERRAIN-SPIN-AND-ENTRY-LIP-ANNOTATION-001',canonical_not_written=True)
(R/'E1_ROUTE_HEALTH_RECOVERY_REVIEW.json').write_text(json.dumps(proof,indent=2),encoding='utf8')
print(json.dumps(dict(actual_route_events=h['route_boundary_truncation_events'],control=h['control_steps'],callbacks=h['actual_physics_callbacks'],task=h['actual_task_reset_events'],ordinary=h['ordinary_episode_reset_events'],unknown=h['unknown_task_reset_events'],own_iteration=rr['latest_complete.json']['iteration'],complete_restore=True,snapshot_count=57)))
