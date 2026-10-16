"""New CURB35 only: discarded128x2 precheck or20k native, discarded4, then production."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
B=Path(__file__).resolve().parent;J=B/'job0';TASK=json.loads((J/'TASK_CURB35.json').read_bytes());RUN=None
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,x):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(x,indent=2));q.replace(p)
def main():
 global RUN
 p=argparse.ArgumentParser();p.add_argument('--mode',choices=('precheck128','native20k_then_production'),required=True);a=p.parse_args();small=a.mode=='precheck128';RUN=J/a.mode;RUN.mkdir();source=J/'source/CURB140.pt';assert H(source)==TASK['source_SHA'];manifest=json.loads((J/'original_run_manifest.json').read_bytes())
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ.update({k:str(v) for k,v in manifest['env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')});os.environ['RM_MOD4_USD']=str(J/'assets/robot.usd');os.environ['RM_RESCUE_STOP_FILE']=str(RUN/'STOP_AFTER_SAVE.json')
 sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4')];entry=J/'runtime/isaac/mod4'/('train_curb35_fresh128_ppo.py' if small else 'train_curb35_resume_ppo.py');N=128 if small else 20000
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs',str(N),'--seed','20260928','--steps_per_env','24','--learning_rate','0.0001','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(RUN/'logs'),'--run_name','CURB35_'+a.mode,'--additional_iterations','100000']
 ns=runpy.run_path(str(entry),run_name='owned_CURB35_config');import torch,numpy as np,rescue_training
 from spring_pressure_checkpoint import exact
 class SavedStop(Exception):pass
 def learn(runner,n,log_dir):
  env=runner.env.unwrapped;vec=runner.env;runner.logger.writer=None;ck=torch.load(source,map_location='cpu',weights_only=False)
  def source_exact():
   for key,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,ck[key]),key
  source_exact();trace_offset=0;trace_files=[]
  def flush(directory):
   nonlocal trace_offset
   directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);rows=env._retention_trace
   if rows:
    q=directory/('retention_prefix_'+str(trace_offset)+'_'+str(trace_offset+len(rows))+'.npz');assert not q.exists();np.savez_compressed(q,rows=np.stack(rows));trace_files.append(dict(path=str(q),bytes=q.stat().st_size,SHA=H(q),first=trace_offset,last=trace_offset+len(rows)));trace_offset+=len(rows);env._retention_trace=[];env._retention_trace_written=0
   put(directory/'RETENTION_COMMAND_ACTUAL.json',dict(epoch=time.time(),actual_controls=trace_offset,files=trace_files,audit=env.command_manager.get_term('twist').audit_retention()))
  env.write_retention_trace=flush;oldsave=runner.save
  def save(path,phase,updates):
   path=Path(path);tmp=path.with_suffix(path.suffix+'.partial');oldsave(str(tmp));v=torch.load(tmp,map_location='cpu',weights_only=False);v['CURB35_training_phase']=phase;v['CURB35_task']=TASK;v['CURB35_reset_approach_axis']=env._curb35_approach_command_receipt;torch.save(v,tmp);tmp.replace(path);steps={int(z['step']) for z in v['optimizer_state_dict']['state'].values()};assert len(steps)==1
   row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),Adam_step=next(iter(steps)),updates=updates,phase=phase,controls=trace_offset+len(env._retention_trace),PPO_preflight_discarded=phase.startswith('precheck'),original20k_typed_DR_restore=not small)
   put(RUN/'latest_complete.json',row);return row
  if small:
   # Fresh128 D0-D7 instance explicitly differs from full20k state; model/Adam/std retained.
   runner.learn(num_learning_iterations=2,init_at_random_ep_len=True);row=save(RUN/'precheck128_discarded.pt','precheck128_discarded',2);assert row['Adam_step']==660440
   put(RUN/'FINAL.json',dict(epoch=time.time(),passed=True,discarded=True,no_production_credit=True,final=row));return
  receipts=sorted(Path(log_dir).glob('*STARTUP_VERIFIED.json'));assert len(receipts)>=8;save(RUN/'own_restored0.pt','native0',0)
  runner.alg.actor.eval();runner.alg.critic.eval();obs=vec.get_observations();tick=env._integrated_contact.tick;prefix=[];chunks=[]
  import warp as wp
  physical=[];cap=env._integrated_contact;oldcapture=cap.capture;oldterm=env.termination_manager.compute;observed={}
  def capture(dt):
   oldcapture(dt);raw=cap.sensor.contact_view.get_net_contact_forces(dt=cap.dt).view(wp.vec3);physical.append(wp.to_torch(raw).reshape(20000,2,3).detach().cpu().numpy().copy())
  def term(*aa,**kw):
   result=oldterm(*aa,**kw);observed.update(executed6=env.action_manager.action.detach().cpu().numpy().copy(),impulse=cap.impulse.detach().cpu().numpy().copy(),history=cap.history.detach().cpu().numpy().copy());return result
  cap.capture=capture;env.termination_manager.compute=term
  def persist():
   if not prefix:return
   q=RUN/('native_chunk_'+str(len(chunks))+'.npz');assert not q.exists();np.savez_compressed(q,**{k:np.stack([r[k] for r in prefix]) for k in prefix[0]});chunks.append(dict(path=str(q),bytes=q.stat().st_size,SHA=H(q)));prefix.clear()
  try:
   with torch.inference_mode():
    for i in range(144):
     x=obs['policy'];assert x.shape==(20000,35) and obs['critic'].shape==(20000,38);before=x.cpu().numpy().copy();critic=obs['critic'].cpu().numpy().copy();action=runner.alg.actor(obs,stochastic_output=False);assert torch.isfinite(action).all();raw=action.cpu().numpy().copy();physical.clear();obs,reward,done,info=vec.step(action);f=env._e1_pre_reset_frame
     prefix.append(dict(policy35=before,critic38=critic,raw6=raw,done=done.cpu().numpy().copy(),reward=reward.cpu().numpy().copy(),root13=f['root'].cpu().numpy().copy(),q30=f['q'].cpu().numpy().copy(),ground=f['ground'].cpu().numpy().copy(),normal=f['normal'].cpu().numpy().copy(),closure=f['closure'].cpu().numpy().copy(),mimic=f['mimic'].cpu().numpy().copy(),independent_query_error=np.asarray(f['independent_ground_error']),physical_wheel_force=np.stack(physical),**observed))
     if i%24==23:persist();assert not (Path(log_dir)/'STOP_AFTER_SAVE').exists() and not (RUN/'STOP_AFTER_SAVE.json').exists()
  finally:persist();flush(log_dir);save(RUN/'own_native_valid_prefix.pt','native0',0)
  source_exact();assert env._integrated_contact.tick-tick==576
  native=save(RUN/'own_native144.pt','native0',0);native.update(source_SHA=TASK['source_SHA'],callbacks=576,controls=144,warmup_controls=24,timed_controls=120,timed_callbacks=480,chunks=chunks,startup_receipts=[str(p) for p in receipts],GPU_UUID=str(torch.cuda.get_device_properties(0).uuid),no_optimizer_updates=True,physics_action_audit=env._physics_action_delay.audit(),chassis_PD_audit=env.chassis_pd_audit());put(RUN/'NATIVE144_COMPLETE.json',native)
  put(RUN/'FINAL.json',dict(epoch=time.time(),passed=True,native_only=True,actual_optimizer_updates=0));return
 rescue_training.learn=learn
 try:ns['main']()
 except BaseException:
  put(RUN/'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
 finally:put(RUN/'APP_CLOSING.json',dict(epoch=time.time(),mode=a.mode));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  if RUN and RUN.exists():put(RUN/'WORKER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True))
  raise
