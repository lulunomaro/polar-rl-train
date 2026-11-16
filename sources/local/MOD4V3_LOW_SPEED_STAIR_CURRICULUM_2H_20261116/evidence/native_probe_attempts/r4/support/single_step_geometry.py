"""Exact collision-bank mesh, independent of live PhysX state."""
import numpy as np
import trimesh
HEIGHTS=(.05,.07,.09,.11,.13,.15,.17,.19,.20)
def single_step(difficulty,cfg):
    row=min(8,max(0,int(float(difficulty)*10)))
    height=HEIGHTS[row]
    base=trimesh.creation.box(extents=(cfg.size[0],cfg.size[1],.10))
    base.apply_translation((cfg.size[0]/2,cfg.size[1]/2,-.05))
    top=trimesh.creation.box(extents=(3.,3.,height))
    top.apply_translation((cfg.size[0]/2,cfg.size[1]/2,height/2))
    return [base,top],np.array([cfg.size[0]/2,cfg.size[1]/2,0.])
