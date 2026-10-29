"""E2-specific read-only metrics/domain hooks; no SDK/actor/RNG/physics call."""
import gzip,json,math,types
from pathlib import Path
from lossless_snapshot_pinned75d683 import LosslessSnapshot
from e2_original_profile_catalog_candidate_v1 import PROFILES,TRANSITION_PHASES,classify,transition_phase

def tensor(x):return x.torch if hasattr(x,'torch') else x


class E2Book:
    def __init__(self,t,n,device,reasons):
        self.t=t;self.n=n;self.ids=t.arange(n,device=device);self.reasons=tuple(reasons)
        self.count=t.zeros((2,10,n),device=device,dtype=t.long)
        self.errors=t.zeros((2,3,10,n),device=device)
        self.terminated=t.zeros_like(self.count);self.truncated=t.zeros_like(self.count)
        self.reason=t.zeros((2,len(reasons),10,n),device=device,dtype=t.long)
        self.cycles=t.zeros_like(self.count);self.windows=t.zeros_like(self.count)
        self.cycle_seconds=t.zeros_like(self.count,dtype=t.float32)
        self.cycle_projection=t.zeros_like(self.cycle_seconds);self.cycle_reference=t.zeros_like(self.cycle_seconds)
        self.cycle_nominal_abs_distance=t.zeros_like(self.cycle_seconds);self.cycle_reference_abs_distance=t.zeros_like(self.cycle_seconds)
        self.maxlive=t.zeros_like(self.cycle_seconds)
        self.phase_count=t.zeros((2,9,2,n),device=device,dtype=t.long)
        self.prev_key=t.full((n,),-1,device=device,dtype=t.long);self.prev_episode=self.prev_key.clone();self.prev_command=self.prev_key.clone()
        self.prev_live=t.zeros(n,device=device,dtype=t.bool);self.prev_phase=-1
        self.age=t.zeros(n,device=device);self.turn=self.age.clone();self.elapsed=self.age.clone();self.ref_distance=self.age.clone()
        self.start_xy=t.zeros((n,2),device=device)

    def observe(self,c,after,terminated,truncated,reason_masks):
        t=self.t;key=c['key'];phase=c['phase'];idx=(key,self.ids);live=~(terminated|truncated)
        assert bool(((key>=0)&(key<10)).all()) and key.shape==(self.n,)
        self.count[phase][idx]+=1
        for j,error in enumerate(after['errors']):
            assert error.shape==(self.n,) and bool(t.isfinite(error).all())
            self.errors[phase,j][idx]+=error
        self.terminated[phase][idx]+=terminated.long();self.truncated[phase][idx]+=truncated.long()
        for j,mask in enumerate(reason_masks):self.reason[phase,j][idx]+=mask.long()
        same=(key==self.prev_key)&(c['episode']==self.prev_episode)&(c['command_uid']==self.prev_command)&self.prev_live
        if phase!=self.prev_phase:same=t.zeros_like(same)
        self.age=t.where(same,self.age+.02,t.full_like(self.age,.02))
        self.maxlive[phase][idx]=t.maximum(self.maxlive[phase][idx],t.where(live,self.age,t.zeros_like(self.age)))
        self.start_xy=t.where(same[:,None],self.start_xy,c['before_xy'])
        self.turn=t.where(same,self.turn+after['heading_delta'],after['heading_delta'])
        self.elapsed=t.where(same,self.elapsed+.02,t.full_like(self.elapsed,.02))
        reference=c['reference_projection']*.02
        self.ref_distance=t.where(same,self.ref_distance+reference,reference)
        # Constant pure and moving only; transition reversal has its own phase exposure.
        active=((key==4)|(key==5)|(key==8)|(key==9))&live
        signed_angle=self.turn*t.sign(c['signed_yaw'])
        turns=t.floor(signed_angle.clamp_min(0)/(2*math.pi)).long()
        completed=active&(turns>0)
        self.cycles[phase][idx]+=t.where(completed,turns,t.zeros_like(turns))
        self.windows[phase][idx]+=completed.long()
        dxy=after['xy']-self.start_xy
        projection=dxy[:,0]*t.cos(c['direction'])+dxy[:,1]*t.sin(c['direction'])
        for table,value in ((self.cycle_seconds,self.elapsed),(self.cycle_projection,projection),(self.cycle_reference,self.ref_distance),
                            (self.cycle_nominal_abs_distance,(projection-.5*self.elapsed).abs()),
                            (self.cycle_reference_abs_distance,(projection-self.ref_distance).abs())):
            table[phase][idx]+=t.where(completed,value,t.zeros_like(value))
        # Real sampled endpoints, no interpolated sub-control motion or residual credit.
        self.start_xy=t.where(completed[:,None],after['xy'],self.start_xy)
        clear=completed|~live
        self.turn=t.where(clear,t.zeros_like(self.turn),self.turn)
        self.elapsed=t.where(clear,t.zeros_like(self.elapsed),self.elapsed)
        self.ref_distance=t.where(clear,t.zeros_like(self.ref_distance),self.ref_distance)
        transitioning=((key==6)|(key==7))&c['written_phase_valid']
        ids=self.ids[transitioning]
        if len(ids):
            bins=transition_phase(t,c['written_phase'][ids])
            self.phase_count[phase,bins,key[ids]-6,ids]+=1
        self.prev_key=key.clone();self.prev_episode=c['episode'].clone();self.prev_command=c['command_uid'].clone();self.prev_live=live.clone();self.prev_phase=phase

    def summary(self):
        out=[]
        for name,ph in (('whole',None),('warmup',0),('steady',1)):
            view=lambda x:x.sum(0) if ph is None else x[ph]
            count=view(self.count);errors=view(self.errors);term=view(self.terminated);trunc=view(self.truncated);cycles=view(self.cycles);windows=view(self.windows)
            sec=view(self.cycle_seconds);distance=view(self.cycle_projection);ref=view(self.cycle_reference);nomerr=view(self.cycle_nominal_abs_distance);referr=view(self.cycle_reference_abs_distance)
            for k,label in enumerate(PROFILES):
                den=int(count[k].sum());seconds=float(sec[k].sum());applicable=k in (8,9)
                out.append(dict(phase=name,profile=k,label=label,population_controls=den,unique_exposed_env=int((count[k]>0).sum()),
                    body_forward_MAE=float(errors[0,k].sum())/den if den else None,yaw_MAE=float(errors[1,k].sum())/den if den else None,height_MAE=float(errors[2,k].sum())/den if den else None,
                    terminated_events=int(term[k].sum()),unique_terminated_env=int((term[k]>0).sum()),truncated_events=int(trunc[k].sum()),unique_truncated_env=int((trunc[k]>0).sum()),
                    measured_signed_turn_events=int(cycles[k].sum()),complete_sampled_window_events=int(windows[k].sum()),unique_env_with_sampled_window=int((windows[k]>0).sum()),
                    sampled_window_seconds=seconds,actual_cycle_projected_progress_m_s=float(distance[k].sum())/seconds if seconds and applicable else None,
                    integrated_command_reference_progress_m_s=float(ref[k].sum())/seconds if seconds and applicable else None,
                    nominal_half_m_s_cycle_abs_error_time_weighted=float(nomerr[k].sum())/seconds if seconds and applicable else None,
                    integrated_reference_cycle_abs_error_time_weighted=float(referr[k].sum())/seconds if seconds and applicable else None,
                    no_graduation_threshold_invented=True))
        return out

    def export(self,path):
        import numpy as np
        ph,k,env=(self.count>0).nonzero(as_tuple=True);idx=(ph,k,env)
        data=dict(phase=ph.cpu().numpy(),profile=k.cpu().numpy(),env_id=env.cpu().numpy(),population_controls=self.count[idx].cpu().numpy())
        for name,value in (('terminated',self.terminated),('truncated',self.truncated),('turn_events',self.cycles),('sampled_windows',self.windows),('window_seconds',self.cycle_seconds),('projected_distance_m',self.cycle_projection),('reference_distance_m',self.cycle_reference),('maximum_live_seconds',self.maxlive)):
            data[name]=value[idx].cpu().numpy()
        for j,name in enumerate(('body_forward_error_sum','yaw_error_sum','height_error_sum')):data[name]=self.errors[ph,j,k,env].cpu().numpy()
        for j,name in enumerate(self.reasons):data['reason_'+name]=self.reason[ph,j,k,env].cpu().numpy()
        with Path(path).open('xb') as f:np.savez_compressed(f,**data)


class E2Panel(LosslessSnapshot):
    def __init__(self,e,t,out,task):
        super().__init__(t,e.num_envs,t.zeros(0,device=e.device,dtype=t.long))
        self.real=e;self.out=Path(out);self.task=task;self.robot=e.scene['robot'];self.cmd=e.command_manager.get_term('twist')
        assert not self.cmd.manual_evaluation_mode and self.cmd.progress_goal==.5 and self.cmd.pure_max==4*math.pi
        assert e.step_dt==.02 and e.physics_dt==.0025 and e.cfg.decimation==8
        assert hasattr(e,'_mod4_ground_z') and not e._own_native_capture
        self.names=tuple(e.termination_manager.active_terms);self.book=E2Book(t,e.num_envs,e.device,self.names)
        self.episode=t.zeros(e.num_envs,device=e.device,dtype=t.long);self.command_uid=self.episode.clone()
        self.written_phase=t.zeros(e.num_envs,device=e.device);self.written_valid=t.zeros(e.num_envs,device=e.device,dtype=t.bool)
        self.frame=None;self.context=None;self.calls=0;self.trace_controls=[];self.trace_bytes=0;self.trace_limited=False
        self.apply_calls={'legs':0,'wheels':0}
        self.stream=gzip.open(self.out/'E2_selected_profile_actual_domain.jsonl.gz','xb')
        self.old_apply=e._physics_action_delay.queue.apply;self.old_reset=e._reset_idx
        self.old_resample=self.cmd._resample_command;self.old_write=self.cmd._write_dynamic
        panel=self
        def apply(key,tick):
            value=panel.old_apply(key,tick)
            panel.apply_calls[key]+=1
            if panel.frame is not None:panel.frame['queue_targets_before_original_apply'].append(dict(group=key,tick=int(tick),target=panel._snapshot(value),receipt=panel._snapshot(e._physics_action_delay.queue.receipt(key,tick))))
            return value
        def reset(this,ids):
            result=panel.old_reset(ids);selected=t.as_tensor(ids,device=e.device,dtype=t.long);panel.episode[selected]+=1
            if panel.frame is not None:panel.frame['reset_ids_after_terminal'].append(selected.cpu().tolist())
            return result
        def write(this,ids):
            before=this.phase_elapsed[ids].clone();result=panel.old_write(ids)
            panel.written_phase[ids]=before;panel.written_valid[ids]=True
            return result
        def resample(this,ids):
            result=panel.old_resample(ids);panel.command_uid[ids]+=1
            if panel.frame is not None:panel.frame['command_resample_ids'].append(t.as_tensor(ids,device=e.device,dtype=t.long).cpu().tolist())
            return result
        e._physics_action_delay.queue.apply=apply;e._reset_idx=types.MethodType(reset,e)
        self.cmd._write_dynamic=types.MethodType(write,self.cmd);self.cmd._resample_command=types.MethodType(resample,self.cmd)
        self.installed=True

    def physical(self):
        r=self.robot;e=self.real
        return dict(ids=self.selected.cpu().tolist(),episode=self._snapshot(self.episode),command_uid=self._snapshot(self.command_uid),root13=self._snapshot(tensor(r.data.root_state_w)),q30=self._snapshot(tensor(r.data.joint_pos)),dq30=self._snapshot(tensor(r.data.joint_vel)),cached_applied_torque=self._snapshot(tensor(r.data.applied_torque)),cached_ground_z=self._snapshot(e._mod4_ground_z),cached_contact_impulse=self._snapshot(e._integrated_contact.impulse),cached_contact_history=self._snapshot(e._integrated_contact.history))

    def domain(self):
        e=self.real
        return self._snapshot(dict(sensor=e._sensor_mild.state_dict(),feedback=e._feedback_delay_mild.state_dict(),queue=e._physics_action_delay.state_dict(),pressure=e._spring_pressure.state_dict(),damping=e._gas_damping.state_dict(),COM=e._chassis_com.state_dict(),PD=e._explicit_pd.state_dict(),actual_cached_stiffness_N_m=tensor(self.robot.data.joint_stiffness)[:,e._spring_pressure.ids],nominal_stiffness_N_m=e._spring_pressure.nominal))

    def begin(self,index,obs):
        t=self.t;term=self.cmd;r=self.robot;e=self.real
        key=classify(t,term.is_standing_env,term.is_pure_spin,term.is_moving_spin,term.is_transition_spin,term.command,term.signed_yaw)
        heading=tensor(r.data.heading_w).clone();direction=term.world_direction.clone();command=term.command.clone();angle=heading-direction
        self.context=dict(key=key,phase=0 if index<100 else 1,episode=self.episode.clone(),command_uid=self.command_uid.clone(),before_xy=tensor(r.data.root_pos_w)[:,:2].clone(),heading=heading,direction=direction,command=command,signed_yaw=term.signed_yaw.clone(),written_phase=self.written_phase.clone(),written_phase_valid=self.written_valid.clone(),reference_projection=command[:,0]*t.cos(angle)-command[:,1]*t.sin(angle))
        self.start_tick=int(e._integrated_contact.tick);self.start_fb=int(e._feedback_100hz_tick);self.calls=0;self.frame=None
        if not self.trace_limited and (index<24 or (index>=100 and (index-100)%25==0)):
            self.selected=t.cat([(key==k).nonzero(as_tuple=True)[0][:2] for k in range(10)])
            self.frame=dict(control=index+1,source_kind='E2_WORLD_MOVING_SIGNED4',profile=self._snapshot(key),before=self.physical(),DR_before=self.domain(),actual_command3=self._snapshot(command),world_direction=self._snapshot(direction),raw_phase_elapsed=self._snapshot(term.phase_elapsed),written_phase=self._snapshot(self.written_phase),written_phase_valid=self._snapshot(self.written_valid),observations_given_to_original_actor=self._snapshot(obs),queue_targets_before_original_apply=[],reset_ids_after_terminal=[],command_resample_ids=[])

    def requested(self,action):
        if self.frame is not None:self.frame['raw_actor_ingress6']=self._snapshot(action)

    def terminal(self):
        self.calls+=1;assert self.calls==1
        t=self.t;e=self.real;r=self.robot;c=self.context;tm=e.termination_manager
        heading=tensor(r.data.heading_w);delta=t.atan2(t.sin(heading-c['heading']),t.cos(heading-c['heading']))
        after=dict(errors=[(c['command'][:,0]-tensor(r.data.root_lin_vel_b)[:,0]).abs(),(c['command'][:,2]-tensor(r.data.root_ang_vel_b)[:,2]).abs(),(tensor(r.data.root_pos_w)[:,2]-e._mod4_ground_z-.25).abs()],heading_delta=delta,xy=tensor(r.data.root_pos_w)[:,:2])
        self.book.observe(c,after,tm.terminated,tm.time_outs,[tm.get_term(k).bool() for k in self.names])
        if self.frame is not None:self.frame.update(terminal_before_autoreset=self.physical(),DR_terminal=self.domain(),action_manager_ingress6=self._snapshot(e.action_manager.action),terminated=self._snapshot(tm.terminated),truncated=self._snapshot(tm.time_outs),reasons={k:self._snapshot(tm.get_term(k).bool()) for k in self.names})

    def after(self,index):
        assert self.calls==1 and int(self.real._integrated_contact.tick)-self.start_tick==8 and int(self.real._feedback_100hz_tick)-self.start_fb==2
        if self.frame is not None:
            for key in ('legs','wheels'):assert [x['tick'] for x in self.frame['queue_targets_before_original_apply'] if x['group']==key]==list(range(self.start_tick,self.start_tick+8))
            self.frame['after_autoreset']=self.physical();self.frame['end_physics_tick']=int(self.real._integrated_contact.tick);self.frame['end_feedback_tick']=int(self.real._feedback_100hz_tick)
            raw=(json.dumps(self.frame,separators=(',',':'),allow_nan=False)+'\n').encode()
            if self.trace_bytes+len(raw)<=256*1024**2:self.stream.write(raw);self.trace_bytes+=len(raw);self.trace_controls.append(index+1)
            else:self.trace_limited=True
        self.frame=None

    def uninstall(self):
        if self.installed:
            self.real._physics_action_delay.queue.apply=self.old_apply;self.real._reset_idx=self.old_reset
            self.cmd._resample_command=self.old_resample;self.cmd._write_dynamic=self.old_write;self.installed=False
        self.stream.close()

    def finish(self):
        self.uninstall();self.book.export(self.out/'E2_profile_phase_env_actual_denominators.npz')
        value=dict(kind='E2_93_original_modes_profile_domain_diagnostic_v1',profiles=self.book.summary(),transition_phase_controls=self.book.phase_count.sum(-1).cpu().tolist(),transition_phase_unique_env=(self.book.phase_count>0).sum(-1).cpu().tolist(),transition_phase_names=TRANSITION_PHASES,trace_controls=self.trace_controls,trace_bytes=self.trace_bytes,trace_limited=self.trace_limited,
            source_model_SHA=self.task['source_SHA'],original_kind='E2_WORLD_MOVING_SIGNED4',original_world_progress_goal_m_s=.5,
            cycle_definition='actual same command_uid/profile/episode/phase live sampled window with net signed yaw>=2pi; endpoints quantized to20ms, no interpolated subcycles; time and displacement sums provided',
            first_written_phase_valid_initially_unknown=True,transition_full12s_same_command_graduation_not_claimed=True,
            not_instantaneous_world_progress_error=True,no_W35_G3_or_nearest250_assumption=True,complete_WM_dataset=False,skill_graduation=False)
        with (self.out/'E2_PROFILE_DOMAIN_DIAGNOSTIC_ACTUAL.json').open('x',encoding='utf-8') as f:json.dump(value,f,indent=2,allow_nan=False)
