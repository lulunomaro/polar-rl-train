"""CPU-only proposed one-channel initialization migration; never deploys training.

The independent actor last-layer row0 is initialized from row1 plus the existing
input-difference lower boundary. It can learn independently afterward: no live
left/right action coupling, extra layer, teacher, or privileged actor input.
"""
from pathlib import Path
import copy,hashlib
import numpy as np
import torch

PROFILE='left_crank_effective_exploration_recenter_v1'
APPROVED_SOURCE_SHA='91d428f02d27cdc6c876e30f355e1dcab6c7398042c2f240a1f177e5b3a898f4'
ANCESTOR_SHA='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
INITIAL35_SHA='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
GEOMETRY_SHA='32e0a753c886244c4bfcf24d5523d800e06e0bb1035a78ddc494d6144e2dc4bd'
PARTITION_SHA='c2317e380d49eea6f4647aecfdc46cfbab70b40ddaf059e9e75f2585950aca78'
ASSIGNMENT_SHA='4c9a7f3b596bc055e8501a91a69bc9ffd1c8c58516b955f0003ba1b5031fe73d'
LOWER=-1.0843;UPPER=.85;SCALE=.5

def same(a,b):
    if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a,b)
    if isinstance(a,np.ndarray):return isinstance(b,np.ndarray) and a.dtype==b.dtype and a.shape==b.shape and np.array_equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
    if isinstance(a,(list,tuple)):return type(a) is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return type(a) is type(b) and a==b

def floating_count(v):
    if isinstance(v,torch.Tensor):
        if v.is_floating_point() or v.is_complex():assert torch.isfinite(v).all();return 1
        return 0
    if isinstance(v,dict):return sum(floating_count(x) for x in v.values())
    if isinstance(v,(tuple,list)):return sum(floating_count(x) for x in v)
    return 0

def validate_source(ck):
    assert ck['independent_terrain_expert']=='E1_WAVE50','wrong expert'
    assert ck['E1_WAVE50_initial_source_sha256']==INITIAL35_SHA,'wrong initial35 ancestor'
    assert ck['LOCAL_TEMPORARY_BRANCH']['source_SHA']==ANCESTOR_SHA,'wrong original459 source'
    assert ck['LOCAL_TEMPORARY_BRANCH']['local_num_envs']==128,'wrong local environment count'
    t=ck['E1_terrain_state']
    assert t['geometry_triangles_sha256']==GEOMETRY_SHA and t['ordered_partition_triangles_sha256']==PARTITION_SHA,'wrong geometry'
    assert t['entry_assignment_sha256']==ASSIGNMENT_SHA and t['num_envs']==128,'wrong assignment'
    a=ck['actor_state_dict']
    assert list(a)==['distribution.std_param','mlp.0.weight','mlp.0.bias','mlp.2.weight','mlp.2.bias','mlp.4.weight','mlp.4.bias','mlp.6.weight','mlp.6.bias'],'wrong actor schema'
    assert a['mlp.6.weight'].shape==(6,64) and a['mlp.6.bias'].shape==(6,),'wrong final action-head shape'
    assert a['distribution.std_param'].shape==(6,) and (a['distribution.std_param']>0).all(),'invalid std'
    o=ck['optimizer_state_dict']
    assert len(o['param_groups'])==1 and o['param_groups'][0]['params']==list(range(17)),'wrong optimizer binding'
    for pid,shape in [(0,(6,)),(7,(6,64)),(8,(6,))]:
        assert set(o['state'][pid])=={'step','exp_avg','exp_avg_sq'},'wrong Adam state schema'
        assert o['state'][pid]['step'].shape==torch.Size([]),'wrong original step scalar'
        assert all(o['state'][pid][key].shape==shape for key in ('exp_avg','exp_avg_sq')),'wrong Adam row binding'
    assert floating_count(ck)==107,'wrong complete floating schema'

def migrate(source_path):
    source_path=Path(source_path)
    digest=hashlib.sha256(source_path.read_bytes()).hexdigest()
    assert digest==APPROVED_SOURCE_SHA,'wrong complete source bytesSHA'
    old=torch.load(source_path,map_location='cpu',weights_only=False)
    validate_source(old);new=copy.deepcopy(old);a=new['actor_state_dict'];o=new['optimizer_state_dict']
    a['mlp.6.weight'][0].copy_(a['mlp.6.weight'][1])
    a['mlp.6.bias'][0]=a['mlp.6.bias'][1]+LOWER/SCALE
    a['distribution.std_param'][0]=a['distribution.std_param'][2]
    for pid in (0,7,8):
        for key in ('exp_avg','exp_avg_sq'):o['state'][pid][key][0].zero_()
        assert torch.equal(o['state'][pid]['step'],old['optimizer_state_dict']['state'][pid]['step'])
    for k in old:
        if k not in ('actor_state_dict','optimizer_state_dict'):assert same(new[k],old[k]),k
    for k in a:
        if k not in ('mlp.6.weight','mlp.6.bias','distribution.std_param'):assert torch.equal(a[k],old['actor_state_dict'][k]),k
        else:assert torch.equal(a[k][1:],old['actor_state_dict'][k][1:]),k
    assert same(o['param_groups'],old['optimizer_state_dict']['param_groups'])
    for pid in o['state']:
        if pid not in (0,7,8):assert same(o['state'][pid],old['optimizer_state_dict']['state'][pid]),pid
        else:
            for key in ('exp_avg','exp_avg_sq'):assert torch.equal(o['state'][pid][key][1:],old['optimizer_state_dict']['state'][pid][key][1:])
    new['LOCAL_LEFT_HEAD_EXPLORATION_MIGRATION']=dict(profile=PROFILE,source_sha256=digest,
        explicit_new_initialization_axis=True,CPU_prepared_only_no_CUDA_or_PPO=True,
        action_dimension_6_unchanged=True,only_actor_output_column0_and_its_std0_changed=True,
        independent_parameter_row_initialization_not_live_action_coupling=True,
        other_five_action_rows_and_std_exact=True,critic_all_DR_all_RNG_terrain_command_episode_state_exact=True,
        optimizer_moment_rows_zeroed=[{'parameter_id':pid,'row':0} for pid in (0,7,8)],
        original_optimizer_step_scalars_retained=True,
        deterministic_guarded_target_preservation_proven_only_for_actual_saved_baseline_prefix_domain=True,
        qualification_claimed=False)
    assert floating_count(new)==107
    return new,old
