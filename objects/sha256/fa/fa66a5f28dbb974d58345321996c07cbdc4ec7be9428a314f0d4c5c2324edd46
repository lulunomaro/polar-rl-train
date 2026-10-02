import os, numpy as np, mujoco
from PIL import Image
ROOT=r"D:\claude2\fangzhen"; OUT=os.path.join(ROOT,"docs","audit"); os.makedirs(OUT,exist_ok=True)
m=mujoco.MjModel.from_xml_path(os.path.join(ROOT,"robot","out_cc","scene_cc.xml"))
d=mujoco.MjData(m); mujoco.mj_resetDataKeyframe(m,d,0); mujoco.mj_forward(m,d)
LEGBODIES={"left_rear1","left_rear2","left_wheel","left_spring1","left_spring2","left_front1","left_front2","left_front3","left_front4",
 "right_rear1","right_rear2","right_wheel","right_spring1","right_spring2","right_front1","right_front2","right_front3","right_front4"}
leggeom=[]; basegeom=[]
for g in range(m.ngeom):
    if m.geom_group[g]!=2: continue
    b=mujoco.mj_id2name(m,mujoco.mjtObj.mjOBJ_BODY,m.geom_bodyid[g])
    (leggeom if b in LEGBODIES else basegeom).append(g)
print("visual geoms: base",len(basegeom),"legs",len(leggeom))
VIEWS={"side":(1.30,8,90),"front34":(1.45,22,55),"rear34":(1.45,22,235),"legL":(0.62,12,68)}
def shot(tag,hide_base=False,hide_leg=False,look=None):
    for g in m.geom_rgba if False else []: pass
    for g in range(m.ngeom):
        if m.geom_group[g]!=2: continue
        m.geom_rgba[g]=[0.78,0.78,0.80,1.0]
    if hide_base:
        for g in basegeom: m.geom_rgba[g]=[0.78,0.78,0.80,0.0]
    if hide_leg:
        for g in leggeom: m.geom_rgba[g]=[0.78,0.78,0.80,0.0]
    r=mujoco.Renderer(m,height=700,width=1244)
    tiles=[]
    lk=np.array([0,0,0.30]) if look is None else np.array(look)
    for name,(dist,elev,azim) in VIEWS.items():
        cam=mujoco.MjvCamera(); cam.type=mujoco.mjtCamera.mjCAMERA_FREE
        cam.lookat=lk; cam.distance=dist; cam.elevation=elev; cam.azimuth=azim
        r.update_scene(d,camera=cam); tiles.append(r.render())
    grid=np.vstack([np.hstack(tiles[:2]),np.hstack(tiles[2:])])
    Image.fromarray(grid).save(os.path.join(OUT,"layers_%s.png"%tag)); print("wrote",tag)
shot("full"); shot("legsonly",hide_base=True); shot("baseonly",hide_leg=True)