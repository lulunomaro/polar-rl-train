"""MOD4-only repaired learner. Shared pinned vendor files are never modified."""
from copy import deepcopy
from dataclasses import asdict
import torch
from torch import nn
from torch.nn import functional as F

from .supermimic_semantics import SCHEMA, OLD_DIM, CONTEXT_DIM


def repaired_learner(Base):
    from ctx_reward_learner import frozen_parameters
    from supermimic_vendor_v2.geometry import unflatten_state

    class RepairedLearner(Base):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.context_predict_mask.copy_(self.mdp.predict_mask(self.device))
            self.extension_contract.update(schema=SCHEMA,
                predict_context_mask=self.context_predict_mask.cpu().tolist(),
                model_fit='joint_autoregressive_state_context_reward_done_H32',
                critic_target='real_replay_nstep_finite_episode_return_popart',
                sensor='physical_clean_endpoint_recorded_100Hz_midpoint_bias_uniform_delay')
            self.value_mean = torch.zeros((), device=self.device)
            self.value_std = torch.ones((), device=self.device)
            self.value_initialized = False
            self.semantic_warmup_remaining = 0
            self.calibration_updates = 0
            self.migration_receipt = None

        def real_value(self, inputs):
            return self.critic(inputs)*self.value_std+self.value_mean

        def policy_value(self, state, frames, context, goal):
            value = self.real_value(self._critic_input(state, frames, context, goal))
            # Exact finite8s loose reward bound. The critic is trained on real
            # returns below; this bounded actor readout is not its training target.
            remaining = (399-frames).clamp(min=0).float()
            bound = self.mdp.max_step_reward*(1-self.cfg.gamma**remaining)/(1-self.cfg.gamma)
            return torch.where(bound > 0, bound*torch.tanh(value/bound.clamp(min=1e-6)), 0.)

        def _window(self, B):
            return self.buffer.sample_windows(B, self.cfg.wm_window)

        def wm_update(self):
            w = self._window(self.cfg.wm_batch)
            state = unflatten_state(w['s'][:,0])
            context = w['xi'][:,0]
            previous = w['a_prev'][:,0]
            state_losses, context_losses, reward_losses, done_losses = [], [], [], []
            std = torch.maximum(self.wm.out_norm.std(), self.err_floor)
            # Update normalizers only on real targets, never on predictions.
            valid = w['mask'].bool()
            truth0, truth1 = unflatten_state(w['s'][valid]), unflatten_state(w['s1'][valid])
            features = self.aux.features(truth0, truth1, w['a'][valid], w['a_prev'][valid],
                                         w['xi'][valid], w['f'][valid])
            with torch.no_grad():
                self.aux.in_norm.update(features)
                self.aux.reward_norm.update(w['r'][valid].unsqueeze(-1))
                context_valid = valid & w['xi1_valid'] & ~w['done']
                if bool(context_valid.any()):
                    self.aux.context_norm.update((w['xi1']-w['xi'])[context_valid])
            for j in range(self.cfg.wm_window):
                action, frame = w['a'][:,j], w['f'][:,j]
                state1 = self.wm.step(state, action, context)
                reward, delta, done_logit = self.aux(self.aux.features(
                    state, state1, action, previous, context, frame))
                next_context = self.mdp.project(context, delta, state1, action, frame+1,state0=state)
                state_losses.append(((self.wm.state_error(state1, unflatten_state(w['s1'][:,j]))/std)**2).mean(-1))
                # Noisy actor sensors are generated, not fitted as deterministic
                # targets. Supervise their real clean critic counterpart and midpoint.
                cmask = self.context_predict_mask
                cerr = ((next_context-w['xi1'][:,j])/self.aux.context_norm.std()).square()*cmask
                context_losses.append(cerr.sum(-1)/cmask.sum().clamp(min=1))
                reward_losses.append(((reward-w['r'][:,j])/self.aux.reward_norm.std()[0]).square())
                done_losses.append(F.binary_cross_entropy_with_logits(done_logit,w['done'][:,j].float(),reduction='none'))
                state, context, previous = state1, next_context, action
            mask = w['mask']; den = mask.sum().clamp(min=1)
            sloss = (torch.stack(state_losses,1)*mask).sum()/den
            clmask = mask*w['xi1_valid']*(~w['done'])
            closs = (torch.stack(context_losses,1)*clmask).sum()/clmask.sum().clamp(min=1)
            rloss = (torch.stack(reward_losses,1)*mask).sum()/den
            dloss = (torch.stack(done_losses,1)*mask).sum()/den
            loss = sloss+closs+rloss+dloss
            self.opt_wm.zero_grad(set_to_none=True); self.opt_aux.zero_grad(set_to_none=True)
            loss.backward()
            norms = [nn.utils.clip_grad_norm_(m.parameters(),1.) for m in (self.wm,self.aux)]
            if not bool(torch.isfinite(loss) & torch.stack([torch.isfinite(x) for x in norms]).all()):
                raise FloatingPointError('Nonfinite joint autoregressive world/context model')
            self.opt_wm.step(); self.opt_aux.step()
            self.last_aux = dict(loss=float(loss.detach()),state_H32=float(sloss.detach()),
                context_H32=float(closs.detach()),reward_H32=float(rloss.detach()),
                done_H32=float(dloss.detach()),closed_loop=True)
            last = (torch.stack(state_losses,1)[:,-1].detach()*mask[:,-1]).sum()/mask[:,-1].sum().clamp(min=1)
            return loss.detach(),last

        @torch.no_grad()
        def _popart(self, targets):
            mean = targets.mean(); std = targets.std(unbiased=False).clamp(min=.01)
            if self.value_initialized:
                mean = .99*self.value_mean+.01*mean
                std = (.99*self.value_std.square()+.01*std.square()).sqrt()
            old_mean, old_std = self.value_mean.clone(),self.value_std.clone()
            ratio = old_std/std
            head = self.critic.net[-1]
            head.weight.mul_(ratio);head.bias.mul_(old_std).add_(old_mean-mean).div_(std)
            for p in (head.weight,head.bias):
                st=self.opt_v.state.get(p,{})
                if 'exp_avg' in st:st['exp_avg'].mul_(ratio)
                if 'exp_avg_sq' in st:st['exp_avg_sq'].mul_(ratio.square())
            self.value_mean.copy_(mean);self.value_std.copy_(std);self.value_initialized=True

        def critic_real_update(self):
            w=self._window(self.cfg.pi_batch)
            with torch.no_grad():
                state=unflatten_state(w['s']);state1=unflatten_state(w['s1'])
                goals=self._goal(w['f'],w['xi'])
                inputs=self._critic_input(state,w['f'],w['xi'],goals)
                next_frames=w['f']+1
                # xi1 is unavailable at a true terminal; its bootstrap is zero.
                nx=w['xi1'];ng=self._goal(next_frames,nx)
                next_values=self.policy_value(state1,next_frames,nx,ng)
                target=next_values[:,-1]
                targets=[]
                for j in range(self.cfg.wm_window-1,-1,-1):
                    continuation=(~w['done'][:,j]).float()
                    chain=(w['mask'][:,j+1] if j+1<self.cfg.wm_window else torch.zeros_like(target))
                    tail=chain*target+(1-chain)*next_values[:,j]
                    target=w['r'][:,j]+self.cfg.gamma*continuation*((1-self.cfg.lam)*next_values[:,j]+self.cfg.lam*tail)
                    targets.append(target)
                targets=torch.stack(targets[::-1],1)
                valid=w['mask'].bool()
                flat_input,flat_targets=inputs[valid],targets[valid]
                self.critic.norm.update(flat_input)
                self._popart(flat_targets)
                normalized=(flat_targets-self.value_mean)/self.value_std
            errors=[]
            for ids in torch.tensor_split(torch.randperm(len(normalized),device=self.device),self.cfg.critic_minibatches):
                if not len(ids):continue
                prediction=self.critic(flat_input[ids])
                loss=F.mse_loss(prediction,normalized[ids])
                self.opt_v.zero_grad(set_to_none=True);loss.backward()
                grad=nn.utils.clip_grad_norm_(self.critic.parameters(),1.)
                if not bool(torch.isfinite(loss)&torch.isfinite(grad)):raise FloatingPointError('Real-return critic nonfinite')
                self.opt_v.step();errors.append(float(loss.detach()))
            self.calibration_updates+=1
            with torch.no_grad():
                value=self.real_value(flat_input)
                self.last_value=dict(source='real_rewards_real_states_finite_nstep',
                    target_mean=float(flat_targets.mean()),value_mean=float(value.mean()),
                    MAE=float((value-flat_targets).abs().mean()),outside_loose80=int((value.abs()>80).sum()),
                    mean=float(self.value_mean),std=float(self.value_std),updates=self.calibration_updates,
                    normalized_loss=sum(errors)/len(errors))
            return loss.detach()

        def policy_update(self):
            value_loss=self.critic_real_update()
            # A new model-conditioned context must be fitted before actor reads it.
            # This warmup performs real collection and model/value learning.
            if self.calibration_updates<32:return None
            self.counts.policy_attempts+=1
            start,history=self._sample_valid_starts(self.cfg.pi_batch)
            state=unflatten_state(start['s']);context=start['xi'];frames=start['f'];previous=start['a_prev']
            obs_hist=self.mdp.obs(unflatten_state(history['s']),history['a_prev'],history['xi'],history['f'])
            goal=self._goal(frames,context)
            states=[state];actions=[];rewards=[];dones=[]
            with frozen_parameters(self.wm,self.critic,self.aux):
                for j in range(self.cfg.horizon):
                    action=self.pi(obs_hist,goal).clamp(-6,6)
                    state1=self.wm.step(state,action,context)
                    reward,delta,logit=self.aux(self.aux.features(state,state1,action,previous,context,frames))
                    next_frames=frames+1
                    next_context=self.mdp.project(context,delta,state1,action,next_frames,state0=state)
                    reward=reward.clamp(-self.mdp.max_step_reward,self.mdp.max_step_reward)
                    timeout=self.mdp.imagination_timeout(next_frames,next_context)
                    done=torch.where(timeout,torch.ones_like(logit),logit.sigmoid())
                    obs=self.mdp.obs(state1,action,next_context,next_frames)
                    obs_hist=torch.cat((obs_hist[:,1:],obs[:,None]),1)
                    goal=self._goal(next_frames,next_context)
                    states.append(state1);actions.append(action);rewards.append(reward);dones.append(done)
                    state,context,frames,previous=state1,next_context,next_frames,action
                rewards,dones=torch.stack(rewards),torch.stack(dones)
                alive=torch.cumprod(1-dones,0)
                continuation=torch.cat((torch.ones_like(alive[:1]),alive[:-1]),0)
                discount=self.cfg.gamma**torch.arange(self.cfg.horizon,device=self.device)[:,None]
                contributions=discount*continuation*rewards
                bootstrap=self.cfg.gamma**self.cfg.horizon*alive[-1]*self.policy_value(state,frames,context,goal)
                loss=-(contributions.sum(0)+bootstrap).mean()
                delayed=contributions[1:].sum(0)+bootstrap
                delayed_grad=torch.autograd.grad(delayed.mean(),actions[0],retain_graph=True,allow_unused=True)[0]
                cot=torch.autograd.grad(delayed.mean(),states[1],retain_graph=True,allow_unused=True)
                cot=tuple(torch.zeros_like(x) if g is None else g.detach() for x,g in zip(states[1],cot))
                wm_grad=torch.autograd.grad(states[1],actions[0],grad_outputs=cot,retain_graph=True,allow_unused=True)[0]
                self.opt_pi.zero_grad(set_to_none=True);loss.backward()
                parameters=[p for g in self.opt_pi.param_groups for p in g['params'] if p.requires_grad]
                norm=nn.utils.clip_grad_norm_(parameters,1.);nn.utils.clip_grad_value_(parameters,.1)
                finite=bool(torch.isfinite(loss)&torch.isfinite(norm))
                probe=next((p for p in parameters if p.grad is not None and bool(p.grad.abs().max()>0)),None)
                if finite and probe is not None and float(norm)>0:
                    self._pending_bptt=dict(probe=probe,before=probe.detach().clone(),
                        cross_time_finite=delayed_grad is not None and bool(torch.isfinite(delayed_grad).all()),
                        cross_time_grad_norm=0. if delayed_grad is None else float(delayed_grad.norm()),
                        wm_path_finite=wm_grad is not None and bool(torch.isfinite(wm_grad).all()),
                        wm_path_grad_norm=0. if wm_grad is None else float(wm_grad.norm()),
                        parameter_grad_norm=float(norm),loss=float(loss.detach()),wm_weights_frozen=True,
                        auxiliary_weights_frozen=True,imagined_reward_source='original_real_Fudan_supervised_H32')
                    try:self.opt_pi.step()
                    finally:self._pending_bptt=None
                elif finite:self.counts.pi_skipped_zero+=1
                else:raise FloatingPointError('Repaired actor gradient nonfinite')
            self.last_imagination=dict(reward_sum=float(contributions.sum(0).mean().detach()),
                bootstrap=float(bootstrap.mean().detach()),objective=float(-loss.detach()),
                real_value_calibration=self.last_value)
            return loss.detach(),value_loss

        def _checkpoint(self, include_optimizers):
            p=super()._checkpoint(include_optimizers)
            p['semantic_repair']=dict(schema=SCHEMA,value_mean=self.value_mean.detach().cpu(),
                value_std=self.value_std.detach().cpu(),value_initialized=self.value_initialized,
                semantic_warmup_remaining=self.semantic_warmup_remaining,
                calibration_updates=self.calibration_updates,migration=self.migration_receipt,
                policy_mode=self.pi.base_clip_before_residual,
                last_value=getattr(self,'last_value',None),last_imagination=getattr(self,'last_imagination',None))
            return p

        def restore_semantics(self,payload):
            r=payload['semantic_repair']
            if r['schema']!=SCHEMA:raise ValueError('Unknown repaired context schema')
            self.value_mean.copy_(r['value_mean']);self.value_std.copy_(r['value_std'])
            self.value_initialized=r['value_initialized'];self.calibration_updates=r['calibration_updates']
            self.semantic_warmup_remaining=r['semantic_warmup_remaining'];self.migration_receipt=r['migration']
            self.pi.base_clip_before_residual=r['policy_mode']

    return RepairedLearner


def expand_tensor(source, target, axis, insertion):
    if source.shape==target.shape:return source
    out=source.new_zeros(target.shape)
    before=[slice(None)]*source.ndim;before[axis]=slice(0,insertion)
    out[tuple(before)]=source[tuple(before)]
    after=[slice(None)]*source.ndim;after[axis]=slice(insertion,None)
    dest=list(after);dest[axis]=slice(insertion+target.shape[axis]-source.shape[axis],None)
    out[tuple(dest)]=source[tuple(after)]
    return out


def migrate_v1(payload, learner):
    """Named schema migration. No strict=False; unchanged tensors/moments retained."""
    ext=payload['context_reward_extension']
    if ext['contract']['context_dim']!=OLD_DIM or ext['contract']['schema']!='mod4v1.ctx_task_reward.v1':
        raise ValueError('Only the reviewed139-channel v1 checkpoint may migrate')
    if not ext['update_boundary_safe'] or ext['pending_iteration'] is not None:
        raise ValueError('Migration requires a completed original update boundary')
    out=dict(payload);ex=dict(ext);out['context_reward_extension']=ex
    # Context insertion positions in each exact architecture.
    insert={'wm':(218,),'aux':(297,),'critic':(212,)}
    for name,optname in (('wm','wm'),('aux','aux'),('critic','v')):
        old=ext['aux'] if name=='aux' else payload[name]
        module=getattr(learner,name)
        current=module.state_dict();mapped={};changes={}
        point=insert[name][0]
        aux_output=str(len(module.net)-1) if name=='aux' else None
        for key,target in current.items():
            value=old[key]
            if value.shape!=target.shape:
                if key in ('net.0.weight','in_norm.mean','in_norm.var','norm.mean','norm.var'):
                    axis=1 if key.endswith('weight') else 0;at=point
                elif name=='aux' and (key.startswith('context_norm.') or key in (f'net.{aux_output}.weight',f'net.{aux_output}.bias')):
                    axis=0;at=OLD_DIM if key.startswith('context_norm.') else 1+OLD_DIM
                else:raise ValueError('Unspecified migration tensor '+name+'.'+key)
                mapped[key]=expand_tensor(value,target,axis,at)
                if key.endswith('.var'):
                    indices=[slice(None)]*value.ndim;indices[axis]=slice(at,at+CONTEXT_DIM-OLD_DIM)
                    mapped[key][tuple(indices)]=1
                changes[key]=(axis,at)
            else:mapped[key]=value
        if name=='aux':ex['aux']=mapped
        else:out[name]=mapped
        original=ext['opt_aux'] if name=='aux' else payload['opt_'+optname]
        optimizer=deepcopy(original)
        ids=[i for g in optimizer['param_groups'] for i in g['params']]
        for (key,param),ident in zip(module.named_parameters(),ids):
            if key in changes:
                axis,at=changes[key]
                for field in ('exp_avg','exp_avg_sq','max_exp_avg_sq'):
                    if field in optimizer['state'].get(ident,{}):
                        optimizer['state'][ident][field]=expand_tensor(optimizer['state'][ident][field],param,axis,at)
        if name=='aux':ex['opt_aux']=optimizer
        else:out['opt_'+optname]=optimizer
    replay=dict(ext['replay']);data=dict(replay['data']);replay['data']=data
    for key in ('xi','xi1'):
        target=data[key].new_zeros((*data[key].shape[:-1],CONTEXT_DIM));target[...,:OLD_DIM]=data[key];data[key]=target
    ex['replay']=replay;ex['contract']=learner.extension_contract
    ex['context_predict_mask']=learner.context_predict_mask.detach().cpu()
    args=dict(payload['args']);args['wm_window']=32;out['args']=args
    # The measured old value is invalid in real reward units. Convert only its
    # output head and corresponding moments, preserving all lower weights/steps.
    last=str(len(learner.critic.net)-1)
    factor=.001
    for key in (f'net.{last}.weight',f'net.{last}.bias'):out['critic'][key]=out['critic'][key]*factor
    optimizer=out['opt_v'];ids=[i for g in optimizer['param_groups'] for i in g['params']]
    for (name,_),ident in zip(learner.critic.named_parameters(),ids):
        if name in (f'net.{last}.weight',f'net.{last}.bias'):
            st=optimizer['state'].get(ident,{})
            if 'exp_avg' in st:st['exp_avg'].mul_(factor)
            if 'exp_avg_sq' in st:st['exp_avg_sq'].mul_(factor**2)
    learner.migration_receipt=dict(from_schema=ext['contract']['schema'],to_schema=SCHEMA,
        source_iteration=payload['iteration'],old_replay_preserved_at_source=True,
        fresh_context_controls_required=learner.buffer.T,
        added_columns_zero_initialized_not_claimed_as_measurements=True,
        model_weights_and_four_Adam_steps_preserved=True,critic_output_recovery_factor=factor,
        critic_targets_changed_to_real_replay=True)
    learner.semantic_warmup_remaining=learner.buffer.T
    return out
