"""NEW strategy, one nominal admission. Does not run controller/model or physics.
Only run this after parent reads V2's saved bounded synthetic proof.
"""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;D=R/'STARTUP_STAND_V2/front_admission001'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf-8')as f:json.dump(x,f,indent=2,allow_nan=False)
proof=R/'STARTUP_STAND_V2/PREFLIGHT_RESULT.json';p=json.loads(proof.read_bytes());assert p['status'].startswith('PASS'),p['status']
entry=R/'run_startup_stand_case_v4.py';der=json.loads((R/'STARTUP_STAND_V2/ENTRY_DERIVATION.json').read_bytes())
assert der['new_SHA']==sha(entry)and der['original_control_loop_AST_equal']and der['healthy_good_complete_passed_AST_equal']
assert der['new_SHA']=='fcb8a10b6dfb1795a39870592e376af0c93dddda3ec2c3db5414d675d0d36c9d'
D.mkdir(exist_ok=False)
old=json.loads((R/'STARTUP_STAND_V1/front_admission001/CONFIG.json').read_bytes());cfg=dict(old)
cfg.update(case_id='startup_front065_coupled_v2_nominal1',kind='NEW_STARTUP_COUPLED_FRONT_NOMINAL_ADMISSION',controller=dict(operator_enable=True,recovery_actuation_enable=True))
a=dict(cfg);b=dict(old)
for x in(a,b):x.pop('case_id');x.pop('kind');x['controller']=dict(x['controller']);x['controller'].pop('recovery_actuation_enable',None)
assert a==b
assert not (R/'results'/cfg['case_id']).exists()and not(R/'batches/startup_front065_coupled_v2_nominal1').exists()
dump(D/'CONFIG.json',cfg)
# All old rooted controller/plant code pinned before the new case; no raw/model hashes.
idx=json.loads((R/'STARTUP_STAND_V1/front_admission001/SOURCE_PREEXEC.json').read_bytes())
paths={R/x['path']for x in idx['files']}
paths.update([Path(__file__).resolve(),entry,R/'STARTUP_STAND_V2/controller.py',R/'STARTUP_STAND_V2/METHOD.md',proof,
    R/'STARTUP_STAND_V2/ENTRY_DERIVATION.json',R/'run_startup_stand_case_v3.py',R/'STARTUP_STAND_V1/reporting_fix003/RECEIPT.json',
    R.parent/'traditional_control_20261101/dr_components.py'])
records=[]
for f in sorted(paths):
    b=f.read_bytes();records.append(dict(path=str(f.resolve()),bytes=len(b),SHA=sha(f)))
dump(D/'SOURCE_PREEXEC.json',dict(files=records,allowed_readonly_source_roots=[str(R),str(R.parent/'traditional_control_20261101')],
    actual_full_asset_guard_still_runs_in_real_episode_not_previously_claimed=True,model_assets_raw_oldQA_not_opened_here=True))
dump(D/'PROTOCOL.json',dict(kind='STARTUP_COUPLED_FRONT065_SINGLE_NOMINAL_TRAIN_ADMISSION',runner=entry.name,config=cfg,max_workers=1,
    previous_failed_case_not_replayed=True,new_strategy_not_only_bookkeeping_fix=True,all_neutral_removed_configs_equal=True,
    maximum_controls=1000,maximum_physics_steps=20000,old_controller_observer_model_driver_grade_gates_unchanged=True,
    same_passively_settled_front_fixture_only_one_initialization=True,upright_prior=False,
    no_DR_back_side_or_automatic_retry=True,support_gate='All2kHz support samples in last3s bins; original100Hz pose gates; not between-sample proof.',
    candidate_is_parent_locked_hypothesis_not_stability_certificate=True,parent_manual_code_and_saved_proof_review_required=True))
dump(D/'PREPARATION_RECEIPT.json',dict(status='PREPARED_NEW_STRATEGY_NOMINAL_CASE_NOT_EXECUTED',config_SHA=sha(D/'CONFIG.json'),protocol_SHA=sha(D/'PROTOCOL.json'),
    source_index_SHA=sha(D/'SOURCE_PREEXEC.json'),runner_SHA=sha(entry),candidate_SHA=sha(R/'STARTUP_STAND_V2/controller.py'),
    saved_synthetic_proof_SHA=sha(proof),files_pinned=len(records),actual_project_import_model_FK_controller_PHY_Git_calls=0))
print((D/'PREPARATION_RECEIPT.json').read_text(encoding='utf-8'))
