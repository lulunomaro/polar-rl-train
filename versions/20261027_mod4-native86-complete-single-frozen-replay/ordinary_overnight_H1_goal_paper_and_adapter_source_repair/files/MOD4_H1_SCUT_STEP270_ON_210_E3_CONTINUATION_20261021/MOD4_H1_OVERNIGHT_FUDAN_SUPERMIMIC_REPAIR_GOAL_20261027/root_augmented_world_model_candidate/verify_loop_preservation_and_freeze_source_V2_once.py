from pathlib import Path
import ast,hashlib,json,traceback
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
T=ROOT.parent
OLD=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/e2/source/supermimic_vendor_v2'
NEW=HERE/'v3/supermimic_wheel_leg_v3'
REPORT=ROOT/'reports/NEW_VENDOR_ACTUAL_LEARNING_LOOP_AST_PRESERVATION_CPU_V2_ACTUAL.json'
assert not REPORT.exists()
def methods(path,cls):
    tree=ast.parse(path.read_text('utf8'))
    node=next(x for x in tree.body if isinstance(x,ast.ClassDef) and x.name==cls)
    return {x.name:x for x in node.body if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef))}
def dump(node):return ast.dump(node,include_attributes=False)
checks=[]
try:
    old=methods(OLD/'learner.py','SuperMimicLearner');new=methods(NEW/'learner.py','SuperMimicLearner')
    changed=[]
    for name in old:
        if dump(old[name])!=dump(new[name]):changed.append(name)
    expected=['__init__','_make_world_model','_wm_rollout','policy_update']
    assert sorted(changed)==sorted(expected),changed
    for name in ['train','collect','wm_update','_imag_step','_reward_term','_critic_input','_make_policy','save','load']:
        assert dump(old[name])==dump(new[name]),name
        checks.append('exact original '+name+' AST retained')
    # A seven-component state is the sole policy_update semantic edit.
    patched=ast.parse(ast.unparse(old['policy_update']))
    ranges=[n for n in ast.walk(patched) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='range' and len(n.args)==1 and isinstance(n.args[0],ast.Constant) and n.args[0].value==6]
    assert len(ranges)==2
    for r in ranges: r.args[0].value=7
    assert dump(patched.body[0])==dump(new['policy_update'])
    checks.append('policy BPTT/value code differs only both state component ranges6->7')
    ro=methods(OLD/'replay.py','ReplayBuffer');rn=methods(NEW/'replay.py','ReplayBuffer')
    for name in ['add','_row','sample_windows','sample_starts']:
        assert dump(ro[name])==dump(rn[name]),name
        checks.append('exact original replay '+name+' AST retained')
    result={'passed':True,'checks':checks,'changed_learner_methods':changed,'not_runtime_admission':True,'no_PT_GPGU_physics_or_actor':True,'root_models_CPU_report':'AUGMENTED_WHEEL_LEG_WORLD_MODEL_AND_VENDOR_CPU_ACTUAL.json','legacy_build_failure':'WHEEL_LEG_V3_ISOLATED_VENDOR_BUILD_SOURCE_ACTUAL.json','CRLF_fix':'V1 failed literal source matching before runtime; V2 normalizes ONLY newly derived Python candidate source. Qualified source and2536-byte metadata helper never touched.','reference_binding_path_reader_error':'Initial new read-only command incorrectly looked under payloads/e2/source. Actual binding is at payloads/e2; original error preserved in conversation and this report; corrected read only reference JSON, no model/raw.'}
except BaseException:
    result={'passed':False,'checks_before_failure':checks,'error':traceback.format_exc(),'partial_unchanged':True}
    REPORT.write_text(json.dumps(result,indent=2),'utf8');raise
REPORT.write_text(json.dumps(result,indent=2),'utf8')
index={'schema':'source_only_augmented_worldmodel_frozen_v1','runtime_SDK_passed':False,'all_files_except_index':[{'path':str(p.relative_to(HERE)),'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(HERE.rglob('*')) if p.is_file()],'related_reports':[{'path':str(p),'bytes':p.stat().st_size,'SHA':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted((ROOT/'reports').glob('*WORLD_MODEL*')) if p.is_file()]}
(HERE/'FROZEN_ROOT_AUGMENTED_MODEL_SOURCE_V3_INDEX.json').write_text(json.dumps(index,indent=2),'utf8')
print(json.dumps({'passed':True,'checks':len(checks),'frozen_files':len(index['all_files_except_index'])}))


