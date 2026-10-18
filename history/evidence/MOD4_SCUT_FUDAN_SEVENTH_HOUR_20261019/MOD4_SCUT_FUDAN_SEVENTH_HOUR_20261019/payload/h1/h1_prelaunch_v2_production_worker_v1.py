"""Prepared only: requires a new actual original-owner GO and admitted native source.

Never launches a native case or learns without the exact bounded H1 grant.
"""
from pathlib import Path
import os,sys,argparse,json,time,hashlib,traceback,runpy
B=Path(__file__).resolve().parent;J=B/'job0'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--phase',choices=('precheck128','precheck20k','production'),required=True);args=p.parse_args();phase=args.phase;task=json.loads((J/'TASK.json').read_bytes());go=json.loads((B/('GO_'+phase.upper()+'.json')).read_bytes());assert go['actual_H1_prelaunch_v2_scope_admitted'] and go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300 and go['save_deadline']<go['nominal_end_epoch'];assert time.time()<go['save_deadline'];assert go['source_SHA']==task['source_SHA'];src=J/'source/H1_closed_hour74.pt';assert H(src)==go['source_SHA'];assert not (J/phase).exists();out=J/phase;out.mkdir();fresh=phase=='precheck128';N=128 if fresh else 20000
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 original=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in original.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_RESCUE_STOP_FILE=str(out/'STOP_AFTER_SAVE.json'),OWN_E2_H1_KIND=task['kind'])
 sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4')];entry=J/'runtime/isaac/mod4'/('train_H1_fresh128_preflight_v1.py' if fresh else 'train_H1_ground_prelaunch_fullstate_v2.py');sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs',str(N),'--seed','20260928','--steps_per_env','24','--learning_rate','.0001','--save_interval','25','--init_checkpoint',str(src),'--log_root',str(out/'logs'),'--run_name','H1_FLAT_PUBLIC_REQUEST_'+phase,'--additional_iterations','100000'];ns=runpy.run_path(str(entry),run_name='owned_H1_learner_config')
 import torch,rescue_training
 from spring_pressure_checkpoint import exact
 from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe
 class OwnSavedStop(Exception):pass
 def learn(runner,n,log_dir):
  env=runner.env.unwrapped;runner.logger.writer=None;s=torch.load(src,map_location='cpu',weights_only=False)
  for k,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,s[k]),k
  assert runner.alg.__class__.__module__=='owned_h1_public4_mean_overflow_ppo_v2';from h1_public4_mean_overflow_loss_v2 import COEFFICIENT,ACTION_BOUND;assert COEFFICIENT==.001 and ACTION_BOUND==6.
  assert int(env._sim_step_counter)==0 and float(os.environ['RM_JUMP_SCRIPT_PROB'])==0;steps={int(v['step']) for v in s['optimizer_state_dict']['state'].values()};assert steps=={665500};assert not env.h1_phase.age_control.any();sdk=isolated_actual_SDK_dt_probe(env);oldsave=runner.save
  def save(path,updates,failed=False):
   path=Path(path);tmp=path.with_suffix('.pt.partial');oldsave(str(tmp));ck=torch.load(tmp,map_location='cpu',weights_only=False);ck['owned_H1_learning_task']=task;ck['owned_H1_phase']=phase;ck['owned_H1_completed_updates']=updates;ck['failed_partial_prefix']=failed;actual_steps=sorted({int(v['step']) for v in ck['optimizer_state_dict']['state'].values()})
   if not failed:assert actual_steps==[665500+updates*20]
   torch.save(ck,tmp);tmp.replace(path);row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),phase=phase,updates=updates,actual17Adam_steps=actual_steps,failed_partial_prefix=failed);put(out/('failed_prefix_complete.json' if failed else 'latest_complete.json'),row);return row
  zero=save(out/'own_H1_startup0.pt',0);put(out/'STARTUP_H1_SOURCE_ACTUAL.json',dict(epoch=time.time(),source_SHA=H(src),source_actor9_critic8_STD17Adam_exact=True,all17Adam665500=True,zero_clock=True,own_admitted_H1_checkpoint_phase_fullrestore=not fresh,fresh128_perenv_DR_explicit_not_full20k_restore=fresh,SDK_live_reward_probe=sdk,zero=zero))
  from h1_scut_fudan_jump_reward_v1 import loaded_recipe;scut=loaded_recipe(env);put(out/'SCUT_FUDAN_LOADED_REWARD_RECIPE_ACTUAL.json',scut)
  from h1_production_control_prefix_trace_v1 import H1ControlPrefixTrace
  trace=H1ControlPrefixTrace(runner,out/'control_prefix_raw');trace.install();completed=0;original_log=runner.logger.log
  def log(*aa,**kk):
   nonlocal completed
   original_log(*aa,**kk);completed+=1;put(out/'OWNED_MEAN_OVERFLOW_LOSS_CURRENT.json',dict(epoch=time.time(),completed=completed,candidate='public4_only_mean_overflow_v2_coefficient.001_clip6',last_batch=getattr(runner.alg,'owned_mean_overflow_last',None),STD_load_keep_learning_contract_LR_and_physics_unchanged=True,environment_reward_changed_H1_SCUT_Fudan=True));from own_H1_storage_finite_guard_v1 import should_save_stop
   import shutil
   own_storage_stop=should_save_stop(phase,completed,shutil.disk_usage(B).free)
   if own_storage_stop:put(out/'OWN_STORAGE_OR_UPDATE_BOUND_SAVED_STOP_ACTUAL.json',dict(epoch=time.time(),completed=completed,free_bytes=shutil.disk_usage(B).free,max_completed_updates=None,reserve8GiB=True,no_reward_or_learning_input_change=True))
   stop=own_storage_stop or (phase=='precheck128' and completed>=2) or (phase=='precheck20k' and completed>=4) or time.time()>=go['save_deadline'] or (out/'STOP_AFTER_SAVE.json').exists() or (Path(log_dir)/'STOP_AFTER_SAVE').exists()
   scut_last=getattr(env,'_h1_scut_reward_last',None);put(out/'SCUT_FUDAN_JUMP_REWARD_CURRENT.json',dict(epoch=time.time(),completed=completed,active_rows=int(scut_last['active'].sum()),airborne_rows=int((scut_last['active']&scut_last['airborne']).sum()),unweighted_rate_means={k:float(v.mean()) for k,v in scut_last['terms'].items()},not_skill_or_final_model_audit=True)) if scut_last is not None else None
   if completed==1 or completed%25==0 or stop:put(out/'PPO_POSITIVE_CURRENT.json',save(out/('model_update'+str(completed)+'.pt'),completed))
   if stop:raise OwnSavedStop()
  runner.logger.log=log
  try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)
  except OwnSavedStop:pass
  except BaseException:
   error=traceback.format_exc();put(out/'LEARN_ORIGINAL_ERROR_BEFORE_SAVE.json',dict(epoch=time.time(),error=error,complete_updates=completed))
   try:save(out/'own_failed_valid_prefix.pt',completed,failed=True)
   except BaseException:put(out/'FAILED_PREFIX_SAVE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),partial_file_retained=True))
   raise
  finally:trace.persist()
  row=json.loads((out/'latest_complete.json').read_bytes());assert row['updates']>0
  if phase=='precheck128':assert row['updates']==2
  if phase=='precheck20k':assert row['updates']==4
  put(out/'FINAL.json',dict(epoch=time.time(),passed=True,final=row,discarded_prechecks=phase!='production',not_frozen_jump_skill_pass=True))
 rescue_training.learn=learn
 try:ns['main']()
 except BaseException:put(out/'ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc(),no_auto_retry=True));raise
 finally:put(out/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  try:put(B/('H1_PHASE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),no_retry=True))
  except BaseException:pass
  raise
