"""Twenty-minute continuation: high body-height commands on ascending wide stairs."""
import math
import torch
from .scut_rough_scut_v1_env import ScutUnifiedRoughV1Env
from .scut_flat_env import tensor
from isaaclab.utils.math import quat_from_euler_xyz
from mod4v1_scut.math_ops import euler_xyz_from_quat

class ScutRoughV1StairLiftEnv(ScutUnifiedRoughV1Env):
    def __init__(self,cfg,meta,bank):
        self._stair_lift_ready=False
        super().__init__(cfg,meta,bank)
        n=self.num_envs;dev=self.device
        self.stair_approach=torch.zeros(n,dtype=torch.bool,device=dev)
        self.stair_target_height=torch.full((n,),.38,device=dev)
        self.stair_target_speed=torch.full((n,),2.,device=dev)
        self.stair_start_abs_x=torch.zeros(n,device=dev)
        self.stair_best_progress=torch.zeros(n,device=dev)
        self.stair_best_step=torch.zeros(n,dtype=torch.long,device=dev)
        self.stair_top_seen=torch.zeros(n,dtype=torch.bool,device=dev)
        self.stair_platform_z=torch.zeros(n,device=dev)
        self.stair_counts=torch.zeros(2,11,10,4,dtype=torch.long,device=dev)
        self.stair_reward_sum=torch.zeros((),device=dev)
        self.stair_height_error_sum=torch.zeros((),device=dev)
        self.stair_height_samples=torch.zeros((),device=dev)
        self._stair_lift_ready=True

    def _center(self,ids=None):
        center=self.terrain.terrain_origins[self.terrain.terrain_levels,self.terrain.terrain_types]
        return center if ids is None else center[ids]

    def _sample_command(self,ids):
        if getattr(self,'_stair_lift_ready',False):
            ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
            old=self.height[ids].clone()
        super()._sample_command(ids)
        if not getattr(self,'_stair_lift_ready',False):return
        selected=self.stair_approach[ids];picked=ids[selected]
        if picked.numel():
            self.height[picked]=old[selected]
            self.stair_target_height[picked]=torch.empty(len(picked),device=self.device).uniform_(.365,.4,generator=self.reset_generator)
            self.stair_target_speed[picked]=torch.empty(len(picked),device=self.device).uniform_(1.5,2.2,generator=self.reset_generator)
            self.heading_env[picked]=False;self.standing_env[picked]=False

    def _count(self,ids,column):
        if not ids.numel():return
        group=self.full_dr.nominal_env_mask[ids].long()
        index=group*110+self.terrain_family[ids]*10+self.terrain.terrain_levels[ids]
        self.stair_counts[...,column].reshape(-1).scatter_add_(0,index,torch.ones_like(index))

    def _reset_idx(self,ids):
        ids=torch.as_tensor(ids,device=self.device,dtype=torch.long).flatten()
        ready=getattr(self,'_stair_lift_ready',False)
        if ready:
            old=ids[self.stair_approach[ids]&self.reset_terminated[ids]]
            self._count(old,3)
            self.stair_approach[ids]=False
        super()._reset_idx(ids)
        if not ready or not ids.numel():return
        family=self.terrain_family[ids]
        selected=((family==0)|(family==4))&(~self.flat_terrain_mask[ids])&(torch.rand(len(ids),device=self.device,generator=self.reset_generator)<.5)
        picked=ids[selected]
        self.stair_best_progress[ids]=0.;self.stair_best_step[ids]=0;self.stair_top_seen[ids]=False
        if not picked.numel():return
        n=len(picked);center=self._center(picked)
        sign=torch.where(torch.rand(n,device=self.device,generator=self.reset_generator)<.5,-1.,1.)
        choices=((self._bank_h>=.22)&(self._bank_h<=.30)).nonzero().flatten()
        if not choices.numel():choices=(self._bank_h<=.34).nonzero().flatten()
        sample=choices[torch.randint(len(choices),(n,),device=self.device,generator=self.reset_generator)]
        q=self._bank_q[sample][:,self._bank_ids].clone()
        root=tensor(self.robot.data.default_root_state)[picked].clone()
        root[:,0]=center[:,0]+sign*3.75
        root[:,1]=center[:,1]+torch.empty(n,device=self.device).uniform_(-.3,.3,generator=self.reset_generator)
        # Positive pyramid stairs have outer ground z=0; inner platform is higher.
        root[:,2]=self._bank_h[sample]+.01
        yaw=torch.where(sign>0,math.pi,0.)
        root[:,3:7]=quat_from_euler_xyz(torch.zeros_like(yaw),torch.zeros_like(yaw),yaw)
        root[:,7:]=0.
        self.robot.write_root_state_to_sim(root,env_ids=picked)
        self.robot.write_joint_state_to_sim(q,torch.zeros_like(q),env_ids=picked)
        self.stair_approach[picked]=True
        self.stair_start_abs_x[picked]=3.75
        self.stair_platform_z[picked]=center[:,2]
        self.stair_target_height[picked]=torch.empty(n,device=self.device).uniform_(.365,.4,generator=self.reset_generator)
        self.stair_target_speed[picked]=torch.empty(n,device=self.device).uniform_(1.5,2.2,generator=self.reset_generator)
        self.height[picked]=.28;self.command[picked]=0.
        self.heading_env[picked]=False;self.standing_env[picked]=False
        self.actions[picked]=0.;self.torque[picked]=0.
        self.reward.ground_z_est[picked]=0.
        self.reward.command.copy_(self.command);self.reward.height_cmd.copy_(self.height)
        self.reward._invalidate_step_caches()
        self._count(picked,0)

    def _pre_physics_step(self,actions):
        super()._pre_physics_step(actions)
        if not getattr(self,'_stair_lift_ready',False):return
        picked=self.stair_approach.nonzero().flatten()
        if not picked.numel():return
        self.height[picked]+=(self.stair_target_height[picked]-self.height[picked]).clamp(-.06*.02,.06*.02)
        forward=self.episode_length_buf[picked]*self.step_dt>=3.
        self.command[picked,0]=torch.where(forward,self.stair_target_speed[picked],0.)
        self.command[picked,1:]=0.;self.heading_env[picked]=False

    def _get_rewards(self):
        base=super()._get_rewards()
        if not getattr(self,'_stair_lift_ready',False):return base
        center=self._center();pos=self.view.data.root_pos_w
        dx=(pos[:,0]-center[:,0]).abs();dy=(pos[:,1]-center[:,1]).abs()
        roll,pitch,_=euler_xyz_from_quat(self.view.data.root_quat_w)
        valid=self.stair_approach&(~self.reset_terminated)&(roll.abs()<.45)&(pitch.abs()<.45)
        progress=(self.stair_start_abs_x-dx).clamp_min(0.)
        advance=(progress-self.stair_best_progress).clamp_min(0.)
        self.stair_best_progress=torch.where(self.stair_approach,torch.maximum(self.stair_best_progress,progress),self.stair_best_progress)
        height=self.snapshots['height_obs']
        height_gate=torch.exp(-((height-self.height)/.05).square())
        rate=(advance/self.step_dt).clamp(0.,2.2)*height_gate*valid.float()
        ground=self.reward.ground_z_est
        step=(ground>=self.stair_platform_z*.45).long()+(ground>=self.stair_platform_z*.90).long()
        step=torch.where(valid,step,self.stair_best_step)
        new_steps=(step-self.stair_best_step).clamp_min(0)
        first=(new_steps>0)&(self.stair_best_step==0)&valid
        self._count(first.nonzero().flatten(),1)
        self.stair_best_step=torch.maximum(self.stair_best_step,step)
        top=valid&(ground>=self.stair_platform_z*.90)&(dx<1.25)&(dy<1.25)&(~self.stair_top_seen)
        self._count(top.nonzero().flatten(),2);self.stair_top_seen|=top
        extra=rate*self.step_dt+.5*new_steps.float()*valid.float()
        self.stair_reward_sum+=extra.sum()
        self.stair_height_error_sum+=((height-self.height).abs()*self.stair_approach).sum()
        self.stair_height_samples+=self.stair_approach.sum()
        return base+extra

    def terrain_summary(self):
        out=super().terrain_summary()
        if getattr(self,'_stair_lift_ready',False):
            out['stair_lift']=dict(active_approach_envs=int(self.stair_approach.sum()),height_command_range=[.365,.4],height_mean=float(self.height[self.stair_approach].mean()) if bool(self.stair_approach.any()) else None,command_range=[1.5,2.2],counts_DR_then_nominal=self.stair_counts.tolist(),columns=['attempts','first_step','platform','terminated'],height_abs_error_mean=float(self.stair_height_error_sum/self.stair_height_samples.clamp_min(1)),extra_reward_sum=float(self.stair_reward_sum),scope='Cumulative training attempts with raised command; not paired fixed-task graduation')
        return out

    def terrain_checkpoint_state(self):
        out=super().terrain_checkpoint_state()
        if getattr(self,'_stair_lift_ready',False):out['stair_lift_counts']=self.stair_counts.clone()
        return out

    def restore_terrain_curriculum(self,state):
        out=super().restore_terrain_curriculum(state)
        if state.get('stair_lift_counts') is not None:self.stair_counts.copy_(state['stair_lift_counts'].to(self.device))
        return out
