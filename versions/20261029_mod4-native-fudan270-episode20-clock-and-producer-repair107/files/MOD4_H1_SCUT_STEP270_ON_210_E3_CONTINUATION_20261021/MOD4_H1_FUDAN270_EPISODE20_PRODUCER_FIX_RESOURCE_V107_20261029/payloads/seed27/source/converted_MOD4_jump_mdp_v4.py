"""MOD4-owned converted jump goal and native SuperMimic analytic heads.

Reference values and masks share the same table for real labels, policy goals and
imagined returns. The real plant, original hard termination, V8 trace and success
callbacks remain separate. No motion file is itself a successful physical case.
"""
from dataclasses import dataclass
import torch
from supermimic_wheel_leg_v3.geometry import invariant_features, quat_to_mat
from compact_episode_static31_v1 import normalize_static31
from static_dynamic_delay_contract_v1 import task_relative_observation

def require(ok,message):
    if not bool(ok):raise ValueError(message)

class ConvertedMOD4Reference:
    def __init__(self,document,device='cpu',*,order_scope='unbound'):
        require(document.get('schema')=='mod4.own_step_converted_reference.v1','explicit converted MOD4 reference schema required; old partial standing jump not a step reference')
        self.document=document;self.device=torch.device(device);self.order_scope=order_scope
        self.names=tuple(document['joint_names'])
        require(len(self.names)==30 and len(set(self.names))==30,'30 unique source joint names required')
        self.ages=torch.tensor(document['ages'],device=device,dtype=torch.long)
        require(self.ages.ndim==1 and len(self.ages)>=2 and self.ages[0]==0,'reference must include fresh age0')
        require(torch.equal(self.ages,torch.arange(len(self.ages),device=device)),'own reference needs each original control age; no hidden clock stretching')
        self.values=torch.tensor(document['packed73'],device=device,dtype=torch.float32)
        mask=torch.tensor(document['mask73'],device=device,dtype=torch.float32)
        if mask.ndim==1:mask=mask[None,:].expand(len(self.ages),-1).clone()
        self.mask=mask
        require(self.values.shape==(len(self.ages),73) and self.mask.shape==self.values.shape,'explicit reference/mask73 shape required')
        require(torch.isfinite(self.values).all() and torch.isfinite(mask).all(),'reference finite required')
        require(((mask==0)|(mask==1)).all(),'explicit binary known/unknown reference masks required')
        require((mask[:,3:7]==1).all(),'orientation reference required')
        require(torch.allclose(self.values[:,3:7].norm(dim=-1),torch.ones(len(self.ages),device=device),rtol=1e-5,atol=1e-5),'wxyz quaternion norm mismatch')
        self.metadata=document['metadata']
        require(self.metadata['control_dt_s']==.01,'original100Hz control clock required')
        require(self.metadata.get('foreign_transitions_for_world_model') is False,'foreign dynamics are not MOD4 WM truth')
        require(self.metadata.get('own_step_edge_x_m')==.35 and self.metadata.get('own_platform_height_m')==.27,'original270mm own terrain required')
        require(self.metadata.get('physical_success_unchanged') is True,'original true physical success criteria required')
        require(self.metadata.get('endpoint_policy')=='hold_pose_zero_velocities','explicit post-table endpoint policy required')
        self.leg_ids=[self.names.index(n) for n in self.metadata['actuator_leg_joint_names']]
        self.joint_scale=torch.tensor(self.metadata['joint_position_range_scale30'],device=device,dtype=torch.float32)
        require(self.joint_scale.shape==(30,) and (self.joint_scale>0).all() and torch.isfinite(self.joint_scale).all(),'own joint range scale required')

    def bind_named_order(self,actual_joint_names,*,scope):
        require(scope in ('source_CPU_fixture','actual_SDK_readback'),'explicit source-vs-SDK mapping scope required')
        actual=tuple(actual_joint_names)
        require(len(actual)==30 and set(actual)==set(self.names),'actual joint name set differs')
        permutation=[self.names.index(n) for n in actual]
        cols=[*range(13),*[13+i for i in permutation],*[43+i for i in permutation]]
        copied=dict(self.document)
        copied['joint_names']=list(actual)
        copied['packed73']=self.values[:,cols].cpu().tolist()
        copied['mask73']=self.mask[:,cols].cpu().tolist()
        copied['metadata']=dict(self.metadata,joint_position_range_scale30=self.joint_scale[permutation].cpu().tolist())
        # Scope records caller readback, not a substitute for signed actual SDK admission.
        return ConvertedMOD4Reference(copied,self.device,order_scope=scope)

    def to(self,device):
        return ConvertedMOD4Reference(self.document,device,order_scope=self.order_scope)

    def query(self,frames):
        idx=frames.long().clamp(0,len(self.ages)-1)
        value=self.values[idx].clone()
        beyond=frames.long()>self.ages[-1]
        value[...,7:13]=torch.where(beyond[...,None],torch.zeros_like(value[...,7:13]),value[...,7:13])
        value[...,43:73]=torch.where(beyond[...,None],torch.zeros_like(value[...,43:73]),value[...,43:73])
        return value,self.mask[idx]

    def future_goal(self,frames,num_frames):
        require(num_frames>=1,'positive future horizon required')
        result=[]
        for offset in range(num_frames):
            value,mask=self.query(frames+offset)
            result.append(torch.cat((value*mask,mask),-1))
        return torch.cat(result,-1)

class ConvertedMOD4JumpMdp:
    num_joints=30;action_dim=6;auxiliary_dim=54;packed_state_dim=127
    context_dim=31;obs_dim=86;goal_frame_dim=146
    step_edge_x_m=.35;platform_top_z_m=.27
    max_step_reward=.06

    def __init__(self,provider,leg_encoder_joint_names=None):
        require(provider.order_scope!='unbound','named joint mapping required before learner construction')
        self.provider=provider
        self.leg_encoder_joint_names=tuple(leg_encoder_joint_names or provider.metadata["actuator_leg_joint_names"])
        require(len(self.leg_encoder_joint_names)==4,"four actual leg encoder names required")
        self.leg_ids=[provider.names.index(n) for n in self.leg_encoder_joint_names]
    def to(self,device):return ConvertedMOD4JumpMdp(self.provider.to(device),self.leg_encoder_joint_names)
    def normalize_context(self,x):return normalize_static31(x)
    def add_noise(self,obs):return obs
    def goal(self,frames,num_frames):return self.provider.future_goal(frames,num_frames)
    def relative_features(self,state,frames):
        target,_=self.provider.query(frames)
        shape=frames.shape
        flat=frames.reshape(-1)
        edge=state[0].new_full((flat.numel(),),self.step_edge_x_m)
        top=state[0].new_full((flat.numel(),),self.platform_top_z_m)
        result=task_relative_observation(state[0].reshape(-1,3),target[...,:3].reshape(-1,3),edge,top,flat)
        return result.reshape(*shape,7)
    def obs(self,state,previous_action,context,frames):
        require(len(state)==7,'explicit dynamic state required')
        # Static privileged xi is NOT fed directly to the actor.
        q=state[4].clone()
        q[...,self.leg_ids]+=context[...,27:31]
        observed_state=(*state[:4],q,state[5])
        return torch.cat((invariant_features(observed_state),previous_action,
                          self.relative_features(state,frames)),-1)
    def critic_features(self,state,frames,normalized_context):
        return torch.cat((invariant_features(state[:6]),state[6],normalized_context,
                          self.relative_features(state,frames)),-1)
    def objective_terms(self,state,frames,action,previous_action):
        p,R,v,w,q,dq,aux=state
        target,mask=self.provider.query(frames)
        def masked_mean(error,m):
            return (error*m).sum(-1)/m.sum(-1).clamp_min(1)
        desired_R=quat_to_mat(target[...,3:7])
        pos_error=((p-target[...,:3]).square()*mask[...,:3]).sum(-1)
        ori_error=(R-desired_R).square().mean((-1,-2))
        vel_error=((v-target[...,7:10]).square()*mask[...,7:10]).sum(-1)
        ang_error=masked_mean((w-target[...,10:13]).square(),mask[...,10:13])
        q_error=masked_mean(((q-target[...,13:43])/self.provider.joint_scale).square(),mask[...,13:43])
        dq_error=masked_mean(((dq-target[...,43:73])/(self.provider.joint_scale/.1)).square(),mask[...,43:73])
        terms=dict(position=torch.exp(-pos_error/.3**2),
                   orientation=torch.exp(-ori_error/.4**2),
                   linear_velocity=torch.exp(-vel_error),
                   angular_velocity=torch.exp(-ang_error/3.14**2),
                   joint_position=torch.exp(-q_error),
                   joint_velocity=torch.exp(-dq_error))
        # Additive dense tracking follows the source method's structure, avoiding
        # the previous multiplication of independent near-zero task scores.
        tracking=sum(terms.values())
        action_rate=.1*(action-previous_action).square().sum(-1)
        terms['tracking_sum']=tracking
        terms['action_rate_cost']=action_rate
        terms['total']=(tracking-action_rate)*.01
        return terms
    def reward(self,state,frames,action,previous_action):
        return self.objective_terms(state,frames,action,previous_action)['total']
    def soft_termination(self,state,frames):
        # Original absolute physical low-height/tilt thresholds, using source-style
        # .02/.04 temperatures; actual hard callback truth remains independent.
        height_failure=torch.sigmoid((.12-state[0][...,2])/.02)
        tilt_failure=torch.sigmoid((.3-state[1][...,2,2])/.04)
        return 1-(1-height_failure)*(1-tilt_failure)
    def valid_imagination_start(self,frames,horizon):
        return torch.ones_like(frames,dtype=torch.bool)
    def contract_manifest(self):
        return dict(schema='mod4.native_supermimic.own_converted_jump_mdp.v3',
            physical_joints=30,packed_state=127,dynamic_aux=54,static_xi=31,
            actual_leg_encoder_joint_names=self.leg_encoder_joint_names,world_model_terrain_features=3,
            actor_observation=86,goal_frame=146,future_goal_frames_expected=10,
            reference_order_scope=self.provider.order_scope,
            reference_metadata=self.provider.metadata,
            reward='same additive masked own-reference tracking head on actual and imagined state',
            physical_V8_reward='unchanged original fulltrace, separate from native tracking return',
            position_and_velocity_errors='masked squared coordinate sums',
            soft_survival=dict(height_threshold=.12,tilt_Rzz_threshold=.3,height_temperature=.02,tilt_temperature=.04),
            termination='original hard callbacks unchanged; calibrated analytic native soft approximation',
            successful_skill=False,requires_actual_SDK_source_resource_admission=True)



