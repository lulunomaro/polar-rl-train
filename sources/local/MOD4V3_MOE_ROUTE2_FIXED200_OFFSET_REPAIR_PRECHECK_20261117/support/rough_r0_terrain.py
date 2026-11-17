"""R0 subset of the archived SCUT rotation terrain; explicit shallow curriculum."""
import math
import numpy as np
import torch
from rough_terrain import generator as reference_generator
from isaaclab.terrains import TerrainImporter
from isaaclab.terrains.height_field.hf_terrains import random_uniform_terrain
from isaaclab.utils.warp import convert_to_warp_mesh, raycast_mesh

FAMILIES = ('tiny_step_rot','slope_for_rm_low','inv_slope_for_rm_low',
            'stair_slope_for_rm_low','inv_stair_slope_for_rm_low',
            'random_uniform_for_rm','plane_for_rm_rot')
COUNTS = (16,8,8,8,8,8,14)

def scaled_noise(difficulty, cfg):
    cfg=cfg.copy()
    maximum=max(.005,round(.03*difficulty/.005)*.005)
    cfg.noise_range=(0.,maximum)
    return random_uniform_terrain(difficulty,cfg)

def generator():
    cfg=reference_generator()
    cfg.seed=66
    cfg.num_rows=4;cfg.num_cols=70
    cfg.difficulty_range=(0.,.35)
    cfg.sub_terrains={name:cfg.sub_terrains[name] for name in FAMILIES}
    for name,count in zip(FAMILIES,COUNTS):cfg.sub_terrains[name].proportion=count/70
    cfg.sub_terrains['random_uniform_for_rm'].function=scaled_noise
    return cfg

def cross_groups(n,device):
    ids=torch.arange(n,device=device)
    nominal=ids%5==4
    flat=torch.zeros(n,device=device,dtype=torch.bool)
    target=round(n*.2);nominal_target=round(int(nominal.sum())*.2)
    for group,count in ((ids[nominal],nominal_target),(ids[~nominal],target-nominal_target)):
        if count:flat[group[torch.div(torch.arange(count,device=device)*len(group),count,rounding_mode='floor')]]=True
    return nominal,flat

def install_origins(cfg):
    old_import=TerrainImporter.import_mesh
    def remember(self,name,mesh):
        self._r0_mesh=mesh
        return old_import(self,name,mesh)
    TerrainImporter.import_mesh=remember
    def origins(self,n,all_origins):
        nominal,flat=cross_groups(n,self.device)
        self.max_terrain_level=all_origins.shape[0]
        self.terrain_levels=torch.zeros(n,device=self.device,dtype=torch.long)
        self.terrain_types=torch.zeros(n,device=self.device,dtype=torch.long)
        col_families=[]
        for family,count in enumerate(COUNTS):col_families.extend([family]*count)
        self.r0_column_families=torch.tensor(col_families,device=self.device)
        flat_cols=(self.r0_column_families==6).nonzero().flatten()
        rough_cols=(self.r0_column_families!=6).nonzero().flatten()
        for mask,columns in ((flat,flat_cols),(~flat,rough_cols)):
            ids=mask.nonzero().flatten()
            self.terrain_types[ids]=columns[torch.arange(len(ids),device=self.device)%len(columns)]
        self.r0_flat_mask=flat;self.r0_nominal_mask=nominal
        self.r0_offsets=torch.zeros(n,3,device=self.device)
        for col in range(cfg.num_cols):
            ids=(self.terrain_types==col).nonzero().flatten()
            k=torch.arange(len(ids),device=self.device)
            columns=math.ceil(math.sqrt(max(len(ids),1)))
            rows=math.ceil(max(len(ids),1)/columns)
            self.r0_offsets[ids,0]=(k%columns-(columns-1)/2.)*.8
            self.r0_offsets[ids,1]=(torch.div(k,columns,rounding_mode='floor')-(rows-1)/2.)*.8
        mesh=self._r0_mesh
        self.r0_wp_mesh=convert_to_warp_mesh(mesh.vertices,mesh.faces,self.device)
        result=all_origins[self.terrain_levels,self.terrain_types].clone()+self.r0_offsets
        starts=result.clone();starts[:,2]+=5.
        direction=torch.zeros_like(starts);direction[:,2]=-1.
        hits=raycast_mesh(starts,direction,self.r0_wp_mesh,max_dist=10.)[0]
        if not bool(torch.isfinite(hits).all()):raise ValueError('R0 spawn ray missed')
        result[:,2]=hits[:,2]
        return result
    TerrainImporter._compute_env_origins_curriculum=origins
