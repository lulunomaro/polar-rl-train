"""Fresh W35 command-UID and sampled whole-cycle telemetry, not a skill gate.

Reads only caller-supplied ORIGINAL command/terminal buffers. No SDK, actor,
sampler, RNG or physics calls. Original timeout and eligibility changes remain.
"""
from pathlib import Path
import hashlib,json,math

MODEL='ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'

class TypedRows:
    def __init__(self,directory,name,schema,maximum_bytes=128*1024**2):
        self.path=Path(directory)/name;self.file=self.path.open('xb');self.hash=hashlib.sha256()
        self.bytes=0;self.rows=0;self.limit=maximum_bytes;self.limited=False;self.schema=schema;self.closed=False
    def append(self,row):
        raw=(json.dumps(dict(schema=self.schema,control_index_base=0,**row),separators=(',',':'),allow_nan=False)+'\n').encode('utf8')
        if self.bytes+len(raw)>self.limit:self.limited=True;return False
        self.file.write(raw);self.hash.update(raw);self.bytes+=len(raw);self.rows+=1;return True
    def finish(self):
        if not self.closed:self.file.close();self.closed=True
        assert self.path.stat().st_size==self.bytes
        return dict(path=str(self.path),bytes=self.bytes,SHA=self.hash.hexdigest(),rows=self.rows,
            schema=self.schema,source_SHA=MODEL,stream_SHA_produced_without_reread=True,
            retention_limited=self.limited,default_reader_transfer='metadata_only_not_JSONL_contents')

def profile_key(t,cmd):
    mode=t.zeros(cmd.num_envs,device=cmd.device,dtype=t.long)
    mode[cmd.is_standing_env]=1
    mode[cmd.linear&(cmd.linear_vx<0)]=2;mode[cmd.linear&(cmd.linear_vx>0)]=3
    mode[cmd.moving&(cmd.signed_yaw<0)]=4;mode[cmd.moving&(cmd.signed_yaw>0)]=5
    mode[cmd.eligible_flat&~cmd.is_standing_env&~cmd.linear&~cmd.moving]=6
    key=(cmd.family+1)*7+mode
    assert key.shape==(cmd.num_envs,) and bool(((key>=0)&(key<42)).all())
    return key

class W35UIDCycleBook:
    def __init__(self,t,n,device,out):
        self.t=t;self.n=n;self.device=device;self.ids=t.arange(n,device=device)
        self.uid=t.zeros(n,dtype=t.long,device=device);self.episode=self.uid.clone();self.source_episode=self.uid.clone()
        self.active=t.zeros(n,dtype=t.bool,device=device);self.known=self.active.clone()
        self.sample_key=self.uid.clone();self.first_control=self.uid.clone();self.command_controls=self.uid.clone()
        self.start_tick=self.uid.clone();self.first_acted=self.uid.clone()-1
        self.moving_controls=self.uid.clone();self.zero_controls=self.uid.clone()
        self.profile_bits=self.uid.clone();self.error=t.zeros(n,3,device=device);self.moving_error=self.error.clone()
        self.sample_command=t.zeros(n,3,device=device);self.sample_direction=t.zeros(n,device=device)
        self.sample_yaw=self.sample_direction.clone();self.start_timer=self.sample_direction.clone()
        self.closed=t.zeros(42,n,dtype=t.long,device=device)
        self.acted=self.closed.clone();self.zero=self.closed.clone();self.complete=self.closed.clone()
        self.left=self.closed.clone();self.reset=self.closed.clone();self.window=self.closed.clone()
        self.complete_controls=self.closed.clone();self.complete_moving_controls=self.closed.clone()
        self.complete_errors=t.zeros(42,3,n,device=device);self.complete_moving_errors=self.complete_errors.clone()
        self.instance_records=TypedRows(out,'W35_OBSERVED_COMMAND_UID_RECORDS_ACTUAL.jsonl','W35_observed_command_uid_v1')
        self.cycle_records=TypedRows(out,'W35_OBSERVED_SAME_UID_SIGNED_CYCLE_RECORDS_ACTUAL.jsonl','W35_same_uid_sampled_signed_cycle_v1')
        self.cycle_active=self.active.clone();self.cycle_uid=self.uid.clone();self.cycle_key=self.uid.clone()
        self.cycle_count=self.uid.clone();self.cycle_turn=self.sample_direction.clone()
        self.cycle_progress=self.sample_direction.clone();self.cycle_ref=self.sample_direction.clone()
        self.cycle_direction=self.sample_direction.clone();self.cycle_sign=self.sample_direction.clone()
        self.cycle_start_phase=self.uid.clone();self.cycle_cross_phase=self.active.clone()
        self.cycle_first_control=self.uid.clone()
        self.cycle_events=t.zeros(3,42,n,dtype=t.long,device=device)
        self.cycle_nonterminal_events=self.cycle_events.clone()
        self.cycle_seconds=t.zeros(3,42,n,device=device);self.cycle_displacement=self.cycle_seconds.clone()
        self.cycle_reference=self.cycle_seconds.clone();self.cycle_overshoot=self.cycle_seconds.clone()
        self.cycle_partial=self.closed.clone()
        self.current_control=0;self.initial_adopted=False;self.errors=[];self.opened_events=0
        self.last_terminated=self.active.clone();self.last_truncated=self.active.clone()

    def _snapshot(self,cmd):
        return dict(key=profile_key(self.t,cmd),command=cmd.command,direction=cmd.direction,signed_yaw=cmd.signed_yaw,timer=cmd.time_left)

    def _open(self,cmd,ids,known):
        assert not bool(self.active[ids].any())
        self.uid[ids]+=1;self.active[ids]=True;self.known[ids]=bool(known)
        self.source_episode[ids]=cmd._env._e1_episode[ids]
        p=self._snapshot(cmd);self.sample_key[ids]=p['key'][ids]
        self.sample_command[ids]=p['command'][ids];self.sample_direction[ids]=p['direction'][ids]
        self.sample_yaw[ids]=p['signed_yaw'][ids];self.start_timer[ids]=p['timer'][ids]
        self.command_controls[ids]=0;self.moving_controls[ids]=0;self.zero_controls[ids]=0
        self.error[ids]=0;self.moving_error[ids]=0;self.profile_bits[ids]=0;self.first_control[ids]=self.current_control
        self.start_tick[ids]=int(cmd._env._sim_step_counter);self.first_acted[ids]=-1
        self.last_terminated[ids]=False;self.last_truncated[ids]=False
        self.opened_events+=len(ids)

    def adopt_observed_initial_packet(self,packet):
        term=packet['term'];ids=packet['ids']
        assert len(ids)==self.n and self.t.equal(ids,self.ids) and packet['tick']==0
        assert not bool(self.active.any())
        self._open(term,ids,True);self.initial_adopted=True

    def original_event(self,event,term,ids,**metadata):
        if event=='BEFORE_ORIGINAL_RESET':
            self.close(ids,'reset',natural_timer_end=False);self.episode[ids]+=1
        elif event=='AFTER_ORIGINAL_RESAMPLE':
            # Resample inside reset begins a fresh command, never a complete old
            # command. Original prior timer is observed, not decremented here.
            prior=metadata.get('original_prior_timer')
            natural=not metadata['within_original_reset'] and prior is not None
            if natural:
                natural_ids=ids[prior<=0];other_ids=ids[prior>0]
                self.close(natural_ids,'resample',natural_timer_end=True)
                self.close(other_ids,'resample',natural_timer_end=False)
            else:self.close(ids,'resample',natural_timer_end=False)
            self._open(term,ids,True)
        else:raise ValueError('Unexpected original command event '+event)

    def begin(self,cmd,ctx):
        self.current_control=int(ctx['control'])
        missing=self.ids[~self.active]
        if len(missing):self._open(cmd,missing,False)
        ctx['observed_command_uid']=self.uid.clone();ctx['observed_episode_uid']=self.episode.clone()
        # A profile/eligibility/direction change breaks a cycle segment but never
        # manufactures another command UID or resampling event.
        valid=ctx['moving']&ctx['eligible']
        same=(ctx['profile_key']==self.cycle_key)&(self.uid==self.cycle_uid)&(ctx['direction']==self.cycle_direction)&(self.t.sign(ctx['signed_yaw'])==self.cycle_sign)
        ended=self.ids[self.cycle_active&(~valid|~same)]
        self._partial_cycle(ended,'original_mode_eligibility_profile_or_direction_change')
        start=self.ids[valid&~self.cycle_active]
        if len(start):
            self.cycle_active[start]=True;self.cycle_uid[start]=self.uid[start];self.cycle_key[start]=ctx['profile_key'][start]
            self.cycle_direction[start]=ctx['direction'][start];self.cycle_sign[start]=self.t.sign(ctx['signed_yaw'][start])
            self.cycle_count[start]=0;self.cycle_turn[start]=0;self.cycle_progress[start]=0;self.cycle_ref[start]=0
            self.cycle_start_phase[start]=0 if self.current_control<100 else 1
            self.cycle_cross_phase[start]=False;self.cycle_first_control[start]=self.current_control

    def observe_original_terminal(self,ctx,root_xy,heading,errors,terminated,truncated):
        t=self.t
        assert t.equal(ctx['observed_command_uid'],self.uid) and t.equal(ctx['observed_episode_uid'],self.episode)
        assert bool(self.active.all()) and len(errors)==3 and all(x.shape==(self.n,) for x in errors)
        first=self.ids[self.command_controls==0];self.first_acted[first]=self.current_control
        self.command_controls+=1;self.error+=t.stack(errors,1)
        moving=ctx['moving']&ctx['eligible'];self.moving_controls+=moving.long()
        self.moving_error+=t.stack(errors,1)*moving[:,None]
        self.zero_controls+=(ctx['command']==0).all(1).long()
        self.profile_bits|=t.bitwise_left_shift(t.ones_like(ctx['profile_key']),ctx['profile_key'])
        self.last_terminated=terminated.clone();self.last_truncated=truncated.clone()
        ids=self.ids[self.cycle_active]
        if not len(ids):return
        delta=t.atan2(t.sin(heading-ctx['heading']),t.cos(heading-ctx['heading']))
        sign=self.cycle_sign;self.cycle_turn[ids]+=delta[ids]*sign[ids]
        displacement=root_xy-ctx['before_root_xy']
        projection=displacement[:,0]*t.cos(ctx['direction'])+displacement[:,1]*t.sin(ctx['direction'])
        reference=ctx['command'][:,0]*t.cos(ctx['heading']-ctx['direction'])-ctx['command'][:,1]*t.sin(ctx['heading']-ctx['direction'])
        self.cycle_progress[ids]+=projection[ids];self.cycle_ref[ids]+=.02*reference[ids];self.cycle_count[ids]+=1
        phase=0 if self.current_control<100 else 1
        self.cycle_cross_phase[ids]|=self.cycle_start_phase[ids]!=phase
        complete=self.ids[self.cycle_active&(self.cycle_turn>=2*math.pi)]
        if len(complete):
            bucket=t.where(self.cycle_cross_phase[complete],2,self.cycle_start_phase[complete])
            key=self.cycle_key[complete];index=(bucket,key,complete)
            self.cycle_events[index]+=1;self.cycle_nonterminal_events[index]+=(~(terminated[complete]|truncated[complete])).long()
            seconds=self.cycle_count[complete].float()*.02
            self.cycle_seconds[index]+=seconds;self.cycle_displacement[index]+=self.cycle_progress[complete]
            self.cycle_reference[index]+=self.cycle_ref[complete]
            self.cycle_overshoot[index]+=self.cycle_turn[complete]-2*math.pi
            columns=dict(env_id=complete,episode_uid=self.episode[complete],original_E1_episode=self.source_episode[complete],command_uid=self.uid[complete],profile=key,
                start_observed=self.known[complete],first_control=self.cycle_first_control[complete],last_control=t.full_like(complete,self.current_control),
                controls=self.cycle_count[complete],seconds=seconds,sampled_signed_turn_rad=self.cycle_turn[complete],
                angular_overshoot_rad=self.cycle_turn[complete]-2*math.pi,world_direction=self.cycle_direction[complete],
                actual_projected_displacement_m=self.cycle_progress[complete],actual_progress_m_s=self.cycle_progress[complete]/seconds,
                sampled_BODY_reference_displacement_m=self.cycle_ref[complete],sampled_BODY_reference_progress_m_s=self.cycle_ref[complete]/seconds,
                terminal_non_timeout=terminated[complete],terminal_timeout=truncated[complete],phase_bucket=bucket)
            self._write_columns(self.cycle_records,columns,dict(complete_sampled_span=True,
                nominal_world_progress_m_s=.5,reference_quadrature='original pre-control BODY reference at sampled heading; left endpoint',
                endpoint_is_original_sample_no_interpolation=True,cycle_event_NOT_skill_success=True))
            # No angular overshoot credit is carried to an unrelated new anchor.
            self.cycle_active[complete]=False

    def _write_columns(self,writer,columns,extra):
        cpu={key:value.detach().cpu().tolist() for key,value in columns.items()}
        size=len(next(iter(cpu.values())))
        for i in range(size):writer.append({**{key:value[i] for key,value in cpu.items()},**extra})

    def _partial_cycle(self,ids,reason):
        ids=ids[self.cycle_active[ids]]
        if not len(ids):return
        self.cycle_partial[self.cycle_key[ids],ids]+=1
        self._write_columns(self.cycle_records,dict(env_id=ids,episode_uid=self.episode[ids],original_E1_episode=self.source_episode[ids],command_uid=self.cycle_uid[ids],
            profile=self.cycle_key[ids],controls=self.cycle_count[ids],sampled_signed_turn_rad=self.cycle_turn[ids],
            actual_projected_displacement_m=self.cycle_progress[ids]),
            dict(complete_sampled_span=False,end_reason=reason,no_exposure_is_pending_not_automatic_policy_failure=True))
        self.cycle_active[ids]=False

    def close(self,ids,reason,natural_timer_end=False):
        assert reason in ('reset','resample','window_end')
        ids=ids[self.active[ids]]
        if not len(ids):return
        self._partial_cycle(ids,reason)
        key=self.sample_key[ids];index=(key,ids);count=self.command_controls[ids]
        acted=count>0;known=self.known[ids]
        full=known&acted&bool(reason=='resample' and natural_timer_end)
        self.closed[index]+=1;self.acted[index]+=acted.long();self.zero[index]+=(~acted).long()
        self.complete[index]+=full.long();self.left[index]+=(~known).long()
        self.reset[index]+=int(reason=='reset');self.window[index]+=int(reason=='window_end')
        self.complete_controls[index]+=self.t.where(full,count,self.t.zeros_like(count))
        self.complete_moving_controls[index]+=self.t.where(full,self.moving_controls[ids],self.t.zeros_like(count))
        for j in range(3):
            self.complete_errors[key,j,ids]+=self.t.where(full,self.error[ids,j],self.t.zeros_like(self.error[ids,j]))
            self.complete_moving_errors[key,j,ids]+=self.t.where(full,self.moving_error[ids,j],self.t.zeros_like(self.error[ids,j]))
        self._write_columns(self.instance_records,dict(env_id=ids,episode_uid=self.episode[ids],original_E1_episode=self.source_episode[ids],command_uid=self.uid[ids],
            sampled_profile=key,start_observed=known,population_controls=count,acted_instance=acted,
            fully_observed_natural_command_lifetime=full,boundary_observed_control_index=self.first_control[ids],
            original_start_physics_tick=self.start_tick[ids],first_acted_control_index=self.first_acted[ids],
            last_control=self.t.full_like(ids,self.current_control),sampled_BODY_command3=self.sample_command[ids],
            sampled_world_direction=self.sample_direction[ids],sampled_signed_yaw_rad_s=self.sample_yaw[ids],
            actual_start_timer_s=self.start_timer[ids],acted_profile_bitset=self.profile_bits[ids],
            errors_sum=self.error[ids],moving_only_population_controls=self.moving_controls[ids],moving_only_errors_sum=self.moving_error[ids],
            actual_zero_command_population_controls=self.zero_controls[ids],
            last_non_timeout_mask=self.last_terminated[ids],last_timeout_mask=self.last_truncated[ids]),
            dict(end_reason=reason,original_timer_expired_observed=bool(natural_timer_end),
                original_start_unknown_if_not_observed=True,zero_control_NOT_skill_denominator=True))
        self.active[ids]=False

    def finish(self):
        self.close(self.ids,'window_end');t=self.t;profiles=[]
        for p in range(42):
            den=int(self.complete_controls[p].sum());moving=int(self.complete_moving_controls[p].sum())
            profiles.append(dict(sampled_profile=p,closed_instance_events=int(self.closed[p].sum()),
                acted_instance_events=int(self.acted[p].sum()),zero_control_instance_events=int(self.zero[p].sum()),
                unique_env_with_acted_instance=int((self.acted[p]>0).sum()),
                fully_observed_natural_command_events=int(self.complete[p].sum()),
                unique_env_with_complete_command=int((self.complete[p]>0).sum()),
                left_censored_events=int(self.left[p].sum()),reset_ended_events=int(self.reset[p].sum()),window_ended_events=int(self.window[p].sum()),
                complete_command_population_controls=den,
                complete_command_MAE_by_sampled_profile=[float(self.complete_errors[p,j].sum())/den if den else None for j in range(3)],
                complete_command_moving_only_population_controls=moving,
                complete_command_moving_only_MAE_by_sampled_profile=[float(self.complete_moving_errors[p,j].sum())/moving if moving else None for j in range(3)],
                actual_acted_profile_changes_are_in_JSONL_bitset=True,no_exposure_is_pending=True))
        cycles=[]
        for bucket,label in enumerate(('warmup_only','steady_only','spans_warmup_boundary')):
            for p in range(42):
                seconds=float(self.cycle_seconds[bucket,p].sum())
                cycles.append(dict(phase=label,profile=p,sampled_whole_cycle_events=int(self.cycle_events[bucket,p].sum()),
                    unique_env_with_sampled_cycle=int((self.cycle_events[bucket,p]>0).sum()),
                    cycles_ending_without_original_terminal_mask=int(self.cycle_nonterminal_events[bucket,p].sum()),
                    actual_population_cycle_seconds=seconds,actual_projected_displacement_m=float(self.cycle_displacement[bucket,p].sum()),
                    population_duration_weighted_actual_progress_m_s=float(self.cycle_displacement[bucket,p].sum())/seconds if seconds else None,
                    population_duration_weighted_sampled_BODY_reference_m_s=float(self.cycle_reference[bucket,p].sum())/seconds if seconds else None,
                    summed_angular_overshoot_rad=float(self.cycle_overshoot[bucket,p].sum()),
                    nominal_reference_m_s=.5,no_exposure_is_pending_not_pass=seconds==0,events_not_unique_env_or_skill_success=True))
        return dict(kind='W35_observed_command_UID_and_same_instance_sampled_cycle_v1',source_SHA=MODEL,
            initial_original_origin_adopted=self.initial_adopted,opened_instance_events=self.opened_events,
            profiles_by_original_sampled_profile=profiles,same_UID_cycle_phase_profile_metrics=cycles,
            partial_cycle_events_by_profile=self.cycle_partial.sum(-1).cpu().tolist(),
            command_instance_JSONL=self.instance_records.finish(),cycle_JSONL=self.cycle_records.finish(),
            zero_control_and_acted_denominators_separate=True,profile_error_labels_are_sampled_profile_not_unconditionally_moving=True,
            original_rough_timeout_and_reset_untouched=True,negative_angle_not_clamped=True,no_overshoot_credit_carried=True,
            sample_endpoint_span_NOT_exact_2pi_interpolation=True,
            unseen_inter_sample_rotations_not_certified=True,
            no_per_command_skill_threshold_invented=True,complete_WM_dataset=False,skill_graduation=False)
