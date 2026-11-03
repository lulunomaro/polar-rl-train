"""Retry only the unused remainder of the original published-recipe window."""
from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
P=N/'env20000_published_recipe_1h_20261104';A=P/'attempt02'
read=lambda p:json.loads(p.read_bytes())
H=lambda b:hashlib.sha256(b).hexdigest()
def put(p,v):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(v,f,ensure_ascii=False,indent=2)
f=read(P/'reports/FIRST_ACTUAL_RETURNED.json')['files']
assert f['OWNER_EXIT.json']['all_own_waited']and f['OWNER_EXIT.json']['original_cost_settled']and f['OWNER_EXIT.json']['original_leases_released']
assert not f.get('production/FIRST_UPDATED.json')and 'Straight-speed contract violated'in f['production/ERROR.json']['error']
go=f['GO_PRODUCTION.json'];assert go['save_deadline']>time.time()+900
A.mkdir();(A/'reports').mkdir()
prior=read(P/'PLAN.json');plan=dict(prior);j=prior['remote_root']+'/attempt02'
remaining=int(go['save_deadline']-time.time())
plan.update(run_id=prior['run_id']+'_YAW_COMMAND_FIX02',remote_root=j,module_overlay=j+'/overlay',
    module_overlays=[j+'/overlay',prior['module_overlay'],*prior['module_overlays'][1:]],
    original_window_run_id=go['run_id'],original_save_deadline=go['save_deadline'],original_nominal_end_epoch=go['nominal_end_epoch'],
    train_seconds=remaining,max_parent_seconds=remaining+300,
    repair='Select yaw-capable shared runtime command domain; cfg.curriculum remainsNone; preserve failure exit1',
    original_window_extended=False,new_budget_or_refund=False,
    prior_failure=str(P/'reports/FIRST_ACTUAL_RETURNED.json'))
put(A/'PLAN.json',plan)
owner=(P/'owner.py').read_text(encoding='utf-8')
needle="source=source.replace(\"if __name__=='__main__':main()\",'')"
append='''
before="assert plan['train_seconds']in (3600,7200) and plan['max_parent_seconds']==plan['train_seconds']+300"
after="assert 0<plan['train_seconds']<=3600 and plan['max_parent_seconds']==plan['train_seconds']+300 and plan['original_save_deadline']>time.time() and plan['original_nominal_end_epoch']==plan['original_save_deadline']+300"
assert source.count(before)==1;source=source.replace(before,after)
before="save_deadline=now+plan['train_seconds'],nominal_end_epoch=now+plan['max_parent_seconds'],max_parent_seconds=plan['max_parent_seconds']"
after="save_deadline=plan['original_save_deadline'],nominal_end_epoch=plan['original_nominal_end_epoch'],max_parent_seconds=int(plan['original_nominal_end_epoch']-now)"
assert source.count(before)==1;source=source.replace(before,after)
'''
assert owner.count(needle)==1;owner=owner.replace(needle,needle+append);ast.parse(owner)
(A/'owner.py').write_text(owner,encoding='utf-8',newline='\n')
(A/'entry.py').write_bytes((P/'entry.py').read_bytes())
files=[]
for name in ('train.py','evaluate.py'):
    p=G/'project/isaac/mod4v1_scut'/name;raw=p.read_bytes();ast.parse(raw)
    files.append(dict(path=str(p),relative='overlay/'+name,bytes=len(raw),SHA=H(raw)))
for name in ('PLAN.json','owner.py','entry.py'):
    p=A/name;raw=p.read_bytes();files.append(dict(path=str(p),relative=name,bytes=len(raw),SHA=H(raw)))
old=read(P/'INDEX_SOURCE_FROZEN.json');shared=list(old['shared_text'])
for row in old['files']:
    if row['relative'].startswith('overlay/'):
        shared.append(dict(path=prior['remote_root']+'/'+row['relative'],bytes=row['bytes'],SHA=row['SHA']))
put(A/'INDEX_SOURCE_FROZEN.json',dict(files=files,shared_text=shared,overlay_resolution_order=plan['module_overlays'],
    same_original_absolute_save=go['save_deadline'],same_original_absolute_exit=go['nominal_end_epoch'],
    no_tree_model_asset_copy=True,source_only=True))
put(A/'reports/PRIOR_FAILURE_AND_REPAIR.json',dict(epoch=time.time(),original_result=f['TRAIN_CLOSED.json'],
    owner_exit=f['OWNER_EXIT.json'],actual_error=f['production/ERROR.json'],
    fix='RM_GYRO_CURRICULUM=1 for trained_stair selects yaw-capable command contract; cfg.curriculum remainsNone',
    no_curriculum_reintroduced=True,source_new_physics_before_admission=0,
    original_deadlines_preserved=True,remaining_training_window_seconds=remaining,new_hour=False))
print(json.dumps(dict(root=str(A),remaining_seconds=remaining,save_deadline=go['save_deadline'],exit_deadline=go['nominal_end_epoch'],source_files=len(files))))
