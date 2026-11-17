"""PPO for the independently trainable stair expert; no normal or keep losses."""
import torch

def route2_update(self):
    assert not self.actor.is_recurrent and not self.critic.is_recurrent
    assert self.rnd is None and self.symmetry is None and not self.is_multi_gpu
    totals = dict(value=0., surrogate=0., entropy=0., kl=0., v1_anchor=0., success_replay=0.)
    updates = 0
    progress=min(1.,max(0.,(self.completed_PPO_updates-20)/60.))
    high_anchor=2.*(1.-progress)+.5*progress
    low_anchor=.75*(1.-progress)+.15*progress
    generator = self.storage.mini_batch_generator(self.num_mini_batches, self.num_learning_epochs)
    for batch in generator:
        self.check_budget()
        selected = batch.observations['policy'][:,29] > .5
        if not bool(selected.any()):
            continue
        obs = batch.observations[selected]
        self.actor(obs, stochastic_output=True)
        logp = self.actor.get_output_log_prob(batch.actions[selected])
        values = self.critic(obs)
        params = self.actor.output_distribution_params
        entropy = self.actor.output_entropy
        with torch.no_grad():
            old = tuple(p[selected] for p in batch.old_distribution_params)
            kl = float(self.actor.get_kl_divergence(old, params).mean())
            if self.desired_kl is not None and self.schedule == 'adaptive':
                if kl > self.desired_kl*2.:
                    self.learning_rate /= 1.5
                elif 0. < kl < self.desired_kl/2.:
                    self.learning_rate *= 1.5
            self.learning_rate = min(1e-4 if self.completed_PPO_updates<20 else 2e-4, max(1e-4, self.learning_rate))
            for group in self.optimizer.param_groups:
                group['lr'] = self.learning_rate
        advantages = batch.advantages[selected].squeeze(-1)
        advantages = (advantages-advantages.mean())/(advantages.std()+1e-8)
        ratio = (logp-batch.old_actions_log_prob[selected].squeeze(-1)).exp()
        surrogate = torch.maximum(-advantages*ratio, -advantages*ratio.clamp(1.-self.clip_param,1.+self.clip_param)).mean()
        old_values, returns = batch.values[selected], batch.returns[selected]
        if self.use_clipped_value_loss:
            clipped = old_values+(values-old_values).clamp(-self.clip_param,self.clip_param)
            value_loss = torch.maximum((values-returns).square(),(clipped-returns).square()).mean()
        else:
            value_loss = (values-returns).square().mean()
        with torch.no_grad():
            reference_mean=self.initial_v1_e1(obs['policy'],obs['obs_history'])
        current_mean=self.actor.mlp.e1(obs['policy'],obs['obs_history'])
        coefficient=torch.where(obs['policy'][:,3]>1.7,high_anchor,low_anchor)
        settle=obs.get('settle_anchor',obs['policy'][:,0:1].abs()<.05).squeeze(-1)>.5
        settle=settle|(obs['policy'][:,0].abs()<.05)
        coefficient=torch.where(settle,torch.full_like(coefficient,8.),coefficient)
        anchor_per_sample=((current_mean-reference_mean)/self.v1_anchor_action_scale).square().mean(-1)
        anchor=(coefficient*anchor_per_sample).mean()
        replay_loss=current_mean.new_zeros(())
        replay=self.success_replay.sample(128,current_mean.device)
        if replay is not None:
            replay_mean=self.actor.mlp.e1(replay['policy'],replay['obs_history'])
            replay_loss=((replay_mean-replay['actions'])/self.v1_anchor_action_scale).square().mean()
        loss = surrogate+self.value_loss_coef*value_loss-self.entropy_coef*entropy.mean()+anchor+.5*replay_loss
        if not bool(torch.isfinite(loss)):
            raise ValueError('Nonfinite E1 PPO loss')
        self.optimizer.zero_grad(set_to_none=True)
        loss.backward()
        trainable = [p for group in self.optimizer.param_groups for p in group['params']]
        if not all(p.grad is not None and bool(torch.isfinite(p.grad).all()) for p in trainable):
            raise ValueError('Missing or nonfinite E1/critic gradient')
        assert all(p.grad is None for m in [self.actor.mlp.e0,self.critic.mlp.e0] for p in m.parameters())
        assert self.actor.distribution.e0_std.grad is None
        torch.nn.utils.clip_grad_norm_(self.actor.mlp.e1.parameters(),self.max_grad_norm)
        torch.nn.utils.clip_grad_norm_([self.actor.distribution.e1_log_std],self.max_grad_norm)
        torch.nn.utils.clip_grad_norm_(self.critic.mlp.e1.parameters(),self.max_grad_norm)
        self.check_budget()
        self.optimizer.step()
        updates += 1
        totals['value'] += float(value_loss.detach());totals['surrogate'] += float(surrogate.detach())
        totals['v1_anchor'] += float(anchor.detach())
        totals['success_replay'] += float(replay_loss.detach())
        totals['entropy'] += float(entropy.detach().mean());totals['kl'] += kl
    self.completed_PPO_updates+=1
    self.storage.clear()
    return {**{k:v/max(updates,1) for k,v in totals.items()},'minibatches':updates,'learning_rate':self.learning_rate,'anchor_high_coefficient':high_anchor,'anchor_low_coefficient':low_anchor,'completed_PPO_updates':self.completed_PPO_updates,'permanent_settle_anchor_coefficient':8.,'replay_frames':self.success_replay.frames}
