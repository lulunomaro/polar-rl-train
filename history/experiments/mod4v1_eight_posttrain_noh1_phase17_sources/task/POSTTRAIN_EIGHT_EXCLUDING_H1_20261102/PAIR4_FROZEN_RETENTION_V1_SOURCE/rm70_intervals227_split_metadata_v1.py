"""Observer-only213-style UID/pre-reset accumulators for ORIGINAL RM70 commands.

No torch import, sampler/RNG/actor/physics call or command writes. Rough BODY
commands have no usable world target:retained cmd.direction is random/unused.
"""
from pathlib import Path
import hashlib,json,math


from positional_rows227 import PositionalRows227 as Rows227
from rm70_published_split_observer_v1 import empty_counts,observe_row,publish_counts


class RM70Intervals227:
 def __init__(self,t,n,device,out,model):
  self.t=t;self.n=n;self.device=device;self.ids=t.arange(n,device=device);self.rows=Rows227(out,model)
  self._published_split_counts=empty_counts();self._published_book_constructor_label=model
  def zeros(dtype=None):return t.zeros(n,device=device,dtype=dtype or t.float32)
  self.uid=zeros(t.long);self.episode=zeros(t.long);self.count=zeros(t.long);self.first=zeros(t.long)
  self.segment=zeros(t.long);self.original_counter=zeros(t.long);self.route_source_episode=zeros(t.long)
  self.active=zeros(t.bool);self.known=zeros(t.bool);self.term=zeros(t.bool);self.timeout=zeros(t.bool)
  self.axis=zeros();self.v=zeros();self.stand=zeros(t.bool);self.source_episode=zeros(t.long)
  self.along=zeros();self.cross=zeros();self.turn=zeros();self.refalong=zeros();self.refcross=zeros();self.refyaw=zeros()
  self.command=t.zeros((n,3),device=device);self.unused_direction=zeros();self.first_tick=zeros(t.long)
  self.closure=zeros();self.mimic=zeros();self.reason={};self.pending_reset=zeros(t.bool)
  self.route_active=zeros(t.bool);self.route_known=zeros(t.bool);self.route_start=zeros(t.long);self.route_goal=zeros(t.long)-1
  self.route_far=zeros(t.bool);self.route_minx=zeros();self.route_maxx=zeros();self.route_first_uid=zeros(t.long)
  self.route_term=zeros(t.bool);self.route_timeout=zeros(t.bool);self.route_clean_goal=zeros(t.bool)
  self.control=-1;self.armed=False;self.last_packet=None;self.depth={};self.errors=[]
  self.events=dict(opened_commands=0,natural_complete_intervals=0,complete_kinematic_bounds_met=0,
   complete_kinematic_false=0,partial_intervals=0,source_parameter_breaks=0,route_episodes=0,
   route_goal_entries=0,observed_nonterminal_catalog_goal_facts=0,reset_events=0)
  self.reason_counts={};self.term_controls=0;self.timeout_controls=0
 def tensor(self,v):return v.torch if hasattr(v,'torch') else v
 def normalize(self,term,ids):
  allids=self.t.arange(term.num_envs,device=term.device)
  return allids if ids is None else allids[ids] if isinstance(ids,slice) else self.t.as_tensor(ids,device=term.device,dtype=self.t.long)
 def install(self,Command):
  book=self;old_sample=Command._resample;old_reset=Command.reset
  inherited={k:k not in Command.__dict__ for k in ('_resample','reset')}
  def sample(term,ids):
   selected=book.normalize(term,ids);prior=term.time_left[selected].clone()
   within=bool(book.depth.get(id(term),0))
   if book.armed:
    natural=book.t.zeros(book.n,device=book.device,dtype=book.t.bool)
    natural[selected]=(prior<=0)&(not within);book.close(selected,'original_resample',natural)
   value=old_sample(term,ids)
   try:
    packet=dict(term=term,ids=selected.clone(),tick=int(term._env._sim_step_counter),timer=term.time_left[selected].clone(),
     command=term.command[selected].clone(),written_heading=term._command_heading[selected].clone(),within_reset=within)
    book.last_packet=packet
    if book.armed:book.open(term,selected,True)
   except Exception as exc:
    if len(book.errors)<32:book.errors.append(type(exc).__name__+': '+str(exc))
   return value
  def reset(term,*a,**kw):
   selected=book.normalize(term,kw.get('env_ids',a[0] if a else None))
   if book.armed:
    book.close(selected,'original_reset',None);book.close_routes(selected,'original_reset')
    book.episode[selected]+=1;book.pending_reset[selected]=True;book.events['reset_events']+=len(selected)
   book.depth[id(term)]=book.depth.get(id(term),0)+1
   try:return old_reset(term,*a,**kw)
   finally:book.depth[id(term)]-=1
  Command._resample=sample;Command.reset=reset
  def uninstall():
   for name,old in (('_resample',old_sample),('reset',old_reset)):
    if inherited[name]:delattr(Command,name)
    else:setattr(Command,name,old)
  self.uninstall=uninstall
 def arm(self,real,cmd):
  self.real=real;self.cmd=cmd;self.armed=True;self.control=0
  p=self.last_packet
  known=bool(p is not None and p['term'] is cmd and p['within_reset'] and p['tick']==0 and
   len(p['ids'])==self.n and self.t.equal(p['ids'],self.ids) and self.t.equal(p['timer'],cmd.time_left) and
   self.t.equal(p['command'],cmd.command) and int(real._sim_step_counter)==0)
  self.open(cmd,self.ids,known);self.pending_reset[:]=known
  return dict(initial_start_observed=known,left_censored_if_false=not known,no_fabricated_initial_resample=True)
 def open(self,cmd,ids,known,increment_uid=True):
  t=self.t
  if increment_uid:self.uid[ids]+=1;self.segment[ids]=0
  else:self.segment[ids]+=1
  self.original_counter[ids]=cmd.command_counter[ids]
  self.active[ids]=True;self.known[ids]=known;self.count[ids]=0
  self.first[ids]=self.control;self.command[ids]=cmd.command[ids];self.v[ids]=cmd.command[ids,0].abs()
  self.axis[ids]=cmd._command_heading[ids]+(cmd.command[ids,0]<0).float()*math.pi
  self.unused_direction[ids]=cmd.direction[ids];self.stand[ids]=cmd.is_standing_env[ids]
  for x in (self.along,self.cross,self.turn,self.refalong,self.refcross,self.refyaw,self.closure,self.mimic):x[ids]=0
  self.term[ids]=False;self.timeout[ids]=False
  for x in self.reason.values():x[ids]=False
  self.events['opened_commands']+=len(ids)
 def begin(self,control,xy,heading):
  t=self.t;self.control=control;cmd=self.cmd
  episode_changed=self.active&self.count.gt(0)&(self.real._e1_episode!=self.source_episode)
  if episode_changed.any():
   ids=self.ids[episode_changed];self.close_routes(ids,'source_E1_episode_changed_without_observed_reset');self.pending_reset[ids]=False
  changed=self.active&self.count.gt(0)&((cmd.command!=self.command).any(1)|episode_changed)
  if changed.any():
   ids=self.ids[changed];self.close(ids,'command_or_E1_episode_changed_without_outer_event',None);self.open(cmd,ids,False,increment_uid=False)
   self.events['source_parameter_breaks']+=len(ids)
  new=self.ids[self.active&(self.count==0)]
  self.first[new]=control;self.first_tick[new]=int(self.real._sim_step_counter);self.source_episode[new]=self.real._e1_episode[new]
  ids=self.ids[~self.route_active]
  self.route_active[ids]=True;self.route_known[ids]=self.pending_reset[ids];self.pending_reset[ids]=False
  self.route_start[ids]=control;self.route_goal[ids]=-1;self.route_far[ids]=False;self.route_first_uid[ids]=self.uid[ids]
  self.route_source_episode[ids]=self.real._e1_episode[ids]
  local=xy-self.real.scene.env_origins[:,:2];self.route_minx[ids]=local[ids,0];self.route_maxx[ids]=local[ids,0]
  self.route_term[ids]=False;self.route_timeout[ids]=False;self.route_clean_goal[ids]=False
  self.before_xy=xy.clone();self.before_heading=heading.clone();self.acted_command=cmd.command.clone()
  self.begin_tick=int(self.real._sim_step_counter)
 def terminal(self,frame,tm):
  t=self.t;root=self.tensor(frame['root']);xy=root[:,:2]
  qx,qy,qz,qw=(root[:,k] for k in (3,4,5,6));heading=t.atan2(2*(qw*qz+qx*qy),1-2*(qy*qy+qz*qz))
  assert int(self.real._sim_step_counter)==self.begin_tick+8
  d=xy-self.before_xy;co=t.cos(self.axis);si=t.sin(self.axis);angle=self.before_heading-self.axis
  self.along+=d[:,0]*co+d[:,1]*si;self.cross+=-d[:,0]*si+d[:,1]*co
  self.turn+=t.atan2(t.sin(heading-self.before_heading),t.cos(heading-self.before_heading))
  self.refalong+=.02*(self.acted_command[:,0]*t.cos(angle)-self.acted_command[:,1]*t.sin(angle))
  self.refcross+=.02*(self.acted_command[:,0]*t.sin(angle)+self.acted_command[:,1]*t.cos(angle));self.refyaw+=.02*self.acted_command[:,2]
  self.count+=1;self.term|=tm.terminated;self.timeout|=tm.time_outs
  self.closure=t.maximum(self.closure,self.tensor(frame['closure']));self.mimic=t.maximum(self.mimic,self.tensor(frame['mimic']))
  non_timeout=t.zeros_like(tm.terminated);timeouts=t.zeros_like(tm.time_outs)
  for name in tm.active_terms:
   mask=tm.get_term(name).bool()
   if name not in self.reason:self.reason[name]=t.zeros_like(mask)
   self.reason[name]|=mask;self.reason_counts[name]=self.reason_counts.get(name,0)+int(mask.sum())
   if tm.get_term_cfg(name).time_out:timeouts|=mask
   else:non_timeout|=mask
  assert t.equal(non_timeout,tm.terminated) and t.equal(timeouts,tm.time_outs)
  self.term_controls+=int(tm.terminated.sum());self.timeout_controls+=int(tm.time_outs.sum())
  self.route_term|=tm.terminated;self.route_timeout|=tm.time_outs
  local=xy-self.real.scene.env_origins[:,:2];self.route_minx=t.minimum(self.route_minx,local[:,0]);self.route_maxx=t.maximum(self.route_maxx,local[:,0])
  reverse=(self.ids%2).bool();far=t.where(reverse,local[:,0]<=6.334789943753937,local[:,0]>=8.741212671140003)
  self.route_far|=far;target=t.where(reverse,t.full_like(self.v,5.85),t.full_like(self.v,9.15))
  goal=(local[:,0]-target).square()+(local[:,1]-6.45).square()<=.35**2
  first=goal&(self.route_goal<0);self.route_goal[first]=self.control;self.events['route_goal_entries']+=int(first.sum())
  self.route_clean_goal[first]=(self.route_known&self.route_far&~self.route_term&~self.route_timeout)[first]
 def emit_columns(self,columns,extra):
  cpu={k:v.detach().cpu().tolist() for k,v in columns.items()}
  for i in range(len(cpu['env_id'])):
   row=dict(**extra, **{k: v[i] for k, v in cpu.items()})
   self._published_split_counts=observe_row(self._published_split_counts,row)
   self.rows.append(row)
 def close(self,ids,reason,natural):
  t=self.t;ids=ids[self.active[ids]&(self.count[ids]>0)]
  if not len(ids):return
  seconds=self.count[ids].float()*.02;along=self.along[ids]/seconds;cross=self.cross[ids]/seconds;yaw=(self.turn[ids]-self.refyaw[ids])/seconds
  tol=t.maximum(t.full_like(seconds,.03),.1*self.v[ids]);kin=(along-self.v[ids]).abs().le(tol)&cross.abs().le(tol)&yaw.abs().le(.2)
  complete=t.zeros(len(ids),device=self.device,dtype=t.bool)
  if natural is not None:
   #Caller supplies natural timer status in the selected batch's order.
   lookup=t.zeros(self.n,device=self.device,dtype=t.bool)
   #Natural mask is full-size from wrapper,or reconstructed there before call.
   if natural.shape==(self.n,):lookup=natural
   else:raise ValueError('Need full per-env natural timer mask')
   complete=lookup[ids]&self.known[ids]&~self.term[ids]&~self.timeout[ids]
  cols=dict(env_id=ids,episode_uid=self.episode[ids],command_uid=self.uid[ids],source_E1_episode=self.source_episode[ids],
   original_command_counter=self.original_counter[ids],same_UID_segment=self.segment[ids],
   first_control=self.first[ids],last_control=t.full_like(ids,self.control),controls=self.count[ids],seconds=seconds,
   first_physics_tick=self.first_tick[ids],last_physics_tick=self.first_tick[ids]+8*self.count[ids],
   start_observed=self.known[ids],standing=self.stand[ids],sampled_BODY_command=self.command[ids],nominal_speed=self.v[ids],
   fixed_observed_heading_axis_rad=self.axis[ids],unused_retained_random_direction=self.unused_direction[ids],
   along_speed_m_s=along,cross_speed_m_s=cross,along_nominal_error_m_s=along-self.v[ids],
   BODY_reference_along_speed_m_s=self.refalong[ids]/seconds,BODY_reference_cross_speed_m_s=self.refcross[ids]/seconds,
   BODY_reference_along_tracking_error_m_s=(self.along[ids]-self.refalong[ids])/seconds,
   BODY_reference_cross_tracking_error_m_s=(self.cross[ids]-self.refcross[ids])/seconds,
   actual_signed_yaw_rad=self.turn[ids],commanded_signed_yaw_rad=self.refyaw[ids],signed_yaw_error_rad_s=yaw,
   original_along_cross_tolerance=tol,original_kinematic_bounds_met=kin,natural_complete_nonterminal_interval=complete,
   complete_interval_bounds_fact=complete&kin,terminated_before_reset=self.term[ids],truncated_before_reset=self.timeout[ids],
   maximum_closure_m=self.closure[ids],maximum_mimic_rad=self.mimic[ids])
  for k,v in self.reason.items():cols['original_terminal_reason_'+k]=v[ids]
  self.emit_columns(cols,dict(record_type='same_UID_original_RM70_command',end_reason=reason,signed_yaw_tolerance=.2,
   axis_semantics='Original effective sampled heading +pi if BODYvx<0;not unused random cmd.direction',
   not_full_expert_or_signed2pi_cycle_graduation=True))
  self.events['natural_complete_intervals']+=int(complete.sum());self.events['complete_kinematic_bounds_met']+=int((complete&kin).sum())
  self.events['complete_kinematic_false']+=int((complete&~kin).sum());self.events['partial_intervals']+=int((~complete).sum());self.active[ids]=False
 def close_routes(self,ids,reason):
  ids=ids[self.route_active[ids]]
  if not len(ids):return
  valid=self.route_clean_goal[ids]
  self.emit_columns(dict(env_id=ids,episode_uid=self.episode[ids],source_E1_episode=self.route_source_episode[ids],observed_reset_origin=self.route_known[ids],
   first_control=self.route_start[ids],last_control=self.t.full_like(ids,self.control),first_command_uid=self.route_first_uid[ids],last_command_uid=self.uid[ids],
   catalog_goal_entry_control=self.route_goal[ids],entire_original_CAD_x_span_reached=self.route_far[ids],
   local_x_min=self.route_minx[ids],local_x_max=self.route_maxx[ids],terminated_before_reset=self.route_term[ids],truncated_before_reset=self.route_timeout[ids],
   observed_nonterminal_catalog_goal_fact=valid,
   non_timeout_failure_by_episode_end_after_goal_observed=self.route_term[ids]&(self.route_goal[ids]>=0)),dict(record_type='same_episode_original_catalog_route',end_reason=reason,
    original_route_x=[5.85,9.15],original_route_y=6.45,original_catalog_goal_radius=.35,
    goal_is_observer_only_not_a_new_reward_reset_or_skill_gate=True))
  self.events['route_episodes']+=len(ids);self.events['observed_nonterminal_catalog_goal_facts']+=int(valid.sum());self.route_active[ids]=False
 def finish(self):
  self.armed=False
  self.close(self.ids,'window_end_partial',None);self.close_routes(self.ids,'window_end')
  return dict(events=self.events,original_reason_counts=self.reason_counts,non_timeout_environment_controls=self.term_controls,
   timeout_environment_controls=self.timeout_controls,producer=self.rows.finish(),diagnostic_errors=self.errors,
   published_moving_standing_counts=publish_counts(self._published_split_counts,self.events,self._published_book_constructor_label),
   full_expert_skill='UNKNOWN',unexposed_profiles=['old flat signed1..1.5','world .5 + signedyaw1..2 full2pi','pure/transition spins','other expert domains'],
   no_new_aggregate_graduation_rate=True,full_SuperMimic_conversion=False)
