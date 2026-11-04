"""One E3 N80 metadata collector and original per-recipe grade, no PT/raw replay."""
from pathlib import Path
import json,time,sys
D=Path(__file__).resolve().parent;stage=json.loads((D/'EVAL_STAGE_RESULT.json').read_bytes());assert stage['returncode']==0 and(D/'EVAL_DISPATCH_RESULT.json').exists();root=stage['root'];assert not(D/'EVAL_OBSERVER_STARTED_ONCE.json').exists();(D/'EVAL_OBSERVER_STARTED_ONCE.json').write_text(json.dumps(dict(epoch=time.time(),root=root,cap_seconds=4500,interval_seconds=15)),encoding='utf8');sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp();start=time.monotonic();last=None
names=['ACTUAL_GROUP_ADMISSION.json','BOUNDED_ORIGINAL_RESOURCE_WAIT.json','GROUP_BARRIER_STATUS.json','GROUP_EVAL_START.json','FINAL.json','TERMINAL_ROWS.json','PARENT_EXIT_SCOPE.json','PARENT_ORIGINAL_ERROR.json','E3_ASSESSMENT_PARENT_WAITED_ACTUAL.json','cases/E3/WORKER_SCENE_READY.json','cases/E3/WORKER_EVAL_STARTED.json','cases/E3/PRE_CLOSE.json','cases/E3/FINAL.json','cases/E3/WORKER_ERROR.json']
def read(n):
 try:
  a=s.stat(root+'/'+n);assert a.st_size<8*1024*1024
  with s.open(root+'/'+n,'rb')as z:return json.loads(z.read())
 except FileNotFoundError:return None
try:
 while True:
  m={n:read(n)for n in names};outer=m['E3_ASSESSMENT_PARENT_WAITED_ACTUAL.json'];end=m['PARENT_EXIT_SCOPE.json'];closed=bool(outer and end);key=(bool(m['ACTUAL_GROUP_ADMISSION.json']),bool(m['GROUP_EVAL_START.json']),closed)
  current=dict(epoch=time.time(),root=root,closed=closed,metadata=m);p=D/'EVAL_CURRENT.tmp';p.write_text(json.dumps(current,indent=2),encoding='utf8');p.replace(D/'EVAL_CURRENT.json')
  if key!=last:print('E3_EVAL_PROGRESS '+json.dumps(dict(admitted=key[0],common_start=key[1],closed=closed)),flush=True);last=key
  if closed:
   group=m['FINAL.json']or{};f=m['cases/E3/FINAL.json'];rows=group.get('rows',[]);cache=(f or{}).get('source_cache',{});qualified=bool(f and group.get('all_members_actual_execution_complete')and len(rows)==1 and rows[0]['role']=='E3'and rows[0]['data']==f and rows[0]['actual_waited']and rows[0]['returncode']==0 and f['passed_execution']and f['controls']==160 and f['physics_callbacks']==1280 and f['feedback_samples']==320 and f['optimizer_updates']==0 and f['source_cache']['source_SHA']==stage['source']['SHA']and f['actor_STD_before_after_exact']and f['cached_full_checkpoint_before_after_exact']and m['cases/E3/WORKER_EVAL_STARTED.json']and m['cases/E3/PRE_CLOSE.json']and not m['cases/E3/WORKER_ERROR.json']and end['all_own_children_waited']and end['original_single_GPU_private_EX_released']and end['original_global_finite_EX_released']and not end['errors']and outer['actual_parent_p_wait_returned']and outer['returncode']==0 and not outer['errors'])
   current['execution_qualified']=qualified;current['full_expert_graduation']=False
   if qualified:
    recipe=f['skill']['original_recovery_recipe_rows'];req=[r for r in recipe if r['original_request']];normal=[r for r in recipe if not r['original_request']];assert len(req)==12 and len(normal)==1 and sum(r['initial_envs']for r in req)==74 and normal[0]['initial_envs']==6
    result=dict(kind='E3_ORIGINAL_N80_FIRST_EPISODE_FROZEN_SCOPE_NOT_FULL_GRADUATION',root=root,model_SHA=cache['source_SHA'],execution_qualified=True,seed=20260928,controls=160,seconds=3.2,recovery_n=sum(r['first_episode_original_stable_credit']for r in req),recovery_N=74,normal_N=6,normal_first_episode_physical_terminated=normal[0]['first_episode_physical_terminated'],original_recipe_rows=recipe,termination_events_by_reason=f['termination_events_by_reason'],source_cache=cache,baseline_selected_1cd_original_same_seed_credit=[0,74],matched_fullDR_realization_and_causal_improvement_not_claimed=True,full_expert_graduated=False)
    (D/'E3_ORIGINAL_FROZEN_SCOPE_RESULT.json').write_text(json.dumps(result,indent=2),encoding='utf8');print('E3_ORIGINAL_SKILL '+json.dumps({k:v for k,v in result.items()if k not in('source_cache','original_recipe_rows')}),flush=True)
   (D/'EVAL_CLOSED_RESULT.json').write_text(json.dumps(current,indent=2),encoding='utf8');print('E3_EVAL_CLOSED '+json.dumps(dict(qualified=qualified,root=root)),flush=True);break
  if time.monotonic()-start>=4500:(D/'EVAL_OBSERVER_TIMEOUT.json').write_text(json.dumps(dict(epoch=time.time(),root=root,original_parent_not_extended_or_signalled=True)),encoding='utf8');break
  time.sleep(15)
finally:s.close();c.close()
