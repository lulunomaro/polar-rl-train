"""Match the reference's whole-leg same-end silhouette with original joint limits."""
from pathlib import Path
import json,sys,math
import numpy as np
import mujoco
D=Path(__file__).resolve().parent;ROOT=Path('C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4');sys.path.insert(0,str(ROOT));from kinematics import leg_configuration
m=mujoco.MjModel.from_xml_path(str(ROOT/'scene.xml'));d=mujoco.MjData(m);hip=.498;diff=.398;values={s:leg_configuration(hip,diff,s)[0]for s in('left','right')};chassis=m.body('chassis').id;wheel=m.body('left_wheel').id;thigh=m.body('left_thigh').id;shin=m.body('left_shin').id
for side,v in values.items():
 for name,q in v.items():
  j=m.joint(side+'_'+name)
  if m.jnt_limited[j.id]:assert m.jnt_range[j.id,0]-1e-9<=q<=m.jnt_range[j.id,1]+1e-9

def bottom(g):
 z=d.geom_xpos[g,2];r=d.geom_xmat[g].reshape(3,3);s=m.geom_size[g];t=m.geom_type[g]
 if t==mujoco.mjtGeom.mjGEOM_BOX:return float(z-np.abs(r[2]).dot(s))
 if t==mujoco.mjtGeom.mjGEOM_SPHERE:return float(z-s[0])
 if t==mujoco.mjtGeom.mjGEOM_CAPSULE:return float(z-abs(r[2,2])*s[1]-s[0])
 if t==mujoco.mjtGeom.mjGEOM_CYLINDER:return float(z-abs(r[2,2])*s[1]-s[0]*math.sqrt(max(0,1-r[2,2]**2)))
 return float(z-m.geom_rbound[g])
collision=[g for g in range(m.ngeom)if m.geom_contype[g]and m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_PLANE];bodygeoms=[g for g in collision if m.geom_bodyid[g]==chassis or 'guide_roller'in(m.geom(g).name or'')]
rows=[]
for pitch in np.linspace(.22,.65,431):
 mujoco.mj_resetData(m,d);d.qpos[:3]=[-4,0,0];d.qpos[3:7]=[math.cos(pitch/2),0,math.sin(pitch/2),0]
 for side,v in values.items():
  for name,q in v.items():d.qpos[m.joint(side+'_'+name).qposadr[0]]=q
 mujoco.mj_forward(m,d);d.qpos[2]=.0625-d.xpos[wheel,2]+.0001;mujoco.mj_forward(m,d);bg=min(bottom(g)for g in bodygeoms);low=min(bottom(g)for g in collision);score=abs(bg-.0002)+100*max(0,-low)
 rows.append((score,float(pitch),float(d.qpos[2]),bg,low,d.qpos.copy()))
best=min(rows,key=lambda x:x[0]);d.qpos[:]=best[-1];mujoco.mj_forward(m,d);R=d.xmat[chassis].reshape(3,3);pose=dict(kind='REFERENCE_SAME_END_WHOLE_LEG_POSE_WITH_ORIGINAL_LIMITS',hip_rad=hip,input_difference_rad=diff,body_pitch_rad=best[1],body_pitch_deg=math.degrees(best[1]),root_xyz=d.qpos[:3].tolist(),root_quaternion=d.qpos[3:7].tolist(),joint_values=values,joint_limits_changed=False,root_body_belly_or_guide_ground_gap_m=best[3],minimum_collision_height_m=best[4],wheel_xyz=d.xpos[wheel].tolist(),knee_xyz=d.xpos[shin].tolist(),qpos=d.qpos.tolist(),reference_is_other_robot_not_exact_dimensions=True,description='Both thigh/knee and wheel extend toward the same pictured end; original hip/crank/linkage bounds retained, chassis tilted to rest on its underside/guide and wheels, not wheel-only tucked pose')
(D/'POSE.json').write_text(json.dumps(pose,indent=2),encoding='utf8');m.vis.headlight.active=1;m.vis.headlight.ambient[:]=.6;m.vis.headlight.diffuse[:]=.8
with mujoco.Renderer(m,height=600,width=1000)as r:
 cam=mujoco.MjvCamera();cam.lookat[:]=[-4.08,0,.18];cam.distance=1.3;cam.azimuth=90;cam.elevation=-8;r.update_scene(d,camera=cam);from PIL import Image;Image.fromarray(r.render()).save(D/'INITIAL_POSE.png')
print(json.dumps({k:v for k,v in pose.items()if k not in('qpos','joint_values')},indent=2))
