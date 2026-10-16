"""Independent episode route state; old global/named/private RNG is unchanged."""
import torch
PROFILE='WAVE50_legal_entry_inward4m_outward2m_lateral2m_v1'
KEY='E1_WAVE50_route_lifecycle_state'
FIELDS=('wave_mask','toward_sign','bound_episode','spawn_xy','inward_limit_m','evaluations')
IDENTITY=('profile','assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_boundary_source_sha256')
def validate(s,n):
 assert s['version']==1 and s['profile']==PROFILE and s['num_envs']==n and s['no_new_rng']
 assert s['Wave_inward_limit_m']==4. and s['outward_limit_m']==2. and s['lateral_limit_m']==2. and s['other_environment_limit_m']==2.
 for k in IDENTITY[1:]:assert isinstance(s[k],str) and len(s[k])==64
 assert s['wave_mask'].shape==(n,) and s['wave_mask'].dtype==torch.bool
 assert s['toward_sign'].shape==(n,) and torch.isfinite(s['toward_sign']).all()
 assert (s['toward_sign'][s['wave_mask']].abs()==1).all() and (s['toward_sign'][~s['wave_mask']]==0).all()
 assert s['bound_episode'].shape==(n,) and s['bound_episode'].dtype==torch.long and (s['bound_episode']>=0).all()
 assert s['spawn_xy'].shape==(n,2) and s['inward_limit_m'].shape==(n,) and torch.isfinite(s['spawn_xy']).all() and torch.isfinite(s['inward_limit_m']).all()
 assert torch.equal(s['inward_limit_m'],torch.where(s['wave_mask'],4.,2.).to(s['inward_limit_m'].device))
 assert s['evaluations'].shape==(n,) and s['evaluations'].dtype==torch.long and (s['evaluations']>=0).all()
 return True
def identity(s):return tuple(s[k] for k in IDENTITY)
def evaluate_timeout(xy,anchor,s,original_timeout):
 assert xy.shape==anchor.shape==(s['num_envs'],2) and torch.isfinite(xy).all()
 delta=xy-anchor;out=original_timeout.clone();mask=s['wave_mask'];inward=delta[:,0]*s['toward_sign']
 out[mask]=((inward>s['inward_limit_m'])|(inward < -2.)|(delta[:,1].abs()>2.))[mask]
 return out
