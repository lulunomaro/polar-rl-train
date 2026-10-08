"""Target CPU independent-group state/selection/range contracts, no SDK proof."""
import copy,torch
from explicit_pd_component import ExplicitPD
def equal(a,b):
    if torch.is_tensor(a):return torch.equal(a,b)
    if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    return a==b
def rejects(fn):
    try:fn()
    except (ValueError,KeyError):return
    raise AssertionError('Required rejection absent')
def test_contracts():
    passed=[];rng=torch.get_rng_state().clone();p=ExplicitPD(10,'cpu',1,True)
    assert {k:tuple(v.shape) for k,v in p.factor.items()}=={'leg_kp':(10,4),'leg_kd':(10,4),'wheel_kd':(10,2)};passed.append('explicit_leg_kp_kd_wheel_kd_groups_shapes')
    p.reset(torch.arange(10));assert all(bool(((v>=.95)&(v<=1.05)).all()) for v in p.factor.values());passed.append('approved_factor_bounds')
    c=p.coefficients();assert bool(((c['leg_kp']>=57)&(c['leg_kp']<=63)).all()) and bool(((c['leg_kd']>=1.9)&(c['leg_kd']<=2.1)).all());passed.append('actual_nominal_leg_coefficients')
    assert bool(((c['wheel_kd']>=.57)&(c['wheel_kd']<=.63)).all());passed.append('wheel_velocity_derivative_coefficient')
    assert not torch.equal(p.factor['leg_kp'],p.factor['leg_kd']);passed.append('independent_coefficient_streams')
    before=p.state_dict();ids=torch.tensor([1,4,7]);other=torch.tensor([0,2,3,5,6,8,9]);p.reset(ids)
    assert all(torch.equal(p.factor[k][other],v[other]) for k,v in before['factor'].items()) and torch.equal(p.episode[ids],before['episode'][ids]+1);passed.append('selected_reset_other_rows_exact')
    q=ExplicitPD(10,'cpu',2,True);q.load_state_dict(p.state_dict());assert equal(q.state_dict(),p.state_dict());p.reset(ids);q.reset(ids);assert equal(q.state_dict(),p.state_dict());passed.append('complete_state_and_next_private_draw_exact')
    off=ExplicitPD(10,'cpu',1,False);s=off.state_dict();off.reset(torch.arange(10));assert equal(s['private_group_RNG'],off.state_dict()['private_group_RNG']) and all(bool((v==1).all()) for v in off.factor.values());passed.append('off_nominal_no_draw')
    assert torch.equal(rng,torch.get_rng_state());passed.append('global_RNG_unchanged')
    for ids in ([1,1],[-1],[10],[1.]):rejects(lambda:p.reset(ids))
    passed.append('invalid_indices_rejected')
    for value in (float('nan'),1.2):
        s=copy.deepcopy(p.state_dict());s['factor']['leg_kp'][0,0]=value;rejects(lambda:q.load_state_dict(s))
    passed.append('nonfinite_out_of_bounds_state_rejected')
    assert not torch.cuda.is_initialized();passed.append('CPU_only_not_SDK_PPO_or_hardware_proof')
    return passed
if __name__=='__main__':
    import json
    print(json.dumps(dict(passed=test_contracts(),torch_version=torch.__version__,CUDA_initialized=torch.cuda.is_initialized())))
