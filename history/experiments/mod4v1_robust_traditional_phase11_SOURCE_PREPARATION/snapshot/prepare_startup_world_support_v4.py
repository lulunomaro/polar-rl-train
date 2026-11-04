"""Prepare exactly one new V4 nominal front TRAIN; metadata/AST only, no robot imports."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;V=R/'STARTUP_STAND_V4';D=V/'front_admission001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
proof=V/'preflight001/RESULT.json';p=json.loads(proof.read_bytes());rc=json.loads((V/'RECEIPT.json').read_bytes())
assert p['status']=='PASS_FRESH_SYNTHETIC_NO_PHYSICAL_SKILL_CLAIM' and p['counts']==rc['counts']
assert p['counts']['enabled_commands']==551 and p['counts']['disabled_and_oracle_commands']==40 and p['counts']['typed_cases']==16
assert p['source_before']==p['source_after'] and p['model_compile_FK_integrator_DR_oldQA_ARM_Git_calls']==0
assert sha(proof)==rc['proof_SHA']
entry=R/'run_startup_stand_case_v6.py';core=V/'controller.py'
assert sha(entry)==rc['entry_SHA']=='c43ab1e83f7b6ef861591f75401e96dd804ddd358586544ddd420f41bb915386'
assert sha(core)==rc['core_SHA']=='9dec4f858524aad034fb287ac31f864299d86a00bd6aaad4f38f04e5063a2bd4'
def parts(path):
    tree=ast.parse(path.read_text(encoding='utf-8'))
    loop=next(x for x in ast.walk(tree) if isinstance(x,ast.For) and isinstance(x.target,ast.Name) and x.target.id=='k')
    assigns={n.targets[0].id:ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('target','healthy','good','complete','passed')}
    return ast.dump(loop,include_attributes=False),assigns
assert parts(R/'run_startup_stand_case_v5.py')==parts(entry)
old=json.loads((R/'STARTUP_STAND_V1/front_admission001/CONFIG.json').read_bytes());cfg=dict(old)
cfg.update(case_id='startup_front065_world_support_v4_nominal1',kind='NEW_STARTUP_WORLD_SUPPORT_CAPTURE_RETURN_FRONT_NOMINAL_V4',
    controller=dict(operator_enable=True,recovery_tracking_enable=True,alignment_wheel_enable=False,support_geometry_enable=True))
a=dict(cfg);b=dict(old)
for x in(a,b):
    x.pop('case_id');x.pop('kind');x['controller']=dict(x['controller'])
    for key in ('recovery_tracking_enable','alignment_wheel_enable','support_geometry_enable'):x['controller'].pop(key,None)
assert a==b
assert not (R/'results'/cfg['case_id']).exists() and not (R/'batches'/cfg['case_id']).exists()
D.mkdir(exist_ok=False);dump(D/'CONFIG.json',cfg)
idx=json.loads((R/'STARTUP_STAND_V3/front_A_admission001/SOURCE_PREEXEC.json').read_bytes());paths={Path(x['path']).resolve() for x in idx['files']}
paths.update([Path(__file__).resolve(),R/'launch_startup_world_support_v4.py',R/'prepare_startup_v4_entry_v6.py',entry,core,proof,
    *[V/s for s in ('METHOD.md','REPORT.md','RECEIPT.json','ENTRY_DERIVATION.json','preflight_once.py','preflight001/SOURCE_PREEXEC.json')],
    R/'STARTUP_SUPPORT_GEOMETRY_V1/REPORT.md',R/'STARTUP_SUPPORT_GEOMETRY_V1/RECEIPT.json'])
roots=[R.resolve(),(R.parent/'traditional_control_20261101').resolve()];records=[]
for f in sorted(paths):
    assert any(f.is_relative_to(root) for root in roots) and f.stat().st_size<2*1024*1024,str(f)
    records.append(dict(path=str(f),bytes=f.stat().st_size,SHA=sha(f)))
dump(D/'SOURCE_PREEXEC.json',dict(files=records,allowed_readonly_source_roots=[str(x) for x in roots],
    original_runtime_robot_asset_guard_retained=True,no_model_assets_or_raw_opened_here=True))
dump(D/'PROTOCOL.json',dict(kind='STARTUP_V4_WORLD_SUPPORT_CAPTURE_RETURN_FRONT065_ONE_NOMINAL_TRAIN',runner=entry.name,config=cfg,max_workers=1,
    maximum_controls=1000,maximum_physics_steps=20000,old_failed_cases_not_replayed=True,new_strategy_not_reporting_repair=True,
    full_for_loop_target_health_good_complete_passed_AST_equal=True,private_grade_gates_model_driver_observer_switch_policy_unchanged=True,
    one_passive_fixture_initialization_no_upright_prior_reset_or_assist=True,nominal_only_not_fullDR_or_holdout=True,
    no_automatic_DR_back_side_second_variant_or_retry=True,profile_B_not_admitted=True,
    actual_independent_source_config_launcher_review_required=True,synthetic_fake_ground_not_physical_permission=True))
dump(D/'PREPARATION_RECEIPT.json',dict(status='PREPARED_V4_NEW_NOMINAL_NOT_EXECUTED',config_SHA=sha(D/'CONFIG.json'),protocol_SHA=sha(D/'PROTOCOL.json'),
    source_index_SHA=sha(D/'SOURCE_PREEXEC.json'),runner_SHA=sha(entry),candidate_SHA=sha(core),saved_proof_SHA=sha(proof),files_pinned=len(records),
    original_loop_and_private_gate_AST_equal=True,actual_model_FK_PHY_oldQA_Git_calls=0))
print(json.dumps(json.loads((D/'PREPARATION_RECEIPT.json').read_bytes()),indent=2))
