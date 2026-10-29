"""New conditional command state, separate from historical terrain bookkeeping."""
import torch
PROFILE='E1_G3_verified_plane_signed_straight_world05_yaw12_v1'
FIELDS=('eligible_flat','linear','moving','direction','signed_yaw','linear_vx','family','sample_histogram','control_histogram','_command_heading','phase_elapsed')
def validate(s,n):
 assert s['version']==1 and s['profile']==PROFILE and s['num_envs']==n
 assert s['rng_device_type'] in ('cpu','cuda') and s['rng'].dtype==torch.uint8 and s['rng'].ndim==1 and s['rng'].numel()>0
 for k in ('eligible_flat','linear','moving'):
  assert s[k].shape==(n,) and s[k].dtype==torch.bool
 assert not (s['linear']&s['moving']).any() and not ((s['linear']|s['moving'])&~s['eligible_flat']).any()
 for k in ('direction','signed_yaw','linear_vx','_command_heading','phase_elapsed'):
  assert s[k].shape==(n,) and s[k].dtype==torch.float32 and torch.isfinite(s[k]).all()
 assert s['family'].shape==(n,) and s['family'].dtype==torch.long
 assert ((s['family']>=-1)&(s['family']<5)).all()
 assert ((s['signed_yaw'][s['moving']].abs()>=1)&(s['signed_yaw'][s['moving']].abs()<=2)).all()
 assert (s['signed_yaw'][~s['moving']]==0).all()
 assert s['BODY_command'].shape==(n,3) and torch.isfinite(s['BODY_command']).all() and (s['BODY_command'][:,1]==0).all()
 assert ((s['linear_vx'][s['linear']].abs()>=1)&(s['linear_vx'][s['linear']].abs()<=1.5)).all()
 for k in ('sample_histogram','control_histogram'):
  assert s[k].shape==(6,7) and s[k].dtype==torch.long and (s[k]>=0).all()
 assert len(s['assignment_sha256'])==64 and s['no_position_correction'] and s['no_mask_actor_or_gate_input']
 return True

def same(a,b):
 if isinstance(a,torch.Tensor):return isinstance(b,torch.Tensor) and torch.equal(a.cpu(),b.cpu())
 if isinstance(a,dict):return a.keys()==b.keys() and all(same(a[k],b[k]) for k in a)
 return a==b
