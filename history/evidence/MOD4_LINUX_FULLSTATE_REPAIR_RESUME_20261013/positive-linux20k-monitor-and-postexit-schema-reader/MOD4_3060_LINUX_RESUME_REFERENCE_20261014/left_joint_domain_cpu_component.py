"""CPU-only explicit interior left-head initialization candidate, not deployment.

Only initial final-layer row0 is replaced by a copy of row1 plus an independently
specified legal difference. Five other means, trunk, std and critic are exact.
No live output coupling, teacher, changed action processor or additional RNG.
"""
import copy
import torch

SOURCE_SHA='17b2271644bbe02ae195a16ea97b2d7442bc957a02662fb6737b81eb64f865e9'
PROFILE='left_final_row0_interior_reset_pose_difference_CPU_candidate_v1'

def same(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.shape==b.shape and a.dtype==b.dtype and torch.equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return type(a)is type(b) and a==b

def legal_raw_left_interval(hip_raw,offsets,*,scale=.5,lower=-1.0843,upper=.85):
    assert hip_raw.dtype==offsets.dtype and hip_raw.device.type==offsets.device.type=='cpu'
    assert scale==.5 and lower<upper and offsets.shape[-1]==4
    hip=hip_raw.clip(-6.,6.)
    delta=offsets[...,0]-offsets[...,1]
    lo=hip+(lower-delta)/scale;hi=hip+(upper-delta)/scale
    return torch.maximum(lo,torch.full_like(lo,-6.)),torch.minimum(hi,torch.full_like(hi,6.))

def guarded_targets(raw,offsets,*,scale=.5,lower=-1.0843,upper=.85):
    assert raw.shape[-1]==6 and offsets.shape[-1]==4
    assert scale==.5 and lower<upper
    target=raw[...,:4].clip(-6.,6.)*scale+offsets
    target=target.clone()
    target[...,0]=torch.clamp(target[...,0],min=target[...,1]+lower,max=target[...,1]+upper)
    target[...,2]=torch.clamp(target[...,2],min=target[...,3]+lower,max=target[...,3]+upper)
    return target

def _network(ck):
    a=ck['actor_state_dict'];o=ck['optimizer_state_dict'];c=ck['critic_state_dict']
    keys=['distribution.std_param','mlp.0.weight','mlp.0.bias','mlp.2.weight','mlp.2.bias','mlp.4.weight','mlp.4.bias','mlp.6.weight','mlp.6.bias']
    assert list(a)==keys and list(c)==keys[1:]
    assert a['mlp.0.weight'].shape==(256,35) and a['mlp.6.weight'].shape==(6,64)
    assert a['mlp.6.bias'].shape==(6,) and a['distribution.std_param'].shape==(6,)
    assert c['mlp.0.weight'].shape==(256,38) and c['mlp.6.weight'].shape==(1,64)
    assert o['param_groups'][0]['params']==list(range(17)) and len(o['param_groups'])==1
    for i,v in enumerate(list(a.values())+list(c.values())):
        s=o['state'][i];assert set(s)=={'step','exp_avg','exp_avg_sq'} and s['step'].ndim==0
        assert s['exp_avg'].shape==s['exp_avg_sq'].shape==v.shape
        assert v.device.type=='cpu' and torch.isfinite(v).all()

def candidate_initialization(source,*,source_sha,actual_offset_witness,desired_difference,
                             scale=.5,lower=-1.0843,upper=.85):
    assert not torch.cuda.is_initialized()
    assert source_sha==SOURCE_SHA and source['independent_terrain_expert']=='E1_WAVE50'
    assert 'LEFT_JOINT_DOMAIN_INTERIOR_CANDIDATE' not in source,'Never repeat initialization on owncandidate'
    assert source['E1_terrain_state']['num_envs']==512
    assert source['E1_terrain_state']['G4_height_peak_to_trough_m']==.05
    assert source['E1_terrain_state']['command_vx_range']==[-.3,.3]
    assert source['E1_terrain_state']['entry_assignment_sha256']=='4c9a7f3b596bc055e8501a91a69bc9ffd1c8c58516b955f0003ba1b5031fe73d'
    _network(source)
    offsets=torch.as_tensor(actual_offset_witness,dtype=torch.float32)
    assert offsets.shape==(4,) and torch.isfinite(offsets).all()
    historical=torch.tensor(source['WINDOWS4090_LEFT_HEAD_REPAIR_ACTUAL']['actual_GPU_API_offset_and_default_q_leg_order'])
    assert torch.equal(offsets,historical),'Saved actual/reference offset identity; targetAPI still must remeasure'
    assert scale==.5 and lower<desired_difference<upper, 'Explicit genuinely interior difference only'
    assert min(desired_difference-lower,upper-desired_difference)>.1,'Keep a stated interior margin; no boundary-preserving pretendrepair'
    rng=torch.get_rng_state().clone();out=copy.deepcopy(source)
    a=out['actor_state_dict'];old=source['actor_state_dict']
    delta=(desired_difference-float(offsets[0]-offsets[1]))/scale
    # One-time parameter copy. Forward and the six-action ABI remain original.
    a['mlp.6.weight'][0].copy_(old['mlp.6.weight'][1])
    a['mlp.6.bias'][0].copy_(old['mlp.6.bias'][1]+delta)
    for param in (7,8):
        for field in ('exp_avg','exp_avg_sq'):out['optimizer_state_dict']['state'][param][field][0].zero_()
    for key in old:
        if key in ('mlp.6.weight','mlp.6.bias'):assert torch.equal(a[key][1:],old[key][1:])
        else:assert torch.equal(a[key],old[key]),key
    assert same(out['critic_state_dict'],source['critic_state_dict'])
    for key in source:
        if key not in ('actor_state_dict','optimizer_state_dict'):assert same(out[key],source[key]),key
    o=out['optimizer_state_dict'];prev=source['optimizer_state_dict']
    assert same(o['param_groups'],prev['param_groups'])
    for i in range(17):
        assert same(o['state'][i]['step'],prev['state'][i]['step'])
        for field in ('exp_avg','exp_avg_sq'):
            if i in (7,8):assert torch.equal(o['state'][i][field][1:],prev['state'][i][field][1:])
            else:assert same(o['state'][i][field],prev['state'][i][field])
    assert torch.equal(rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
    out['LEFT_JOINT_DOMAIN_INTERIOR_CANDIDATE']=dict(profile=PROFILE,source_SHA=source_sha,
       desired_crank_minus_hip_rad=desired_difference,actual_reference_offset=offsets.tolist(),
       source512_history_preserved=True,only_left_final_weight_bias_row0_changed=True,
       five_other_mean_heads_shared_trunk_std_critic_exact=True,only_Adam_moment_row0_parameters7_8_cleared=True,
       Adam_step_scalars_preserved=True,no_new_RNG=True,no_live_action_coupling=True,
       initial_left_mechanical_target_change_explicit=True,CPU_prepared_only=True,
       own_GPU_physics_fullstate_sourceepisodeplusone_and_behavior_not_evaluated=True,
       cannot_load_into_running_trainer=True,not_qualified50=True)
    return out

def CPU_mean(actor,obs):
    assert obs.dtype==torch.float32 and obs.shape[-1]==35 and obs.device.type=='cpu'
    x=obs
    for i in (0,2,4):x=torch.nn.functional.elu(torch.nn.functional.linear(x,actor[f'mlp.{i}.weight'],actor[f'mlp.{i}.bias']))
    return torch.nn.functional.linear(x,actor['mlp.6.weight'],actor['mlp.6.bias'])
