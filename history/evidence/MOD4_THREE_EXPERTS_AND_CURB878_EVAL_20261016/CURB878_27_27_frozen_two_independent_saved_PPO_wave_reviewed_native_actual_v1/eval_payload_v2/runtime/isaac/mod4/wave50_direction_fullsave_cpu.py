"""Full legacy contract plus independent command direction state, actual tensor count."""
import torch
from wave50_entry_fullsave_cpu_v2 import fullsave as old
from wave50_direction_state import KEY,PROFILE,validate
def fullsave(path,count=20000):
 info=old(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False)
 validate(ck[KEY],count);assert ck['E1_WAVE50_episode_direction_profile']==PROFILE
 assert ck[KEY]['assignment_sha256']==ck['E1_retained_flat_command_state']['assignment_sha256']
 assert ck[KEY]['entry_map_sha256']==ck['E1_terrain_state']['entry_map_sha256']
 assert torch.equal(ck[KEY]['bound_episode'].cpu(),ck['E1_terrain_state']['episode'].cpu())
 assert ck[KEY]['entry_origin_sha256']==ck['E1_terrain_state']['entry_origin_sha256']
 info['direction_state_verified']=True;return info
