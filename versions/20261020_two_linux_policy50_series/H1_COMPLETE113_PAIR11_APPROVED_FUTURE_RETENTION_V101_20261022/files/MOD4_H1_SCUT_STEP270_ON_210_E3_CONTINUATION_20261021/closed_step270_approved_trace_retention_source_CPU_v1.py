"""Reserved for a future actually closed step270 source; not current admission."""
from pathlib import Path
import ast,hashlib,json,os,psutil
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(spec,B):
    read=lambda p:json.loads(Path(p).read_bytes())
    m=read(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    proof=read(B/'CURRENT_ORIGINAL_PAIR_CLOSED_MODELS_COST_CPU_ACTUAL.json')
    assert spec['key']==m['key']=='h1' and spec['policy_hz']==spec['source_policy_hz']==100
    assert proof['passed'] and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled']
    model=proof['models']['h1'];assert model['final']['SHA']==spec['source_SHA']==m['source_SHA']
    assert model['Adam']==spec['source_Adamstep']==m['source_Adamstep']
    old=Path(spec['previous_runtime_root'])
    e=read(old/'NODE_EXIT_ACTUAL.json');r=read(old/'NODE_TERMINAL_ACTUAL.json')['row']
    assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired']
    assert r['terminal_all_own_children_waited'] and r['returncode']==0 and r['final']['passed'] and not r['errors']
    assert r['final']['final']['SHA']==spec['source_SHA']
    assert not any(p.pid!=os.getpid() and any(a.startswith(str(old)+'/') for a in p.info['cmdline'] or [])
                   for p in psutil.process_iter(['pid','cmdline']))
    prior={x['relative']:x for x in read(B/'QUALIFIED_RUNTIME_BASE_MANIFEST.json')['files']}
    for row in m['files']:
        if row['relative'].startswith(('job0/runtime/','job0/assets/','lib/')):
            assert row['SHA']==prior[row['relative']]['SHA'] and row['bytes']==prior[row['relative']]['bytes']
    approved=read(B/'H1_TRACE_RETENTION_HUMAN_APPROVAL_ACTUAL.json');retention=read(B/'H1_TRACE_RETENTION_CANDIDATE_CPU_ACTUAL.json')
    assert approved['approved'] and approved['approval_scope']=='future_new_root_first1_latest2_prefix_pairs_plus_current_failure_v1'
    assert retention['passed'] and retention['original_trace_AST_exact_except_two_append_nodes']
    assert approved['candidate_trace_SHA']==retention['candidate_trace']['SHA'] and approved['candidate_adapter_SHA']==retention['candidate_adapter']['SHA']
    current={x['relative']:x for x in m['files']};trace='h1_production_control_prefix_trace_v1.py';adapter='h1_prefix_pair_retention_v1.py'
    assert H(B/trace)==current[trace]['SHA']==retention['candidate_trace']['SHA']
    assert H(B/adapter)==current[adapter]['SHA']==retention['candidate_adapter']['SHA']
    assert H(old/trace)==prior[trace]['SHA']
    if prior[trace]['SHA']==retention['original_trace']['SHA']:
        tree=ast.parse((B/trace).read_text('utf8'));assert isinstance(tree.body[-2],ast.ImportFrom) and tree.body[-2].module=='h1_prefix_pair_retention_v1'
        assert isinstance(tree.body[-1],ast.Assign) and ast.unparse(tree.body[-1])=='H1ControlPrefixTrace.persist = wrap_trace_persist(H1ControlPrefixTrace.persist)'
        assert ast.dump(ast.Module(body=tree.body[:-2],type_ignores=[]),include_attributes=False)==ast.dump(ast.parse((old/trace).read_text('utf8')),include_attributes=False)
    else:
        assert prior[trace]['SHA']==retention['candidate_trace']['SHA'] and prior[adapter]['SHA']==retention['candidate_adapter']['SHA'] and H(old/adapter)==prior[adapter]['SHA']
    for row in m['files']:
        rel=row['relative']
        if rel.endswith('.py') and rel in prior and rel not in (trace,'closed_production_continuation_CPU_v2.py'):
            assert row['SHA']==prior[rel]['SHA'] and row['bytes']==prior[rel]['bytes']
    cpu=read(B/'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json')
    assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA']
    assert cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    v=dict(kind='closed_same_backend_production',key='h1',passed=True,source_SHA=spec['source_SHA'],
           GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],
           all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,
           same_active_runtime_assets_and_PPO_AST=True,new_step270_phase_fullstate_same_task_continuation=True,
           source_original_cost_settled=True,no_native_or_query_replay=True,not_skill_graduation=True)
    return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
