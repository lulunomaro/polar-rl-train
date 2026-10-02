import os,numpy as np,mujoco
from PIL import Image
ROOT=r"D:\claude2\fangzhen"
base=mujoco.MjModel.from_xml_path(os.path.join(ROOT,"robot","out_cc","scene_cc.xml"))
def shot(tag,floor_mat=True,floor_alpha=1.0,hide=False):
    m=mujoco.MjModel.from_xml_path(os.path.join(ROOT,"robot","out_cc","scene_cc.xml"))
    d=mujoco.MjData(m); mujoco.mj_resetDataKeyframe(m,d,0); mujoco.mj_forward(m,d)
    fl=mujoco.mj_name2id(m,mujoco.mjtObj.mjOBJ_GEOM,"floor")
    print("  floor geom id",fl,"matid",m.geom_matid[fl],"rgba",m.geom_rgba[fl])
    if hide: m.geom_group[fl]=5
    else:
        if not floor_mat: m.geom_matid[fl]=-1
        m.geom_rgba[fl]=[0.5,0.5,0.5,floor_alpha]
    r=mujoco.Renderer(m,height=700,width=1100)
    cam=mujoco.MjvCamera(); cam.type=mujoco.mjtCamera.mjCAMERA_FREE
    cam.lookat=[0,0,0.30]; cam.distance=1.7; cam.elevation=20; cam.azimuth=55
    r.update_scene(d,camera=cam); img=r.render()
    Image.fromarray(img).save(os.path.join(ROOT,"docs","audit","ft_%s.png"%tag))
    print("wrote ft_%s.png"%tag)
shot("1_mat",floor_mat=True)
shot("2_nomat",floor_mat=False)
shot("3_hidden",hide=True)