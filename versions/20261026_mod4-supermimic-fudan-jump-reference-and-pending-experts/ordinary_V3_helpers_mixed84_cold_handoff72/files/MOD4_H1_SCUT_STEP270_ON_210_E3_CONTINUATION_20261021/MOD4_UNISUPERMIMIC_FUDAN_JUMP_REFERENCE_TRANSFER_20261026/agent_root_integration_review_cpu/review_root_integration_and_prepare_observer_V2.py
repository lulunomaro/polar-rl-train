"""Independent local source/metadata review. No bridge/worker/binder is executed."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import importlib.util
import json
import sys
import time
import traceback

HERE=Path(__file__).resolve().parent
J=HERE.parent
T=J.parent
INTEGRATED=J/'root_integrated_native_Fudan_V3'
BASE=J/'agent_native_finalization_cpu/h1_supermimic_bridge_v1.py'
PROTOCOL=J/'agent_next_mixed84_protocol'
N=T/'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026'
snap=HERE/'source_metadata_snapshots'
snap.mkdir()
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
read=lambda path:json.loads(Path(path).read_bytes())


def snapshot(path,label):
    raw=Path(path).read_bytes()
    with (snap/label).open('xb') as stream:stream.write(raw)
    return dict(path=str(path),snapshot=str(snap/label),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest())


def fn(tree,name):
    return next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name==name)


def canonical(node):return ast.dump(node,include_attributes=False)


def main():
    inputs=read(INTEGRATED/'ROOT_REVIEWED_MIXED84_INPUTS_V3_ACTUAL.json')
    bridge_text=(INTEGRATED/'h1_supermimic_bridge_v1.py').read_text('utf8')
    base_text=BASE.read_text('utf8')
    sources=[snapshot(INTEGRATED/'h1_supermimic_bridge_v1.py','root_bridge.py'),
             snapshot(INTEGRATED/'ROOT_REVIEWED_MIXED84_INPUTS_V3_ACTUAL.json','root_reviewed_inputs.json'),
             snapshot(J/'reports/ROOT_FUDAN_V3_BRIDGE_SOURCE_INTEGRATION_AST_REVIEW_ACTUAL.json','root_AST_review.json'),
             snapshot(BASE,'frozen_finalization_bridge.py'),
             snapshot(PROTOCOL/'mixed84_protocol_v1.py','frozen_mixed84_protocol.py'),
             snapshot(N/'observe_mixed84_baselines_native_first_finite_TEMPLATE.py','original_N84_observer.py'),
             snapshot(N/'deploy_mixed84_original_writer_TEMPLATE.py','original_N84_deployer.py'),
             snapshot(N/'payloads/e2/target_H1_step270_closed_source_sdk_cpu_review_v1.py','target_SDK_CPU_source.py'),
             snapshot(N/'payloads/e2/test_native_h1_fudan_reference_CPU_v84.py','native_reference_CPU_source.py')]
    old=ast.parse(base_text);new=ast.parse(bridge_text)
    oldrun=fn(old,'run');newrun=fn(new,'run')
    assert canonical(ast.Module(body=[n for n in old.body if n is not oldrun],type_ignores=[]))==canonical(ast.Module(body=[n for n in new.body if n is not newrun],type_ignores=[]))
    for name in ('save','wm_update','pi_update'):
        assert canonical(next(n for n in oldrun.body if isinstance(n,ast.FunctionDef) and n.name==name))==canonical(next(n for n in newrun.body if isinstance(n,ast.FunctionDef) and n.name==name))
    assert canonical(oldrun.body[-1])==canonical(newrun.body[-1]),'Finalization lifecycle changed'
    learner_index=next(i for i,n in enumerate(newrun.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='learner' for t in n.targets))
    order_index=next(i for i,n in enumerate(newrun.body) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='actual_joint_names' for t in n.targets))
    for_sdk_index=next(i for i,n in enumerate(newrun.body) if isinstance(n,ast.Assign) and any(isinstance(v,ast.Attribute) and v.attr=='for_sdk_joint_order' for v in ast.walk(n)))
    receipt_index=next(i for i,n in enumerate(newrun.body) if isinstance(n,ast.Expr) and 'NATIVE_FUDAN_REFERENCE_RUNTIME_ORDER_ACTUAL.json' in ast.unparse(n))
    assert order_index<for_sdk_index<receipt_index<learner_index
    order_node=newrun.body[order_index]
    assert "env.scene['robot'].joint_names" in ast.unparse(order_node)
    assert 'for_offline_joint_order' not in bridge_text
    producer=next(n for n in newrun.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='publisher' for t in n.targets))
    expected_fields={'bridge_source_SHA','finalization_source_SHA','bootstrap_task_source_SHA','reference_artifact_SHA',
                     'adapter_CPU_report_SHA','objective_contract_SHA','runtime_objective_contract_SHA'}
    dict_call=next(n.value for n in producer.value.keywords if n.arg=='producer')
    assert expected_fields<={kw.arg for kw in dict_call.keywords}
    spec=importlib.util.spec_from_file_location('reviewed_pure_mixed84_protocol',PROTOCOL/'mixed84_protocol_v1.py')
    protocol=importlib.util.module_from_spec(spec);spec.loader.exec_module(protocol)
    protocol.validate_reference_preparation(inputs['reference_bundle'])
    protocol.validate_objective_contract(inputs['reference_bundle']['objective_contract'])
    assert inputs['reference_bundle']['candidate_pins']['bridge_source_SHA']==H(INTEGRATED/'h1_supermimic_bridge_v1.py')
    for rel,row in inputs['native_candidate_files'].items():
        assert Path(row['local_path']).suffix=='.py'
        assert H(row['local_path'])==row['SHA'],rel
    original_observer=N/'observe_mixed84_baselines_native_first_finite_TEMPLATE.py'
    observer=original_observer.read_text('utf8')
    outer=ast.parse(observer)
    read72_node=next(n for n in outer.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='READ72' for t in n.targets))
    read72=ast.literal_eval(read72_node.value)
    assert 'from mixed84_protocol_v1 import validate_objective_contract' in read72
    assert 'sys.path.insert' not in read72
    fixed=read72.replace('import json,psutil,subprocess,time','import json,psutil,subprocess,time,sys',1)
    needle="B=Path(v['root']);node="
    assert fixed.count(needle)==1
    fixed=fixed.replace(needle,"B=Path(v['root']);sys.path.insert(0,str(B));node=",1)
    fixed_ast=ast.parse(fixed);original_ast=ast.parse(read72)
    reverted=copy.deepcopy(fixed_ast)
    reverted.body=[node for node in reverted.body if not (isinstance(node,ast.Expr) and isinstance(node.value,ast.Call) and ast.unparse(node.value.func)=='sys.path.insert')]
    for node in reverted.body:
        if isinstance(node,ast.Import):node.names=[alias for alias in node.names if alias.name!='sys']
    assert canonical(original_ast)==canonical(reverted)
    # Preserve all outer code exactly apart from READ72 string content.
    lines=observer.splitlines(keepends=True)
    replacement='READ72='+repr(fixed)+'\n'
    output=''.join(lines[:read72_node.lineno-1])+replacement+''.join(lines[read72_node.end_lineno:])
    out=HERE/'observe_mixed84_baselines_native_first_finite_V2_UNUSED.py'
    with out.open('x',encoding='utf8') as stream:stream.write(output)
    check_outer=ast.parse(output)
    new_read72_node=next(n for n in check_outer.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='READ72' for t in n.targets))
    new_read72_node.value=copy.deepcopy(read72_node.value)
    assert canonical(outer)==canonical(check_outer)
    compile(output,str(out),'exec');compile(fixed,'new_READ72_compile_only','exec')
    with (HERE/'OBSERVER_V2_MINIMAL.diff').open('x',encoding='utf8') as stream:
        stream.write(''.join(difflib.unified_diff(read72.splitlines(True),fixed.splitlines(True),fromfile='original_READ72',tofile='fixed_READ72_V2')))
    # Minimal import resolution fixture; do not execute READ72 or any real observer.
    fixture=HERE/'import_resolution_fixture';fixture.mkdir()
    with (fixture/'mixed84_protocol_v1.py').open('x',encoding='utf8') as stream:
        stream.write('def validate_objective_contract(value):\n    return value.get("fixture_only") is True\n')
    saved_path=list(sys.path);saved_module=sys.modules.pop('mixed84_protocol_v1',None)
    negative=None
    try:
        sys.path=[item for item in sys.path if Path(item or '.').resolve()!=fixture.resolve()]
        try:exec('from mixed84_protocol_v1 import validate_objective_contract',{})
        except ModuleNotFoundError as error:negative=str(error)
        else:raise AssertionError('Fixture protocol unexpectedly importable without payload path')
        scope={'B':fixture,'sys':sys}
        exec('sys.path.insert(0,str(B));from mixed84_protocol_v1 import validate_objective_contract',scope)
        assert scope['validate_objective_contract']({'fixture_only':True})
    finally:
        sys.path=saved_path;sys.modules.pop('mixed84_protocol_v1',None)
        if saved_module is not None:sys.modules['mixed84_protocol_v1']=saved_module
    report=dict(epoch=time.time(),attempt_id='root-Fudan-V3-source-contract-independent-review',
        passed_bridge_source_review=True,passed_input_source_CPU_metadata=True,
        actual_joint_order_before_learner_first_native_control_and_Pi=True,
        runtime_provider_scope_and_producer_pin_contract_correct=True,
        frozen_class_other_functions_save_WM_Pi_lifecycle_AST_exact=True,
        actual_runtime_or_model_behavior_tested=False,
        finding=dict(priority='P1',component='first native observer READ72 import resolution',
            original_problem='python -c has no payload root in sys.path before local mixed84_protocol import',
            consequence='ModuleNotFoundError after native policy becomes positive; a reader failure, not a training failure',
            original_negative_fixture=negative,fix='Add sys import and sys.path.insert(0,str(B)) before local gate import',
            correction=str(out),correction_SHA=H(out),minimal_remote_AST_change_only=True,
            all_other_outer_observer_AST_exact=True,original_files_unchanged=True),
        preGO_SDK_interface_review='SDK producer emits passed_CPU_only/source_SHA/all17Adam/manifest_SHA/actual_RSL_sources/new_reward_integration_CPU/sampling_acceleration_CPU consumed by native CPU/guard. No additional static interface blocker found in this pass; actual target SDK/RSL and reference algebra execution remains required.',
        no_preGO_runtime_order_cycle=True,
        root_review_report_flags_are_source_only_not_actual_runtime_or_GO=True,
        reader_path_error_preserved='Initial shorthand lookup at J/ROOT_REVIEWED_MIXED84_INPUTS_V3_ACTUAL.json was absent; resolved actual nested path from root AST review receipt without any once replay.',
        sources=sources,
        no_network_remote_GPU_model_weights_policy_inference_physics_training_budget_ledger_locks_or_Git_action=True,
        no_other_directory_mutation=True,Git_status='LOCAL_PENDING_ROOT_PHASE_ARCHIVE')
    with (HERE/'ROOT_BRIDGE_INPUTS_AND_OBSERVER_V2_INDEPENDENT_REVIEW_ACTUAL.json').open('x',encoding='utf8') as stream:json.dump(report,stream,indent=2)
    print(json.dumps(dict(bridge_review_passed=True,actual_runtime_unverified=True,
                          observer_P1_fixed_in_new_source_only=True,observer_V2=str(out),report=str(HERE/'ROOT_BRIDGE_INPUTS_AND_OBSERVER_V2_INDEPENDENT_REVIEW_ACTUAL.json'))))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (HERE/('REVIEW_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as stream:
            json.dump(dict(epoch=time.time(),error=traceback.format_exc(),no_live_action=True,original_sources_unchanged=True),stream,indent=2)
        raise
