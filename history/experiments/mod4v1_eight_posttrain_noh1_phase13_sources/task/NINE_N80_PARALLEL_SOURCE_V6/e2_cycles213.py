"""New E2 same-UID world-cycle facts from original cached terminal buffers.

No Torch/SDK import,actor/sampler/RNG/getter,or physics call. The caller supplies
its existing t module and original E2Panel context/after/reason buffers. The old
V5 aggregates and raw remain untouched. This is not a native WM dataset.
"""
from pathlib import Path
import hashlib,json,math

MODEL='b3ae94dfded75360d43dcebc1ac0e7a0c51f2c2f11a9b28e58bb9ae8566ea1e1'


class Rows213:
    def __init__(self,out,maximum_bytes=192*1024**2):
        self.path=Path(out)/'E2_FULL_WORLD_SIGNED_UID_CYCLES_213_ACTUAL.jsonl'
        self.file=self.path.open('xb');self.h=hashlib.sha256();self.rows=0;self.bytes=0
        self.maximum_bytes=maximum_bytes;self.limited=False;self.closed=False
    def append(self,value):
        raw=(json.dumps(value,separators=(',',':'),allow_nan=False)+'\n').encode()
        if self.bytes+len(raw)>self.maximum_bytes:self.limited=True;return
        self.file.write(raw);self.h.update(raw);self.rows+=1;self.bytes+=len(raw)
    def finish(self):
        if not self.closed:self.file.close();self.closed=True
        return dict(path=str(self.path),bytes=self.bytes,rows=self.rows,SHA=self.h.hexdigest(),
            source_SHA=MODEL,schema='mod4.E2.same_UID_world213.v1',maximum_bytes=self.maximum_bytes,
            retention_limited=self.limited,producer_stream_SHA_without_reread=True,
            default_reader_transfer='metadata_only_no_JSONL_content_or_hash_read',complete_WM_dataset=False)


class E2Cycles213:
    def __init__(self,t,n,device,out):
        self.t=t;self.n=n;self.ids=t.arange(n,device=device);self.writer=Rows213(out)
        self.active=t.zeros(n,device=device,dtype=t.bool)
        self.key=t.zeros(n,device=device,dtype=t.long)
        self.episode=self.key.clone();self.uid=self.key.clone();self.controls=self.key.clone()
        self.first_control=self.key.clone();self.last_control=self.key.clone()
        self.direction=t.zeros(n,device=device);self.sign=self.direction.clone()
        self.turn=self.direction.clone();self.cross=self.direction.clone();self.along=self.direction.clone()
        self.command_yaw=self.direction.clone();self.reference=self.direction.clone()
        self.first_phase=self.key.clone();self.cross_phase=self.active.clone()
        self.term=self.active.clone();self.timeout=self.active.clone();self.reasons={}
        self.complete=0;self.false=0;self.partial=0;self.terminal_complete=0
        self.control=-1;self.last_physics_tick=None
    def begin(self,control,c,physics_tick):
        for name in ('key','episode','command_uid'):
            if c[name].shape!=(self.n,) or c[name].dtype!=self.t.long:
                raise ValueError('Original E2 UID/profile schema mismatch: '+name)
        if self.last_physics_tick is not None and physics_tick!=self.last_physics_tick:
            raise ValueError('Missing original consecutive E2 physical control interval')
        self.control=int(control)
        valid=(c['key']==8)|(c['key']==9)
        same=(self.key==c['key'])&(self.episode==c['episode'])&(self.uid==c['command_uid'])
        same&=(self.direction==c['direction'])&(self.sign==self.t.sign(c['signed_yaw']))
        self.close(self.ids[self.active&(~valid|~same)],'original_UID_episode_profile_direction_sign_change')
        ids=self.ids[valid&~self.active]
        self.active[ids]=True;self.key[ids]=c['key'][ids];self.episode[ids]=c['episode'][ids]
        self.uid[ids]=c['command_uid'][ids];self.direction[ids]=c['direction'][ids]
        self.sign[ids]=self.t.sign(c['signed_yaw'][ids]);self.controls[ids]=0
        self.first_control[ids]=control;self.last_control[ids]=control-1
        self.first_phase[ids]=c['phase'];self.cross_phase[ids]=False
        self.term[ids]=False;self.timeout[ids]=False
        for value in (self.turn,self.cross,self.along,self.command_yaw,self.reference):value[ids]=0
        self.begin_tick=int(physics_tick)
    def observe(self,c,after,terminated,truncated,reason_masks,physics_end_tick):
        t=self.t
        if int(physics_end_tick)!=self.begin_tick+8:
            raise ValueError('Need original eight2.5ms applied substeps')
        self.last_physics_tick=int(physics_end_tick)
        self.reasons={k:v.clone() for k,v in reason_masks.items()}
        ids=self.ids[self.active]
        xy=after['xy']-c['before_xy'];angle=c['direction']
        if not all(bool(t.isfinite(v).all()) for v in (xy,after['heading_delta'],c['command'])):
            raise ValueError('Nonfinite original terminal measurement')
        self.along[ids]+=xy[ids,0]*t.cos(angle[ids])+xy[ids,1]*t.sin(angle[ids])
        self.cross[ids]+=-xy[ids,0]*t.sin(angle[ids])+xy[ids,1]*t.cos(angle[ids])
        self.turn[ids]+=after['heading_delta'][ids]
        self.command_yaw[ids]+=c['command'][ids,2]*.02
        self.reference[ids]+=c['reference_projection'][ids]*.02
        self.controls[ids]+=1;self.last_control[ids]=self.control
        self.cross_phase[ids]|=self.first_phase[ids]!=c['phase']
        self.term[ids]|=terminated[ids];self.timeout[ids]|=truncated[ids]
        complete=self.ids[self.active&(self.turn*self.sign>=2*math.pi)]
        self.emit(complete,True,'original_sampled_signed_2pi_endpoint')
        # One sampled endpoint finishes the span; overshoot is never carried.
        self.active[complete]=False
        self.close(self.ids[self.active&(terminated|truncated)],'original_terminal_before_reset')
    def emit(self,ids,complete,reason):
        if not len(ids):return
        t=self.t;seconds=self.controls[ids].float()*.02
        safe=t.where(seconds>0,seconds,t.ones_like(seconds))
        along=self.along[ids]/safe;cross=self.cross[ids]/safe
        yaw=(self.turn[ids]-self.command_yaw[ids])/safe
        kinematic=((along-.5).abs()<=.05)&(cross.abs()<=.05)&(yaw.abs()<=.2)
        valid=(seconds>0)&~self.term[ids]&~self.timeout[ids]&complete
        columns=dict(env_id=ids,episode_uid=self.episode[ids],command_uid=self.uid[ids],
            original_E2_profile=self.key[ids],first_control=self.first_control[ids],last_control=self.last_control[ids],
            controls=self.controls[ids],seconds=seconds,world_direction_rad=self.direction[ids],
            actual_signed_yaw_rad=self.turn[ids],commanded_signed_yaw_integral_rad=self.command_yaw[ids],
            signed_yaw_error_rad_s=yaw,along_displacement_m=self.along[ids],cross_displacement_m=self.cross[ids],
            along_speed_m_s=along,cross_speed_m_s=cross,nominal_world_goal_m_s=t.full_like(seconds,.5),
            sampled_original_BODY_reference_displacement_m=self.reference[ids],
            non_timeout_before_reset=self.term[ids],timeout_before_reset=self.timeout[ids],
            crossed_warmup_steady_boundary=self.cross_phase[ids],
            original_kinematic_bounds_met=kinematic,
            valid_original_complete_skill_sample=valid,original_complete_cycle_fact=valid&kinematic)
        for name,mask in self.reasons.items():columns['original_terminal_reason_'+name]=mask[ids]
        cpu={k:v.detach().cpu().tolist() for k,v in columns.items()}
        for i in range(len(ids)):
            self.writer.append(dict(schema='mod4.E2.same_UID_world213.v1',source_SHA=MODEL,
                complete_sampled_span=complete,end_reason=reason,
                original_along_cross_tolerance='max(.03,.1V)=.05 atV=.5',signed_yaw_tolerance_rad_s=.2,
                no_new_aggregate_pass_rate=True,sampled_endpoint_no_interpolation=True,
                **{k:v[i] for k,v in cpu.items()}))
        if complete:
            self.complete+=len(ids);self.false+=int((~(valid&kinematic)).sum())
            self.terminal_complete+=int((self.term[ids]|self.timeout[ids]).sum())
        else:self.partial+=len(ids)
    def close(self,ids,reason):
        ids=ids[self.active[ids]];self.emit(ids,False,reason);self.active[ids]=False
    def finish(self):
        self.close(self.ids,'window_end_partial');producer=self.writer.finish()
        return dict(complete_cycle_events=self.complete,original_false_cycle_events=self.false,
            incomplete_events=self.partial,terminal_complete_events=self.terminal_complete,
            producer=producer,old_V5_cycle_results_unchanged=True,
            phase_boundary_is_reported_not_an_artificial_new_cycle_break=True,
            missing_or_retention_limited_exposure_not_a_pass=True,
            full_E2_skill=False,complete_SuperMimic_conversion=False)
