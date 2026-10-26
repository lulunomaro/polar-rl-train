"""Minimal pure CPU fixtures; no binder/installer/owner/ledger operation."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import time
import traceback
import types

HERE=Path(__file__).resolve().parent;P=HERE.parent
H=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
dump=lambda node:ast.dump(node,include_attributes=False)
rows=[]


def parse(path):return ast.parse(path.read_text('utf8'))


def fn(module,name):return next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name==name)


def test_compile_dependencies_paths():
    for path in HERE.rglob('*.py'):
        if 'source_snapshots' in path.parts:continue
        tree=parse(path);compile(tree,str(path),'exec')
        for node in tree.body:
            if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CODE' for t in node.targets):
                code=ast.literal_eval(node.value);compile(code,str(path)+'_remote','exec')
                assert '2610v85m' in code
    binder=(HERE/'bind_dual72_V85M_migrated_source_UNUSED.py').read_text('utf8')
    assert "prebind85M_exact_history" in binder and "N.mkdir(exist_ok=True)" in binder
    assert "OLD=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_RESOURCE_V85_20261026'" in binder
    assert "N=T/'H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_MIGRATED_V85M_20261026'" in binder
    for path in (HERE/'install_dual72_V85M_source_SDK_native_CPU_only_UNUSED.py',HERE/'dual72_V85M_resource_install_source_v1.py',HERE/'controllers/mixed84_protocol_v1.py',HERE/'guards/e2_closed_production_continuation_CPU_v2.py',HERE/'guards/recovery_original_account_policy50_source_CPU.py'):assert path.is_file()
    installer=(HERE/'install_dual72_V85M_source_SDK_native_CPU_only_UNUSED.py').read_text('utf8')
    assert "sys.path.insert(0,str(N))" in installer
    assert '.launch(' not in installer and 'route.connect' not in installer
    return dict(all_first_batch_dependencies_exist=True,existing_reports_allowed=True,unique85Mhistory=True,explicit_runpy_root_import=True)


def test_protected_common_and_forwarder():
    for original_path in (P/'controllers/three_slot_common_v1.py',):
        old=parse(original_path);new=parse(HERE/'controllers/three_slot_common_v1.py')
        remove=lambda module:ast.Module(body=[n for n in module.body if not(isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ('C','LOCKS') for t in n.targets))],type_ignores=[])
        assert dump(remove(old))==dump(remove(new))
        for name in ('charge_values','spawn','state','native_CPU','authenticated_row'):assert dump(fn(old,name))==dump(fn(new,name))
    old=parse(P/'controllers/forwarded_original_owner_control_v1.py');new=parse(HERE/'controllers/forwarded_original_owner_control_v1.py')
    remove=lambda module:ast.Module(body=[n for n in module.body if not(isinstance(n,ast.FunctionDef) and n.name in ('send','close'))],type_ignores=[])
    assert dump(remove(old))==dump(remove(new))
    send=ast.unparse(fn(new,'send'))
    assert '_ssh(' not in send and '127.0.0.1' in send and 'hmac.compare_digest' in send
    assert (HERE/'controllers/three_slot_finite_node_v1.py').read_bytes()==(P/'controllers/three_slot_finite_node_v1.py').read_bytes()
    return dict(only_common_C_LOCKS_and_send_close_changed=True,charge_spawn_wait_source_HMAC_exact=True,node_bytes_exact=True)


def test_authority_modes_and_actual_fee():
    spec=importlib.util.spec_from_file_location('v85m_pure_authority',HERE/'controllers/single_writer72_authority_V85M_source.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    hand=dict(schema='mod4.single_writer72.authority_handoff.v1',authority_generation=module.GENERATION,authority_host='72',
        activated=True,approved=True,old_authority_retired=True,canonical_path=str(module.CANONICAL),owner_locks=[str(x) for x in module.LOCKS],
        canonical_copied=False,historical_records_reconstructed=False,old_canonical_SHA256=module.OLD_SHA,
        known_last_settled_run_id='THREE4090_EXPERT_ORIGINAL_1792994651814636100',latest_original_owner_allout=True,latest_original_active_segment=None,
        authorization_file_SHA256=module.AUTH_SHA,seed_canonical_SHA256='7'*64,budget_mode=module.MODE)
    module.validate_authority_handoff(hand,module.AUTH_SHA);module.read_authority=lambda:hand
    class Receipt:
        def __init__(self,exists):self.present=exists
        def exists(self):return self.present
        def read_bytes(self):return json.dumps(dict(approved=True,limits_restored=True,authority_generation=module.GENERATION,single4090_returned=True,budget_mode=module.FINITE_MODE,minimum_remaining_seconds=86412.86069250107)).encode()
    c=dict(authority_generation=module.GENERATION,budget_mode=module.MODE,active_spending_cap_seconds=None,
        authorized_training_seconds=2268000,historical_budget_extension_count=9,new_authority_budget_extensions=[],
        historical_charged_training_seconds=module.HISTORICAL_CHARGED,charged_training_seconds=2268010.,remaining_training_seconds=-10.,completed_segments=[],active_segment=None)
    module.RESTORATION=Receipt(False);assert module.authority_budget_GO_allowed(c) and module.authority_original_extension_count(c)==9
    module.RESTORATION=Receipt(True);c['budget_mode']=module.FINITE_MODE
    c['remaining_training_seconds']=86412.86069250107;c['charged_training_seconds']=2268000-c['remaining_training_seconds']
    assert module.authority_budget_GO_allowed(c) is False
    c['remaining_training_seconds']+=.01;c['charged_training_seconds']=2268000-c['remaining_training_seconds'];assert module.authority_budget_GO_allowed(c)
    common=parse(HERE/'controllers/three_slot_common_v1.py');scope={};exec(compile(ast.Module(body=[fn(common,'charge_values')],type_ignores=[]),'original_charge_only','exec'),scope)
    tracking=dict(charged_training_seconds=module.HISTORICAL_CHARGED,remaining_training_seconds=module.HISTORICAL_REMAINING)
    active=dict(experts={},charged_expert_seconds=0.);go=dict(e2=dict(learning_started_epoch=100.,max_parent_seconds=3900))
    scope['terminal']=lambda row:bool(row.get('terminal_all_own_children_waited') and row.get('returncode') is not None)
    scope['charge_values'](tracking,active,go,dict(e2=dict(terminal_all_own_children_waited=True,returncode=0,owner_received_terminal_epoch=4105.)),4106.)
    assert active['experts']['e2']['charged_seconds']==4005. and active['experts']['e2']['duration_bound_passed'] is False
    assert abs(tracking['remaining_training_seconds']-(module.HISTORICAL_REMAINING-4005.))<1e-5
    return dict(unlimited_allows_negative_truthful_tracking=True,finite_strict_floor_restored=True,no_fake_nine_extensions=True,overcap_actual_fee_full_not_clamped=True)


def main():
    for test in (test_compile_dependencies_paths,test_protected_common_and_forwarder,test_authority_modes_and_actual_fee):
        try:rows.append(dict(name=test.__name__,passed=True,details=test()))
        except BaseException as error:rows.append(dict(name=test.__name__,passed=False,error=str(error),traceback=traceback.format_exc()))
    pins=[]
    for path in sorted(HERE.rglob('*.py')):
        if 'source_snapshots' in path.parts or '__pycache__' in path.parts:continue
        pins.append(dict(path=str(path),bytes=path.stat().st_size,SHA=H(path)))
    result=dict(epoch=time.time(),attempt_id='V85M-first-batch-source-CPU-'+str(time.time_ns()),passed=all(x['passed'] for x in rows),tests=rows,
        count=len(rows),passed_count=sum(x['passed'] for x in rows),file_pins=pins,
        no_binder_installer_remote_ledger_GPU_weights_Git_or_GO_action=True,Git_status='LOCAL_PENDING_ROOT_PHASE_ARCHIVE')
    report=HERE/'reports'/('V85M_FIRST_BATCH_CPU_'+str(time.time_ns())+'_ACTUAL.json')
    with report.open('x',encoding='utf8') as stream:json.dump(result,stream,indent=2)
    print(json.dumps(dict(passed=result['passed'],passed_count=result['passed_count'],count=result['count'],report=str(report))))
    return 0 if result['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
