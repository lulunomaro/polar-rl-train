"""SOURCEcandidate: fourE1finiteposttrain, originalfullrunner/restore/save/PPO.
H1excluded. ParentoriginalcanonicalownerONLY; noSDK/modelbeforeactualROOT/GO.
NotN80,notnewreward/STDreset/physics/capacity. NoimportsTorch/SDK atmoduleload.
"""
from pathlib import Path
import argparse,copy,hashlib,importlib,json,os,runpy,sys,time,traceback
from e1_posttrain_contract import KIND,ROLES,read_parent_receipts,source_Adam
from e1_posttrain_state_tools import exact_tree,live_core,install_complete_unknown_merge,install_published_save_receipts


def main():
 p=argparse.ArgumentParser();p.add_argument('--job-root',type=Path,required=True);p.add_argument('--task',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
 root=a.job_root.resolve();out=a.out.resolve();task=json.loads(a.task.read_bytes());ns=env=runner=cache=health=guard=None;completed=[0];records=[];published=[];loop_begun=False;saved_stop=False;result=None
 def put(name,value):
  target=out/name;assert target.resolve().is_relative_to(out)
  with target.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
 # No parentTask/admission -> failurebefore evenmodel/SDK imports.
 admission,go=read_parent_receipts(root,task)
 assert task['canonical'] in ROLES and task['canonical']!='H1_normal'
 out.mkdir(parents=True,exist_ok=False)
 put('POSTTRAIN_TASK_BINDING_VERIFIED_BEFORE_MODEL_SDK.json',dict(kind=KIND,run_id=task['run_id'],role_key=task['role_key'],canonical=task['canonical'],root_admission_SHA=task['root_admission_SHA'],source_SHA=task['source_SHA'],source_read_count=0,SDK_constructed=False,parent_original_canonical_binding=admission['canonical_binding'],child_canonical_reads_or_writes=0))
 try:
  meta=json.loads((root/'E1_CANONICAL_SOURCE_METADATA.json').read_bytes());CPUraw=(root/'CPU_FOUR_LEAF_ACTUAL_COMPLETE.json').read_bytes();CPU=json.loads(CPUraw)
  assert meta['canonical']==task['canonical'] and CPU['passed'] and CPU['canonical']==task['canonical'] and CPU['original_source']['SHA']==meta['original_source_SHA']==task['original_source_SHA']
  mod=root/'runtime/isaac/mod4';source=Path(task['selected_typed_source_path']).resolve();assert str(source)==str(Path(task['model_path']).resolve())
  assert not out.is_relative_to(source) and not source.is_relative_to(out)
  for name in list(os.environ):
   if name.startswith('RM_') or name in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[name]
  os.environ.update({k:str(v) for k,v in meta['original_env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')})
  os.environ.update(RM_KEEP_STD='1',RM_PHYSICS_DT_S='.0025',RM_SOLVER_POS='32',RM_SOLVER_VEL='4',RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',MOD4_RESUME_QUEUE_CONTROL_US='20000',RM_RESCUE_DEADLINE=str(go['save_deadline']),RM_RESCUE_STOP_FILE=str(task['rescue_stop_file']),MOD4V1_E1_ACTUAL_JOB_ROOT=str(root),MOD4V1_E1_KIT_STORAGE_ROOT=str(root/'kit_isolation'),PYTHONDONTWRITEBYTECODE='1')
  # SourceoriginalN20kcfg, NO N80 smallmemorypreset. Parentstagesnewunusedroot.
  storage=root/'kit_isolation';storage.mkdir(exist_ok=False);(storage/'data').mkdir();(storage/'DerivedDataCache').mkdir();(storage/'data/user.config.json').write_text('{}')
  sys.path[:0]=[str(mod),str(root/'runtime'),str(root/'producer/lib'),str(root/'lib'),str(root)]
  from mod4v1_fresh_dr_guard import bind_before_task_import,verify_task_module,configure_new_task,FreshDRNominalGuard
  from e1_pinned_source_v1 import PinnedSourceE1,selected_source,runner_source_load_scope
  identity=bind_before_task_import(Path(task['asset_dir']))
  import torch
  cache=PinnedSourceE1(torch,source,task['source_SHA'],task['source_bytes'],role=meta['role'],original_source_SHA=task['original_source_SHA'],CPU_receipt_SHA=hashlib.sha256(CPUraw).hexdigest())
  ck=cache.state;immutable_source=copy.deepcopy(ck);savedLR=ck['optimizer_state_dict']['param_groups'][0]['lr'];savedIteration=int(ck['iter']);steps={int(x['step']) for x in ck['optimizer_state_dict']['state'].values()}
  assert savedIteration==task['source_iteration'] and savedLR==task['source_LR'] and steps=={source_Adam(task)} and len(ck['optimizer_state_dict']['state'])==17
  entry=mod/meta['entry'];sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed',str(task['seed']),'--steps_per_env','24','--learning_rate',str(savedLR),'--init_checkpoint',str(source),'--log_root',str(out),'--run_name',task['run_id'],'--additional_iterations',str(task['additional_updates']),'--save_interval',str(task['save_interval'])]
  ns=runpy.run_path(str(entry),run_name='E1_original_full20k_posttrain_source_no_entry_main')
  import mod4_task
  verify_task_module(mod4_task,identity);assert mod4_task.POLICY_HZ==50 and mod4_task.DECIMATION==8
  oldcfg=ns['Mod4EnvCfg'];factory=ns['build_env']
  def cfg():
   c=oldcfg();c.terminations.mimic.params={**c.terminations.mimic.params,'threshold':.01};configure_new_task(c,identity)
   assert c.sim.dt==.0025 and c.decimation==8 and c.sim.physics.solver_type==1
   assert c.scene.robot.spawn.articulation_props.solver_position_iteration_count==32 and c.scene.robot.spawn.articulation_props.solver_velocity_iteration_count==4
   return c
  factory.__globals__['Mod4EnvCfg']=cfg
  with selected_source(cache):
   env=factory();guard=FreshDRNominalGuard(env,identity,torch_module=torch,tensor_converter=importlib.import_module('mild_dr').tensor);env._mod4v1_nominal_guard=guard
   assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==.02 and env.command_manager.get_term('twist')._dt==.02
   from e1_terrain_training_health import E1TerrainTrainingHealth
   health=E1TerrainTrainingHealth(env,out)  # Originaltrainer samehealthbeforevec/runner.
   rcfg=ns['runner_config']();vec=ns['RslRlVecEnvWrapper'](env,clip_actions=rcfg.clip_actions);rcfg=ns['handle_deprecated_rsl_rl_cfg'](rcfg,ns['metadata'].version('rsl-rl-lib'));runner=ns['OnPolicyRunner'](vec,rcfg.to_dict(),log_dir=str(out),device=rcfg.device)
   with runner_source_load_scope():runner.load(str(source))
   helper=importlib.import_module(meta['restore_helper'])
   with guard.around_original_fullstate_restore():helper.resume_e1_new_episode(runner,env,str(source),str(out))
   assert runner.current_learning_iteration==savedIteration and runner.alg.learning_rate==savedLR
   assert exact_tree(torch,runner.alg.actor.state_dict(),ck['actor_state_dict']) and exact_tree(torch,runner.alg.critic.state_dict(),ck['critic_state_dict']) and exact_tree(torch,runner.alg.optimizer.state_dict(),ck['optimizer_state_dict'])
   obs=runner.env.get_observations();guard.check_observations(obs);assert guard.reset_calls==1
   audit_before=guard.verify_live_parameters();assert audit_before['actual_parameters_pass'];before=live_core(torch,runner)
   helper.install_e1_save_contract(runner,env)
   records=install_complete_unknown_merge(runner,env,cache,torch,out)
   import rescue_training
   # Originalatomiccomplete-save andcheckpoint-safe stop install once.
   rescue_training.install(runner,str(out))
   published=install_published_save_receipts(runner,env,cache,torch,out,records,rescue_training.SavedStop,put,completed)
   old_update=runner.alg.update
   def observed_original_update(*aa,**kk):
    assert completed[0]<task['additional_updates'],'Originalrunnerexceededfiniteadditionalupdates'
    value=old_update(*aa,**kk);completed[0]+=1
    with (out/'ACTUAL_ORIGINAL_PPO_UPDATE_EVENTS.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(dict(epoch=time.time(),completed_actual_updates=completed[0],actual_core=live_core(torch,runner),canonical_accounting='Parentoriginalownercharge_values_only'))+'\n')
    return value
   runner.alg.update=observed_original_update
   put('POSTTRAIN_FULL20K_FULLSTATE_BEFORE_LEARN.json',dict(kind=KIND,run_id=task['run_id'],canonical=task['canonical'],role_key=task['role_key'],source_SHA=cache.SHA,source_cache=cache.receipt(),live_actor_critic_STD17Adam_LR_iter_exact=True,actual_core=before,nominal_guard=guard.receipt(),actual_parameter_audit=audit_before,original_helper_receipts=[p.name for p in out.glob('*STARTUP_VERIFIED.json')],all20k_source_history_RNG_queue_restored_by_original_owners=True,helper_startup_fresh_reset_count=guard.reset_calls,source20k_sliced=False,N80_smallcapacity_applied=False,live_training_uses_original_PPO=True,no_STD_reopen_or_manual_STDfreeze=True,unknownroot_preserve_fullsave_installed=True,requested_max_updates=task['additional_updates'],parent_deadline=go['save_deadline'],parent_stop_file=task['rescue_stop_file'],rank0_only20k_notall60k=task['canonical']=='CURB_PROTECTED878',protected_historical_rankcontract_preserved=True,canonical_child_reads_writes=0))
   start_tick=int(env._sim_step_counter);start_contact=int(env._integrated_contact.tick);start_feedback=int(env._feedback_100hz_tick);delay_before=dict(env._physics_action_delay.calls)
   try:
    if time.time()>=go['save_deadline'] or Path(task['rescue_stop_file']).exists():saved_stop=True
    else:
     loop_begun=True
     # ThisisEXACTcallusedbyrescue_training.learnafteritsinstall; avoidsdoubleinstall.
     runner.learn(num_learning_iterations=task['additional_updates'],init_at_random_ep_len=True)
   except rescue_training.SavedStop:saved_stop=True
   finally:runner.alg.update=old_update
   assert 0<=completed[0]<=task['additional_updates'];guard.assert_new_nominals_unchanged();health_result=health.write();audit_after=guard.verify_live_parameters();assert audit_after['actual_parameters_pass']
   actual_controls=health.steps;assert int(env._sim_step_counter)-start_tick==int(env._integrated_contact.tick)-start_contact==actual_controls*8
   assert int(env._feedback_100hz_tick)-start_feedback==actual_controls*2
   assert {k:env._physics_action_delay.calls[k]-delay_before[k] for k in ('legs','wheels')}==dict(legs=actual_controls*8,wheels=actual_controls*8)
   assert exact_tree(torch,cache.state,immutable_source)
   final_path=out/('model_posttrain_final_complete_U'+str(completed[0]).zfill(3)+'.pt')
   try:runner.save(str(final_path))
   except rescue_training.SavedStop:saved_stop=True
   assert published and published[-1]['checkpoint']==str(final_path.resolve())
   result=dict(kind=KIND,canonical=task['canonical'],role_key=task['role_key'],run_id=task['run_id'],original_selected_source_SHA=cache.SHA,completed_actual_updates=completed[0],requested_max_additional_updates=task['additional_updates'],completed_requested_update_window=completed[0]==task['additional_updates'],parent_saved_stop_boundary=saved_stop,actual_controls=actual_controls,physics_callbacks=actual_controls*8,feedback_samples=actual_controls*2,source_cache=cache.receipt(),before_live_core=before,after_live_core=live_core(torch,runner),new_fullstate_checkpoint=published[-1],all_complete_checkpoints=published,selected_source_immutable_exact=True,full20k_history_saved_and_original_unknownkeys_preserved=True,health=health_result,original_parameter_audit_after=audit_after,skill_graduated=False,next_action='FROZEN_OWN_ORIGINAL_SKILL_EVAL_AFTER_ENV_APPCLOSE_AND_PARENTWAIT; parentretainbest_or_nextnewwindowrollbackfullstate_keepallfailures',canonical_accounting='Parentoriginalcharge_valuescontinuesuntilSDKclosechildwaitterminal; nochildcanonicalwriter',actual_parent_wait_RC0='PARENT_TO_VERIFY')
   put('FINAL.json',result)
 except BaseException:
  error=dict(kind=KIND,run_id=task.get('run_id'),canonical=task.get('canonical'),error=traceback.format_exc(),completed_actual_updates=completed[0],model_or_SDK_preflight_passed=True,loop_begun=loop_begun,no_automatic_retry=True,parent_canonical_settlement_required=True)
  if cache is not None:error['source_cache']=cache.receipt()
  if runner is not None and loop_begun:
   try:
    with selected_source(cache):runner.save(str(out/'model_posttrain_error_boundary_complete.pt'))
    error['best_effort_complete_error_save']='PublishedownerrorcheckpointNotqualified'
   except BaseException:error['error_save_exception']=traceback.format_exc()
  put('ORIGINAL_POSTTRAIN_ERROR.json',error);raise
 finally:
  try:
   if health is not None:health.write()
   if cache is not None:put('SELECTED_SOURCE_FINAL_READ_COUNTS.json',cache.receipt())
  finally:
   try:
    if env is not None:put('PRE_CLOSE.json',dict(kind=KIND,run_id=task['run_id'],completed_actual_updates=completed[0],complete_checkpoints=len(published),calling_original_env_close=True));env.close();put('ENV_CLOSE_RETURNED.json',dict(closed=True))
   finally:
    if ns is not None:put('APP_CLOSING.json',dict(calling_original_App_close=True,actual_parent_wait_RC0_required=True));ns['app'].close()
if __name__=='__main__':main()
