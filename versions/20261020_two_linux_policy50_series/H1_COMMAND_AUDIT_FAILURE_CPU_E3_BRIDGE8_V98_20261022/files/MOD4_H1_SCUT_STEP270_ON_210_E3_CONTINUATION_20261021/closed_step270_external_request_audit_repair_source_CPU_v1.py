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
    repair=read(B/'H1_EXTERNAL_REQUEST_AUDIT_REPAIR_CPU_ACTUAL.json');failure=read(B/'H1_PREVIOUS_FAILED_PAIR_ORIGINAL_COST_EVIDENCE.json')
    assert repair['passed'] and repair['candidate']['normalized_rest_AST_exact'] and failure['H1_production_failed_no_FINAL'] and failure['original_canonical_cost_settled']
    path='h1_step270_sdk_runtime_candidate.py';current={x['relative']:x for x in m['files']}
    assert prior[path]['SHA']==repair['candidate']['old_runtime_SHA'] and current[path]['SHA']==repair['candidate']['candidate_runtime_SHA'] and H(B/path)==current[path]['SHA']
    normalized=ast.parse((B/path).read_text('utf8'));normalized.body=[x for x in normalized.body if not isinstance(x,ast.FunctionDef) or x.name!='audit_step270_external_request']
    cls=next(x for x in normalized.body if isinstance(x,ast.ClassDef) and x.name=='H1Step270Env');init=next(x for x in cls.body if isinstance(x,ast.FunctionDef) and x.name=='__init__');assert isinstance(init.body[-2],ast.Import) and isinstance(init.body[-1],ast.Assign);init.body=init.body[:-2]
    assert H(old/path)==prior[path]['SHA'] and ast.dump(normalized,include_attributes=False)==ast.dump(ast.parse((old/path).read_text('utf8')),include_attributes=False)
    for row in m['files']:
        rel=row['relative']
        if rel.endswith('.py') and rel in prior and rel not in (path,'closed_production_continuation_CPU_v2.py'):
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
