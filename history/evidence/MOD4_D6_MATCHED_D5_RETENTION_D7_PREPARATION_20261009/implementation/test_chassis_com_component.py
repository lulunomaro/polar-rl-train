"""Target Torch CPU state/reset/units contracts; no CUDA initialization or SDK."""
import copy,torch
from chassis_com_component import ChassisCOM,PROFILE

def same(a,b):
    if torch.is_tensor(a):return torch.equal(a,b)
    if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return a==b
def rejected(fn):
    try:fn()
    except (ValueError,KeyError):return
    raise AssertionError('Required rejection missing')
def test_contracts():
    passed=[];global_rng=torch.get_rng_state().clone()
    c=ChassisCOM(10,'cpu',731,True);assert c.delta_m.shape==(10,3) and bool((c.delta_m==0).all());passed.append('shape_initial_SI_zero')
    c.reset(torch.arange(10));assert bool((c.delta_m.abs()<=.005).all()) and bool((c.episode==1).all());passed.append('three_axes_5mm_bounds_episode')
    before=c.state_dict();ids=torch.tensor([1,4,7]);other=torch.tensor([0,2,3,5,6,8,9]);c.reset(ids)
    assert torch.equal(c.delta_m[other],before['delta_m'][other]) and torch.equal(c.episode[other],before['episode'][other]);passed.append('selected_reset_other_rows_exact')
    assert torch.equal(c.episode[ids],before['episode'][ids]+1);passed.append('selected_episode_once')
    assert not torch.equal(c.delta_m[:,0],c.delta_m[:,1]) and not torch.equal(c.delta_m[:,1],c.delta_m[:,2]);passed.append('independent_axis_streams')
    after=c.state_dict();c.reset(torch.empty(0,dtype=torch.long));assert same(c.state_dict(),after);passed.append('empty_reset_no_draw')
    off=ChassisCOM(10,'cpu',731,False);s=off.state_dict();off.reset(torch.arange(10));assert bool((off.delta_m==0).all()) and same(s['private_xyz_RNG'],off.state_dict()['private_xyz_RNG']);passed.append('off_exact_no_draw')
    x=ChassisCOM(10,'cpu',1,True);x.load_state_dict(c.state_dict());assert same(x.state_dict(),c.state_dict());passed.append('complete_state_roundtrip')
    c.reset(ids);x.reset(ids);assert same(x.state_dict(),c.state_dict());passed.append('next_selected_draw_exact')
    assert torch.equal(global_rng,torch.get_rng_state());passed.append('global_RNG_unchanged')
    rejected(lambda:c.reset([1,1]));rejected(lambda:c.reset([-1]));rejected(lambda:c.reset([10]));rejected(lambda:c.reset([1.]));passed.append('invalid_indices_rejected')
    for key,value in [('profile','wrong'),('enabled',False),('num_envs',9),('version',0)]:
        s=copy.deepcopy(c.state_dict());s[key]=value;rejected(lambda:x.load_state_dict(s))
    passed.append('state_scope_rejected')
    for value in (float('nan'),.006):
        s=copy.deepcopy(c.state_dict());s['delta_m'][0,0]=value;rejected(lambda:x.load_state_dict(s))
    passed.append('nonfinite_out_of_bounds_rejected')
    assert not torch.cuda.is_initialized();passed.append('CPU_only_no_CUDA')
    return passed
if __name__=='__main__':
    import json
    print(json.dumps(dict(profile=PROFILE,passed=test_contracts(),torch_version=torch.__version__,CUDA_initialized=torch.cuda.is_initialized())))
