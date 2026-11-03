"""Freeze one NEW front-lying startup admission. No model/controller execution.
V1 runner remains unchanged/unexecuted; V2 fixes only private support semantics.
"""
from pathlib import Path
import ast,hashlib,json
R=Path(__file__).resolve().parent;D=R/'STARTUP_STAND_V1/front_admission001';D.mkdir(exist_ok=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf-8')as f:json.dump(x,f,indent=2,allow_nan=False)
v1=R/'run_startup_stand_case_v1.py';old=v1.read_text(encoding='utf-8')
changes=[
("            main=np.mean([r['main_normal_N2']for r in sub],axis=0)","            main_series=np.asarray([r['main_normal_N2']for r in sub]);assert main_series.shape==(20,2)\n            main=np.mean(main_series,axis=0);both_support=bool(np.all(main_series>1.))"),
("in_balance and healthy and np.all(main>1.)and no_other","in_balance and healthy and both_support and no_other"),
("main_contact_mean_N2=main.tolist(),no_other_contact_in_control=no_other,","main_contact_mean_N2=main.tolist(),main_contact_min_N2=np.min(main_series,axis=0).tolist(),both_support_every_2k_sample=both_support,no_other_contact_in_control=no_other,"),
("grade_requires_actual_double_wheel_support_and_no_nonwheel_tail=True,","grade_requires_actual_double_wheel_support_and_no_nonwheel_tail=True,grade_support_sample_Hz=2000,\n            every_support_sample_in_consecutive_last_3s_bins=True,between_2k_samples_not_continuous_time_proven=True,pose_velocity_joint_gates_sampled_Hz=100,")]
new=old
for a,b in changes:assert new.count(a)==1;new=new.replace(a,b)
ast.parse(new);v2=R/'run_startup_stand_case_v2.py'
with v2.open('x',encoding='utf-8',newline='')as f:f.write(new)
# New software-only support fixtures: no imports of NumPy, controller or model.
fixtures=[('all_double_support',[[2.,3.]]*20,True),
 ('alternating_mean_false_positive',[[3.,0.]]*10+[[0.,3.]]*10,False),
 ('exact_one_N_is_not_above',[[2.,3.]]*19+[[1.,3.]],False)]
for _,rows,want in fixtures:assert all(all(x>1. for x in row)for row in rows)==want
alternating=fixtures[1][1];assert all(sum(row[i]for row in alternating)/20>1. for i in range(2))
dump(D/'SUPPORT_CORRECTION.json',dict(old_runner_SHA=sha(v1.read_bytes()),new_runner_SHA=sha(v2.read_bytes()),
    changes=[dict(old=a,new=b)for a,b in changes],fixtures=fixtures,checks=4,passes=4,
    old_runner_executed=False,model_controller_oldQA_physics_calls=0,threshold_unchanged_N=1.,
    support_definition='Every recorded 2kHz sample has both main wheel normals >1N. Not just boxcar means; not proof between sample times.'))
cfg=dict(case_id='startup_front065_nominal_v1',kind='NEW_STARTUP_FRONT_NOMINAL_ADMISSION',seed=0,nominal=True,duration_s=10.,
    initial_fixture='STARTUP_STAND_V1/passive_settle001/front_rest_065/result.json',controller=dict(operator_enable=True))
dump(D/'CONFIG.json',cfg)
# Read-only local AST import closure; no imports or execution of project code.
paths={Path(__file__).resolve(),v1,v2,R/'fresh_train_batch_v2.py',R/cfg['initial_fixture'],
       R/'STARTUP_STAND_V1/PREFLIGHT_RESULT.json',R/'STARTUP_STAND_V1/ENTRY_DELTA_REVIEW_001.json',R/'TALL_ROUGH_BANK_V1/gain_delta0.json'}
queue=[v2]
while queue:
    p=queue.pop()
    for node in ast.walk(ast.parse(p.read_text(encoding='utf-8-sig'))):
        modules=[node.module]if isinstance(node,ast.ImportFrom)and node.module else [a.name for a in node.names]if isinstance(node,ast.Import)else []
        for mod in modules:
            candidate=R.joinpath(*mod.split('.')).with_suffix('.py')
            if candidate.is_file()and candidate not in paths:paths.add(candidate);queue.append(candidate)
records=[]
for p in sorted(paths):
    b=p.read_bytes();records.append(dict(path=str(p.relative_to(R)).replace('\\','/'),bytes=len(b),SHA=sha(b)))
dump(D/'SOURCE_PREEXEC.json',dict(files=records,local_AST_imports_only=True,all_asset_model_checks_remain_in_real_episode_manifest=True,
    libraries_models_raw_assets_not_rehashed_for_metadata=True))
dump(D/'PROTOCOL.json',dict(kind='STARTUP_FRONT065_SINGLE_NOMINAL_TRAIN_ADMISSION',config=cfg,runner=v2.name,
    max_workers=1,maximum_controls=1000,maximum_physics_steps=20000,old_controller_unit_not_replayed=True,
    only_initial_saved_qpos_qvel_then_no_root_overwrite_or_assist=True,upright_prior=False,
    support='All 2kHz samples in each of last consecutive3s: LFn>1N and RFn>1N, guide/hard<=1N.',
    other_unchanged_private_gates='BALANCE; each100Hz endpoint finite/closure<=.01/mimic<=.01/uprightCos>=.45; |pitch,roll|<.10, |vx|<.15, |omega|<.35, maxjointErr<.08, rootZ>=.30; finalheightGain>=.05/maxXY<=.5.',
    initial_guide_contact_allowed=True,software_failure_save_actual_prefix_and_stop=True,
    real_standup_pass_not_yet_observed=True,fullDR_or_back_side_recovery_not_qualified=True,
    launch_allowed_only_after_new_independent_delta_review_and_parent_approval=True))
print(json.dumps(dict(status='PREPARED_ONE_FRONT065_NOT_EXECUTED',source_files=len(records),
    config_SHA=sha((D/'CONFIG.json').read_bytes()),protocol_SHA=sha((D/'PROTOCOL.json').read_bytes()),source_index_SHA=sha((D/'SOURCE_PREEXEC.json').read_bytes()),
    new_runner_SHA=sha(v2.read_bytes()),support_fixtures=4,physics_model_controller_calls=0),indent=2))
