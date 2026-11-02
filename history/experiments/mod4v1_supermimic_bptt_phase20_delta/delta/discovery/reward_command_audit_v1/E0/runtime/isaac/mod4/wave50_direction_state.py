"""Episode-bound entry direction, independent state, no additional random stream."""
import torch
PROFILE='WAVE50_actual_legal_entry_episode_direction_v1'
KEY='E1_WAVE50_episode_direction_state'
FIELDS=('wave_mask','entry_sign','bound_episode','reset_xy','control_histogram')

def validate(s,n):
 assert s['profile']==PROFILE and s['version']==1 and s['num_envs']==n
 assert s['no_new_rng'] and s['no_live_position_or_heading_correction']
 for k in ('assignment_sha256','entry_map_sha256','entry_origin_sha256'):assert isinstance(s[k],str) and len(s[k])==64
 assert s['wave_mask'].shape==(n,) and s['wave_mask'].dtype==torch.bool
 assert s['entry_sign'].shape==(n,) and s['bound_episode'].shape==(n,)
 assert s['bound_episode'].dtype==torch.long and (s['bound_episode']>=0).all()
 assert s['reset_xy'].shape==(n,2) and torch.isfinite(s['reset_xy']).all()
 assert ((s['entry_sign'][s['wave_mask']].abs()==1).all()) and (s['entry_sign'][~s['wave_mask']]==0).all()
 assert s['control_histogram'].shape==(2,3) and s['control_histogram'].dtype==torch.long and (s['control_histogram']>=0).all()
 return True
