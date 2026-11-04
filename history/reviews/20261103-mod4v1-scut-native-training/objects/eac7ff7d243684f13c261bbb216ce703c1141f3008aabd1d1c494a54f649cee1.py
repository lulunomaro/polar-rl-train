"""Retry only the measured patch-stream failure inside the approved hour."""
from pathlib import Path
import ast
import hashlib
import json
import time

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
P=N/'env20000_scut_stairs_1h_20261104';B=P/'attempt06';A=P/'attempt07'
read=lambda path:json.loads(Path(path).read_bytes())
H=lambda raw:hashlib.sha256(raw).hexdigest()


def put(path,value):
    with path.open('x',encoding='utf8',newline='\n')as out:json.dump(value,out,ensure_ascii=False,indent=2)


f=read(B/'reports/POSTROUND_FULL_RETURNED.json')['files']
assert all(f['OWNER_EXIT.json'][k]for k in('all_own_waited','original_cost_settled','original_leases_released'))
assert 'Patch buffer overflow detected'in read(B/'reports/FIRST_ACTUAL_RETURNED.json')['files']['WORKER.log']
assert read(B/'reports/ACTUAL_PATCH_FAILURE_FINAL_NATIVE_REVIEW.json')['current_model_view_image']
go=f['GO_PRODUCTION.json'];remaining=int(go['save_deadline']-time.time());assert remaining>60
old=read(B/'PLAN.json');remote=old['remote_root'].rsplit('/',1)[0]+'/attempt07'
plan=dict(old)
plan.update(run_id=old['run_id']+'_PATCH_STREAM_FIX07',remote_root=remote,
    module_overlay=remote+'/overlay',module_overlays=[remote+'/overlay']+old['module_overlays'],
    train_seconds=remaining,max_parent_seconds=remaining+300,
    original_window_run_id=old['run_id'],original_save_deadline=go['save_deadline'],
    original_nominal_end_epoch=go['nominal_end_epoch'],original_window_extended=False,
    newly_authorized_window=False,remaining_original_authorized_window=True,
    gpu_max_rigid_patch_count=2**19,
    repair='Only actual overflowing contact patch stream: cfg.sim.physics.gpu_max_rigid_patch_count=524288; original pair buffers unchanged',
    prior_failure=str(B/'reports/ACTUAL_PATCH_BUFFER_FAILURE_AND_REPAIR.json'),
    prior_final_failed_training_SHA=f['production/FINAL.json']['checkpoint']['SHA'],
    source_checkpoint=old['source_checkpoint'],new_budget_or_refund=False)
A.mkdir();(A/'reports').mkdir();put(A/'PLAN.json',plan)
(A/'owner.py').write_bytes((P/'attempt05/owner.py').read_bytes())
(A/'entry.py').write_bytes((B/'entry.py').read_bytes())
files=[]
path=G/'project/isaac/mod4v1_scut/sdk.py';raw=path.read_bytes();ast.parse(raw)
files.append(dict(path=str(path),relative='overlay/sdk.py',bytes=len(raw),SHA=H(raw)))
for name in('PLAN.json','owner.py','entry.py'):
    path=A/name;raw=path.read_bytes()
    if path.suffix=='.py':ast.parse(raw)
    files.append(dict(path=str(path),relative=name,bytes=len(raw),SHA=H(raw)))
index=read(B/'INDEX_SOURCE_FROZEN.json');shared=list(index['shared_text'])
for row in index['files']:
    if row['relative'].startswith('overlay/'):
        shared.append(dict(path=old['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
put(A/'INDEX_SOURCE_FROZEN.json',dict(epoch=time.time(),files=files,shared_text=shared,
    overlay_resolution_order=plan['module_overlays'],source_only=True,
    whole_tree_model_asset_copy=False,original_absolute_save=go['save_deadline'],
    original_absolute_exit=go['nominal_end_epoch'],new_budget_or_refund=False))
put(A/'reports/PATCH_STREAM_RETRY_PREPARED.json',dict(epoch=time.time(),prior_owner_exit=f['OWNER_EXIT.json'],
    prior_failed_final=f['production/FINAL.json'],prior_evaluation=f['evaluation/RESULT.json'],
    prior_all_four_native_images_reviewed=True,
    repair=plan['repair'],configured_patch_capacity=2**19,
    actual_required_max_in_FIRST=267958,original_pair_capacity_unchanged=True,
    CPU_regression_tests=2,CPU_tests_passed=True,production_model_reads_for_prepare=0,
    physics_for_prepare=0,source_failed_weights_used=False,
    source_checkpoint=plan['source_checkpoint'],original_save=go['save_deadline'],new_hour=False))
print(json.dumps(dict(root=str(A),remaining_seconds=remaining,files=len(files),source_SHA=plan['source_checkpoint']['SHA'],save=go['save_deadline'])))
