"""New pure metadata/AST fixtures. No binder, deployer, observer, model, or env run."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import time
import traceback

import mixed84_protocol_v1 as p

HERE = Path(__file__).resolve().parent
SNAP = HERE / 'source_snapshots'
RESULTS = []


def tree(name):
    return ast.parse((HERE / name).read_text('utf8'))


def function(module, name):
    return next(n for n in module.body if isinstance(n, ast.FunctionDef) and n.name == name)


def expect_reject(call):
    try:
        call()
    except (AssertionError, KeyError, TypeError) as error:
        return dict(expected_rejection=True, type=type(error).__name__, message=str(error))
    raise AssertionError('Synthetic invalid/pending input was accepted')


def fixture_bundle():
    # Entirely synthetic gate dictionaries, never written as actual admission.
    mask = [True] * 73
    for i in (0, 1, 7, 8):
        mask[i] = False
    phase = dict(schema='mod4.supermimic.partial_step270_phase_contract.v1',
                 demo_height_vz_after_ascent='excluded_from_conditioning_and_imagination_loss_source_returns_to_original_surface',
                 measured_ascent_cutoff_basis='recorded_minimum_two_wheel_bottom_path_apex',
                 own_task_step_edge_x_m=.35, own_task_platform_height_m=.27,
                 source_XY_forward_and_H1_step_ascent_coverage=False,
                 physical_V8_reward_commands_success_unchanged=True)
    contract = dict(schema='mod4.supermimic.partial_reference_objective_contract.v2',
                    native_goal_dim=73, native_obs_dim=128, native_history=10, native_actions=6, native_joints=30,
                    own_task_analytic_height_curve='excluded_from_this_imagination_surrogate',
                    own_task_forward='existing_native_base_goal_X_and_Y0_only_not_Fudan_coverage',
                    demo_XY_and_XY_velocity_and_unobserved_spins='excluded_by_explicit_mask',
                    native_world_model='only_actual_own_plant_executed_transitions',
                    physical_reward='existing_V8_RewardManager_unchanged',
                    physical_H1='2.5ms_TGS32_4_100Hz_decimation4_unchanged',
                    does_not_admit_environment_training_or_skill_graduation=True,
                    provider_execution_scope='offline_CPU_named_mapping_SDK_readback_false',
                    phase_mask=phase,
                    own_task_landing='post_ascent_nominal_own_chassis_height_plus_actual0.270m_platform_in_own_step_region_not_foreign_demonstration',
                    reference_metadata=dict(conditioning_feature_mask73=mask,
                        foreign_transitions_for_native_world_model=False, target_control_dt_s=.01,
                        partial_phase_contract=phase,
                        reference_reward_integration='PartialReferenceImitationMdp_v3_ascent_Z_Vz_mask_plus_separate_own_task_support_height',
                        sdk_joint_order_verified=False,
                        clock_alignment=dict(native_frame_anchor=100, reference_time_anchor_s=.5,
                                             uses_future_actions_or_gate_choices=False)))
    return dict(status='ACTUAL_REFERENCE_AND_ADAPTER_CPU_VALIDATED', fixture_only=True,
                reference=dict(passed=True, teacher_CPU_rollout_actual=True, repository_commit=p.FUDAN_REPO_SHA,
                    original_teacher_ONNX_used=True, required_assets_complete=True,
                    selected_original_source_timestep_s=.002,
                    source_is_partial_standing_jump_not_H1_step270_or_stable_recovery_proof=True,
                    not_our_policy_inference=True, not_forced_action_or_trajectory_clamp=True,
                    teacher_ONNX_SHA=p.FUDAN_TEACHER_ONNX_PINS['jump'], teacher_ONNX_pins=p.FUDAN_TEACHER_ONNX_PINS,
                    asset_provenance_SHA='b'*64,
                    reference_artifact_SHA=p.FUDAN_NATIVE_V3_SHA, reference_provenance_report_SHA='d'*64,
                    artifact_relative='reference/H1_PARTIAL_JUMP_NATIVE_REFERENCE_PACKED73.json', artifact_bytes=123),
                adapter_CPU=dict(passed=True, CPU_only=True, CUDA_initialized=False, actual_reference_loaded=True,
                    reference_reader_schema_verified=True, reference_artifact_SHA=p.FUDAN_NATIVE_V3_SHA,
                    source_robot='Fudan_wheel_legged', target_robot='MOD4_H1', state_joints=30, actions=6,
                    no_forced_actions=True, original_goal_machine_unchanged=True,
                    retargeting_protocol_SHA='e'*64, adapter_source_SHA='f'*64, report_SHA='1'*64,
                    objective_contract_SHA='2'*64), objective_contract=contract,
                candidate_pins=dict(bridge_source_SHA='3'*64, finalization_source_SHA='4'*64,
                                    native_CPU_source_SHA='5'*64),
                native_bootstrap_source_SHA=p.SOURCES['h1']['SHA'], native_bootstrap_Adam=829700,
                native_bootstrap_kind='qualified83B_H1_frozen_PPO_core_only',
                old82Q_native_prefix_or_unknown_final_used=False, candidate_V10_reward_used=False,
                finalization_CPU=dict(passed=True, CPU_only=True, passed_count=21, count=21,
                                     finalization_source_SHA='4'*64, report_SHA='6'*64))


def fixture_spec(bundle):
    return dict(key='e2', finite_method_test=True, h1_step270_method_test=True,
                source_SHA=p.SOURCES['h1']['SHA'], source_Adamstep=829700,
                execution_backend='target72', GPU_UUID=p.GPUS['e2'], manifest_SHA='7'*64,
                cross_host_qualified_source=False,
                reference_artifact_SHA=bundle['reference']['reference_artifact_SHA'],
                adapter_CPU_report_SHA=bundle['adapter_CPU']['report_SHA'],
                objective_contract_SHA=bundle['adapter_CPU']['objective_contract_SHA'],
                runtime_objective_contract_SHA=None, candidate_pins=bundle['candidate_pins'])


def fixture_installed(bundle, spec):
    sdk = dict(passed_CPU_only=True, source_SHA=spec['source_SHA'], all17Adam=829700,
               manifest_SHA=spec['manifest_SHA'], sampling_acceleration_CPU=dict(passed=True),
               actual_RSL_sources=[{}, {}], new_reward_integration_CPU=dict(actual_installed_sampled_excess_SDK_compute_tested=True))
    runtime_contract = copy.deepcopy(bundle['objective_contract'])
    unit = dict(passed=True, actual_installed_CPU_passed=True, CUDA_initialized=False,
                manifest_SHA=spec['manifest_SHA'], source_SHA=spec['source_SHA'],
                reference_artifact_SHA=bundle['reference']['reference_artifact_SHA'],
                adapter_CPU_report_SHA=bundle['adapter_CPU']['report_SHA'],
                objective_contract_SHA=bundle['adapter_CPU']['objective_contract_SHA'],
                offline_objective_contract=runtime_contract,
                offline_named_mapping_verified=True, actual_runtime_order_readback=False,
                candidate_pins=bundle['candidate_pins'], original_physics_and_success_unchanged=True,
                finalization_lifecycle_CPU_passed=True, partial_mask_objective_actual_CPU_admitted=True)
    unit['ascent_phase_mask_and_own_step_support_loss_CPU_passed']=True
    return sdk, unit


def actual_metadata_and_pending():
    proof = json.loads((SNAP/'83B_complete_metadata.json').read_text('utf8'))
    identity = json.loads((SNAP/'83B_detached_metadata.json').read_text('utf8'))['owner_identity']
    p.validate_closed83B(proof, identity)
    pending = json.loads((HERE/'MIXED84_INTEGRATION_PENDING.json').read_text('utf8'))
    assert pending['ready'] is False and pending['admitted'] is False and pending['GO'] is False
    result = expect_reject(lambda: p.validate_reference_preparation(pending['reference_bundle']))
    # Execute only binder's initial assertion AST, never its function or body.
    initial = function(tree('bind_mixed84_qualified83B_sources_TEMPLATE.py'), 'bind_new_payloads').body[0]
    result2 = expect_reject(lambda: exec(compile(ast.Module(body=[initial],type_ignores=[]),'binder_first_assert_only','exec'),dict(integration=pending)))
    return dict(actual_closed83B_metadata_valid=True, pending_reference=result, pending_binder_first_assert=result2)


def protected_controller_AST():
    old = ast.parse((SNAP/'83B_three_slot_common_v1.py').read_text('utf8'))
    new = tree('owner_controller_templates/three_slot_common_v1.py')
    protected = ('charge_values', 'authenticated_row', 'validate_payload', 'environment', 'native_CPU', 'state')
    for name in protected:
        assert ast.dump(function(old,name)) == ast.dump(function(new,name)), name
    original_ready = function(old,'valid_ready')
    candidate_ready = copy.deepcopy(function(new,'valid_ready'))
    candidate_ready.body = candidate_ready.body[1:]
    assert ast.dump(original_ready) == ast.dump(candidate_ready)
    for name in ('three_slot_finite_owner_v1.py','three_slot_finite_node_v1.py','forwarded_original_owner_control_v1.py'):
        assert (SNAP/('83B_'+name)).read_bytes() == (HERE/'owner_controller_templates'/name).read_bytes()
    assert (HERE/'owner_controller_templates/mixed84_protocol_v1.py').read_bytes() == (HERE/'mixed84_protocol_v1.py').read_bytes()
    return dict(protected=list(protected), owner_node_network_bytes_exact=True,
                native_ready_branch_only_plus_GPU_threshold_change=True)


def original_copy_loop_exact():
    old_tree = ast.parse((SNAP/'82Q_e2_installer.py').read_text('utf8'))
    old_code = ast.literal_eval(next(n.value for n in old_tree.body if isinstance(n,ast.Assign)))
    new_tree = tree('e2_healthy83B_physical_resource_install84_TEMPLATE.py')
    new_code = ast.literal_eval(next(n.value for n in new_tree.body if isinstance(n,ast.Assign)))
    loop = lambda text: next(n for n in ast.parse(text).body if isinstance(n,ast.For) and ast.unparse(n.iter)=="v['manifest']['files']")
    assert ast.dump(loop(old_code)) == ast.dump(loop(new_code))
    assert "set(proof['models'])=={'h1','e2','recovery'}" in new_code
    assert "r['returncode']==0 and not r['original_error']" in new_code
    assert 'failed_method' not in new_code and '2610v81o' not in new_code
    return dict(original_per_file_copy_and_path_containment_AST_exact=True,
                new_physical_slot_proof_healthy83B_normal_E2=True)


def normal_guard_and_metadata_exact():
    for key,role in (('h1','closed_production_continuation_CPU_v2.py'),('recovery','original_account_policy50_source_CPU.py')):
        old=ast.parse((SNAP/('83B_'+key+'_'+role)).read_text('utf8'))
        new=tree('normal_'+key+'_source_guard_TEMPLATE.py')
        for node in old.body:
            if isinstance(node,ast.FunctionDef) and node.name!='load':
                assert ast.dump(node)==ast.dump(function(new,node.name))
        assert 'production_h1_recovery_pair_and_separate_native_method_diagnostic' not in ast.unparse(function(new,'load'))
        assert "set(proof['models']) == {'h1', 'e2', 'recovery'}" in ast.unparse(function(new,'load'))
    metadata=SNAP/'metadata_exact_CRLF.py'
    assert metadata.stat().st_size==p.METADATA_BYTES and hashlib.sha256(metadata.read_bytes()).hexdigest()==p.METADATA_SHA
    raw=metadata.read_bytes();assert b'\r\n' in raw
    return dict(normal_guard_helpers_exact=True, metadata_CRLF2536_SHA_exact=True,
                baseline_overlay_only_guard_role_and_E3_savedAdam_assert=True)


def ready_positive_and_negative():
    bundle=fixture_bundle();spec=fixture_spec(bundle);sdk,unit=fixture_installed(bundle,spec)
    p.validate_reference_preparation(bundle)
    value=p.native_ready_value(spec,bundle,sdk,unit,spec['manifest_SHA'])
    row=dict(key='e2',phase='ready',original_error=False,manifest_SHA=spec['manifest_SHA'],
             closed_source_CPU=dict(value=value,SHA=p.digest(value),actual_CPU_waited_EXIT0=True))
    assert p.native_valid_ready(row,spec)
    rejected=[]
    for label,mutator in (
        ('paused_normal_E2_not_native_source',lambda x:x.update(source_SHA=p.SOURCES['e2']['SHA'])),
        ('unknown_native_final_not_bootstrap',lambda x:x.update(source_SHA='0'*64))):
        bad=copy.deepcopy(spec);mutator(bad);assert p.native_valid_ready(row,bad) is False;rejected.append(label)
    badunit=copy.deepcopy(unit);badunit['offline_named_mapping_verified']=False
    rejected.append(expect_reject(lambda:p.validate_installed_native(sdk,badunit,spec,spec['manifest_SHA'],bundle)))
    badunit=copy.deepcopy(unit);badunit['actual_runtime_order_readback']=True
    rejected.append(expect_reject(lambda:p.validate_installed_native(sdk,badunit,spec,spec['manifest_SHA'],bundle)))
    badunit=copy.deepcopy(unit);badunit['partial_mask_objective_actual_CPU_admitted']=False
    rejected.append(expect_reject(lambda:p.validate_installed_native(sdk,badunit,spec,spec['manifest_SHA'],bundle)))
    return dict(synthetic_ready_fixture_passed=True,fixture_is_not_actual_admission=True,rejected=rejected)


def partial_mask_and_clock_negative():
    bundle=fixture_bundle();bad=copy.deepcopy(bundle);bad['objective_contract']['reference_metadata']['conditioning_feature_mask73'][0]=True
    first=expect_reject(lambda:p.validate_reference_preparation(bad))
    bad=copy.deepcopy(bundle);bad['objective_contract']['reference_metadata']['clock_alignment']['reference_time_anchor_s']=0.
    second=expect_reject(lambda:p.validate_reference_preparation(bad))
    bad=copy.deepcopy(bundle);bad['reference']['selected_original_source_timestep_s']=.005
    third=expect_reject(lambda:p.validate_reference_preparation(bad))
    return dict(XY_mask=first,phase_alignment=second,unselected_005_source=third)


def actual_V3_objective_contract_metadata():
    contract_path=SNAP/'ACTUAL_V3_OFFLINE_OBJECTIVE_CONTRACT.json'
    report_path=SNAP/'ACTUAL_V3_REFERENCE_H1_MDP_CPU_PROOF_RESULT.json'
    contract=json.loads(contract_path.read_text('utf8'));report=json.loads(report_path.read_text('utf8'))
    assert report['status']=='PASS_ACTUAL_REFERENCE_REAL_H1_MDP_OFFLINE_CPU_OBJECTIVE_PROOF'
    assert report['native_reference']['SHA256']==p.FUDAN_NATIVE_V3_SHA and report['native_reference']['bytes']==470968
    assert report['actual_runtime_SDK_readback'] is False and report['offline_named_order_proved']
    assert report['actual_native_actor_forward_optimizer_GPU_plant_or_WM_training_executed'] is False
    assert report['source_flat_return_Z_Vz_and_horizontal_mutations_do_not_change_postascent_loss']
    p.validate_objective_contract(contract)
    assert hashlib.sha256(contract_path.read_bytes()).hexdigest()==report['offline_objective_contract']['SHA256']
    old=copy.deepcopy(contract);old['schema']='mod4.supermimic.partial_reference_objective_contract.v1'
    rejection=expect_reject(lambda:p.validate_objective_contract(old))
    return dict(actual_V3_report_and_contract_verified_metadata_only=True,
                actual_runtime_SDK_readback=False,pending=report['pending'],old_V2_loss_contract_rejected=rejection)


def resource_and_result_scope():
    r=dict(actual_fresh_snapshot=True,all_expected_GPU_empty=True,free_MiB=dict(h1=16000,e2=16000,recovery=8000),
           RAM_available_bytes=9*1024**3,postcopy_disk_free_bytes=26*1024**3,
           runtime_fullsave_disk_floor_bytes=8*1024**3,canonical_active_segment=None,
           original_locks_actual_free=True,remaining_actual_snapshot=p.CLOSED_REMAINING_SNAPSHOT)
    p.validate_fresh_resources(r);r['free_MiB']['e2']=8000
    rejection=expect_reject(lambda:p.validate_fresh_resources(r))
    result=p.split_collected_results({'h1':{},'recovery':{}},{'not_production_H1_or_E2_source':True},
                                     {key:{'duration_bound_passed':True} for key in ('h1','e2','recovery')})
    assert set(result['models'])=={'h1','recovery'} and result['normal_E2_83B_source_preserved_paused']['Adam']==857460
    return dict(native15669_not_E3_7000_floor=rejection,separate_native_method_and_three_original_costs=True)


def compile_and_no_live_execution():
    count=0
    for path in HERE.rglob('*.py'):
        if 'source_snapshots' in path.parts:continue
        module=ast.parse(path.read_text('utf8'));compile(module,str(path),'exec');count+=1
        for node in module.body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CODE','READ210','READ72') for t in node.targets):
                value=ast.literal_eval(node.value)
                if isinstance(value,str):compile(value,str(path)+'_embedded','exec')
    assert not (HERE.parent.parent/p.LOCAL_STAGE).exists(), 'Preparation unexpectedly created real stage'
    return dict(source_files_compiled_only=count,no_generated_template_import_or_execution=True,
                no_payload_model_copy_TASK_GO_network_GPU_or_budget=True)


def main():
    for test in (actual_metadata_and_pending,protected_controller_AST,original_copy_loop_exact,
                 normal_guard_and_metadata_exact,ready_positive_and_negative,
                 partial_mask_and_clock_negative,actual_V3_objective_contract_metadata,
                 resource_and_result_scope,compile_and_no_live_execution):
        try:RESULTS.append(dict(name=test.__name__,passed=True,details=test()))
        except BaseException as error:RESULTS.append(dict(name=test.__name__,passed=False,error=str(error),traceback=traceback.format_exc()))
    result=dict(epoch=time.time(),attempt_id='mixed84-protocol-source-CPU-'+str(time.time_ns()),
                passed=all(row['passed'] for row in RESULTS),count=len(RESULTS),
                passed_count=sum(row['passed'] for row in RESULTS),tests=RESULTS,
                ready=False,admitted=False,GO=False,source_templates_only=True,
                actual83B_metadata_read_only=True,synthetic_gate_dicts_are_not_actual_admission=True,
                prior21_finalization_tests_not_rerun=True,Git_status='PENDING_ROOT_PHASE_ARCHIVE')
    output=HERE/'reports'/('SOURCE_PROTOCOL_CPU_'+str(time.time_ns())+'_ACTUAL.json')
    with output.open('x',encoding='utf8') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(dict(passed=result['passed'],passed_count=result['passed_count'],count=result['count'],report=str(output))))
    return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
