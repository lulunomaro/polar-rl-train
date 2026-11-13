"""Commanded moving jump: policy actions only, phase rewards, training-only labels."""
import math
import torch
from mod4v1_scut.math_ops import euler_xyz_from_quat
from isaaclab.utils.math import quat_from_euler_xyz
from .scut_flat_env import tensor, ScutFlatEnv
from .scut_flat_mixed_dr_env import ScutFlatMixedRemainingDREnv
from .stair_training_repair import install_native_done_repair


class MovingJumpEnv(ScutFlatMixedRemainingDREnv):
    def __init__(self,cfg,meta,bank):
        self._jump_ready=False
        super().__init__(cfg,meta,bank)
        self.leg_pd_decimation=4
        self.wheel_pd_decimation=1
        n,dev=self.num_envs,self.device
        self.phase=torch.zeros(n,device=dev,dtype=torch.long)
        self.phase_time=torch.zeros(n,device=dev)
        self.speed=torch.full((n,),.6,device=dev)
        self.cue=torch.full((n,),2.2,device=dev)
        self.reference_height=torch.full((n,),.34,device=dev)
        self.reference_x=torch.zeros(n,device=dev)
        self.crouched=torch.zeros(n,device=dev,dtype=torch.bool)
        self.extended=self.crouched.clone()
        self.retracted=self.crouched.clone()
        self.took_off=self.crouched.clone()
        self.landed=self.crouched.clone()
        self.completed=self.crouched.clone()
        self.upright_flight=self.crouched.clone()
        self.air_count=torch.zeros(n,device=dev)
        self.air_total=torch.zeros(n,device=dev)
        self.flight_start=torch.zeros(n,device=dev)
        self.flight_pitch=torch.zeros(n,device=dev)
        self.flight_roll=torch.zeros(n,device=dev)
        self.rim_peak=torch.zeros(n,device=dev)
        self.stable_hold=torch.zeros(n,device=dev)
        self.support_history=torch.zeros(25,n,2,device=dev)
        self._support_slot=0
        self.jump_extra=torch.zeros(n,device=dev)
        self.counts={k:torch.zeros(2,device=dev,dtype=torch.long) for k in ('episodes','crouched','extended','takeoff','retracted','upright_flight','landed','success')}
        self.wheel_ids=self.reward._wheel_link_idx
        self.wheel_sensor_ids=[self.scene['contacts'].body_names.index(x) for x in ('left_wheel_link','right_wheel_link')]
        self.teacher_net=None
        self._jump_ready=True
        self.height_range=(.36,.36)
        self.command_vx=(.4,.8)
        self.command_wz=(0.,0.)
        self.heading_fraction=0.
        self.standing_fraction=0.

    def _make_reward(self,meta):
        reward=super()._make_reward(meta)
        install_native_done_repair(reward)
        return reward

    def _count(self,ids,name):
        if len(ids):
            group=self.full_dr.nominal_env_mask[ids].long()
            self.counts[name].scatter_add_(0,group,torch.ones_like(group))

    def _sample_command(self,ids):
        super()._sample_command(ids)
        if self._jump_ready:
            self.command[ids]=0.
            self.command[ids,0]=self.speed[ids]
            self.height[ids]=.36
            self.heading_env[ids]=False
            self.command_timer[ids]=1e9

    def _pre_physics_step(self,actions):
        if self._jump_ready:
            age=self.episode_length_buf*self.step_dt
            ramp=((age-.8)/.3).clamp(0.,1.)
            self.command[:,0]=self.speed*ramp
            self.command[:,1:]=0.
            self.height.fill_(.36)
            self.heading_env.zero_()
        super()._pre_physics_step(actions)

    def prepare_endpoint(self):
        super().prepare_endpoint()
        if self._jump_ready:
            self.reward._stair_course_mask.fill_(True)
            self.reward._stair_guide_allowed.zero_()

    def _advance_task(self):
        d=self.view.data
        age=self.episode_length_buf*self.step_dt
        root=d.root_pos_w
        z=root[:,2]-self.scene.env_origins[:,2]
        forces=tensor(self.scene['contacts'].data.net_forces_w)
        supported=forces[:,self.wheel_sensor_ids,2]>5.
        no_support=torch.linalg.vector_norm(forces,dim=-1).sum(-1)<1.
        wheel=d.body_pos_w[:,self.wheel_ids]
        rim=wheel[:,:,2].amin(1)-self.scene.env_origins[:,2]-.0625
        rpy=euler_xyz_from_quat(d.root_quat_w)
        roll,pitch=rpy[0].abs(),rpy[1].abs()
        q=tensor(self.robot.data.joint_pos)[:,self.active_ids]
        delta=torch.stack((q[:,0]-q[:,1],q[:,2]-q[:,3]),1).mean(1)
        ready=(self.phase==0)&(age>=self.cue)
        self.reference_height[ready]=z[ready]
        self.reference_x[ready]=root[ready,0]
        self.phase[ready]=1
        self.phase_time[ready]=age[ready]
        compressed=(self.phase==1)&((delta<.80)|(z<self.reference_height-.05))
        new=compressed&~self.crouched
        self._count(new.nonzero().flatten(),'crouched')
        self.crouched|=compressed
        push=(self.phase==1)&((age-self.phase_time)>=.32)
        self.phase[push]=2
        self.phase_time[push]=age[push]
        extension=(self.phase==2)&self.crouched&(delta>1.25)
        self._count((extension&~self.extended).nonzero().flatten(),'extended')
        self.extended|=extension
        self.air_count=torch.where(no_support,self.air_count+self.step_dt,torch.zeros_like(self.air_count))
        launch=(self.phase==2)&self.crouched&(self.air_count>=.04)&(d.root_lin_vel_w[:,2]>.10)&(d.root_lin_vel_b[:,0]>.10)&(rim>.005)
        self._count(launch.nonzero().flatten(),'takeoff')
        self.took_off|=launch
        self.phase[launch]=3
        self.phase_time[launch]=age[launch]
        self.flight_start[launch]=age[launch]
        flying=(self.phase==3)&no_support
        self.air_total+=flying*self.step_dt
        self.flight_pitch=torch.where(flying,torch.maximum(self.flight_pitch,pitch),self.flight_pitch)
        self.flight_roll=torch.where(flying,torch.maximum(self.flight_roll,roll),self.flight_roll)
        self.rim_peak=torch.where(flying,torch.maximum(self.rim_peak,rim),self.rim_peak)
        retraction=flying&self.extended&(delta<.9)
        self._count((retraction&~self.retracted).nonzero().flatten(),'retracted')
        self.retracted|=retraction
        upright=flying&(self.air_total>=.16)&(self.flight_pitch<=math.radians(10))&(self.flight_roll<=math.radians(5))
        new=upright&~self.upright_flight
        self._count(new.nonzero().flatten(),'upright_flight')
        self.upright_flight|=upright
        land=(self.phase==3)&(self.air_total>=.08)&supported.any(1)&(d.root_lin_vel_w[:,2]<.3)
        self._count(land.nonzero().flatten(),'landed')
        self.landed|=land
        self.phase[land]=4
        self.phase_time[land]=age[land]
        self.support_history[self._support_slot]=supported.float()
        self._support_slot=(self._support_slot+1)%25
        duty=self.support_history.mean(0).amin(1)
        forbidden=forces[:,self.reward._reset_contact_link_idx].norm(dim=-1).amax(1)>1.
        stable=(self.phase==4)&(roll<math.radians(15))&(pitch<math.radians(15))&(d.root_lin_vel_w[:,2].abs()<.3)&(duty>=.8)&(~forbidden)&(d.root_lin_vel_b[:,0]>.10)
        self.stable_hold=torch.where(stable,self.stable_hold+self.step_dt,torch.zeros_like(self.stable_hold))
        balanced=(self.flight_pitch<=math.radians(10))&(self.flight_roll<=math.radians(5))
        success=(self.stable_hold>=.5)&(self.rim_peak>=.12)&(self.air_total>=.16)&self.extended&self.retracted&balanced&~self.completed
        self._count(success.nonzero().flatten(),'success')
        self.completed|=success
        self.jump_extra=6.*launch.float()+4.*land.float()+12.*success.float()
        self.jump_snapshot=dict(phase=self.phase.clone(),crouched=self.crouched.clone(),extended=self.extended.clone(),takeoff=self.took_off.clone(),retracted=self.retracted.clone(),landed=self.landed.clone(),success=self.completed.clone(),air_s=self.air_total.clone(),rim_peak=self.rim_peak.clone(),air_pitch=self.flight_pitch.clone(),air_roll=self.flight_roll.clone(),stable_hold=self.stable_hold.clone(),age=age.clone(),vx=d.root_lin_vel_b[:,0].clone())

    def _get_dones(self):
        term,timeout=super()._get_dones()
        if self._jump_ready:
            self._advance_task()
            local=self.view.data.root_pos_w-self.scene.env_origins
            boundary=(local[:,0].abs()>4.1)|(local[:,1].abs()>2.)
            term|=boundary
            timeout|=self.episode_length_buf*self.step_dt>=6.
            timeout&=~term
            self.reward.reset_terminated.copy_(term)
        return term,timeout

    def _get_rewards(self):
        legacy=super()._get_rewards()
        if not self._jump_ready:return legacy
        d=self.view.data
        q=tensor(self.robot.data.joint_pos)[:,self.active_ids]
        delta=torch.stack((q[:,0]-q[:,1],q[:,2]-q[:,3]),1).mean(1)
        rpy=euler_xyz_from_quat(d.root_quat_w)
        pitch,roll=rpy[1],rpy[0]
        velocity=d.root_lin_vel_b[:,0]
        track=torch.exp(-((velocity-self.command[:,0])/.35).square())
        orient=torch.exp(-(pitch/.174533).square()-(roll/.0872665).square())
        torque=(self.applied_motor_torque[:,:4]/40.).square().mean(1)
        reward=track+.5*orient-.03*torque-.02*d.root_ang_vel_b.square().sum(1)
        crouch=(self.phase==1).float()
        push=(self.phase==2).float()
        air=(self.phase==3).float()
        descending=d.root_lin_vel_w[:,2]<0.
        air_target=torch.where(descending,torch.full_like(delta,1.35),torch.full_like(delta,.25))
        reward+=crouch*3.*torch.exp(-((delta-.55)/.30).square())
        reward+=push*(3.*torch.exp(-((delta-1.75)/.30).square())+3.*d.root_lin_vel_w[:,2].clamp(0,1.5)/1.5)
        reward+=air*(3.*orient+1.5*torch.exp(-((delta-air_target)/.35).square()))
        reward+=(self.phase==4)*2.*orient
        reward+=self.jump_extra
        reward-=8.*self.reward.reset_terminated.float()
        self.terminal_observations=self._encode()
        return reward

    def _encode(self):
        raw=super()._encode()
        if not self._jump_ready:return raw
        mode=torch.zeros(self.num_envs,7,device=self.device)
        mode[:,0]=1.
        mode[:,1]=((self.phase>=1)&(~self.completed)).float()
        mode[:,2]=((self.phase==3)&(self.air_count>0)).float()
        mode[:,3]=self.landed.float()
        raw['policy'][:,28:35]=mode
        privileged=torch.nn.functional.one_hot(self.phase.clamp_max(6),7).float()
        raw['critic'][:,32:39]=privileged
        return raw

    def _get_observations(self):
        raw=super()._get_observations()
        if self._jump_ready:
            raw['jump_target']=self.teacher_actions(raw['policy']).detach()
        return raw

    def teacher_actions(self,obs):
        if self.teacher_net is None:return torch.zeros(self.num_envs,6,device=self.device)
        with torch.no_grad():
            clean=obs.clone()
            clean[:,28:35]=0.
            clean[:,28]=1.
            result=self.teacher_net(clean).clamp(-6,6)
            default=tensor(self.robot.data.default_joint_pos)[:,self.active_ids]
            age=self.episode_length_buf*self.step_dt
            elapsed=age-self.phase_time
            d=self.view.data
            rpy=euler_xyz_from_quat(d.root_quat_w)
            nominal_delta=torch.stack((default[:,0]+.5*result[:,0]-default[:,1]-.5*result[:,1],default[:,2]+.5*result[:,2]-default[:,3]-.5*result[:,3]),1).clamp(.172652,1.750894)
            target=nominal_delta.clone()
            alpha=(elapsed/.30).clamp(0,1)
            target=torch.where((self.phase==1)[:,None],nominal_delta*(1-alpha[:,None])+.5*alpha[:,None],target)
            target=torch.where((self.phase==2)[:,None],torch.full_like(target,1.750894),target)
            flight=self.phase==3
            tuck=(elapsed/.08).clamp(0,1)
            fly_target=1.750894+(torch.full_like(elapsed,.20)-1.750894)*tuck
            fly_target=torch.where(d.root_lin_vel_w[:,2]<-.10,torch.full_like(elapsed,1.35),fly_target)
            target=torch.where(flight[:,None],fly_target[:,None],target)
            active=(self.phase>=1)&(self.phase<=3)
            pitch_shift=(2.*rpy[1]+.2*d.root_ang_vel_b[:,1]).clamp(-.35,.35)*flight
            roll_shift=(.6*rpy[0]+.08*d.root_ang_vel_b[:,0]).clamp(-.15,.15)*flight
            target[:,0]-=roll_shift
            target[:,1]+=roll_shift
            target.clamp_(.172652,1.750894)
            for i,(front,rear) in enumerate(((0,1),(2,3))):
                mean=.5*(default[:,front]+.5*result[:,front]+default[:,rear]+.5*result[:,rear])+pitch_shift
                result[:,front]=torch.where(active,2.*(mean+target[:,i]/2-default[:,front]),result[:,front])
                result[:,rear]=torch.where(active,2.*(mean-target[:,i]/2-default[:,rear]),result[:,rear])
            wheel_v=tensor(self.robot.data.joint_vel)[:,self.active_ids[4:]]
            each=(8.*rpy[1]+d.root_ang_vel_b[:,1])*.5
            result[:,4:]=torch.where(flight[:,None],(wheel_v+each[:,None]/.6)/10.,result[:,4:])
            return result.clamp(-6,6)

    def _reset_idx(self,ids):
        super()._reset_idx(ids)
        if not self._jump_ready:return
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        self._count(ids,'episodes')
        for name in ('phase','phase_time','crouched','extended','retracted','took_off','landed','completed','upright_flight','air_count','air_total','flight_start','flight_pitch','flight_roll','rim_peak','stable_hold'):
            getattr(self,name)[ids]=0
        self.support_history[:,ids]=0
        self.speed[ids]=torch.empty(len(ids),device=self.device).uniform_(.4,.8)
        self.cue[ids]=torch.empty(len(ids),device=self.device).uniform_(1.9,2.5)
        root=tensor(self.robot.data.default_root_state)[ids].clone()
        root[:,:3]=self.scene.env_origins[ids]
        root[:,0]-=2.0
        pick=int((self._bank_h-.26).abs().argmin())
        root[:,2]+=self._bank_h[pick]
        yaw=torch.empty(len(ids),device=self.device).uniform_(-.04,.04)
        zero=torch.zeros_like(yaw)
        root[:,3:7]=quat_from_euler_xyz(zero,zero,yaw)
        root[:,7:]=0.
        q=self._bank_q[pick,self._bank_ids].expand(len(ids),-1).clone()
        self.robot.write_root_state_to_sim(root,env_ids=ids)
        self.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=ids)
        self.zero_torque_remaining[ids]=0
        self._ground_command_until[ids]=0
        self._sample_command(ids)
        self.reward.reset(ids)
        for cause in ('contact','orientation','other'):
            for suffix in ('_counter','_raw_buf'):
                value=getattr(self.reward,'_stair_'+cause+suffix,None)
                if value is not None:value[ids]=0
        for name in ('_stair_guide_allowed','_stair_contact_raw','_stair_suppressed_guide_raw'):
            value=getattr(self.reward,name,None)
            if value is not None:value[ids]=False
        self.reward.command.copy_(self.command)
        self.reward.height_cmd.copy_(self.height)

    def reset_distribution_summary(self):
        return dict(task='moving_jump',upright_only=True,feasible_pose_height_m=.26,
            yaw_rad=[-.04,.04],initial_velocity=0,command_vx_m_s=[.4,.8],
            command_ramp_s=[.8,1.1],jump_cue_s=[1.9,2.5],episode_seconds=6.,
            note='Task-specific reset replaces prior ground/fall distribution; DR ranges retained')

    def jump_summary(self):
        return dict(counts={k:v.tolist() for k,v in self.counts.items()},
            grouping=['fullDR','nominal'],active_phases=torch.bincount(self.phase,minlength=5).tolist(),
            max_rim_m=float(self.rim_peak.max()),max_air_pitch_deg=float(self.flight_pitch.max()*180/math.pi),
            max_closure_m=float(self.closure_error.max()),done_totals=dict(self.done_totals))
