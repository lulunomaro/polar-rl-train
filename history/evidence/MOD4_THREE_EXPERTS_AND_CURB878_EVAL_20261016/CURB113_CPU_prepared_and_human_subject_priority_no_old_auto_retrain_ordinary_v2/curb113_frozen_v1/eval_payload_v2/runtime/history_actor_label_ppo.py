"""Approved S1A A1 auxiliary-detached / A2 joint-PPO candidates; no privileged actor path."""
from copy import deepcopy
import torch
from torch import nn
from rsl_rl.models import MLPModel
from rsl_rl.algorithms import PPO
from history_latent_component import VelocityEncoder,actor_input,supervised_velocity_loss

def masked_velocity_loss(history,encoder,label,valid):
    if valid.shape!=(history.shape[0],1) or not bool(((valid==0)|(valid==1)).all()):
        raise ValueError('Explicit per-sample reset validity required')
    selected=valid[:,0].bool()
    if not bool(selected.any()):return None
    return supervised_velocity_loss(history[selected],encoder,label[selected])

class HistoryActor(MLPModel):
    def __init__(self,*args,variant='A1',encoder_seed=20261007,**kwargs):
        if variant not in ('A1','A2'):raise ValueError('Explicit approved architecture variant required')
        self.variant=variant
        super().__init__(*args,**kwargs)
        self.encoder=VelocityEncoder(seed=encoder_seed)
        if self.obs_normalization:raise ValueError('Baseline observation scaling retained; no new normalizer')

    def _get_obs_dim(self,obs,groups,obs_set):
        if obs_set!='actor' or groups['actor']!=['policy','feedback_history']:
            raise ValueError('Actor only consumes deployable current35 and history175')
        if obs['policy'].shape[-1]!=35 or obs['feedback_history'].shape[-1]!=175:
            raise ValueError('Actual35/175 feedback required')
        return list(groups['actor']),35

    def _get_latent_dim(self):return 38

    def get_latent(self,obs,masks=None,hidden_state=None):
        return actor_input(obs['policy'],obs['feedback_history'],self.encoder,self.variant)

    def as_jit(self):return HistoryExport(self)

    def as_onnx(self,verbose=False):
        raise NotImplementedError('History-aware ONNX export must be independently verified; prevent parent current-only export')

class HistoryExport(nn.Module):
    def __init__(self,actor):
        super().__init__();self.encoder=deepcopy(actor.encoder.net);self.mlp=deepcopy(actor.mlp)
    def forward(self,policy35:torch.Tensor,feedback_history175:torch.Tensor):
        return self.mlp(torch.cat((policy35,self.encoder(feedback_history175)),dim=-1))

class HistoryPPO(PPO):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        if not isinstance(self.actor,HistoryActor):raise TypeError('History-aware actor required')
        self.aux_optimizer=None
        self.aux_updates=0
        self.actual_updates=0
        if self.actor.variant=='A1':
            params=[p for name,p in self.actor.named_parameters() if not name.startswith('encoder.')]+list(self.critic.parameters())
            self.optimizer=type(self.optimizer)(params,**self.optimizer.defaults)
            self.aux_optimizer=torch.optim.Adam(self.actor.encoder.parameters(),lr=1e-4)

    def update(self):
        count=int(self.storage.step)
        if count!=self.storage.num_transitions_per_env:raise ValueError('Complete rollout required')
        # A1 PPO sees a detached latent; encoder has its own velocity-supervision optimizer.
        losses=super().update()
        self.actual_updates+=1
        if self.actor.variant=='A1':
            flat=self.storage.observations.flatten(0,1)
            if flat['body_velocity_label'].shape[-1]!=3:raise ValueError('Actual COM Body velocity label missing')
            total=flat.batch_size[0];mean=0.
            # One auxiliary epoch per actual PPO update; accounted in the same learning segment.
            for lo in range(0,total,max(1,(total+3)//4)):
                batch=flat[lo:lo+max(1,(total+3)//4)]
                loss=masked_velocity_loss(batch['feedback_history'],self.actor.encoder,batch['body_velocity_label'],batch['body_velocity_valid'])
                if loss is None:continue
                self.aux_optimizer.zero_grad(set_to_none=True);loss.backward()
                nn.utils.clip_grad_norm_(self.actor.encoder.parameters(),1.)
                self.aux_optimizer.step();self.aux_updates+=1;mean+=float(loss.detach())*batch.batch_size[0]/total
            losses['aux_velocity_mse']=mean
        return losses

    def save(self):
        state=super().save()
        state['history_architecture']=dict(schema=1,variant=self.actor.variant,actor_feedback=[35,175],actor_head_input=38,
          encoder=[175,128,64,3],teacher_point='root COM',teacher_frame='root link/body',teacher_units='m/s',
          actual_updates=self.actual_updates,aux_updates=self.aux_updates,teacher_is_actor_input=False,
          original_optimizer_restored=False,A2_auxiliary_supervision=False,reset_teacher_mask_required=True)
        state['aux_optimizer_state_dict']=self.aux_optimizer.state_dict() if self.aux_optimizer else None
        state['adaptive_learning_rate']=float(self.learning_rate)
        return state

    def load(self,state,load_cfg=None,strict=True):
        meta=state['history_architecture']
        if meta['variant']!=self.actor.variant or meta['teacher_is_actor_input']:
            raise ValueError('Checkpoint architecture or privileged input contract mismatch')
        result=super().load(state,load_cfg,strict)
        if self.aux_optimizer:
            if state['aux_optimizer_state_dict'] is None:raise ValueError('Missing auxiliary optimizer')
            self.aux_optimizer.load_state_dict(state['aux_optimizer_state_dict'])
        elif state['aux_optimizer_state_dict'] is not None:raise ValueError('A2 cannot restore auxiliary learning')
        self.actual_updates=int(meta['actual_updates']);self.aux_updates=int(meta['aux_updates'])
        self.learning_rate=float(state['adaptive_learning_rate'])
        return result
