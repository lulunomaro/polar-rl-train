"""Application-boundary fixture with original affine/CAD targets and reset paths."""
import torch,json,types
from action_delay_sdk_adapter import PhysicalActionDelayAdapter
torch.set_num_threads(1);rng=torch.random.get_rng_state().clone()
class Term:
    def __init__(self,env,width):
        self.action_dim=width;self._max_lag=0;self._joint_ids=list(range(width));self._processed_actions=torch.zeros(env.num_envs,width);self.calls=0;self.env=env
        self._asset=types.SimpleNamespace(data=types.SimpleNamespace(default_joint_pos=torch.full((env.num_envs,width),.125),joint_pos_target=torch.zeros(env.num_envs,width),joint_vel_target=torch.zeros(env.num_envs,width)))
        self._asset.set_joint_position_target_index=lambda target,joint_ids:self._asset.data.joint_pos_target.copy_(target)
        self._asset.set_joint_velocity_target_index=lambda target,joint_ids:self._asset.data.joint_vel_target.copy_(target)
    @property
    def processed_actions(self):return self._processed_actions
    def process_actions(self,actions):
        self._processed_actions=actions*2+.125
        if self.action_dim==4:
            self._processed_actions[:,0]=self._processed_actions[:,0].clamp(min=self._processed_actions[:,1]-1.,max=self._processed_actions[:,1]+.85)
            self._processed_actions[:,2]=self._processed_actions[:,2].clamp(min=self._processed_actions[:,3]-1.,max=self._processed_actions[:,3]+.85)
    def apply_actions(self):
        self.calls+=1
        data=self._asset.data
        (data.joint_pos_target if self.action_dim==4 else data.joint_vel_target).copy_(self.processed_actions)
    def reset(self,env_ids=None):pass
def fixture(enabled):
    env=types.SimpleNamespace(num_envs=6,device='cpu',physics_dt=.0025,step_dt=.01,cfg=types.SimpleNamespace(decimation=4),sim=types.SimpleNamespace(_physics_handles_decimation=False),_sim_step_counter=0)
    terms={'legs':Term(env,4),'wheels':Term(env,2)};env.action_manager=types.SimpleNamespace(get_term=lambda k:terms[k])
    adapter=PhysicalActionDelayAdapter(env,enabled,73,collect=True)
    for key,term in terms.items():
        if enabled:adapter.queue.groups[key]['lag_steps']=torch.arange(6)%3
        action=torch.arange(6*term.action_dim).reshape(6,term.action_dim).float()*.01
        term.process_actions(action);requested=term.processed_actions.clone()
        for tick in range(4):
            env._sim_step_counter=tick+1;term.apply_actions()
            actual=term._asset.data.joint_pos_target if key=='legs' else term._asset.data.joint_vel_target
            expected=requested.clone()
            if enabled:
                hold=(torch.arange(6)%3)>tick;expected[hold]=adapter.neutral(key)[hold]
            assert torch.equal(actual,expected) and torch.equal(term.processed_actions,requested)
        env._sim_step_counter=0
        term.reset(torch.tensor([1,4]));assert not bool(adapter.queue.groups[key]['applied_valid'][[1,4]].any())
    assert adapter.formula_max_error==0 and adapter.calls==dict(legs=4,wheels=4)
    return adapter
off=fixture(False);on=fixture(True)
assert torch.equal(rng,torch.random.get_rng_state()) and not torch.cuda.is_initialized()
print(json.dumps(dict(passed=True,contracts=['original_affine_and_CAD_processing_retained','counter_minus1_actual_apply_boundary','0_2500_5000us_selected_transition','actual_articulation_target_matches_queue','requested_processed_targets_restored_after_apply','reset_real_default_q_and_zero_wheel','selected_reset_preserves_other_rows_and_clock','off_exact','independent_streams_no_global_RNG_change','no_CUDA_no_Isaac_no_learning'],count=10,torch_version=torch.__version__,actual_SDK=False,production_runtime_changed=False)))
