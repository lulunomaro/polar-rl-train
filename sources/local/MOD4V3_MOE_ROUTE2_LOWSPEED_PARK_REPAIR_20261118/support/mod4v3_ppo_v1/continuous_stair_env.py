"""Low-speed one-step course. Collision bank is built once; each env moves on reset."""
import math,torch
from .legacy_continuous_stair_env import _OriginalContinuousStairEnv
from .scut_rough_scut_v1_env import ScutUnifiedRoughV1Env
from .stair_training_repair import ContinuousStairRepairMixin,wheel_center_ground
from .scut_flat_env import tensor
from .fixed200_reward_math import fixed200_reward
from .dense_top_reward import dense_top_support
from .start_offset_partition import OFFSETS_MM,assign_offset_indices,population_by_dr_offset
from pathlib import Path
import json
from .single_step_math import SPEC,COURSE,advance,supported_upper,stable_completion,first_landings
from isaaclab.utils.math import quat_from_euler_xyz
from mod4v1_scut.math_ops import euler_xyz_from_quat,wrap_to_pi

class ContinuousStairEnv(ContinuousStairRepairMixin,_OriginalContinuousStairEnv):
    # User2026-11-09/10:2mm is diagnostic only; inherited >1m catastrophe reset remains.
    enforce_closure_reset=False
    def __init__(self,cfg,meta,bank):
        self._course_ready=False
        super().__init__(cfg,meta,bank)
        n=self.num_envs;dev=self.device
        self.course_mastered=torch.zeros(n,dtype=torch.long,device=dev)
        self.course_level=torch.zeros_like(self.course_mastered)
        self.course_success_streak=torch.zeros_like(self.course_mastered)
        self.course_attempts=torch.zeros(2,len(SPEC.heights),dtype=torch.long,device=dev)
        self.course_successes=torch.zeros_like(self.course_attempts)
        self.course_promotions=torch.zeros_like(self.course_attempts)
        self.course_demotions=torch.zeros_like(self.course_attempts)
        self.course_speed_rejections=torch.zeros_like(self.course_attempts)
        self.course_failure_causes=torch.zeros(2,len(SPEC.heights),3,dtype=torch.long,device=dev)
        self.course_entry_speed=torch.zeros(n,device=dev)
        self.course_speed_max=torch.zeros_like(self.course_entry_speed)
        self.course_hold=torch.zeros_like(self.course_entry_speed)
        self.course_lift_best=torch.zeros(n,2,device=dev)
        self.course_lift_reference=torch.zeros_like(self.course_lift_best)
        self.course_landed=torch.zeros(n,2,dtype=torch.bool,device=dev)
        self.course_lift_armed=torch.zeros(n,dtype=torch.bool,device=dev)
        self.course_entry_seen=torch.zeros(n,dtype=torch.bool,device=dev)
        self.course_success=torch.zeros_like(self.course_entry_seen)
        self.course_progress=torch.zeros(n,device=dev)
        self.course_event_reward=torch.zeros(n,device=dev)
        self.course_reward_sums=torch.zeros(4,device=dev)
        self.course_accounting=False;self.course_evaluation=False
        self.speed_stage=torch.zeros(n,dtype=torch.long,device=dev)
        self.speed_streak=torch.zeros_like(self.speed_stage)
        self.speed_limits=self.command.new_tensor([1.2,.95,.80,.70,.64,.60])
        self.speed_completed=torch.zeros(6,device=dev,dtype=torch.long)
        self.speed_penalty_sum=torch.zeros((),device=dev)
        self.strict_hold=torch.zeros(n,device=dev)
        self.strict_success=torch.zeros(n,dtype=torch.bool,device=dev)
        self.strict_success_count=torch.zeros((),device=dev,dtype=torch.long)
        self.course_stop_latched=torch.zeros(n,dtype=torch.bool,device=dev)
        self.course_park_hold=torch.zeros(n,device=dev)
        self.top_latch_events=torch.zeros(2,dtype=torch.long,device=dev)
        self.previous_course_body_x=torch.zeros(n,device=dev)
        self.course_pitch_peak=torch.zeros(n,device=dev)
        self.course_quality_penalty_sum=torch.zeros(9,device=dev)
        self.bilateral_landing_seen=torch.zeros(n,dtype=torch.bool,device=dev)
        self.bilateral_top_now=torch.zeros_like(self.bilateral_landing_seen)
        self.no_progress_seconds=torch.zeros(n,device=dev)
        self.last_reward_breakdown=None
        self.true_top_completion_events=torch.zeros(2,dtype=torch.long,device=dev)
        self.replay_success_now=torch.zeros(n,dtype=torch.bool,device=dev)
        self.replay_top_support_count=torch.zeros(n,dtype=torch.long,device=dev)
        self.replay_speed_limit_at_step=torch.zeros(n,device=dev)
        self.replay_actual_DR_at_step=torch.zeros(n,dtype=torch.bool,device=dev)
        self.top_dense_reward_sum=torch.zeros((),device=dev)
        self.last_top_dense=torch.zeros(n,device=dev)
        self.replay_completion_bonus=torch.zeros(n,device=dev)
        self.start_offset_mm=torch.zeros(n,device=dev)
        self.start_offset_index=assign_offset_indices(self.continuous_stair_mask,self.full_dr.nominal_env_mask)
        self.actual_start_offset_index=self.start_offset_index.clone()
        pose=json.loads((Path(__file__).resolve().parents[2]/"startup_pose.json").read_bytes())
        self.high_startup_q=self.command.new_tensor([pose["joint_pos"][name]for name in self.robot.joint_names])
        self.high_startup_z=float(pose["root_height_m"])
        self.height_aux_ready=torch.zeros(n,dtype=torch.bool,device=dev)
        self.offset_attempts=torch.zeros(2,5,dtype=torch.long,device=dev)
        self.offset_completion_events=torch.zeros(2,5,dtype=torch.long,device=dev)
        self.reference_nominal_env_mask=self.full_dr.nominal_env_mask.clone()
        self._course_ready=True

    def _set_origins(self,ids):
        ScutUnifiedRoughV1Env._set_origins(self,ids)
        special=getattr(self.terrain,'r1_continuous_stair_mask',None)
        if special is not None:
            selected=ids[special[ids]]
            # The bank's origin is the lower ground, while its center ray hits the top.
            lower=self.terrain.terrain_origins[self.terrain.terrain_levels[selected],self.terrain.terrain_types[selected],2]
            self.terrain.env_origins[selected,2]=lower
            self.scene.env_origins[selected,2]=lower

    def _course_scatter(self,buffer,ids,values):
        if ids.numel():
            index=self.reference_nominal_env_mask[ids].long()*len(SPEC.heights)+self.course_level[ids]
            buffer.view(-1).scatter_add_(0,index,values.long())

    def _finish_course_episodes(self,ids):
        if not self.course_accounting or self.snapshots is None:return
        picked=ids[self.continuous_stair_mask[ids]&(self.episode_length_buf[ids]>0)]
        if not picked.numel():return
        ok=self.course_success[picked]&(~self.reset_terminated[picked])
        if not self.course_evaluation:
            self.speed_streak[picked]=torch.where(ok&(self.course_level[picked]==len(SPEC.heights)-1),self.speed_streak[picked]+1,torch.zeros_like(self.speed_streak[picked]))
            promoted=(self.speed_streak[picked]>=2)&(self.speed_stage[picked]<len(self.speed_limits)-1)&(self.course_level[picked]==len(SPEC.heights)-1)
            self.speed_stage[picked]+=promoted.long()
            self.speed_streak[picked]=torch.where(promoted,torch.zeros_like(self.speed_streak[picked]),self.speed_streak[picked])
        attempted=torch.ones_like(ok)
        new,streak,up,down=advance(self.course_mastered[picked],self.course_level[picked],self.course_success_streak[picked],ok,attempted)
        self._course_scatter(self.course_attempts,picked,attempted)
        offset_group=self.reference_nominal_env_mask[picked].long()*5+self.actual_start_offset_index[picked]
        self.offset_attempts.view(-1).scatter_add_(0,offset_group,attempted.long())
        self._course_scatter(self.course_successes,picked,ok)
        self._course_scatter(self.course_speed_rejections,picked,self.course_entry_seen[picked]&((self.course_entry_speed[picked]>SPEC.maximum_speed)|(self.course_speed_max[picked]>SPEC.maximum_speed)))
        if not self.course_evaluation:
            self._course_scatter(self.course_promotions,picked,up)
            self._course_scatter(self.course_demotions,picked,down)
            self.course_mastered[picked]=new;self.course_success_streak[picked]=streak
        group=self.reference_nominal_env_mask[picked].long();level=self.course_level[picked]
        for k,mask in enumerate((self.reset_terminated[picked],~self.course_landed[picked].all(1),self.course_landed[picked].all(1)&~ok)):
            self.course_failure_causes[:,:,k].index_put_((group,level),mask.long(),accumulate=True)

    def _reset_idx(self,ids):
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        ready=getattr(self,'_course_ready',False)
        if ready:
            self._finish_course_episodes(ids)
            picked=ids[self.continuous_stair_mask[ids]]
            if not self.course_evaluation:
                level=self.course_mastered[picked].clone()
                review=(level>0)&(torch.rand(len(picked),device=self.device,generator=self.reset_generator)<SPEC.review_fraction)
                level[review]=(torch.rand(int(review.sum()),device=self.device,generator=self.reset_generator)*level[review]).long()
                self.course_level[picked]=level
            self.terrain.terrain_levels[picked]=self.course_level[picked]
        # Keep the native full-DR/rough/air reset implementation and bypass the old 200mm reset.
        ScutUnifiedRoughV1Env._reset_idx(self,ids)
        if not ready:return
        self._flat_preservation_commands(ids)
        for cause in ('contact','orientation','other'):
            for suffix in ('_counter','_raw_buf'):
                value=getattr(self.reward,'_stair_'+cause+suffix,None)
                if value is not None:value[ids]=0
        for name in ('_stair_guide_allowed','_stair_contact_raw','_stair_suppressed_guide_raw'):
            value=getattr(self.reward,name,None)
            if value is not None:value[ids]=False
        for buf in (self.course_entry_seen,self.course_success,self.course_landed,self.course_lift_armed,self.course_stop_latched):buf[ids]=False
        for buf in (self.course_entry_speed,self.course_speed_max,self.course_hold,self.course_park_hold,self.course_lift_best,self.course_progress,self.course_event_reward):buf[ids]=0
        picked=ids[self.continuous_stair_mask[ids]]
        self.strict_hold[ids]=0.;self.strict_success[ids]=False;self.course_pitch_peak[ids]=0.
        self.previous_course_body_x[ids]=(self.view.data.root_pos_w[ids,0]-self._center()[ids,0])*self.stair_side[ids]
        self.stair_up[ids]=False;self.stair_mid[ids]=False;self.stair_goal_hold[ids]=0.;self.stair_stage[ids]=0
        if not picked.numel():return
        self.bilateral_landing_seen[ids]=False;self.bilateral_top_now[ids]=False;self.no_progress_seconds[ids]=0.
        n=len(picked);gen=self.reset_generator;center=self._center()[picked]
        q=self.high_startup_q[None].expand(n,-1).clone();root=tensor(self.robot.data.default_root_state)[picked].clone()
        self.height_aux_ready[ids]=False
        side=torch.where(torch.rand(n,device=self.device,generator=gen)<.5,-1.,1.)
        offset=self.command.new_tensor(OFFSETS_MM)[self.actual_start_offset_index[picked]]/1000.;self.start_offset_mm[picked]=offset*1000.
        distance=SPEC.edge+1.2-offset
        root[:,:3]=center;root[:,0]+=side*distance;root[:,1]+=torch.empty(n,device=self.device).uniform_(-.15,.15,generator=gen)
        root[:,2]+=self.high_startup_z
        yaw=torch.where(side<0,0.,math.pi);root[:,3:7]=quat_from_euler_xyz(torch.zeros_like(yaw),torch.full_like(yaw,.02),yaw);root[:,7:]=0.
        self.robot.write_root_state_to_sim(root,env_ids=picked);self.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=picked)
        self.stair_up[picked]=True;self.stair_side[picked]=side;self.stair_start[picked]=distance
        h=self.command.new_tensor(SPEC.heights)[self.course_level[picked]]
        self.stair_height[picked]=h+.2091
        self.stair_speed[picked]=torch.empty(n,device=self.device).uniform_(.3,.5,generator=gen)
        self.height[picked]=.4091;self.command[picked]=0.;self.heading_env[picked]=False;self.standing_env[picked]=True
        self.actions[picked]=0.;self.torque[picked]=0.;self.zero_torque_remaining[picked]=0;self._ground_command_until[picked]=0;self.r2_air_reset[picked]=False
        self.course_lift_reference[picked]=.25
        self.reward.ground_z_est[picked]=center[:,2];self.reward._invalidate_step_caches()
        self._course_commands()

    def _sample_command(self,ids):
        ScutUnifiedRoughV1Env._sample_command(self,ids)
        if getattr(self,'_course_ready',False):
            self._flat_preservation_commands(ids);self._course_commands()

    def _course_commands(self):
        if not getattr(self,'_course_ready',False):return
        picked=self.continuous_stair_mask.nonzero().flatten()
        age=self.episode_length_buf[picked]*self.step_dt
        self.height[picked]=self.stair_height[picked]
        # The approved native teacher commands a low stance after bilateral landing.
        self.height[picked]=torch.where(self.bilateral_landing_seen[picked],self.height.new_full((len(picked),),.20),self.height[picked])
        moving_cmd=(age>=SPEC.settle_seconds)&(~self.course_stop_latched[picked])
        self.command[picked]=0.;self.command[picked,0]=torch.where(moving_cmd,self.stair_speed[picked],0.)
        self.command_timer[picked]=1e9;self.heading_env[picked]=False;self.standing_env[picked]=~moving_cmd
        self._ground_original_command[picked]=self.command[picked];self._ground_original_heading[picked]=False
        self.reward.command[picked]=self.command[picked];self.reward.height_cmd[picked]=self.height[picked];self.reward._invalidate_step_caches()

    def _get_observations(self):
        self._course_commands()
        raw=ScutUnifiedRoughV1Env._get_observations(self)
        if getattr(self,'_course_ready',False):
            mask=self.continuous_stair_mask
            for key,mode_slice in (('policy',slice(28,35)),('critic',slice(32,39))):
                raw[key]=raw[key].clone()
                raw[key][mask,mode_slice]=raw[key].new_tensor([0.,1.,0.,0.,0.,1.,0.])
        return raw

    def _pre_physics_step(self,actions):
        self._course_commands()
        ScutUnifiedRoughV1Env._pre_physics_step(self,actions)
        self._course_commands()

    def prepare_endpoint(self):
        ScutUnifiedRoughV1Env.prepare_endpoint(self)
        if not getattr(self,'_course_ready',False):return
        r=self.reward;wheels=self.view.data.body_pos_w[:,self.stair_wheel_idx]
        ground=torch.stack([wheel_center_ground(tensor(self.scene[name].data.ray_hits_w),wheels[:,side,:2],r.ground_wheels[:,side])for side,name in enumerate(('ground_left','ground_right'))],1)
        mask=self.continuous_stair_mask
        self.stair_original_root_ground=r.ground_z_est.clone();self.stair_wheel_ground=ground
        r.ground_z_est=torch.where(mask,ground.amin(1),r.ground_z_est)
        r.ground_wheels=torch.where(mask[:,None],ground,r.ground_wheels);r._invalidate_step_caches()
        x=(wheels[:,:,0]-self._center()[:,None,0])*self.stair_side[:,None]
        r._stair_course_mask=mask
        r._stair_guide_allowed=mask&(~self.course_success)&((x-SPEC.edge).abs().amin(1)<.45)

    def _update_course_events(self,term):
        self.course_event_reward.zero_()
        center=self._center();d=self.view.data;wheel=d.body_pos_w[:,self.stair_wheel_idx]
        forces=tensor(self.scene['contacts'].data.net_forces_w)[:,self.wheel_sensor_ids]
        x=(wheel[:,:,0]-center[:,None,0])*self.stair_side[:,None];y=wheel[:,:,1]-center[:,None,1];z=wheel[:,:,2]-center[:,None,2]
        h=self.command.new_tensor(SPEC.heights)[self.course_level]
        active=self.continuous_stair_mask&(~term)&(self.episode_length_buf*self.step_dt>=SPEC.settle_seconds)
        near=(x-SPEC.edge).abs().amin(1)<.45
        speed=tensor(self.robot.data.root_lin_vel_w)[:,:2].norm(dim=-1)
        entering=active&(~self.course_entry_seen)&(x.amin(1)<SPEC.edge+.20)
        self.course_entry_speed[entering]=speed[entering];self.course_entry_seen|=entering
        self.course_speed_max=torch.where(self.continuous_stair_mask,torch.maximum(self.course_speed_max,speed),self.course_speed_max)
        upper=supported_upper(x,y,z,forces[:,:,2],h)
        gained,self.course_landed=first_landings(self.course_landed,upper,active)
        self.bilateral_top_now=upper.all(1)&active
        body_x=(d.root_pos_w[:,0]-center[:,0])*self.stair_side
        roll,pitch,_=euler_xyz_from_quat(self.robot.data.root_quat_w)
        self.course_pitch_peak=torch.where(self.continuous_stair_mask,torch.maximum(self.course_pitch_peak,wrap_to_pi(pitch).abs()),self.course_pitch_peak)
        self.bilateral_landing_seen|=self.bilateral_top_now&(body_x<SPEC.edge-SPEC.body_margin)
        limit=self.speed_limits[self.speed_stage]
        climb_failed=term|self.reward._stair_contact_raw|(self.course_pitch_peak>math.radians(38))
        move_stable=stable_completion(upper,body_x,wrap_to_pi(pitch),wrap_to_pi(roll),d.root_ang_vel_b[:,:2].norm(dim=-1),tensor(self.robot.data.root_lin_vel_w)[:,2],self.course_entry_speed,self.course_speed_max,self.course_entry_seen,climb_failed,active&(~self.course_stop_latched),maximum_allowed=limit)
        self.course_hold=torch.where(self.course_stop_latched,self.course_hold,torch.where(move_stable,self.course_hold+self.step_dt,torch.zeros_like(self.course_hold)))
        newly_latched=(self.course_hold>=SPEC.hold_seconds-1e-7)&(~self.course_stop_latched)
        self.course_stop_latched|=newly_latched
        if bool(newly_latched.any()):
            self.top_latch_events+=torch.bincount(self.reference_nominal_env_mask[newly_latched].long(),minlength=2)
        latch_bonus=torch.where(self.course_speed_max<=.60,10.,6.)*newly_latched.float()
        park_stable=(upper.all(1)&(body_x<SPEC.edge-SPEC.body_margin)&(body_x>-SPEC.edge+.2)&(wrap_to_pi(pitch).abs()<SPEC.maximum_angle)&(wrap_to_pi(roll).abs()<SPEC.maximum_angle)&(d.root_ang_vel_b[:,:2].norm(dim=-1)<SPEC.maximum_rate)&(tensor(self.robot.data.root_lin_vel_w)[:,2].abs()<.25)&(speed<=.20)&self.course_entry_seen&(self.course_entry_speed>=SPEC.minimum_entry_speed)&(self.course_entry_speed<=limit)&(self.course_speed_max<=limit)&(~climb_failed)&active)
        self.course_park_hold=torch.where(self.course_stop_latched&park_stable,self.course_park_hold+self.step_dt,torch.zeros_like(self.course_park_hold))
        completed=self.course_stop_latched&(self.course_park_hold>=1.0-1e-7)&(~self.course_success)
        strict_new=completed&(self.course_entry_speed<=.6)&(self.course_speed_max<=.6)
        self.strict_hold=torch.where(self.course_stop_latched&park_stable&(self.course_entry_speed<=.6)&(self.course_speed_max<=.6),self.course_park_hold,torch.zeros_like(self.strict_hold))
        self.strict_success|=strict_new;self.strict_success_count+=strict_new.long().sum()
        self.course_success|=completed;self.stair_goal_hold.copy_(self.course_hold+self.course_park_hold)
        self.replay_success_now.copy_(completed)
        self.replay_top_support_count.copy_(upper.long().sum(1))
        self.replay_speed_limit_at_step.copy_(limit)
        actual=getattr(getattr(self,"dr_course",None),"actual_full_dr",None)
        if actual is not None:self.replay_actual_DR_at_step.copy_(actual)
        # Credit increases only, near the real edge with measured support and actual wheel lift.
        supported=(forces[:,:,2]>SPEC.support_force).any(1)
        interaction=active&near&supported
        arm=interaction&(~self.course_lift_armed)
        self.course_lift_reference[arm]=self.reward.length[arm];self.course_lift_armed|=arm
        lift=((z-SPEC.radius)/h[:,None]).clamp(0,1)
        retract=((self.course_lift_reference-self.reward.length)/.08).clamp(0,1)
        score=lift*retract
        lift_gain=(score-self.course_lift_best).clamp_min(0).mean(1)*interaction
        self.course_lift_best=torch.where(interaction[:,None],torch.maximum(self.course_lift_best,score),self.course_lift_best)
        progress=(self.stair_start-body_x).clamp(0,1.5)
        advance=(progress-self.course_progress).clamp(0,.02)*interaction
        self.course_progress=torch.where(interaction,torch.maximum(self.course_progress,progress),self.course_progress)
        completion_scale=self.command.new_tensor([14.,16.,19.,22.,25.,28.])[self.speed_stage]+10.*(self.course_speed_max<=.60).float()
        self.replay_completion_bonus.copy_(completion_scale*completed.float()+latch_bonus)
        self.speed_completed+=torch.bincount(self.speed_stage[completed],minlength=6)
        completed_group=self.reference_nominal_env_mask[completed].long()
        self.true_top_completion_events+=torch.bincount(completed_group,minlength=2)
        idx=completed.nonzero().flatten()
        if idx.numel():self.offset_completion_events.view(-1).scatter_add_(0,self.reference_nominal_env_mask[idx].long()*5+self.actual_start_offset_index[idx],torch.ones_like(idx))
        real_forward=(self.previous_course_body_x-body_x)>.0001
        waiting=self.continuous_stair_mask&(self.command[:,0]>.1)&(~self.bilateral_landing_seen)&(~real_forward)
        self.no_progress_seconds=torch.where(waiting,self.no_progress_seconds+self.step_dt,torch.zeros_like(self.no_progress_seconds))
        speed_penalty=2.*(speed-limit).clamp_min(0).square()*active*near*(real_forward|gained.any(1))*self.step_dt
        self.previous_course_body_x.copy_(body_x);self.speed_penalty_sum+=speed_penalty.sum()
        parts=torch.stack((.25*lift_gain,.15*advance,.2*gained.sum(1),latch_bonus+completion_scale*completed.float()-speed_penalty),1)
        dense,top_parts=dense_top_support(upper,active,wrap_to_pi(pitch),wrap_to_pi(roll),self.course_pitch_peak,self.reward._stair_contact_raw,speed,limit,self.course_hold,self.step_dt,stop_latched=self.course_stop_latched,vx=d.root_lin_vel_b[:,0],episode_speed_max=self.course_speed_max)
        self.last_top_dense.copy_(dense);self.last_top_parts=top_parts;self.top_dense_reward_sum+=dense.sum()
        self.course_event_reward.copy_(parts.sum(1)+dense);self.course_reward_sums+=parts.sum(0)
        self.stair_stage=torch.where(self.bilateral_landing_seen,1,0)

    def _get_dones(self):
        term,timeout=ScutUnifiedRoughV1Env._get_dones(self)
        if getattr(self,'_course_ready',False):
            self._update_course_events(term)
            timeout|=self.course_success&(~term)
        return term,timeout

    def _get_rewards(self):
        base=ScutUnifiedRoughV1Env._get_rewards(self)
        if not getattr(self,'_course_ready',False):return base
        d=self.view.data
        roll,pitch,yaw=euler_xyz_from_quat(self.robot.data.root_quat_w)
        target_yaw=torch.where(self.stair_side<0,torch.zeros_like(yaw),torch.full_like(yaw,math.pi))
        yaw_error=wrap_to_pi(yaw-target_yaw)
        wheel_z=d.body_pos_w[:,self.stair_wheel_idx,2]-self._center()[:,None,2]
        lifting=(wheel_z>SPEC.radius+.035).any(1)
        current_height=self._height_observation()
        self.height_aux_ready|=(self.height-current_height).abs()<.03
        aux_active=self.height_aux_ready&(self.episode_length_buf*self.step_dt>=SPEC.settle_seconds)
        result,parts=fixed200_reward(base,self.course_event_reward,self.continuous_stair_mask,self.command[:,0],d.root_lin_vel_b[:,0],d.root_lin_vel_b[:,:2].norm(dim=-1),wrap_to_pi(pitch),yaw_error,self.height-self._height_observation(),lifting,self.bilateral_top_now,self.bilateral_landing_seen,self.no_progress_seconds,self.actions[:,4:],self.speed_limits[self.speed_stage],self.step_dt,height_aux_active=aux_active)
        self.course_quality_penalty_sum+=parts['penalties'].sum(0)
        self.last_reward_breakdown={k:v.detach().clone()for k,v in parts.items()}
        self.last_reward_breakdown['top_dense']=self.last_top_dense.detach().clone()
        self.last_reward_breakdown.update({k:v.detach().clone() for k,v in self.last_top_parts.items()})
        self.last_reward_breakdown['command_vx']=self.command[:,0].detach().clone()
        self.last_reward_breakdown['actual_vx']=d.root_lin_vel_b[:,0].detach().clone()
        self.last_reward_breakdown['height_error']=(self.height-self._height_observation()).detach().clone()
        self.last_reward_breakdown['yaw_error']=yaw_error.detach().clone()
        self.last_reward_breakdown['actual_height']=self._height_observation().detach().clone()
        self.last_reward_breakdown['episode_age']=self.episode_length_buf.detach().clone()*self.step_dt
        self.last_reward_breakdown['forward_position']=(-(self.view.data.root_pos_w[:,0]-self._center()[:,0])*self.stair_side).detach().clone()
        self.last_reward_breakdown['landing_seen']=self.bilateral_landing_seen.detach().clone()
        return result

    def terrain_summary(self):
        out=ScutUnifiedRoughV1Env.terrain_summary(self)
        if not getattr(self,'_course_ready',False):return out
        mask=self.continuous_stair_mask
        out['closure_contract']=dict(closure_2mm_diagnostic_only=not self.enforce_closure_reset,closure_2mm_reset_enabled=bool(self.enforce_closure_reset),catastrophic_closure_single_env_reset_m=1.,single_peak_batch_stop=False,solver='TGS32/4')
        out['course_groups']=dict(continuous_stairs=int(mask.sum()),retained_rough=int(self.terrain.r1_retained_rough_mask.sum()),flat=int(self.flat_terrain_mask.sum()))
        out['single_step_curriculum']=dict(course=COURSE,heights_m=list(SPEC.heights),mastered_population=torch.bincount(self.course_mastered[mask],minlength=len(SPEC.heights)).tolist(),episode_population=torch.bincount(self.course_level[mask],minlength=len(SPEC.heights)).tolist(),attempts_DR_then_nominal=self.course_attempts.tolist(),successes_DR_then_nominal=self.course_successes.tolist(),promotions_DR_then_nominal=self.course_promotions.tolist(),demotions_DR_then_nominal=self.course_demotions.tolist(),entry_speed_rejections_DR_then_nominal=self.course_speed_rejections.tolist(),failure_causes=self.course_failure_causes.tolist(),failure_columns=['terminated','both_wheels_never_landed','landing_without_qualified_hold'],reward_sums=self.course_reward_sums.tolist(),reward_columns=['incremental_supported_lift','incremental_edge_progress','each_wheel_first_landing','qualified_stable_completion'],review_fraction=SPEC.review_fraction,failures_before_demotion=SPEC.failures_to_demote,formal_evaluation_maximum_actual_entry_speed=SPEC.maximum_speed,training_maximum_actual_entry_speed=1.5,hold_s=SPEC.hold_seconds,per_env_reset_only=True,evaluation_only=self.course_evaluation,scope='stochastic training episode totals; not a frozen evaluation')
        return out

    def terrain_checkpoint_state(self):
        state=ScutUnifiedRoughV1Env.terrain_checkpoint_state(self)
        state.update(course=COURSE,heights_m=SPEC.heights,training_speed_state={k:getattr(self,k).clone()for k in ['speed_stage','speed_streak','speed_completed','strict_success_count','speed_penalty_sum','true_top_completion_events','top_latch_events','offset_completion_events','offset_attempts']})
        for name in ('course_mastered','course_level','course_success_streak','course_attempts','course_successes','course_promotions','course_demotions','course_speed_rejections','course_failure_causes','course_reward_sums'):
            state[name]=getattr(self,name).clone()
        return state

    def restore_terrain_curriculum(self,state):
        same=state.get('course')==COURSE
        if same:
            for name,value in state.get('training_speed_state',{}).items():getattr(self,name).copy_(value.to(getattr(self,name)))
        self.course_accounting=False
        if same:
            assert tuple(state['heights_m'])==SPEC.heights
            for name in ('course_mastered','course_level','course_success_streak','course_attempts','course_successes','course_promotions','course_demotions','course_speed_rejections','course_failure_causes','course_reward_sums'):
                target=getattr(self,name);value=state[name].to(target)
                if value.shape!=target.shape:raise ValueError('Course resume shape differs: '+name)
                target.copy_(value)
        self.parent_terrain_state=state;self.snapshots=None;self.reset()
        return dict(new_course=not same,course=COURSE,counters_restored=same,old_terrain_not_relabelled=True,fresh_physical_episodes=True)

    def begin_training_counts(self):
        self.course_accounting=True
