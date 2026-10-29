"""Readonly E3 original recovery phase/cache telemetry, no contact/SDK query."""
from pathlib import Path
from original_flat_height_provider_v1 import OriginalFlatHeightProvider
import gzip,json,types
from lossless_snapshot_pinned75d683 import LosslessSnapshot
from e3_original_recipe_phase_catalog_v1 import PROFILE_LABELS,profile_key,upcoming_request,new_original_credit
def tensor(x):return x.torch if hasattr(x,'torch') else x
class E3Book:
 def __init__(self,t,n,device,reasons):
  self.t=t;self.n=n;self.ids=t.arange(n,device=device);self.reasons=tuple(reasons)
  self.count=t.zeros((2,25,n),device=device,dtype=t.long);self.attempt_exposure=t.zeros_like(self.count);self.last_attempt=t.full_like(self.count,-1)
  self.whole_attempt_exposure=t.zeros((25,n),device=device,dtype=t.long);self.whole_last_attempt=t.full_like(self.whole_attempt_exposure,-1)
  self.errors=t.zeros((2,6,25,n),device=device);self.terminated=t.zeros_like(self.count);self.truncated=t.zeros_like(self.count);self.credits=t.zeros_like(self.count)
  self.reason=t.zeros((2,len(reasons),25,n),device=device,dtype=t.long);self.raw_soft=t.zeros((2,2,25,n),device=device,dtype=t.long)
  self.peak_gain=t.zeros_like(self.count,dtype=t.float32);self.maximum_stable_ticks=t.zeros_like(self.count);self.live_seconds=t.zeros_like(self.peak_gain)
  self.prev_key=t.full((n,),-1,device=device,dtype=t.long);self.prev_episode=self.prev_key.clone();self.prev_live=t.zeros(n,device=device,dtype=t.bool);self.prev_phase=-1;self.age=t.zeros(n,device=device)
 def observe(self,c,after,terminated,truncated,reason_masks,raw_soft):
  t=self.t;phase=c['phase'];key=c['key'];idx=(key,self.ids);live=~(terminated|truncated);self.count[phase][idx]+=1
  fresh=self.last_attempt[phase][idx]!=c['episode'];self.attempt_exposure[phase][idx]+=fresh.long();self.last_attempt[phase][idx]=c['episode']
  whole_fresh=self.whole_last_attempt[idx]!=c['episode'];self.whole_attempt_exposure[idx]+=whole_fresh.long();self.whole_last_attempt[idx]=c['episode']
  assert bool((after['age']==c['age']+2).all()) and bool((after['recipe']==c['recipe']).all()) and bool((after['request']==c['request']).all())
  event=new_original_credit(t,c['credited'],after['credited'],c['episode'],after['episode']);self.credits[phase][idx]+=event.long()
  assert not bool((event&~c['request']).any()) and bool((after['stable'][event]>=50).all())
  for j,value in enumerate(after['errors']):assert bool(t.isfinite(value).all());self.errors[phase,j][idx]+=value
  self.terminated[phase][idx]+=terminated.long();self.truncated[phase][idx]+=truncated.long()
  for j,value in enumerate(reason_masks):self.reason[phase,j][idx]+=value.long()
  for j,value in enumerate(raw_soft):self.raw_soft[phase,j][idx]+=value.long()
  assert bool((after['peak']>=c['peak']).all());self.peak_gain[phase][idx]+=after['peak']-c['peak']
  self.maximum_stable_ticks[phase][idx]=t.maximum(self.maximum_stable_ticks[phase][idx],after['stable'])
  same=(key==self.prev_key)&(c['episode']==self.prev_episode)&self.prev_live
  if phase!=self.prev_phase:same=t.zeros_like(same)
  self.age=t.where(same,self.age+.02,t.full_like(self.age,.02));self.live_seconds[phase][idx]=t.maximum(self.live_seconds[phase][idx],t.where(live,self.age,t.zeros_like(self.age)))
  self.prev_key=key.clone();self.prev_episode=c['episode'].clone();self.prev_live=live.clone();self.prev_phase=phase
 def summary(self):
  rows=[]
  for phase_name,phase in (('whole',None),('warmup',0),('steady',1)):
   view=lambda x:x.sum(0) if phase is None else x[phase];count=view(self.count);errors=view(self.errors)
   for k,label in enumerate(PROFILE_LABELS):
    den=int(count[k].sum());credits=view(self.credits)[k];term=view(self.terminated)[k];trunc=view(self.truncated)[k]
    rows.append(dict(phase=phase_name,profile=k,label=label,recipe=k//2 if k<24 else 12,population_controls=den,unique_exposed_env=int((count[k]>0).sum()),attempt_profile_exposures=int((self.whole_attempt_exposure[k] if phase is None else self.attempt_exposure[phase,k]).sum()),
     mean_errors={name:float(errors[j,k].sum())/den if den else None for j,name in enumerate(('upright_deficit','root_speed','angular_speed','height_abs_from_point25','body_vx_abs','yaw_abs'))},
     original_new_recovery_credit_events=int(credits.sum()),unique_env_with_original_credit=int((credits>0).sum()),terminated_events=int(term.sum()),unique_terminated_env=int((term>0).sum()),truncated_events=int(trunc.sum()),unique_truncated_env=int((trunc>0).sum()),
     original_reason_events={n:int(view(self.reason)[j,k].sum()) for j,n in enumerate(self.reasons)},raw_soft_orientation_positive_controls=int(view(self.raw_soft)[0,k].sum()),raw_soft_base_contact_positive_controls=int(view(self.raw_soft)[1,k].sum()),
     original_peak_upright_gain_sum=float(view(self.peak_gain)[k].sum()),peak_gain_is_not_recovery_credit=True,maximum_source_stable_seconds=float((self.maximum_stable_ticks[:,k].amax() if phase is None else self.maximum_stable_ticks[phase,k].amax()))/100,
     maximum_live_profile_seconds=float((self.live_seconds[:,k].amax() if phase is None else self.live_seconds[phase,k].amax())),no_inherited_graduation=True))
  return rows
 def export(self,path):
  import numpy as np
  ph,key,env=(self.count>0).nonzero(as_tuple=True);idx=(ph,key,env);data=dict(phase=ph.cpu().numpy(),profile=key.cpu().numpy(),env_id=env.cpu().numpy(),population_controls=self.count[idx].cpu().numpy())
  for name,value in (('attempt_profile_exposures',self.attempt_exposure),('terminated',self.terminated),('truncated',self.truncated),('original_new_credit_events',self.credits),('original_peak_gain_sum',self.peak_gain),('maximum_stable_ticks',self.maximum_stable_ticks),('maximum_live_seconds',self.live_seconds)):data[name]=value[idx].cpu().numpy()
  for j,name in enumerate(('upright_deficit','root_speed','angular_speed','height_abs_from_point25','body_vx_abs','yaw_abs')):data[name+'_sum']=self.errors[ph,j,key,env].cpu().numpy()
  for j,name in enumerate(self.reasons):data['reason_'+name]=self.reason[ph,j,key,env].cpu().numpy()
  whole_key,whole_env=(self.whole_attempt_exposure>0).nonzero(as_tuple=True);data.update(whole_profile=whole_key.cpu().numpy(),whole_env_id=whole_env.cpu().numpy(),whole_attempt_profile_exposures=self.whole_attempt_exposure[whole_key,whole_env].cpu().numpy())
  with Path(path).open('xb') as f:np.savez_compressed(f,**data)
class E3Panel(LosslessSnapshot):
 def __init__(self,e,t,out,task,ground_module=None):
  super().__init__(t,e.num_envs,t.zeros(0,device=e.device,dtype=t.long));self.real=e;self.out=Path(out);self.task=task;self.robot=e.scene['robot'];self.cmd=e.command_manager.get_term('twist')
  assert not e.e3_capture and not e.e3_stepping and e.step_dt==.02 and e.physics_dt==.0025 and e.cfg.decimation==8 and e._physics_action_delay.queue.control_us==20000
  assert self.cmd.manual_evaluation_mode and not bool(self.cmd.command.any()) and len(e.e3_shapes)==34
  self.ground=OriginalFlatHeightProvider(e,t,task['ground_provider_contract'],ground_module)
  self.book=E3Book(t,e.num_envs,e.device,e.termination_manager.active_terms);self.episode=t.zeros(e.num_envs,device=e.device,dtype=t.long)
  self.frame=None;self.context=None;self.calls=0;self.trace_controls=[];self.trace_bytes=0;self.trace_limited=False;self.apply_calls={'legs':0,'wheels':0};self.installed=False
  self.stream=gzip.open(self.out/'E3_selected_recipe_actual_domain.jsonl.gz','xb');self.old_apply=e._physics_action_delay.queue.apply;self.old_reset=e._reset_idx;panel=self
  def apply(key,tick):
   value=panel.old_apply(key,tick);panel.apply_calls[key]+=1
   if panel.frame is not None:panel.frame['physical_queue_targets'].append(dict(group=key,tick=int(tick),target=panel._snapshot(value),receipt=panel._snapshot(e._physics_action_delay.queue.receipt(key,tick))))
   return value
  def reset(this,ids):
   result=panel.old_reset(ids);selected=t.as_tensor(ids,device=e.device,dtype=t.long);panel.episode[selected]+=1
   if panel.frame is not None:panel.frame['reset_ids_after_terminal'].append(selected.cpu().tolist())
   return result
  e._physics_action_delay.queue.apply=apply;e._reset_idx=types.MethodType(reset,e);self.installed=True
 def physical(self):
  r=self.robot;e=self.real
  return dict(ids=self.selected.cpu().tolist(),run_local_episode_uid=self._snapshot(self.episode),root13=self._snapshot(tensor(r.data.root_state_w)),q30=self._snapshot(tensor(r.data.joint_pos)),dq30=self._snapshot(tensor(r.data.joint_vel)),cached_applied_torque=self._snapshot(tensor(r.data.applied_torque)),original_source_ground_world_z=self._snapshot(self.ground.ground_z()),cached_contact_impulse=self._snapshot(e._integrated_contact.impulse),cached_contact_history=self._snapshot(e._integrated_contact.history),phase_state=self._snapshot(e.recovery.state_dict()),cached_published_mode=self._snapshot(e._mod4_mode_bit))
 def domain(self):
  e=self.real
  return self._snapshot(dict(sensor=e._sensor_mild.state_dict(),feedback=e._feedback_delay_mild.state_dict(),queue=e._physics_action_delay.state_dict(),pressure=e._spring_pressure.state_dict(),damping=e._gas_damping.state_dict(),COM=e._chassis_com.state_dict(),PD=e._explicit_pd.state_dict(),actual_cached_stiffness_N_m=tensor(self.robot.data.joint_stiffness)[:,e._spring_pressure.ids],nominal_stiffness_N_m=e._spring_pressure.nominal))
 def begin(self,index,obs):
  p=self.real.recovery;t=self.t;key=profile_key(t,p.recipe,p.age)
  self.context=dict(key=key,phase=0 if index<100 else 1,episode=self.episode.clone(),recipe=p.recipe.clone(),age=p.age.clone(),request=upcoming_request(t,p.recipe,p.age),credited=p.credited.clone(),peak=p.peak.clone())
  self.start_tick=int(self.real._integrated_contact.tick);self.start_fb=int(self.real._feedback_100hz_tick);self.calls=0;self.frame=None
  if not self.trace_limited and (index<24 or (index>=100 and (index-100)%25==0)):
   self.selected=t.cat([(p.recipe==k).nonzero(as_tuple=True)[0][:2] for k in range(13)])
   self.frame=dict(control=index+1,source_kind='E3_PUBLIC_RECOVERY',profile=self._snapshot(key),phase_before_original_begin=self._snapshot(p.state_dict()),upcoming_request_expected_from_original_begin_formula=self._snapshot(self.context['request']),before=self.physical(),DR_before=self.domain(),actual_command3=self._snapshot(self.cmd.command),observations_given_to_original_actor=self._snapshot(obs),physical_queue_targets=[],reset_ids_after_terminal=[])
 def requested(self,action):
  if self.frame is not None:self.frame['raw_actor_ingress6']=self._snapshot(action)
 def terminal(self):
  self.calls+=1;assert self.calls==1;t=self.t;e=self.real;r=self.robot;p=e.recovery;root=tensor(r.data.root_state_w);g=tensor(r.data.projected_gravity_b)[:,2];tm=e.termination_manager
  after=dict(episode=self.episode.clone(),recipe=p.recipe,age=p.age,request=p.request,credited=p.credited,stable=p.stable,peak=p.peak,errors=[1-((1-g)/2).clamp(0,1),root[:,7:10].norm(dim=-1),root[:,10:13].norm(dim=-1),(self.ground.height()-.25).abs(),tensor(r.data.root_lin_vel_b)[:,0].abs(),tensor(r.data.root_ang_vel_b)[:,2].abs()])
  self.book.observe(self.context,after,tm.terminated,tm.time_outs,[tm.get_term(k).bool() for k in self.book.reasons],[e.recovery_original_soft['bad_orientation'].bool(),e.recovery_original_soft['base_contact'].bool()])
  if self.frame is not None:self.frame.update(terminal_before_autoreset=self.physical(),DR_terminal=self.domain(),original_phase_update_already_completed=True,action_manager_ingress6=self._snapshot(e.action_manager.action),terminated=self._snapshot(tm.terminated),truncated=self._snapshot(tm.time_outs),reasons={k:self._snapshot(tm.get_term(k).bool()) for k in self.book.reasons},original_raw_soft=self._snapshot(e.recovery_original_soft))
 def after(self,index):
  assert self.calls==1 and int(self.real._integrated_contact.tick)-self.start_tick==8 and int(self.real._feedback_100hz_tick)-self.start_fb==2
  if self.frame is not None:
   for key in ('legs','wheels'):assert [x['tick'] for x in self.frame['physical_queue_targets'] if x['group']==key]==list(range(self.start_tick,self.start_tick+8))
   self.frame['after_autoreset']=self.physical();raw=(json.dumps(self.frame,separators=(',',':'),allow_nan=False)+'\n').encode()
   if self.trace_bytes+len(raw)<=256*1024**2:self.stream.write(raw);self.trace_bytes+=len(raw);self.trace_controls.append(index+1)
   else:self.trace_limited=True
  self.frame=None
 def uninstall(self):
  if self.installed:self.real._physics_action_delay.queue.apply=self.old_apply;self.real._reset_idx=self.old_reset;self.installed=False
  self.stream.close()
 def finish(self):
  self.uninstall();self.book.export(self.out/'E3_recipe_phase_env_actual_denominators.npz')
  value=dict(kind='E3_97_original13recipe_phase_domain_diagnostic_v1',profiles=self.book.summary(),source_model_SHA=self.task['source_SHA'],original_source_kind='E3_PUBLIC_RECOVERY',original_request_age_lt300_public100Hz_ticks_3s=True,original_stable_ge50_public100Hz_ticks_point5s=True,original_upright_gravity_z_lt=-.984807753,original_root_speed_lt=.03,original_angular_speed_lt=.2,initial_source_phase_restored_then_original_new_fallen_episode=True,run_local_reset_UID_increments=int(self.episode.sum()),unique_env_reset=int((self.episode>0).sum()),trace_controls=self.trace_controls,trace_bytes=self.trace_bytes,trace_limited=self.trace_limited,events_not_unique_env_and_attempt_profile_exposure_not_global_attempt_count=True,source_recipe12_baseline_not_E2_or_W35_standing_complement=True,extra_contact_capture_enabled=False,complete_WM_dataset=False,skill_graduation=False)
  with (self.out/'E3_PROFILE_DOMAIN_DIAGNOSTIC_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2,allow_nan=False)
