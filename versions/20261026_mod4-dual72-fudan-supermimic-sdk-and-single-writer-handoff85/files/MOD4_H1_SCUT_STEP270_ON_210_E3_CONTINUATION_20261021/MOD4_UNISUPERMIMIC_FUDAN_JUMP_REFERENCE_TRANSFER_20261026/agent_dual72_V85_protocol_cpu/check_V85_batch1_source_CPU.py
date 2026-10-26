"""Pure source/AST/dictionary fixtures; no binder/installer/owner call."""
from pathlib import Path
import ast
import copy
import hashlib
import json
import time
import traceback
import types

HERE=Path(__file__).resolve().parent
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
canon=lambda node:ast.dump(node,include_attributes=False)
results=[]


def tree(path):return ast.parse(path.read_text('utf8'))


def source_compiles_and_binder_dependencies():
    binder=tree(HERE/'bind_dual72_V85_from_reviewed84_TEMPLATE.py')
    for path in HERE.rglob('*.py'):
        if 'source_snapshots' in path.parts:continue
        module=tree(path);compile(module,str(path),'exec')
        for node in module.body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('CODE','READ210','READ72') for t in node.targets):
                value=ast.literal_eval(node.value)
                if isinstance(value,str):compile(value,str(path)+'_embedded','exec')
    for name in ('install_dual72_V85_source_SDK_native_CPU_only_UNUSED.py','dual72_V85_resource_install_source_v1.py'):
        assert (HERE/name).is_file()
    assert (HERE/'controllers/mixed84_protocol_v1.py').is_file()
    source=(HERE/'bind_dual72_V85_from_reviewed84_TEMPLATE.py').read_text('utf8')
    assert "assert not (N/'payloads').exists() and not (N/'controllers').exists()" in source
    assert 'assert not N.exists()' not in source
    assert "path.suffix in ('.pt','.npz','.usd','.stl')" in source
    return dict(compile_only=True,binder_dependencies_exist=True,existing_reports_allowed=True,no_binary_planning_hash=True)


def owner_selection_and_budget_AST():
    old=tree(HERE/'source_snapshots/84_owner.py')
    new=tree(HERE/'controllers/three_slot_finite_owner_V85_pair_source_only.py')
    owner=lambda module:next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='owner')
    before=owner(old);after=owner(new)
    specs={key:dict(key=key,max_parent_seconds=3900,exit_headroom_seconds=300) for key in ('e2','recovery')}
    scope=dict(specs=specs,b=types.SimpleNamespace(CAPS=dict(h1=3900,e2=3900,recovery=3900)),
               cfg=dict(scheduling_authority='human_requested_available_experts',deferred_experts=['h1']))
    assertions=[node for node in after.body[:8] if isinstance(node,ast.Assert)]
    assert len(assertions)==2
    for node in assertions:exec(compile(ast.Module(body=[node],type_ignores=[]),'pair_selector_fixture','exec'),scope)
    oldassert=next(node for node in before.body if isinstance(node,ast.Assert))
    try:exec(compile(ast.Module(body=[oldassert],type_ignores=[]),'original_selector_negative','exec'),scope)
    except AssertionError:pass
    else:raise AssertionError('Original three-slot owner should reject pair')
    restored=copy.deepcopy(after)
    old_asserts=[node for node in before.body[:8] if isinstance(node,ast.Assert)]
    new_asserts=[node for node in restored.body[:8] if isinstance(node,ast.Assert)]
    for oldnode,newnode in zip(old_asserts,new_asserts):
        restored.body[restored.body.index(newnode)]=copy.deepcopy(oldnode)
    budget=next(node for node in ast.walk(restored) if isinstance(node,ast.Assert) and 'max(86412.86069250107' in ast.unparse(node))
    oldbudget=next(node for node in ast.walk(before) if isinstance(node,ast.Assert) and 'authorized_training_seconds' in ast.unparse(node))
    original_budget=copy.deepcopy(budget)
    class Restore(ast.NodeTransformer):
        def visit_Call(self,node):
            if isinstance(node.func,ast.Name) and node.func.id=='max' and len(node.args)==2 and isinstance(node.args[0],ast.Constant) and node.args[0].value==86412.86069250107:return copy.deepcopy(node.args[1])
            return self.generic_visit(node)
    Restore().visit(restored)
    assert canon(before)==canon(restored),'Owner changed outside selectors and stricter budget floor'
    for remaining,expected in ((86412.86069250107,False),(86412.86169250107,True)):
        s=dict(scope,c=dict(active_segment=None,authorized_training_seconds=2268000,budget_extensions=[None]*9,remaining_training_seconds=remaining))
        try:exec(compile(ast.Module(body=[original_budget],type_ignores=[]),'strict_floor_fixture','exec'),s);passed=True
        except AssertionError:passed=False
        assert passed is expected
    return dict(pair_selection_passed=True,original_three_slot_rejection_retained=True,
                strict_floor_not_lowered=True,all_other_owner_AST_exact=True)


def unchanged_common_and_copy_loop():
    for name in ('three_slot_common_v1.py','three_slot_finite_node_v1.py','three_real_gpu_resource_v1.py','forwarded_original_owner_control_v1.py','mixed84_protocol_v1.py'):
        assert (HERE/'controllers'/name).read_bytes()==(HERE/'source_snapshots'/('84_controller_'+name)).read_bytes()
    old_code=ast.literal_eval(next(node.value for node in tree(HERE/'source_snapshots/84_e2_installer.py').body if isinstance(node,ast.Assign)))
    new_code=ast.literal_eval(next(node.value for node in tree(HERE/'dual72_V85_resource_install_source_v1.py').body if isinstance(node,ast.Assign)))
    loop=lambda text:next(node for node in ast.parse(text).body if isinstance(node,ast.For) and ast.unparse(node.iter)=="v['manifest']['files']")
    assert canon(loop(old_code))==canon(loop(new_code))
    assert 'TRAINING_BUDGET_10H.json' not in new_code and 'OWNER_IDENTITY' not in new_code
    assert "proof['models']['h1']['final']['SHA']" in new_code and "proof['models'][key]['final']['SHA']" in new_code
    return dict(charge_values_HMAC_node_network_C_LOCKS_bytes_exact=True,copy_loop_and_containment_AST_exact=True,
                native_H1_bootstrap_vs_normalE2_physical_proof_separate=True)


def only72_no_authority_or_launch():
    module=tree(HERE/'install_dual72_V85_source_SDK_native_CPU_only_UNUSED.py')
    calls=[node for node in ast.walk(module) if isinstance(node,ast.Call)]
    assert not any(isinstance(node.func,ast.Attribute) and node.func.attr in ('launch','install_h1') for node in calls)
    assert not any(isinstance(node,ast.Name) and node.id=='route' for node in ast.walk(module))
    assert not any(isinstance(node,ast.Attribute) and node.attr=='OWNER' for node in ast.walk(module))
    assert any(isinstance(node.func,ast.Attribute) and node.func.attr=='connect72' for node in calls)
    source=(HERE/'install_dual72_V85_source_SDK_native_CPU_only_UNUSED.py').read_text('utf8')
    assert 'TRAINING_BUDGET_10H.json' not in source
    assert 'original_live_account_checked=False' in source and 'owner_launched=False,node_launched=False,GO=False' in source
    return dict(only72_entry_no210_route_owner_canonical_or_launch=True,target_CPU_not_live_account_pass=True)


def main():
    for test in (source_compiles_and_binder_dependencies,owner_selection_and_budget_AST,unchanged_common_and_copy_loop,only72_no_authority_or_launch):
        try:results.append(dict(name=test.__name__,passed=True,details=test()))
        except BaseException as error:results.append(dict(name=test.__name__,passed=False,error=str(error),traceback=traceback.format_exc()))
    files=[HERE/'bind_dual72_V85_from_reviewed84_TEMPLATE.py',HERE/'dual72_V85_resource_install_source_v1.py',HERE/'install_dual72_V85_source_SDK_native_CPU_only_UNUSED.py']
    files.extend(sorted((HERE/'controllers').glob('*.py')))
    result=dict(epoch=time.time(),attempt_id='V85-batch1-source-CPU-'+str(time.time_ns()),passed=all(row['passed'] for row in results),
                tests=results,count=len(results),passed_count=sum(row['passed'] for row in results),
                file_pins=[dict(path=str(path),bytes=path.stat().st_size,SHA=H(path)) for path in files],
                no_binder_or_installer_or_live_owner_executed=True,no_weight_raw_GPU_network_Git_or_budget_action=True,
                original_live_account_checked=False,owner_GO_allowed=False,Git_status='LOCAL_PENDING_ROOT_PHASE_ARCHIVE')
    path=HERE/'reports'/('V85_BATCH1_SOURCE_CPU_'+str(time.time_ns())+'_ACTUAL.json')
    with path.open('x',encoding='utf8') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(dict(passed=result['passed'],passed_count=result['passed_count'],count=result['count'],report=str(path))))
    return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
