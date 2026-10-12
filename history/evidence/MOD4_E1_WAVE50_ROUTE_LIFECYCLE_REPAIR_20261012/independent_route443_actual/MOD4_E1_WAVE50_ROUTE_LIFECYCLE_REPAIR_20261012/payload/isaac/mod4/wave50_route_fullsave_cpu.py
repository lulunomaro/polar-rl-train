import torch
from wave50_direction_fullsave_cpu import fullsave as old
from wave50_route_state import KEY,PROFILE,validate
def fullsave(path,count=20000):
 info=old(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False);s=ck[KEY];validate(s,count);assert ck['E1_WAVE50_route_lifecycle_profile']==PROFILE
 terrain=ck['E1_terrain_state'];direction=ck['E1_WAVE50_episode_direction_state']
 assert s['assignment_sha256']==terrain['entry_assignment_sha256'] and s['entry_map_sha256']==terrain['entry_map_sha256'] and s['entry_origin_sha256']==terrain['entry_origin_sha256']
 assert torch.equal(s['bound_episode'].cpu(),terrain['episode'].cpu()) and torch.equal(s['spawn_xy'].cpu(),terrain['spawn_xy'].cpu())
 assert torch.equal(s['wave_mask'].cpu(),direction['wave_mask'].cpu()) and torch.equal(s['toward_sign'].cpu(),direction['entry_sign'].cpu())
 info['route_lifecycle_state_verified']=True;return info
