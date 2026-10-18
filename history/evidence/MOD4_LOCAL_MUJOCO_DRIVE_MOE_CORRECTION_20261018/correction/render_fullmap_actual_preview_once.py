from pathlib import Path
import sys,time,json
import mujoco,numpy as np
from PIL import Image
B=Path(__file__).resolve().parent;D=B.parent/'MOD4_LOCAL_MUJOCO_DRIVE_20261008'
sys.path.insert(0,str(D))
from rm7v7_moe_sim import RM7V7MoESim
s=RM7V7MoESim()
with mujoco.Renderer(s.model,height=720,width=1280,max_geom=60000) as renderer:
    cam=mujoco.MjvCamera();cam.type=mujoco.mjtCamera.mjCAMERA_FREE;cam.lookat[:]=[0,0,.3]
    cam.distance=24;cam.azimuth=110;cam.elevation=-65
    renderer.update_scene(s.data,camera=cam)
    p=B/'FULL_RM7V7_LATEST_MOE_PREVIEW.png';assert not p.exists();Image.fromarray(renderer.render()).save(p)
    print(json.dumps(dict(rendered=str(p),bytes=p.stat().st_size)))
