"""Future one-seed dual-role metadata collector; no collection occurs on import.

Original source grade, own SDK-child waits/both EX and outer actual Popen.wait
are independent evidence. No SOURCE/fake test is an actual SDK or quality pass.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import shlex
import time
import good_holdout_contract as C
from good_holdout_remote_reader import BIG, _complete

HERE=Path(__file__).resolve().parent
R=HERE.parent
CONNECTOR=R.parent/'mod4v1_experts_fulldr_rm70_20261101/project_connector.py'
CONNECTOR_SHA='623599cf014fe39b46f1a10bc4e858c498860578f4b277ac81a802ede2da09d6'


def summarize(dispatch, packet):
    C.validate_dispatch(dispatch)
    errors=[]; gates={}; documents=packet.get('documents',{}) if type(packet) is dict else {}
    if type(documents) is not dict: documents={}
    info=packet.get('file_metadata',{}) if type(packet) is dict else {}
    if type(info) is not dict: info={}
    def check(label, condition):
        gates[label]=bool(condition)
        if not condition: errors.append(dict(check=label))
    check('typed_own_packet',type(packet) is dict and packet.get('kind')=='GOOD_HOLDOUT_OWN_METADATA_PACKET_V1'
        and all(packet.get(k)==dispatch[k] for k in ('root','group_id','seed','evaluation_purpose')))
    producer=documents.get(C.GRADE)
    check('producer_original_source_grade',type(producer) is dict
        and producer.get('kind')=='CLOSED_EMBEDDED_TEACHER_REFERENCE_SOURCE_GRADE_V1'
        and producer.get('passed_closed_reference_source_grade') is True and producer.get('original_error') is False
        and producer.get('reasons')==[] and producer.get('checked_roles')==list(C.REQUESTED)
        and producer.get('group_root')==dispatch['root'] and producer.get('batch_purpose')==C.purpose(dispatch['seed']))
    exit_scope=documents.get('PARENT_EXIT_SCOPE.json',{})
    if type(exit_scope) is not dict: exit_scope={}
    waits=exit_scope.get('child_waits')
    actual_waits=(type(waits) is list and len(waits)==2 and all(type(v) is dict for v in waits)
        and {v.get('role') for v in waits}==set(C.REQUESTED)
        and all(v.get('actual_waited') is True and type(v.get('returncode')) is int and v['returncode']==0 for v in waits))
    check('original_ownchild_actual_waits',exit_scope.get('all_own_children_waited') is True and actual_waits)
    check('original_both_EX_released',exit_scope.get('original_single_GPU_private_EX_released') is True
        and exit_scope.get('original_global_finite_EX_released') is True and exit_scope.get('errors')==[]
        and type(exit_scope.get('canonical_writes')) is int and exit_scope['canonical_writes']==0)
    outer=documents.get(C.WAITED,{})
    if type(outer) is not dict: outer={}
    outer_binding=all(outer.get(k)==dispatch.get(k) for k in
        ('root','group_id','seed','GPU_UUID','evaluation_purpose','controller','parent','parent_source_SHA',
         'controller_source_SHA','stage_receipt_SHA256','GROUP_PLAN_bytes','GROUP_PLAN_SHA256'))
    check('independent_outer_actual_Popen_wait',outer.get('kind')==C.WAITED_KIND
        and outer.get('actual_parent_p_wait_returned') is True and type(outer.get('returncode')) is int
        and outer['returncode']==0 and outer.get('controller_errors')==[] and outer_binding
        and outer.get('original_parent_resource_close_wait_not_replaced') is True
        and type(outer.get('actual_native_parent_Popen_calls')) is int and outer['actual_native_parent_Popen_calls']==1)
    validation=packet.get('cached_validation') if type(packet) is dict else None
    check('independent_full_cached_metadata',type(validation) is dict and validation.get('kind')=='GOOD_HOLDOUT_INDEPENDENT_CACHED_METADATA_VALIDATION_V1'
        and validation.get('passed') is True and validation.get('producer_source_grade_preserved') is True
        and validation.get('materialization_raw_receipt_and_plan_validated') is True
        and validation.get('ownchild_waits_and_both_EX_verified') is True
        and validation.get('independent_outer_actual_wait_verified') is True
        and validation.get('checked_roles')==list(C.REQUESTED))
    closure=packet.get('metadata_closure') if type(packet) is dict else None
    try:
        C.need(type(closure) is dict and closure.get('kind')=='WHOLE_ORIGINAL_GOOD20_METADATA_CLOSURE_V1'
            and closure.get('source_aliases')==20 and closure.get('full_original_modules') is True
            and closure.get('AST_cropped_or_stubbed') is False and closure.get('full_AppV6_Base_imported') is True
            and closure.get('helper_base_is_actual_module') is True and closure.get('native_modules_loaded')==[]
            and closure.get('parent_or_worker_main_called') is False and closure.get('old_producer_IO_predicates_rerun') is False,
            'complete original metadata closure receipt differs')
        rows=closure['sources']; C.need(type(rows) is list and len(rows)==20,'good20 full SOURCE receipt required')
        actual={row['relative']:(row['bytes'],row['SHA256']) for row in rows}
        C.need(len(actual)==20 and actual==C.OVERLAY_PINS,'complete source aliases/bytes differ')
        check('whole_good20_AppV6_Base_closure',True)
    except Exception as exc:
        check('whole_good20_AppV6_Base_closure',False); errors[-1]['error']=str(exc)
    try:
        for name in BIG+('GROUP_PLAN.json',C.STAGE_NAME): _complete(info,name)
        C.need((info['GROUP_PLAN.json']['bytes'],info['GROUP_PLAN.json']['SHA256'])==
            (dispatch['GROUP_PLAN_bytes'],dispatch['GROUP_PLAN_SHA256'])
            and info[C.STAGE_NAME]['SHA256']==dispatch['stage_receipt_SHA256'],'raw stage/plan identity differs')
        C.need(packet.get('whole_original_FINALs_read_once') is True and packet.get('FINAL_projection_applied') is False
            and packet.get('read_only_own_metadata') is True,'complete onecache/no-projection receipt required')
        check('whole_original_bytes_onecache',True)
    except Exception as exc:
        check('whole_original_bytes_onecache',False); errors[-1]['error']=str(exc)
    final=documents.get('FINAL.json'); terminal=documents.get('TERMINAL_ROWS.json')
    check('good_rows_not_Phase1_terminal',type(final) is dict and final.get('kind')=='ACTUAL_GOOD_EXPERT_HOLDOUT_C878_S135_V1'
        and 'terminal' not in final and type(terminal) is list and len(terminal)==2 and final.get('rows')==terminal
        and final.get('seed')==dispatch['seed'] and final.get('batch_purpose')==C.purpose(dispatch['seed']))
    observed={}
    for role in C.REQUESTED:
        data=documents.get('cases/'+role+'/FINAL.json')
        observed[role]={key:C.nullable_count(data.get(key)) if type(data) is dict else None
                        for key in ('controls','physics','feedback','actor_calls')}
        if type(data) is dict:
            observed[role]['source_actual_BPTT_policy_steps']=C.nullable_count(data.get('source_cache',{}).get('actual_BPTT_policy_steps')) if type(data.get('source_cache')) is dict else None
        else: observed[role]['source_actual_BPTT_policy_steps']=None
    original_error_names=[n for n in ('PARENT_ORIGINAL_ERROR.json','GROUP_ABORT.json','GROUP_STARTUP_ABORT.json',C.ERROR) if n in documents]
    for role in C.REQUESTED:
        name='cases/'+role+'/WORKER_ERROR.json'
        if name in documents: original_error_names.append(name)
    secondary=packet.get('secondary_worker_errors',{}) if type(packet) is dict else {}
    check('no_durable_original_errors',not original_error_names and type(secondary) is dict
        and all(secondary.get(r)==[] for r in C.REQUESTED))
    collector_errors=packet.get('collector_errors') if type(packet) is dict else None
    check('collector_errors_empty',collector_errors==[])
    if type(collector_errors) is list: errors.extend(dict(check='collector',detail=e) for e in collector_errors)
    passed=all(gates.values())
    actual_outer_rc=outer.get('returncode') if type(outer.get('returncode')) is int else None
    definite_error=bool(original_error_names or (type(producer) is dict and producer.get('passed_closed_reference_source_grade') is False)
        or (actual_outer_rc is not None and actual_outer_rc!=0))
    status='CLOSED_GOOD_REFERENCE_SOURCE_GRADE_AND_ACTUAL_WAITS' if passed else 'FAILED_ORIGINAL_ERROR_OR_SOURCE_GRADE' if definite_error else 'INCONCLUSIVE_MISSING_METADATA_OR_OUTER_WAIT'
    return dict(kind='GOOD_HOLDOUT_CLOSED_RESULT_V1',root=dispatch['root'],group_id=dispatch['group_id'],seed=dispatch['seed'],
        evaluation_purpose=C.purpose(dispatch['seed']),requested_roles=list(C.REQUESTED),deferred_roles=list(C.DEFERRED),
        passed_closed_good_reference_execution=passed,status=status,gates=gates,errors=errors,
        producer_original_source_grade=producer,producer_grade_rewritten=False,
        actual_outer_parent_returncode=actual_outer_rc,own_child_waits=waits,
        observed_counts=observed,original_error_metadata_names=original_error_names,
        metadata=packet,complete_original_FINAL_projection_applied=False,
        conditional_original_scope_results=(final.get('absolute_original_scope_results') if passed else None),
        pooled_whole_skill_rate=None,ninety_percent_whole_skill_claim=None,relative_improvement=None,
        noninferiority_claim=None,matched_UID_or_cache_improvement_claim=None,
        original_acceptance_changed=False,canonical_write_or_lock_or_native_control_operations=0,
        native_deadline_extended=False,stage2_GO=False)


def conditional_two_seed_summary(results, original_runtime):
    """Original 170-219 summary only AFTER two externally-qualified group results."""
    C.need(type(results) is list and len(results)==2 and {v.get('seed') for v in results}==set(C.SEEDS)
        and len({v.get('group_id') for v in results})==2,'two independent externally-qualified groups required')
    batches=[]
    for value in results:
        C.need(value.get('passed_closed_good_reference_execution') is True and value.get('status')=='CLOSED_GOOD_REFERENCE_SOURCE_GRADE_AND_ACTUAL_WAITS'
            and type(value.get('gates')) is dict and value['gates'] and all(value['gates'].values()),
            'no conditional aggregation of a merely materialized/source-grade-only/unwaited group')
        batch=value['metadata']['documents']['FINAL.json']
        C.need(batch.get('seed')==value['seed'] and batch.get('group_id')==value['group_id'],'two-seed batch/result binding differs')
        batches.append(batch)
    # original_runtime comes from the complete pinned metadata closure, never an AST subset.
    return original_runtime.summarize_independent_seed_results(batches)


def connect_original():
    raw=CONNECTOR.read_bytes()
    C.need(hashlib.sha256(raw).hexdigest()==CONNECTOR_SHA,'original project connector source differs')
    spec=importlib.util.spec_from_file_location('_good_holdout_result_original_connector',CONNECTOR)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module.connect72()


def remote_packet(client, dispatch, *, cap_seconds=6000, interval_seconds=20):
    # Complete own configuration + reader modules are executed in RAM. Original
    # runtime/core/AppV6/Base/guard/reference modules are imported whole from root.
    common=(HERE/'good_holdout_contract.py').read_text(encoding='utf-8')
    reader=(HERE/'good_holdout_remote_reader.py').read_text(encoding='utf-8')
    code='import sys,types\n_c=types.ModuleType("good_holdout_contract")\nsys.modules[_c.__name__]=_c\n'
    code+='exec(compile('+repr(common)+',"<complete_good_holdout_contract_SOURCE>","exec"),_c.__dict__)\n'
    code+=reader+'\nremote_main('+repr(dispatch)+',cap_seconds='+repr(cap_seconds)+',interval_seconds='+repr(interval_seconds)+')\n'
    command=shlex.quote(C.BASE+'/run-python.sh')+' -u -B -c '+shlex.quote(code)
    incoming,outgoing,err=client.exec_command(command,timeout=cap_seconds+120);incoming.close()
    raw=outgoing.read(C.EXPORT_MAX+1);error=err.read(65537);rc=outgoing.channel.recv_exit_status()
    C.need(len(raw)<=C.EXPORT_MAX and len(error)<=65536,'complete metadata export/stdout exceeds bound')
    C.need(rc==0,'metadata reader exit '+str(rc)+': '+error.decode('utf-8','replace')[-4000:])
    value=json.loads(raw);C.need(type(value) is dict and value.get('kind')=='GOOD_HOLDOUT_OWN_METADATA_PACKET_V1','own good packet kind differs')
    value['transport']=dict(returncode=rc,stderr_tail=error.decode('utf-8','replace'))
    return value


def atomic_closed(output_root, value):
    output_root=Path(output_root)
    C.need(output_root.is_absolute() and not output_root.exists(),'new absent absolute local result root required')
    output_root.mkdir(parents=True,exist_ok=False)
    target=output_root/'CLOSED_RESULT.json';partial=output_root/'CLOSED_RESULT.json.partial'
    with partial.open('x',encoding='utf-8') as stream:
        json.dump(value,stream,indent=2,allow_nan=False);stream.flush();os.fsync(stream.fileno())
    C.need(partial.resolve().parent==output_root.resolve() and not target.exists(),'own atomic result target changed')
    os.replace(partial,target)
    return target


def collect(dispatch, output_root, *, connector=None, packet_reader=None, cap_seconds=6000, interval_seconds=20):
    C.validate_dispatch(dispatch);path=Path(output_root)
    C.need(path.is_absolute() and not path.exists(),'one-use local result root required')
    client=None
    try:
        client=(connect_original if connector is None else connector)()
        packet=(remote_packet if packet_reader is None else packet_reader)(client,dispatch,cap_seconds=cap_seconds,interval_seconds=interval_seconds)
        result=summarize(dispatch,packet)
    except Exception as exc:
        result=summarize(dispatch,dict(documents={},file_metadata={},collector_errors=[dict(type=type(exc).__name__,message=str(exc))]))
    finally:
        if client is not None:
            try: client.close()
            except Exception as exc:
                result['errors'].append(dict(check='transport_close',error=type(exc).__name__+': '+str(exc)))
                result['passed_closed_good_reference_execution']=False;result['status']='INCONCLUSIVE_MISSING_METADATA_OR_OUTER_WAIT'
    return atomic_closed(path,result),result


def main():
    C.require_final_pins()
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--dispatch',type=Path,required=True);parser.add_argument('--output-root',type=Path,required=True)
    args=parser.parse_args()
    with args.dispatch.open('rb') as stream:raw=stream.read(C.PLAN_MAX+1)
    C.need(len(raw)<=C.PLAN_MAX,'bounded dispatch metadata required')
    from source_pins import verify_sources
    verify_sources()
    target,result=collect(C.validate_dispatch(json.loads(raw)),args.output_root)
    print(json.dumps(dict(report=str(target),status=result['status'],seed=result['seed'],stage2_GO=False)))
    return 0 if result['passed_closed_good_reference_execution'] else 1


if __name__=='__main__':raise SystemExit(main())
