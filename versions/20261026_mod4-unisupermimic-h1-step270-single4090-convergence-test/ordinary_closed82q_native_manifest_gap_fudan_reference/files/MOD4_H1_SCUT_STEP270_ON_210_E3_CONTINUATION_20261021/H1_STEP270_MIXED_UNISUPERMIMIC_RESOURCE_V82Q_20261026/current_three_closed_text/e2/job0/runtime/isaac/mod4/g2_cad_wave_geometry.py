"""One new geometric axis: replace only the random-height family with 20mm waves."""
from pathlib import Path
import hashlib,json
import numpy as np
import trimesh
PROFILE=Path(__file__).with_name('g2_cad_profile.json')
def profile():
 p=json.loads(PROFILE.read_text());assert p['version']==1 and p['derived_peak_to_trough_m']==.02
 assert p['scope'].startswith('E1-G2 CAD-derived') and len(p['profile_x_m'])==len(p['normalized_height'])
 assert np.isfinite(p['profile_x_m']).all() and np.isfinite(p['normalized_height']).all()
 assert np.all(np.diff(p['profile_x_m'])>0) and min(p['normalized_height'])==0. and max(p['normalized_height'])==1.
 return p
def make_mesh(size):
 p=profile();sx,sy=map(float,size);assert sx>p['span_m']+1. and sy>1.
 # Two y rows are sufficient for an explicitly x-only extruded profile.
 # Long flat supports precede and follow the complete ten-wave section.
 start=(sx-p['span_m'])*.5
 x=np.r_[0.,start,start+np.asarray(p['profile_x_m'])[1:-1],start+p['span_m'],sx]
 z=np.r_[0.,np.asarray(p['normalized_height'])[0:-1]*.02,0.,0.]
 assert len(x)==len(z) and np.all(np.diff(x)>0) and np.ptp(z)==.02
 vertices=np.stack((np.repeat(x,2),np.tile([0.,sy],len(x)),np.repeat(z,2)),axis=-1)
 i=np.arange(len(x)-1)*2
 faces=np.stack((np.stack((i,i+2,i+1),axis=-1),np.stack((i+1,i+2,i+3),axis=-1)),axis=1).reshape(-1,3)
 mesh=trimesh.Trimesh(vertices,faces,process=False);assert (mesh.face_normals[:,2]>0).all()
 return mesh,np.array([sx*.5,sy*.5,float(np.interp(sx*.5,x,z))])
def wave_mesh(difficulty,cfg):
 mesh,origin=make_mesh(cfg.size)
 return [mesh],origin
def configure_g2(cfg):
 from e1_scene_query_resource import configure_intro
 from isaaclab.terrains.sub_terrain_cfg import SubTerrainBaseCfg
 from isaaclab.utils.configclass import configclass
 recipe=configure_intro(cfg)
 @configclass
 class G2WaveCfg(SubTerrainBaseCfg):
  function=wave_mesh
 old=cfg.scene.terrain.terrain_generator.sub_terrains['random_uniform_for_rm']
 new=G2WaveCfg(proportion=old.proportion,size=cfg.scene.terrain.terrain_generator.size)
 cfg.scene.terrain.terrain_generator.sub_terrains['random_uniform_for_rm']=new
 recipe['profile']='mod4_G2_CAD_derived_20mm_v1'
 recipe['G2_geometry_change']=dict(revision='MOD4-RM-TERRAIN-CURRICULUM-REVISION-003',family='continuous_rough',peak_to_trough_m=.02,profile_sha256=hashlib.sha256(PROFILE.read_bytes()).hexdigest(),period_m=profile()['period_m'],full_section_span_m=profile()['span_m'],source_tessellation_error_retained=True,old_random_height_family_replaced_only=True,other_four_families_unchanged=True,proportions_unchanged=True,not_RM70mm=True)
 return recipe
