"""Root source-only integration of independently tested native publication and actual partial demo."""
from pathlib import Path
import ast,hashlib,importlib.util,json,time,traceback
J=Path(__file__).resolve().parent;R=J/'reports';A=J/'agent_native_finalization_cpu';P=J/'agent_next_mixed84_protocol';C=J/'root_integrated_native_Fudan_V3';H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(path,v):
 with Path(path).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
try:
 assert not C.exists();C.mkdir();base=(A/'h1_supermimic_bridge_v1.py').read_text('utf8');assert H(A/'h1_supermimic_bridge_v1.py')=='2a69bba5f59f005562ab42a7eac8e53ee6ecec158dbfdc6932983f4c03adb5fa';s=base
 needle='    cfg = SuperMimicConfig(iterations=1000000,';assert s.count(needle)==1
 block='''    # New reference is a measured foreign jump retargeted to our static geometry;
    # its phase masks/task support objective are distinct from physical rewards.
    from supermimic_reference_adapter_v1 import read_json_reference, PartialReferenceImitationMdp
    reference_bundle = json.loads((B / 'MIXED84_REFERENCE_BINDING_ACTUAL.json').read_bytes())
    reference_path = B / reference_bundle['reference']['artifact_relative']
    assert hashlib.sha256(reference_path.read_bytes()).hexdigest() == reference_bundle['reference']['reference_artifact_SHA']
    reference = read_json_reference(reference_path)
    actual_joint_names = list(env.scene['robot'].joint_names)
    reference = reference.for_sdk_joint_order(actual_joint_names)
    assert reference.metadata['sdk_joint_order_verified'] is True
    bridge.mdp = PartialReferenceImitationMdp(bridge.mdp, reference.torch_provider(env.device))
    runtime_objective = bridge.mdp.contract_manifest()
    assert runtime_objective['provider_execution_scope'] == 'runtime_actual_SDK_named_mapping_required'
    assert runtime_objective['reference_metadata']['sdk_joint_order_verified'] is True
    assert runtime_objective['config'] == reference_bundle['objective_contract']['config']
    runtime_bytes = (json.dumps(runtime_objective, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\\n').encode('utf8')
    runtime_contract_SHA = hashlib.sha256(runtime_bytes).hexdigest()
    runtime_path = out / 'NATIVE_FUDAN_REFERENCE_OBJECTIVE_CONTRACT_ACTUAL.json'
    assert not runtime_path.exists()
    runtime_partial = runtime_path.with_suffix('.json.partial')
    with runtime_partial.open('xb') as stream:
        stream.write(runtime_bytes)
    runtime_partial.replace(runtime_path)
    assert bridge.pi_updates == 0 and bridge.wm_updates == 0 and bridge.trace is None
    put(out / 'NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json', dict(
        actual_runtime_order_readback=True, complete_named_permutation=True,
        before_first_physical_step_and_Pi=True,
        scope='before first native learning control/Pi; original environment construction/reset is separate',
        actual_robot_joint_names=actual_joint_names,
        reference_artifact_SHA=reference_bundle['reference']['reference_artifact_SHA'],
        runtime_objective_contract_SHA=runtime_contract_SHA,
        source_SHA=task['source_SHA'], original_run_id=go['run_id'],
        actual_own_task_physics_commands_and_success_unchanged=True))
'''
 s=s.replace(needle,block+needle,1)
 needle='        native_not_production_H1_or_E2_source=True))';assert s.count(needle)==1
 producer='''        reference_artifact_SHA=reference_bundle['reference']['reference_artifact_SHA'],
        adapter_CPU_report_SHA=reference_bundle['adapter_CPU']['report_SHA'],
        objective_contract_SHA=reference_bundle['adapter_CPU']['objective_contract_SHA'],
        runtime_objective_contract_SHA=runtime_contract_SHA,
'''
 s=s.replace(needle,producer+needle,1)
 old='root_reference_is_not_successful_mocap_or_forced_action=True';new='reference_is_partial_retarget_not_our_successful_step_or_forced_action=True';assert s.count(old)==1;s=s.replace(old,new,1)
 restored=s.replace(block,'',1).replace(producer,'',1).replace(new,old,1);assert restored==base
 before=ast.parse(base);after=ast.parse(s);assert {x.name:ast.dump(x) for x in before.body if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name!='run'}=={x.name:ast.dump(x) for x in after.body if isinstance(x,(ast.ClassDef,ast.FunctionDef)) and x.name!='run'}
 run=next(x for x in after.body if isinstance(x,ast.FunctionDef) and x.name=='run');ordered=ast.unparse(run)
 assert ordered.index('reference.for_sdk_joint_order(actual_joint_names)')<ordered.index('SuperMimicLearner(')<ordered.index('trace.install()')<ordered.index('return run_native_lifecycle(')
 assert "list(env.scene['robot'].joint_names)" in ordered and 'for_offline_joint_order' not in ordered
 out=C/'h1_supermimic_bridge_v1.py';out.write_text(s,'utf8');integration=json.loads((P/'MIXED84_REVIEWED_INPUT_MAPPING_PENDING_V3.json').read_bytes())
 integration['status']='ROOT_REVIEWED_ACTUAL_INPUTS_READY_FOR_NEW_BINDING';integration['source_only_authorization'].update(approved=True,human_scope='Fudan repository jump through SuperMimic; allunfinished experts queue; existingbounded oneDual4090 H1 test',no_new_training_or_GO_authorization=True)
 bundle=integration['reference_bundle'];bundle['status']='ACTUAL_REFERENCE_AND_ADAPTER_CPU_VALIDATED';bundle['candidate_pins']['bridge_source_SHA']=H(out);integration['native_candidate_files']['source/h1_supermimic_bridge_v1.py'].update(local_path=str(out),SHA=H(out))
 sp=importlib.util.spec_from_file_location('source_protocol_prebind_review',P/'mixed84_protocol_v1.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);m.validate_reference_preparation(bundle)
 for rel,row in integration['native_candidate_files'].items():assert row['local_path'] and H(row['local_path'])==row['SHA'],rel
 for field,digest in [('reference_artifact_path',bundle['reference']['reference_artifact_SHA']),('adapter_CPU_report_path',bundle['adapter_CPU']['report_SHA']),('objective_contract_path',bundle['adapter_CPU']['objective_contract_SHA']),('finalization_CPU_proof_path',bundle['finalization_CPU']['report_SHA'])]:assert H(integration[field])==digest,field
 put(C/'ROOT_REVIEWED_MIXED84_INPUTS_V3_ACTUAL.json',integration)
 put(R/'ROOT_FUDAN_V3_BRIDGE_SOURCE_INTEGRATION_AST_REVIEW_ACTUAL.json',dict(epoch=time.time(),passed_source_only=True,base_finalization_bridge_SHA=H(A/'h1_supermimic_bridge_v1.py'),integrated_bridge_SHA=H(out),all_class_and_other_function_AST_exact=True,original_run_text_restored_exact_after_only_reference_binding_receipts_producer_and_startup_label_changes=True,actual_joint_names_read_before_first_native_step_Pi=True,not_offline_relabelled_as_runtime=True,unchangedWM_Pi_Critic_creation_and_updates_physical_sampling_trace_retention_save_lifecycle=True,reference_V3_and_objective_CPU_pins_match=True,all_candidate_text_and_reference_SHA_pins_match=True,no_model_policy_GPU_plant_or_budget_action=True,no_payload_Task_GO_yet=True,reviewed_input=str(C/'ROOT_REVIEWED_MIXED84_INPUTS_V3_ACTUAL.json')))
 print(json.dumps(dict(source_integrated=True,bridge_SHA=H(out),reviewed_input=str(C/'ROOT_REVIEWED_MIXED84_INPUTS_V3_ACTUAL.json'),no_payload_Task_GO_yet=True)))
except BaseException:
 put(R/('ROOT_NATIVE_BRIDGE_SOURCE_INTEGRATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),not_training_failure=True,no_same_once_replay=True));raise
