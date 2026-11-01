"""Own-plant SuperMimic with separate frozen LQR/MPC state supervision.

Reference states are labels, never actor observations or WM replay transitions.
Only the current observed support anchor supplies imagined depth context.
"""
from copy import deepcopy
import hashlib, inspect, io, json
import torch
from torch import nn
from tensordict import TensorDict
from rsl_rl.models import MLPModel
from zero_input_bound_adam277 import prepare_split_plan, bind_target_optimizer
from future_safe_wm_warm273 import context_from_start_anchor273
from native_depth_world_model50_v255 import normalize_context40
from predicted_literal_frame268 import predicted_literal_frame
from literal_imagination259 import RewardMemory, imagined_step, POLICY_TO_REWARD_MOTOR
from jump194_boundary import LiteralJump194

DEPTH_SCALE=(4.,.4,2.,3.141592653589793,2.,4.,1.,.2,1.)

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

def model(width, actor, device):
    obs=TensorDict({'policy':torch.zeros(1,width,device=device)},batch_size=[1])
    return MLPModel(obs,{'actor':['policy'],'critic':['policy']},'actor' if actor else 'critic',
        6 if actor else 1,hidden_dims=[128,64,32],activation='elu',obs_normalization=False,
        distribution_cfg=({'class_name':'rsl_rl.modules.distribution:GaussianDistribution',
            'init_std':1.,'std_type':'scalar'} if actor else None)).to(device)

def forward(net, obs):
    return net(TensorDict({'policy':obs},batch_size=list(obs.shape[:-1])))

def binding_for(nets, optimizer, kind, **extra):
    serialized=optimizer.state_dict();names={id(p):(scope,k,p) for scope,m in nets.items() for k,p in m.named_parameters()}
    rows=[]
    for gi,(live,saved) in enumerate(zip(optimizer.param_groups,serialized['param_groups'],strict=True)):
        for pos,(p,pid) in enumerate(zip(live['params'],saved['params'],strict=True)):
            scope,key,obj=names[id(p)]
            assert obj is p
            rows.append(dict(scope=scope,state_key=key,optimizer_id=pid,group_index=gi,
                group_position=pos,shape=list(p.shape),actual_object_identity_bound=True))
    value=dict(kind=kind,parameter_bindings=rows,**extra)
    value['identity_receipt_SHA']=digest(value)
    return value

def migrate(carrier, cpu_sha, device):
    """Restore the original RSL constructor and its actual parameter objects."""
    source=carrier['teacher_full_PPO_state']
    original={'actor':model(35,True,device),'critic':model(38,False,device)}
    for name,m in original.items():m.load_state_dict(source[name+'_state_dict'],strict=True)
    # This is the actual PPO constructor; it binds actor/critic object order.
    from owned_h1_public4_mean_overflow_ppo_v2 import PPO
    text=inspect.getsource(PPO.__init__)
    assert 'chain(self.actor.parameters(), self.critic.parameters())' in text
    alg=PPO(original['actor'],original['critic'],None,device=device,
        learning_rate=.0019461950683593758)
    assert [g['params'] for g in alg.optimizer.state_dict()['param_groups']]==[g['params'] for g in source['optimizer_state_dict']['param_groups']]
    alg.optimizer.load_state_dict(source['optimizer_state_dict'])
    witness=binding_for(original,alg.optimizer,'ACTUAL_SOURCE_ADAM_NAME_ID_OBJECT_BINDING',
        source_fullstate_CPU_receipt_SHA=cpu_sha,source_teacher_SHA=carrier['teacher_source_SHA'],
        source_iteration=2135,source_Adam_step=42940,saved_group_order_identity_verified=True,
        original_constructor_SHA=hashlib.sha256(text.encode()).hexdigest(),
        provenance='RSL PPO original constructor chain(actual actor.parameters,actual critic.parameters); loaded source group order')
    # Compare every restored slot through its live object, rather than sort IDs.
    for r in witness['parameter_bindings']:
        p=dict(original[r['scope']].named_parameters())[r['state_key']]
        for k,v in source['optimizer_state_dict']['state'][r['optimizer_id']].items():
            got=alg.optimizer.state[p][k]
            assert torch.equal(got.to(v.device),v) if torch.is_tensor(v) else got==v
    plan=prepare_split_plan(source['actor_state_dict'],source['critic_state_dict'],source['optimizer_state_dict'],witness)
    target={'actor':model(44,True,device),'critic':model(47,False,device)};opts={};targets={}
    for scope,m in target.items():
        m.load_state_dict(plan['actor44_state_dict' if scope=='actor' else 'critic47_state_dict'])
        parameters={scope+':'+k:p for k,p in m.named_parameters()}
        groups=[dict(params=[parameters[n] for n in g['names']],**g['options']) for g in plan['split_adam_plans'][scope]['groups']]
        opt=torch.optim.Adam(groups)
        w=binding_for({scope:m},opt,'ACTUAL_TARGET_ADAM_NAME_ID_OBJECT_BINDING',
            source_identity_receipt_SHA=witness['identity_receipt_SHA'],optimizer_scope=scope)
        opt.load_state_dict(bind_target_optimizer(plan,scope,opt.state_dict(),w))
        opts[scope]=opt;targets[scope]=w
    # Equivalence uses an actual current sample later; zero suffix is exact here.
    for scope,width in (('actor',35),('critic',38)):
        assert torch.equal(target[scope].state_dict()['mlp.0.weight'][:,:width],source[scope+'_state_dict']['mlp.0.weight'])
        assert int(torch.count_nonzero(target[scope].state_dict()['mlp.0.weight'][:,width:]))==0
    return target,opts,dict(source=witness,targets=targets,
        inherited_WM_updates=carrier['actual_new_WM_updates'],source_Adam17_partition=[9,8],
        initial_LR_restored=.0019461950683593758,training_LR_explicitly_selected=1e-4)

def policy_obs(state, previous_action, start_policy, start_critic, raw_context, leg_ids, wheel_ids):
    p,R,v,w,q,dq,aux=state;rt=R.transpose(-1,-2)
    ang=(rt@w.unsqueeze(-1)).squeeze(-1)*.5
    lin=(rt@v.unsqueeze(-1)).squeeze(-1)*.5
    gravity=-R[...,2,:]
    # Preserve known commands/mode, rebuild predicted sensors with original scales.
    base=torch.cat((start_policy[...,:4],ang,gravity,q[...,leg_ids],
        torch.zeros_like(q[...,wheel_ids]),dq[...,leg_ids]*.1,dq[...,wheel_ids]*.1,
        previous_action,start_policy[...,28:35]),-1)
    critic=torch.cat((start_critic[...,:4],ang,lin,gravity,q[...,leg_ids],
        torch.zeros_like(q[...,wheel_ids]),dq[...,leg_ids]*.1,dq[...,wheel_ids]*.1,
        previous_action,start_critic[...,31:38]),-1)
    depth=raw_context[...,31:]/raw_context.new_tensor(DEPTH_SCALE)
    assert base.shape[-1]==35 and critic.shape[-1]==38
    return torch.cat((base,depth),-1),torch.cat((critic,depth),-1)

def state_supervision(state, label, joint_mask):
    p,R,v,w,q,dq,aux=state
    losses=[((p-label[...,:3])/.3).square().mean(-1),
        (R-label[...,3:12].reshape_as(R)).square().mean((-1,-2)),
        ((v-label[...,12:15])/2).square().mean(-1),
        ((w-label[...,15:18])/5).square().mean(-1),
        ((q[...,joint_mask]-label[...,18:48][...,joint_mask])).square().mean(-1),
        ((dq[...,joint_mask]-label[...,48:78][...,joint_mask])/10).square().mean(-1)]
    return torch.stack(losses,-1).mean(-1)

class TeacherStudent282:
    def __init__(self, wm, carrier, reference, env, binding, cpu_sha, put):
        self.wm,self.env,self.binding,self.put=wm,env,binding,put
        self.networks,self.optimizers,identity=migrate(carrier,cpu_sha,str(wm.device))
        self.actor,self.critic=self.networks['actor'],self.networks['critic']
        for opt in self.optimizers.values():
            for g in opt.param_groups:g['lr']=1e-4
        self.reference=reference;self.Pi_updates=self.critic_updates=0
        self.initial_WM_updates=wm.updates
        self.leg_ids=[env.scene['robot'].joint_names.index(n) for n in ('left_crank','left_hip','right_crank','right_hip')]
        self.wheel_ids=[env.scene['robot'].joint_names.index(n) for n in ('left_wheel_spin','right_wheel_spin')]
        self.joint_mask=torch.tensor(self.leg_ids,device=wm.device)
        self.saved={k:torch.zeros((64,80,*tail),device=wm.device,dtype=dtype) for k,tail,dtype in (
            ('policy',(35,),torch.float32),('critic',(38,),torch.float32),('commands',(4,),torch.float32),
            ('air',(),torch.float32),('contacts',(2,),torch.bool),('actions',(6,2),torch.float32),
            ('origin',(3,),torch.float32),('ref',(),torch.int64),('phase',(),torch.int64))}
        self.identity=identity;put('ACTUAL282_THREE_OPTIMIZER_IDENTITY_MIGRATION.json',dict(passed=True,**identity))

    def add_metadata(self,slot,policy,critic,commands,memory,origins):
        p=self.wm.measured_layout.unpack(self.wm.buffer.data['s'][slot])
        ids,phase=self.reference.match(p,self.env.target282,origins)
        values=dict(policy=policy,critic=critic,commands=commands,air=memory.base_air_time,
            contacts=memory.last_contacts,actions=memory.last_actions,origin=origins,ref=ids,phase=phase)
        for k,v in values.items():self.saved[k][slot].copy_(v.detach())

    def action(self,policy,depth):
        return forward(self.actor,torch.cat((policy,depth/depth.new_tensor(DEPTH_SCALE)),-1)).clamp(-6,6)

    def update(self):
        wm=self.wm;b=wm.buffer;k=32;B=256
        # Current supported observed starts; disjoint flat environments retained as
        # original environment transitions, without labelling them stair demos.
        ages=torch.arange(b.size,device=wm.device);slots=b._row(ages)
        candidates=(wm.anchors.data['valid_anchor'][slots]&(~self.env._mixed209_flat)[None]).nonzero()
        if not len(candidates):return None
        selected=candidates[torch.randint(len(candidates),(B,),device=wm.device,generator=wm.generator)]
        rows=slots[selected[:,0]];envs=selected[:,1]
        anchor=wm.anchors.gather(rows,envs);meta={n:v[rows,envs].detach().clone() for n,v in self.saved.items()}
        state=wm.measured_layout.unpack(b.data['s'][rows,envs].detach().clone())
        previous=b.data['a_prev'][rows,envs].detach().clone();initial=state
        memory=RewardMemory(meta['air'],meta['contacts'],meta['actions'])
        reward_sum=state[0].new_zeros(B);aux_sum=reward_sum.clone();alive=torch.ones_like(reward_sum)
        value_inputs=[];rewards=[];continuations=[];survivals=[]
        for module in (wm.model,self.critic):
            for p in module.parameters():p.requires_grad_(False)
        try:
            for i in range(k):
                raw=context_from_start_anchor273(anchor,state,i,wm.native_geometry)
                obs,co=policy_obs(state,previous,meta['policy'],meta['critic'],raw,self.leg_ids,self.wheel_ids)
                action=forward(self.actor,obs).clamp(-6,6)
                following=wm.model.step(state,action,normalize_context40(raw))
                frame=predicted_literal_frame(state,following,meta['commands'],environment_origins=meta['origin'],layout=wm.measured_layout,binding=self.binding)
                motor_action=action[:,list(POLICY_TO_REWARD_MOTOR)]
                reward,memory=imagined_step(frame,motor_action,memory,literal_class=LiteralJump194,
                    body_names=self.binding.body_names,tick=i)
                # Explicit soft survival for imagined posture; no physical guard changes.
                survival=torch.sigmoid((following[1][:,2,2]-.45)*20.)
                continuations.append(alive.detach().clone());survivals.append(survival.detach());value_inputs.append(co.detach())
                rewards.append(reward.detach());reward_sum=reward_sum+(.99**i)*alive*reward
                label=self.reference.labels(meta['ref'],meta['phase']+i+1,envs,self.env.target282,meta['origin'])
                aux_sum=aux_sum+(.99**i)*alive*state_supervision(following,label,self.joint_mask)
                alive=alive*survival;state,previous=following,action
            raw=context_from_start_anchor273(anchor,state,k,wm.native_geometry)
            _,co=policy_obs(state,previous,meta['policy'],meta['critic'],raw,self.leg_ids,self.wheel_ids)
            terminal=(.99**k)*alive*forward(self.critic,co).squeeze(-1)
            coefficient=max(.05,1.-self.Pi_updates/4000.)
            reward_loss=-reward_sum.mean();terminal_loss=-terminal.mean()
            teacher_loss=aux_sum.mean()/k
            loss=reward_loss+terminal_loss+coefficient*teacher_loss
            diagnostic={}
            if self.Pi_updates==0:
                params=tuple(self.actor.parameters())
                for name,l in (('reward_only',reward_loss),('terminal_only',terminal_loss),
                               ('teacher_only',teacher_loss),('combined',loss)):
                    grads=torch.autograd.grad(l,params,retain_graph=True,allow_unused=True)
                    assert all(g is None or torch.isfinite(g).all() for g in grads)
                    diagnostic[name]=float(torch.sqrt(sum((g.square().sum() for g in grads if g is not None),torch.zeros((),device=wm.device))))
                assert diagnostic['combined']>0 and diagnostic['teacher_only']>0
            opt=self.optimizers['actor'];opt.zero_grad(set_to_none=True);loss.backward()
            norm=nn.utils.clip_grad_norm_(self.actor.parameters(),1.);assert torch.isfinite(norm)
            assert all(p.grad is None or torch.isfinite(p.grad).all() for p in self.actor.parameters())
            opt.step();self.Pi_updates+=1
        finally:
            for module in (wm.model,self.critic):
                for p in module.parameters():p.requires_grad_(True)
        # SuperMimic terminal critic target uses only unchanged Fudan rewards;
        # auxiliary imitation is deliberately absent from the value target.
        with torch.no_grad():
            target=forward(self.critic,co.detach()).squeeze(-1)
            targets=[]
            for i in reversed(range(k)):
                target=rewards[i]+.99*target*survivals[i]
                targets.append(target)
            targets=torch.stack(list(reversed(targets)))
        inputs=torch.stack(value_inputs);prediction=forward(self.critic,inputs).squeeze(-1)
        value_loss=(prediction-targets).square().mean()
        opt=self.optimizers['critic'];opt.zero_grad(set_to_none=True);value_loss.backward()
        cnorm=nn.utils.clip_grad_norm_(self.critic.parameters(),1.);assert torch.isfinite(cnorm);opt.step();self.critic_updates+=1
        assert all(torch.isfinite(p).all() for m in self.networks.values() for p in m.parameters())
        return dict(Pi_updates=self.Pi_updates,critic_updates=self.critic_updates,H32=k,batch=B,
            reward_loss=float(reward_loss.detach()),terminal_loss=float(terminal_loss.detach()),
            separate_teacher_state_loss=float(teacher_loss.detach()),teacher_coefficient=coefficient,
            value_loss=float(value_loss.detach()),actor_grad_norm=float(norm),critic_grad_norm=float(cnorm),
            first_actual_gradient_components=diagnostic,student_current_depth_only=True,
            original_Fudan_reward_unchanged=True,teacher_actions_cloned=False)

    def checkpoint(self):
        return dict(actor_state_dict=self.actor.state_dict(),critic_state_dict=self.critic.state_dict(),
            actor_optimizer=self.optimizers['actor'].state_dict(),critic_optimizer=self.optimizers['critic'].state_dict(),
            Pi_updates=self.Pi_updates,critic_updates=self.critic_updates,identity=self.identity,
            inherited_WM_updates=self.initial_WM_updates,teacher_coefficient=max(.05,1.-self.Pi_updates/4000.))
