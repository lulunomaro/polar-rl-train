"""SuperMimic learned-model BPTT adapter for the actual Newton Fudan task.

Simulator stepping remains Newton. The referenced learner differentiates its
learned state/reward/context models, with the real Fudan reward as labels.
This module is used only by a future saved-boundary worker, never injected
into the active PPO process.
"""
from pathlib import Path
from types import SimpleNamespace
import hashlib,json,sys
import torch


def load_sources(binding):
    binding=json.loads(Path(binding).read_bytes())
    root=Path(binding['root'])
    for row in binding['files']:
        p=root/row['relative'];raw=p.read_bytes()
        if len(raw)!=row['bytes']or hashlib.sha256(raw).hexdigest()!=row['SHA']:
            raise ValueError('Referenced SuperMimic source changed: '+str(p))
    if str(root)not in sys.path:sys.path.insert(0,str(root))
    from ctx_reward_learner import ContextRewardLearner
    from supermimic_vendor_v2.learner import SuperMimicConfig
    return ContextRewardLearner,SuperMimicConfig


class FudanJumpMdp:
    num_joints=30
    action_dim=6
    obs_dim=35
    goal_frame_dim=3
    max_step_reward=.8 #16 independently clipped weighted rates *2.5 *.02

    def __init__(self,context_dim):self.context_dim=context_dim
    def to(self,device):return self
    def normalize_context(self,x):return x
    def add_noise(self,x):return x #Native100Hz D2/D3 already present in context
    def obs(self,state,previous_action,context,frames):return context[...,:35]
    def goal_with_context(self,frames,count,context):
        return context[...,:3].repeat(*([1]*(context.ndim-1)),count)
    def goal(self,*args):raise RuntimeError('Current command context required')
    def reward(self,*args):raise RuntimeError('Use real16-term Fudan reward labels')
    def soft_termination(self,*args):raise RuntimeError('Use actual task term/trunc labels')
    def critic_features(self,state,frames,context):
        from supermimic_vendor_v2.geometry import invariant_features
        return torch.cat((invariant_features(state),context,frames[...,None].float()/400),-1)
    def valid_imagination_start(self,frames,horizon):return frames<399-horizon
    def valid_imagination_start_with_context(self,frames,horizon,context):
        return self.valid_imagination_start(frames,horizon)
    def imagination_timeout(self,frames,context):return frames>=399
    def project_predicted_context(self,context,state1,action,frames):
        value=context.clone()
        value[...,:3]=context[...,:3] #Command is held over a short imagined rollout
        value[...,14:16]=0. #Original actor wheel-position placeholders
        value[...,22:28]=action.clamp(-6,6) #Original clipped action-history slots
        return value


class FudanPPOResidualPolicy(torch.nn.Module):
    """Start from the exact saved PPO mean action, with zero new residual."""
    def __init__(self,residual,teacher):
        super().__init__()
        self.residual,self.teacher=residual,teacher
        teacher.eval().requires_grad_(False)
        torch.nn.init.zeros_(residual.dec[-1].weight)
        torch.nn.init.zeros_(residual.dec[-1].bias)

    @property
    def obs_norm(self):return self.residual.obs_norm
    @property
    def goal_norm(self):return self.residual.goal_norm

    def forward(self,history,goal):
        from tensordict import TensorDict
        current=history[...,-1,:35]
        observation=TensorDict(dict(policy=current),batch_size=list(current.shape[:-1]))
        base=self.teacher(observation,stochastic_output=False)
        return (base+self.residual(history,goal).tanh()).clamp(-6,6)


def warmstarted_learner(base_learner,teacher):
    """Keep the entire PPO checkpoint as source; BPTT has its own optimizers."""
    class FudanNewtonLearner(base_learner):
        def _make_policy(self):
            return FudanPPOResidualPolicy(super()._make_policy(),teacher)
    return FudanNewtonLearner


class NewtonSuperMimicBridge:
    """Real terminal physical state is captured before the task resets it."""
    def __init__(self,env):
        from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY
        self.real=env;self.device=env.device;self.num_envs=env.num_envs
        self.controls=0;self.last_action=torch.zeros(env.num_envs,6,device=env.device)
        self._old_observer=env.physics_observer;self.pre=None
        obs=env.get_observations();context=self.context(obs)
        self.supermimic_mdp=FudanJumpMdp(context.shape[-1])
        self.state=SimpleNamespace(info={SUPERMIMIC_STATE_KEY:self.info(context)})
        env.physics_observer=self.observe

    def pack(self):
        from .math_ops import quat_apply
        d=self.real.data
        omega=quat_apply(d.root_quat_w,d.root_ang_vel_b)
        return torch.cat((d.root_pos_w,d.root_quat_w,d.root_lin_vel_w,omega,
                          d.joint_pos,d.joint_vel),-1).detach().clone()

    def context(self,obs):
        e=self.real;r=e.reward
        values=[obs['policy'],obs['critic']]
        for name in ('fudan_last_contacts','fudan_contact_filt','fudan_was_in_flight',
                     'fudan_base_air_time','fudan_leg_length','fudan_leg_theta'):
            values.append(getattr(r,name).reshape(e.num_envs,-1).float())
        for key in ('legs','wheels'):
            g=e._physics_action_delay.groups[key]
            for name in ('lag_steps','applied','pending','pending_valid'):
                values.append(g[name].reshape(e.num_envs,-1).float())
        return torch.cat(values,-1).detach().clone()

    def info(self,context):
        frame=self.real.episode_length_buf.clone()
        return dict(s=self.pack(),xi=context,a_prev=self.last_action.clone(),f=frame,ep_step=frame)

    def observe(self,e):
        if self._old_observer is not None:self._old_observer(e)
        if e.physics_ticks%8==0:self.pre=self.pack()

    @torch.no_grad()
    def step(self,action):
        from supermimic_vendor_v2.contract import SUPERMIMIC_STATE_KEY,SUPERMIMIC_TRANSITION_KEY
        old=self.state.info[SUPERMIMIC_STATE_KEY]
        action=action.detach().clamp(-6,6);self.pre=None
        obs,reward,done,extras=self.real.step(action);self.controls+=1
        if self.pre is None:raise RuntimeError('Real pre-reset physical endpoint missing')
        snap=self.real.terminal_snapshot;term=snap['terminated'];trunc=snap['time_out']
        assert torch.equal(done,term|trunc)
        if bool(snap['numerical_reset'].any()):
            raise FloatingPointError('BPTT real replay excludes numerical-reset transitions; inspect native batch before switching')
        context=self.context(obs);next_valid=context.clone();next_valid[done]=0
        transition=dict(s=old['s'],s1=self.pre,a=action.clone(),a_prev=old['a_prev'],
            xi=old['xi'],xi1=next_valid,xi1_valid=~done,r=reward.detach().clone(),
            f=old['f'],ep_step=old['ep_step'],done=done.clone(),term=term.clone(),trunc=trunc.clone())
        self.last_action=action.clone();self.last_action[done]=0
        self.state=SimpleNamespace(info={SUPERMIMIC_STATE_KEY:self.info(context),SUPERMIMIC_TRANSITION_KEY:transition},
            reward=reward.detach(),terminated=term,truncated=trunc,obs=obs)
        return self.state

    def export_supermimic_resume(self):
        from .newton_checkpoint import COMPONENTS
        e=self.real
        return dict(exact=False,backend='Newton/SolverMuJoCo/MuJoCo-Warp',
            resume_scope='Complete learner/replay/RNG plus restored DR streams then a fresh physical episode',
            physical_state=self.pack().cpu(),physics_ticks=e.physics_ticks,controls=self.controls,
            components={k:getattr(e,k).state_dict()for k in COMPONENTS},
            physical_rng=dict(generator=e.rng.get_state(),cpu_generator=e.cpu_generator.get_state()))

    def close(self):self.real.physics_observer=self._old_observer
