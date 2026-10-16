from pathlib import Path
import json,torch
from wave50_route_fullsave_CPU_parent_reviewed import fullsave as old
from wave50_lifetime_state import KEY,PROFILE,validate
def fullsave(path,count=20000):
 info=old(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False);s=ck[KEY];validate(s,count);assert ck['E1_WAVE50_episode_lifetime_profile']==PROFILE
 route=ck['E1_WAVE50_route_lifecycle_state'];assert all(s[k]==route[k] for k in ('assignment_sha256','entry_map_sha256','entry_origin_sha256'))
 assert torch.equal(s['wave_mask'].cpu(),route['wave_mask'].cpu()) and torch.equal(s['bound_episode'].cpu(),ck['E1_terrain_state']['episode'].cpu())
 assert ck['independent_terrain_expert']=='E1_WAVE50' and ck['E1_WAVE50_initial_source_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
 assert s['parent_timeout_source_sha256']==json.loads(Path(__file__).parents[2].joinpath('reports/PARENT_TIMEOUT_SOURCE_ACTUAL.json').read_bytes())['canonical_function_sha256']
 info['lifetime_state_verified']=True;info['initial_source_and_expert_identity_exact']=True;return info
