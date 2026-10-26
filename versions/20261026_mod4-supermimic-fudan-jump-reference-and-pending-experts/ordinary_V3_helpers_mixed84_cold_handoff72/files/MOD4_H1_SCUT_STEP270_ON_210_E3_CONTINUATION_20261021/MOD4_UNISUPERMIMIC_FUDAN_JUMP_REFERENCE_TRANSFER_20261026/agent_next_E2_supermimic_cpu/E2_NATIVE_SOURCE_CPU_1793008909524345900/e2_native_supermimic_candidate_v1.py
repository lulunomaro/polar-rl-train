"""E2 source/CPU candidate: declared command references + own actual transition bridge.

No simulator/model/trainer is imported. No RNG is read or sampled. Planned
kinematics are task hypotheses, never measured demonstrations/WM groundtruth.
Original source owns commands, clipping6, delay, PD/DR, physical rewards/resets.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import torch
import torch.nn.functional as F

KIND="E2_WORLD_MOVING_SIGNED4"
QUALIFIED_SOURCE_SHA="72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f"
QUALIFIED_SOURCE_ADAM=857460
CONTROL_DT=.02
PHYSICS_DT=.0025
DECIMATION=8
PLAN_STRIDE=1024  # >16s*50Hz; prefix is immutable plan ID, suffix its control clock.
STATE_KEY="supermimic_state"
TRANSITION_KEY="supermimic"
ACTION_ORDER=("left_crank","left_hip","right_crank","right_hip","left_wheel_spin","right_wheel_spin")
FLAG_ORDER=("is_standing_env","is_heading_env","is_pure_spin","is_moving_spin","is_transition_spin")
CONTEXT_SLICES={"mean_force_history18":(0,18),"applied_torque30":(18,48),"actual_command_body3":(48,51),
 "command_flags5":(51,56),"world_direction_cos_sin":(56,58),"signed_yaw":(58,59),"phase_elapsed":(59,60),
 "world_progress_goal":(60,61),"body_speed_limit":(61,62),"height_command":(62,63),"manual_mode":(63,64),
 "leg_delay_history12":(64,76),"leg_delay_lag_age":(76,78),"wheel_delay_history6":(78,84),
 "wheel_delay_lag_age":(84,86),"previous_processed_targets6":(86,92),"command_time_left":(92,93)}


class E2ContractError(ValueError):pass
class PlanCapacitySaveRequired(E2ContractError):pass


def require(value,message):
    if not value:raise E2ContractError(message)


def checked(value,shape,name):
    require(torch.is_tensor(value) and tuple(value.shape)==tuple(shape),f"{name} shape mismatch")
    require(bool(torch.isfinite(value).all()),f"{name} nonfinite")
    return value


def quat_to_mat(q):
    q=F.normalize(q,dim=-1);w,x,y,z=q.unbind(-1)
    return torch.stack((1-2*(y*y+z*z),2*(x*y-w*z),2*(x*z+w*y),2*(x*y+w*z),1-2*(x*x+z*z),2*(y*z-w*x),
                        2*(x*z-w*y),2*(y*z+w*x),1-2*(x*x+y*y)),-1).reshape(q.shape[:-1]+(3,3))


def yaw_of(rotation):return torch.atan2(rotation[...,1,0],rotation[...,0,0])
def wrap(angle):return torch.atan2(torch.sin(angle),torch.cos(angle))


def invariant_features(state):
    p,r,v,w,q,dq=state;yaw=yaw_of(r);c,s=torch.cos(yaw),torch.sin(yaw)
    heading=torch.zeros_like(r);heading[...,0,0]=c;heading[...,0,1]=-s;heading[...,1,0]=s;heading[...,1,1]=c;heading[...,2,2]=1
    relative=heading.transpose(-1,-2)@r;rt=r.transpose(-1,-2)
    return torch.cat((p[...,2:3],relative[...,:,:2].reshape(p.shape[:-1]+(6,)),(rt@v.unsqueeze(-1)).squeeze(-1),
                      (rt@w.unsqueeze(-1)).squeeze(-1),q,dq),-1)


def unpack73(value):
    require(value.shape[-1]==73,"own state requires 30 joints")
    return value[...,:3],quat_to_mat(value[...,3:7]),value[...,7:10],value[...,10:13],value[...,13:43],value[...,43:73]


def pack_actual_root_xyzw(root13,q30,dq30,env_origins):
    """Only subtract own origins and reorder measured xyzw->wxyz; preserve all other values."""
    n=len(root13);checked(root13,(n,13),"actual root13");checked(q30,(n,30),"actual q30");checked(dq30,(n,30),"actual dq30")
    checked(env_origins,(n,3),"origins")
    root=root13.detach().clone();root[:,:3]-=env_origins;root[:,3:7]=root[:,[6,3,4,5]]
    return torch.cat((root,q30.detach(),dq30.detach()),-1)


def transition_yaw(elapsed,target):
    # Same piecewise public command function as e2_directional_spin_runtime_v1.
    scale=torch.where(elapsed<1,elapsed,torch.where(elapsed<4,1.,torch.where(elapsed<5,5-elapsed,
          torch.where(elapsed<6,0.,torch.where(elapsed<7,-(elapsed-6),torch.where(elapsed<10,-1.,
          torch.where(elapsed<11,elapsed-11,0.)))))))
    return target*scale


def transition_yaw_integral(t):
    """Analytic integral of the declared yaw profile, not plant integration."""
    t=t.clamp_min(0)
    return torch.where(t<1,.5*t*t,torch.where(t<4,t-.5,torch.where(t<5,3.5+(t-4)-.5*(t-4).square(),
           torch.where(t<6,4.,torch.where(t<7,4-.5*(t-6).square(),torch.where(t<10,3.5-(t-7),
           torch.where(t<11,.5-(t-10)+.5*(t-10).square(),0.)))))))


def body_command(progress,direction,heading,limit):
    vx=2*progress*torch.cos(heading-direction)
    return torch.maximum(torch.minimum(vx,limit),-limit),torch.zeros_like(vx)


def project_world_velocity(vxy,direction):
    c,s=torch.cos(direction),torch.sin(direction)
    return vxy[...,0]*c+vxy[...,1]*s,-vxy[...,0]*s+vxy[...,1]*c


def planned_world_moving_path(t,heading,alpha,speed,omega):
    """Analytic ideal nonholonomic command path; includes twice-yaw cross ripple."""
    theta=heading+omega*t;safe=torch.where(omega.abs()>1e-6,omega,torch.ones_like(omega))
    angle0=2*heading-alpha;angle=2*theta-alpha
    vx=2*speed*torch.cos(theta-alpha);worldvx=vx*torch.cos(theta);worldvy=vx*torch.sin(theta)
    dx=speed*torch.cos(alpha)*t+speed/(2*safe)*(torch.sin(angle)-torch.sin(angle0))
    dy=speed*torch.sin(alpha)*t-speed/(2*safe)*(torch.cos(angle)-torch.cos(angle0))
    dx=torch.where(omega.abs()>1e-6,dx,worldvx*t);dy=torch.where(omega.abs()>1e-6,dy,worldvy*t)
    return torch.stack((dx,dy),-1),torch.stack((worldvx,worldvy),-1)


@dataclass
class ActualSnapshot:
    """All tensors are source readbacks; this class does not run the source command updater."""
    packed73:torch.Tensor
    mean_force_history:torch.Tensor
    applied_torque30:torch.Tensor
    command_body3:torch.Tensor
    flags5:torch.Tensor
    world_direction:torch.Tensor
    signed_yaw:torch.Tensor
    phase_elapsed:torch.Tensor
    progress_goal:torch.Tensor
    body_speed_limit:torch.Tensor
    height_command:torch.Tensor
    manual_mode:torch.Tensor
    command_time_left:torch.Tensor
    ground_local_z:torch.Tensor
    leg_delay_history:torch.Tensor
    leg_delay_lag:torch.Tensor
    leg_delay_age:torch.Tensor
    wheel_delay_history:torch.Tensor
    wheel_delay_lag:torch.Tensor
    wheel_delay_age:torch.Tensor
    processed_targets6:torch.Tensor
    source_stage:str="actual_current_pre_action"
    source_kind:str=KIND

    def validate(self):
        n=len(self.packed73);require(self.source_kind==KIND,"wrong source expert kind")
        for name,shape in {"packed73":(n,73),"mean_force_history":(n,3,2,3),"applied_torque30":(n,30),
             "command_body3":(n,3),"flags5":(n,5),"leg_delay_history":(3,n,4),"wheel_delay_history":(3,n,2),
             "processed_targets6":(n,6)}.items():checked(getattr(self,name),shape,name)
        scalar=("world_direction","signed_yaw","phase_elapsed","progress_goal","body_speed_limit","height_command","manual_mode",
                "command_time_left","ground_local_z","leg_delay_lag","leg_delay_age","wheel_delay_lag","wheel_delay_age")
        for name in scalar:checked(getattr(self,name),(n,),name)
        require(bool(torch.isin(self.flags5,torch.tensor([0,1],device=self.flags5.device,dtype=self.flags5.dtype)).all()),"command flags must be binary")
        stand,heading,pure,moving,transition=self.flags5.unbind(-1)
        require(not bool(heading.any()) and not bool((pure.bool()&moving.bool()).any()),"invalid original heading/mode state")
        require(not bool((transition.bool()&~pure.bool()).any()) and not bool((stand.bool()&(pure.bool()|moving.bool())).any()),"overlapping source modes")
        require(bool((self.command_time_left>=0).all()),"negative original resampling timer")
        require(bool((self.body_speed_limit>0).all() and (2*self.progress_goal<=self.body_speed_limit).all()),
                "analytic moving path requires the actual unclipped body projection range")
        return self

    def context93(self):
        self.validate()
        scalar=lambda x:x[:,None]
        return torch.cat((self.mean_force_history.flatten(1),self.applied_torque30,self.command_body3,self.flags5,
            scalar(torch.cos(self.world_direction)),scalar(torch.sin(self.world_direction)),scalar(self.signed_yaw),
            scalar(self.phase_elapsed),scalar(self.progress_goal),scalar(self.body_speed_limit),scalar(self.height_command),
            scalar(self.manual_mode),self.leg_delay_history.permute(1,0,2).flatten(1),
            scalar(self.leg_delay_lag),scalar(self.leg_delay_age),self.wheel_delay_history.permute(1,0,2).flatten(1),
            scalar(self.wheel_delay_lag),scalar(self.wheel_delay_age),self.processed_targets6,scalar(self.command_time_left)),-1).detach().clone()

    def signature(self):
        # Actual changing heading/body projection/elapsed/time_left do not create a
        # new plan every step. Resampling/episode reset is detected separately.
        literal=(self.manual_mode>0)|(~self.flags5[:,2].bool()&~self.flags5[:,3].bool()&~self.flags5[:,4].bool()&~self.flags5[:,0].bool())
        return torch.cat((self.flags5,self.world_direction[:,None],self.signed_yaw[:,None],self.progress_goal[:,None],
                          self.body_speed_limit[:,None],self.height_command[:,None],self.manual_mode[:,None],
                          torch.where(literal[:,None],self.command_body3,torch.zeros_like(self.command_body3))),1)


class E2ReferenceBook:
    """Immutable command intervals; native scalar frames encode planID*1024+control.

    Original random command draws are observed only after they happen. The book
    neither samples RNG nor invents future draws. No plan is overwritten while
    replay may reference it. Capacity/cooperative complete save is an owner task.
    """
    def __init__(self,*,device="cpu",max_plans=100000):
        self.device=torch.device(device);self.max_plans=int(max_plans)
        self.table=torch.empty((0,16),device=self.device,dtype=torch.float32)
        self.revision=0;self._source_book=None;self._source_revision=None

    def register(self,snapshot,ids):
        snapshot.validate();ids=ids.to(snapshot.packed73.device);count=len(ids)
        require(self._source_book is None,"learner-side reference view may not register source commands")
        if len(self.table)+count>self.max_plans:raise PlanCapacitySaveRequired("reference book capacity reached; owner complete-save boundary required, no plan overwritten")
        stand,_,pure,moving,transition=snapshot.flags5[ids].unbind(-1)
        mode=torch.where(stand>0,0,torch.where(moving>0,3,torch.where(transition>0,4,torch.where(pure>0,2,1))))
        mode=torch.where(snapshot.manual_mode[ids]>0,5,mode)
        p=snapshot.packed73[ids,:3];heading=yaw_of(quat_to_mat(snapshot.packed73[ids,3:7]))
        available=torch.floor(snapshot.command_time_left[ids]/CONTROL_DT).clamp(0,PLAN_STRIDE-1)
        phase_anchor=(snapshot.phase_elapsed[ids]-CONTROL_DT).clamp_min(0)
        rows=torch.stack((mode.float(),snapshot.world_direction[ids],snapshot.signed_yaw[ids],snapshot.progress_goal[ids],
            snapshot.body_speed_limit[ids],phase_anchor,*snapshot.command_body3[ids].unbind(-1),p[:,0],p[:,1],
            snapshot.ground_local_z[ids]+snapshot.height_command[ids],heading,available,snapshot.command_time_left[ids],ids.float()),-1)
        start=len(self.table);self.table=torch.cat((self.table,rows.to(self.device)),0);self.revision+=1
        return torch.arange(start,start+count,device=self.device,dtype=torch.int64)*PLAN_STRIDE

    def lookup(self,frames):
        self._synchronize_source()
        plan=torch.div(frames.long(),PLAN_STRIDE,rounding_mode="floor");step=frames.long()%PLAN_STRIDE
        require(bool((plan>=0).all() and (plan<len(self.table)).all()),"unknown E2 plan ID")
        return self.table[plan],step

    def reference(self,frames):
        row,step=self.lookup(frames);t=step.float()*CONTROL_DT
        mode,alpha,omega,speed,limit,phase=row[...,:6].unbind(-1)
        vx0,vy0,wz0=row[...,6:9].unbind(-1);x0,y0,z0,heading=row[...,9:13].unbind(-1)
        moving=mode==3;pure=(mode==2)|(mode==4);transition=mode==4;stand=mode==0
        theta=heading+torch.where(transition,omega*(transition_yaw_integral(phase+t)-transition_yaw_integral(phase)),
                                  torch.where(mode==5,wz0,omega)*t)
        theta=torch.where((mode==1)|stand,heading,theta)
        moving_path,moving_velocity=planned_world_moving_path(t,heading,alpha,speed,omega)
        dx,dy=moving_path.unbind(-1)
        vx,vy=body_command(speed,alpha,theta,limit)
        worldvx=vx*torch.cos(theta);worldvy=vx*torch.sin(theta)
        # Straight/manual constant BODY twist has its own circle/line reference.
        rate=torch.where(mode==5,wz0,torch.zeros_like(wz0));safe_rate=torch.where(rate.abs()>1e-6,rate,torch.ones_like(rate))
        constant_theta=heading+rate*t
        cx=vx0/safe_rate*(torch.sin(constant_theta)-torch.sin(heading))+vy0/safe_rate*(torch.cos(constant_theta)-torch.cos(heading))
        cy=-vx0/safe_rate*(torch.cos(constant_theta)-torch.cos(heading))+vy0/safe_rate*(torch.sin(constant_theta)-torch.sin(heading))
        cvx=vx0*torch.cos(constant_theta)-vy0*torch.sin(constant_theta);cvy=vx0*torch.sin(constant_theta)+vy0*torch.cos(constant_theta)
        cx=torch.where(rate.abs()>1e-6,cx,cvx*t);cy=torch.where(rate.abs()>1e-6,cy,cvy*t)
        x=x0+torch.where(moving,dx,torch.where(pure|stand,0.,cx));y=y0+torch.where(moving,dy,torch.where(pure|stand,0.,cy))
        z=torch.zeros_like(x)
        command_yaw=torch.where(transition,transition_yaw(phase+t,omega),torch.where(mode==5,wz0,omega))
        command_yaw=torch.where(stand|(mode==1),0.,command_yaw)
        velocity=torch.stack((torch.where(moving,worldvx,torch.where(pure|stand,0.,cvx)),
                              torch.where(moving,worldvy,torch.where(pure|stand,0.,cvy)),z),-1)
        result=torch.zeros(frames.shape+(73,),device=frames.device,dtype=torch.float32)
        result[...,:3]=torch.stack((x,y,z0),-1)
        result[...,3]=torch.cos(theta*.5);result[...,6]=torch.sin(theta*.5)
        result[...,7:10]=velocity;result[...,12]=command_yaw
        return result

    def effective_command(self,state,frames):
        row,step=self.lookup(frames);mode=row[...,0];heading=yaw_of(state[1]);vx,_=body_command(row[...,3],row[...,1],heading,row[...,4])
        command=row[...,6:9].clone()
        command[...,0]=torch.where(mode==3,vx,command[...,0]);command[...,1]=torch.where(mode==3,0.,command[...,1])
        command[...,2]=torch.where(mode==4,transition_yaw(row[...,5]+step.float()*CONTROL_DT,row[...,2]),command[...,2])
        # Offset zero retains the exact source readback, not a recomputed guess.
        return torch.where((step==0)[...,None],row[...,6:9],command)

    def to(self,device):
        device=torch.device(device)
        if device==self.device:return self
        copy=E2ReferenceBook(device=device,max_plans=self.max_plans);copy._source_book=self;copy._synchronize_source();return copy

    def _synchronize_source(self):
        if self._source_book is not None:
            source=self._source_book;source._synchronize_source()
            if self._source_revision!=source.revision:
                self.table=source.table.to(self.device).clone();self._source_revision=source.revision;self.revision=source.revision

    def state_dict(self):return dict(schema="mod4.e2.reference_book.v1",table=self.table.detach().clone(),max_plans=self.max_plans,plan_stride=PLAN_STRIDE,control_dt_s=CONTROL_DT)
    def load_state_dict(self,state):
        require(state["schema"]=="mod4.e2.reference_book.v1" and state["plan_stride"]==PLAN_STRIDE and state["control_dt_s"]==CONTROL_DT,"reference-book schema/clock mismatch")
        table=state["table"];checked(table,(len(table),16),"reference plan table")
        require(len(table)<=self.max_plans,"saved plan capacity exceeds configured capacity");self.table=table.to(self.device).clone();self.revision+=1


class E2GoalMdp:
    num_joints=30;action_dim=6;context_dim=93;obs_dim=175;goal_frame_dim=73;max_step_reward=1.
    def __init__(self,book):self.book=book
    def to(self,device):return E2GoalMdp(self.book.to(device))
    def normalize_context(self,context):return torch.tanh(context)
    def add_noise(self,obs):return obs
    def relative_error(self,state,frames):
        target=self.book.reference(frames);r=state[1];yaw=yaw_of(r);delta=target[...,:2]-state[0][...,:2]
        c,s=torch.cos(yaw),torch.sin(yaw);targetyaw=2*torch.atan2(target[...,6],target[...,3])
        return torch.stack((c*delta[...,0]+s*delta[...,1],-s*delta[...,0]+c*delta[...,1],wrap(targetyaw-yaw)),-1)
    def obs(self,state,previous_action,context,frames):
        ctx=context.clone();ctx[...,48:51]=self.book.effective_command(state,frames)
        row,step=self.book.lookup(frames);ctx[...,59]=row[...,5]+CONTROL_DT+step.float()*CONTROL_DT
        ctx[...,92]=(row[...,14]-step.float()*CONTROL_DT).clamp_min(0)
        return torch.cat((invariant_features(state),previous_action,self.normalize_context(ctx),self.relative_error(state,frames)),-1)
    def goal(self,frames,num_frames):
        require(isinstance(num_frames,int) and num_frames>0,"positive goal count required")
        # Planned joints/wheel spin are unobserved, so all q/dq channels stay zero
        # and are excluded from the objective. Pose/velocity are declared task plans.
        return torch.cat([self.book.reference(frames+i) for i in range(num_frames)],-1)
    def objective_terms(self,state,frames,action,previous_action):
        p,r,v,w,q,dq=state;rt=r.transpose(-1,-2);vb=(rt@v.unsqueeze(-1)).squeeze(-1);wb=(rt@w.unsqueeze(-1)).squeeze(-1)
        desired=self.book.effective_command(state,frames);target=self.book.reference(frames)
        cosine_pitch=(1-r[...,2,0].square()).clamp_min(0).sqrt()
        forward=(desired[...,0]-vb[...,0]*cosine_pitch).square()/.25
        yaw=(desired[...,2]-wb[...,2]).square()/.25
        height=15*(p[...,2]-target[...,2]).square()
        # Ideal cross ripple is in the target, so it is NOT scored as secular drift.
        path=.1*(p[...,:2]-target[...,:2]).square().sum(-1)
        upright=((r[...,2,2]+1)*.5).clamp(0,1)
        regularization=.001*(action-previous_action).square().mean(-1)+.0001*dq.square().mean(-1)
        total=upright*torch.exp(-forward-yaw-height-path)-regularization
        return dict(total=total,forward_cost=forward,yaw_cost=yaw,height_cost=height,declared_path_cost=path,
                    upright=upright,regularization=regularization)
    def reward(self,state,frames,action,previous_action):return self.objective_terms(state,frames,action,previous_action)["total"]
    def soft_termination(self,state,frames):return (torch.sigmoid((.12-state[0][...,2])*20)+torch.sigmoid((.3-state[1][...,2,2])*10)).clamp(0,1)
    def critic_features(self,state,frames,normalized_context):
        _,step=self.book.lookup(frames)
        return torch.cat((invariant_features(state),normalized_context,self.relative_error(state,frames),(step.float()/PLAN_STRIDE)[...,None]),-1)
    def valid_imagination_start(self,frames,horizon):
        row,step=self.book.lookup(frames)
        return (step+horizon<row[...,13])&(step+horizon<PLAN_STRIDE)
    def contract_manifest(self):
        return dict(schema="mod4.e2.native_supermimic_candidate.v1",kind=KIND,source_SHA=QUALIFIED_SOURCE_SHA,source_Adam=QUALIFIED_SOURCE_ADAM,
          original_source_PPO_obs_history175_critic98_not_native_compatibility=True,
          native_state73=True,joints30=True,actions6=list(ACTION_ORDER),native_context93=CONTEXT_SLICES,
          native_obs175="invariant73+previous6+context93+reference_error3",native_history_candidate=10,
          native_critic_base169="invariant73+context93+relative_error3+clock1",goal73="declared_plan_root_pose_velocity;q_dq_all_masked",
          control_dt_s=CONTROL_DT,physics_dt_s=PHYSICS_DT,decimation=DECIMATION,plan_stride=PLAN_STRIDE,
          reference_kind="declared_command_kinematic_hypothesis_not_measured_demonstration",
          moving_body_command="2V*cos(actual_or_imagined_heading-alpha),vy0,signed_yaw4",
          world_progress="V_along_alpha_over_complete_turns_not_constant_instantaneous_world_velocity",
          native_imagination_surrogate="separate_declared_velocity_yaw_height_periodic_path_tracking_not_original_physical_reward_reproduction",
          physical_reward="original_SCUT_and_stateful_cycle_cross_reward_unchanged",
          action_provenance="a=actual_ActionManager_ingress6_after_existing_vec_clip_before_delay/PD;processed_targets_and_delay_state_separate",
          world_model_groundtruth="only_actual_own_pre_reset_transitions;never_declared_plan_transitions",
          reference_book_save_required=True,reference_capacity_and_cross_device_sync_admission="pending_owner_runtime_review",
          command_resampling="original_private_RNG_untouched;unknown_future_draws_excluded_by_valid_imagination_start",
          actual_SDK_runtime_physics_feasibility_and_GO="pending_source_CPU_only",
          velocity_Metrics_success_rate_is_not_graduation=True,E0_W35_and_all_qualified_models="retained_no_checkpoint_loaded",
          numerical_guards="existing_float32_native160k_reuse_2mm_perenv_reset_no_new_global_gate")


@dataclass
class NativeBridgeState:
    info:dict
    reward:torch.Tensor
    terminated:torch.Tensor
    truncated:torch.Tensor
    obs:dict


class E2NativeBridge:
    """Source-only bridge; injected readers must be actual source-owned callbacks.
    Instantiation does not install hooks or enable source capture. Root's future
    original writer must admit callbacks and complete-save this book/bridge state.
    """
    def __init__(self,vec,read_current_snapshot,read_pre_reset_frame,book):
        self.vec=vec;self.read_current=read_current_snapshot;self.read_pre_reset=read_pre_reset_frame;self.book=book
        self.mdp=E2GoalMdp(book);self.state=None;self.frames=None;self.last_snapshot=None;self.ep_step=None
    @property
    def supermimic_mdp(self):return self.mdp
    def _frames_for(self,snapshot,done=None):
        n=len(snapshot.packed73);device=snapshot.packed73.device
        require(self.book.device==device,"source-side reference book must share the actual sampler device")
        if self.frames is None:changed=torch.ones(n,dtype=torch.bool,device=device);frames=torch.zeros(n,dtype=torch.int64,device=device)
        else:
            old=self.last_snapshot;frames=self.frames+1
            changed=((snapshot.signature()!=old.signature()).any(-1)|(snapshot.phase_elapsed<old.phase_elapsed-1e-5)|
                     (snapshot.command_time_left>old.command_time_left+CONTROL_DT))
            if done is not None:changed|=done.bool()
        ids=changed.nonzero(as_tuple=False).flatten()
        if len(ids):frames[ids]=self.book.register(snapshot,ids)
        self.frames=frames;self.last_snapshot=snapshot;return frames
    def init_state(self):
        snap=self.read_current().validate();f=self._frames_for(snap);n=len(f);dev=f.device
        self.ep_step=torch.zeros(n,dtype=torch.int32,device=dev);zero=torch.zeros(n,device=dev)
        info=dict(s=snap.packed73.detach().clone(),xi=snap.context93(),f=f.clone(),a_prev=torch.zeros((n,6),device=dev),ep_step=self.ep_step.clone())
        self.state=NativeBridgeState({STATE_KEY:info},zero,zero.bool(),zero.bool(),{});return self.state
    def step(self,requested_action6):
        require(self.state is not None,"initialize E2 bridge first")
        before=self.state.info[STATE_KEY]
        # No clipping/reordering/delay/PD/command changes here: original vec owns it.
        _,physical_reward,done,_=self.vec.step(requested_action6)
        terminal=self.read_pre_reset()
        require(terminal["source_stage"]=="termination_manager_compute_pre_reset","actual pre-reset terminal reader required")
        actual_s1=terminal["packed73"];actual_ingress=terminal["action_manager_ingress6"]
        checked(actual_s1,(len(done),73),"actual terminal73");checked(actual_ingress,(len(done),6),"actual source ingress6")
        transition=dict(s=before["s"],s1=actual_s1.detach().clone(),a=actual_ingress.detach().clone(),a_prev=before["a_prev"],
                        xi=before["xi"],r=physical_reward.detach().clone(),f=before["f"],ep_step=before["ep_step"],done=done.bool())
        snap=self.read_current().validate();f=self._frames_for(snap,done);self.ep_step=torch.where(done.bool(),0,self.ep_step+1).to(torch.int32)
        previous=actual_ingress.detach().clone();previous[done.bool()]=0
        info=dict(s=snap.packed73.detach().clone(),xi=snap.context93(),f=f.clone(),a_prev=previous,ep_step=self.ep_step.clone())
        self.state=NativeBridgeState({STATE_KEY:info,TRANSITION_KEY:transition},physical_reward,done.bool(),torch.zeros_like(done,dtype=torch.bool),{})
        return self.state
