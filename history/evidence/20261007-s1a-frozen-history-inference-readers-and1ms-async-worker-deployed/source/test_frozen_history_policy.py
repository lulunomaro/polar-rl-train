"""CPU fixtures of actual trained actor loading and evaluation history lifecycle; no learning."""
from pathlib import Path
import sys,json,torch
from tensordict import TensorDict
from frozen_history_policy import load_frozen_actor,DecisionHistoryVec
torch.set_num_threads(1);tests=[]
for p in sys.argv[1:]:
    before=torch.random.get_rng_state().clone();actor,variant,digest=load_frozen_actor(p,4,'cpu')
    assert torch.equal(before,torch.random.get_rng_state());tests.append(variant+'_loader_global_RNG_exact')
    obs=TensorDict(dict(policy=torch.randn(4,35),feedback_history=torch.randn(4,175)),batch_size=[4])
    with torch.no_grad():
        expected=actor.mlp(obs['policy'] if variant=='A0' else torch.cat((obs['policy'],actor.encoder(obs['feedback_history'])),1))
        assert torch.equal(actor(obs),expected)
        extra=obs.clone();extra['body_velocity_label']=torch.randn(4,3)*100;extra['critic']=torch.randn(4,38)*100
        assert torch.equal(actor(obs),actor(extra))
    assert not any(p.requires_grad for p in actor.parameters());tests.extend([variant+'_exact_deterministic_trained_output',variant+'_teacher_and_critic_ignored',variant+'_all_weights_frozen'])

class Env:
    def __init__(self):
        self.common_step_counter=0;self.command=torch.zeros(2,3)
        self.command_manager=type('CM',(),{'get_term':lambda _,name:self})()
    def _reset_idx(self,ids):return None
class Vec:
    def __init__(self):self.unwrapped=Env();self.num_envs=2;self.device='cpu';self.obs=torch.zeros(2,35)
    def get_observations(self):
        self.obs[:,:3]=self.unwrapped.command
        return TensorDict(dict(policy=self.obs.clone(),critic=torch.zeros(2,38)),batch_size=[2])
    def step(self,action):self.unwrapped.common_step_counter+=1;return self.get_observations(),None,None,None
vec=Vec();h=DecisionHistoryVec(vec,'A1');vec.unwrapped._reset_idx(torch.tensor([0,1]));vec.unwrapped.command[:,0]=.3
first=h.get_observations();assert torch.equal(first['feedback_history'].reshape(2,5,35),first['policy'][:,None,:].expand(-1,5,-1))
assert torch.equal(first['feedback_history'],h.get_observations()['feedback_history']);assert h.history.advances==1
tests.append('manual_command_before_first_history_sample_and_same_tick_cache')
h.step(None);vec.unwrapped.command[:,0]=-.3;nextobs=h.get_observations()
assert (nextobs['feedback_history'].reshape(2,5,35)[:,-1,0]==-.3).all();assert h.history.advances==2
tests.append('next_manual_command_is_sampled_before_action_not_on_step_return')
unchanged=h.history.frames[1].clone();vec.unwrapped._reset_idx(torch.tensor([0]));vec.obs[0,5]=4
reset=h.get_observations();assert torch.equal(h.history.frames[1],unchanged) and (h.history.frames[0,:,5]==4).all()
assert h.history.advances==2;tests.append('selected_reset_fresh_history_other_rows_unchanged_same_tick')
vec.obs[1,7]=2
try:h.get_observations();raise AssertionError('Same-tick feedback mutation silently accepted')
except AssertionError as ex:assert 'Feedback changed' in str(ex)
tests.append('same_tick_feedback_change_rejected')
assert not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True,test_count=len(tests),tests=tests,CUDA_initialized=False,actual_task_PPO=False)))
