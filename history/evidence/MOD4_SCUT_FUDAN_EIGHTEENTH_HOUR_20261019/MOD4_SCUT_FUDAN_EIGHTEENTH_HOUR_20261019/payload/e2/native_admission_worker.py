"""New phase in a fresh process; H1 is explicitly native-only, no teacher or jump PPO."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback,shutil
B=Path(__file__).resolve().parent
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--job',type=int,choices=(0,1),required=True);p.add_argument('--phase',choices=('native','precheck128','precheck20k','production'),required=True);args=p.parse_args();j=B/('job'+str(args.job));task=json.loads((j/'TASK.json').read_bytes());phase=args.phase;out=j/phase;out.mkdir();assert args.job==0 or phase=='native'
 source=j/'source/E2_closed_hour241.pt';assert H(source)==task['source_SHA'];N=128 if phase=='precheck128' else task['per_GPU_envs'];fresh=phase=='precheck128' or args.job==1
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 m=json.loads((j/'original_run_manifest.json').read_bytes());os.environ.update({k:str(v) for k,v in m['env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE','RM_SLOPE_INITIAL_ADMISSION')});os.environ.update(RM_MOD4_USD=str(j/'assets/robot.usd'),RM_RESCUE_STOP_FILE=str(out/'STOP_AFTER_SAVE.json'),RM_JUMP_SCRIPT_PROB='0',OWN_E2_H1_KIND=task['kind'],RM_MOD4_MAP='',RM_MOD4_TERRAIN='flat')
 sys.path[:0]=[str(B/'lib'),str(j/'runtime/isaac/mod4')];entry=j/'runtime/isaac/mod4'/('train_E2_H1_fresh_v1.py' if fresh else 'train_E2_full_resume_v1.py');sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs',str(N),'--seed','20260928','--steps_per_env','24','--learning_rate','.0001','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(out/'logs'),'--run_name',task['kind']+'_'+phase,'--additional_iterations','100000'];ns=runpy.run_path(str(entry),run_name='owned_new_phase_config')
 import torch,numpy as np,rescue_training
 from spring_pressure_checkpoint import exact
 class SavedStop(Exception):pass
 def learn(runner,n,log_dir):
  env=runner.env.unwrapped;vec=runner.env;runner.logger.writer=None;src=torch.load(source,map_location='cpu',weights_only=False)
  for key,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,src[key]),key
  assert int(env._sim_step_counter)==0 and float(os.environ['RM_JUMP_SCRIPT_PROB'])==0
  receipts=sorted(Path(log_dir).glob('*STARTUP_VERIFIED.json'));assert fresh or len(receipts)>=7
  term=env.command_manager.get_term('twist')
  if args.job==1:term.set_manual_evaluation_mode();term.vel_command_b.zero_();env._mod4_mode_bit=torch.full((N,),4,device=env.device,dtype=torch.long)
  oldsave=runner.save
  def save(path,updates):
   path=Path(path);tmp=path.with_suffix(path.suffix+'.partial');oldsave(str(tmp));v=torch.load(tmp,map_location='cpu',weights_only=False);v['owned_new_expert_task']=task;v['owned_phase']=phase;v['owned_phase_complete_updates']=updates;torch.save(v,tmp);tmp.replace(path);steps={int(x['step']) for x in v['optimizer_state_dict']['state'].values()};assert steps=={772320+updates*20};r=dict(epoch=time.time(),path=str(path),bytes=path.stat().st_size,SHA=H(path),phase=phase,updates=updates,Adam_step=next(iter(steps)),kind=task['kind']);put(out/'latest_complete.json',r);return r
  zero=save(out/'own_startup0.pt',0);put(out/'STARTUP_SOURCE_ACTUAL.json',dict(epoch=time.time(),source_SHA=H(source),model9_critic8_STD17Adam_literal_exact=True,zero_clock=True,full20k_original_D0_D7_restore=not fresh,fresh80_or128_perenv_not_full20k_restore=fresh,typed_receipts=[str(p) for p in receipts],zero=zero))
  if phase=='native':
   runner.alg.actor.eval();runner.alg.critic.eval();obs=vec.get_observations();tick=env._integrated_contact.tick;prefix=[];chunks=[];env._own_native_capture=True
   def persist():
    if not prefix:return
    q=out/('native_chunk_'+str(len(chunks))+'.npz');assert not q.exists();np.savez_compressed(q,**{k:np.stack([z[k] for z in prefix]) for k in prefix[0]});chunks.append(dict(path=str(q),bytes=q.stat().st_size,SHA=H(q)));prefix.clear()
   try:
    with torch.inference_mode():
     for i in range(144):
      x=obs['policy'];assert x.shape==(N,35) and obs['critic'].shape==(N,38);before=x.cpu().numpy().copy();critic=obs['critic'].cpu().numpy().copy();a=runner.alg.actor(obs,stochastic_output=False);raw=a.cpu().numpy().copy();env._own_raw_physical=[];obs,reward,done,info=vec.step(a);f=env._own_flat_frame;assert len(env._own_raw_physical)==4
      row={k:v.cpu().numpy().copy() for k,v in f.items()};row.update(policy35=before,critic38=critic,raw6=raw,done=done.cpu().numpy().copy(),reward=reward.cpu().numpy().copy(),physical_wheel_force=np.stack([v.cpu().numpy() for v in env._own_raw_physical]))
      if args.job==1:
       sensor=env.scene.sensors['full_robot_contact'];forces=sensor.data.net_forces_w;forces=forces.torch if hasattr(forces,'torch') else forces;row['full_robot_contact_force']=forces.cpu().numpy().copy();row['all_body_pos']=env.scene['robot'].data.body_pos_w.cpu().numpy().copy();row['all_body_quat']=env.scene['robot'].data.body_quat_w.cpu().numpy().copy()
      prefix.append(row)
      if i%24==23:persist();assert not (Path(log_dir)/'STOP_AFTER_SAVE').exists()
   finally:persist();env._own_native_capture=False;save(out/'own_native_valid_prefix.pt',0)
   assert env._integrated_contact.tick-tick==576
   for key,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,src[key]),key
   saved=save(out/'own_native144.pt',0);data=dict(epoch=time.time(),passed_physical_worker_not_CPU_admission=True,controls=144,warmup=24,timed=120,callbacks=576,num_envs=N,chunks=chunks,saved=saved,source_SHA=H(source),original_chassis_PD_audit=env.chassis_pd_audit(),original_action_queue_audit=env._physics_action_delay.audit(),fullstate_source_startup=not fresh,new_H1_operator_request_no_PPO=args.job==1,body_names=list(env.scene['robot'].body_names))
   if args.job==1:
    from pxr import Usd,UsdPhysics,UsdGeom
    cache=UsdGeom.BBoxCache(0.,[UsdGeom.Tokens.default_,UsdGeom.Tokens.proxy,UsdGeom.Tokens.render]);shapes=[]
    for prim in Usd.PrimRange(env.sim.stage.GetPrimAtPath('/World/envs/env_0/Robot'),Usd.TraverseInstanceProxies()):
     if prim.HasAPI(UsdPhysics.CollisionAPI):
      q=cache.ComputeWorldBound(prim).ComputeAlignedRange();shapes.append(dict(path=str(prim.GetPath()),type=prim.GetTypeName(),source_USD_world_min=list(q.GetMin()),source_USD_world_max=list(q.GetMax())))
    assert shapes;data.update(source_USD_colliders=shapes,actual_full_sensor_body_names=list(env.scene.sensors['full_robot_contact'].body_names),actual_cooked_shapeLocal_not_direct_read=True,not_airborne_or_jump_skill_pass=True,no_jump_reward_or_PPO_released=True)
   put(out/'NATIVE144_COMPLETE.json',data);put(out/'FINAL.json',dict(epoch=time.time(),passed=True,native_only=True,actual_optimizer_updates=0));return
  completed=0;oldlog=runner.logger.log
  go=json.loads((j/('GO_'+phase.upper()+'.json')).read_bytes());deadline=go['save_deadline']
  def log(*aa,**kk):
   nonlocal completed
   oldlog(*aa,**kk);completed+=1;stop=(shutil.disk_usage(B).free<8*1024**3) or (phase=='precheck128' and completed>=2) or (phase=='precheck20k' and completed>=4) or time.time()>=deadline or (out/'STOP_AFTER_SAVE.json').exists() or (Path(log_dir)/'STOP_AFTER_SAVE').exists()
   if completed==1 or completed%25==0 or stop:put(out/'PPO_POSITIVE_CURRENT.json',save(out/('model_update'+str(completed)+'.pt'),completed))
   if stop:raise SavedStop()
  runner.logger.log=log
  try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)
  except SavedStop:pass
  row=json.loads((out/'latest_complete.json').read_bytes());assert row['updates']>0
  if phase=='precheck128':assert row['updates']==2
  if phase=='precheck20k':assert row['updates']==4
  put(out/'FINAL.json',dict(epoch=time.time(),passed=True,final=row,prechecks_discarded=phase!='production'))
 rescue_training.learn=learn
 try:ns['main']()
 except BaseException:put(out/'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc()));raise
 finally:put(out/'APP_CLOSING.json',dict(epoch=time.time()));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  try:put(Path(__file__).resolve().parent/('WORKER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_automatic_retry=True))
  except BaseException:pass
  raise
