"""No reward code. Fudan Terrain calls the installed SDK staircase algorithm.
The existing Lab heightfield converter owns the slope-to-vertical triangulation.
"""
from types import SimpleNamespace
import numpy as np
from installed_original_raw_pyramid_stairs188 import pyramid_stairs_terrain as original_hf

class SubTerrain:
    def __init__(self,name,width,length,vertical_scale,horizontal_scale):
        self.name=name;self.width=width;self.length=length
        self.vertical_scale=vertical_scale;self.horizontal_scale=horizontal_scale
        self.height_field_raw=np.zeros((width,length),dtype=np.int16)

def pyramid_stairs_terrain(t,step_width,step_height,platform_size=1.):
    cfg=SimpleNamespace(size=(t.width*t.horizontal_scale,t.length*t.horizontal_scale),
        step_height_range=(step_height,step_height),inverted=False,step_width=step_width,
        platform_width=platform_size,horizontal_scale=t.horizontal_scale,vertical_scale=t.vertical_scale)
    t.height_field_raw=original_hf(0.,cfg)
    assert t.height_field_raw.shape==(t.width,t.length)
    return t

def convert_heightfield_to_trimesh(raw,horizontal_scale,vertical_scale,slope_threshold):
    from isaaclab.terrains.height_field.utils import convert_height_field_to_mesh
    value=convert_height_field_to_mesh(raw,horizontal_scale,vertical_scale,slope_threshold)
    if hasattr(value,'vertices') and hasattr(value,'faces'):return value.vertices,value.faces
    assert isinstance(value,tuple) and len(value)==2
    return value

def unavailable(*args,**kwargs):
    raise RuntimeError('Selected STAIRS3 proportions must never call a non-stair terrain branch')

terrain_utils=SimpleNamespace(SubTerrain=SubTerrain,pyramid_stairs_terrain=pyramid_stairs_terrain,
    convert_heightfield_to_trimesh=convert_heightfield_to_trimesh,
    pyramid_sloped_terrain=unavailable,random_uniform_terrain=unavailable,
    discrete_obstacles_terrain=unavailable,stepping_stones_terrain=unavailable)
