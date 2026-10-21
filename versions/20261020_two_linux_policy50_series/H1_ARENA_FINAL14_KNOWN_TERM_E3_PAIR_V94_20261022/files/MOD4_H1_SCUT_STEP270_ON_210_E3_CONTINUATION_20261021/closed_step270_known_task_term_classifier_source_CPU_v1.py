"""Reserved for a future actually closed step270 source; not current admission."""
from pathlib import Path
import hashlib,json,os,psutil
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
    repair=read(B/'H1_KNOWN_ORDINARY_TASK_TERM_CLASSIFIER_CPU_ACTUAL.json')
    source=read(B/'H1_KNOWN_TASK_TERM_SOURCE_STOP_ACTUAL.json')
    assert repair['passed_known_task_term_CPU_classification'] and repair['normalized_rest_AST_exact'] and repair['all_other_unknown_mimic_nonfinite_callback_guards_unchanged']
    assert source['only_original_unknown_is_known_arena_exit'] and not source['original_health_relabelled_pass']
    for row in m['files']:
        if row['relative'].startswith(('job0/runtime/','job0/assets/','lib/')):
            if row['relative']==repair['relative']:
                assert row['SHA']==repair['candidate']['SHA'] and prior[row['relative']]['SHA']==repair['original']['SHA']
            else:
                assert row['SHA']==prior[row['relative']]['SHA'] and row['bytes']==prior[row['relative']]['bytes']
    cpu=read(B/'TARGET_H1_STEP270_SOURCE_AND_CONTROLLERS_INSTALLED_CPU_ADMITTED_ACTUAL.json')
    assert cpu['passed_CPU_only'] and cpu['source_SHA']==spec['source_SHA']
    assert cpu['all17Adam']==spec['source_Adamstep'] and cpu['manifest_SHA']==H(B/'THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    v=dict(kind='closed_same_backend_production',key='h1',passed=True,source_SHA=spec['source_SHA'],
           GPU_UUID=spec['GPU_UUID'],execution_backend=spec['execution_backend'],
           all_source_model_runtime_finite_CPU=True,old_complete_production_checkpoint_actual_EXIT0=True,
           same_active_runtime_assets_and_PPO_AST=True,new_step270_phase_fullstate_same_task_continuation=True,
           source_original_cost_settled=True,no_native_or_query_replay=True,not_skill_graduation=True)
    return dict(value=v,SHA=hashlib.sha256(json.dumps(v,indent=2).encode()).hexdigest(),actual_CPU_waited_EXIT0=True)
