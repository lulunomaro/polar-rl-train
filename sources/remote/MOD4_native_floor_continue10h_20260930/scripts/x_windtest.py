import os,numpy as np,trimesh,mujoco
from PIL import Image
ROOT=r"D:\claude2\fangzhen"; MD=os.path.join(ROOT,"robot","out_cc","meshes"); TMP=os.path.join(ROOT,"docs","audit")
def stats(fn):
    m=trimesh.load(os.path.join(MD,fn),process=False)
    # winding-derived normals vs stored
    fn_w=m.face_normals
    inv=m.is_winding_consistent
    vol=m.volume
    return len(m.faces), inv, vol
for f in ["base_armor_00.stl","base_frame_00.stl","thigh_l.stl","wheel_l.stl"]:
    n,inv,vol=stats(f)
    print("%-18s faces %7d  winding_consistent=%s  signed_volume=%12.1f mm3 %s"%(f,n,inv,vol,"(NEGATIVE => normals point INWARD)" if vol<0 else ""))
def render(fn,tag,fix):
    src=os.path.join(MD,fn); m=trimesh.load(src,process=False)
    if fix:
        trimesh.repair.fix_normals(m)
    p=os.path.join(TMP,"wind_%s.stl"%tag); m.export(p)
    xml=os.path.join(TMP,"wind_%s.xml"%tag)
    open(xml,"w",encoding="utf-8").write(
      '<mujoco><compiler meshdir="%s"/><visual><global offwidth="640" offheight="480"/></visual>'
      '<asset><mesh name="x" file="%s" scale="0.001 0.001 0.001"/></asset>'
      '<worldbody><geom name="fl" type="plane" size="0 0 0.05" rgba="0.5 0.5 0.5 1" contype="0" conaffinity="0"/>'
      '<body pos="0 0 0.35"><geom type="mesh" mesh="x" rgba="0.8 0.3 0.3 1" contype="0" conaffinity="0"/></body></worldbody></mujoco>'
      %(TMP.replace("\\","/"), os.path.basename(p).replace("\\","/")))
    mm=mujoco.MjModel.from_xml_path(xml); dd=mujoco.MjData(mm); mujoco.mj_forward(mm,dd)
    r=mujoco.Renderer(mm,height=480,width=640)
    cam=mujoco.MjvCamera(); cam.type=mujoco.mjtCamera.mjCAMERA_FREE; cam.lookat=[0,0,0]; cam.distance=1.4; cam.elevation=12; cam.azimuth=45
    r.update_scene(dd,camera=cam); img=r.render()
    Image.fromarray(img).save(os.path.join(TMP,"wind_%s.png"%tag))
    # fraction of pixels that are the red geom
    red=(img[:,:,0].astype(int)-img[:,:,1].astype(int)>40)
    print("  %-26s geom pixels %.1f%%"%(tag,100*red.mean()))
render("base_armor_00.stl","armor_raw",False)
render("base_armor_00.stl","armor_fixed",True)
render("thigh_l.stl","thigh_raw",False)