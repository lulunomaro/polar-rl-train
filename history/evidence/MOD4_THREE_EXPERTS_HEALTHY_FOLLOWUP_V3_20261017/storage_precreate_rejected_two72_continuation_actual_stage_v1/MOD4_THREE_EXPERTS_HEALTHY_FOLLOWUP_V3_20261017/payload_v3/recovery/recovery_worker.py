"""New recovery native336 and finite independent PPO, preserving full states and prefixes."""
from pathlib import Path
import argparse,os,sys,time,json,hashlib,traceback,runpy
B=Path(__file__).resolve().parent;J=B/'job0';OUT=None
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 global OUT
 p=argparse.ArgumentParser();p.add_argument('--job',type=int,default=0);p.add_argument('--phase',choices=['native','production'],required=True);a=p.parse_args();native=a.phase=='native';OUT=J/a.phase;OUT.mkdir();task=json.loads((J/'TASK.json').read_bytes());src=J/'source/E0_full_source.pt' if native else J/'native/own_native336.pt'
 if native:assert H(src)==task['source_SHA']
 else:assert H(src)==json.loads((J/'native/NATIVE336_COMPLETE.json').read_bytes())['SHA']
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','WORLD_SIZE','LOCAL_RANK','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 old=json.loads((J/'original_run_manifest.json').read_bytes())['env'];os.environ.update({k:str(v) for k,v in old.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(J/'assets/robot.usd'),RM_MOD4_TERRAIN='flat',RM_MOD4_MAP='',RM_JUMP_SCRIPT_PROB='0',RM_RESCUE_STOP_FILE=str(OUT/'STOP_AFTER_SAVE.json'),OWN_E2_H1_KIND='E3_PUBLIC_RECOVERY')
 sys.path[:0]=[str(B/'lib'),str(J/'runtime/isaac/mod4')];entry=J/'runtime/isaac/mod4/train_E3_fullstate_v1.py';sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','.0001','--save_interval','25','--init_checkpoint',str(src),'--log_root',str(OUT/'logs'),'--run_name','E3_'+a.phase,'--additional_iterations','100000'];ns=runpy.run_path(str(entry),run_name='owned_E3_config')
 import torch,numpy as np,rescue_training
 from spring_pressure_checkpoint import exact
 class SavedStop(Exception):pass
 def work(runner,n,log_dir):
  env=runner.env.unwrapped;vec=runner.env;runner.logger.writer=None;s=torch.load(src,map_location='cpu',weights_only=False)
  for k,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,s[k]),k
  assert int(env._sim_step_counter)==0 and env.num_envs==20000;receipts=list(Path(log_dir).glob('*STARTUP_VERIFIED.json'));assert set(['ACTION_DELAY_RESUME_STARTUP_VERIFIED.json', 'CHASSIS_PD_RESUME_STARTUP_VERIFIED.json', 'DELAY_RESUME_STARTUP_VERIFIED.json', 'E3_PHASE_FULLSTATE_RESUME_STARTUP_VERIFIED.json', 'GAS_DAMPING_RESUME_STARTUP_VERIFIED.json', 'SENSOR_RESUME_STARTUP_VERIFIED.json', 'SPRING_PRESSURE_RESUME_STARTUP_VERIFIED.json']).issubset({p.name for p in receipts});chunks=[];rows=[]
  def save(path,updates):
   tmp=path.with_suffix('.pt.partial');runner.save(str(tmp));v=torch.load(tmp,map_location='cpu',weights_only=False);v['E3_task']=task;v['E3_phase']=a.phase;v['E3_production_updates']=updates;torch.save(v,tmp);tmp.replace(path);steps={int(x['step']) for x in v['optimizer_state_dict']['state'].values()};assert steps=={647300+20*updates};row=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),updates=updates,Adam_step=next(iter(steps)),phase=a.phase);put(OUT/'latest_complete.json',row);return row
  def persist():
   if rows:
    q=OUT/('native_chunk_'+str(len(chunks))+'.npz');assert not q.exists();np.savez_compressed(q,**{k:np.stack([r[k] for r in rows]) for k in rows[0]});chunks.append(dict(path=str(q),bytes=q.stat().st_size,SHA=H(q)));rows.clear();put(OUT/'VALID_PREFIX_INDEX.json',dict(epoch=time.time(),chunks=chunks))
  from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe
  actual_dt=isolated_actual_SDK_dt_probe(env);put(OUT/'E3_ACTUAL_SDK_REWARD_DT_PROBE.json',actual_dt)
  zero=save(OUT/'own_startup0.pt',0);put(OUT/'SOURCE_TYPED_ZERO_CLOCK_ACTUAL.json',dict(epoch=time.time(),source_SHA=H(src),core_actor9_critic8_STD17Adam_literal_exact=True,startup=[dict(path=str(p),value=json.loads(p.read_bytes())) for p in receipts],own0=zero))
  if native:
   put(OUT/'GEOMETRY_AND_RESET_ACTUAL.json',dict(shapes=env.e3_shapes,body_names=env.e3_body_names,contact_names=env.e3_contact_names,witness_ids=env.e3_witness.cpu().tolist(),reset=env.e3_reset_receipt,actual_quaternion='XYZW',reference_plane_z0=True,not_cookedShapeLocal_or_hardware=True));runner.alg.actor.eval();runner.alg.critic.eval();obs=vec.get_observations();tick=env._integrated_contact.tick;env.e3_capture=True
   try:
    with torch.inference_mode():
     for i in range(336):
      x=obs['policy'];assert x.shape==(20000,35) and obs['critic'].shape==(20000,38);mode=torch.nn.functional.one_hot(env.recovery.mode(),7).to(x.dtype);assert torch.equal(x[:,28:35],mode);before=x.cpu().numpy().copy();critic=obs['critic'].cpu().numpy().copy();action=runner.alg.actor(obs,stochastic_output=False);raw=action.cpu().numpy().copy();env.e3_physical=[];obs,reward,done,info=vec.step(action);f=env.e3_frame;assert len(env.e3_physical)==4;row={k:v.cpu().numpy().copy() for k,v in f.items()};row.update(policy35=before,critic38=critic,raw6=raw,done=done.cpu().numpy().copy(),reward=reward.cpu().numpy().copy(),physical_wheel_force=np.stack([z['wheel_raw'].cpu().numpy() for z in env.e3_physical]),physical_full31_force=np.stack([z['all31_force'].cpu().numpy() for z in env.e3_physical]),witness_body_pos=np.stack([z['witness_body_pos'].cpu().numpy() for z in env.e3_physical]),witness_body_quat_xyzw=np.stack([z['witness_body_quat_xyzw'].cpu().numpy() for z in env.e3_physical]),witness_clear34=np.stack([z['witness_clear34'].cpu().numpy() for z in env.e3_physical]));rows.append(row);env.e3_physical=[]
      if i%6==5:persist();put(OUT/'CURRENT_ACTUAL.json',dict(epoch=time.time(),controls=i+1,callbacks=env._integrated_contact.tick-tick,optimizer_updates=0));assert not (OUT/'STOP_AFTER_SAVE.json').exists() and not (Path(log_dir)/'STOP_AFTER_SAVE').exists()
   finally:persist();env.e3_capture=False;save(OUT/'valid_prefix_fullstate.pt',0)
   assert env._integrated_contact.tick-tick==1344
   for k,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,s[k]),k
   last=save(OUT/'own_native336.pt',0);put(OUT/'NATIVE336_COMPLETE.json',dict(**last,source_SHA=task['source_SHA'],controls=336,callbacks=1344,chunks=chunks,optimizer_updates=0,original_chassis_audit=env.chassis_pd_audit(),action_delay=env._physics_action_delay.audit()));put(OUT/'FINAL.json',dict(epoch=time.time(),passed=True,native_only=True));return
  go=json.loads((J/'GO_PRODUCTION.json').read_bytes());assert go['source_SHA']==task['source_SHA'] and go['max_parent_seconds']==task['max_parent_seconds'] and go['exit_headroom_seconds']==300;deadline=go['save_deadline'];completed=0;oldlog=runner.logger.log
  def log(*aa,**kk):
   nonlocal completed
   oldlog(*aa,**kk);completed+=1;stop=time.time()>=deadline or (OUT/'STOP_AFTER_SAVE.json').exists() or (Path(log_dir)/'STOP_AFTER_SAVE').exists()
   if completed==1 or completed%25==0 or stop:put(OUT/'PPO_POSITIVE_CURRENT.json',save(OUT/('model_update'+str(completed)+'.pt'),completed))
   if stop:raise SavedStop()
  runner.logger.log=log
  try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)
  except SavedStop:pass
  finally:
   if completed:save(OUT/('final_valid_update'+str(completed)+'.pt'),completed)
  assert completed>0;put(OUT/'FINAL.json',dict(epoch=time.time(),passed=True,final=json.loads((OUT/'latest_complete.json').read_bytes()),not_recovery_skill_qualification=True))
 rescue_training.learn=work
 try:ns['main']()
 except BaseException:put(OUT/'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
 finally:put(OUT/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  if OUT and OUT.exists():put(OUT/'WORKER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True))
  raise
