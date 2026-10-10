"""Validate terrain identity/bookkeeping; this is not a serialized physics engine."""
import torch
VERSION=1
def validate(state,n):
 assert state['version']==VERSION and state['num_envs']==n
 assert state['profile']=='mod4_intro_gentle_v1' and state['seed']==20260928
 assert state['layout']==[40,40] and state['command_vx_range']==[-.3,.3] and state['command_vy_yaw']==[0.,0.]
 assert state['partition_exact'] and state['no_ground_fallback'] and state['no_privileged_terrain_actor_input']
 assert len(state['geometry_triangles_sha256'])==64 and len(state['ordered_partition_triangles_sha256'])==64
 assert state['triangles']>0 and state['reset_bank_sha256']=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
 for name,shape in (('spawn_xy',(n,2)),('reset_expected_q',(n,30))):
  x=state[name];assert x.shape==shape and x.dtype==torch.float32 and bool(torch.isfinite(x).all())
 assert state['episode'].shape==(n,) and state['episode'].dtype==torch.long and bool((state['episode']>=0).all())
 return True
