"""One original PPO expert per physical GPU; native admission then bounded independent learning."""
from pathlib import Path
import argparse,hashlib,json,os,runpy,sys,time,traceback
BASE=Path(__file__).resolve().parent
OWN_JOB_ID=None
def H(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
def put(p,v):
 p=Path(p);q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def main():
 global OWN_JOB_ID
 p=argparse.ArgumentParser();p.add_argument('--job',type=int,choices=(3,),required=True);a=p.parse_args();OWN_JOB_ID=a.job;j=BASE/('job'+str(a.job));out=j/'run';out.mkdir();task=json.loads((j/'TASK.json').read_bytes());source=j/'source/source.pt';assert H(source)==task['source_SHA'];manifest=json.loads((j/'original_run_manifest.json').read_bytes())
 for k in list(os.environ):
  if k.startswith('RM_') or k in ('RANK','LOCAL_RANK','WORLD_SIZE','MASTER_ADDR','MASTER_PORT'):del os.environ[k]
 os.environ.update({k:str(v) for k,v in manifest['env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')});os.environ['RM_MOD4_USD']=str(j/'assets/robot.usd');os.environ['RM_RESCUE_STOP_FILE']=str(out/'STOP_AFTER_SAVE.json')
 sys.path[:0]=[str(BASE/'lib'),str(j/'runtime/isaac/mod4')];entry=j/'runtime/isaac/mod4'/task['entry'];sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','0.0001','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(out/'logs'),'--run_name','independent_'+task['kind']+'_first1800','--additional_iterations','100000'];ns=runpy.run_path(str(entry),run_name='owned_expert_config_only')
 import torch,numpy as np,rescue_training
 from spring_pressure_checkpoint import exact
 from independent_expert_axis_v1 import bind_after_restore
 class SavedStop(Exception):pass
 def learn(runner,n,log_dir):
  env=runner.env.unwrapped;vec=runner.env;runner.logger.writer=None;ck=torch.load(source,map_location='cpu',weights_only=False)
  for k,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,ck[k]),k
  receipts=sorted(Path(log_dir).glob('*STARTUP_VERIFIED.json'));assert len(receipts)>=8;initial_step=task['source_Adamstep'];trace_offset=0;trace_files=[]
  def flush(directory):
   nonlocal trace_offset
   directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);rows=env._retention_trace
   if rows:
    q=directory/('retention_prefix_'+str(trace_offset)+'_'+str(trace_offset+len(rows))+'.npz');assert not q.exists();np.savez_compressed(q,rows=np.stack(rows));trace_files.append(dict(path=str(q),bytes=q.stat().st_size,SHA=H(q),first=trace_offset,last=trace_offset+len(rows)));trace_offset+=len(rows);env._retention_trace=[];env._retention_trace_written=0
   put(directory/'RETENTION_COMMAND_ACTUAL.json',dict(epoch=time.time(),actual_controls=trace_offset,files=trace_files,audit=env.command_manager.get_term('twist').audit_retention()))
  env.write_retention_trace=flush;oldsave=runner.save
  axis=bind_after_restore(env,task['kind'])
  def save(path,complete=True):
   path=Path(path);tmp=path.with_suffix(path.suffix+'.partial');oldsave(str(tmp));v=torch.load(tmp,map_location='cpu',weights_only=False);v['independent_expert_scope_state']={k:z.detach().clone() if torch.is_tensor(z) else z for k,z in axis.items()};v['independent_expert_task_contract']=task;torch.save(v,tmp);tmp.replace(path);steps={int(z['step']) for z in v['optimizer_state_dict']['state'].values()};assert len(steps)==1;s=next(iter(steps));row=dict(epoch=time.time(),job=a.job,kind=task['kind'],path=str(path),bytes=path.stat().st_size,SHA=H(path),Adam_step=s,updates=(s-initial_step)//20,controls=trace_offset+len(env._retention_trace),complete_optimizer_update=complete)
   if complete:put(out/'latest_complete.json',row)
   return row
  save(out/'own_axis_restored0.pt');runner.alg.actor.eval();runner.alg.critic.eval();obs=vec.get_observations();tick=env._integrated_contact.tick;prefix=[];chunks=[]
  def persist():
   if not prefix:return
   q=out/('native_chunk_'+str(len(chunks))+'.npz');assert not q.exists();np.savez_compressed(q,**{k:np.stack([r[k] for r in prefix]) for k in prefix[0]});chunks.append(dict(path=str(q),bytes=q.stat().st_size,SHA=H(q)));prefix.clear()
  try:
   with torch.inference_mode():
    for i in range(120):
     x=obs['policy'];assert x.shape==(20000,35) and obs['critic'].shape==(20000,38);before=x.cpu().numpy().copy();critic_before=obs['critic'].cpu().numpy().copy();action=runner.alg.actor(obs,stochastic_output=False);assert torch.isfinite(action).all();raw=action.cpu().numpy().copy();obs,reward,done,info=vec.step(action);f=env._e1_pre_reset_frame
     prefix.append(dict(policy35=before,critic38=critic_before,raw6=raw,done=done.cpu().numpy().copy(),reward=reward.cpu().numpy().copy(),root13=f['root'].cpu().numpy().copy(),q30=f['q'].cpu().numpy().copy(),ground=f['ground'].cpu().numpy().copy(),normal=f['normal'].cpu().numpy().copy(),closure=f['closure'].cpu().numpy().copy(),mimic=f['mimic'].cpu().numpy().copy(),independent_query_error=np.asarray(f['independent_ground_error'])))
     if i%24==23:persist();assert not (Path(log_dir)/'STOP_AFTER_SAVE').exists() and not (out/'STOP_AFTER_SAVE.json').exists()
  finally:persist();flush(log_dir);save(out/'own_native_valid_prefix.pt')
  assert env._integrated_contact.tick-tick==480
  for key,v in [('actor_state_dict',runner.alg.actor.state_dict()),('critic_state_dict',runner.alg.critic.state_dict()),('optimizer_state_dict',runner.alg.optimizer.state_dict())]:assert exact(v,ck[key]),key
  native=save(out/'own_native120.pt');native.update(source_SHA=task['source_SHA'],callbacks=480,controls=120,chunks=chunks,startup_receipts=[str(p) for p in receipts],GPU_UUID=str(torch.cuda.get_device_properties(0).uuid),no_optimizer_updates=True,new_axis_explicit=True,physics_action_audit=env._physics_action_delay.audit(),chassis_PD_audit=env.chassis_pd_audit());put(out/'NATIVE120_COMPLETE.json',native)
  wait=time.time()
  while not (out/'GO_LEARN.json').exists():
   if time.time()-wait>1800 or (out/'STOP_AFTER_SAVE.json').exists():raise RuntimeError('Own finite learning admission not received; no PPO')
   time.sleep(2)
  go=json.loads((out/'GO_LEARN.json').read_bytes());deadline=go['save_deadline'];oldlog=runner.logger.log;completed=0
  def log(*aa,**kw):
   nonlocal completed
   oldlog(*aa,**kw);completed+=1;stop=time.time()>=deadline or (out/'STOP_AFTER_SAVE.json').exists() or (Path(log_dir)/'STOP_AFTER_SAVE').exists()
   if completed==1 or completed%25==0 or stop:
    row=save(out/('model_update'+str(completed)+'.pt'));assert row['Adam_step']==initial_step+20*completed;put(out/'PPO_POSITIVE_CURRENT.json',dict(epoch=time.time(),job=a.job,kind=task['kind'],row=row,independent_policy_no_NCCL=True))
   if stop:raise SavedStop()
  runner.logger.log=log
  try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)
  except SavedStop:pass
  finally:flush(log_dir)
  row=json.loads((out/'latest_complete.json').read_bytes());assert row['updates']>0;put(out/'FINAL.json',dict(epoch=time.time(),passed=True,final=row))
 rescue_training.learn=learn
 try:ns['main']()
 except BaseException:
  put(j/'WORKER_ORIGINAL_ERROR_BEFORE_APP_CLOSE.json',dict(epoch=time.time(),error=traceback.format_exc(),preserved_before_SDK_teardown=True));raise
 finally:
  put(out/'APP_CLOSING.json',dict(epoch=time.time(),job=a.job));ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  p=BASE/('job'+str(OWN_JOB_ID));p.mkdir(exist_ok=True);put(p/'WORKER_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_automatic_retry=True));raise
