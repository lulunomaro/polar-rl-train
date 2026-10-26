"""Append concrete observer/reviewer source only; no generated template execution."""
from pathlib import Path
import ast
import difflib
import hashlib
import json
import time

HERE = Path(__file__).resolve().parent
T = HERE.parent.parent
NORMAL = T / 'H1_STEP270_THREE_EXPERTS_RESOURCE_V83B_20261026'
NATIVE = T / 'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026'


def write_new(name, text, prior):
    ast.parse(text)
    with (HERE / name).open('x', encoding='utf8') as stream:
        stream.write(text)
    with (HERE / 'diffs' / (name + '.diff')).open('x', encoding='utf8') as stream:
        stream.write(''.join(difflib.unified_diff(prior.splitlines(True), text.splitlines(True),
                                                fromfile='READ_ONLY_REFERENCE', tofile=name)))


observer_path = NATIVE / 'collect_actual82q_PPO_and_native_H1_policy_first_finite_unused_once.py'
old = observer_path.read_text('utf8')
new = old.replace('H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V82Q_20261026', 'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026')
new = new.replace('MIXED82Q_ACTUAL_GO_PPO_AND_NATIVE_POLICY_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json',
                  'MIXED84_ACTUAL_GO_BASELINES_AND_NATIVE_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
new = new.replace("dict(root=q['roots'][key],row=a['current']['rows'][key],run_id=q['run_id'],", "dict(root=q['roots'][key],row=a['current']['rows'][key],spec=q['specs'][key],run_id=q['run_id'],")
needle = "go=json.loads((B/'job0/GO_PRODUCTION.json').read_bytes());"
extra = """if v['key']=='e2':
 source=v['row']['closed_source_CPU']['value'];spec=v['spec'];assert source['reference_and_adapter_actual_CPU_validated'] and source['reference_artifact_SHA']==spec['reference_artifact_SHA'] and source['objective_contract_SHA']==spec['objective_contract_SHA']
 objective=B/'job0/production'/spec['objective_contract_runtime_basename'];raw=objective.read_bytes();assert __import__('hashlib').sha256(raw).hexdigest()==spec['objective_contract_SHA'],'Actual installed partial-mask objective contract required'
 assert source['source_closed83B_healthy_three_original_cost_allout_passed'] and source['not_production_E2_source_or_skill_qualification']
"""
assert new.count(needle) == 1
new = new.replace(needle, extra + needle, 1)
write_new('observe_mixed84_baselines_native_first_finite_TEMPLATE.py', new, old)
with (HERE / 'source_snapshots/82Q_first_observer.py').open('x', encoding='utf8') as stream:
    stream.write(old)

reviewer_path = NORMAL / 'review_three83B_normal_complete_models_original_cost_CPU_unused_once.py'
old = reviewer_path.read_text('utf8')
new = old.replace("receipt=read(R/'THREE_EXPERT_COMPLETE_FINALS_AND_ORIGINAL_COST_RETURNED_ACTUAL.json')", "receipt=read(R/'MIXED84_BASELINES_NATIVE_H1_AND_ORIGINAL_COST_RETURNED_ACTUAL.json')")
new = new.replace("for key in ('h1','e2','recovery'):", "for key in ('h1','recovery'):", 1)
native_function = '''
def review_new_native_method(receipt,q,co,segment):
    import hashlib,importlib.util
    rows=receipt['native_H1_method_fullstate'];terminal=co['rows']['e2'];cost=segment['experts']['e2']
    base=dict(present=False,original_terminal=terminal,actual_cost=cost,not_production_H1_or_E2_source=True,not_frozen_skill_graduation=True)
    assert cost['duration_bound_passed'] and 0<cost['charged_seconds']<=3900
    if not rows:
        assert not (terminal.get('final') or {}).get('passed'),'Passed terminal checkpoint was not collected; preserve collection failure'
        return dict(base,no_qualified_native_model=True,rc0_is_not_success=True)
    assert len(rows)==1 and terminal['returncode']==0 and not terminal['original_error'] and not terminal['errors']
    final=rows[0];commit=terminal['final'];assert commit['passed'] and commit['trace_persisted'] and final['twohost_complete_SHA'] and final['SHA']==commit['final']['SHA']
    spec=q['specs']['e2'];s=torch.load(final['local_path'],map_location='cpu',weights_only=False)
    bootstrap=Path(q['payloads']['e2'])/'job0/source'/spec['source_filename'];old=torch.load(bootstrap,map_location='cpu',weights_only=False)
    expected=s['UniSuperMimic_publication'];producer=expected['producer'];pins=spec['candidate_pins']
    assert producer['bridge_source_SHA']==pins['bridge_source_SHA'] and producer['finalization_source_SHA']==pins['finalization_source_SHA']
    assert producer['bootstrap_task_source_SHA']==spec['source_SHA'] and producer['reference_artifact_SHA']==spec['reference_artifact_SHA']
    assert producer['adapter_CPU_report_SHA']==spec['adapter_CPU_report_SHA'] and producer['objective_contract_SHA']==spec['objective_contract_SHA']
    for name in ('run_token','save_token'):assert expected[name]==commit['final'][name]
    module_path=Path(q['payloads']['e2'])/'source/native_finalization_v1.py'
    assert hashlib.sha256(module_path.read_bytes()).hexdigest()==pins['finalization_source_SHA']
    module_spec=importlib.util.spec_from_file_location('new_native_finalization_verified_source',module_path);module=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(module)
    module.verify_native(s,expected)
    def exact(a,b):
        if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
        if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(exact(a[k],b[k]) for k in a)
        if isinstance(a,(tuple,list)):return type(a)==type(b) and len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
        return type(a)==type(b) and a==b
    for name in ('actor_state_dict','critic_state_dict','optimizer_state_dict'):assert exact(s[name],old[name]),'Frozen83B PPO bootstrap changed: '+name
    assert {int(v['step']) for v in s['optimizer_state_dict']['state'].values()}=={829700}
    native=s['UniSuperMimic_H1_test'];assert native['iteration']==commit['final']['updates']>0
    assert commit['final']['world_updates']>0 and commit['final']['policy_updates']>0
    assert all(name in native for name in ('wm','pi','critic','opt_wm','opt_pi','opt_v'))
    return dict(base,present=True,final=final,producer=producer,bootstrap_frozen_Adam829700=True,world_updates=commit['final']['world_updates'],policy_updates=commit['final']['policy_updates'],native_fullstate_CPU_verified=True)

'''
assert new.count('def main():') == 1
new = new.replace('def main():', native_function + 'def main():', 1)
needle = "    result=dict(epoch=time.time(),passed=True,models=models,all_owner_nodes_children_actual_out=True,"
assert new.count(needle) == 1
replacement = "    native=review_new_native_method(receipt,q,co,segment)\n    assert set(models)=={'h1','recovery'}\n    result=dict(epoch=time.time(),passed=True,qualification_scope='normal83B_H1_E3_baselines_and_separate_Fudan_native_H1_method',models=models,native_method=native,normal_E2_83B_preserved_paused=dict(SHA='72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f',Adam=857460),all_owner_nodes_children_actual_out=True,"
new = new.replace(needle, replacement, 1)
new = new.replace("R/'THREE_EXPERT_COMPLETE_MODELS_AND_ORIGINAL_COST_CPU_ACTUAL.json'", "R/'MIXED84_BASELINES_NATIVE_METHOD_AND_ORIGINAL_COST_CPU_ACTUAL.json'")
write_new('review_mixed84_baselines_native_fullstate_CPU_TEMPLATE.py', new, old)
with (HERE / 'source_snapshots/83B_reviewer.py').open('x', encoding='utf8') as stream:
    stream.write(old)

# Keep the owner copy of the pure protocol at this exact reviewed source revision.
owner_protocol=HERE/'owner_controller_templates/mixed84_protocol_v1.py'
with (HERE/'source_snapshots/owner_protocol_initial_generated.py').open('xb') as stream:
    stream.write(owner_protocol.read_bytes())
owner_protocol.write_bytes((HERE/'mixed84_protocol_v1.py').read_bytes())
with (HERE/'reports/CONCRETE_OBSERVER_REVIEWER_SOURCE_EXTENSION_ACTUAL.json').open('x',encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(),source_only=True,observer=str(observer_path),reviewer=str(reviewer_path),
                   native_publication_verified_separately_from_baselines=True,
                   no_template_execution_or_model_copy_or_TASK_GO=True,
                   source_hardening_notes=['Explicit objective-contract digest admission',
                       'Use strengthened86412 helper template rather than original80 helper',
                       'Upload pure native gate dependency to owner; baseline common source unchanged'],
                   reader_tool_error_preserved='An rg invocation incorrectly used PowerShell -LiteralPath; it returned unrecognized file type, then the source search was corrected.',
                   Git_status='PENDING_ROOT_PHASE_ARCHIVE'),stream,indent=2)
print(json.dumps(dict(concrete_observer_and_reviewer_written=True,no_template_executed=True)))
