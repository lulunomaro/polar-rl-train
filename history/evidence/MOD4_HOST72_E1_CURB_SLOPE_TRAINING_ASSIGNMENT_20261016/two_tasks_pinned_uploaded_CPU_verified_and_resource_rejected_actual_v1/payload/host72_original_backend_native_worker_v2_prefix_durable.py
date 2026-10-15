"""Own finite original-source 20k native/fullrestore; no optimizer step or learning."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
ROOT=Path('/home/lc01/Zonglin Li/zonglin2');BASE=ROOT/'tasks/MOD4_HOST72_E1_CURB_SLOPE_TRAINING_ASSIGNMENT_20261016'
def put(p,v):
 with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
def main():
 p=argparse.ArgumentParser();p.add_argument('--job',type=int,choices=(0,1),required=True);a=p.parse_args()
 j=BASE/('job'+str(a.job));out=j/'original_backend_native120_v2';out.mkdir()
 task=json.loads((j/'TASK_ASSIGNMENT.json').read_text());manifest=json.loads((j/'original_run_manifest.json').read_text())
 env=manifest['env'];assert all(k.startswith('RM_') for k in env)
 for k in list(os.environ):
  if k.startswith('RM_'):del os.environ[k]
 os.environ.update({k:str(v) for k,v in env.items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')})
 os.environ['RM_MOD4_USD']=str(j/'assets/robot.usd');os.environ['CUDA_VISIBLE_DEVICES']=task['GPU_UUID'];os.environ['RM_RESCUE_DEADLINE']=str(time.time()+720)
 os.environ['RM_RESCUE_STOP_FILE']=str(out/'STOP_AFTER_SAVE')
 os.environ['PYTHONPYCACHEPREFIX']=str(ROOT/'cache/pycache');os.environ['TORCH_EXTENSIONS_DIR']=str(ROOT/'cache/torch_extensions')
 sys.path.insert(0,str(ROOT/'tools'));m=j/'runtime/isaac/mod4';sys.path.insert(0,str(m))
 entry=m/'train_host72_backend_admission_v1.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','0.0001','--save_interval','25','--init_checkpoint',str(j/'source/source.pt'),'--log_root',str(out/'logs'),'--run_name','host72_original_backend_native120_v2','--additional_iterations','1']
 ns=runpy.run_path(str(entry),run_name='host72_configuration_only')
 import numpy as np,torch,rescue_training
 def finite(runner,n,log_dir):
  from spring_pressure_checkpoint import exact
  vec=runner.env;physical=vec.unwrapped;source=torch.load(j/'source/source.pt',map_location='cpu',weights_only=False)
  runner.logger.writer=None
  runner.alg.actor.eval();runner.alg.critic.eval()
  assert exact(runner.alg.actor.state_dict(),source['actor_state_dict']) and exact(runner.alg.critic.state_dict(),source['critic_state_dict'])
  assert exact(runner.alg.optimizer.state_dict(),source['optimizer_state_dict'])
  runner.save(str(out/'own_restored0.pt'))
  obs=vec.get_observations();rows=[];before_tick=physical._integrated_contact.tick
  try:
   with torch.inference_mode():
    for tick in range(120):
     assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38)
     action=runner.alg.actor(obs,stochastic_output=False)
     assert action.shape==(20000,6) and torch.isfinite(action).all()
     policy=obs['policy'].detach().cpu().numpy().copy();raw=action.detach().cpu().numpy().copy()
     obs,reward,done,info=vec.step(action)
     frame=physical._e1_pre_reset_frame
     rows.append(dict(policy35=policy,raw6=raw,root=frame['root'].cpu().numpy().copy(),q30=frame['q'].cpu().numpy().copy(),closure=frame['closure'].cpu().numpy().copy(),mimic=frame['mimic'].cpu().numpy().copy(),done=done.cpu().numpy().copy(),reward=reward.cpu().numpy().copy()))
     if (out/'STOP_AFTER_SAVE').exists():raise RuntimeError('Own original health requested save-stop during native; preserve partial prefix')
  finally:
   if rows:
    prefix=out/('NATIVE_VALID_PREFIX_'+str(len(rows))+'.npz')
    np.savez_compressed(prefix,**{k:np.stack([r[k] for r in rows]) for k in rows[0]})
   runner.save(str(out/'own_native_prefix_complete.pt'))
  raw_path=out/'NATIVE120_ORIGINAL_FULL_PHYSICAL.npz';np.savez_compressed(raw_path,**{k:np.stack([r[k] for r in rows]) for k in rows[0]})
  assert physical._integrated_contact.tick-before_tick==480
  assert exact(runner.alg.actor.state_dict(),source['actor_state_dict']) and exact(runner.alg.critic.state_dict(),source['critic_state_dict']) and exact(runner.alg.optimizer.state_dict(),source['optimizer_state_dict'])
  runner.save(str(out/'own_native120.pt'))
  saved=torch.load(out/'own_native120.pt',map_location='cpu',weights_only=False)
  assert exact(saved['actor_state_dict'],source['actor_state_dict']) and exact(saved['critic_state_dict'],source['critic_state_dict']) and exact(saved['optimizer_state_dict'],source['optimizer_state_dict'])
  put(out/'NATIVE120_DATA_COMPLETE_ACTUAL.json',dict(epoch=time.time(),pid=os.getpid(),GPU_UUID=task['GPU_UUID'],original_source_SHA=task['original_source']['sha256'],controls=120,num_envs=20000,callbacks=480,optimizer_updates=0,actor_critic_STD_17Adam_source_exact=True,
   original_geometry_restore_contract_reused=True,new_task_axis_admitted=False,raw=dict(path=str(raw_path),bytes=raw_path.stat().st_size,sha256=hashlib.file_digest(raw_path.open('rb'),'sha256').hexdigest()),checkpoint_SHA=hashlib.file_digest((out/'own_native120.pt').open('rb'),'sha256').hexdigest()))
 rescue_training.learn=finite
 try:ns['main']()
 finally:ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  p=BASE/('NATIVE_WORKER_ORIGINAL_ERROR_'+str(time.time_ns())+'.json');put(p,dict(error=traceback.format_exc(),PPO_updates_not_authorized_in_this_native=True));raise
