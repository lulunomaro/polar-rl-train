"""Split physical collision cooking while preserving the recorded ray geometry."""
from pathlib import Path
import ast
import hashlib
import json
import time
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
P=N/'env20000_scut_stairs_1h_20261104';B=P/'attempt03';A=P/'attempt04'
read=lambda path:json.loads(Path(path).read_bytes())
H=lambda value:hashlib.sha256(value).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2)
f=read(B/'reports/POSTROUND_FULL_RETURNED.json')['files']
assert all(f['OWNER_EXIT.json'][key]for key in('all_own_waited','original_cost_settled','original_leases_released'))
assert(B/'reports/ACTUAL_MESH_COOKING_FAILURE.json').exists()
assert all((B/'evaluation'/name/'RENDER_REPORT.json').exists()for name in('recorded_native','recorded_native_late'))
go=f['GO_PRODUCTION.json'];remaining=int(go['save_deadline']-time.time());assert remaining>300
put(B/'reports/ACTUAL_COOKING_FAILURE_NATIVE_REVIEW.json',dict(epoch=time.time(),valid_training=False,
    reason='Native cooking failure for the140column single collision mesh before actual FIRST',
    first=f['production/FIRST_UPDATED.json'],final=f['production/FINAL.json'],owner_exit=f['OWNER_EXIT.json'],
    evaluation=f['evaluation/RESULT.json'],current_model_view_image=True,actual_images=4,
    findings='Early drop to selected original inverse-stair centre; env0 staysnearcentre,env1/40/41 travel beyond narrowview;41ends6.44s. Independent80 on14columns does not validate the missing140column collision mesh.',
    source_for_retry='Original valid0fdd, not failed7ea final',model_decodes=0,new_physics=0))
prior=read(B/'PLAN.json');plan=dict(prior);remote=read(P/'PLAN.json')['remote_root']+'/attempt04'
plan.update(run_id=read(P/'PLAN.json')['run_id']+'_COLLISION_CHUNK_FIX04',remote_root=remote,
    module_overlay=remote+'/overlay',module_overlays=[remote+'/overlay']+prior['module_overlays'],
    train_seconds=remaining,max_parent_seconds=remaining+300,
    repair='Preserve original raymesh without CollisionAPI; cook10physical14column strips and sum actualcontact filters',
    prior_failure=str(B/'reports/ACTUAL_COOKING_FAILURE_NATIVE_REVIEW.json'),
    original_window_extended=False,new_budget_or_refund=False)
A.mkdir();(A/'reports').mkdir();put(A/'PLAN.json',plan)
for name in('owner.py','entry.py'):(A/name).write_bytes((B/name).read_bytes())
files=[]
for name in('stairs.py','sdk.py'):
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
put(A/'reports/COOKING_REPAIR_SOURCE.json',dict(epoch=time.time(),source_modules=2,
    selected_stair_geometry_unchanged=True,physics_collision_meshes=10,
    raymesh_collisionAPI=False,old_failure_preserved=True,
    reader_false='Local CPU runtime cannot import pxr without application. No targetnative claim from that read; USD authoring verified only in native launch.',
    source_checkpoint=plan['source_checkpoint'],save_deadline=go['save_deadline'],new_hour=False))
print(json.dumps(dict(root=str(A),remaining=remaining,files=len(files),save=go['save_deadline'])))
