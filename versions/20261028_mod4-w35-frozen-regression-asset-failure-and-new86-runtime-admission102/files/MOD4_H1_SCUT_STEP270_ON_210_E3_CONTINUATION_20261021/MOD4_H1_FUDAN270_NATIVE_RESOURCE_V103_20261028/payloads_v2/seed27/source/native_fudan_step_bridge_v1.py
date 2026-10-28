"""New task request clock and command, preserving the exact original270 event truth."""
import types
import torch
from native_wheel_leg_bridge_v4 import NativeWheelLegBridge
from supermimic_wheel_leg_v3.contract import SUPERMIMIC_STATE_KEY
from private_phase_frame_v1 import encode

class FudanStepBridge(NativeWheelLegBridge):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.own_env_ids=torch.arange(self.num_envs,device=self.device,dtype=torch.long)
        self._real_reward_tracking=None
    def _encode_current_frame(self,state):
        row=state.info[SUPERMIMIC_STATE_KEY]
        row['f']=encode(row['f'],self.own_env_ids)
        return state
    def init_state(self):return self._encode_current_frame(super().init_state())
    def step(self,actions):
        result=super().step(actions)
        terms=self.mdp.last_reward_components
        # These tensors come from the actual terminal pre-reset state already
        # used for the native reward, never a second actor or world-model call.
        def means(value):
            return {k:means(v) if isinstance(v,dict) else v.detach().mean() for k,v in value.items() if isinstance(v,(dict,torch.Tensor))}
        self._real_reward_tracking=means(terms)
        return self._encode_current_frame(result)
    def reward_tracking_snapshot(self):
        def plain(value):return {k:plain(v) if isinstance(v,dict) else float(v.cpu()) for k,v in value.items()}
        return dict(scope='last_complete_actual_control_mean_over_all4096_not_frozen_skill_evaluation',components=None if self._real_reward_tracking is None else plain(self._real_reward_tracking),step_top_z_m=.27,request_control_interval=[200,500],physical_success_from_original270_counter_only=True)

def install_fudan_step_request_and_command(env):
    import spin_commands
    from h1_original_directional_runtime import audit as directional_audit
    from h1_external_operator_command_v1 import H1ExternalOperatorCommand
    assert not getattr(env,'_own_fudan_step_task_installed',False)
    phase=env.h1_phase
    def request(this):return (this.age_control>=200)&(this.age_control<500)
    phase.public_request=types.MethodType(request,phase)
    def publish(this):
        this._mod4_mode_bit=this.h1_phase.public_mode()
        term=this.command_manager.get_term('twist');term.set_manual_evaluation_mode();term.vel_command_b.zero_()
        term.vel_command_b[:,0]=this.h1_phase.public_request().to(term.vel_command_b.dtype)*.5*(~this.h1_phase.goal.success).to(term.vel_command_b.dtype)
    def audit(this):
        result=directional_audit(this);term=this.command_manager.get_term('twist')
        assert isinstance(term,H1ExternalOperatorCommand)
        expected=torch.zeros_like(term.command);expected[:,0]=phase.public_request().to(expected.dtype)*.5*(~phase.goal.success).to(expected.dtype)
        assert torch.equal(term.command,expected)
        result.update(stage='MOD4_Fudan103_real270_task',request_control_interval=[200,500],approach_command_m_s=.5,zero_yaw_and_lateral=True,original_physical_reset_RNG_unchanged=True,original_true270_cross_footprint_topcontact12_stable200_unchanged=True,public_schedule_explicitly_changed_from100_180=True)
        return result
    env._h1_publish_external_request=types.MethodType(publish,env);spin_commands.audit=audit
    env._own_fudan_step_task_installed=True;env._h1_publish_external_request()
    return audit(env)
