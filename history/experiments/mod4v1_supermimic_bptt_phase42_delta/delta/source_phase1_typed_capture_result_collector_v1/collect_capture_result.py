"""One future metadata collection purpose. No collection occurs on import.

CLI --dispatch LOCAL_JSON [--output-root NEW_ABSOLUTE_DIRECTORY]. Original
connect72 is loaded only by main's explicit future call. No parent is created.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import shlex
import sys
import time
import typed_collector_contract as TC
from remote_metadata_reader import (validate_dispatch, OUTER, PURPOSE, PARENT_SHA,
    CONTROLLER_SHA, INDEX_SHA, BASE, LOGS, SOURCE_VERSION, SOURCE_DERIVATION)

HERE = Path(__file__).resolve().parent
R = HERE.parent
CONNECTOR = R.parent/'mod4v1_experts_fulldr_rm70_20261101/project_connector.py'
CONNECTOR_SHA = '623599cf014fe39b46f1a10bc4e858c498860578f4b277ac81a802ede2da09d6'
REMOTE_LIMIT = 16*1024*1024


def integer(value):
    return value if type(value) is int else None


def same_identity(left, right):
    return type(left) is dict and type(right) is dict and all(left.get(k) == right.get(k)
        and left.get(k) is not None for k in ('pid','linux_start_ticks'))


def summarize(dispatch, packet):
    """Separate producer execution closure, outer actual wait, and unknown Gate1."""
    docs = packet.get('documents',{}); infos = packet.get('file_metadata',{})
    errors = list(packet.get('collector_errors',[])); checks = {}; missing = []
    def obj(name):
        item = docs.get(name)
        if type(item) is not dict:
            missing.append(name); return {}
        return item
    def check(name, ok):
        checks[name] = bool(ok)
        if not ok: errors.append(dict(check=name,error='missing or contradictory published metadata'))
    plan = obj('GROUP_PLAN.json'); stage = obj('STAGE_COMPLETE_PHASE1_CAPTURE_V1.json')
    remote_dispatch = obj('PHASE1_CAPTURE_PARENT_DISPATCH_RECEIPT_V1.json')
    outer = obj(OUTER); scope = obj('PARENT_EXIT_SCOPE.json')
    grade = obj('PHASE1_CAPTURE_GROUP_CLOSED_SOURCE_GRADE_V1.json')
    group = obj('FINAL.json'); worker = obj('cases/E3/FINAL.json')
    task = obj('cases/E3/task.json'); admission = obj('ACTUAL_GROUP_ADMISSION.json')
    request = obj('PHASE1_CAPTURE_PARENT_DISPATCH_REQUEST_V1.json')
    controller_started = obj('PHASE1_CAPTURE_PARENT_CONTROLLER_STARTED_V1.json')
    parent_started = obj('PARENT_STARTED.json'); children = docs.get('CHILDREN.json')
    check('same_original_parent_and_controller_start',controller_started.get('kind') == 'OWN_PHASE1_CAPTURE_PARENT_ACTUAL_WAIT_CONTROLLER_V1'
        and same_identity(controller_started.get('controller'),dispatch['controller'])
        and controller_started.get('parent_source_SHA') == PARENT_SHA
        and integer(controller_started.get('controller_resource_SDK_model_C_lock_or_signal_operations')) == 0
        and parent_started.get('kind') == 'ONEGPU_PHASE1_PASSIVE_CAPTURE_E3_ONLY_PARENT_V1'
        and parent_started.get('pid') == dispatch['parent']['pid'] and parent_started.get('requested_roles') == ['E3'])
    check('same_new_purpose_plan', plan.get('kind') == TC.PLAN_KIND
        and plan.get('batch_purpose') == PURPOSE and plan.get('group_id') == dispatch['group_id']
        and plan.get('requested_roles') == ['E3'])
    try:
        TC.validate_materialization(stage, plan, infos, dispatch)
        check('actual_typed_materialization_and_raw_plan_binding', True)
    except Exception as exc:
        check('actual_typed_materialization_and_raw_plan_binding', False)
        errors.append(dict(check='actual_typed_materialization_and_raw_plan_binding', error=type(exc).__name__+': '+str(exc)))
    check('materialization_is_not_admission', stage.get('materialized') is True
        and integer(stage.get('parent_launches')) == 0 and stage.get('purpose') == PURPOSE
        and infos.get('STAGE_COMPLETE_PHASE1_CAPTURE_V1.json',{}).get('SHA256') == dispatch['stage_receipt_SHA256']
        and stage.get('GROUP_PLAN_SHA256') == infos.get('GROUP_PLAN.json',{}).get('SHA256'))
    check('dispatch_request_same_purpose', request.get('root') == dispatch['root']
        and request.get('group_id') == dispatch['group_id'] and request.get('purpose') == PURPOSE
        and request.get('stage_receipt_SHA256') == dispatch['stage_receipt_SHA256']
        and request.get('SDK_scene_or_skill_admission') is False
        and request.get('controller_source_SHA') == CONTROLLER_SHA)
    for label, row in (('controller_dispatch',remote_dispatch),('outer_wait',outer)):
        check(label+'_identity', same_identity(row.get('controller'),dispatch['controller'])
            and same_identity(row.get('parent'),dispatch['parent'])
            and row.get('group_id') == dispatch['group_id'] and row.get('parent_source_SHA') == PARENT_SHA
            and integer(row.get('actual_native_parent_Popen_calls')) == 1)
    check('controller_dispatch_not_admission',remote_dispatch.get('kind') == 'ONE_ORIGINAL_PHASE1_CAPTURE_PARENT_POPEN_NOT_RESOURCE_ADMISSION'
        and remote_dispatch.get('root') == dispatch['root'] and remote_dispatch.get('SDK_scene_or_skill_admission') is False)
    check('independent_outer_actual_parent_wait',outer.get('kind') == 'ACTUAL_EXTERNAL_PARENT_POPEN_WAIT_PHASE1_CAPTURE_V1'
        and outer.get('actual_parent_p_wait_returned') is True and integer(outer.get('returncode')) == 0
        and outer.get('controller_errors') == [] and outer.get('original_parent_resource_close_wait_not_replaced') is True
        and integer(outer.get('controller_resource_SDK_model_C_lock_or_signal_operations')) == 0)
    waits = scope.get('child_waits'); terminal = group.get('terminal'); rows = docs.get('TERMINAL_ROWS.json')
    good_wait = type(waits) is list and len(waits) == 1 and type(waits[0]) is dict
    good_terminal = type(terminal) is list and len(terminal) == 1 and type(terminal[0]) is dict
    check('parent_own_child_wait_and_both_EX_release', scope.get('all_own_children_waited') is True
        and scope.get('original_single_GPU_private_EX_released') is True
        and scope.get('original_global_finite_EX_released') is True
        and integer(scope.get('canonical_writes')) == 0 and scope.get('errors') == []
        and scope.get('no_foreign_scope_touched') is True and good_wait
        and waits[0].get('role') == 'E3' and waits[0].get('actual_waited') is True
        and integer(waits[0].get('returncode')) == 0)
    check('producer_closed_source_grade',grade.get('kind') == TC.GRADE_KIND
        and grade.get('purpose') == PURPOSE and grade.get('passed_closed_capture_execution') is True
        and grade.get('errors') == [])
    check('group_execution_final', group.get('kind') == TC.GROUP_FINAL_KIND
        and group.get('purpose') == PURPOSE and group.get('group_id') == dispatch['group_id']
        and group.get('passed_execution') is True and group.get('requested_roles') == ['E3'])
    check('actual_child_terminal_receipts',good_wait and good_terminal and rows == terminal
        and terminal[0].get('role') == 'E3' and terminal[0].get('actual_waited') is True
        and integer(terminal[0].get('returncode')) == 0 and terminal[0].get('pid') == waits[0].get('pid')
        and terminal[0].get('passed_execution') is True and terminal[0].get('error') is None
        and terminal[0].get('semantic',{}).get('passed_execution') is True
        and terminal[0].get('data') == worker and type(children) is list and len(children) == 1
        and children[0].get('role') == 'E3' and children[0].get('pid') == waits[0].get('pid')
        and children[0].get('root') == dispatch['root']+'/cases/E3'
        and children[0].get('worker') == 'worker_passive_interface_v1.py')
    go = obj('GROUP_EVAL_START.json'); ready = obj('cases/E3/WORKER_SCENE_READY.json')
    started = obj('cases/E3/WORKER_EVAL_STARTED.json')
    check('actual_E3_common_GO_not_materialization',go.get('kind') == TC.COMMON_START_KIND
        and go.get('purpose') == PURPOSE and go.get('group_id') == dispatch['group_id']
        and go.get('members') == ['E3'] and type(go.get('epoch')) in (int,float)
        and group.get('GO_epoch') == go.get('epoch') and started.get('GO_epoch') == go.get('epoch')
        and ready.get('role') == 'E3' and started.get('role') == 'E3'
        and ready.get('kind') == 'PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_V1'
        and started.get('kind') == 'PHASE1_TYPED_NATIVE_CAPTURE_SOURCE_V1')
    check('original_admission_receipt_observed_not_recreated',admission.get('group_id') == dispatch['group_id']
        and admission.get('original_private_GPU_EX_held') is True
        and admission.get('original_global_finite_EX_held') is True and integer(admission.get('canonical_writes')) == 0)
    validation = packet.get('metadata_validation') or {}; closure = packet.get('closure') or {}
    check('full_real_metadata_source_closure',type(closure.get('source_aliases')) is int and closure['source_aliases'] == 34
        and type(closure.get('overlay_source_aliases')) is int and closure['overlay_source_aliases'] == 32
        and type(closure.get('independent_bootstrap_source_aliases')) is int and closure['independent_bootstrap_source_aliases'] == 2
        and closure.get('full_AppV6_Base_imported') is True
        and closure.get('native_modules_loaded') == [])
    for name in ('original_capture_plan','original_capture_preclose','original_app_close_metadata','typed_materialization_raw_plan_binding'):
        check(name, validation.get(name) is True)
    errors.extend(validation.get('errors',[]))
    for name in ('FINAL.json','TERMINAL_ROWS.json','cases/E3/FINAL.json'):
        info = infos.get(name,{})
        check('whole_original_once_before_projection:'+name,
            TC.complete_info(info, maximum=TC.BIG_LIMIT)
            and info.get('SHA256_is_whole_original_bytes') is True
            and info.get('exported_projection_is_not_original_bytes') is True)
    controls = integer(worker.get('controls'))
    check('worker_same_task_and_complete_bound',task.get('group_id') == dispatch['group_id']
        and task.get('kind') == TC.TASK_KIND and task.get('purpose') == PURPOSE
        and worker.get('kind') == TC.FINAL_KIND and worker.get('purpose') == PURPOSE
        and worker.get('group_id') == dispatch['group_id'] and worker.get('role') == 'E3'
        and worker.get('passed_execution') is True and controls == task.get('controls') and controls in (64,128)
        and worker.get('typed_producer_schema') == TC.SCHEMA and task.get('typed_producer_schema') == TC.SCHEMA
        and integer(worker.get('physics_callbacks')) == controls*8
        and integer(worker.get('feedback_samples')) == controls*2
        and worker.get('delay_calls') == dict(legs=controls*8,wheels=controls*8))
    check('synthetic_PT0_probe_not_quality_or_training',task.get('train') is False
        and task.get('quality_evaluation') is False and worker.get('full_clean35') == 'UNKNOWN'
        and worker.get('policy_variant') == 'EXPLICIT_SYNTHETIC_ZERO6_NOT_POLICY_QUALITY'
        and all(integer(worker.get(k)) == 0 for k in ('model_PT_reads','training_updates','optimizer_updates'))
        and all(worker.get(k) is False for k in ('learner_created','replay_created','teacher_created')))
    for name, row in (('worker',worker),('group',group),('source_grade',grade)):
        check(name+'_does_not_admit_interface_or_stage2', row.get('capture_interface_passed') is False
            and row.get('exact') is False and row.get('stage2_GO') is False and row.get('gate1') == 'UNKNOWN')
    error_files = [name for name in docs if name.endswith(('WORKER_ERROR.json','PARENT_ORIGINAL_ERROR.json',
        'GROUP_ABORT.json','GROUP_STARTUP_ABORT.json','PHASE1_CAPTURE_PARENT_CONTROLLER_ERROR_V1.json',
        'STAGE_ERROR_PHASE1_CAPTURE_V1.json','TYPED_CAPTURE_INCOMPLETE_V1.json'))]
    error_suffixes = ('WORKER_ERROR.json','PARENT_ORIGINAL_ERROR.json','GROUP_ABORT.json',
        'GROUP_STARTUP_ABORT.json','PHASE1_CAPTURE_PARENT_CONTROLLER_ERROR_V1.json',
        'STAGE_ERROR_PHASE1_CAPTURE_V1.json','TYPED_CAPTURE_INCOMPLETE_V1.json')
    error_files = sorted(set(error_files) | {name for name, info in infos.items()
        if name.endswith(error_suffixes) and info.get('published_regular_file_observed') is True})
    check('no_published_original_errors',not error_files)
    closed = not errors and all(checks.values())
    observed_failure = bool(error_files) or integer(outer.get('returncode')) not in (None,0) or grade.get('passed_closed_capture_execution') is False
    status = 'PASS_CLOSED_CAPTURE_EXECUTION_METADATA_ONLY' if closed else 'FAIL_CLOSED_CAPTURE_EXECUTION' if observed_failure else 'INCONCLUSIVE_METADATA_GAP_OR_COLLECTOR_CAP'
    return dict(kind='PHASE1_TYPED_CAPTURE_RESULT_COLLECTION_CLOSED_V1',purpose='NEW_OWN_RESULT_METADATA_COLLECTION_ONLY',
        source_version=SOURCE_VERSION,source_derivation=SOURCE_DERIVATION,
        status=status,root=dispatch['root'],group_id=dispatch['group_id'],created_epoch=time.time(),
        passed_closed_capture_execution=closed,checks=checks,errors=errors,missing_metadata=sorted(set(missing)),
        producer_source_grade=grade or None,outer_actual_parent_wait=outer or None,parent_exit_scope=scope or None,
        worker_observed=dict(controls=integer(worker.get('controls')),physics_callbacks=integer(worker.get('physics_callbacks')),
            feedback_samples=integer(worker.get('feedback_samples')),delay_calls=worker.get('delay_calls'),
            model_PT_reads=integer(worker.get('model_PT_reads')),training_updates=integer(worker.get('training_updates')),
            optimizer_updates=integer(worker.get('optimizer_updates')),coverage=worker.get('coverage'),
            producer_gate1=worker.get('gate1'),producer_capture_interface_passed=worker.get('capture_interface_passed')),
        actual_native_parent_Popen_calls=integer(remote_dispatch.get('actual_native_parent_Popen_calls')),
        actual_parent_wait_returned=outer.get('actual_parent_p_wait_returned'),
        producer_GATE1=None if not worker else worker.get('gate1'),gate1='UNKNOWN',capture_interface_passed=False,
        exact=False,paper_ready=False,stage2_GO=False,skill_success_rate=None,overall_eight_pass_rate=None,
        collection=packet.get('watch'),file_metadata=infos,remote_whole_FINAL_JSON_read=infos.get('cases/E3/FINAL.json',{}).get('whole_JSON_read'),
        new_capture_trace_fields_parsed=infos.get('cases/E3/FINAL.json',{}).get('new_capture_trace_fields_parsed'),
        trace_payload_exported=False,remote_FINAL_read_count=infos.get('cases/E3/FINAL.json',{}).get('read_count'),
        typed_projection=dict(removed_path_allowlist=list(TC.REMOVAL_PATHS), projected_metadata_is_not_original_bytes=True,
            unknown_fields_retained=True, unknown_future_payload_fields_are_not_silently_cropped=True),
        science_consumer_enabled=False, science_consistency_status=worker.get('science_consistency_status','UNKNOWN'),
        SDK_cost_settlement_verified=False,source_grade_is_not_quality_training_or_interface_success=True,
        no_parent_restarted=True,no_native_deadline_changed=True,no_remote_writes=True,
        published_metadata=docs,log_tails=packet.get('log_tails',{}))


def connect_original():
    raw = CONNECTOR.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CONNECTOR_SHA:
        raise ValueError('existing project connector pin differs')
    spec = importlib.util.spec_from_file_location('_phase1_result_original_connector',CONNECTOR)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module.connect72()


def remote_packet(client, dispatch, *, cap_seconds=6000, interval_seconds=20):
    contract_source = (HERE/'typed_collector_contract.py').read_text(encoding='utf-8')
    source = (HERE/'remote_metadata_reader.py').read_text(encoding='utf-8')
    source = 'import types,sys\n_m=types.ModuleType(\"typed_collector_contract\");sys.modules[_m.__name__]=_m\nexec('+repr(contract_source)+',_m.__dict__)\n'+source
    code = source+'\nremote_main('+repr(dispatch)+',cap_seconds='+repr(cap_seconds)+',interval_seconds='+repr(interval_seconds)+')\n'
    command = shlex.quote(BASE+'/run-python.sh')+' -u -B -c '+shlex.quote(code)
    incoming, outgoing, err = client.exec_command(command,timeout=cap_seconds+120)
    incoming.close()
    raw = outgoing.read(REMOTE_LIMIT+1); error = err.read(65537); rc = outgoing.channel.recv_exit_status()
    if len(raw) > REMOTE_LIMIT or len(error) > 65536:
        raise ValueError('metadata packet/stdout exceeds bounded export')
    if rc != 0:
        raise ValueError('metadata reader exit '+str(rc)+': '+error.decode('utf-8','replace')[-4000:])
    value = json.loads(raw)
    if type(value) is not dict or value.get('kind') != 'PHASE1_TYPED_CAPTURE_OWN_METADATA_PACKET_V1':
        raise ValueError('metadata packet kind differs')
    value['transport'] = dict(returncode=rc,stderr_tail=error.decode('utf-8','replace'))
    return value


def atomic_closed(output_root, value):
    output_root = Path(output_root)
    if not output_root.is_absolute() or output_root.exists():
        raise ValueError('local output root must be NEW absent absolute directory')
    output_root.mkdir(parents=True,exist_ok=False)
    target = output_root/'CLOSED_RESULT.json'; partial = output_root/'CLOSED_RESULT.json.partial'
    with partial.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False); stream.flush(); os.fsync(stream.fileno())
    # Both exact paths were constructed inside the just-created, resolved own root.
    if partial.resolve().parent != output_root.resolve() or target.exists():
        raise ValueError('atomic own output target changed')
    os.replace(partial,target)
    return target


def collect(dispatch, output_root, *, connector=None, packet_reader=None, cap_seconds=6000, interval_seconds=20):
    validate_dispatch(dispatch)
    path = Path(output_root)
    if not path.is_absolute() or path.exists():
        raise ValueError('output root already consumed or not absolute')
    client = None
    try:
        client = (connect_original if connector is None else connector)()
        packet = (remote_packet if packet_reader is None else packet_reader)(client,dispatch,
            cap_seconds=cap_seconds,interval_seconds=interval_seconds)
        result = summarize(dispatch,packet)
    except Exception as exc:
        result = summarize(dispatch,dict(documents={},file_metadata={},
            collector_errors=[dict(type=type(exc).__name__,message=str(exc))]))
    finally:
        if client is not None:
            try:
                client.close()
            except Exception as exc:
                result['errors'].append(dict(check='transport_close',error=type(exc).__name__+': '+str(exc)))
                result['passed_closed_capture_execution'] = False
                result['status'] = 'INCONCLUSIVE_METADATA_GAP_OR_COLLECTOR_CAP'
    return atomic_closed(path,result),result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dispatch',type=Path,required=True)
    parser.add_argument('--output-root',type=Path)
    args = parser.parse_args(); raw = args.dispatch.read_bytes()
    if len(raw) > 1024*1024:
        raise ValueError('dispatch metadata exceeds1MiB')
    dispatch = validate_dispatch(json.loads(raw))
    from source_pins import verify_sources
    verify_sources()  # Local fixed source bytes once; never credentials/native metadata.
    output = args.output_root or R/'reports'/('PHASE1_E3_CAPTURE_RESULT_COLLECTION_V4_'+time.strftime('%Y%m%d_%H%M%S'))
    target,result = collect(dispatch,output)
    print(json.dumps(dict(report=str(target),status=result['status'],gate1=result['gate1'],stage2_GO=False)))
    return 0 if result['passed_closed_capture_execution'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
