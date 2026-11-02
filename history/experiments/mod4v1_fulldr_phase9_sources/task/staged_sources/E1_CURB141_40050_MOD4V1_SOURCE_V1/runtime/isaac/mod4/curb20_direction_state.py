"""Episode-bound entry direction, independent state, no additional random stream."""
import torch
PROFILE='CURB20_actual_entry_episode_direction_v1'
KEY='E1_CURB_entry_direction_state'
FIELDS=('curb_mask','entry_sign','bound_episode','reset_xy','control_histogram')

def validate(s,n):
 assert s['profile']==PROFILE and s['version']==1 and s['num_envs']==n
 assert s['no_new_rng'] and s['no_live_position_or_heading_correction']
 for k in ('assignment_sha256','entry_map_sha256'):assert isinstance(s[k],str) and len(s[k])==64
 assert s['curb_mask'].shape==(n,) and s['curb_mask'].dtype==torch.bool
 assert s['entry_sign'].shape==(n,) and s['bound_episode'].shape==(n,)
 assert s['bound_episode'].dtype==torch.long and (s['bound_episode']>=0).all()
 assert s['reset_xy'].shape==(n,2) and torch.isfinite(s['reset_xy']).all()
 assert ((s['entry_sign'][s['curb_mask']].abs()==1).all()) and (s['entry_sign'][~s['curb_mask']]==0).all()
 assert s['control_histogram'].shape==(2,3) and s['control_histogram'].dtype==torch.long and (s['control_histogram']>=0).all()
 return True

def bind_numpy(xy,assignments):
 import numpy as np
 xy=np.asarray(xy,dtype='<f4');mask=np.zeros(len(xy),bool);sign=np.zeros(len(xy),dtype='<f4')
 for a in assignments:
  if a['family']!='random_uniform_for_rm':continue
  b=np.asarray(a['bounds']);inside=((xy>=b[0,:2])&(xy<b[1,:2])).all(1)
  assert not (mask&inside).any();center=(b[0,0]+b[1,0])*.5
  d=xy[inside,0]-center;assert (abs(d)>.7).all()
  mask[inside]=True;sign[inside]=-np.sign(d)
 return mask,sign
