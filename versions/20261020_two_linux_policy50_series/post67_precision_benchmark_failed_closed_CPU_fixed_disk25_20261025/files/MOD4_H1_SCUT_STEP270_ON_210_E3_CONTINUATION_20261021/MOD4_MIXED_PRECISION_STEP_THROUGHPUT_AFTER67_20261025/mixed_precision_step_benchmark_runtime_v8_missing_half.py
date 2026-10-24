"""Isolated post-window precision benchmark; never a qualified policy source."""
from pathlib import Path
import contextlib,copy,hashlib,inspect,json,random,shutil,time,traceback,types
import numpy as np
import torch
def put(p,v):
 p=Path(p);tmp=p.with_suffix(p.suffix+'.partial');tmp.write_text(json.dumps(v,indent=2),encoding='utf8');tmp.replace(p)
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def amp_ppo_source(source):
 lines=source.splitlines()
 back=next(line for line in lines if line.strip()=='loss.backward()')
 step=next(line for line in lines if line.strip()=='self.optimizer.step()')
 clip=next(line for line in lines if line.strip()=='nn.utils.clip_grad_norm_(self.actor.parameters(), self.max_grad_norm)')
 assert lines.count(back)==lines.count(step)==lines.count(clip)==1
 indent=clip[:len(clip)-len(clip.lstrip())];step_indent=step[:len(step)-len(step.lstrip())]
 return source.replace(back,back.replace('loss.backward()','self._benchmark_scaler.scale(loss).backward()')).replace(clip,indent+'self._benchmark_scaler.unscale_(self.optimizer)\n'+clip).replace(step,step.replace('self.optimizer.step()','self._benchmark_scaler.step(self.optimizer)')+'\n'+step_indent+'self._benchmark_scaler.update()')
def finite_tree(x):
 if torch.is_tensor(x):return not x.is_floating_point() or bool(torch.isfinite(x).all())
 if isinstance(x,dict):return all(finite_tree(v) for v in x.values())
 if isinstance(x,(tuple,list)):return all(finite_tree(v) for v in x)
 return True
def actual_callback_clock(env,key):
 return (int(env._integrated_contact.tick),None if key=='h1' else int(env._feedback_100hz_tick))
def verify_callback_clock(before,after,key):
 assert after[0]-before[0]==(4 if key=='h1' else 8)
 if key!='h1':assert after[1]-before[1]==2

def actual_logger_timing(original_log,args,kwargs):
 bound=inspect.signature(original_log).bind(*args,**kwargs)
 return float(bound.arguments['collect_time']),float(bound.arguments['learn_time'])

class ExclusivePhaseTimers:
 def __init__(self,clock=time.perf_counter):
  self.clock=clock;self.enabled=False;self.sums={};self.counts={};self.stack=[];self.originals=[]
 def clear(self):self.sums={};self.counts={};assert not self.stack
 def install(self,obj,name,label):
  original=getattr(obj,name)
  def wrapper(*aa,**kk):
   if not self.enabled:return original(*aa,**kk)
   frame=[label,self.clock(),0.];self.stack.append(frame)
   try:return original(*aa,**kk)
   finally:
    elapsed=self.clock()-frame[1];self.stack.pop();self.sums[label]=self.sums.get(label,0.)+max(0.,elapsed-frame[2]);self.counts[label]=self.counts.get(label,0)+1
    if self.stack:self.stack[-1][2]+=elapsed
  setattr(obj,name,wrapper);self.originals.append((obj,name,original))
 def restore(self):
  for obj,name,fn in reversed(self.originals):setattr(obj,name,fn)

def run(runner,src,task,go,out,key):
 out=Path(out);env=runner.env.unwrapped;alg=runner.alg
 assert task['performance_benchmark_only'] and go['source_SHA']==task['source_SHA'] and go['max_parent_seconds']==3900 and go['exit_headroom_seconds']==300
 assert env.num_envs==20000 and env.physics_dt==.0025 and env.step_dt==(.01 if key=='h1' else .02) and env.cfg.decimation==(4 if key=='h1' else 8)
 env._physics_action_delay.queue.control_us=10000 if key=='h1' else 20000
 assert int(env._sim_step_counter)==0 and not alg.is_multi_gpu and alg.rnd is None
 from spring_pressure_checkpoint import exact
 s=torch.load(src,map_location='cpu',weights_only=False)
 for name,value in [('actor_state_dict',alg.actor.state_dict()),('critic_state_dict',alg.critic.state_dict()),('optimizer_state_dict',alg.optimizer.state_dict())]:assert exact(value,s[name]),name
 assert len(s['actor_state_dict'])==9 and len(s['critic_state_dict'])==8 and len(s['optimizer_state_dict']['state'])==17
 assert all(p.dtype==torch.float32 for model in (alg.actor,alg.critic) for p in model.parameters())
 from h1_reward_scope_v1 import isolated_actual_SDK_dt_probe
 put(out/'ACTUAL_ORIGINAL_SDK_REWARD_DT_PROBE.json',isolated_actual_SDK_dt_probe(env))
 runner.logger.writer=None
 sourcefile=Path(inspect.getsourcefile(alg.__class__));source=sourcefile.read_text('utf8');patched=amp_ppo_source(source)
 (out/'ACTUAL_BASE_PPO_SOURCE.py').write_text(source,encoding='utf8');(out/'BENCHMARK_ONLY_AMP_PPO_SOURCE.py').write_text(patched,encoding='utf8')
 module=types.ModuleType('isolated_precision_benchmark_ppo_'+key);module.__file__=str(out/'BENCHMARK_ONLY_AMP_PPO_SOURCE.py');exec(compile(patched,module.__file__,'exec'),module.__dict__)
 original_update=alg.update;alg.update=types.MethodType(module.PPO.update,alg)
 original_mlp={k:m.mlp.forward for k,m in [('actor',alg.actor),('critic',alg.critic)]}
 mode_state={'mode':'fp32','dtype':None,'act_s':0.,'env_s':0.,'act_calls':0,'env_calls':0,'cycle_start':None,'cycle_end':None,'update_s':0.}
 for name,model in [('actor',alg.actor),('critic',alg.critic)]:
  orig=original_mlp[name]
  def forward(*aa,_orig=orig,**kw):
   with torch.autocast(device_type='cuda',dtype=mode_state['dtype'] or torch.float16,enabled=mode_state['dtype'] is not None):
    result=_orig(*aa,**kw)
   assert torch.is_tensor(result)
   return result.float()
  model.mlp.forward=forward
 profile=ExclusivePhaseTimers()
 for obj,name,label in [(env.sim,'step','physics_sim_step'),(env.scene,'update','scene_update_sensors_and_state'),(env.reward_manager,'compute','reward_compute'),(env.termination_manager,'compute','termination_checks'),(env.observation_manager,'compute','observation_compute'),(env,'_reset_idx','selected_environment_reset')]:
  profile.install(obj,name,label)
 if key=='h1':profile.install(env.h1_phase,'physical','step270_goal_geometry_and_events')
 from e1_rough_ground import AuthoredTerrainRaycast
 for name,obj in list(vars(env).items()):
  if isinstance(obj,AuthoredTerrainRaycast):profile.install(obj,'cast','terrain_query_'+name)
 original_act=alg.act;original_step=runner.env.step;original_log=runner.logger.log
 sync=lambda:torch.cuda.synchronize()
 def neural_act(*aa,**kk):
  sync();start=time.perf_counter();ret=original_act(*aa,**kk);sync();mode_state['act_s']+=time.perf_counter()-start;mode_state['act_calls']+=1;return ret
 def act(*aa,**kk):
  if mode_state['cycle_start'] is None:
   sync();mode_state['cycle_start']=time.perf_counter();profile.clear();profile.enabled=True
  return mode_state['act_impl'](*aa,**kk)
 def step(action):
  before=actual_callback_clock(env,key);sync();start=time.perf_counter();ret=mode_state['step_impl'](action);sync();mode_state['env_s']+=time.perf_counter()-start;mode_state['env_calls']+=1
  verify_callback_clock(before,actual_callback_clock(env,key),key)
  return ret
 update_impl=alg.update
 def update(*aa,**kk):
  sync();start=time.perf_counter();result=update_impl(*aa,**kk);sync();mode_state['cycle_end']=time.perf_counter();mode_state['update_s']=mode_state['cycle_end']-start;profile.enabled=False;return result
 alg.act=act;runner.env.step=step;alg.update=update
 base_term=env.termination_manager.compute;base_reward=env.reward_manager.compute
 class BlockComplete(Exception):pass
 suite=[];mode_results=[];NUM_UPDATES=6;WARMUP_UPDATES=2
 put(out/'PRECISION_BENCHMARK_SOURCE_AND_PROTOCOL_ACTUAL.json',dict(epoch=time.time(),key=key,source_SHA=task['source_SHA'],source_Adam=task['source_Adamstep'],source_actor_critic_STD17Adam_exact=True,base_PPO_path=str(sourcefile),base_PPO_SHA=hashlib.sha256(source.encode()).hexdigest(),benchmark_PPO_SHA=hashlib.sha256(patched.encode()).hexdigest(),declared_changes='MLP-only autocast with FP32 outputs; GradScaler scale/unscale/step in isolated PPO copy; original installed PPO untouched',modes=['bf16','fp16'],independent_source_clones_per_mode=True,source_model_never_replaced=True,all_physics_command_goal_reward_identical=True,normal_full_env_reset_between_independent_benchmark_cases_not_jump_assistance=True,per_mode_complete_updates=NUM_UPDATES,excluded_warmup_updates=WARMUP_UPDATES,CUDA_synchronization_same_all_modes=True,not_a_training_source_or_skill_evaluation=True,original_H1_trace_record_compression_and_approved_prune_preserved=True))
 try:
  for mode,dtype in [('bf16',torch.bfloat16),('fp16',torch.float16)]:
   if time.time()+300>=go['save_deadline'] or (out/'STOP_AFTER_SAVE.json').exists():
    mode_results.append(dict(mode=mode,not_run=True,reason='Own original finite save headroom'));break
   dest=out/mode;dest.mkdir();mode_state.update(mode=mode,dtype=dtype,act_s=0.,env_s=0.,act_calls=0,env_calls=0,cycle_start=None,cycle_end=None,update_s=0.)
   alg.actor.load_state_dict(s['actor_state_dict']);alg.critic.load_state_dict(s['critic_state_dict']);alg.optimizer.load_state_dict(copy.deepcopy(s['optimizer_state_dict']));alg.learning_rate=float(s['optimizer_state_dict']['param_groups'][0]['lr'])
   alg.optimizer.zero_grad(set_to_none=True);alg.storage.clear();alg._benchmark_scaler=torch.amp.GradScaler('cuda',enabled=mode=='fp16')
   for name,value in [('actor_state_dict',alg.actor.state_dict()),('critic_state_dict',alg.critic.state_dict()),('optimizer_state_dict',alg.optimizer.state_dict())]:assert exact(value,s[name]),(mode,name)
   torch.manual_seed(20260928);torch.cuda.manual_seed_all(20260928);np.random.seed(20260928);random.seed(20260928)
   with torch.inference_mode():env.reset()
   obs=runner.env.get_observations()
   with torch.no_grad():
    mode_state['dtype']=None;base_actor=alg.actor(obs,stochastic_output=False).float();base_critic=alg.critic(obs).float()
    mode_state['dtype']=dtype;test_actor=alg.actor(obs,stochastic_output=False).float();test_critic=alg.critic(obs).float()
   assert finite_tree([base_actor,base_critic,test_actor,test_critic])
   compare=dict(actor_max_abs_error=float((test_actor-base_actor).abs().max()),actor_RMS_error=float((test_actor-base_actor).square().mean().sqrt()),critic_max_abs_error=float((test_critic-base_critic).abs().max()),critic_RMS_error=float((test_critic-base_critic).square().mean().sqrt()),same_observations_and_source_weights=True)
   trace=None;alg.act=neural_act;runner.env.step=original_step
   profile.install(alg,'act','actor_critic_inference')
   if key=='h1':
    from h1_production_control_prefix_trace_v1 import H1ControlPrefixTrace
    trace=H1ControlPrefixTrace(runner,dest/'control_prefix_raw');trace.install()
    profile.install(trace,'persist','trace_compression_full_SHA_and_retention')
    profile.install(env.termination_manager,'compute','trace_pre_reset_state_capture')
    profile.install(env.reward_manager,'compute','trace_reward_capture')
    profile.install(alg,'act','trace_preupdate_checkpoint_and_observation_capture')
   mode_state['act_impl']=alg.act;mode_state['step_impl']=runner.env.step
   alg.act=act;runner.env.step=step
   rows=[];completed=0;mode_error=None
   def log(*aa,**kk):
    nonlocal completed
    sync();full_cycle_end=time.perf_counter();original_log(*aa,**kk);completed+=1
    collect_time,learn_time=actual_logger_timing(original_log,aa,kk)
    assert mode_state['act_calls']==mode_state['env_calls']==24
    cycle=full_cycle_end-mode_state['cycle_start'];steps=sorted({int(v['step']) for v in alg.optimizer.state_dict()['state'].values()})
    finite=finite_tree([alg.actor.state_dict(),alg.critic.state_dict(),alg.optimizer.state_dict()])
    row=dict(update=completed,warmup=completed<=WARMUP_UPDATES,collection_s=collect_time,original_logger_learning_s=learn_time,actor_critic_act_wall_s=mode_state['act_s'],environment_step_wall_s=mode_state['env_s'],PPO_update_wall_s=mode_state['update_s'],cycle_wall_s=cycle,env_transitions=480000,collection_env_steps_s=480000/collect_time,end_to_end_env_steps_s=480000/cycle,actual17Adam_steps=steps,source_Adam=int(task['source_Adamstep']),expected_Adam_without_skipped_FP16_steps=int(task['source_Adamstep'])+completed*20,GradScaler_scale=float(alg._benchmark_scaler.get_scale()),all_source_model_optimizer_tensors_finite=finite)
    row.update(sampling_phase_exclusive_CPU_wall_s=dict(profile.sums),sampling_phase_call_counts=dict(profile.counts),collection_unattributed_or_async_tail_s=max(0.,collect_time-sum(profile.sums.values())),phase_timing_includes_implicit_GPU_waits_not_CUPTI_kernel_attribution=True)
    rows.append(row);put(dest/'TIMING_CURRENT.json',dict(epoch=time.time(),mode=mode,rows=rows,comparison=compare));put(out/'BENCHMARK_PROGRESS_CURRENT.json',dict(epoch=time.time(),key=key,mode=mode,completed_in_mode=completed,earlier_mode_results=mode_results,current_row=row,not_model_qualification=True))
    mode_state.update(act_s=0.,env_s=0.,act_calls=0,env_calls=0,cycle_start=None,cycle_end=None,update_s=0.)
    assert finite,'Nonfinite benchmark output preserved; no production source replacement'
    free=shutil.disk_usage(out).free
    if free<8*1024**3:put(out/'OWN_STORAGE_COMPLETE_UPDATE_SAVED_STOP_ACTUAL.json',dict(epoch=time.time(),free_bytes=free,original_reserve8GiB=True,complete_update_only=True,no_force_kill=True))
    if completed>=NUM_UPDATES or free<8*1024**3 or time.time()>=go['save_deadline'] or (out/'STOP_AFTER_SAVE.json').exists():raise BlockComplete()
   runner.logger.log=log
   started=time.time()
   try:runner.learn(num_learning_iterations=NUM_UPDATES+1,init_at_random_ep_len=True)
   except BlockComplete:pass
   except BaseException:mode_error=traceback.format_exc();put(dest/'MODE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=mode_error,complete_updates=completed,no_retry=True))
   finally:
    profile.enabled=False
    if trace is not None:trace.persist()
    env.termination_manager.compute=base_term;env.reward_manager.compute=base_reward
    snapshot=dest/('benchmark_complete_snapshot.pt' if mode_error is None else 'benchmark_failed_prefix_snapshot.pt');tmp=snapshot.with_suffix('.pt.partial')
    try:
     runner.save(str(tmp));tmp.replace(snapshot);artifact=dict(path=str(snapshot),bytes=snapshot.stat().st_size,SHA=H(snapshot),benchmark_only_not_qualified_source=True)
    except BaseException:artifact=None;put(dest/'SNAPSHOT_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),partial_retained=True))
   result=dict(mode=mode,actual_completed_updates=completed,complete=completed==NUM_UPDATES and mode_error is None,error=mode_error,comparison=compare,rows=rows,artifact=artifact,mode_started_epoch=started,mode_ended_epoch=time.time(),all_FP32_master_parameters=all(p.dtype==torch.float32 for model in (alg.actor,alg.critic) for p in model.parameters()),benchmark_only_not_qualified_source=True)
   put(dest/'MODE_COMPLETE_ACTUAL.json',result);mode_results.append(result)
   if mode_error is not None or completed<NUM_UPDATES:break
  assert mode_results and mode_results[0].get('complete'),'First requested missing precision mode failed'
  summary=dict(epoch=time.time(),suite_execution_complete=True,key=key,source_SHA=task['source_SHA'],mode_results=mode_results,all_original_errors_and_failed_prefixes_preserved=True,not_a_training_FINAL_model=True,not_a_qualified_continuation_source=True,not_a_skill_or_270mm_evaluation=True,original_owner_must_still_wait_SDKclose_childexit_and_settle_actual_cost=True)
  put(out/'PRECISION_BENCHMARK_COMPLETE_ACTUAL.json',summary)
 finally:
  profile.enabled=False;profile.restore()
  alg.act=original_act;alg.update=original_update;runner.env.step=original_step;runner.logger.log=original_log
  for name,model in [('actor',alg.actor),('critic',alg.critic)]:model.mlp.forward=original_mlp[name]

