"""Installed70 source guard V2: closed69 normal cost, unchanged optimized source, exact saved-Adam substitution."""
from pathlib import Path
import ast,hashlib,json,os
from same_optimized_source_contract_metadata_candidate_v1 import validate_closed69_metadata,validate_same_optimized_protected_inventory
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_bytes())

def exact_recovery_source_adam_change(before_text,after_text,old_Adam,new_Adam):
    import ast,copy
    before=ast.parse(before_text);after=ast.parse(after_text)
    expected=ast.parse(str(old_Adam)+'+20*updates',mode='eval').body
    target=ast.parse(str(new_Adam)+'+20*updates',mode='eval').body
    matches=[]
    class Replace(ast.NodeTransformer):
        def visit_Assert(self,node):
            if (isinstance(node.test,ast.Compare) and isinstance(node.test.left,ast.Name)
                and node.test.left.id=='steps' and len(node.test.ops)==1 and isinstance(node.test.ops[0],ast.Eq)
                and len(node.test.comparators)==1 and isinstance(node.test.comparators[0],ast.Set)
                and len(node.test.comparators[0].elts)==1
                and ast.dump(node.test.comparators[0].elts[0])==ast.dump(expected)):
                matches.append(node.lineno);node.test.comparators[0].elts[0]=copy.deepcopy(target)
            return self.generic_visit(node)
    changed=Replace().visit(before)
    assert len(matches)==1 and ast.dump(changed)==ast.dump(after),'Only exact saved-Adam assertion literal may change'
    return dict(passed=True,old_source_Adam=old_Adam,new_source_Adam=new_Adam,changed_assert_lines=matches,all_other_AST_exact=True)

def load(spec,B):
    import psutil
    B=Path(B);key=spec['key'];assert key in ('h1','recovery')
    auth=read(B/'SAME_OPTIMIZED_CONTINUATION_SOURCE_AUTH_ACTUAL.json')
    assert auth['approved'] and auth['kind']=='actual_closed69_to_same_optimized_source70'
    assert auth['source69_complete_SHA']==spec['source_SHA']
    role='closed_production_continuation_CPU_v2.py' if key=='h1' else 'original_account_policy50_source_CPU.py'
    assert H(B/role)==auth['new_guard_SHA']
    assert H(B/'same_optimized_source_contract_metadata_candidate_v1.py')==auth['metadata_contract_SHA']
    proof=read(B/('CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json' if key=='h1' else 'CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json'))
    source_start={'h1':790480,'recovery':837420}[key]
    qualified=validate_closed69_metadata(proof,key,source_start)
    assert qualified['source_SHA']==spec['source_SHA'] and qualified['source_Adam']==spec['source_Adamstep']
    old=Path(spec['previous_runtime_root']);exit=read(old/'NODE_EXIT_ACTUAL.json');terminal=read(old/'NODE_TERMINAL_ACTUAL.json')['row']
    assert exit['actual_all_own_children_waited'] and exit['validation_fcntl_released_if_acquired']
    assert terminal['terminal_all_own_children_waited'] and terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors']
    assert terminal['final']['passed'] and terminal['final']['final']['SHA']==spec['source_SHA']
    assert not any(p.pid!=os.getpid() and any(a.startswith(str(old)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
    prior=read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json');current=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    validate_same_optimized_protected_inventory(prior,current)
    before={x['relative']:x for x in prior['files']};after={x['relative']:x for x in current['files']}
    for rel,row in before.items():
        if rel.endswith('.py') and rel!=role and not (key=='recovery' and rel=='recovery_worker.py'):
            assert rel in after and after[rel]['bytes']==row['bytes'] and after[rel]['SHA']==row['SHA'],rel
    if key=='recovery':
        exact_recovery_source_adam_change((old/'recovery_worker.py').read_text('utf8'),(B/'recovery_worker.py').read_text('utf8'),837420,spec['source_Adamstep'])
    new_python={r for r in after if r.endswith('.py') and r not in before}
    assert new_python=={'same_optimized_source_contract_metadata_candidate_v1.py'}
    for rel in ('H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json','H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json','H1_REWARD_CHANGE_AUTH_AND_SOURCE_CPU_ACTUAL.json','SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json') if key=='h1' else ('SAMPLING_OPTIMIZATION_HUMAN_AUTH_AND_CPU_ACTUAL.json',):
        assert H(B/rel)==H(old/rel)
    cpu=read(B/('TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json' if key=='h1' else 'TARGET_TWO50_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json'))
    assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA'] and cpu['all17Adam']==spec['source_Adamstep']
    assert cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json') and cpu['sampling_acceleration_CPU']['passed']
    if key=='h1':
        assert cpu['boundary_repair_integration_CPU']['passed'] and cpu['new_reward_integration_CPU']['passed']
        assert spec['policy_hz']==spec['source_policy_hz']==100 and not spec.get('reward_migration')
        kind='closed_same_backend_production'
    else:
        assert spec['policy_hz']==spec['source_policy_hz']==50 and cpu['source_schema_counts']==[173,96]
        clock=read(old/'job0/production/E3_POLICY50_CLOCK_ACTUAL.json')
        assert clock['policy_hz']==50 and clock['physics_dt_s']==.0025 and clock['decimation']==8
        assert cpu['sampling_acceleration_CPU']['fresh_bank_physical_read_count']==1
        kind='closed_same_backend_policy50_production'
    v=dict(kind=kind,key=key,passed=True,source_SHA=spec['source_SHA'],GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],
           all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,same_active_runtime_assets_and_PPO_AST=True,
           source_original_cost_settled=True,explicit_policy_clock_50Hz_admitted=key=='recovery',same_clock_closed_production=True,
           source_cost_original_account_ready=True,source_account_reconciliation_receipt_SHA=H(B/('CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json' if key=='h1' else 'CURRENT_ORIGINAL_COHORT_CLOSED_COST_CPU_ACTUAL.json')),
           original_clip6_query_COM_closure_mimic_hardware_savedstop_guards_retained=True,not_skill_graduation=True)
    return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
