from pathlib import Path
import ast,hashlib,json,time
S=Path(__file__).resolve().parent;T=S.parent;N=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026';R=S/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 R.mkdir();review=N/'reports/THREE_GPU86B_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json';cpu=json.loads(review.read_bytes());assert cpu['passed'] and cpu['native_method']['passed']
 collected=json.loads((N/'reports/THREE_GPU86B_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json').read_bytes());assert collected['actual_finite_transport_returned'] and collected['all_three_node_collection_passed'] and collected['original_canonical_cost_settled']
 detached=json.loads((N/'reports/THREE_GPU86B_ACTUAL_OWNER_NODES_DETACHED.json').read_bytes());native=cpu['native_method'];model=native['final']
 assert model['SHA']=='3a61af6db47990cf96b281fd628d6baffea04f37c5255451f52feb96ac2a7e45'
 order=json.loads((N/'current_three_closed_text/e2/job0/production/NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json').read_bytes())
 A=T/'MOD4_UNISUPERMIMIC_FUDAN_JUMP_REFERENCE_TRANSFER_20261026/agent_native86_full_replay_feasibility_cpu_20261026'
 index=A/'FROZEN_NATIVE_FULL_ATTEMPT_FEASIBILITY_INDEX.json';assert H(index)=='c7306bc5c604a8f1dd7dd82865db776dafe3ff3bfc8851bd6f7258a424ab61cb'
 for row in json.loads(index.read_bytes())['files']:
  p=Path(row['path']);assert p.resolve().is_relative_to(A.resolve()) and H(p)==row['SHA'] and p.stat().st_size==row['bytes']
 driver=A/'native_frozen_single_attempt_driver_candidate_v1.py';assert H(driver)=='9ab29554071a3b4012bf22c3791a916ec681b20db60e87a0539aa1e20b015413'
 with (S/'driver.py').open('xb') as f:f.write(driver.read_bytes())
 entry=S/'native86_frozen_single_sdk_entry_v1.py';ast.parse(entry.read_bytes());ast.parse(driver.read_bytes())
 C='/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026'
 q=dict(schema='mod4.qualified_native86.frozen_single_attempt.v1',epoch=time.time(),source_root=detached['roots']['e2'],old_owner_root=detached['owner_root'],
  source_run_id=detached['run_id'],model={k:model[k] for k in ('path','bytes','SHA')},source_CPU_report_SHA=H(review),producer=native['producer'],
  remote_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1native86_complete_single_replay_20261027r1',
  GPU_UUID=detached['specs']['e2']['GPU_UUID'],canonical=C+'/TRAINING_BUDGET_10H.json',
  locks=[C+'/native_floor_supervisor.lock',C+'/autonomy_controller.lock',detached['specs']['e2']['private_lock'],'/home/lc01/Zonglin Li/zonglin2/state/finite_environment_validation.lock'],
  ordered_joint_names=order['actual_robot_joint_names'],runtime_objective_contract_SHA=native['producer']['runtime_objective_contract_SHA'],
  driver_SHA=H(driver),entry_SHA=H(entry),one_frozen_native_policy_attempt_only=True,no_training_or_optimizer_or_normalizer_update=True,no_budget_write=True,
  fresh_single_env_not_original_training_trajectory_replay=True,action_mode='deterministic_native_mean',max_sim_seconds=10.,first_done_or_success_stops=True,
  user_request='完整回放一次经过supermimic后的轮腿上台阶现在最成熟情况',human_requested_new_full_policy_test_after_saved_trace_scope_insufficient=True)
 with (S/'BINDING.json').open('x',encoding='utf8') as f:json.dump(q,f,ensure_ascii=False,indent=2)
 with (R/'QUALIFIED_NATIVE86_SINGLE_REPLAY_SOURCE_BOUND_NOT_EXECUTED_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),passed_source_preparation=True,source_model=q['model'],source_CPU_report=str(review),source_CPU_report_SHA=q['source_CPU_report_SHA'],driver_frozen_bytes_exact=True,root_entry_source_compiled=True,actual_N1_SDK_policy_GPU_replay_not_executed=True,config=q),f,ensure_ascii=False,indent=2)
 print(json.dumps(dict(source_prepared=True,formal_native_iteration=137,policy_updates=127,actual_replay_not_started=True)))
if __name__=='__main__':main()
