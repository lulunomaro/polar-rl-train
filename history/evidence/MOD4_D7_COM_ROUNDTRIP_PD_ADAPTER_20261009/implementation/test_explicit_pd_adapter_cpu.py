"""Meaningful fake-backend boundary contracts, not a replacement for actual CUDA SDK."""
from types import SimpleNamespace
import torch
from explicit_pd_sdk_adapter import ExplicitPDSDK
def fixture():
    n=10;legs=SimpleNamespace(stiffness=torch.full((n,4),60.),damping=torch.full((n,4),2.),joint_indices=[0,2,4,6])
    wheels=SimpleNamespace(stiffness=torch.zeros(n,2),damping=torch.full((n,2),.6),joint_indices=[1,3])
    dk=torch.zeros(n,8);dd=torch.zeros(n,8);dd[:,7]=3.
    r=SimpleNamespace(actuators=dict(legs=legs,wheels=wheels),joint_names=list('abcdefgh'),root_view=SimpleNamespace(get_dof_stiffnesses=lambda:dk,get_dof_dampings=lambda:dd))
    mild=SimpleNamespace(gains={name:{k:getattr(a,k).clone() for k in ('stiffness','damping')} for name,a in r.actuators.items()})
    def audit():
        for name,a in r.actuators.items():
            for k,v in mild.gains[name].items():assert torch.equal(getattr(a,k),v)
        assert dd[0,7]==3.;return dict(actual_parameters_pass=True)
    mild.audit=audit;env=SimpleNamespace(scene={'robot':r},_mild_dr=mild,num_envs=n,device='cpu',resets=[])
    env._reset_idx=lambda ids:env.resets.append(ids.clone())
    return env,r,dk,dd
def test_contracts():
    passed=[];e,r,dk,dd=fixture();refs={n:{k:v for k,v in row.items()} for n,row in e._mild_dr.gains.items()};global_rng=torch.get_rng_state().clone()
    a=ExplicitPDSDK(e,True,7);assert a.leg_ids==[0,2,4,6] and a.wheel_ids==[1,3];passed.append('actual_motor_group_indices_and_coefficient_shape')
    values=a.audit_parameters();assert bool(((values['leg_kp']>=57)&(values['leg_kp']<=63)).all());passed.append('separate_explicit_PD_coefficients_within_approved_range')
    assert bool((dk==0).all()) and dd[0,7]==3.;passed.append('motor_zero_drive_and_other_gas_damping_unchanged')
    assert bool((r.actuators['wheels'].stiffness==0).all());passed.append('wheel_kp_stays_zero')
    assert e._mild_dr.audit()['actual_parameters_pass'];passed.append('actual_expected_value_audit_without_tolerance_change')
    assert all(e._mild_dr.gains[n][k] is v for n,row in refs.items() for k,v in row.items());passed.append('finally_restores_original_audit_references')
    ids=torch.tensor([1,4,7]);other=torch.tensor([0,2,3,5,6,8,9]);old=a.state_dict();oldkp=r.actuators['legs'].stiffness.clone();e._reset_idx(ids)
    assert torch.equal(a.component.episode[ids],old['episode'][ids]+1) and len(e.resets)==1;passed.append('selected_parent_reset_then_PD_episode_once')
    assert torch.equal(r.actuators['legs'].stiffness[other],oldkp[other]) and torch.equal(a.component.episode[other],old['episode'][other]);passed.append('other_environment_model_state_unchanged')
    state=a.state_dict();a.component.reset(ids);a.apply(ids);a.load_state_dict(state);assert torch.equal(a.component.factor['leg_kp'],state['factor']['leg_kp']);passed.append('complete_private_state_restores_actual_model')
    dk[0,0]=1
    try:a.audit_parameters()
    except AssertionError:pass
    else:raise AssertionError('Implicit drive mutation accepted')
    dk[0,0]=0;passed.append('nonzero_implicit_motor_drive_rejected')
    r.actuators['legs'].stiffness[0,0]=999
    try:a.audit_parameters()
    except AssertionError:pass
    else:raise AssertionError('Wrong model coefficient accepted')
    a.apply(torch.tensor([0]));passed.append('wrong_model_coefficient_rejected')
    # An explicit PD model consumes these coefficients; this check does not claim SDK torque measurement.
    expected=state['factor']['leg_kp']*60*.05-state['factor']['leg_kd']*2*.2
    actual=r.actuators['legs'].stiffness*.05-r.actuators['legs'].damping*.2
    assert torch.equal(actual,expected);passed.append('explicit_model_coefficient_effect_separate_from_implicit_drive')
    e2,r2,_,_=fixture();off=ExplicitPDSDK(e2,False,9);assert off.model_write_calls==0;passed.append('off_no_model_parameter_writes')
    assert torch.equal(global_rng,torch.get_rng_state());passed.append('global_RNG_unchanged')
    assert not torch.cuda.is_initialized();passed.append('CPU_only_not_actual_SDK_or_PPO_proof')
    return passed
