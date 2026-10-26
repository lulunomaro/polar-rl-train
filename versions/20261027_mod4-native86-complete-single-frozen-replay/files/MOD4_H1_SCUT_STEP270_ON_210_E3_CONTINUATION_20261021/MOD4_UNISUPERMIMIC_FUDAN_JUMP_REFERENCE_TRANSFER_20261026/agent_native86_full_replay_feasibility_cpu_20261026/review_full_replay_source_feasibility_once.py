"""Source/AST only. Does not open any model or saved raw motion artifact."""
from pathlib import Path
import ast,hashlib,json,time
D=Path(__file__).resolve().parent;T=D.parent.parent
B=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2'
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
paths=dict(trace=B/'h1_production_control_prefix_trace_v1.py',retention=B/'h1_prefix_pair_retention_v1.py',
 bridge=B/'source/h1_supermimic_bridge_v1.py',worker=B/'h1_unisupermimic_step270_worker_v1.py',
 learner=B/'source/supermimic_vendor_v2/learner.py',policy=B/'source/supermimic_vendor_v2/networks.py',
 build_env=B/'job0/runtime/isaac/mod4/train_H1_ground_prelaunch_fullstate_v2.py',
 observer=B/'job0/runtime/isaac/mod4/h1_takeoff_progress_environment_v2.py',
 renderer=T/'H1_STEP270_CLOSED83B_SAVED_REPLAY_AFTER_V8_20261026/analyze_render_closed83B_saved_step_timing_CPU_unused_once.py')
text={k:p.read_text('utf8') for k,p in paths.items()}
assert 'if len(self.rows)==24:self.persist()' in text['trace'] and 'physical_callback_replay=False' in text['trace']
assert 'set(range(min(1,len(index))))' in text['retention'] and 'len(index)-2' in text['retention']
assert 'older_pruned_prefixes_not_recoverable_on_later_failure' in text['retention']
assert 'frames=48' in text['renderer'] and 'no physics replay' in text['renderer']
assert 'self.pi.obs_norm.update(obs)' in text['learner'] and 'self.pi.goal_norm.update(goal)' in text['learner']
assert 'self.wm.in_norm.update(' in text['learner'] and 'self.wm.out_norm.update(' in text['learner']
assert 'cfg.scene.num_envs = args.num_envs' in text['build_env']
assert 'env.num_envs==20000' in text['worker'] and 'env.num_envs == 20000' in text['bridge']
candidate=D/'native_frozen_single_attempt_driver_candidate_v1.py';tree=ast.parse(candidate.read_text('utf8'))
compile(tree,str(candidate),'exec') # Compile only; do not execute/import its functions.
for node in ast.walk(tree):
 if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
  assert node.func.attr not in ('collect','learn','backward','zero_grad','update'),ast.dump(node.func)
assert not any(isinstance(n,ast.Name) and n.id in ('H1ControlPrefixTrace','SuperMimicLearner') for n in ast.walk(tree))
value=dict(schema='mod4.native86.full_attempt.source_feasibility.v1',epoch=time.time(),passed_source_AST_only=True,
 source_files=[dict(role=k,path=str(p),bytes=p.stat().st_size,SHA=H(p)) for k,p in paths.items()],
 driver_candidate=dict(path=str(candidate),bytes=candidate.stat().st_size,SHA=H(candidate),actual_executable_admission=False),
 saved_source_conclusions=dict(normal_persist_controls=24,normal_policy='first1_latest2_complete_pairs_plus_incomplete_and_current_failure',
  longest_guaranteed_late_contiguous_controls=48,late_contiguous_seconds=.48,first_segment_seconds=.24,
  middle_raw_may_be_pruned=True,full_attempt_reconstructable_from_retention_index=False,
  raw_is_control_rate_not_full_physics_callbacks=True,saved_kinematic_renderer_is_not_FINAL_policy_evaluation=True,
  no_actual_raw_file_inventory_or_reads_performed=True),
 frozen_attempt_boundary=dict(source='latest_formal_CPU_qualified_NATIVE_FINAL_after86B_close_not_PPO_or_preupdate',
  physical_scope='fresh_single_env_using_original_build_env_and_reset; no20k_D0_D7_state_reshape',
  smallN_source_factory_parameterized=True,smallN_actual_SDK_and_DR_profile_admission=False,
  inherited_witness_ids_include_1_2_3=True,do_not_enable_original_h1_capture_for_N1=True,
  actor_inputs=[128,10,73,6],exact_named30_order_required=True,exact_partial_reference_runtime_contract_required=True,
  no_training_main_learn_collect_or_WM=True,no_normalizer_updates=True,post_state_literal_immutability_required=True,
  stop='first_actual_done_or_original_success_or10seconds; cap explicitly censored',
  one_seed_one_episode_no_retry_or_best_case_selection=True),
 no_model_PT_raw_NPZ_read_hash_copy=True,no_actor_forward_physics_GPU_SSH_Git_ledger=True,
 old_frozen_directories_unchanged=True,pending=['latest86B formal native source qualification','actual single-env SDK/fresh reset and physical profile readback',
 'independent root resource/evaluation transport protocol','actual native frozen attempt and camera/render delivery'],
 archive_status='pending root ordinary source supplement')
path=D/'reports/FULL_NATIVE_REPLAY_SOURCE_FEASIBILITY_AST_ACTUAL.json'
with path.open('x',encoding='utf8') as stream:json.dump(value,stream,indent=2,allow_nan=False)
print(json.dumps(dict(passed_source_AST_only=True,report=str(path),driver_SHA=H(candidate),actual_SDK_or_rollout=False)))
