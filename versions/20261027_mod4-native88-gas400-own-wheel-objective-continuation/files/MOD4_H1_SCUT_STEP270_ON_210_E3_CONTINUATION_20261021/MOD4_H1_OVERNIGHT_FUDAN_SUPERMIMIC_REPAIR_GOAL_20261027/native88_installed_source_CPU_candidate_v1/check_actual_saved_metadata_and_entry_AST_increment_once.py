"""New metadata/AST increment only; no previous fixture or model reexecution."""
from pathlib import Path
import sys,json,ast,hashlib,traceback
D=Path(__file__).resolve().parent;L=D.parent;T=L.parent;N=T/'H1_STEP270_THREE_GPU_OWN_FUDAN_NATIVE_V87_20261027'
sys.path[:0]=[str(D),str(L/'native88_two_available_H1_runtime_protocol_source_v1')]
from native88_source_guard_v1 import validate_saved_source_evidence,read,H
def main():
    pair=read(N/'reports/H1_NATIVE87R5_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json')
    closing=N/'reports/H1_NATIVE87R5_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json'
    asset=read(L/'native88_gas400_actual_asset_CPU_admission_20261027/ASSET_COMPOSITION_CPU_ACTUAL.json')
    qualified=read(L/'native88_own_step_differentiable_objective_source_v1/SELECTED_OWN_STEP_OBJECTIVE_SOURCE_QUALIFICATION_FINAL_ACTUAL.json')
    c=dict(previous_R5_closure_SHA=H(closing),gas400_parameter_contract_SHA=asset['parameter_source_contract_SHA'])
    task=dict(previous_R5_closure_SHA=c['previous_R5_closure_SHA'])
    assert validate_saved_source_evidence(c,task,dict(qualified_R5_pair_report=pair,previous_R5_closure=read(closing),actual_asset_report=asset,own_step_objective_qualification=qualified))
    target=ast.parse((D/'target_native88_source_sdk_cpu_v1.py').read_bytes())
    calls=[n for n in ast.walk(target) if isinstance(n,ast.Call)]
    names=[ast.unparse(n.func) for n in calls]
    assert names.count('torch.load')==2
    assert not any('process_iter' in x for x in names)
    # Exercise the real worker source with only the target's pure AST checker;
    # no top-level target execution, App, source model or physical factory.
    node=next(n for n in target.body if isinstance(n,ast.FunctionDef) and n.name=='factory_source_check')
    ns=dict(ast=ast);exec(compile(ast.Module(body=[node],type_ignores=[]),'pure_factory_source_check','exec'),ns)
    result=ns['factory_source_check'](L/'native88_two_available_H1_runtime_protocol_source_v1',{})
    assert result['passed'] and result['actual_GPU_runtime_pending']
    report=dict(passed=True,count=4,scope='saved actual R5 metadata + original worker AST only',actual_saved_metadata_validated=True,
        source_read_pins={str(p):H(p) for p in (N/'reports/H1_NATIVE87R5_TYPED_FINALS_AND_ORIGINAL_COST_CPU_ACTUAL.json',closing,L/'native88_gas400_actual_asset_CPU_admission_20261027/ASSET_COMPOSITION_CPU_ACTUAL.json')},
        actual_target_CPU_executed=False,models_or_USD_read=False,actual_gpu=False,old_fixture_not_rerun=True,worker_AST=result)
    with (D/'ACTUAL_SAVED_METADATA_AND_ENTRY_AST_INCREMENT_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,indent=2)
    print(json.dumps(dict(passed=True,count=4)))
if __name__=='__main__':
    try:main()
    except BaseException:
        with (D/'ACTUAL_SAVED_METADATA_AND_ENTRY_AST_INCREMENT_ORIGINAL_ERROR.json').open('x',encoding='utf8') as f:json.dump(dict(passed=False,error=traceback.format_exc()),f,indent=2)
        raise
