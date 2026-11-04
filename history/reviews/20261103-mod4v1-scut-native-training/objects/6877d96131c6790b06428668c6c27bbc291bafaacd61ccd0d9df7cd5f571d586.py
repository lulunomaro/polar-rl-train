"""Fix native USD array conversion before any scene physics or model decode."""
from pathlib import Path
import ast
import hashlib
import json
import time
N=Path(__file__).resolve().parent;G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
P=N/'env20000_scut_stairs_1h_20261104';B=P/'attempt04';A=P/'attempt05'
read=lambda path:json.loads(Path(path).read_bytes())
H=lambda value:hashlib.sha256(value).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2)
f=read(B/'reports/FIRST_ACTUAL_RETURNED.json')['files']
assert 'numpy.int32'in f['production/ERROR.json']['error']
assert not f.get('production/FIRST_UPDATED.json')and not f.get('production/FINETUNE_INITIALIZATION.json')
assert all(f['OWNER_EXIT.json'][key]for key in('all_own_waited','original_cost_settled','original_leases_released'))
prior=read(B/'PLAN.json');go=f['GO_PRODUCTION.json'];remaining=int(go['save_deadline']-time.time());assert remaining>60
remote=read(P/'PLAN.json')['remote_root']+'/attempt05';plan=dict(prior)
plan.update(run_id=read(P/'PLAN.json')['run_id']+'_USD_ARRAY_FIX05',remote_root=remote,
    module_overlay=remote+'/overlay',module_overlays=[remote+'/overlay']+prior['module_overlays'],
    train_seconds=remaining,max_parent_seconds=remaining+300,
    repair='Use Vt.IntArray.FromNumpy for facecounts/indices; previous constructor rejected numpy.int32 before model or physics',
    prior_failure=str(B/'reports/FIRST_ACTUAL_RETURNED.json'),new_budget_or_refund=False)
A.mkdir();(A/'reports').mkdir();put(A/'PLAN.json',plan)
for name in('owner.py','entry.py'):(A/name).write_bytes((B/name).read_bytes())
files=[]
path=G/'project/isaac/mod4v1_scut/stairs.py';value=path.read_bytes();ast.parse(value)
files.append(dict(path=str(path),relative='overlay/stairs.py',bytes=len(value),SHA=H(value)))
for name in('PLAN.json','owner.py','entry.py'):
    path=A/name;value=path.read_bytes();files.append(dict(path=str(path),relative=name,bytes=len(value),SHA=H(value)))
old=read(B/'INDEX_SOURCE_FROZEN.json');shared=list(old['shared_text'])
for row in old['files']:
    if row['relative'].startswith('overlay/'):
        shared.append(dict(path=prior['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
put(A/'INDEX_SOURCE_FROZEN.json',dict(files=files,shared_text=shared,
    overlay_resolution_order=plan['module_overlays'],source_only=True,whole_tree_model_asset_copy=False,
    same_original_absolute_save=go['save_deadline'],same_original_absolute_exit=go['nominal_end_epoch'],new_budget_or_refund=False))
put(A/'reports/NATIVE_ARRAY_FAILURE_AND_REPAIR.json',dict(epoch=time.time(),prior_error=f['production/ERROR.json'],
    prior_exit=f['OWNER_EXIT.json'],prior_model_decodes=0,prior_physics=0,
    fix='Vt.IntArray.FromNumpy, existing Vec3fArray.FromNumpy reached nextline successfully',
    save_deadline=go['save_deadline'],new_hour=False))
print(json.dumps(dict(root=str(A),remaining=remaining,files=len(files),save=go['save_deadline'])))
