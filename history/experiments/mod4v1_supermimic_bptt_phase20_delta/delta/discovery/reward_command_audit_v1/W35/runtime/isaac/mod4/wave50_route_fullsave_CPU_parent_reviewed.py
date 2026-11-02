"""Prepared v1 retained; additionally pin the immutable parent boundary source SHA."""
from pathlib import Path
import hashlib,torch
from wave50_route_fullsave_cpu import fullsave as original
from wave50_route_state import KEY
def fullsave(path,count=20000):
 info=original(path,count=count);ck=torch.load(path,map_location='cpu',weights_only=False)
 assert ck[KEY]['parent_boundary_source_sha256']==hashlib.sha256(Path(__file__).with_name('e1_terrain_runtime.py').read_bytes()).hexdigest()
 info['parent_route_boundary_source_CPU_exact']=True;return info
