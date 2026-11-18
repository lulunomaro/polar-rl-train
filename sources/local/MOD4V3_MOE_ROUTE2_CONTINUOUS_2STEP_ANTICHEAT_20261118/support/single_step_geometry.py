"""Exact collision-bank mesh:
- row 0 (difficulty < 0.15): 1-step 200mm platform (3.0m x 3.0m x 0.20m, riser at |x|=1.50m)
- row >= 1 (difficulty >= 0.15): continuous 2-step 200mm+200mm=400mm pyramid
  (Step 1: 5.80m x 5.80m x 0.20m, riser at |x|=2.90m, 1.50m tread;
   Step 2: 2.80m x 2.80m x 0.40m, riser at |x|=1.40m, 2.80m top platform)
"""
import numpy as np
import trimesh

HEIGHTS = (0.20, 0.40)


def single_step(difficulty, cfg):
    cx, cy = cfg.size[0] / 2.0, cfg.size[1] / 2.0
    base = trimesh.creation.box(extents=(cfg.size[0], cfg.size[1], 0.10))
    base.apply_translation((cx, cy, -0.05))
    if difficulty < 0.08:
        top = trimesh.creation.box(extents=(3.0, 3.0, 0.20))
        top.apply_translation((cx, cy, 0.10))
        return [base, top], np.array([cx, cy, 0.0])
    step1 = trimesh.creation.box(extents=(5.2, 5.2, 0.20))
    step1.apply_translation((cx, cy, 0.10))
    step2 = trimesh.creation.box(extents=(2.2, 2.2, 0.40))
    step2.apply_translation((cx, cy, 0.20))
    return [base, step1, step2], np.array([cx, cy, 0.0])
