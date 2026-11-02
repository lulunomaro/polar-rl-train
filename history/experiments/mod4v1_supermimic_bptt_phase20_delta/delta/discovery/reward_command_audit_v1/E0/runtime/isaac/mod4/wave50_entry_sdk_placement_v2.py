"""Diagnostic SDK placement only; original production reset/math untouched."""
import json,numpy as np,torch
from pathlib import Path
def prepare(env):
 rows=env.scene.terrain.retention_assignment;chosen=[]
 for i,row in enumerate(range(15,25)):
  candidates=sorted([x for x in rows if x['row']==row and x['family']=='random_uniform_for_rm' and not x['actual_mesh_flat']],key=lambda x:x['column'])
  assert len(candidates)==6;chosen.append(candidates[i%2])
 centers=np.array([[(x['bounds'][0][k]+x['bounds'][1][k])*.5 for k in (0,1)] for x in chosen])
 from g4_cad_wave_geometry import profile
 half=profile()['span_m']*.5;side=np.where(np.arange(10)%2==0,-1.,1.);xy=centers.copy();xy[:,0]+=side*(half+.8)
 points=env._rough_probe_bank['points'].cpu().numpy();extent=np.max(abs(points[:,:2]),axis=0)
 for i,x in enumerate(chosen):
  lo=np.array(x['bounds'][0][:2]);hi=np.array(x['bounds'][1][:2]);assert np.all(xy[i]-extent>lo) and np.all(xy[i]+extent<hi)
 assert .8-extent[0]>=.4 and np.unique(xy,axis=0).shape[0]==10
 actual=torch.as_tensor(xy,device=env.device,dtype=torch.float32)
 env.scene.env_origins[:,:2]=actual;env.scene.terrain.env_origins[:,:2]=actual
 return dict(chosen_actual_assignments=chosen,centers=centers.tolist(),actual_requested_starts=actual.cpu().tolist(),side=side.tolist(),full_bank_extent_xy=extent.tolist(),front_flat_clearance_m=float(.8-extent[0]),actual10G4_cells=True,two_front_support_sides=True,assignment_sha256=env.scene.terrain.retention_assignment_sha)
def verify(env,placement):
 root=env.scene['robot'].data.root_pos_w[:,:2];expected=torch.tensor(placement['actual_requested_starts'],device=env.device,dtype=root.dtype)
 assert torch.equal(root,expected) and torch.equal(env._rough_spawn_xy,expected)
 from e1_full_pose_reset import query
 ray=query(env);p=env._rough_probe_bank['points'];starts=p[None,:,:].repeat(10,1,1);starts[:,:,:2]+=root[:,None,:];starts[:,:,2]=float(ray.geometry.vertices[:,2].max())+2.
 out=ray.cast(starts.contiguous(),10.);assert out['hit'].all() and (out['normal'][...,2]>.99).all()
 spread=(out['height'].amax(1)-out['height'].amin(1));assert float(spread.max())<=1e-6
 for i,x in enumerate(placement['chosen_actual_assignments']):
  lo=torch.tensor(x['bounds'][0][:2],device=env.device);hi=torch.tensor(x['bounds'][1][:2],device=env.device)
  assert ((starts[i,:,:2]>lo)&(starts[i,:,:2]<hi)).all()
 assert env._wave50_entry_map_receipt['actual_origin_bound']
 assert env._wave50_entry_map_receipt['Wave_environments']==10
 return dict(placement,actual_origin_bound_entry_cache_verified=True,entry_map_receipt=env._wave50_entry_map_receipt,reset_root_before_physics_exact=True,complete_footprint_all_flat_hits=True,actual_G4_cell_count=10,actual_footprint_max_height_range_m=float(spread.max()),original_full_reset_receipt=env._rough_probe_reset_receipt)
