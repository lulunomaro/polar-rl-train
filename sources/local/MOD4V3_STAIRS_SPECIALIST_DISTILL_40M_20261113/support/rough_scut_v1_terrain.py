"""40% continuous200mm stairs with oblique ascent +35% originalRough-v1 +25% plane."""
import math
import torch
from isaaclab.terrains import TerrainGeneratorCfg, TerrainImporter
import isaaclab.terrains as t
from isaaclab.utils.warp import convert_to_warp_mesh, raycast_mesh
from rough_terrain import MeshCustomGridBarsTerrainCfg
from scut_cliff_terrain import HfCliffInvertedPyramidStairsTerrainCfg
FAMILIES=('low_speed_stair_for_rm','tiny_step','slope_for_rm_high','inv_slope_for_rm_low','high_speed_stair_for_rm','stair_slope_for_rm_high','inv_stair_slope_for_rm_low','inv_stair_slope_for_rm_high','plane_for_rm','random_uniform_for_rm','cliff_inv_stair_slope_short_for_rm')
COUNTS=(1,2,1,1,1,1,1,2,8,1,1)
SPECIAL_START=sum(COUNTS)
COLUMN_FAMILIES=tuple(f for f,count in enumerate(COUNTS) for _ in range(count))+(0,)*10+(4,)*10
def generator():
 return TerrainGeneratorCfg(seed=66,curriculum=True,size=(9.,9.),border_width=10.,border_height=1.,num_rows=10,num_cols=40,color_scheme='none',horizontal_scale=.1,vertical_scale=.005,slope_threshold=.5,difficulty_range=(0.,1.),use_cache=False,sub_terrains={
  'low_speed_stair_for_rm':t.HfPyramidStairsTerrainCfg(proportion=1/40,step_height_range=(.15,.35),step_width=1.5,platform_width=3.,border_width=0.),
  'tiny_step':MeshCustomGridBarsTerrainCfg(proportion=2/40,num_horizontal_range=(2,4),num_vertical_range=(2,4),randomize_bar_count_difficulty=True,force_unequal_counts=False,force_even_counts=True,bar_width_range=(.05,.2),randomize_bar_width_difficulty=True,bar_height_range=(.02,.06),bar_length_ratio=.95,ground_thickness=.05),
  'slope_for_rm_high':t.HfPyramidSlopedTerrainCfg(proportion=1/40,slope_range=(.15,.35),platform_width=2.,border_width=2.),
  'inv_slope_for_rm_low':t.HfInvertedPyramidSlopedTerrainCfg(proportion=1/40,slope_range=(.05,.15),platform_width=0.,inverted=True,border_width=1.),
  'high_speed_stair_for_rm':t.HfPyramidStairsTerrainCfg(proportion=1/40,step_height_range=(.15,.4),step_width=1.5,platform_width=3.,border_width=0.),
  'stair_slope_for_rm_high':t.HfPyramidStairsTerrainCfg(proportion=1/40,step_height_range=(.015,.032),step_width=.1,platform_width=1.,border_width=1.),
  'inv_stair_slope_for_rm_low':t.HfInvertedPyramidStairsTerrainCfg(proportion=1/40,step_height_range=(.005,.015),step_width=.1,platform_width=2.,inverted=True,border_width=1.),
  'inv_stair_slope_for_rm_high':t.HfInvertedPyramidStairsTerrainCfg(proportion=2/40,step_height_range=(.015,.032),step_width=.1,platform_width=2.,inverted=True,border_width=1.),
  'plane_for_rm':t.MeshPlaneTerrainCfg(proportion=8/40),
  'random_uniform_for_rm':t.HfRandomUniformTerrainCfg(proportion=1/40,noise_range=(0.,.03),noise_step=.005,downsampled_scale=.2,border_width=0.),
  'cliff_inv_stair_slope_short_for_rm':HfCliffInvertedPyramidStairsTerrainCfg(proportion=1/40,step_height_range=(.025,.032),step_width=.1,platform_width=3.,border_width=2.,height_offset_range=(.3,.4),height_offset_curriculum_scale_by_difficulty=False,height_offset_curriculum_num_levels=11),
  'continuous_low_200mm':t.HfPyramidStairsTerrainCfg(proportion=10/40,step_height_range=(.2,.2),step_width=1.5,platform_width=3.,border_width=0.),
  'continuous_high_200mm':t.HfPyramidStairsTerrainCfg(proportion=10/40,step_height_range=(.2,.2),step_width=1.5,platform_width=3.,border_width=0.)})


def cross_groups(n,device):
 ids=torch.arange(n,device=device);nominal=ids%5==4;flat=torch.zeros(n,device=device,dtype=torch.bool)
 total=round(n*.25);nt=round(int(nominal.sum())*.25)
 for group,count in ((ids[nominal],nt),(ids[~nominal],total-nt)):
  if count:flat[group[torch.div(torch.arange(count,device=device)*len(group),count,rounding_mode='floor')]]=True
 return nominal,flat

def install_origins(cfg):
 old_import=TerrainImporter.import_mesh
 def remember(self,name,mesh):self._r1_mesh=mesh;return old_import(self,name,mesh)
 TerrainImporter.import_mesh=remember
 def origins(self,n,all_origins):
  nominal,flat=cross_groups(n,self.device);special=torch.zeros(n,device=self.device,dtype=torch.bool)
  target=round(n*.4);nt=round(int(nominal.sum())*.4)
  for mask,count in ((nominal,nt),(~nominal,target-nt)):
   available=(mask&~flat).nonzero().flatten()
   if count:special[available[torch.div(torch.arange(count,device=self.device)*len(available),count,rounding_mode='floor')]]=True
  retained=~(flat|special);self.max_terrain_level=all_origins.shape[0]
  self.terrain_levels=torch.randint(0,all_origins.shape[0],(n,),device=self.device);self.terrain_levels[special]=3
  self.terrain_types=torch.zeros(n,device=self.device,dtype=torch.long)
  self.r1_column_families=torch.tensor(COLUMN_FAMILIES,device=self.device)
  retained_columns=torch.arange(SPECIAL_START,device=self.device)
  flat_columns=retained_columns[self.r1_column_families[:SPECIAL_START]==FAMILIES.index('plane_for_rm')]
  rough_columns=retained_columns[self.r1_column_families[:SPECIAL_START]!=FAMILIES.index('plane_for_rm')]
  for mask,columns in ((flat,flat_columns),(retained,rough_columns),(special,torch.arange(SPECIAL_START,40,device=self.device))):
   ids=mask.nonzero().flatten();self.terrain_types[ids]=columns[torch.arange(len(ids),device=self.device)%len(columns)]
  self.r1_flat_mask=flat;self.r1_nominal_mask=nominal;self.r1_continuous_stair_mask=special;self.r1_retained_rough_mask=retained
  self.r1_offsets=torch.zeros(n,3,device=self.device)
  for col in range(SPECIAL_START):
   ids=(self.terrain_types==col).nonzero().flatten();k=torch.arange(len(ids),device=self.device);width=math.ceil(math.sqrt(max(1,len(ids))));rows=math.ceil(max(1,len(ids))/width)
   self.r1_offsets[ids,0]=(k%width-(width-1)/2.)*.8
   self.r1_offsets[ids,1]=(torch.div(k,width,rounding_mode='floor')-(rows-1)/2.)*.8
  self.r1_wp_mesh=convert_to_warp_mesh(self._r1_mesh.vertices,self._r1_mesh.faces,self.device)
  result=all_origins[self.terrain_levels,self.terrain_types].clone()+self.r1_offsets;starts=result.clone();starts[:,2]+=5.;down=torch.zeros_like(starts);down[:,2]=-1.
  hit=raycast_mesh(starts,down,self.r1_wp_mesh,max_dist=10.)[0]
  if not bool(torch.isfinite(hit).all()):raise ValueError('Retention terrain spawn ray missed')
  result[:,2]=hit[:,2];return result
 TerrainImporter._compute_env_origins_curriculum=origins
