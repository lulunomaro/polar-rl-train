"""Three physical4090s, one synchronous original RSL5 PPO; owned process only."""
from pathlib import Path
from datetime import timedelta
import argparse,hashlib,json,os,sys,time,traceback
BASE=Path(__file__).resolve().parent
def atomic(p,v):
 q=p.with_suffix(p.suffix+'.partial');q.write_text(json.dumps(v,indent=2));q.replace(p)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--rank',type=int,required=True);p.add_argument('--mode',choices=('probe','train'),required=True);a=p.parse_args();rank=a.rank
 out=BASE/('rank'+str(rank));out.mkdir(exist_ok=True);start=time.time()
 import torch
 assert torch.cuda.device_count()==1;torch.cuda.set_device(0)
 if a.mode=='probe':
  torch.distributed.init_process_group('nccl',rank=rank,world_size=3,timeout=timedelta(seconds=120))
  x=torch.tensor([rank+1.],device='cuda:0');torch.distributed.all_reduce(x);assert x.item()==6.
  w=torch.nn.Parameter(torch.tensor([1.],device='cuda:0'));opt=torch.optim.Adam([w],lr=.0001)
  (w*(rank+1.)).sum().backward();torch.distributed.all_reduce(w.grad);w.grad.div_(3);opt.step()
  rows=[None]*3;torch.distributed.all_gather_object(rows,w.detach().cpu().tolist());assert rows[0]==rows[1]==rows[2]
  atomic(out/'NCCL_PROBE_COMPLETE.json',dict(epoch=time.time(),rank=rank,pid=os.getpid(),CUDA_UUID=str(torch.cuda.get_device_properties(0).uuid),allreduce_value=x.item(),three_rank_shared_fixture_Adam_equal=True,fixture_not_MOD4_PPO=True,rank_results=rows))
  torch.distributed.destroy_process_group();return
 plant=BASE/'plant';m=plant/'runtime/isaac/mod4';source=plant/'source/source.pt';assert sha(source)=='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e'
 manifest=json.loads((plant/'original_run_manifest.json').read_bytes())
 for k in list(os.environ):
  if k.startswith('RM_'):del os.environ[k]
 os.environ.update({k:str(v) for k,v in manifest['env'].items() if k not in ('RM_RESCUE_DEADLINE','RM_RESCUE_STOP_FILE')})
 os.environ['RM_MOD4_USD']=str(plant/'assets/robot.usd');os.environ['RM_RESCUE_STOP_FILE']=str(out/'STOP_AFTER_SAVE.json')
 sys.path.insert(0,str(BASE/'lib'));sys.path.insert(0,str(m))
 entry=m/'train_host72_backend_admission_v1.py'
 sys.argv=[str(entry),'--headless','--device','cuda:0','--num_envs','20000','--seed','20260928','--steps_per_env','24','--learning_rate','0.0001','--save_interval','25','--init_checkpoint',str(source),'--log_root',str(out/'logs'),'--run_name','CURB20_one_PPO_three_GPU_7h','--additional_iterations','100000']
 import runpy
 ns=runpy.run_path(str(entry),run_name='owned_configuration_only')
 import rescue_training,numpy as np
 from spring_pressure_checkpoint import exact
 class SavedStop(Exception):pass
 def learning(runner,n,log_dir):
  vec=runner.env;env=vec.unwrapped;runner.logger.writer=None;runner.alg.actor.eval();runner.alg.critic.eval()
  ck=torch.load(source,map_location='cpu',weights_only=False);initial_step=int(next(iter(ck['optimizer_state_dict']['state'].values()))['step'])
  assert exact(runner.alg.actor.state_dict(),ck['actor_state_dict']) and exact(runner.alg.critic.state_dict(),ck['critic_state_dict']) and exact(runner.alg.optimizer.state_dict(),ck['optimizer_state_dict'])
  receipts=sorted(Path(log_dir).glob('*STARTUP_VERIFIED.json'));assert len(receipts)>=8,[p.name for p in receipts]
  # Only after strict whole original restore: explicit independent rank-stream migration.
  fork=[];seen=set();objects=[('command',env.command_manager.get_term('twist'))]
  for key,value in vars(env).items():
   if any(x in key.lower() for x in ('sensor','mild_dr','feedback','delay','spring','damping','chassis','explicit_pd')):objects.append(('env.'+key,value))
  def visit(path,obj,depth=0):
   if id(obj) in seen or depth>5:return
   seen.add(id(obj))
   if isinstance(obj,torch.Generator):
    before=hashlib.sha256(obj.get_state().cpu().numpy().tobytes()).hexdigest()
    if rank:obj.manual_seed(int(hashlib.sha256((before+'|rank'+str(rank)+'|'+path).encode()).hexdigest()[:15],16))
    fork.append(dict(path=path,source_state_SHA=before,actual_state_SHA=hashlib.sha256(obj.get_state().cpu().numpy().tobytes()).hexdigest(),explicit_rank_fork=rank!=0));return
   if torch.is_tensor(obj) or isinstance(obj,(str,int,float,bool,type(None),torch.nn.Module)):return
   if isinstance(obj,dict):items=obj.items()
   elif isinstance(obj,(list,tuple)):items=enumerate(obj)
   elif hasattr(obj,'__dict__'):items=vars(obj).items()
   else:return
   for k,v in items:
    if str(k) not in ('_env','env','robot','_robot','scene','_scene','sim','_sim','cfg'):visit(path+'.'+str(k),v,depth+1)
  for k,v in objects:visit(k,v)
  assert len(fork)>=10,len(fork)
  if rank:
   torch.manual_seed(20260928+rank*1000003);torch.cuda.manual_seed_all(20260928+rank*1000003)
  atomic(out/'STRICT_SOURCE_RESTORE_THEN_EXPLICIT_RANK_STREAM_FORK.json',dict(epoch=time.time(),rank=rank,receipts=[p.name for p in receipts],original_actor_critic_STD_17Adam_exact=True,sourceepisode_plus_one_original_receipts=True,rank_fork_after_restore=True,initial_physical_factors_shared_source_not_independent_claim=True,streams=fork,rank_seed=20260928+rank*1000003 if rank else 20260928,global_envs=60000,per_rank_envs=20000))
  # Bounded raw evidence, preserving all original 16-column prefix rows.
  trace_offset=0;trace_files=[]
  def flush(directory):
   nonlocal trace_offset
   directory=Path(directory);directory.mkdir(parents=True,exist_ok=True);rows=env._retention_trace
   if rows:
    p=directory/('rank'+str(rank)+'_retention_prefix_'+str(trace_offset)+'_'+str(trace_offset+len(rows))+'.npz');assert not p.exists();np.savez_compressed(p,rows=np.stack(rows))
    trace_files.append(dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p),first=trace_offset,last=trace_offset+len(rows)));trace_offset+=len(rows);env._retention_trace=[];env._retention_trace_written=0
   atomic(directory/'RETENTION_COMMAND_ACTUAL.json',dict(actual_controls=trace_offset,trace_files=trace_files,audit=env.command_manager.get_term('twist').audit_retention(),pre_reset_roots_no_teleport=True,complete_cycles_not_claimed_from_truncated_prefixes=True))
  env.write_retention_trace=flush
  save_old=runner.save
  def save(path,*aa,**kw):
   path=Path(path);tmp=path.with_suffix(path.suffix+'.partial');save_old(str(tmp),*aa,**kw)
   saved=torch.load(tmp,map_location='cpu',weights_only=False);saved['distributed_rank_contract']=dict(world_size=3,rank=rank,task='E1_CURB20_original_entry',per_rank_envs=20000,global_envs=60000,source_SHA=sha(source),explicit_source_stream_fork_after_strict_restore=True)
   torch.save(saved,tmp);tmp.replace(path);steps=sorted(set(int(x['step']) for x in saved['optimizer_state_dict']['state'].values()));assert len(steps)==1
   actor_hash=hashlib.sha256(b''.join(x.detach().cpu().contiguous().numpy().tobytes() for x in saved['actor_state_dict'].values())).hexdigest()
   critic_hash=hashlib.sha256(b''.join(x.detach().cpu().contiguous().numpy().tobytes() for x in saved['critic_state_dict'].values())).hexdigest()
   row=dict(epoch=time.time(),rank=rank,pid=os.getpid(),checkpoint=str(path),bytes=path.stat().st_size,SHA=sha(path),Adam_step=steps[0],updates=(steps[0]-initial_step)//20,actor_SHA=actor_hash,critic_SHA=critic_hash,controls=trace_offset+len(env._retention_trace))
   atomic(out/'latest_complete.json',row);return row
  runner.save=save;save(out/'own_restored0.pt')
  obs=vec.get_observations();before=env._integrated_contact.tick;prefix=[];native_chunks=[]
  def persist_native():
   if not prefix:return
   p=out/('native_physical_controls_'+str(len(native_chunks)*24)+'_'+str(len(native_chunks)*24+len(prefix))+'.npz')
   assert not p.exists();np.savez_compressed(p,**{k:np.stack([r[k] for r in prefix]) for k in prefix[0]})
   native_chunks.append(dict(path=str(p),bytes=p.stat().st_size,SHA=sha(p)));prefix.clear()
  try:
   with torch.inference_mode():
    for i in range(120):
     assert obs['policy'].shape==(20000,35) and obs['critic'].shape==(20000,38)
     policy=obs['policy'].cpu().numpy().copy();critic=obs['critic'].cpu().numpy().copy();action=runner.alg.actor(obs,stochastic_output=False);assert torch.isfinite(action).all();raw=action.cpu().numpy().copy();obs,reward,done,info=vec.step(action)
     frame=env._e1_pre_reset_frame
     prefix.append(dict(policy35=policy,critic38=critic,raw6=raw,expected_clip6=np.clip(raw,-6.,6.),root13=frame['root'].cpu().numpy().copy(),q30=frame['q'].cpu().numpy().copy(),ground=frame['ground'].cpu().numpy().copy(),normal=frame['normal'].cpu().numpy().copy(),closure=frame['closure'].cpu().numpy().copy(),mimic=frame['mimic'].cpu().numpy().copy(),done=done.cpu().numpy().copy(),reward=reward.cpu().numpy().copy(),query_error=np.asarray(frame['independent_ground_error'])))
     if i%24==23:
      persist_native()
      assert not (Path(log_dir)/'STOP_AFTER_SAVE').exists() and not (out/'STOP_AFTER_SAVE.json').exists()
  finally:persist_native();flush(log_dir)
  assert env._integrated_contact.tick-before==480 and exact(runner.alg.actor.state_dict(),ck['actor_state_dict']) and exact(runner.alg.optimizer.state_dict(),ck['optimizer_state_dict'])
  native=save(out/'own_native120.pt');native.update(native120=True,callbacks=480,no_optimizer_update=True,native_full_physical_chunks=native_chunks);atomic(out/'NATIVE120_COMPLETE.json',native)
  flags=torch.ones(1,device='cuda:0');torch.distributed.all_reduce(flags);assert flags.item()==3
  atomic(out/'READY_FOR_SINGLE_PPO.json',dict(epoch=time.time(),rank=rank,all_three_native120_completed=True,source_SHA=sha(source)))
  while not (out/'GO_SINGLE_PPO.json').exists():
   if time.time()-start>1200 or (out/'STOP_AFTER_SAVE.json').exists():raise RuntimeError('No learning admission from original solecanonical owner; no PPO started')
   time.sleep(1)
  go=json.loads((out/'GO_SINGLE_PPO.json').read_bytes());deadline=go['save_deadline_epoch'];oldlog=runner.logger.log;completed=0
  def log(*aa,**kw):
   nonlocal completed
   oldlog(*aa,**kw);completed+=1
   stop=torch.tensor([int(time.time()>=deadline or (out/'STOP_AFTER_SAVE.json').exists() or (Path(log_dir)/'STOP_AFTER_SAVE').exists())],device='cuda:0');torch.distributed.all_reduce(stop,op=torch.distributed.ReduceOp.MAX)
   if completed==1 or completed%25==0 or stop.item():
    row=save(out/('model_update'+str(completed)+'.pt'));all_rows=[None]*3;torch.distributed.all_gather_object(all_rows,{k:row[k] for k in ('rank','updates','Adam_step','actor_SHA','critic_SHA')})
    assert len({x['actor_SHA'] for x in all_rows})==len({x['critic_SHA'] for x in all_rows})==len({x['Adam_step'] for x in all_rows})==1
    atomic(out/'SHARED_PPO_ALL_RANK_PARAMETERS_EXACT_ACTUAL.json',dict(epoch=time.time(),rows=all_rows,shared_single_policy=True,not_three_independent_PPO=True));torch.distributed.barrier()
   if stop.item():raise SavedStop('All ranks saved same complete PPO update; bounded stop')
  runner.logger.log=log
  try:runner.learn(num_learning_iterations=n,init_at_random_ep_len=True)
  except SavedStop:pass
  finally:flush(log_dir)
  final=json.loads((out/'latest_complete.json').read_bytes());assert final['updates']>0;atomic(out/'FINAL_SINGLE_PPO.json',dict(epoch=time.time(),passed=True,final=final,all_rank_synchronized_saved_stop=True))
 rescue_training.learn=learning
 try:ns['main']()
 finally:
  if torch.distributed.is_initialized():torch.distributed.destroy_process_group()
  ns['app'].close()
if __name__=='__main__':
 try:main()
 except BaseException:
  rank=os.environ.get('RANK','unknown');p=BASE/('rank'+rank);p.mkdir(exist_ok=True);atomic(p/'ORIGINAL_WORKER_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_failed_or_partial_update_relabelled_complete=True));raise
