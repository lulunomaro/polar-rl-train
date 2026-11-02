"""No-learning inference adapter for matched A0/A1/A2 manual evaluation commands."""
from pathlib import Path
import sys,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import torch
from tensordict import TensorDict
from rsl_rl.models import MLPModel
from history_actor_label_ppo import HistoryActor
from history_latent_component import FeedbackHistory

def load_frozen_actor(path,num_envs,device):
    ck=torch.load(path,map_location='cpu',weights_only=False)
    variant=ck.get('history_architecture',{}).get('variant','A0')
    assert variant in ('A0','A1','A2')
    state=ck['actor_state_dict'];assert 'distribution.std_param' in state
    if variant!='A0':
        meta=ck['history_architecture']
        assert meta['actual_updates']==275 and not meta['teacher_is_actor_input'] and meta['reset_teacher_mask_required']
        assert state['encoder.net.0.weight'].shape==(128,175)
    obs=TensorDict(dict(policy=torch.zeros(num_envs,35),critic=torch.zeros(num_envs,38),feedback_history=torch.zeros(num_envs,175)),batch_size=[num_envs])
    # Actor construction must not change the RNG used by the matched physical reset.
    with torch.random.fork_rng(devices=[]):
        cfg=dict(class_name='rsl_rl.modules.distribution:GaussianDistribution',init_std=1.,std_type='scalar')
        if variant=='A0':actor=MLPModel(obs,dict(actor=['policy'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=cfg)
        else:actor=HistoryActor(obs,dict(actor=['policy','feedback_history'],critic=['critic']),'actor',6,[256,128,64],'elu',distribution_cfg=cfg,variant=variant)
        actor.load_state_dict(state,strict=True)
    actor.to(device).eval();actor.requires_grad_(False)
    for p in actor.state_dict().values():assert torch.isfinite(p).all()
    return actor,variant,hashlib.sha256(Path(path).read_bytes()).hexdigest()

class DecisionHistoryVec:
    """Sample after final manual command write, once per actual policy decision tick.

    step returns original feedback without pre-sampling the next manual command.
    This keeps current commands and the historical decision feedback consistent.
    """
    def __init__(self,vec,variant):
        self.vec=vec;self.env=vec.unwrapped;self.variant=variant
        self.history=FeedbackHistory(vec.num_envs,device=vec.device)
        self.cached_policy=None;self.cached_tick=None;self.reset_count=0;self.command_error=0.
        original=self.env._reset_idx
        def reset(ids):
            result=original(ids);self.history.reset_rows(ids);self.reset_count+=int(len(ids));return result
        self.env._reset_idx=reset
    def __getattr__(self,name):return getattr(self.vec,name)
    def get_observations(self):
        clean=self.vec.get_observations();tick=int(self.env.common_step_counter)
        assert clean['policy'].shape==(self.num_envs,35) and clean['critic'].shape==(self.num_envs,38)
        requested=self.env.command_manager.get_term('twist').command
        self.command_error=max(self.command_error,float((clean['policy'][:,:3]-requested).abs().max()))
        assert self.command_error<=1e-6,'Actor feedback does not contain actual current command'
        if self.cached_tick==tick and not bool(self.history.pending.any()):
            assert torch.equal(clean['policy'],self.cached_policy),'Feedback changed inside one decision tick'
        history=self.history.observe(clean['policy'],tick)
        self.cached_tick=tick;self.cached_policy=clean['policy'].clone()
        # Deployable inputs only; no privileged critic or teacher is passed to actor.
        result=TensorDict(dict(policy=clean['policy']),batch_size=[self.num_envs])
        if self.variant!='A0':result['feedback_history']=history
        return result
    def step(self,action):return self.vec.step(action)
    def audit(self):
        return dict(variant=self.variant,current_actor_dimension=35,history_frames=5,history_span_ms=40,
          history_advances=self.history.advances,decision_tick=self.history.last_tick,
          explicit_reset_row_count=self.reset_count,actual_command_error=self.command_error,
          actor_receives_teacher=False,actor_receives_critic=False,optimizer_updates=0,
          reset_history_filled_from_current_feedback=True,
          manual_command_timing='final manual command then feedback/history sample at policy decision',
          step_feedback_not_sampled_before_next_manual_command=True)

def build_frozen_policy(vec,path,device):
    actor,variant,digest=load_frozen_actor(path,vec.num_envs,device)
    wrapped=DecisionHistoryVec(vec,variant)
    def policy(obs):
        with torch.inference_mode():return actor(obs)
    wrapped.checkpoint_sha256=digest
    return wrapped,policy,wrapped
