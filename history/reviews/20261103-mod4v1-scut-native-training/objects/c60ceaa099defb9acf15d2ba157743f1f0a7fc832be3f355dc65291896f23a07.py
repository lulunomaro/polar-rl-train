"""Repeat selected stair tiles spatially after the measured pair-buffer OOM."""
from pathlib import Path
import ast
import hashlib
import json
import time
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
P=N/'env20000_scut_stairs_1h_20261104';B=P/'attempt02';A=P/'attempt03'
read=lambda path:json.loads(Path(path).read_bytes())
H=lambda value:hashlib.sha256(value).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2)

failed=read(B/'reports/FIRST_ACTUAL_RETURNED.json')['files']
assert 'out of memory'in failed['production/ERROR.json']['error']
assert not failed.get('production/FIRST_UPDATED.json')
assert all(failed['OWNER_EXIT.json'][key]for key in('all_own_waited','original_cost_settled','original_leases_released'))
prior=read(B/'PLAN.json');go=failed['GO_PRODUCTION.json'];assert go['save_deadline']>time.time()+900
remote=read(P/'PLAN.json')['remote_root']+'/attempt03'
plan=dict(prior);remaining=int(go['save_deadline']-time.time())
plan.update(run_id=read(P/'PLAN.json')['run_id']+'_STAIR_TILE_LAYOUT_FIX03',remote_root=remote,
    module_overlay=remote+'/overlay',module_overlays=[remote+'/overlay']+prior['module_overlays'],
    train_seconds=remaining,max_parent_seconds=remaining+300,
    repair='Same10 difficulty rows with140 repeated columns for20k instead of14; return aggregatepair buffer to original32M after280M caused actualOOM',
    course_layout=dict(source_rows=10,source_columns=14,training_rows=10,training_columns=140,
        selected_branch_unchanged=True,perstep_geometry_reward_and_PPO_unchanged=True,
        purpose='Reduce co-located articulation density and broadphase pairs; original20k retained'),
    prior_failure=str(B/'reports/FIRST_ACTUAL_RETURNED.json'),original_window_extended=False,new_budget_or_refund=False)
A.mkdir();(A/'reports').mkdir();put(A/'PLAN.json',plan)
for name in('owner.py','entry.py'):(A/name).write_bytes((B/name).read_bytes())
files=[]
for name in('stairs.py','sdk.py','train.py'):
    path=G/'project/isaac/mod4v1_scut'/name;value=path.read_bytes();ast.parse(value)
    files.append(dict(path=str(path),relative='overlay/'+name,bytes=len(value),SHA=H(value)))
for name in('PLAN.json','owner.py','entry.py'):
    path=A/name;value=path.read_bytes();files.append(dict(path=str(path),relative=name,bytes=len(value),SHA=H(value)))
old=read(B/'INDEX_SOURCE_FROZEN.json');shared=list(old['shared_text'])
for row in old['files']:
    if row['relative'].startswith('overlay/'):
        shared.append(dict(path=prior['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
put(A/'INDEX_SOURCE_FROZEN.json',dict(files=files,shared_text=shared,
    overlay_resolution_order=plan['module_overlays'],source_only=True,whole_tree_model_asset_copy=False,
    same_original_absolute_save=go['save_deadline'],same_original_absolute_exit=go['nominal_end_epoch'],
    new_budget_or_refund=False,source_weights_or_STD_reinitialized=False))
put(A/'reports/ACTUAL_OOM_AND_LAYOUT_REPAIR.json',dict(epoch=time.time(),old_error=failed['production/ERROR.json'],
    old_closed=failed['TRAIN_CLOSED.json'],old_exit=failed['OWNER_EXIT.json'],
    old_FIRST=False,native_failure_not_reward_math=True,new_layout=plan['course_layout'],
    source_checkpoint=plan['source_checkpoint'],save_deadline=go['save_deadline'],
    original_nominal_end_epoch=go['nominal_end_epoch'],new_hour=False))
print(json.dumps(dict(root=str(A),remaining=remaining,files=len(files),save=go['save_deadline'])))
