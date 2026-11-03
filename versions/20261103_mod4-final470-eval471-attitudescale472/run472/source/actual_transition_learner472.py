"""Residual PPO on actual own transitions; no actor gradients through the world model."""
from copy import deepcopy
import math
import torch
from torch import nn
from teacher_student292 import model, forward, binding_for, DEPTH_SCALE
from residual_policy389 import ResidualPolicy389


def terminal_gae409(reward, value, next_value, done, gamma=.99, lam=.95):
    assert reward.shape == value.shape == next_value.shape == done.shape
    alive = (~done.bool()).to(reward.dtype)
    delta = reward + gamma * alive * next_value - value
    advantage = torch.zeros_like(reward)
    carry = torch.zeros_like(reward[-1])
    for step in reversed(range(len(reward))):
        carry = delta[step] + gamma * lam * alive[step] * carry
        advantage[step] = carry
    return advantage, advantage + value


class ActualTransitionLearner472:
    def __init__(self, wm, carrier, reference, env, binding, cpu_sha, put):
        self.wm, self.reference, self.env, self.put = wm, reference, env, put
        self.actor = model(103, True, str(wm.device))
        self.critic = model(106, False, str(wm.device))
        saved = carrier['student']
        self.actor.load_state_dict(saved['actor_state_dict'], strict=True)
        self.critic.load_state_dict(saved['critic_state_dict'], strict=True)
        self.actor.distribution.std_param.requires_grad_(False)
        self.residual_origin_actor = deepcopy(self.actor).eval()
        self.residual_origin_actor.load_state_dict(saved['residual_origin_actor_state_dict'], strict=True)
        for parameter in self.residual_origin_actor.parameters():
            parameter.requires_grad_(False)
        self.target_critic = deepcopy(self.critic).eval()
        self.target_critic.load_state_dict(saved['target_critic_state_dict'], strict=True)
        for parameter in self.target_critic.parameters():
            parameter.requires_grad_(False)
        self.actor_optimizer = torch.optim.Adam(self.actor.parameters(), lr=1e-4)
        self.critic_optimizer = torch.optim.Adam(self.critic.parameters(), lr=1e-4)
        self.actor_optimizer.load_state_dict(saved['actor_optimizer'])
        self.critic_optimizer.load_state_dict(saved['critic_optimizer'])
        for optimizer in (self.actor_optimizer, self.critic_optimizer):
            for group in optimizer.param_groups:
                group['lr'] = 1e-4
        self.optimizers = dict(actor=self.actor_optimizer, critic=self.critic_optimizer)
        self.networks = dict(actor=self.actor, critic=self.critic)
        self.actor_offset = saved['actor_Adam_offset'] + saved['Pi_updates']
        self.critic_offset = saved['critic_Adam_offset'] + saved['critic_updates']
        assert (self.actor_offset, self.critic_offset, wm.updates) == (56848, 13908, 63793)
        self.initial_WM_updates = wm.updates
        self.Pi_updates = self.critic_updates = self.PPO_updates = 0
        self.residual_policy = ResidualPolicy389(reference.path.parent / 'feedforward389.json', wm.device)
        assert self.residual_policy.protocol == saved['residual_policy_protocol']
        self.rollout = []
        self.rollout_controls = 128
        self.gae_lambda = 1.0
        self.latent_std = .15
        self.exploration_gain = .6
        self.exploration_max_std = 2.
        self.generator = torch.Generator(device=wm.device)
        self.generator.set_state(saved['residual_sampling_rng'].cpu())
        robot = env.scene['robot']
        self.legs = [robot.joint_names.index(name) for name in ('left_crank','left_hip','right_crank','right_hip')]
        self.wheels = [robot.joint_names.index(name) for name in ('left_wheel_spin','right_wheel_spin')]
        self.wheelbodies = [robot.body_names.index(name) for name in ('left_wheel','right_wheel')]
        self.identity = dict(parent=saved['identity'], targets=dict(
            actor=binding_for({'actor':self.actor},self.actor_optimizer,'ACTUAL409_RESTORED389_ACTOR_FULL_ADAM'),
            critic=binding_for({'critic':self.critic},self.critic_optimizer,'ACTUAL409_RESTORED389_CRITIC_FULL_ADAM')))
        put('ACTUAL472_FULL_RESTORE_AND_REAL_RL_PROTOCOL.json',dict(passed=True,
            actor_offset=self.actor_offset,critic_offset=self.critic_offset,WM=wm.updates,
            origin_saved_from389=True,teacher_STD_frozen=True,policy='latentGaussianResidualPPO',
            rollout_controls=self.rollout_controls,GAE_lambda=self.gae_lambda,latent_std_floor=self.latent_std,exploration_gain=self.exploration_gain,exploration_max_std=self.exploration_max_std,actual_reward_done_GAE=True,
            actor_WM_gradients=False,new_reward=True,optimizer_steps=0))

    def inputs(self, policy, critic, depth, packed, phase):
        envs = torch.arange(len(policy), device=self.wm.device)
        goal = self.reference.goals(self.wm.measured_layout.unpack(packed),phase,envs,self.env.target389)
        normalized_depth = depth / depth.new_tensor(DEPTH_SCALE)
        return torch.cat((policy,normalized_depth,goal),-1),torch.cat((critic,normalized_depth,goal),-1)

    def exploration_std(self, mean):
        # A per-channel policy distribution. Its variance is recomputed and
        # differentiated in the likelihood; no stale fixed-std PPO ratio.
        return torch.sqrt(self.latent_std**2+(self.exploration_gain*mean).square()).clamp_max(self.exploration_max_std)

    def log_prob(self, latent, mean):
        std = self.exploration_std(mean)
        return (-.5*((latent-mean)/std).square()-std.log()-.5*math.log(2*math.pi)).sum(-1)

    def policy_KL(self, old_mean, updated):
        old_std = self.exploration_std(old_mean)
        new_std = self.exploration_std(updated)
        return (torch.log(new_std/old_std)+(old_std.square()+(old_mean-updated).square())/(2*new_std.square())-.5).sum(-1).mean()

    def sample_action(self, policy, critic, depth, packed, phase):
        with torch.no_grad():
            x,cx = self.inputs(policy,critic,depth,packed,phase)
            mean = forward(self.actor,x) - forward(self.residual_origin_actor,x)
            noise = torch.randn(mean.shape,device=mean.device,dtype=mean.dtype,generator=self.generator)
            latent = mean + self.exploration_std(mean)*noise
            action = (self.residual_policy.baseline(phase)+torch.tanh(latent)).clamp(-6,6)
            return action, dict(x=x.detach().clone(),cx=cx.detach().clone(),latent=latent.detach().clone(),
                old_log_prob=self.log_prob(latent,mean).detach(),latent_std=self.exploration_std(mean).detach().clone(),old_value=forward(self.critic,cx).squeeze(-1).detach())

    def observe(self, sample, reward, done, next_critic, next_depth, next_packed, next_phase):
        with torch.no_grad():
            envs = torch.arange(len(reward),device=self.wm.device)
            goal = self.reference.goals(self.wm.measured_layout.unpack(next_packed),next_phase,envs,self.env.target389)
            cx = torch.cat((next_critic,next_depth/next_depth.new_tensor(DEPTH_SCALE),goal),-1)
            next_value = forward(self.critic,cx).squeeze(-1)
            row = dict(sample,reward=reward.detach().clone(),done=done.bool().detach().clone(),
                next_value=next_value.detach().clone())
            if len(self.rollout)==self.rollout_controls:
                self.rollout.pop(0)
            self.rollout.append(row)

    def update(self, apply_step=True):
        if len(self.rollout)<self.rollout_controls:
            return None
        batch = {key:torch.stack([row[key]for row in self.rollout])for key in self.rollout[0]}
        with torch.no_grad():
            advantage,returns = terminal_gae409(batch['reward'],batch['old_value'],batch['next_value'],batch['done'],lam=self.gae_lambda)
            advantage = (advantage-advantage.mean())/advantage.std(unbiased=False).clamp_min(1e-8)
        x = batch['x'].flatten(0,1)
        cx = batch['cx'].flatten(0,1)
        latent = batch['latent'].flatten(0,1)
        old_log_prob = batch['old_log_prob'].flatten()
        mean = forward(self.actor,x) - forward(self.residual_origin_actor,x)
        ratio = torch.exp(self.log_prob(latent,mean)-old_log_prob)
        clipped = ratio.clamp(.8,1.2)
        actor_loss = -torch.minimum(ratio*advantage.flatten(),clipped*advantage.flatten()).mean()
        prediction = forward(self.critic,cx).squeeze(-1)
        critic_loss = torch.nn.functional.smooth_l1_loss(prediction,returns.flatten())
        self.actor_optimizer.zero_grad(set_to_none=True)
        self.critic_optimizer.zero_grad(set_to_none=True)
        actor_loss.backward()
        critic_loss.backward()
        actor_grad = nn.utils.clip_grad_norm_(self.actor.parameters(),1.)
        critic_grad = nn.utils.clip_grad_norm_(self.critic.parameters(),1.)
        assert torch.isfinite(actor_grad) and torch.isfinite(critic_grad)
        trust = dict(applied=False, nominal_lr=1e-4, KL_limit=.01, max_action_delta_limit=.05)
        if apply_step:
            # With oneepoch the PPO ratio is1 before Adam. Measure the proposed
            # policy after Adam, not just the pre-update surrogate clipping.
            before_weights = [parameter.detach().clone() for parameter in self.actor.parameters()]
            before_optimizer = deepcopy(self.actor_optimizer.state_dict())
            old_mean = mean.detach().clone()
            with torch.no_grad():
                # baseline cancels in the action delta; no changed command table.
                old_residual = torch.tanh(old_mean)
            accepted = False
            for exponent in range(13):
                with torch.no_grad():
                    for parameter,before in zip(self.actor.parameters(),before_weights):parameter.copy_(before)
                self.actor_optimizer.load_state_dict(deepcopy(before_optimizer))
                factor = .5**exponent
                for group in self.actor_optimizer.param_groups:group['lr']=1e-4*factor
                self.actor_optimizer.step()
                with torch.no_grad():
                    updated = forward(self.actor,x)-forward(self.residual_origin_actor,x)
                    actual_KL = self.policy_KL(old_mean,updated)
                    action_delta = (torch.tanh(updated)-old_residual).abs().amax()
                if torch.isfinite(actual_KL) and torch.isfinite(action_delta) and actual_KL<=.01 and action_delta<=.05:
                    accepted = True
                    trust = dict(applied=True, nominal_lr=1e-4, accepted_lr=1e-4*factor, factor=factor,
                        KL_limit=.01, actual_KL=float(actual_KL), max_action_delta_limit=.05,
                        actual_max_action_delta=float(action_delta), proposals=exponent+1,
                        rejected_candidate_weights_and_Adam_fully_restored=True, one_committed_Adam_step=True)
                    break
            assert accepted, 'No finite policytruststep; preserveerrorcheckpoint withoutunboundedactorstep'
            self.critic_optimizer.step()
            with torch.no_grad():
                for target,source in zip(self.target_critic.parameters(),self.critic.parameters()):
                    target.lerp_(source,.01)
            self.Pi_updates += 1
            self.critic_updates += 1
            self.PPO_updates += 1
            self.rollout.clear()
        return dict(Pi_updates=self.Pi_updates,critic_updates=self.critic_updates,
            PPO_updates=self.PPO_updates,optimizer_steps_applied=apply_step,
            actor_grad_norm=float(actor_grad),critic_grad_norm=float(critic_grad),
            actor_loss=float(actor_loss.detach()),critic_loss=float(critic_loss.detach()),
            reward_mean=float(batch['reward'].mean()),terminal_fraction=float(batch['done'].float().mean()),
            terminal_bootstrap=0.,actual_done_in_GAE=True,actor_model_gradient=False,
            actual_onpolicy_samples=int(batch['reward'].numel()),rollout_controls=self.rollout_controls,
            latent_std_floor=self.latent_std,latent_std_mean=float(batch['latent_std'].mean()),latent_std_max=float(batch['latent_std'].max()),exploration_gain=self.exploration_gain,exploration_max_std=self.exploration_max_std,ratio_mean=float(ratio.detach().mean()),
            actor_trust_step=trust,
            source='actual own onpolicy rewards/done/latentlogprob; no WM imaginedreturns',
            online_MPC=False,RL_residual=True,STD_updates=0)

    def checkpoint(self):
        return dict(actor_state_dict=self.actor.state_dict(),critic_state_dict=self.critic.state_dict(),
            target_critic_state_dict=self.target_critic.state_dict(),actor_optimizer=self.actor_optimizer.state_dict(),
            critic_optimizer=self.critic_optimizer.state_dict(),residual_origin_actor_state_dict=self.residual_origin_actor.state_dict(),
            residual_policy_protocol=self.residual_policy.protocol,RL_residual=True,online_MPC=False,
            actor_Adam_offset=self.actor_offset,critic_Adam_offset=self.critic_offset,
            Pi_updates=self.Pi_updates,critic_updates=self.critic_updates,PPO_updates=self.PPO_updates,
            identity=self.identity,actual_RL_rollout=self.rollout,
            residual_sampling_rng=self.generator.get_state(),residual_latent_std=self.latent_std,
            exploration_protocol=dict(kind='SATURATION_AWARE_LATENT_GAUSSIAN',floor=self.latent_std,gain=self.exploration_gain,max_std=self.exploration_max_std,fullGaussianKL=True,deterministic_action_unchanged=True),
            actor_training='actual onpolicy residualPPO/full128controlreturn gamma.99lambda1clip.2/oneepoch',GAE_lambda=self.gae_lambda,
            actor_model_gradient=False,actual_reward_unchanged=False,actual_done_bootstrap=False,
            actor_trust_protocol=dict(kind='POST_ADAM_ACTUAL_KL_AND_RESIDUAL_DELTA',KL_limit=.01,max_action_delta=.05,max_backtracks=12),
            origin_frozen_from389=True,goal_dim=59,actor_horizon_actual_controls=self.rollout_controls,
            WM_supervision_horizon=32,actor_terminal_bootstrap=False)
