"""Prepare one new V5 TRAIN only after parent actually accepts new synthetic evidence. No robot imports."""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;V=R/'STARTUP_STAND_V5';D=V/'front_admission001';OLD=R/'STARTUP_STAND_V4/front_admission002'
def get(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def parts(p):
    t=ast.parse(p.read_text(encoding='utf-8'));loops=[x for x in ast.walk(t)if isinstance(x,ast.For)and isinstance(x.target,ast.Name)and x.target.id=='k'];assert len(loops)==1
    assignments={k:[ast.dump(x,include_attributes=False)for x in ast.walk(t)if isinstance(x,ast.Assign)and any(isinstance(v,ast.Name)and v.id==k for v in x.targets)]for k in('target','healthy','good','complete','passed')}
    assert all(len(v)==1 for v in assignments.values())
    return ast.dump(loops[0],include_attributes=False),assignments
assert not D.exists()
acceptance=V/'PARENT_MATH_PROOF_ACCEPTANCE.json';accepted=get(acceptance)
assert accepted['approved_synthetic_only'] is True and accepted['physical_skill_qualified'] is False
counts=accepted['counts'];assert 0<counts['enabled_including_oracles']<=320 and 0<counts['disabled_including_oracles']<=40 and 0<counts['typed_cases']<=16
assert accepted['new_feature_branch_fired_in_synthetic'] is True and accepted['proof_failures']==0
entry=R/'run_startup_stand_case_v7.py';core=V/'controller.py';proof=V/'preflight001/RESULT.json'
assert sha(core)==accepted['core_SHA']=='209c0385d1501021b05822f0222228ae78b012570f73fb526a435e8c02b2045a'
assert sha(entry)==accepted['entry_SHA']=='b96f10a45b79527e63a5afdc126579b480ce87931aeb8de57d2805e0a8b48367'
assert sha(proof)==accepted['proof_SHA']
assert parts(R/'run_startup_stand_case_v6.py')==parts(entry)
text=entry.read_text(encoding='utf-8');assert 'dr.queue_receipt()'in text and 'runtime_receipt'not in text
assert "load_gain(ROOT/'TALL_ROUGH_BANK_V1/gain_delta20.json')"in text and "file_record(ROOT/'TALL_ROUGH_BANK_V1/gain_delta20.json')"in text
old=get(OLD/'CONFIG.json');cfg=dict(old);cfg['controller']=dict(old['controller'])
cfg.update(case_id='startup_front065_lift_pose_v5_nominal1',kind='NEW_STARTUP_LIFT_POSE_TIMING_ONLY_FRONT_NOMINAL_V5');cfg['controller']['lift_pose_enable']=True
comparison=dict(cfg);comparison['controller']=dict(cfg['controller']);comparison['controller'].pop('lift_pose_enable');comparison['case_id']=old['case_id'];comparison['kind']=old['kind'];assert comparison==old
assert not (R/'results'/cfg['case_id']).exists() and not (R/'batches'/cfg['case_id']).exists()
old_index=get(OLD/'SOURCE_PREEXEC.json');assert len(old_index['files'])==57
records={str(Path(x['path']).resolve()).casefold():dict(x)for x in old_index['files']};assert len(records)==57
roots=[R.resolve(),(R.parent/'traditional_control_20261101').resolve()]
extra=[Path(__file__).resolve(),R/'launch_startup_lift_pose_v5.py',acceptance,entry,core,proof,OLD/'CONFIG.json',OLD/'PROTOCOL.json',OLD/'SOURCE_PREEXEC.json']
extra += [Path(x['path'])for x in accepted['source_artifacts']]
for p in extra:
    p=p.resolve();assert any(p.is_relative_to(root)for root in roots)and p.stat().st_size<2*1024*1024,str(p)
    rec=dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p));key=str(p).casefold()
    if key in records:assert records[key]==rec,str(p)
    else:records[key]=rec
for x in accepted['source_artifacts']:assert sha(Path(x['path']))==x['SHA'] and Path(x['path']).stat().st_size==x['bytes'],x['path']
support=(R/'TALL_ROUGH_BANK_V1/gain_delta20.json').resolve();s=records[str(support).casefold()]
assert s['SHA']==sha(support)=='f97040665db51c4bc1686187f14aa46579d8d6f6eabff6ef2ee69dea5328d099' and s['bytes']==29484
D.mkdir(exist_ok=False);dump(D/'CONFIG.json',cfg)
dump(D/'SOURCE_PREEXEC.json',dict(files=sorted(records.values(),key=lambda x:x['path'].casefold()),allowed_readonly_source_roots=[str(x)for x in roots],
    inherited57_record_identity=True,actual_support_gain20_dependency_inherited_and_rechecked=True,new_input_sources_locked=True,original_runtime_asset_guard_retained=True,
    no_model_assets_or_raw_opened_here=True))
dump(D/'PROTOCOL.json',dict(kind='STARTUP_V5_LIFT_POSE_TIMING_ONLY_FRONT065_ONE_NOMINAL_TRAIN',runner=entry.name,config=cfg,max_workers=1,maximum_controls=1000,maximum_physics_steps=20000,
    same_leg_reference_algorithm_not_identical_closed_loop_leg_trajectory=True,earlier_latch_carryover_part_of_timing_intervention=True,
    old_failed_cases_not_replayed=True,full_for_loop_target_health_good_complete_passed_AST_equal=True,private_grade_model_driver_observer_unchanged=True,
    one_passive_fixture_initialization_no_upright_prior_or_assist=True,nominal_only_not_fullDR_or_holdout=True,no_automatic_DR_back_side_second_variant_or_retry=True,
    profile_B_not_admitted=True,actual_independent_source_config_launcher_review_required=True,synthetic_fake_ground_not_physical_permission=True))
receipt=dict(status='PREPARED_V5_NEW_FRONT_NOMINAL_NOT_EXECUTED',config_SHA=sha(D/'CONFIG.json'),protocol_SHA=sha(D/'PROTOCOL.json'),source_index_SHA=sha(D/'SOURCE_PREEXEC.json'),
    runner_SHA=sha(entry),candidate_SHA=sha(core),saved_proof_SHA=sha(proof),proof_acceptance_SHA=sha(acceptance),launcher_SHA=sha(R/'launch_startup_lift_pose_v5.py'),
    files_pinned=len(records),support_gain20_actually_pinned=True,original_loop_and_private_gate_AST_equal=True,actual_model_FK_PHY_oldQA_native_Git_calls=0)
dump(D/'PREPARATION_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2))
