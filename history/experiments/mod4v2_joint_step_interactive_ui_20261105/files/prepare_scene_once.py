"""Make a separate manual v2 scene with a real 0.200m collidable step; source assets unchanged."""
from pathlib import Path
import json,hashlib,xml.etree.ElementTree as ET,sys,time
D=Path(__file__).resolve().parent;P=D.parent/'mod4v2_p0_mechanical_limits_20261105/candidates/HW300N60/package';out=D/'interactive_scene.xml';receipt=D/'SCENE_RECEIPT.json';assert not out.exists()and not receipt.exists()
src=P/'mjcf/scene.xml';raw=src.read_bytes();root=ET.fromstring(raw);root.set('model','MOD4v2 HW300N60 manual joint probe and 200mm step');root.find('compiler').set('meshdir',str((P/'mjcf/assets').resolve()));world=root.find('worldbody');assert world.find("geom[@name='ground']")is not None
ET.SubElement(world,'geom',dict(name='probe_step_200mm',type='box',pos='.75 0 .1',size='.35 .65 .1',rgba='.86 .43 .07 1',contype='1',conaffinity='2',friction='.9 .003 .0001'))
ET.SubElement(world,'site',dict(name='step_200mm_top_marker',pos='.40 -.65 .2',size='.005',rgba='1 .2 .1 1',group='4'))
ET.indent(root,space='  ');data=ET.tostring(root,encoding='utf8',xml_declaration=True);out.write_bytes(data)
import mujoco,numpy as np
sys.path.insert(0,str(P));import kinematics_v2 as kin
m=mujoco.MjModel.from_xml_path(str(out));d=mujoco.MjData(m);kin.set_configuration(m,d,left=(0,0),right=(0,0));g=m.geom('probe_step_200mm').id;bottom=float(m.geom_pos[g,2]-m.geom_size[g,2]);top=float(m.geom_pos[g,2]+m.geom_size[g,2]);assert abs(bottom)<1e-12 and abs(top-.2)<1e-12
names=[m.joint(i).name for i in range(m.njnt)if int(m.jnt_type[i])!=int(mujoco.mjtJoint.mjJNT_FREE)];assert len(names)==30 and m.nu==6 and m.neq==10 and np.isfinite(d.qpos).all()
assert src.read_bytes()==raw
r=dict(epoch=time.time(),version='MOD4v2-HW300N60',source_mjcf=str(src),source_sha256=hashlib.sha256(raw).hexdigest(),scene=str(out),scene_sha256=hashlib.sha256(data).hexdigest(),step=dict(name='probe_step_200mm',height_m=top-bottom,bottom_z_m=bottom,top_z_m=top,near_face_x_m=.4,far_face_x_m=1.1,width_y_m=1.3,collidable=True),joint_names=names,robot_body_count=m.nbody-1,nq=m.nq,nv=m.nv,nu=m.nu,closure_equalities=m.neq,default_root_pose=d.qpos[:7].tolist(),initial_pose_valid=True,source_assets_modified=False,policy_weights_or_training=False)
receipt.write_text(json.dumps(r,indent=2),encoding='utf8');print(json.dumps(r,indent=2))
