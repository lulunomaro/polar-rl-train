"""Independent derived continuous10degree ramp, both orientations, no curb or stair."""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh
PROFILE=Path(__file__).with_name('slope10_profile.json')

def profile():
 p=json.loads(PROFILE.read_bytes());assert p['angle_deg']==10. and p['ramp_length_m']==2.
 assert p['derived_not_actual_RM_geometry'] and p['no_vertical_riser']
 return p

def make_mesh(size,mirrored=False):
 p=profile();assert tuple(map(float,size))==(9.,9.)
 v=np.array(p['vertices'],dtype=np.float64);f=np.array(p['triangles'],dtype=np.int64)
 if mirrored:v[:,0]*=-1;f=f[:,::-1]
 v[:,:2]+=np.asarray(size)*.5
 m=trimesh.Trimesh(v,f,process=False);assert (m.face_normals[:,2]>0).all()
 return m,np.array([4.5,4.5,p['height_m']/2])

def slope_mesh(difficulty,cfg):
 assert 0.<=difficulty<=.25
 mesh,origin=make_mesh(cfg.size,difficulty>=.125);return [mesh],origin

def configure_slope(cfg):
 from e1_scene_query_resource import configure_intro
 from isaaclab.terrains.sub_terrain_cfg import SubTerrainBaseCfg
 from isaaclab.utils.configclass import configclass
 r=configure_intro(cfg);gen=cfg.scene.terrain.terrain_generator
 assert gen.difficulty_range==(0.,.25) and tuple(gen.size)==(9.,9.)
 @configclass
 class SlopeCfg(SubTerrainBaseCfg):function=slope_mesh
 old=gen.sub_terrains['random_uniform_for_rm'];gen.sub_terrains['random_uniform_for_rm']=SlopeCfg(proportion=old.proportion,size=gen.size)
 r.update(profile='mod4_SLOPE_derived10deg_2m_mirrored_v1')
 r['SLOPE_geometry_change']=dict(revision='MOD4-MOE-TERRAIN-SUBEXPERT-REVISION-004',angle_deg=10.,ramp_length_m=2.,height_m=profile()['height_m'],
  profile_sha256=hashlib.sha256(PROFILE.read_bytes()).hexdigest(),mirrored=True,no_vertical_riser=True,
  old_random_height_family_replaced_only=True,other_four_families_unchanged=True,proportions_unchanged=True,
  derived_not_actual_RM_geometry=True,not_stair_flight=True,not_CURB_height_progression=True)
 return r
