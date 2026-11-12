"""Fixed level3 horizontal stair geometry, 200mm risers, 80%stairs/20%flat."""
import math,torch
from isaaclab.terrains import TerrainGeneratorCfg,TerrainImporter
import isaaclab.terrains as t
from isaaclab.utils.warp import convert_to_warp_mesh,raycast_mesh
FAMILIES=('low_speed_stair_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','high_speed_stair_for_rm','stair_slope_for_rm_high','inv_stair_slope_for_rm_low','inv_stair_slope_for_rm_high','plane_for_rm','random_uniform_for_rm','cliff_inv_stair_slope_short_for_rm')
COUNTS=(4,0,0,0,4,0,0,0,2,0,0)
def generator():
 return TerrainGeneratorCfg(seed=66,curriculum=True,size=(9.,9.),border_width=10.,border_height=1.,num_rows=4,num_cols=10,color_scheme='none',horizontal_scale=.1,vertical_scale=.005,slope_threshold=.5,difficulty_range=(0.,1.),use_cache=False,sub_terrains={
 'low_speed_stair_for_rm':t.HfPyramidStairsTerrainCfg(proportion=.4,step_height_range=(.2,.2),step_width=1.5,platform_width=3.,border_width=0.),
 'high_speed_stair_for_rm':t.HfPyramidStairsTerrainCfg(proportion=.4,step_height_range=(.2,.2),step_width=1.5,platform_width=3.,border_width=0.),
 'plane_for_rm':t.MeshPlaneTerrainCfg(proportion=.2)})
def cross_groups(n,device):
 ids=torch.arange(n,device=device);nominal=ids%5==4;flat=torch.zeros(n,device=device,dtype=torch.bool);target=round(n*.2);nt=round(int(nominal.sum())*.2)
 for group,count in ((ids[nominal],nt),(ids[~nominal],target-nt)):
  if count:flat[group[torch.div(torch.arange(count,device=device)*len(group),count,rounding_mode='floor')]]=True
 return nominal,flat

def install_origins(cfg):
 old_import=TerrainImporter.import_mesh
 def remember(self,name,mesh):self._r1_mesh=mesh;return old_import(self,name,mesh)
 TerrainImporter.import_mesh=remember
 def origins(self,n,all_origins):
  nominal,flat=cross_groups(n,self.device);self.max_terrain_level=4;self.terrain_levels=torch.full((n,),3,device=self.device,dtype=torch.long);self.terrain_types=torch.zeros_like(self.terrain_levels)
  self.r1_column_families=torch.tensor([0]*4+[4]*4+[8]*2,device=self.device)
  for mask,cols in ((flat,torch.tensor([8,9],device=self.device)),(~flat,torch.arange(8,device=self.device))):
   ids=mask.nonzero().flatten();self.terrain_types[ids]=cols[torch.arange(len(ids),device=self.device)%len(cols)]
  self.r1_flat_mask=flat;self.r1_nominal_mask=nominal;self.r1_offsets=torch.zeros(n,3,device=self.device)
  for col in [8,9]:
   ids=(self.terrain_types==col).nonzero().flatten();k=torch.arange(len(ids),device=self.device);width=math.ceil(math.sqrt(max(1,len(ids))));rows=math.ceil(max(1,len(ids))/width)
   self.r1_offsets[ids,0]=(k%width-(width-1)/2.)*min(.8,7/max(width,1));self.r1_offsets[ids,1]=(torch.div(k,width,rounding_mode='floor')-(rows-1)/2.)*min(.8,7/max(rows,1))
  self.r1_wp_mesh=convert_to_warp_mesh(self._r1_mesh.vertices,self._r1_mesh.faces,self.device)
  result=all_origins[self.terrain_levels,self.terrain_types].clone()+self.r1_offsets;starts=result.clone();starts[:,2]+=5.;down=torch.zeros_like(starts);down[:,2]=-1.;hit=raycast_mesh(starts,down,self.r1_wp_mesh,max_dist=10.)[0]
  if not bool(torch.isfinite(hit).all()):raise ValueError('Continuous stairs origin ray missed')
  result[:,2]=hit[:,2];return result
 TerrainImporter._compute_env_origins_curriculum=origins
