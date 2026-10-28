"""Native127 MOD4 step adapter. Source candidate; requires new typed admission.

Fudan-inspired state-conditioned reward, static terminal task-space goal.
It is neither the upstream two-policy switching controller nor a measured
joint-motion reference. Original real270mm success remains independently exact.
"""
import math
import torch
from converted_MOD4_jump_mdp_v4 import ConvertedMOD4JumpMdp,require
from own_step_differentiable_geometry_v1 import OwnStepWheelGeometry
from private_phase_frame_v1 import decode as decode_private_frame
from static_dynamic_delay_contract_v1 import task_relative_observation
from mod4_fudan_contact_phase_reward_candidate_v2 import BoundOwnStepReward,contact_and_step_modes,combined_reward,UPSTREAM_COMMIT

class OwnFudanStepReference:
    def __init__(self,document,device='cpu',*,order_scope='unbound'):
        require(document['schema']=='mod4.own_fudan_step_terminal_goal.v1','typed Fudan step goal')
        self.document=document;self.device=torch.device(device);self.order_scope=order_scope
        self.names=tuple(document['joint_names']);self.metadata=document['metadata']
        require(len(self.names)==len(set(self.names))==30,'named physical30')
        require(self.metadata['control_dt_s']==.01 and self.metadata['request_age_ticks']==200,'original native100Hz and declared2s request')
        require(self.metadata['physical270_success_unchanged'] and not self.metadata['source_is_measured_successful_Fudan_joint_motion'],'own task goal, no counterfeit teacher')
        self.neutral=torch.tensor(document['neutral_packed73'],dtype=torch.float32,device=self.device)
        self.joint_scale=torch.tensor(self.metadata['joint_position_range_scale30'],dtype=torch.float32,device=self.device)
        require(self.neutral.shape==(73,) and self.joint_scale.shape==(30,) and torch.isfinite(self.neutral).all() and (self.joint_scale>0).all(),'finite source shapes')
        self.leg_ids=[self.names.index(x) for x in self.metadata['actuator_leg_joint_names']]
        self.parameters=BoundOwnStepReward(**self.metadata['bound_own_step_reward'])
    def bind_named_order(self,names,*,scope):
        names=tuple(names);require(scope in ('source_CPU_fixture','actual_SDK_readback') and len(names)==30 and set(names)==set(self.names),'exact named order')
        perm=[self.names.index(x) for x in names];cols=[*range(13),*[13+i for i in perm],*[43+i for i in perm]]
        doc=dict(self.document,joint_names=list(names),neutral_packed73=self.neutral[cols].cpu().tolist());doc['metadata']=dict(self.metadata,joint_position_range_scale30=self.joint_scale[perm].cpu().tolist())
        return OwnFudanStepReference(doc,self.device,order_scope=scope)
    def to(self,device):return OwnFudanStepReference(self.document,device,order_scope=self.order_scope)
    def active(self,frames):return decode_private_frame(frames)['public_age']>=200
    def query(self,frames):
        active=self.active(frames);p=self.parameters;value=self.neutral.expand(*frames.shape,73).clone()
        value[...,:2]=0;value[...,0]=torch.where(active,value.new_tensor(p.goal_root_x_m),value.new_tensor(0.))
        value[...,2]=p.standing_body_height_m+active.to(value.dtype)*p.step_top_z_m
        value[...,3:7]=value.new_tensor([1.,0.,0.,0.]);value[...,7:13]=0;value[...,43:73]=0
        mask=torch.zeros_like(value);mask[...,:13]=1
        return value,mask
    def future_goal(self,frames,num_frames):
        return torch.cat([torch.cat(self._masked_query(frames+i),-1) for i in range(num_frames)],-1)
    def _masked_query(self,frames):
        value,mask=self.query(frames);return value*mask,mask

class OwnFudanStepMdp(ConvertedMOD4JumpMdp):
    def __init__(self,provider,contract,geometry,leg_encoder_joint_names=None):
        super().__init__(provider,leg_encoder_joint_names);self.import_contract=contract;self.authored_geometry=geometry
        self.wheel_geometry=OwnStepWheelGeometry(contract,geometry,provider.names).to(provider.device)
        self.reward_parameters=provider.parameters;p=provider.parameters
        require(p.step_top_z_m==self.platform_top_z_m==.27 and p.step_edge_x_m==self.step_edge_x_m,'actual existing270 scene')
        self.leg_names=tuple(provider.metadata['actuator_leg_joint_names']);self.leg_indices=[provider.names.index(n) for n in self.leg_names]
        self.actuated_names=tuple(contract['actuated_joint_names']);require(set(self.leg_names).issubset(self.actuated_names) and len(self.actuated_names)==6,'actual six motors')
        self.actuated_indices=[provider.names.index(n) for n in self.actuated_names]
        self.hip_anchors=torch.tensor([contract['joints'][n]['local_pos0'] for n in ('left_hip','right_hip')],dtype=torch.float32,device=provider.device)
        require(all(contract['joints'][n]['parent']=='chassis' for n in ('left_hip','right_hip')),'recorded own hip anchors')
        limits=torch.tensor([contract['joints'][n]['limits_si'] for n in self.leg_names],dtype=torch.float32,device=provider.device)
        middle=limits.mean(-1);half=(limits[:,1]-limits[:,0])*.5*.97;self.soft_lower=middle-half;self.soft_upper=middle+half
    def to(self,device):return OwnFudanStepMdp(self.provider.to(device),self.import_contract,self.authored_geometry,self.leg_encoder_joint_names)
    def relative_features(self,state,frames):
        target,_=self.provider.query(frames);age=decode_private_frame(frames)['public_age'];shape=frames.shape;flat=age.reshape(-1)
        return task_relative_observation(state[0].reshape(-1,3),target[...,:3].reshape(-1,3),state[0].new_full((flat.numel(),),self.step_edge_x_m),state[0].new_full((flat.numel(),),self.platform_top_z_m),flat).reshape(*shape,7)
    def objective_terms(self,state,frames,action,previous_action):
        p,R,v,w,q,dq,aux=state;g=self.wheel_geometry(state);Rt=R.transpose(-1,-2)
        body_v=(Rt@v.unsqueeze(-1)).squeeze(-1);body_w=(Rt@w.unsqueeze(-1)).squeeze(-1)
        local_wheels=(Rt.unsqueeze(-3)@(g['centre']-p.unsqueeze(-2)).unsqueeze(-1)).squeeze(-1)-self.hip_anchors
        L0=local_wheels[...,[0,2]].norm(dim=-1);theta=torch.atan2(local_wheels[...,0],-local_wheels[...,2])
        history=aux[...,:18].reshape(*frames.shape,3,2,3);fz=torch.maximum(history[...,0,:,2],history[...,1,:,2])
        modes=contact_and_step_modes(g['low'],g['high'],fz,p[...,0],v[...,2],self.reward_parameters)
        active=self.provider.active(frames).to(p.dtype);modes['jump']=modes['jump']*active;modes['recovery']=1-modes['jump'];modes['command_forward_velocity']=modes['command_forward_velocity']*active
        leg_q=q[...,self.leg_indices];violation=(self.soft_lower-leg_q).clamp_min(0).sum(-1)+(leg_q-self.soft_upper).clamp_min(0).sum(-1)
        projected_gravity=-R[...,2,:]
        measurements=dict(flight=modes['flight'],takeoff=modes['takeoff'],virtual_leg_length=L0,virtual_leg_angle=theta,
            world_vertical_velocity=v[...,2],body_vertical_velocity=body_v[...,2],body_forward_velocity=body_v[...,0],body_yaw_velocity=body_w[...,2],
            command_forward_velocity=modes['command_forward_velocity'],command_yaw_velocity=torch.zeros_like(v[...,2]),root_height=p[...,2],
            relative_base_height=p[...,2]-modes['support_surface_height'],action=action,previous_action=previous_action,
            actuated_torque=aux[...,18:48][...,self.actuated_indices],actuated_leg_dq=dq[...,self.leg_indices],
            projected_gravity=projected_gravity,body_angular_velocity=body_w,actuated_soft_limit_violation=violation,root_planar_velocity=v[...,:2])
        result=combined_reward(measurements,self.reward_parameters,modes);result['contact_step_modes']=modes;return result
    def soft_termination(self,state,frames):
        height=torch.sigmoid((.12-state[0][...,2])/.02);tilt=torch.sigmoid((math.cos(.75)-state[1][...,2,2])/.04)
        timeout=(decode_private_frame(frames)['public_age']>=500).to(height.dtype)
        return 1-(1-height)*(1-tilt)*(1-timeout)
    def valid_imagination_start(self,frames,horizon):
        row=decode_private_frame(frames);return (frames>=0)&(row['delay_ticks']<250)&(row['public_age']<500)
    def contract_manifest(self):
        return dict(schema='mod4.native_supermimic.fudan_inspired_own270_step.v1',upstream_commit=UPSTREAM_COMMIT,
            packed_state=127,dynamic_aux=54,static_xi=31,actor_observation=86,goal_frame=146,future_goal_frames_expected=10,action_dim=6,
            reference_metadata=self.provider.metadata,reference_order_scope=self.provider.order_scope,
            virtual_leg_definition='own hip anchor to exact wheel-mesh centre projected to chassis sagittal XZ',
            actual_physical_reset_RNG_action_PD_delay_DR_and_success_unchanged=True,
            contact_modes_refreshed_on_every_actual_or_predicted_state=True,root_goal_is_terminal_task_pose_not_limb_mocap=True,
            actual270_cross_fullfootprint_topcontact12_stable200_callbacks_required=True,
            not_unmodified_upstream_reward_or_two_policy_controller=True,source_candidate_not_installed=True,successful_skill=False)
