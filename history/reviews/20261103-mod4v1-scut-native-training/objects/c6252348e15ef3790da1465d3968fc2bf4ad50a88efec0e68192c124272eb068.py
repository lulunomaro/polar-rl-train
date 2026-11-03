"""One source-only public-recipe candidate after the actual E0 input diagnosis."""
from pathlib import Path
import ast,hashlib,json,time

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
PREVIOUS=N/'env20000_repair_e0_1h_20261104'
Q=PREVIOUS/'e0_source_diagnostic'
A=N/'env20000_published_recipe_1h_20261104'
read=lambda p:json.loads(p.read_bytes())
H=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2)

facts=read(Q/'reports/attempt03/ACTUAL_E0_SOURCE_INPUT_NATIVE_REVIEW.json')
assert facts['result']['strict']==0 and facts['result']['anytop_envs']==0
assert facts['release']['all_own_waited']and facts['release']['locks_released']
assert facts['native_visual_review']['current_model_view_image']
assert facts['observations']['all_other_than_height_max_delta']<1.e-6
A.mkdir();(A/'reports').mkdir()
prior=read(PREVIOUS/'PLAN.json');plan=dict(prior)
remote=prior['remote_root'].rsplit('/',1)[0]+'/'+A.name
plan.update(run_id='MOD4V1_SCUT_PUBLISHED_RECIPE_20000ENV_1H_'+str(time.time_ns()),
    remote_root=remote,module_overlay=remote+'/overlay',
    module_overlays=[remote+'/overlay',prior['module_overlay']],
    profile='trained_stair',num_envs=20000,train_seconds=3600,max_parent_seconds=3900,
    initialization='Published SCUT weights-only flat-policy finetune method; same original enhanced E0/freshAdam/iteration0',
    resized_learning_continuation=False,
    previous_diagnostic=str(Q/'reports/attempt03/ACTUAL_E0_SOURCE_INPUT_NATIVE_REVIEW.json'),
    recipe_changes=['Use published trained_stair instead of custom jump270',
        'Disable Airborne/StepUp/Stair and omit the two additional Stair rewards',
        'Restore published velocity/heading/standing/special commands and height .2-.42',
        'Restore 20s training episode and randomized initial episode clocks',
        'Keep independent evaluation capped at first8s/400controls/seed9137',
        'Record pre-reset contact forces per resetbody and actual command/height; no termination threshold changes'],
    preserved=['Enhanced MOD4v1/USD and fullD0-D7','50policy100feedback400physics/.0025TGS32-4',
        'Original PD/DC/queue and clip6','Original SCUT PPO hyperparameters',
        'Chosen fixed270mm four-side course/spawn; no fullrough curriculum',
        'Strict270 acceptance and unique original canonical/reserve/fullsave boundaries'],
    task_differences=['Enhanced MOD4v1 and required physics instead of SCUT robot',
        'User-selected fixed270mm course and spawn relation instead of rough curriculum',
        'Enhanced MOD4 E0 weights instead of SCUT flat model8000'],
    exact_published_full_training_reproduction=False,
    independent_evaluation='first80 episodes capped at400controls/8s; seed9137 newDR; actual400Hz manifold and saved wxyz body poses')
put(A/'PLAN.json',plan)
owner=(PREVIOUS/'owner.py').read_bytes();ast.parse(owner);(A/'owner.py').write_bytes(owner)
entry=(PREVIOUS/'entry.py').read_text(encoding='utf-8')
old="if task.get('module_overlay'):\n    import mod4v1_scut\n    mod4v1_scut.__path__.insert(0,task['module_overlay'])"
new="if task.get('module_overlay'):\n    import mod4v1_scut\n    for overlay in reversed(task.get('module_overlays',[task['module_overlay']])):\n        mod4v1_scut.__path__.insert(0,overlay)"
assert entry.count(old)==1;entry=entry.replace(old,new);ast.parse(entry)
(A/'entry.py').write_text(entry,encoding='utf-8',newline='\n')
files=[]
for name in ('train.py','sdk.py','evaluate.py'):
    p=G/'project/isaac/mod4v1_scut'/name;raw=p.read_bytes();ast.parse(raw)
    files.append(dict(path=str(p),relative='overlay/'+name,bytes=len(raw),SHA=H(raw)))
for name in ('PLAN.json','owner.py','entry.py'):
    p=A/name;raw=p.read_bytes();files.append(dict(path=str(p),relative=name,bytes=len(raw),SHA=H(raw)))
old_index=read(PREVIOUS/'INDEX_SOURCE_FROZEN.json');shared=list(old_index['shared_text'])
for row in old_index['files']:
    if row['relative'].startswith('overlay/'):
        shared.append(dict(path=prior['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
put(A/'INDEX_SOURCE_FROZEN.json',dict(files=files,shared_text=shared,
    overlay_resolution_order=plan['module_overlays'],shared_package=plan['package_root'],
    source_only=True,tree_model_asset_copies=False,checkpoint_reads=0,physics=0))
print(json.dumps(dict(prepared=str(A),profile=plan['profile'],files=len(files),shared_refs=len(shared),native_started=False)))
