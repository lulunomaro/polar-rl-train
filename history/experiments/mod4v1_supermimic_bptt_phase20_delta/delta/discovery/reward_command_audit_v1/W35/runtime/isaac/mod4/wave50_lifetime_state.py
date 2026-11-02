import torch
PROFILE='WAVE50_birth_episode_timeout40s_nonWave20s_v1'
KEY='E1_WAVE50_episode_lifetime_state'
FIELDS=('wave_mask','bound_episode','limit_steps')
IDENTITY=('profile','assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_timeout_source_sha256','route_profile')
def identity(s):return tuple(s[k] for k in IDENTITY)
def validate(s,n):
 assert s['version']==1 and s['profile']==PROFILE and s['num_envs']==n and s['no_new_rng']
 assert s['step_dt_s']==.01 and s['Wave_seconds']==40. and s['other_seconds']==20.
 assert s['route_profile']=='WAVE50_legal_entry_inward4m_outward2m_lateral2m_v1'
 for k in ('assignment_sha256','entry_map_sha256','entry_origin_sha256','parent_timeout_source_sha256'):assert isinstance(s[k],str) and len(s[k])==64
 assert s['wave_mask'].shape==(n,) and s['wave_mask'].dtype==torch.bool
 assert s['bound_episode'].shape==(n,) and s['bound_episode'].dtype==torch.long and (s['bound_episode']>=0).all()
 assert s['limit_steps'].shape==(n,) and s['limit_steps'].dtype==torch.long
 assert torch.equal(s['limit_steps'],torch.where(s['wave_mask'],4000,2000))
 return True
def evaluate(age,s,old):
 assert age.shape==old.shape==(s['num_envs'],) and age.dtype==torch.long and (age>=0).all()
 out=old.clone();mask=s['wave_mask'];out[mask]=age[mask]>=s['limit_steps'][mask];return out
