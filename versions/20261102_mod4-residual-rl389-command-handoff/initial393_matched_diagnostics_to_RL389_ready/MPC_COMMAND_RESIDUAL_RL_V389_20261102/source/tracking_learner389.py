"""Reference-conditioned H8 direct-error BPTT actor, H32 WM unchanged and matching tracking-cost critic."""
import torch
from torch import nn
from teacher_student292 import migrate,model,forward,policy_obs,binding_for,DEPTH_SCALE
from future_safe_wm_warm273 import context_from_start_anchor273
from native_depth_world_model50_v255 import normalize_context40
from bounded_actor292 import bounded_actor_step
from tracking_reference389 import GOAL_DIM,tracking_cost389 as tracking_cost389
from tracking_survival389 import matched_survival389
from residual_policy389 import ResidualPolicy389

ACTOR_DIM=44+GOAL_DIM
CRITIC_DIM=47+GOAL_DIM

def expand_actor389(actor,optimizer,identity,device):
    width=ACTOR_DIM;target=model(width,True,device)
    weights={k:v.detach().clone() for k,v in actor.state_dict().items()}
    first=weights['mlp.0.weight'];weights['mlp.0.weight']=torch.cat((first,first.new_zeros((128,GOAL_DIM))),-1)
    target.load_state_dict(weights,strict=True);target.distribution.std_param.requires_grad_(False)
    names=dict(target.named_parameters());source_names={id(p):n for n,p in actor.named_parameters()}
    groups=[dict(params=[names[source_names[id(p)]]for p in group['params']],**{k:v for k,v in group.items()if k!='params'})for group in optimizer.param_groups]
    opt=torch.optim.Adam(groups);state=optimizer.state_dict()
    source_ids={r['optimizer_id']:r['state_key']for r in identity['parameter_bindings']}
    for pid,slot in state['state'].items():
        if source_ids[pid]=='mlp.0.weight':
            for name in('exp_avg','exp_avg_sq'):
                x=slot[name];slot[name]=torch.cat((x,x.new_zeros((128,GOAL_DIM))),-1)
    opt.load_state_dict(state)
    receipt=binding_for({'actor':target},opt,'ACTUAL_TARGET_ADAM_NAME_ID_OBJECT_BINDING',
        source_identity_receipt_SHA=identity['identity_receipt_SHA'],optimizer_scope='actor',goal59_zero_suffix=True)
    return target,opt,receipt

class TrackingLearner389:
    def __init__(self,wm,carrier,reference,env,binding,cpu_sha,put):
        self.wm,self.env,self.reference,self.binding,self.put=wm,env,reference,binding,put
        self.actor=model(ACTOR_DIM,True,str(wm.device));self.critic=model(CRITIC_DIM,False,str(wm.device))
        saved=carrier['student'];self.actor.load_state_dict(saved['actor_state_dict']);self.critic.load_state_dict(saved['critic_state_dict'])
        self.actor.distribution.std_param.requires_grad_(False)
        from copy import deepcopy
        self.residual_origin_actor=deepcopy(self.actor).eval()
        for parameter in self.residual_origin_actor.parameters():parameter.requires_grad_(False)
        self.residual_policy=ResidualPolicy389(reference.path.parent/'feedforward389.json',wm.device)
        self.actor_optimizer=torch.optim.Adam(self.actor.parameters(),lr=1e-4)
        self.critic_optimizer=torch.optim.Adam(self.critic.parameters(),lr=1e-4)
        self.actor_optimizer.load_state_dict(saved['actor_optimizer']);self.critic_optimizer.load_state_dict(saved['critic_optimizer'])
        self.actor_offset=saved['actor_Adam_offset']+saved['Pi_updates'];self.critic_offset=saved['critic_Adam_offset']+saved['critic_updates']
        assert self.actor_offset==52636 and self.critic_offset==9696
        for opt in(self.actor_optimizer,self.critic_optimizer):
            for group in opt.param_groups:group['lr']=1e-4
        self.optimizers={'actor':self.actor_optimizer,'critic':self.critic_optimizer};self.networks={'actor':self.actor,'critic':self.critic}
        from copy import deepcopy
        self.target_critic=deepcopy(self.critic).eval()
        self.target_critic.load_state_dict(saved['target_critic_state_dict'],strict=True)
        for p in self.target_critic.parameters():p.requires_grad_(False)
        self.identity=dict(parent=saved['identity'],targets=dict(actor=binding_for({'actor':self.actor},self.actor_optimizer,'ACTUAL_RESTORED305_ACTOR_FULL_ADAM'),critic=binding_for({'critic':self.critic},self.critic_optimizer,'ACTUAL_RESTORED305_CRITIC_FULL_ADAM')),actor_Adam_offset=self.actor_offset,critic_Adam_offset=self.critic_offset)
        self.Pi_updates=self.critic_updates=self.proposals=0;self.initial_WM_updates=wm.updates;self.batch=256
        robot=env.scene['robot'];self.legs=[robot.joint_names.index(n)for n in('left_crank','left_hip','right_crank','right_hip')]
        self.wheels=[robot.joint_names.index(n)for n in('left_wheel_spin','right_wheel_spin')]
        self.wheelbodies=[robot.body_names.index(n)for n in('left_wheel','right_wheel')]
        self.saved={k:torch.zeros((64,80,*tail),device=wm.device,dtype=dtype)for k,tail,dtype in(
            ('policy',(35,),torch.float32),('critic',(38,),torch.float32),('phase',(),torch.int64),('next_critic',(38,),torch.float32),('next_depth',(9,),torch.float32))}
        put('ACTUAL389_TRACKING_THREE_OPTIMIZER_IDENTITIES.json',dict(passed=True,**self.identity,actor_dim=ACTOR_DIM,critic_dim=CRITIC_DIM,restored305_all_three_optimizers_and_EMAtarget=True))

    def add_metadata(self,slot,policy,critic,phase,next_critic,next_depth):
        for key,value in dict(policy=policy,critic=critic,phase=phase,next_critic=next_critic,next_depth=next_depth).items():self.saved[key][slot].copy_(value.detach())

    def action(self,policy,depth,packed,phase):
        state=self.wm.measured_layout.unpack(packed);envs=torch.arange(80,device=self.wm.device)
        goal=self.reference.goals(state,phase,envs,self.env.target389)
        x=torch.cat((policy,depth/depth.new_tensor(DEPTH_SCALE),goal),-1)
        return self.residual_policy.action(forward(self.actor,x),forward(self.residual_origin_actor,x),phase)

    def update(self,apply_step=True):
        wm=self.wm;b=wm.buffer;k=8;slots=b._row(torch.arange(b.size,device=wm.device))
        candidates=wm.anchors.data['valid_anchor'][slots].nonzero()
        if not len(candidates):return None
        draw=candidates[torch.randint(len(candidates),(self.batch,),device=wm.device,generator=wm.generator)]
        rows,envs=slots[draw[:,0]],draw[:,1];anchor=wm.anchors.gather(rows,envs)
        meta={n:x[rows,envs].detach().clone()for n,x in self.saved.items()}
        state=wm.measured_layout.unpack(b.data['s'][rows,envs].detach().clone());previous=b.data['a_prev'][rows,envs].detach().clone()
        actual_start=tuple(x.detach().clone()for x in state)
        alive=state[0].new_ones(self.batch);total=alive.new_zeros(self.batch);regularizer=total.clone()
        inputs=[];costs=[];survivals=[];component_sums={}
        for module in(wm.model,self.critic,self.target_critic):
            for p in module.parameters():p.requires_grad_(False)
        try:
            for i in range(k):
                context=context_from_start_anchor273(anchor,state,i,wm.native_geometry)
                obs,co=policy_obs(state,previous,meta['policy'],meta['critic'],context,self.legs,self.wheels)
                if i==0:
                    obs=torch.cat((meta['policy'],b.data['xi'][rows,envs,31:]/context.new_tensor(DEPTH_SCALE)),-1)
                    co=torch.cat((meta['critic'],b.data['xi'][rows,envs,31:]/context.new_tensor(DEPTH_SCALE)),-1)
                goal=self.reference.goals(state,meta['phase']+i,envs,self.env.target389)
                x=torch.cat((obs,goal),-1);cx=torch.cat((co,goal),-1)
                raw=self.residual_policy.raw(forward(self.actor,x),forward(self.residual_origin_actor,x),meta['phase']+i);action=raw.clamp(-6,6)
                if i==0:trust=x.detach().clone()
                following=wm.model.step(state,action,normalize_context40(context))
                label=self.reference.labels(meta['phase']+i,envs,self.env.target389)
                cost,terms=tracking_cost389(following,label,self.legs,self.wheelbodies,previous,raw)
                survival=matched_survival389(following)
                # Failure reduces future tracking opportunity; positive alive reward
                # makes termination unattractive while costs supply tracking gradients.
                reward=torch.exp(-cost/5.)
                total=total-(.99**i)*cost/5.  # direct tracking error; no exp attenuation or alive cost deletion
                for name,value in terms.items():component_sums[name]=component_sums.get(name,0.)+float(value.detach().mean())/k
                costs.append(reward.detach());survivals.append(survival.detach());inputs.append(cx.detach())
                alive=alive*survival;state,previous=following,action
            context=context_from_start_anchor273(anchor,state,k,wm.native_geometry)
            _,co=policy_obs(state,previous,meta['policy'],meta['critic'],context,self.legs,self.wheels)
            goal=self.reference.goals(state,meta['phase']+k,envs,self.env.target389);cx=torch.cat((co,goal),-1)
            terminal_value_diagnostic=forward(self.target_critic,cx).squeeze(-1).detach()
            terminal=total*0.  # Explicitly no learned terminal-value actor gradient.
            tracking_loss=-total.mean();terminal_loss=-terminal.mean();loss=tracking_loss+terminal_loss
            gradients={}
            if self.Pi_updates==0:
                parameters=tuple(p for p in self.actor.parameters()if p.requires_grad)
                for name,value in(('tracking_only',tracking_loss),('terminal_only',terminal_loss),('combined',loss)):
                    g=torch.autograd.grad(value,parameters,retain_graph=True,allow_unused=True)
                    assert all(v is None or torch.isfinite(v).all()for v in g)
                    gradients[name]=float(torch.sqrt(sum((v.square().sum()for v in g if v is not None),loss.new_zeros(()))))
                assert gradients['tracking_only']>0 and gradients['combined']>0
            self.actor_optimizer.zero_grad(set_to_none=True);loss.backward()
            norm=nn.utils.clip_grad_norm_(self.actor.parameters(),1.);assert torch.isfinite(norm)
            with torch.no_grad():before=forward(self.actor,trust).detach().clone()
            step=bounded_actor_step(self.actor,self.actor_optimizer,lambda x:forward(self.actor,x),trust,trust,before,apply_step=apply_step,radius=.05,retention_radius=.05)
            if apply_step:
                self.proposals+=1
                self.put('LATEST_ACTOR389_CONSTRAINT.json',dict(proposal=self.proposals,**step))
                if not step['applied']:
                    self.put('REJECTED_ACTOR389_PROPOSAL_'+str(self.proposals)+'.json',dict(proposal=self.proposals,**step));return None
                self.Pi_updates+=1
        finally:
            for module in(wm.model,self.critic):
                for p in module.parameters():p.requires_grad_(True)
        # One-step TD on actual own transitions, never imagined reward labels.
        with torch.no_grad():
            label_goal=self.reference.goals(actual_start,meta['phase'],envs,self.env.target389)
            actual_cx=torch.cat((meta['critic'],b.data['xi'][rows,envs,31:]/state[0].new_tensor(DEPTH_SCALE),label_goal),-1)
            next_state=wm.measured_layout.unpack(b.data['s1'][rows,envs])
            next_goal=self.reference.goals(next_state,meta['phase']+1,envs,self.env.target389)
            next_cx=torch.cat((meta['next_critic'],meta['next_depth']/state[0].new_tensor(DEPTH_SCALE),next_goal),-1)
            actual_reward=b.data['r'][rows,envs].reshape(-1)
            actual_done=b.data['done'][rows,envs].reshape(-1).bool()
            next_value=forward(self.target_critic,next_cx).squeeze(-1).clamp(0.,100.)
            td_target=actual_reward+.99*(~actual_done).float()*next_value
        prediction=forward(self.critic,actual_cx).squeeze(-1)
        value_loss=torch.nn.functional.smooth_l1_loss(prediction,td_target)
        self.critic_optimizer.zero_grad(set_to_none=True);value_loss.backward();cnorm=nn.utils.clip_grad_norm_(self.critic.parameters(),1.)
        assert torch.isfinite(cnorm)
        if apply_step:
            self.critic_optimizer.step();self.critic_updates+=1
            with torch.no_grad():
                for target_p,p in zip(self.target_critic.parameters(),self.critic.parameters()):target_p.lerp_(p,.01)
        assert all(torch.isfinite(p).all()for m in self.networks.values()for p in m.parameters())
        return dict(Pi_updates=self.Pi_updates,critic_updates=self.critic_updates,H32=False,policy_H=k,WM_H=32,batch=self.batch,optimizer_steps_applied=apply_step,
            tracking_loss=float(tracking_loss.detach()),terminal_loss=float(terminal_loss.detach()),value_loss=float(value_loss.detach()),
            actor_grad_norm=float(norm),critic_grad_norm=float(cnorm),first_actual_gradient_components=gradients,
            tracking_components=component_sums,actor_terminal_bootstrap=False,actor_direct_tracking_cost=True,actor_alive_mask_applied=False,actual_reward_remains_exp_for_diagnostics=True,terminal_value_diagnostic_mean=float(terminal_value_diagnostic.mean()),critic_target_source='actual own transition r/done/nextcritic/currentdepth, EMA.01target',actual_terminal_fraction=float(actual_done.float().mean()),actual_TD_reward_mean=float(actual_reward.mean()),actual_TD_target_mean=float(td_target.mean()),matched_orientation_angle=.75,bootstrap_value_clamp=[0,100],actor_step_constraint=step,goal59=True,actor_dim=ACTOR_DIM,critic_dim=CRITIC_DIM,
            Fudan_objective_used=False,old_command_reward_used=False,critic_same_tracking_return=True,reference_phase='episode time; monotonic; finalposeheld',
            tracker_scope='RL residual on fixed processed motor command feedforward; online actor only/no MPC solver; plannedreference conditioned',residual_RL=True,residual_radius=1.,fixed_feedforward_source='347',online_MPC=False)

    def checkpoint(self):
        return dict(residual_origin_actor_state_dict=self.residual_origin_actor.state_dict(),residual_policy_protocol=self.residual_policy.protocol,RL_residual=True,online_MPC=False,actor_state_dict=self.actor.state_dict(),critic_state_dict=self.critic.state_dict(),actor_optimizer=self.actor_optimizer.state_dict(),
            critic_optimizer=self.critic_optimizer.state_dict(),Pi_updates=self.Pi_updates,critic_updates=self.critic_updates,identity=self.identity,
            target_critic_state_dict=self.target_critic.state_dict(),critic_training='actual TD/Huber; sameexptrackingreward;EMA.01target',actor_Adam_offset=self.actor_offset,critic_Adam_offset=self.critic_offset,inherited_WM_updates=self.initial_WM_updates,actor_proposals=self.proposals,goal_dim=GOAL_DIM,policy_horizon=8,WM_supervision_horizon=32,actor_terminal_bootstrap=False,repair_source='3390cross/24full8swithspindrift;342H8position.018897m/yawtracked;H8directsameweightedcost/noexpattenuation/noactorvalue',tracking_objective='actor sumdiscountedweightedcost/5 overH8;noexp/noalivecostdeletion/noactorbootstrap;actualTDcriticusesexpdiagnosticreturn',
            old_Fudan_return=False,critic_same_tracking_return=True,phase_mode='clamped episode_step',planned_reference=True)
