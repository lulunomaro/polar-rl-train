"""Only the shadow fixture scene API changes; actual boundary/runtime are unchanged."""
import types,torch
from wave50_route_runtime import state_dict
from wave50_route_state import evaluate_timeout
def verify_GPU_boundary_fixture(env):
 from e1_terrain_runtime import boundary_timeout as original
 s=state_dict(env,refresh=True);anchor=s['spawn_xy'];mask=s['wave_mask'];sign=s['toward_sign'];rows=[]
 class FixtureScene(dict):pass
 for x,y in ((2.5,0.),(4.,0.),(4.001,0.),(-2.001,0.),(0.,2.001)):
  xy=anchor.clone();xy[:,0]+=torch.where(mask,sign,torch.ones_like(sign))*x;xy[:,1]+=y
  scene=FixtureScene(robot=types.SimpleNamespace(data=types.SimpleNamespace(root_pos_w=xy)));scene.env_origins=anchor
  fixture=types.SimpleNamespace(scene=scene,_rough_spawn_xy=anchor)
  old=original(fixture);new=evaluate_timeout(xy,anchor,s,old);assert torch.equal(new[~mask],old[~mask])
  expected=x>4 or x < -2 or abs(y)>2;assert torch.equal(new[mask],torch.full_like(new[mask],expected))
  rows.append(dict(inward_fixture_m=x,lateral_fixture_m=y,old_truncated_Wave=int(old[mask].sum()),new_truncated_Wave=int(new[mask].sum()),nonWave_exact=True))
 return dict(passed=True,actual_bound_CUDA_state=anchor.is_cuda,rows=rows,no_physics_step_reset_teleport_or_progress_credit=True,not_physical_fullroute_or_contact_certificate=True,fixture_scene_original_attribute_and_mapping_API_exact=True)
