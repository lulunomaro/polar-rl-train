"""Once <=4500s /15s own-JSON collector. No model/raw/log/C/GPU-state reads."""
from pathlib import PurePosixPath
import argparse,json,math,time
from E0_SINGLE_FROZEN_stage import D,OWN,connect,need,put,read_json
ROOT_NAMES=['PARENT_STARTED.json','BOUNDED_ORIGINAL_RESOURCE_WAIT.json','ACTUAL_GROUP_ADMISSION.json','CHILDREN.json','GROUP_BARRIER_STATUS.json','GROUP_EVAL_START.json','GROUP_ABORT.json','GROUP_STARTUP_ABORT.json','PARENT_ORIGINAL_ERROR.json','TERMINAL_ROWS.json','E0_SINGLE_FROZEN_PARENT_FINAL.json','PARENT_EXIT_SCOPE.json','OUTER_OWNER_IDENTITY.json','OUTER_OWNER_WAIT_ACTUAL.json']
CASE_NAMES=['task.json','WORKER_SCENE_READY.json','WORKER_EVAL_STARTED.json','V2_FROZEN_EVAL_FINAL.json','PRE_CLOSE.json','ENV_CLOSE_RETURNED.json','V2_FROZEN_EVAL_APP_CLOSE_INTENT.json','APP_CLOSED.json']

def normal_metrics(final):
 if not isinstance(final,dict):return None
 skill=final.get('skill') or {};integral=skill.get('body_velocity_absolute_error_time_integral_per_env');n=final.get('num_envs');seconds=final.get('seconds');mae=None
 if n==80 and isinstance(seconds,(int,float)) and seconds>0 and isinstance(integral,list) and len(integral)==80 and all(isinstance(row,list) and len(row)==3 and all(isinstance(v,(int,float)) and math.isfinite(v) for v in row) for row in integral):mae=dict(zip(('body_vx_m_s','body_vy_m_s','yaw_rate_rad_s'),[sum(row[i] for row in integral)/(n*seconds) for i in range(3)]))
 return dict(controls=final.get('controls'),seconds=seconds,physics_callbacks=final.get('physics_callbacks'),feedback_samples=final.get('feedback_samples'),termination_events_by_reason=final.get('termination_events_by_reason'),unique_envs_terminated=final.get('unique_envs_terminated'),unique_envs_truncated=final.get('unique_envs_truncated'),episode_end_events=final.get('episode_end_events'),body_velocity_MAE=mae,max_current_closure_m=final.get('max_current_closure_m'),max_current_mimic_rad=final.get('max_current_mimic_rad'),max_raw_action_abs=final.get('max_raw_action_abs'),max_applied_action_abs=final.get('max_applied_action_abs'),skill_grader=skill.get('full_grader'),predicate_gap=skill.get('predicate_gap'),full_skill_graduation=final.get('full_skill_graduation'),execution_not_skill_graduation=True)

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--seconds',type=int,default=4500);args=parser.parse_args();need(1<=args.seconds<=4500,'Own JSON observation bound at most4500s')
 marker=D/'E0_SINGLE_FROZEN_COLLECT_ONCE.json';need(not marker.exists(),'One own metadata observation only');stage=read_json(D/'E0_SINGLE_FROZEN_STAGE_RESULT.json');dispatch=read_json(D/'E0_SINGLE_FROZEN_DISPATCH_RESULT.json');need(stage['returncode']==dispatch['returncode']==0 and stage['root']==dispatch['root'],'Same actually dispatched own purpose');root=stage['root'];need(root.startswith(OWN+'/tasks/E0_SINGLE_FROZEN_'),'Only new E0 eval root')
 out=D/'reports'/stage['run_id'];out.mkdir(parents=True,exist_ok=False);put(marker,dict(epoch=time.time(),root=root,output=str(out),bound_seconds=args.seconds,interval_seconds=15,only_own_JSON=True,model_raw_log_C_GPU_reads=0));until=time.monotonic()+args.seconds;client=connect();ftp=client.open_sftp();cache={};last=None;closed=False
 def get(relative):
  rel=PurePosixPath(relative);need(not rel.is_absolute() and '..' not in rel.parts and rel.suffix=='.json','Own purpose JSON only');path=root+'/'+relative;remaining=until-time.monotonic()
  if remaining<=0:raise TimeoutError('Own JSON observation deadline reached')
  ftp.get_channel().settimeout(min(15.,remaining))
  try:
   st=ftp.stat(path);signature=(st.st_mtime,st.st_size)
   if path in cache and cache[path][0]==signature:return cache[path][1]
   with ftp.open(path,'rb') as stream:value=json.loads(stream.read())
   cache[path]=(signature,value);return value
  except FileNotFoundError:return None
 try:
  while time.monotonic()<until:
   meta={name:get(name) for name in ROOT_NAMES};case={name:get('cases/E0/'+name) for name in CASE_NAMES}
   try:names=ftp.listdir(root+'/cases/E0')
   except FileNotFoundError:names=[]
   case['ERROR_JSON']={name:get('cases/E0/'+name) for name in names if name.endswith('.json') and 'ERROR' in name}
   final=case['V2_FROZEN_EVAL_FINAL.json'];rows=meta['TERMINAL_ROWS.json'] or [];exit_scope=meta['PARENT_EXIT_SCOPE.json'] or {};outer=meta['OUTER_OWNER_WAIT_ACTUAL.json'];parent_final=meta['E0_SINGLE_FROZEN_PARENT_FINAL.json'] or {};identity=meta['PARENT_STARTED.json'] or {}
   qualified=bool(outer and outer.get('original_owner_reaped') is True and outer.get('actual_wait_returncode')==0 and outer.get('original_owner_pid')==identity.get('pid') and exit_scope.get('all_own_children_waited') is True and exit_scope.get('original_single_GPU_private_EX_released') is True and exit_scope.get('original_global_finite_EX_released') is True and exit_scope.get('GPU_settled') is True and exit_scope.get('errors')==[] and parent_final.get('all_E0_actual_execution_complete') is True and len(rows)==1 and rows[0].get('role')=='E0' and rows[0].get('returncode')==0 and rows[0].get('actual_waited') is True and rows[0].get('passed_execution') is True and (rows[0].get('semantic_qualification') or {}).get('qualified') is True and not case['ERROR_JSON'] and meta['PARENT_ORIGINAL_ERROR.json'] is None)
   value=dict(epoch=time.time(),root=root,metadata=meta,cases={'E0':case},execution_qualified=qualified,skill_grader=None,full_skill_graduation=None,normal_metrics=normal_metrics(final),only_own_JSON_read=True,models_raw_logs_C_GPU_reads=0,qualification_scope='ACTUAL_WAIT_FINAL_INTENT_ERROR_AND_RESOURCE_CLOSE_CONJUNCTION_NOT_RC0_ALONE')
   put(out/'LATEST_METADATA.json',value);token=json.dumps(dict(ready=case['WORKER_SCENE_READY.json'] is not None,started=case['WORKER_EVAL_STARTED.json'] is not None,final=final is not None,exit=bool(exit_scope),outer=outer,qualified=qualified,errors=list(case['ERROR_JSON'])),sort_keys=True)
   if token!=last:print(token,flush=True);last=token
   if outer is not None and (meta['PARENT_EXIT_SCOPE.json'] is not None or outer['actual_wait_returncode']!=0):
    value['closed']=True;value['all_selected_execution_qualified']=qualified;value['skill_graduation_not_claimed']=True;put(out/'CLOSED_RESULT.json',value);put(D/'E0_SINGLE_FROZEN_CLOSED_RESULT_PATH.json',dict(path=str(out/'CLOSED_RESULT.json'),root=root));print(json.dumps(dict(closed_result=str(out/'CLOSED_RESULT.json'),execution_qualified=qualified,skill_grader=None,full_skill_graduation=None,normal_metrics=value['normal_metrics'])),flush=True);closed=True;break
   time.sleep(min(15,max(0,until-time.monotonic())))
  if not closed:raise TimeoutError('Own E0 eval metadata observation bound; no extension, retry or foreign action')
 finally:ftp.close();client.close()

if __name__=='__main__':main()
