"""Separate local range-extrapolation scenario: level chassis floor, both legs rear.
Original MJCF and training sources stay untouched; the assumption is explicit.
"""
from pathlib import Path
import sys,json,math,ast
import numpy as np
import mujoco
D=Path(__file__).resolve().parent;ROOT=Path('C:/Users/lulu/Desktop/claude/mjcf/chassis_mod4');sys.path.insert(0,str(ROOT));from kinematics import leg_configuration
m=mujoco.MjModel.from_xml_path(str(ROOT/'scene.xml'));d=mujoco.MjData(m);ranges={}
for side in('left','right'):
 for name in('hip','crank','drive_hip_spin','drive_input_spin'):
  j=m.joint(side+'_'+name);ranges[j.name]=dict(original=m.jnt_range[j.id].tolist(),scenario=[-3.,3.]);m.jnt_range[j.id]=[-3.,3.]
chassis=m.body('chassis').id;wheel=m.body('left_wheel').id;shin=m.body('left_shin').id

def bottom(g):
 z=d.geom_xpos[g,2];r=d.geom_xmat[g].reshape(3,3);s=m.geom_size[g];t=m.geom_type[g]
 if t==mujoco.mjtGeom.mjGEOM_BOX:return float(z-np.abs(r[2]).dot(s))
 if t==mujoco.mjtGeom.mjGEOM_SPHERE:return float(z-s[0])
 if t==mujoco.mjtGeom.mjGEOM_CAPSULE:return float(z-abs(r[2,2])*s[1]-s[0])
 if t==mujoco.mjtGeom.mjGEOM_CYLINDER:return float(z-abs(r[2,2])*s[1]-s[0]*math.sqrt(max(0,1-r[2,2]**2)))
 return float(z-m.geom_rbound[g])
collision=[g for g in range(m.ngeom)if m.geom_contype[g]and m.geom_type[g]!=mujoco.mjtGeom.mjGEOM_PLANE];bodygeoms=[g for g in collision if m.geom_bodyid[g]==chassis or 'guide_roller'in(m.geom(g).name or'')];rows=[];diff=.398
for hip in np.linspace(-2.6,-1.1,1501):
 vals={s:leg_configuration(float(hip),diff,s)[0]for s in('left','right')};mujoco.mj_resetData(m,d);d.qpos[:3]=[-4.,0.,0.];d.qpos[3:7]=[1.,0.,0.,0.]
 for side,v in vals.items():
  for name,q in v.items():
   j=m.joint(side+'_'+name);assert not m.jnt_limited[j.id]or m.jnt_range[j.id,0]-1e-8<=q<=m.jnt_range[j.id,1]+1e-8;d.qpos[j.qposadr[0]]=q
 mujoco.mj_forward(m,d);d.qpos[2]=-min(bottom(g)for g in bodygeoms)+.0001;mujoco.mj_forward(m,d);low=min(bottom(g)for g in collision);kx=d.xpos[shin,0]+4;wx=d.xpos[wheel,0]+4
 if low>=-1e-7 and kx>.03 and wx>.27:
  score=float(d.xpos[wheel,2]-.0625);rows.append((score,float(hip),d.qpos.copy(),vals,low))
assert rows,'No nonpenetrating same-end extended-range pose';best=min(rows,key=lambda x:x[0]);d.qpos[:]=best[2];mujoco.mj_forward(m,d);bodygap=min(bottom(g)for g in bodygeoms);belly=m.geom('chassis_belly').id
pose=dict(kind='LEVEL_BELLY_GROUND_BOTH_LEGS_REAR_EXTENDED_RANGE_SCENARIO',qpos=d.qpos.tolist(),root_xyz=d.qpos[:3].tolist(),root_quaternion=d.qpos[3:7].tolist(),body_pitch_deg=0.,hip_rad=best[1],input_difference_rad=diff,joint_values=best[3],joint_limits_changed=True,range_overlay=ranges,original_XML_or_training_modified=False,hardware_range_not_verified=True,chassis_lowest_collision_ground_gap_m=bodygap,chassis_belly_ground_gap_m=bottom(belly),minimum_collision_height_m=best[4],knee_xyz=d.xpos[shin].tolist(),wheel_xyz=d.xpos[wheel].tolist(),description='Level chassis resting at its lowest belly/guide collision; both whole leg assemblies swept toward true +X rear; hip/crank range widened only in this local what-if, not original capability qualification')
(D/'POSE.json').write_text(json.dumps(pose,indent=2),encoding='utf8');m.vis.headlight.active=1;m.vis.headlight.ambient[:]=.6;m.vis.headlight.diffuse[:]=.8
with mujoco.Renderer(m,height=600,width=1000)as r:
 cam=mujoco.MjvCamera();cam.lookat[:]=[-3.9,0,.13];cam.distance=1.3;cam.azimuth=270;cam.elevation=-8;r.update_scene(d,camera=cam);from PIL import Image;Image.fromarray(r.render()).save(D/'INITIAL_POSE.png')
s=(D.parent/'mod4v1_e3_full_leg_pose_view_20261104/view_live.py').read_text(encoding='utf8');anchor="sim=ns['E3Sim']();pose=json.loads((D/'POSE.json').read_bytes());";assert s.count(anchor)==1;s=s.replace(anchor,anchor+"\nfor name,r in pose['range_overlay'].items():sim.model.jnt_range[sim.model.joint(name).id]=r['scenario']\n")
s=s.replace('WHOLE LEG EXTENDED','EXTENDED HIP RANGE / BELLY GROUND').replace('LIVE_CURRENT_E3_WHOLE_LEG_REFERENCE_POSE_NOT_ANIMATION','LIVE_E3_EXTENDED_RANGE_SCENARIO_NOT_ORIGINAL_MODEL_QUALIFICATION').replace('joint_limits_changed=False','joint_limits_changed=True').replace('viewer.cam.azimuth=105.','viewer.cam.azimuth=270.').replace("270. if s['camera']==1 else 135.","270. if s['camera']==1 else 245.").replace("np.array([-.08,0,-.015])","np.array([.08,0,-.005])");ast.parse(s);(D/'view_live.py').write_text(s,encoding='utf8');print(json.dumps({k:v for k,v in pose.items()if k not in('qpos','joint_values','range_overlay')},indent=2))
