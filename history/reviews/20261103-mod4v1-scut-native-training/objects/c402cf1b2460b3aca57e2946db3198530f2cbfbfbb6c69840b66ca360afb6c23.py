"""Source-only20k continuation after native target-limit and output repair review."""
from pathlib import Path
import ast
import hashlib
import json
import time

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
P=N/'env20000_published_recipe_1h_20261104/attempt02'
Q=P/'target_limit_eval1'
A=N/'env20000_target_axis_repair_1h_20261104'
read=lambda p:json.loads(Path(p).read_bytes())
H=lambda b:hashlib.sha256(b).hexdigest()


def put(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:
        json.dump(value,stream,ensure_ascii=False,indent=2)


native=read(Q/'reports/ACTUAL_TARGET_LIMIT_NATIVE_REVIEW.json')
axis=read(Q/'reports_first_axis/ACTUAL_FIRST_AXIS_NATIVE_REVIEW.json')
assert native['actual_all_motor_intervals_passed']
assert axis['actual_all_motor_intervals_passed']and axis['first_axis_raw_max_abs']==0.
assert axis['native_visual_review']['current_model_view_image']
assert axis['release']['all_own_waited']and axis['release']['locks_released']
prior=read(P/'PLAN.json');original=read(P/'reports/POSTROUND_FULL_RETURNED.json')['files']
plan=dict(prior)
for key in ('original_save_deadline','original_nominal_end_epoch','original_window_run_id','prior_failure','original_window_extended'):
    plan.pop(key,None)
remote=prior['remote_root'].split('/env20000_published_recipe_')[0]+'/'+A.name
plan.update(run_id='MOD4V1_SCUT_TARGET_LIMIT_FIRST_AXIS_20000ENV_1H_'+str(time.time_ns()),
    remote_root=remote,module_overlay=remote+'/overlay',
    module_overlays=[remote+'/overlay']+prior['module_overlays'],
    num_envs=20000,train_seconds=3600,max_parent_seconds=3900,
    source_checkpoint=original['production/FINAL.json']['checkpoint'],
    initialization='Weights-only samepublishedfinal actor35/critic78; explicit saturatedleftcrank row/bias0 and STD1; freshAdam iteration0',
    repair_first_axis=True,resized_learning_continuation=False,
    previous_diagnostics=[str(Q/'reports/ACTUAL_TARGET_LIMIT_NATIVE_REVIEW.json'),
                          str(Q/'reports_first_axis/ACTUAL_FIRST_AXIS_NATIVE_REVIEW.json')],
    repair='Processed fourmotor target limits and originalCADdifference beforeD4, nativeverified; explicit firstaxisinitialization',
    exact_published_full_training_reproduction=False,
    task_differences=prior['task_differences']+['Explicit left-crank output reinitialization after actual100% saturation; other learned tensors retained'],
    source_optimizer_loaded=False,source_checkpoint_overwritten=False,
    same_original_canonical=True,new_budget_or_refund=False)
A.mkdir();(A/'reports').mkdir();put(A/'PLAN.json',plan)
owner=(N/'env20000_repair_e0_1h_20261104/owner.py').read_bytes();ast.parse(owner)
(A/'owner.py').write_bytes(owner)
entry=(P/'entry.py').read_text(encoding='utf8')
before="    runpy.run_module('mod4v1_scut.train',run_name='__main__')"
after="    if task.get('repair_first_axis'):sys.argv+=['--repair-first-axis']\n"+before
assert entry.count(before)==1;entry=entry.replace(before,after);ast.parse(entry)
(A/'entry.py').write_text(entry,encoding='utf8',newline='\n')
files=[]
for name in ('config.py','target_limits.py','sdk.py','train.py','checkpoint.py','evaluate.py','finetune.py'):
    path=G/'project/isaac/mod4v1_scut'/name;raw=path.read_bytes();ast.parse(raw)
    files.append(dict(path=str(path),relative='overlay/'+name,bytes=len(raw),SHA=H(raw)))
for name in ('PLAN.json','owner.py','entry.py'):
    path=A/name;raw=path.read_bytes();files.append(dict(path=str(path),relative=name,bytes=len(raw),SHA=H(raw)))
oldindex=read(P/'INDEX_SOURCE_FROZEN.json');shared=list(oldindex['shared_text'])
for row in oldindex['files']:
    if row['relative'].startswith('overlay/'):
        shared.append(dict(path=prior['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
put(A/'INDEX_SOURCE_FROZEN.json',dict(files=files,shared_text=shared,
    overlay_resolution_order=plan['module_overlays'],source_only=True,
    whole_tree_model_asset_copy=False,native_diagnostics_reviewed=True,
    reward_PPO_spawn_physics_unchanged=True,explicit_initialization_repair=True))
print(json.dumps(dict(prepared=str(A),files=len(files),shared_refs=len(shared),native_launched=False)))
