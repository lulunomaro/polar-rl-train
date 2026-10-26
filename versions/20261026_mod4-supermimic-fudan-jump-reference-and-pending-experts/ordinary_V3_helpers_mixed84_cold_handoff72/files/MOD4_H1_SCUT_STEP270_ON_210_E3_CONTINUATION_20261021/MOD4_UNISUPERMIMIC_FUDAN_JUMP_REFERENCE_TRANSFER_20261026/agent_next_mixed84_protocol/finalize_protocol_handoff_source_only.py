"""Finalize source-only handoff and a deliberately pending root input document."""
from pathlib import Path
import difflib
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent
J=HERE.parent
REF=J/'agent_reference_retarget_cpu'
PROOF=REF/'ACTUAL_PARTIAL_H1_OBJECTIVE_CPU_PROOF_V3_1793006856598755100'
read=lambda path:json.loads(Path(path).read_bytes())
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
source_proof=read(PROOF/'ACTUAL_REFERENCE_H1_MDP_CPU_PROOF_RESULT.json')
assert H(PROOF/'ACTUAL_REFERENCE_H1_MDP_CPU_PROOF_RESULT.json')=='8761ebdcd7ce6a2c9e9e7a087237145a2f7e8bd641308060dc1ebc6a22d1c148'
contract_path=PROOF/'PARTIAL_REFERENCE_OBJECTIVE_OFFLINE_CPU_CONTRACT_V3.json'
contract=read(contract_path)
assert H(contract_path)=='ee372360ced1fcd0eef6d4c8c7258495ecba99bcd6b0e2ad2c45a7154d6dcecd'
adapter=REF/'supermimic_reference_adapter_v1.py'
assert H(adapter)=='0994762dbf8a78a0f44db03ac91796963e6be9fcd177e8ceecd5159748c8f476'
lifecycle_dir=J/'agent_native_finalization_cpu'
lifecycle_report=lifecycle_dir/'cpu_attempts/attempt_1793003350386701200_01ad0c0c/CPU_LIFECYCLE_TESTS_ACTUAL.json'
lifecycle=read(lifecycle_report)
assert lifecycle['passed'] and lifecycle['passed_count']==lifecycle['count']==21
module=lifecycle_dir/'native_finalization_v1.py'
assert H(module)==lifecycle['source_SHA']['native_finalization_v1.py']
remote_report=J/'reports/FUDAN_ORIGINAL_JUMP_CPU_REFERENCE_REMOTE_RESULT_ACTUAL.json'
remote=read(remote_report)
assert remote['all_assets_twoend_verified'] and remote['reference_returncode']==0 and remote['own_reference_child_actual_out']
asset=next(row for row in remote['texts'] if row['relative']=='PINNED_ASSETS_TWOEND_FULL_SHA_ACTUAL.json')
artifact=source_proof['native_reference']
assert artifact['SHA256']=='0b9d642f3530ad55bd353c19918a0778378746ecc250e1f22c10c58b8c095c94'
from mixed84_protocol_v1 import validate_objective_contract,FUDAN_TEACHER_ONNX_PINS,SOURCES
validate_objective_contract(contract)

# Metadata/source pins below are actual, but bridge integration/auth remain
# explicitly pending. This file can neither pass the binder nor imply GO.
bundle=dict(status='PENDING_ROOT_NATIVE_BRIDGE_SOURCE_PINS_AND_REVIEW',
    reference=dict(passed=True,teacher_CPU_rollout_actual=True,
        repository_commit='8204e853dfd2ed06d85a322e1a998c3d20a3be2c',original_teacher_ONNX_used=True,
        required_assets_complete=True,selected_original_source_timestep_s=.002,
        source_is_partial_standing_jump_not_H1_step270_or_stable_recovery_proof=True,
        not_our_policy_inference=True,not_forced_action_or_trajectory_clamp=True,
        teacher_ONNX_SHA=FUDAN_TEACHER_ONNX_PINS['jump'],teacher_ONNX_pins=FUDAN_TEACHER_ONNX_PINS,
        asset_provenance_SHA=asset['SHA'],reference_artifact_SHA=artifact['SHA256'],
        reference_provenance_report_SHA=H(remote_report),
        artifact_relative='reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73_PHASE_V3.json',artifact_bytes=artifact['bytes']),
    adapter_CPU=dict(passed=True,CPU_only=True,CUDA_initialized=False,actual_reference_loaded=True,
        reference_reader_schema_verified=True,reference_artifact_SHA=artifact['SHA256'],
        source_robot='Fudan_wheel_legged',target_robot='MOD4_H1',state_joints=30,actions=6,
        no_forced_actions=True,original_goal_machine_unchanged=True,
        retargeting_protocol_SHA=H(REF/'own_usd_closed_chain_ik_v1.py'),
        retargeting_protocol_pin_scope='own_USD_closed_chain_IK_source; raw retarget attempts remain separately archived',
        adapter_source_SHA=H(adapter),report_SHA=H(PROOF/'ACTUAL_REFERENCE_H1_MDP_CPU_PROOF_RESULT.json'),
        objective_contract_SHA=H(contract_path),
        raw_report_status=source_proof['status'],raw_report_pending=source_proof['pending'],
        actual_runtime_SDK_readback=False),
    objective_contract=contract,
    candidate_pins=dict(bridge_source_SHA=None,finalization_source_SHA=H(module),
                        native_CPU_source_SHA=H(HERE/'test_native_h1_fudan_reference_CPU_v84_TEMPLATE.py')),
    finalization_CPU=dict(passed=True,CPU_only=True,passed_count=21,count=21,
                         finalization_source_SHA=H(module),report_SHA=H(lifecycle_report)),
    native_bootstrap_source_SHA=SOURCES['h1']['SHA'],native_bootstrap_Adam=829700,
    native_bootstrap_kind='qualified83B_H1_frozen_PPO_core_only',
    old82Q_native_prefix_or_unknown_final_used=False,candidate_V10_reward_used=False)
candidate_files={
    'source/h1_supermimic_bridge_v1.py':dict(local_path=None,SHA=None,reason='Root integrates V3 MDP plus native finalization and actual runtime-order hook'),
    'source/native_finalization_v1.py':dict(local_path=str(module),SHA=H(module)),
    'source/supermimic_reference_adapter_v1.py':dict(local_path=str(adapter),SHA=H(adapter)),
    'source/own_usd_closed_chain_ik_v1.py':dict(local_path=str(REF/'own_usd_closed_chain_ik_v1.py'),SHA=H(REF/'own_usd_closed_chain_ik_v1.py')),
    'h1_unisupermimic_step270_worker_v1.py':dict(local_path=str(HERE/'h1_unisupermimic_step270_worker_v84_TEMPLATE.py'),SHA=H(HERE/'h1_unisupermimic_step270_worker_v84_TEMPLATE.py')),
    'test_native_h1_fudan_reference_CPU_v84.py':dict(local_path=str(HERE/'test_native_h1_fudan_reference_CPU_v84_TEMPLATE.py'),SHA=H(HERE/'test_native_h1_fudan_reference_CPU_v84_TEMPLATE.py')),
}
integration=dict(status='PENDING_ROOT_REVIEW_NO_BINDING_EXECUTED',
    source_only_authorization=dict(approved=False,no_new_training_or_GO_authorization=True),
    reference_bundle=bundle,native_candidate_files=candidate_files,
    reference_artifact_path=artifact['path'],reference_provenance_path=str(remote_report),
    adapter_CPU_report_path=str(PROOF/'ACTUAL_REFERENCE_H1_MDP_CPU_PROOF_RESULT.json'),
    objective_contract_path=str(contract_path),finalization_CPU_proof_path=str(lifecycle_report),
    actual_target_source_SDK_native_CPU=None,ready=False,admitted=False,GO=False,
    normalized_fields_are_source_CPU_only_not_runtime_or_skill_admission=True)
with (HERE/'MIXED84_REVIEWED_INPUT_MAPPING_PENDING_V3.json').open('x',encoding='utf8') as stream:json.dump(integration,stream,indent=2)

pairs={
    'normal_h1_source_guard_TEMPLATE.py':'83B_h1_closed_production_continuation_CPU_v2.py',
    'normal_recovery_source_guard_TEMPLATE.py':'83B_recovery_original_account_policy50_source_CPU.py',
    'owner_controller_templates/three_slot_common_v1.py':'83B_three_slot_common_v1.py',
    'native_controller_templates/three_real_gpu_resource_v1.py':'83B_three_real_gpu_resource_v1.py',
    'deploy_mixed84_original_writer_TEMPLATE.py':'82Q_deployer.py',
    'observe_mixed84_baselines_native_first_finite_TEMPLATE.py':'82Q_first_observer.py',
    'collect_mixed84_finals_original_cost_TEMPLATE.py':'83B_collector.py',
    'review_mixed84_baselines_native_fullstate_CPU_TEMPLATE.py':'83B_reviewer.py',
    'h1_unisupermimic_step270_worker_v84_TEMPLATE.py':'82Q_native_worker.py',
}
for target,original in pairs.items():
    old=(HERE/'source_snapshots'/original).read_text('utf8');new=(HERE/target).read_text('utf8')
    name='FINAL_'+target.replace('/','_')+'.diff'
    with (HERE/'diffs'/name).open('x',encoding='utf8') as stream:
        stream.write(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=original,tofile=target)))
tests=[read(path) for path in sorted((HERE/'reports').glob('SOURCE_PROTOCOL_CPU_*_ACTUAL.json'))]
assert tests[-1]['passed'] and tests[-1]['passed_count']==9
entries=[name for name in candidate_files if name not in ('source/h1_supermimic_bridge_v1.py',)]
report=dict(epoch=time.time(),attempt_id='mixed84-source-protocol-final-handoff',
    source_protocol_passed=True,latest_pure_metadata_AST_checks='9/9',
    tests=[dict(attempt_id=x['attempt_id'],passed=x['passed'],passed_count=x['passed_count'],count=x['count']) for x in tests],
    initial_AST_false_preserved=True,initial_CRLF_dispatch_omission_fixed_without_live_execution=True,
    root_circularity_correction_preserved=True,
    source_snapshots_scope='Original source bytes, initial generated/pre-hardening revisions, rejected common, pre-circularity correction and pre-V3 snapshot, final exact diffs/current sources. Early intermediate reports did not store per-file source SHAs; no false reconstruction is claimed.',
    actual_V3_native_artifact_metadata=artifact,actual_adapter_source_SHA=H(adapter),
    actual_reference_CPU_report_SHA=H(PROOF/'ACTUAL_REFERENCE_H1_MDP_CPU_PROOF_RESULT.json'),
    actual_offline_objective_contract_SHA=H(contract_path),
    preGO_scope='Fresh actual target source/SDK/native CPU, actual reference/provenance and OFFLINE named mapping/loss only',
    runtime_scope='After env construction, before first physical step/Pi: actual robot.joint_names check/reorder and actual runtime contract/order receipts',
    baseline_sources=dict(H1=SOURCES['h1'],E3=SOURCES['recovery']),native_bootstrap=SOURCES['h1'],
    physical_displaced_resource='healthy closed83B normalE2 root/allout; separate from sourceH1',
    paused_normal_E2=SOURCES['e2'],previous_owner=dict(pid=1493851,creation=1792994651.61),
    closed_fee=10943.796510219574,closed_remaining_snapshot=595256.8240613937,
    preserved=dict(cap_seconds=3900,save_seconds=3600,exit_seconds=300,
        strict_remaining=86412.86069250107,H1_native_H1_free_MiB_strict=15669,E3_free_MiB_strict=7000,
        RAM_bytes_strict=8*1024**3,postcopy_disk_bytes_strict=25*1024**3,runtime_save_floor_bytes=8*1024**3,
        metadata_bytes=2536,metadata_SHA='c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e',
        charge_values_AST_exact=True,owner_node_network_bytes_exact=True,per_file_copy_loop_path_containment_AST_exact=True),
    ready=False,admitted=False,GO=False,templates_executed=False,
    no_model_binary_old_raw_NPZ_USD_content_read_or_hash=True,
    no_network_remote_GPU_environment_actor_forward_optimizer_training_or_budget_ledger_locks_Git_action=True,
    no_mutation_of_completed_agent_native_finalization_cpu=True,
    all_unfinished_experts='Parent queue preserved; first H1 only, no all-experts training claim',
    candidate_V10_reward='HELD_NOT_DEPLOYED',actual82Q_cause='UNPROVEN',
    tool_error_append='One attempted apply_patch had an empty second hunk/typo path and was rejected atomically; corrected patch then applied.',
    Git_status='LOCAL_PENDING_ROOT_NEXT_PHASE_ARCHIVE')
with (HERE/'reports/FINAL_MIXED84_SOURCE_PROTOCOL_HANDOFF_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(report,stream,indent=2)

handoff=f'''Concrete mixed84 source templates are complete and UNEXECUTED. Latest pure metadata/AST checks passed9/9. The original7/8 CRLF-dispatch failure, rejected source, correction, later8/8 and9/9 reports remain. No model/payload copy, TASK/GO, binder/deployer/observer/collector/reviewer execution, network, GPU, environment, inference, training, budget/ledger/lock or Git mutation occurred.

The V3 reference is470968bytes, SHA0b9d642f3530ad55bd353c19918a0778378746ecc250e1f22c10c58b8c095c94. Adapter source is0994762dbf8a78a0f44db03ac91796963e6be9fcd177e8ceecd5159748c8f476. The actual offline proof is8761ebdcd7ce6a2c9e9e7a087237145a2f7e8bd641308060dc1ebc6a22d1c148; exact offline contract isee372360ced1fcd0eef6d4c8c7258495ecba99bcd6b0e2ad2c45a7154d6dcecd. No packed-reference/NPZ/model content was read here. Protocol requires objective schema mod4.supermimic.partial_reference_objective_contract.v2 and partial phase schema mod4.supermimic.partial_step270_phase_contract.v1. Demo Z/Vz ends at measured reference.860s/ownage136; post-ascent support height is a separate own nominal+.270 task target at edgeX.35. Old V2/analytic/composition-only loss is rejected.

Root execution/integration order:

1. Keep agent_native_finalization_cpu immutable. In a NEW candidate source location, combine its bridge/save candidate with the frozen V3 adapter. After H1Bridge reads the actual constructed robot and before SuperMimicLearner/first collection, call ref.for_sdk_joint_order(robot.joint_names), install PartialReferenceImitationMdp, and retain all original physical V8/commands/success/real-transition WM/control/trace/retention code. The preGO CPU path uses ref.for_offline_joint_order(ref.joint_names).torch_provider('cpu',offline_cpu_only=True) with SDK-readback=false; it never waits for a postGO receipt.

2. Before any first physical step/Pi, write production/NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json with actual_runtime_order_readback=true, complete_named_permutation=true, before_first_physical_step_and_Pi=true, actual_robot_joint_names30 list, reference_artifact_SHA, and runtime_objective_contract_SHA. Write production/NATIVE_FUDAN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json from the actual reordered mdp.contract_manifest(). Runtime manifest must say provider_execution_scope=runtime_actual_SDK_named_mapping_required and sdk_joint_order_verified=true. Use the real actual joint-name list, never the offline list relabeled as SDK.

3. Add publication producer fields reference_artifact_SHA, adapter_CPU_report_SHA, objective_contract_SHA (offline fixed pin), runtime_objective_contract_SHA (actual runtime receipt). Keep the existing bridge_source_SHA/finalization_source_SHA/bootstrap_task_source_SHA and unique run/save tokens. The final reviewer requires all of them. The native core PPO bootstrap is qualified83B H1 SHA8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6/Adam829700, frozen. No82Q prefix or unknown final promotion.

4. Edit a NEW copy of MIXED84_REVIEWED_INPUT_MAPPING_PENDING_V3.json. Fill only the new integrated bridge path/SHA (and optional reviewed integration helper), verify all existing actual source/report/artifact pins, set its source-only approval from the existing root authority, set reference_bundle.status=ACTUAL_REFERENCE_AND_ADAPTER_CPU_VALIDATED, and top status=ROOT_REVIEWED_ACTUAL_INPUTS_READY_FOR_NEW_BINDING. Its current pending/null/false values deliberately reject. It preserves raw actual CPU pending items and does not claim runtime/skill admission.

5. Execute the binder ONCE from this agent folder, using an absolute reviewed input path:
   C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe {HERE/'bind_mixed84_qualified83B_sources_TEMPLATE.py'} REVIEWED_INPUT.json
   This was NOT run here. It creates only the new local stage H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026 and copies the concrete scripts into that stage. Preserve known qualified binary producer SHAs during planning; actual installed validation retains the original full-file integrity checks. Do not rerun the already consumed source-template generators; current templates and FINAL diffs are the reviewed revision.

6. Root reviews and adds exact new basenames to its next same-session transport whitelist144+. Use stage/deploy_mixed84_original_writer_TEMPLATE.py once only when independently authorized. It reuses the original transport/HMAC/pins/owner/node/charge_values, original per-file transfer loop/path containment, healthy closed83B source/cost/owner boundary, fresh original resource locks, target SDK/source CPU, test_native_h1_fudan_reference_CPU_v84.py and strict original valid_ready. Native CPU reuses the actual21/21 lifecycle proof, checks V3 partial loss/static dimensions on tensors, and labels ordering OFFLINE. It does not create a preGO/runtime-order cycle. No GO can result from the current pending input document.

7. New source210 H1 and target72 E3 are normal same-V8/read-only-journal baselines from83B; only their source-guard role and E3 saved-Adam assertion change. Native logicale2 uses H1's frozen bootstrap while its physical previous root is successful83B normalE2, not failed82Q. The normalE2 source SHA72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f/Adam857460 stays paused and qualified. Baseline E3 starts860800 SHA68d95156fc5dd294e43b21ad39691da8f1df1c5b85667db3001335796521ea49. Previous owner1493851/create1792994651.61 and closed fee10943.796510219574/closing595256.8240613937 are historical snapshots; fresh original canonical/resource evidence still governs deployment.

8. Run stage/observe_mixed84_baselines_native_first_finite_TEMPLATE.py once for actual GO/UUID/pid-creation/argv/baseline PPO/native Pi and runtime-order/objective receipts. Then use stage/collect_mixed84_finals_original_cost_TEMPLATE.py only at the original final900s closure boundary, followed by stage/review_mixed84_baselines_native_fullstate_CPU_TEMPLATE.py. Collector/reviewer keep normal models={{h1,recovery}}, native H1 separately, and all3 original slot costs; no native source is called E2 production or skill graduation. No old/missing/stale FINAL file is promoted.

Ordinary native own deadline is not inherently a SavedStop failure in the captured source route: worker replaces rescue_training.learn before train.main imports it, and physical save chain does not call rescue_training.install. OwnCompleteSavedStop can reach a fresh full physical+native save normally. If another route adds an inner SavedStop wrapper, that path stays explicit error-only because upper physical/task/native augmentation may be incomplete. No safe outer acknowledgment wrapper exists in the captured chain, and no bypass was added. Actual82Q cause remains UNPROVEN.

Preserved constants:3900 lifecycle/3600 save/300 exit, strict remaining>86412.86069250107, empty H1/nativeH1>15669MiB and E3>7000MiB, RAM>8GiB, postcopy disk>25GiB, runtime fullsave8GiB; exact metadata CRLF2536bytes/SHA c6e421115263e6bfd0fb31630882087fb644efbfb3a56bfbd39643c4478c891e. V10 remains held. Parent's all-unfinished-experts SuperMimic queue is preserved; this first run is H1 only.

All files are LOCAL/PENDING ROOT NEXT-PHASE GIT ARCHIVE. The completed native-finalization folder was read only and not mutated. Current source/diffs and all failed/pending/correction reports must be archived together; no actual training or admission is claimed.
'''
with (HERE/'FINAL_ROOT_EXECUTION_HANDOFF.md').open('x',encoding='utf8') as stream:stream.write(handoff)
inventory=[]
for path in sorted(HERE.rglob('*')):
    if not path.is_file():continue
    text=path.suffix in ('.py','.json','.md','.txt','.diff')
    inventory.append(dict(path=str(path),relative=path.relative_to(HERE).as_posix(),bytes=path.stat().st_size,
                          SHA=H(path) if text else None,
                          archive='REQUIRED_TEXT_SOURCE_REPORT' if text else 'GENERATED_CACHE_INDEX_ONLY',
                          actual_model_or_raw_NPZ_USD=False))
with (HERE/'reports/FINAL_ARTIFACT_INDEX_PENDING_ROOT_GIT.json').open('x',encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(),files=inventory,self_index_not_self_hashed=True,
                   Git_status='LOCAL_PENDING_ROOT_NEXT_PHASE_ARCHIVE'),stream,indent=2)
print(json.dumps(dict(source_protocol_complete=True,latest_checks='9/9',ready=False,admitted=False,GO=False,
                      root_entry=str(HERE/'bind_mixed84_qualified83B_sources_TEMPLATE.py'),
                      handoff=str(HERE/'FINAL_ROOT_EXECUTION_HANDOFF.md'),files=len(inventory))))
