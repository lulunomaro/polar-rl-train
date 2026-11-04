"""Repair the measured pair-buffer shortage within the original absolute hour."""
from pathlib import Path
import ast
import hashlib
import json
import time

N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
P=N/'env20000_scut_stairs_1h_20261104';A=P/'attempt02'
read=lambda path:json.loads(Path(path).read_bytes())
H=lambda value:hashlib.sha256(value).hexdigest()
def put(path,value):
    with path.open('x',encoding='utf8',newline='\n')as stream:json.dump(value,stream,indent=2)

f=read(P/'reports/POSTROUND_FULL_RETURNED.json')['files']
exit=f['OWNER_EXIT.json'];assert all(exit[key]for key in('all_own_waited','original_cost_settled','original_leases_released'))
assert 'foundLostAggregatePairsCapacity'in f['WORKER.log']
assert all((P/'evaluation'/name/'RENDER_REPORT.json').exists()for name in('recorded_native','recorded_native_late'))
go=f['GO_PRODUCTION.json'];assert go['save_deadline']>time.time()+900
review=dict(epoch=time.time(),valid_training=False,reason='PhysX explicitly reported dropped interactions: foundLostAggregatePairsCapacity269692772 required',
    first=f['production/FIRST_UPDATED.json'],final=f['production/FINAL.json'],owner_exit=exit,
    evaluation=f['evaluation/RESULT.json'],current_model_view_image=True,actual_images=4,
    visual_findings='Env0 remains near birth; env1 moves and returns; env40/41 leave narrow view while actual saved terrain and body poses remain valid. env41 terminates6.36s. Evaluation does not validate the20k dropped-pair training.',
    source_for_retry='Original valid0fdd weights, not this failed16ece final',
    scope_of_repair='Only aggregate pair storage; leave physical integration/solver/DR/reward/PPO and source weights unchanged',
    initial_overlap_or_shared_terrain_is_not_proven_unique_cause=True,
    original_save_deadline=go['save_deadline'],original_nominal_end_epoch=go['nominal_end_epoch'],new_budget_or_refund=False)
put(P/'reports/ACTUAL_CAPACITY_FAILURE_NATIVE_REVIEW.json',review)
prior=read(P/'PLAN.json');plan=dict(prior);remote=prior['remote_root']+'/attempt02'
plan.update(run_id=prior['run_id']+'_PAIR_BUFFER_FIX02',remote_root=remote,
    module_overlay=remote+'/overlay',module_overlays=[remote+'/overlay']+prior['module_overlays'],
    original_window_run_id=go['run_id'],original_save_deadline=go['save_deadline'],
    original_nominal_end_epoch=go['nominal_end_epoch'],train_seconds=int(go['save_deadline']-time.time()),
    max_parent_seconds=int(go['save_deadline']-time.time())+300,
    repair='Set actual20000-stair gpu_found_lost_aggregate_pairs_capacity280000000 after native requested269692772',
    original_window_extended=False,new_budget_or_refund=False,
    prior_failure=str(P/'reports/ACTUAL_CAPACITY_FAILURE_NATIVE_REVIEW.json'))
A.mkdir();(A/'reports').mkdir();put(A/'PLAN.json',plan)
owner=(P/'owner.py').read_text(encoding='utf8')
needle="source=source.replace(\"if __name__=='__main__':main()\",'')"
extra='''
before="assert plan['train_seconds']in (3600,7200) and plan['max_parent_seconds']==plan['train_seconds']+300"
after="assert 0<plan['train_seconds']<=3600 and plan['max_parent_seconds']==plan['train_seconds']+300 and plan['original_save_deadline']>time.time() and plan['original_nominal_end_epoch']==plan['original_save_deadline']+300"
assert source.count(before)==1;source=source.replace(before,after)
before="save_deadline=now+plan['train_seconds'],nominal_end_epoch=now+plan['max_parent_seconds'],max_parent_seconds=plan['max_parent_seconds']"
after="save_deadline=plan['original_save_deadline'],nominal_end_epoch=plan['original_nominal_end_epoch'],max_parent_seconds=int(plan['original_nominal_end_epoch']-now)"
assert source.count(before)==1;source=source.replace(before,after)
'''
assert owner.count(needle)==1;owner=owner.replace(needle,needle+extra);ast.parse(owner)
(A/'owner.py').write_text(owner,encoding='utf8',newline='\n')
(A/'entry.py').write_bytes((P/'entry.py').read_bytes())
files=[]
path=G/'project/isaac/mod4v1_scut/sdk.py';value=path.read_bytes();ast.parse(value)
files.append(dict(path=str(path),relative='overlay/sdk.py',bytes=len(value),SHA=H(value)))
for name in('PLAN.json','owner.py','entry.py'):
    path=A/name;value=path.read_bytes();files.append(dict(path=str(path),relative=name,bytes=len(value),SHA=H(value)))
old=read(P/'INDEX_SOURCE_FROZEN.json');shared=list(old['shared_text'])
for row in old['files']:
    if row['relative'].startswith('overlay/'):
        shared.append(dict(path=prior['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
put(A/'INDEX_SOURCE_FROZEN.json',dict(files=files,shared_text=shared,
    overlay_resolution_order=plan['module_overlays'],source_only=True,whole_tree_model_asset_copy=False,
    same_original_absolute_save=go['save_deadline'],same_original_absolute_exit=go['nominal_end_epoch'],
    new_budget_or_refund=False,output_or_STD_reinitialization=False))
put(A/'reports/ORIGINAL_WINDOW_CAPACITY_REPAIR.json',dict(epoch=time.time(),native_failure_review=review,
    native_reported_required_capacity=269692772,configured_capacity=280000000,
    source_checkpoint=plan['source_checkpoint'],original_save_deadline=go['save_deadline'],
    original_nominal_end_epoch=go['nominal_end_epoch'],new_hour=False,model_reads=0,physics=0))
print(json.dumps(dict(root=str(A),remaining=plan['train_seconds'],save=go['save_deadline'],source_files=len(files))))
