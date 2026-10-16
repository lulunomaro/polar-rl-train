"""Fresh process only: reuse admitted native/prechecks, preserve zero-clock restore guard."""
from pathlib import Path
import hashlib,json,os,runpy,sys,time,traceback
B=Path(__file__).resolve().parent;J=B/'job0';RUN=J/'production_only'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(x,indent=2));q.replace(p)
def main():
 RUN.mkdir();task=json.loads((J/'TASK_CURB35.json').read_bytes());source=J/'source/CURB140.pt';assert H(source)==task['source_SHA'];prior=json.loads((B/'job0/native20k_then_production/INDEPENDENT_NATIVE_CPU_ADMITTED.json').read_bytes());assert prior['passed']
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 manifest=json.loads((J/'original_run_manifest.json').read_bytes());os.environ.update({k:str(v) for k,v in manifest['env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')});os.environ['RM_MOD4_USD']=str(J/'assets/robot.usd');os.environ['RM_RESCUE_STOP_FILE']=str(RUN/'STOP_AFTER_SAVE.json')
 sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4')];entry=J/'runtime/isaac/mod4/train_curb35_resume_ppo.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','0.0001','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(RUN/'logs'),'--run_name','CURB35_production_fresh_process_v2','--additional_iterations','100000'];ns=runpy.run_path(str(entry),run_name='owned_new_production_config');import torch,numpy as np,rescue_training
 from spring_pressure_checkpoint import exact
 class SavedStop(Exception):pass
 def learn(runner,n,log_dir):
  env=runner.env.unwrapped;runner.logger.writer=None;ck=torch.load(source,map_location='cpu',weights_only=False)
  for k,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,ck[k]),k
  receipts=sorted(Path(log_dir).glob('*STARTUP_VERIFIED.json'));assert len(receipts)>=8 and int(env._sim_step_counter)==0
  from curb35_checkpoint import current_state,identity
  assert identity(current_state(env))==identity(ck['E1_terrain_state'])
  trace_offset=0;trace_files=[]
  def flush(directory):
   nonlocal trace_offset
   directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);rows=env._retention_trace
   if rows:
    q=directory/('retention_prefix_'+str(trace_offset)+'_'+str(trace_offset+len(rows))+'.npz');assert not q.exists();np.savez_compressed(q,rows=np.stack(rows));trace_files.append(dict(path=str(q),bytes=q.stat().st_size,SHA=H(q),first=trace_offset,last=trace_offset+len(rows)));trace_offset+=len(rows);env._retention_trace=[];env._retention_trace_written=0
   put(directory/'RETENTION_COMMAND_ACTUAL.json',dict(epoch=time.time(),actual_controls=trace_offset,files=trace_files,audit=env.command_manager.get_term('twist').audit_retention()))
  env.write_retention_trace=flush;oldsave=runner.save
  def save(path,updates):
   path=Path(path);tmp=path.with_suffix(path.suffix+'.partial');oldsave(str(tmp));v=torch.load(tmp,map_location='cpu',weights_only=False);v['CURB35_training_phase']='production' if updates else 'production0';v['CURB35_task']=task;v['CURB35_reset_approach_axis']=env._curb35_approach_command_receipt;v['CURB35_source140_native_CPU_admitted_no_prechecks']=prior;torch.save(v,tmp);tmp.replace(path);steps={int(z['step']) for z in v['optimizer_state_dict']['state'].values()};assert steps=={672200+20*updates};row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),Adam_step=next(iter(steps)),updates=updates,phase=v['CURB35_training_phase'],controls=trace_offset+len(env._retention_trace),original20k_typed_DR_restore=True,not_reused_preflight_weights=True);put(RUN/'latest_complete.json',row);return row
  zero=save(RUN/'own_fresh_startup0.pt',0);put(RUN/'PRODUCTION_FRESH_ZERO_CLOCK_FULLRESTORE_ACTUAL.json',dict(epoch=time.time(),source_SHA=task['source_SHA'],zero_clock_guard_unmodified_passed=True,source_actor9_critic8_STD17Adam_literal_exact=True,source_episode_plus_one_and_original_typed_startup_receipts=[str(p) for p in receipts],current_new35_identity=identity(current_state(env)),same_admitted_native_backend_scope=True,own_zero_save=zero,no_native_or_prechecks_replayed=True))
  go=json.loads((B/'GO_PRODUCTION_ACTUAL.json').read_bytes());deadline=go['save_deadline'];assert go['source_SHA']==task['source_SHA'] and go['max_parent_seconds']==task['remaining_scope_cap_seconds'] and go['exit_headroom_seconds']==300;oldlog=runner.logger.log;completed=0
  def log(*aa,**kw):
   nonlocal completed
   oldlog(*aa,**kw);completed+=1;stop=time.time()>=deadline or (RUN/'STOP_AFTER_SAVE.json').exists() or (Path(log_dir)/'STOP_AFTER_SAVE').exists()
   if completed==1 or completed%25==0 or stop:put(RUN/'PPO_POSITIVE_CURRENT.json',save(RUN/('model_update'+str(completed)+'.pt'),completed))
   if stop:raise SavedStop()
  runner.logger.log=log
  try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)
  except SavedStop:pass
  finally:flush(log_dir)
  row=json.loads((RUN/'latest_complete.json').read_bytes());assert row['updates']>0;put(RUN/'FINAL.json',dict(epoch=time.time(),passed=True,final=row))
 rescue_training.learn=learn
 try:ns['main']()
 except BaseException:put(RUN/'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
 finally:put(RUN/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  if RUN.exists():put(RUN/'WORKER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True))
  raise
