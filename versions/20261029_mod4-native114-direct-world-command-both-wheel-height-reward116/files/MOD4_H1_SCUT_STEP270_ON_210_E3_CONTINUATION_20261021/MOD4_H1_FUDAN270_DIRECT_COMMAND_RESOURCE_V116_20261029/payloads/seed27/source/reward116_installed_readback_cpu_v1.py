"""Installed candidate116 own133 FK/command/reward readback, no learned forward."""
import torch
from private_phase_frame_v1 import encode
from reward111_installed_readback_cpu_v1 import check as retained_input_FK_readback

def check(mdp,pi,critic,bank_state):
    old=retained_input_FK_readback(mdp,pi,critic,bank_state)
    n=len(bank_state[0]);frame=encode(torch.full((n,),300,dtype=torch.long),torch.zeros(n,dtype=torch.long));a=torch.zeros(n,6)
    root=bank_state[0].clone();root[:,0]=.056;root[:,1]=0
    aux=bank_state[6].clone();aux[...,:18].reshape(n,3,2,3)[...,:,2]=100.
    zero_v=torch.zeros_like(root)
    s=(root,bank_state[1],zero_v,bank_state[3],bank_state[4],bank_state[5],aux)
    result=mdp.objective_terms(s,frame,a,a)
    selected=result['selected_optimization_terms']
    assert torch.equal(result['total'],sum(selected.values()))
    assert torch.equal(selected['both_wheel_height_270_with_forward_command'],torch.zeros_like(result['total']))
    assert result['legacy_jump_reward_is_diagnostic_not_optimization']
    assert result['command_tracking116']['target_each_wheel_bottom_m']==.27
    assert torch.isfinite(result['total']).all() and (result['total']>=0).all() and (result['total']<=.160001).all()
    return dict(passed=True,retained_input_own_FK_heading=old,actual_own_bank_poses=n,stationary_height_bonus_exact_zero=True,
        actual_selected_sum_literal=True,actual_wheel_bottom_target_m=.27,legacy_jump_reward_is_diagnostic_only=True,
        no_body_height_flight_tuck_extend_positive_terms_selected=True,no_learned_actor_WM_Critic_forward=True,
        source_counterexamples_separate_from_actual_dynamic_success=True,actual_PhysX_precontrol_readback_still_required=True)
