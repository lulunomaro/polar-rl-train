"""Explicit S1A wrapper. Underlying policy35/critic38 and plant remain unchanged."""
import torch
from history_latent_component import FeedbackHistory

def tensor(value):
    return value if isinstance(value,torch.Tensor) else value.torch

class HistoryObservationAdapter:
    def __init__(self,vec):
        self.vec=vec
        self.env=vec.unwrapped
        self.history=FeedbackHistory(vec.num_envs,device=vec.device)
        self.cached=None
        self.cached_tick=None
        self.dirty=True
        self.selected_resets=[]
        original=self.env._reset_idx
        def reset(ids):
            result=original(ids)
            self.history.reset_rows(ids)
            self.dirty=True
            self.selected_resets.append((int(self.env.common_step_counter),tensor(ids).detach().clone()))
            return result
        self.env._reset_idx=reset

    def __getattr__(self,name):
        return getattr(self.vec,name)

    def augment(self,clean):
        assert clean['policy'].shape==(self.num_envs,35)
        assert clean['critic'].shape==(self.num_envs,38)
        tick=int(self.env.common_step_counter)
        result=clean.clone(False)
        result['feedback_history']=self.history.observe(clean['policy'],tick)
        # Privileged training-only label: root COM linear velocity expressed in root-link frame.
        # Actor consumes current feedback and feedback_history, never this key.
        result['body_velocity_label']=tensor(self.env.scene['robot'].data.root_com_lin_vel_b).detach().clone()
        self.cached=result
        self.cached_tick=tick
        self.dirty=False
        return result

    def get_observations(self):
        if self.cached is not None and not self.dirty and self.cached_tick==int(self.env.common_step_counter):
            return self.cached.clone(False)
        return self.augment(self.vec.get_observations())

    def reset(self):
        obs,extra=self.vec.reset()
        return self.augment(obs),extra

    def step(self,action):
        obs,reward,done,extra=self.vec.step(action)
        return self.augment(obs),reward,done,extra

    def history_state_dict(self):
        return dict(frames=self.history.frames.clone(),pending=self.history.pending.clone(),
                    last_tick=self.history.last_tick,advances=self.history.advances)

    def load_history_state_dict(self,state):
        if state['frames'].shape!=self.history.frames.shape or state['pending'].shape!=self.history.pending.shape:
            raise ValueError('History state belongs to a different environment count')
        if not torch.isfinite(state['frames']).all():raise ValueError('Nonfinite saved history')
        self.history.frames.copy_(state['frames'])
        self.history.pending.copy_(state['pending'])
        self.history.last_tick=state['last_tick']
        self.history.advances=int(state['advances'])
        self.cached=None;self.dirty=True
