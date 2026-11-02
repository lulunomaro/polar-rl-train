"""Full legacy contract plus independent command direction state, actual tensor count."""
import torch
from curb20_entry_fullsave_cpu import fullsave as old
from curb20_direction_state import KEY,PROFILE,validate
def fullsave(path,count=20000):
 info=old(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False)
 validate(ck[KEY],count);assert ck['E1_CURB_entry_direction_profile']==PROFILE
 assert ck[KEY]['assignment_sha256']==ck['E1_retained_flat_command_state']['assignment_sha256']
 assert ck[KEY]['entry_map_sha256']==ck['E1_terrain_state']['entry_map_sha256']
 assert torch.equal(ck[KEY]['bound_episode'].cpu(),ck['E1_terrain_state']['episode'].cpu())
 info['direction_state_verified']=True;return info
