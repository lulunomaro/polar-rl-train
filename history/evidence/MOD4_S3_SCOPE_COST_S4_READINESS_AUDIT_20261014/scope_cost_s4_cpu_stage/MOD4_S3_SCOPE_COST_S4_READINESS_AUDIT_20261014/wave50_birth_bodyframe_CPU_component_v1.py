"""Proposed birth-only orientation exposure math; no live simulator integration.

Old full state must be restored before declaring this new entry/direction scope.
World route limits stay fixed. BODY coefficients are bound only at real births.
"""
import torch
PROFILE='E1_WAVE50_balanced_birth_bodyframe_v1'
KEY='E1_WAVE50_balanced_birth_bodyframe_state_v1'
SOURCE='e3e825b1e24f11885f2f9d5b196d85cbce4a46363cd09b440e7efa2b846fd47c'

def validate(s,identity=None):
 assert s['profile']==PROFILE and s['source_SHA']==SOURCE and s['num_envs']==20000
 assert s['new_geometry'] is False and s['new_entry_pose'] is True and s['new_BODY_direction_identity'] is True
 assert s['new_world_route_or_lifetime'] is False and s['new_RNG_draws'] is False and s['live_heading_position_correction'] is False
 assert s['actual_GPU_fullrestore_verified'] is False and s['CPU_proposal_only'] is True
 n=s['num_envs'];mask=s['wave_mask'];sign=s['world_toward_sign']
 assert mask.shape==(n,) and mask.dtype==torch.bool and sign.shape==(n,) and sign.dtype==torch.float32
 assert torch.equal(sign[~mask],torch.zeros_like(sign[~mask])) and ((sign[mask]==1)|(sign[mask]==-1)).all()
 for k in ('rank_in_entry_side','source_episode','bound_episode'):
  assert s[k].shape==(n,) and s[k].dtype==torch.int64
 assert s['flip_pi'].shape==(n,) and s['flip_pi'].dtype==torch.bool and not s['flip_pi'][~mask].any()
 assert torch.equal(s['BODY_coefficient'],torch.where(s['flip_pi'],-torch.ones_like(sign),torch.ones_like(sign)))
 assert s['Wave_inward_limit_m']==4. and s['other_outward_lateral_limit_m']==2. and s['Wave_seconds']==40. and s['other_seconds']==20.
 assert s['source_episode'].min()>=0
 if identity is not None:assert s['source_bindings']==identity
 return True

def from_strict_source(source_sha,wave_mask,world_sign,source_episode,identity):
 assert source_sha==SOURCE and len(source_episode)==20000
 mask=wave_mask.clone();sign=world_sign.clone();base=source_episode.clone();rank=torch.full_like(base,-1)
 for side in (-1.,1.):
  ids=torch.nonzero(mask & (sign==side),as_tuple=False).flatten();rank[ids]=torch.arange(len(ids),dtype=torch.int64)
 n=len(base)
 s=dict(profile=PROFILE,source_SHA=source_sha,num_envs=n,source_bindings=dict(identity),wave_mask=mask,world_toward_sign=sign,rank_in_entry_side=rank,source_episode=base,bound_episode=torch.full_like(base,-1),flip_pi=torch.zeros(n,dtype=torch.bool),BODY_coefficient=torch.ones(n,dtype=torch.float32),
  new_geometry=False,new_entry_pose=True,new_BODY_direction_identity=True,new_world_route_or_lifetime=False,new_RNG_draws=False,live_heading_position_correction=False,
  actual_GPU_fullrestore_verified=False,CPU_proposal_only=True,Wave_inward_limit_m=4.,other_outward_lateral_limit_m=2.,Wave_seconds=40.,other_seconds=20.)
 validate(s,identity);return s

def bind_selected_births(s,ids,new_episode,identity):
 validate(s,identity)
 assert ids.ndim==1 and ids.dtype==torch.int64 and len(ids)==len(torch.unique(ids)) and ((ids>=0)&(ids<s['num_envs'])).all()
 assert new_episode.shape==s['source_episode'].shape and new_episode.dtype==torch.int64
 prior=s['bound_episode'][ids];base=s['source_episode'][ids]
 expected=torch.where(prior<0,base+1,prior+1)
 assert torch.equal(new_episode[ids],expected),'Exactly one new physical birth; no live rebinding or skipped episode'
 q={k:(v.clone() if torch.is_tensor(v) else dict(v) if isinstance(v,dict) else v) for k,v in s.items()}
 mask=q['wave_mask'][ids];flip=mask & (((q['rank_in_entry_side'][ids]+new_episode[ids]-base)%2)==1)
 q['bound_episode'][ids]=new_episode[ids];q['flip_pi'][ids]=flip;q['BODY_coefficient'][ids]=torch.where(flip,-1.,1.)
 validate(q,identity);return q

def command_from_original(original,current_family,standing,s):
 validate(s);n=s['num_envs']
 assert original.shape==(n,3) and torch.isfinite(original).all() and current_family.shape==(n,) and standing.shape==(n,) and standing.dtype==torch.bool
 active=s['wave_mask']&(current_family==4)&~standing
 assert (s['bound_episode'][active]>=0).all()
 assert (original[active,0]*s['world_toward_sign'][active]>=0).all() and (original[active,0].abs()<=.300001).all()
 assert (original[active,1:]==0).all() and (original[standing]==0).all()
 out=original.clone();out[active,0]*=s['BODY_coefficient'][active]
 assert torch.equal(out[~active],original[~active]) and torch.equal(out[:,1:],original[:,1:])
 assert torch.equal(out[active,0]*s['BODY_coefficient'][active],original[active,0])
 return out

def rotate_birth_xyzw(original,flip):
 assert original.ndim==2 and original.shape[1]==4 and flip.shape==(len(original),) and flip.dtype==torch.bool
 assert torch.isfinite(original).all() and torch.allclose(original.square().sum(-1),torch.ones(len(original)),atol=1e-6,rtol=0)
 result=original.clone();q=original[flip];result[flip]=torch.stack((-q[:,1],q[:,0],q[:,3],-q[:,2]),-1)
 assert torch.equal(result[~flip],original[~flip])
 return result
