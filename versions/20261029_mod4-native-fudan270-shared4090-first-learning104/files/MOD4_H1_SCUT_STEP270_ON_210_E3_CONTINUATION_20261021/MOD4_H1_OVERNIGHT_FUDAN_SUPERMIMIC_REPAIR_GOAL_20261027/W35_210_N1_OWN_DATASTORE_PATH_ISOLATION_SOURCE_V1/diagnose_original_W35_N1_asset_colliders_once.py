"""One original W35 environment, no checkpoint/model/actor or learning call."""
from pathlib import Path
import argparse,json,os,runpy,sys,time,traceback

def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);a=p.parse_args();J=a.job_root.resolve()
 def put(n,v):
  with (J/n).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
 K=J/'kit_isolation';assert not K.exists();K.mkdir()
 for name in ('data','DerivedDataCache'):(K/name).mkdir()
 with (K/'data/user.config.json').open('x') as f:f.write('{}')
 os.environ['MOD4_W35_OWN_KIT_STORAGE_ROOT']=str(K)
 original=json.loads((J/'original_run_manifest.json').read_bytes())
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 env={k:str(v) for k,v in original['env'].items() if k not in ('RM_RESCUE_STOP_FILE','RM_RESCUE_DEADLINE')}
 env.update(RM_MOD4_USD=str(J/'runtime/assets/robot.usd'),RM_RESCUE_STOP_FILE=str(J/'UNUSED_STOP.json'),RM_RESCUE_DEADLINE=str(time.time()+180))
 os.environ.update(env);os.environ['MOD4_RESUME_QUEUE_CONTROL_US']='20000'
 mod=J/'runtime/isaac/mod4';sys.path[:0]=[str(J/'lib'),str(mod),str(J/'runtime')]
 entry=mod/'train_e1_retention_named_owned_resume_ppo.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','1','--seed','20260928','--steps_per_env','24','--learning_rate','.00011390625000000003','--log_root',str(J/'logs'),'--run_name','W35_N1_ASSET_ONLY_NO_MODEL','--additional_iterations','1']
 ns=None;real=None
 try:
  import zonglin2_app_launcher as owned_launcher
  assert Path(owned_launcher.__file__).resolve()==J/'lib/zonglin2_app_launcher.py'
  ns=runpy.run_path(str(entry),run_name='W35_original_N1_asset_diagnostic_only')
  import mild_dr,carb
  from omni.physx.bindings import _physx
  settings=carb.settings.get_settings();config=[]
  keys=('/UJITSO/datastore/localCachePath','/UJITSO/datastore/allowLocalDataStore','/UJITSO/datastore/allowHubDataStore','/UJITSO/datastore/allowGRPCDataStore','/UJITSO/datastore/grpcDnsName','/app/userConfigPath','/physics/cooking/ujitsoCollisionCooking','/physics/cooking/ujitsoRemoteCacheEnabled','/persistent/physics/cooking/ujitsoCookingMaxProcessCount')
  actual={key:settings.get(key) for key in keys}
  put('N1_ACTUAL_OWN_KIT_AND_DATASTORE_PATHS_BEFORE_ENV.json',dict(epoch=time.time(),values={key:repr(value) for key,value in actual.items()},expected_cache=str(K/'DerivedDataCache'),expected_user_config=str(K/'data/user.config.json'),source_user_config_new_empty_owned_file=True,old_effective_datastore_path_was_not_collected=True,no_physics_or_cooking_boolean_written=True))
  assert Path(actual['/UJITSO/datastore/localCachePath']).resolve()==K/'DerivedDataCache'
  assert Path(actual['/app/userConfigPath']).resolve()==K/'data/user.config.json'
  assert actual['/physics/cooking/ujitsoCollisionCooking'] is True and actual['/physics/cooking/ujitsoRemoteCacheEnabled'] is False and actual['/persistent/physics/cooking/ujitsoCookingMaxProcessCount']==16
  assert not actual['/UJITSO/datastore/grpcDnsName'] and not actual['/UJITSO/datastore/allowHubDataStore'], 'Local-path test cannot claim isolation while an external datastore is selected'
  for name in sorted(dir(_physx)):
   if name.startswith('SETTING_') and any(s in name for s in ('CACHE','COOK','DATASTORE')):
    key=getattr(_physx,name)
    if isinstance(key,str):config.append(dict(exported_constant=name,key=key,value=repr(settings.get(key))))
  put('ACTUAL_EXPORTED_PHYSX_CACHE_COOKING_SETTINGS_READONLY.json',dict(epoch=time.time(),values=config,no_setting_written=True,project_environment={k:os.environ.get(k) for k in ('HOME','TMPDIR','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','CUDA_CACHE_PATH')}))
  old=mild_dr.MildDR.__init__
  def observed(self,cfg,env):
   try:return old(self,cfg,env)
   except BaseException:
    tb=sys.exc_info()[2];scope=None
    while tb:
     if tb.tb_frame.f_code is old.__code__:scope=tb.tb_frame.f_locals
     tb=tb.tb_next
    row=dict(epoch=time.time(),original_exception=traceback.format_exc(),original_assertion_unchanged=True,extra_GPU_shape_queries=0)
    if scope is not None:
     robot=scope.get('robot');row['counts_already_computed_by_original_MildDR']=scope.get('counts');row['wheel_shapes_already_computed']=getattr(self,'wheel_shapes',None)
     if robot is not None:row.update(body_names=list(robot.body_names),link_paths=robot.root_view.link_paths,articulation_max_shapes=robot.root_view.max_shapes)
    put('ORIGINAL_MILD_DR_ALREADY_COMPUTED_SHAPE_EVIDENCE.json',row)
    raise
  mild_dr.MildDR.__init__=observed
  # build_env only: original main/runner/checkpoint/load/learn are never called.
  real=ns['build_env']()
  put('N1_ORIGINAL_ENV_BUILD_PASSED.json',dict(epoch=time.time(),passed=True,num_envs=real.num_envs,physics_dt=real.physics_dt,step_dt=real.step_dt,decimation=real.cfg.decimation,original_wheel_shapes=list(real._mild_dr.wheel_shapes),no_model_actor_optimizer_or_policy_control=True))
 except BaseException:
  put('N1_ORIGINAL_EXCEPTION_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),traceback=traceback.format_exc(),no_model_actor_optimizer_or_policy_control=True))
  raise
 finally:
  try:
   files=[];total=0
   for q in sorted((K/'DerivedDataCache').rglob('*')):
    if not q.is_file():continue
    assert q.resolve().is_relative_to(K/'DerivedDataCache') and not q.is_symlink();total+=1
    if len(files)<64:files.append(dict(relative=q.relative_to(K).as_posix(),bytes=q.stat().st_size))
   put('N1_OWN_NEW_DATASTORE_FILE_METADATA_BEFORE_CLOSE.json',dict(epoch=time.time(),new_owned_cache_only=True,own_cache_file_count=total,first64_metadata=files,metadata_truncated=total>64,cache_contents_not_read=True,old_cache_not_read_deleted_or_changed=True,successful_environment_not_proof_of_unique_root_cause=True))
  except BaseException:put('N1_OWN_CACHE_METADATA_ORIGINAL_ERROR.json',dict(epoch=time.time(),traceback=traceback.format_exc()))
  put('N1_APP_CLOSING.json',dict(epoch=time.time()))
  if ns is not None:ns['app'].close()
if __name__=='__main__':main()
