import os, numpy as np, mujoco, colorsys, math
from PIL import Image
ROOT=r"D:\claude2\fangzhen"; OUT=os.path.join(ROOT,"docs","audit")
os.makedirs(OUT,exist_ok=True)
m=mujoco.MjModel.from_xml_path(os.path.join(ROOT,"robot","out_cc","scene_cc.xml"))
d=mujoco.MjData(m)
mujoco.mj_resetDataKeyframe(m,d,0); mujoco.mj_forward(m,d)
cen=np.array([0.0,0.0,0.30])
VIEWERS={
 "iso":   (cen,1.75, 25.0, 30.0),
 "side":  (cen,1.65,  5.0, 90.0),
 "front": (cen,1.75,  5.0,  0.0),
 "rear":  (cen,1.75,  5.0,180.0),
 "top":   (cen,1.60, 88.0,  0.0),
 "legL":  (np.array([-0.10,-0.24,0.20]),0.75, 20.0, 40.0),
}
r=mujoco.Renderer(m,height=700,width=1244)
for mode in ("grey","rainbow"):
    vg=[g for g in range(m.ngeom) if m.geom_group[g]==2]
    for i,g in enumerate(vg):
        if mode=="rainbow":
            c=colorsys.hsv_to_rgb(i/len(vg),0.95,0.95); m.geom_rgba[g]=[*c,1.0]
        else:
            m.geom_rgba[g]=[0.72,0.72,0.75,1.0]
    tiles=[]
    for name,(lk,dist,elev,azim) in VIEWERS.items():
        cam=mujoco.MjvCamera(); cam.type=mujoco.mjtCamera.mjCAMERA_FREE
        cam.lookat=lk; cam.distance=dist; cam.elevation=elev; cam.azimuth=azim
        r.update_scene(d,camera=cam); img=r.render()
        Image.fromarray(img).save(os.path.join(OUT,"geom_%s_%s.png"%(mode,name)))
        tiles.append(img)
    grid=np.vstack([np.hstack(tiles[0:3]),np.hstack(tiles[3:6])])
    Image.fromarray(grid).save(os.path.join(OUT,"grid_%s.png"%mode))
    print("wrote",mode,grid.shape)
