from pathlib import Path
import ast,hashlib,json,time
T=Path(__file__).resolve().parent;R=T/'reports'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(n,v):
    with (R/n).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)
proof=json.loads((R/'STEP270_PRODUCTION_WHOLE_SOURCE_AND_RSL_CPU_ACTUAL.json').read_bytes())
assert proof['passed_independent_whole_production_source_and_RSL_CPU']
target=(T/'target_H1_step270_source_sdk_cpu_review_v1.py').read_text()
old="from h1_step270_fullstate_checkpoint_candidate_uninstalled import validate_source\nvalidate_source(s, 20000)"
new="""from h1_step270_fullstate_checkpoint_candidate_uninstalled import validate_new_phase, RETAINED_GROUPS
assert all(k in s for k in RETAINED_GROUPS) and 'H1_step270_task_state' in s
phase=s['H1_step270_task_state'];assert phase['version']==270
validate_new_phase(phase['phase'],20000)
assert s['H1_step270_runtime_contract']['original_D0_D7_STD_optimizer_save_chain_retained']
def finite(x):
    if torch.is_tensor(x):assert not x.is_floating_point() or torch.isfinite(x).all()
    elif isinstance(x,dict):
        for value in x.values():finite(value)
    elif isinstance(x,(list,tuple)):
        for value in x:finite(value)
finite(s)"""
assert target.count(old)==1;target=target.replace(old,new)
p=T/'target_H1_step270_closed_source_sdk_cpu_review_v1.py';p.open('x',encoding='utf8',newline='\n').write(target)
for p in (T/'closed_step270_same_phase_production_source_CPU_v1.py',p):ast.parse(p.read_text('utf8'))
errors=sorted(R.glob('STEP270_PRODUCTION_WHOLE_SOURCE_CPU_ORIGINAL_ERROR_*.json'))
sources=[T/('review_step270_production_whole_source_and_RSL_CPU'+v+'_once.py') for v in ('','_V2','_V3')]
put('STEP270_PRODUCTION_CPU_READER_REPAIRS_AND_SAMEPHASE_SUPPORT_ACTUAL.json',dict(
    epoch=time.time(),whole_production_source_and_RSL_CPU_passed=True,
    original_reader_errors=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in errors],
    reader_sources=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in sources],
    V1_reader_error='Substring replacement of 673900 corrupted the keyword all17Adam673900; source worker was not erroneous.',
    V2_reader_error='Reader expected E3-only 7000MiB spawn AST verbatim; actual H1 branch correctly retains original 15669MiB threshold.',
    V3_repair='Normalize only documented dynamic Adam and the original H1 memory branch; original load/learn/log/save/stop and charge/account/auth AST verified.',
    unused_loader_V1_error='Historical own-GPU receipt uses own list of nvidia CSV rows, not direct GPU_UUID field. Corrected unused loader V2 before any remote installation; original source and manifest preserved.',
    source_H1_actual_saved_optimizer_LR=proof['original_RSL_PPO_CPU_fixture']['source_optimizer_saved_LR'],
    source_initial_config_LR=.0001,adaptive_LR_and_optimizer_inheritance_not_reset=True,
    synthetic_CPU_fixture_not_training_source_or_actual_H1_GO=True,
    future_samephase_loader_and_target_CPU_source_AST_only=[
        dict(path=str(T/n),bytes=(T/n).stat().st_size,SHA=H(T/n)) for n in
        ('closed_step270_same_phase_production_source_CPU_v1.py','target_H1_step270_closed_source_sdk_cpu_review_v1.py')],
    future_not_model_prepared_or_installed_or_admitted=True,
    future_must_require_actual_current_pair_complete_models_CPU_original_cost_allout=True,
    future_new_H1_source_Adam_dynamic_no_native_or_query_replay=True))
print(json.dumps(dict(reader_errors_preserved=len(errors),whole_CPU_passed=True,future_support_source_only=True)))
